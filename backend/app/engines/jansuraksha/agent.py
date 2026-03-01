"""
Jan Suraksha Bot v3 — Manager Agent Architecture.

Manager pattern: ONE central node handles ALL routing decisions by reading
the actual state (entities, context, history) — no phases, no string tracking.

Graph: START → manager → {classify, execute, respond} → manager → END
       All tool nodes return to manager. Manager validates and decides next step.

Per-turn cost: 2 LLM calls (classify + respond/execute). Same as v2.
"""

import json
import asyncio
from datetime import datetime
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage

from app.core import get_openai_client, MODEL_SMART, MODEL_FAST
from app.db import get_db
from app.engines.jansuraksha.neo4j_context import load_user_context, save_complaint
from app.engines.jansuraksha.retrieval import retrieve_legal_context
from app.engines.jansuraksha.prompts import (
    SMART_CLASSIFY_SYSTEM,
    RESPONSE_GENERATION_SYSTEM,
    build_conditional_sections,
)
from app.engines.jansuraksha.mappings import get_authority_info, get_suggested_actions
from app.engines.jansuraksha.tools import fill_complaint, fill_cpgrams
from app.engines.jansuraksha.templates import _WR_STATIONS, _CR_STATIONS, _HR_STATIONS
from app.utils.logger import get_logger

log = get_logger("jansuraksha.agent")

import re as _re

# ── Sensitive Content Handling ───────────────────────────────
# Azure OpenAI's content filter blocks explicit descriptions of sexual
# assault/harassment even when the context is legitimate legal-aid.
# Pre-screen → rule-based classify + regex entity extraction → sanitised
# message for downstream LLM calls.  Zero API waste, zero user-facing errors.

_SENSITIVE_KEYWORDS = frozenset({
    "sexual", "molest", "groping", "grope", "rape",
    "touched inappropriately", "inappropriate touch",
    "eve teasing", "molestation", "indecent", "obscene",
    "यौन", "बलात्कार", "छेड़छाड़", "छेड़", "उत्पीड़न",
    "लैंगिक", "छळ", "विनयभंग",
})


def _is_sensitive_content(message: str) -> bool:
    """Return True if the message will trigger Azure's content filter."""
    msg_lower = message.lower()
    return any(kw in msg_lower for kw in _SENSITIVE_KEYWORDS)


def _extract_entities_regex(message: str) -> dict:
    """Best-effort entity extraction via regex (no LLM)."""
    entities = {
        "time": None, "location": None, "from_station": None,
        "to_station": None, "items_lost": None, "accused_description": None,
        "injuries": None, "platform": None, "train_name": None,
        "travel_class": None,
    }
    msg_lower = message.lower()

    # Time
    m = _re.search(r'(\d{1,2})\s*(?::\d{2})?\s*(am|pm)', msg_lower)
    if m:
        entities["time"] = m.group(0).strip()

    # Stations — match longest names first
    all_stations = _WR_STATIONS | _CR_STATIONS | _HR_STATIONS
    found = []
    for stn in sorted(all_stations, key=len, reverse=True):
        if stn in msg_lower and stn not in found:
            found.append(stn)
    if found:
        entities["from_station"] = found[0]
        entities["location"] = found[0]
        if len(found) > 1:
            entities["to_station"] = found[1]

    # Travel class
    for pat, cls in {
        "first class": "First Class", "1st class": "First Class",
        "second class": "Second Class", "2nd class": "Second Class",
        "general": "General", "ladies": "Ladies",
    }.items():
        if pat in msg_lower:
            entities["travel_class"] = cls
            break

    # Accused description
    for pat in [r'(?:group of|bunch of)\s+\w+',
                r'(?:a |an )\w+\s+(?:man|men|person|people|guy|guys)']:
        m = _re.search(pat, msg_lower)
        if m:
            entities["accused_description"] = m.group(0)
            break

    return entities


def _sanitize_message(message: str, incident_type: str, entities: dict) -> str:
    """Replace explicit content with clinical/legal terms for Azure compliance."""
    if incident_type != "sexual_harassment":
        return message

    parts = ["The complainant reports a serious incident of physical assault and harassment"]
    if entities.get("from_station") and entities.get("to_station"):
        parts.append(f"while travelling from {entities['from_station'].title()} to {entities['to_station'].title()}")
    elif entities.get("from_station"):
        parts.append(f"at/near {entities['from_station'].title()} station")
    loc = entities.get("location")
    if loc and loc != entities.get("from_station"):
        parts.append(f"near {loc.title()} station")
    if entities.get("time"):
        parts.append(f"at approximately {entities['time']}")
    if entities.get("travel_class"):
        parts.append(f"in {entities['travel_class']} compartment")
    if entities.get("accused_description"):
        parts.append(f"by {entities['accused_description']}")
    parts.append("during their railway journey. The incident falls under IPC Section 354A and the POSH Act 2013.")
    return " ".join(parts)


_SENSITIVE_RESPONSES = {
    "show_options": {
        "en": "I'm really sorry this happened to you. What you experienced is a serious crime, and you have every right to seek justice. Your safety is the top priority right now. Please select an option below so I can help you take the next step immediately.",
        "hi": "मुझे बहुत दुख है कि आपके साथ यह हुआ। यह एक गंभीर अपराध है और आपको न्याय पाने का पूरा अधिकार है। अभी आपकी सुरक्षा सबसे ज़रूरी है। कृपया नीचे एक विकल्प चुनें ताकि मैं तुरंत आपकी मदद कर सकूं।",
        "mr": "तुम्हाला हे सहन करावे लागले याबद्दल मला खूप वाईट वाटते. हा एक गंभीर गुन्हा आहे आणि तुम्हाला न्याय मिळवण्याचा पूर्ण अधिकार आहे. तुमची सुरक्षा सर्वात महत्त्वाची आहे. कृपया खालील एक पर्याय निवडा.",
    },
    "ask_details": {
        "en": "I'm so sorry you're going through this. To help you file a strong complaint, could you share when and where this happened? Even approximate details will help.",
        "hi": "मुझे बहुत दुख है। एक मज़बूत शिकायत दर्ज करने के लिए, क्या आप बता सकते हैं यह कब और कहाँ हुआ?",
        "mr": "तुम्हाला हे सहन करावे लागले याबद्दल खूप वाईट वाटते. एक मजबूत तक्रार दाखल करण्यासाठी, कृपया हे कधी आणि कुठे घडले ते सांगा.",
    },
}


# ── State = The TopicHolder ──────────────────────────────────
# Shared across ALL nodes. Every node reads and writes here.
# No phases — manager reads actual data to make decisions.

class BotState(TypedDict, total=False):
    # Conversation
    messages: Annotated[list[AnyMessage], add_messages]
    user_id: str
    language: str

    # Accumulated context (persists across turns via checkpoint)
    user_context: dict          # from Neo4j: name, route, train
    original_message: str       # concatenated user messages for templates
    incident_type: str          # theft, robbery, assault, ...
    severity: str               # low/medium/high/critical
    entities: dict              # time, location, items_lost, suspect, ...
    legal_context: list         # from Zilliz vector search
    authority_info: dict        # from rule-based lookup
    suggested_actions: list     # from rule-based lookup

    # Per-turn control (reset each invocation via run_agent)
    classified_this_turn: bool  # has classify run this turn?
    response_ready: bool        # is the response ready to send?
    sensitive_content: bool     # Azure content-filter bypass active?

    # Manager → tool node instructions
    next_step: str              # "classify" | "execute" | "respond" | "done"
    current_action: str         # action_id for execute (file_complaint, check_status, ...)
    respond_mode: str           # "show_options" | "ask_details" | "follow_up"
    detected_action: str        # from classify: user's explicit intent

    # Output (read by run_agent at the end)
    turn_output: dict


# ── Helpers ──────────────────────────────────────────────────

def _get_lang(lang_code: str) -> str:
    return {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(lang_code, "English")


def _get_latest_human_message(state: dict) -> str:
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def _parse_choice(message: str, actions: list[dict]) -> str | None:
    """Parse user's message as an action choice (number, id, or label match)."""
    msg = message.strip()
    if not actions:
        return None

    if msg.isdigit():
        idx = int(msg) - 1
        if 0 <= idx < len(actions):
            return actions[idx]["id"]

    msg_lower = msg.lower()
    for action in actions:
        if msg_lower == action["id"]:
            return action["id"]

    for action in actions:
        label_lower = action["label"].lower()
        if label_lower in msg_lower or msg_lower in label_lower:
            return action["id"]

    return None


def _has_enough_details(state: dict) -> bool:
    """
    Check if we have enough details to proceed with filing.

    RULES:
    - After 2+ human messages → ALWAYS return True (stop asking, use what we have)
    - On 1st message → need basic anchors: when + where + what happened
    - train_name, travel_class, accused_description are NICE-TO-HAVE, never block
    """
    # Count human messages — after user has responded once to follow-up, STOP asking
    human_count = sum(1 for m in state.get("messages", []) if isinstance(m, HumanMessage))
    if human_count >= 2:
        return True

    # First message only — check bare minimum anchors
    entities = state.get("entities", {})
    incident_type = state.get("incident_type", "general")

    has_when = bool(entities.get("time"))
    # Require a real station name, not a vague location like "inside the train"
    all_stations = _WR_STATIONS | _CR_STATIONS | _HR_STATIONS
    from_stn = (entities.get("from_station") or "").strip().lower()
    location = (entities.get("location") or "").strip().lower()
    has_where = from_stn in all_stations or any(s in location for s in all_stations)
    has_what = bool(entities.get("items_lost")) if incident_type in ("theft", "robbery") else True

    return has_when and has_where and has_what


# ── MANAGER NODE ─────────────────────────────────────────────
# The brain. Reads state, decides what tool to call next.
# Pure Python — zero LLM calls. Runs multiple times per turn.

def manager_node(state: BotState) -> dict:
    """
    Central decision-maker. Reads the TopicHolder (state) and decides.
    No phases — looks at what DATA actually exists.
    """
    # ── If response is ready → we're done ──
    if state.get("response_ready"):
        log.info("[manager] Response ready → done")
        return {"next_step": "done"}

    latest_msg = _get_latest_human_message(state)
    actions = state.get("suggested_actions", [])

    # ── Before classifying: check if user picked a numbered action ──
    # This saves 1 LLM call — no need to classify "1" or "2"
    if not state.get("classified_this_turn") and actions:
        choice = _parse_choice(latest_msg, actions)
        if choice:
            # Info-only actions can execute immediately
            if choice in ("check_status", "know_authority", "know_rights"):
                log.info("[manager] User picked info action '%s' → execute", choice)
                return {"next_step": "execute", "current_action": choice}
            # Filing actions need detail check first
            if _has_enough_details(state):
                log.info("[manager] User picked '%s' + enough details → execute", choice)
                return {"next_step": "execute", "current_action": choice}
            else:
                log.info("[manager] User picked '%s' but missing details → ask_details", choice)
                return {"next_step": "respond", "respond_mode": "ask_details"}

    # ── Not classified yet → classify first ──
    if not state.get("classified_this_turn"):
        log.info("[manager] Not classified → classify")
        return {"next_step": "classify"}

    # ── After classification: route based on actual state ──

    intent = state.get("detected_action") or None  # normalize empty string to None

    # 1. Info-only intents — don't need entity details, execute immediately
    if intent in ("check_status", "know_authority", "know_rights"):
        log.info("[manager] Info intent='%s' → execute", intent)
        return {"next_step": "execute", "current_action": intent}

    # 2. Action intents (file_complaint, compensation_info, file_cpgrams)
    #    These NEED details. Check before executing.
    if intent:
        if _has_enough_details(state):
            log.info("[manager] Intent='%s' + enough details → execute", intent)
            return {"next_step": "execute", "current_action": intent}
        else:
            log.info("[manager] Intent='%s' but missing details → ask_details", intent)
            return {"next_step": "respond", "respond_mode": "ask_details"}

    # 3. Conversational follow-up (re-entry with general+none = "thanks", "ok")
    if state.get("legal_context") and state.get("incident_type") == "general":
        log.info("[manager] Re-entry general+none → respond(follow_up)")
        return {"next_step": "respond", "respond_mode": "follow_up"}

    # 4. User described an incident without explicit intent
    if _has_enough_details(state):
        log.info("[manager] Enough details → respond(show_options)")
        return {"next_step": "respond", "respond_mode": "show_options"}
    else:
        log.info("[manager] Missing details → respond(ask_details)")
        return {"next_step": "respond", "respond_mode": "ask_details"}


# ── CLASSIFY NODE ────────────────────────────────────────────
# Cost: 1 LLM (smart classify) + 0-1 EMBED (legal retrieval)
# Also: Neo4j context load, rule-based authority + actions

def classify_node(state: BotState) -> dict:
    """
    Classify incident, extract entities, load context.
    Re-entry aware: merges entities, skips embed, reuses Neo4j context.
    """
    user_id = state["user_id"]
    latest_msg = _get_latest_human_message(state)
    language = state.get("language", "en")
    is_reentry = bool(state.get("legal_context"))

    log.info("[classify] START — user=%s, reentry=%s, msg=%.60s...",
             user_id, is_reentry, latest_msg)

    # ── 1. Neo4j context (skip if already loaded) ──
    existing_ctx = state.get("user_context")
    if existing_ctx and existing_ctx.get("found"):
        user_ctx = existing_ctx
    else:
        try:
            user_ctx = load_user_context(user_id)
            log.info("[classify] User: name=%s, phone=%s",
                     user_ctx.get("name"), user_ctx.get("phone"))
        except Exception as e:
            log.error("[classify] Neo4j FAILED: %s", e)
            user_ctx = {"user_id": user_id, "found": False}

    # ── 2. Smart classify ──
    # Check for sensitive content FIRST — Azure blocks sexual assault descriptions
    incident_type = "general"
    severity = "medium"
    detected_action = None
    new_entities = {}
    sensitive = _is_sensitive_content(latest_msg)

    if sensitive:
        # Rule-based classification — skip LLM entirely
        incident_type = "sexual_harassment"
        severity = "critical"
        new_entities = _extract_entities_regex(latest_msg)
        log.info("[classify] SENSITIVE content — rule-based: type=%s, entities=%s",
                 incident_type, [k for k, v in new_entities.items() if v])
    else:
        # Normal LLM classification (1 call)
        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model=MODEL_FAST,
                messages=[
                    {"role": "system", "content": SMART_CLASSIFY_SYSTEM},
                    {"role": "user", "content": latest_msg},
                ],
                temperature=0,
                max_tokens=300,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            result = json.loads(raw)
            incident_type = result.get("incident_type", "general")
            severity = result.get("severity", "medium")
            user_intent = result.get("user_intent", "none")
            new_entities = result.get("entities", {})
            detected_action = user_intent if user_intent and user_intent != "none" else None

            log.info("[classify] type=%s, severity=%s, intent=%s, entities=%s",
                     incident_type, severity, detected_action or "none",
                     [k for k, v in new_entities.items() if v])
        except Exception as e:
            log.error("[classify] LLM FAILED: %s", e)

    # ── 2b. Merge entities (fill nulls, don't overwrite) ──
    existing_entities = state.get("entities", {})
    if existing_entities:
        merged = dict(existing_entities)
        for key, new_val in new_entities.items():
            if new_val and not merged.get(key):
                merged[key] = new_val
        entities = merged
    else:
        entities = new_entities

    # Preserve original incident_type on re-entry if classify returned general
    if is_reentry and incident_type == "general" and state.get("incident_type") != "general":
        incident_type = state.get("incident_type", "general")
        severity = state.get("severity", severity)

    # ── 2c. Concatenate messages for templates ──
    existing_msg = state.get("original_message", "")
    if existing_msg and existing_msg != latest_msg:
        original_msg = f"{existing_msg}\n{latest_msg}"
    else:
        original_msg = latest_msg

    # ── 3. Legal retrieval (skip on re-entry or status check) ──
    existing_legal = state.get("legal_context", [])
    if detected_action == "check_status":
        legal_context = existing_legal or []
    elif existing_legal and (is_reentry or incident_type == state.get("incident_type")):
        legal_context = existing_legal
        log.info("[classify] Legal: REUSED (%d chunks)", len(legal_context))
    else:
        legal_context = []
        try:
            legal_context = retrieve_legal_context(
                query=latest_msg, mode="legal_basis",
                incident_type=incident_type, location_scope="mumbai", top_k=5,
            )
            log.info("[classify] Legal: retrieved %d chunks", len(legal_context))
        except Exception as e:
            log.error("[classify] Retrieval FAILED: %s", e)

    # ── 4. Rule-based authority + actions (zero API) ──
    authority_info = get_authority_info(incident_type, user_ctx)
    legal_refs = [c["section_ref"] for c in legal_context if c.get("section_ref")]
    authority_info["legal_references"] = legal_refs[:3]
    if not authority_info["compensation_eligible"]:
        authority_info["compensation_eligible"] = any(
            c.get("compensation_eligible") for c in legal_context
        )

    suggested_actions = get_suggested_actions(incident_type, language)

    log.info("[classify] DONE — authority=%s, actions=%s",
             authority_info.get("primary_authority"), [a["id"] for a in suggested_actions])

    return {
        "classified_this_turn": True,
        "sensitive_content": sensitive,
        "original_message": original_msg,
        "user_context": user_ctx,
        "incident_type": incident_type,
        "severity": severity,
        "entities": entities,
        "detected_action": detected_action,
        "legal_context": legal_context,
        "authority_info": authority_info,
        "suggested_actions": suggested_actions,
    }


# ── RESPOND NODE ─────────────────────────────────────────────
# Cost: 1 LLM call
# Modes: show_options (with buttons), ask_details (no buttons), follow_up

def respond_node(state: BotState) -> dict:
    """
    Generate response. Mode is set by manager based on state.
    - ask_details: empathy + ask for missing info, NO buttons
    - show_options: empathy + buttons
    - follow_up: conversational chat with full history
    """
    mode = state.get("respond_mode", "show_options")
    language = _get_lang(state.get("language", "en"))

    log.info("[respond] mode=%s", mode)

    if mode == "follow_up":
        return _respond_follow_up(state, language)

    # ── ask_details or show_options → use conditional prompt ──
    prompt_mode = "ask_details" if mode == "ask_details" else "show_options"

    # Sensitive content → pre-written empathetic response (skip LLM)
    if state.get("sensitive_content") and prompt_mode in _SENSITIVE_RESPONSES:
        lang_code = state.get("language", "en")
        response_text = _SENSITIVE_RESPONSES[prompt_mode].get(lang_code,
                            _SENSITIVE_RESPONSES[prompt_mode]["en"])
        log.info("[respond] SENSITIVE — using pre-written %s response", prompt_mode)
    else:
        try:
            client = get_openai_client()
            conditional = build_conditional_sections(prompt_mode, state)
            system_prompt = RESPONSE_GENERATION_SYSTEM.format(
                language=language,
                conditional_sections=conditional,
            )

            response = client.chat.completions.create(
                model=MODEL_FAST,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": state.get("original_message", "")},
                ],
                temperature=0.4,
                max_tokens=250,
            )
            response_text = response.choices[0].message.content
        except Exception as e:
            log.error("[respond] FAILED: %s", e)
            response_text = "I understand your concern. Could you share a few more details so I can help you better?"

    # KEY: only include options when we have enough details
    options = state.get("suggested_actions") if mode == "show_options" else None

    log.info("[respond] DONE — mode=%s, options=%s", mode, bool(options))

    return {
        "response_ready": True,
        "messages": [AIMessage(content=response_text)],
        "turn_output": {
            "response": response_text,
            "options": options,
            # Only show authority pill when showing options, not during detail gathering
            "authority": state.get("authority_info", {}).get("primary_authority") if mode == "show_options" else None,
        },
    }


def _respond_follow_up(state: dict, language: str) -> dict:
    """Handle conversational follow-up using full message history."""
    authority_info = state.get("authority_info", {})
    user_ctx = state.get("user_context", {})

    system_msg = f"""You are Jan Suraksha Bot — a helpful assistant for Mumbai train passengers.
Respond in {language}. Use simple everyday language. Talk like a caring friend.
NEVER use abbreviations (GRP, RPF, RCT, CPGRAMS, FIR, IPC). Use plain words.

You are helping this user with a railway incident:
- Incident type: {state.get('incident_type')}
- Authority: {authority_info.get('primary_authority')} (helpline: {authority_info.get('helpline')})
- Name: {user_ctx.get('name', 'Passenger')}

Respond helpfully and concisely. Maximum 4-5 sentences."""

    is_sensitive = state.get("sensitive_content", False)
    entities = state.get("entities", {})
    inc_type = state.get("incident_type", "general")

    llm_messages = [{"role": "system", "content": system_msg}]
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            content = (_sanitize_message(msg.content, inc_type, entities)
                       if is_sensitive else msg.content)
            llm_messages.append({"role": "user", "content": content})
        elif isinstance(msg, AIMessage):
            llm_messages.append({"role": "assistant", "content": msg.content})

    client = get_openai_client()
    response = client.chat.completions.create(
        model=MODEL_FAST, messages=llm_messages, temperature=0.3, max_tokens=300,
    )
    response_text = response.choices[0].message.content

    log.info("[respond] follow_up DONE")
    return {
        "response_ready": True,
        "messages": [AIMessage(content=response_text)],
        "turn_output": {"response": response_text},
    }


# ── INCIDENT SUMMARY GENERATOR ────────────────────────────────
# Generates a formal 3-4 sentence FIR-style description from chat context.

def _generate_fir_context(state: dict) -> dict:
    """
    Single LLM call to generate:
    1. incident_summary — formal FIR description (replaces raw chat messages)
    2. compensation_amount — extracted from the same legal RAG chunks

    Returns dict with both keys.
    """
    entities = state.get("entities", {})
    incident_type = state.get("incident_type", "general")
    original_msg = state.get("original_message", "")
    language = state.get("language", "en")
    legal_context = state.get("legal_context", [])

    # Sanitize for Azure content filter
    if state.get("sensitive_content"):
        original_msg = _sanitize_message(original_msg, incident_type, entities)

    lang_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(language, "English")
    ent_str = json.dumps({k: v for k, v in entities.items() if v}, ensure_ascii=False)

    # Compensation chunks from the same RAG retrieval
    comp_chunks = [c for c in legal_context
                   if c.get("compensation_eligible") or c.get("doc_type") == "compensation_schedule"]
    comp_text = "\n".join(f"- {c['section_ref']}: {c['text'][:300]}" for c in comp_chunks[:4])

    prompt = f"""Return ONLY a JSON object with two keys.

1. "incident_summary": A formal 3-4 sentence incident description for a police FIR.
   - Write in {lang_name}, formal third-person: "The complainant states that..."
   - Based on: {original_msg}
   - Details: {ent_str}
   - ONLY facts. No assumptions. Maximum 4 sentences.

2. "compensation_amount": The applicable compensation amount for this {incident_type} incident.
   Injuries reported: {entities.get('injuries', 'not specified')}
   Legal context from RAG:
   {comp_text if comp_text else 'No compensation data retrieved for this incident type.'}
   - Extract the exact Rs. amount from the legal context above that applies to this case.
   - Include the legal source reference.
   - If no compensation data, return "N/A".

Respond ONLY with JSON: {{"incident_summary": "...", "compensation_amount": "..."}}"""

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=400,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(raw)
        log.info("[fir_context] summary=%d chars, compensation=%s",
                 len(result.get("incident_summary", "")),
                 result.get("compensation_amount", "N/A")[:60])
        return result
    except Exception as e:
        log.error("[fir_context] FAILED: %s", e)
        return {
            "incident_summary": original_msg,
            "compensation_amount": "[______]",
        }


# ── EXECUTE NODE ─────────────────────────────────────────────
# Cost: 2 LLM calls (incident summary + conversational summary)
# Also: template filling (zero LLM) + DB save

def execute_node(state: BotState) -> dict:
    """
    Execute an action: fill templates + generate summary + save complaint.
    action_id comes from state.current_action (set by manager).
    """
    action_id = state.get("current_action")
    log.info("[execute] action=%s", action_id)

    if not action_id:
        return {
            "response_ready": True,
            "messages": [AIMessage(content="I didn't understand. Could you try again?")],
            "turn_output": {"response": "I didn't understand. Could you try again?"},
        }

    language = _get_lang(state.get("language", "en"))
    authority_info = state.get("authority_info", {})
    result = {"response": ""}

    # ── Step 0: Generate FIR context — summary + compensation from RAG (1 LLM call) ──
    if action_id in ("file_complaint", "file_cpgrams", "compensation_info"):
        fir_ctx = _generate_fir_context(state)
        incident_summary = fir_ctx.get("incident_summary")
        compensation_amount = fir_ctx.get("compensation_amount")
    else:
        incident_summary = None
        compensation_amount = None

    # ── Step 1: Template filling (zero LLM) ──
    if action_id == "file_complaint":
        template_state = {**state, "current_action": "file_complaint",
                          "incident_summary": incident_summary,
                          "compensation_amount": compensation_amount}
        complaint = fill_complaint(template_state)
        result["complaint_draft"] = complaint.get("filled_text")
        result["authority"] = authority_info.get("primary_authority")
        result["cpgrams_ref"] = complaint.get("tracking_ref")
        result["follow_up_date"] = complaint.get("follow_up_date")
        if authority_info.get("compensation_eligible"):
            result["compensation"] = "Eligible for compensation under Railways Act"
        state_for_prompt = {**state,
                            "cpgrams_ref": complaint.get("tracking_ref"),
                            "follow_up_date": complaint.get("follow_up_date")}

    elif action_id == "file_cpgrams":
        cpgrams = fill_cpgrams({**state, "incident_summary": incident_summary,
                                "compensation_amount": compensation_amount})
        result["complaint_draft"] = cpgrams.get("filled_text")
        result["cpgrams_ref"] = cpgrams.get("tracking_ref")
        result["follow_up_date"] = cpgrams.get("follow_up_date")
        state_for_prompt = {**state,
                            "cpgrams_ref": cpgrams.get("tracking_ref"),
                            "follow_up_date": cpgrams.get("follow_up_date")}

    elif action_id == "compensation_info":
        template_state = {**state, "current_action": "compensation_info",
                          "incident_summary": incident_summary,
                          "compensation_amount": compensation_amount}
        rct = fill_complaint(template_state)
        result["complaint_draft"] = rct.get("filled_text")
        result["compensation"] = "See details in response"
        state_for_prompt = state

    elif action_id == "know_authority":
        result["authority"] = authority_info.get("primary_authority")
        state_for_prompt = state

    elif action_id == "know_rights":
        state_for_prompt = state

    elif action_id == "check_status":
        try:
            db = get_db()
            latest_msg = _get_latest_human_message(state)

            # 1. Check if user mentioned a specific ref number (e.g. RM-20260301-CD078A)
            import re
            ref_match = re.search(r'RM-\d{8}-[A-F0-9]{6}', latest_msg, re.IGNORECASE)

            if ref_match:
                # User asked about a specific complaint
                rows = db.execute("""
                    SELECT ref, status, incident_type, date_filed, officer_note
                    FROM complaints WHERE user_id = ? AND ref = ?
                """, (state.get("user_id", ""), ref_match.group(0).upper())).fetchall()
            else:
                # No specific ref → return only the most recent complaint
                rows = db.execute("""
                    SELECT ref, status, incident_type, date_filed, officer_note
                    FROM complaints WHERE user_id = ?
                    ORDER BY date_filed DESC LIMIT 1
                """, (state.get("user_id", ""),)).fetchall()

            user_complaints = [dict(r) for r in rows]
            db.close()
        except Exception as e:
            log.error("[execute] check_status query failed: %s", e)
            user_complaints = []
        state_for_prompt = {**state, "user_complaints": user_complaints}

    else:
        state_for_prompt = state

    # ── Step 2: Conversational summary (1 LLM call) ──
    # Sanitize original_message for Azure content filter compliance
    user_msg_for_llm = state.get("original_message", "")
    if state.get("sensitive_content"):
        user_msg_for_llm = _sanitize_message(
            user_msg_for_llm, state.get("incident_type", "general"),
            state.get("entities", {}))
        # Also sanitize the state copy so build_conditional_sections is clean
        state_for_prompt = {**state_for_prompt,
                            "original_message": user_msg_for_llm}

    try:
        client = get_openai_client()
        conditional = build_conditional_sections(action_id, state_for_prompt)
        system_prompt = RESPONSE_GENERATION_SYSTEM.format(
            language=language,
            conditional_sections=conditional,
        )
        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg_for_llm},
            ],
            temperature=0.3,
            max_tokens=400,
        )
        result["response"] = response.choices[0].message.content
        log.info("[execute] DONE — action=%s", action_id)
    except Exception as e:
        log.error("[execute] LLM FAILED: %s", e)
        result["response"] = "Your request has been processed. Please check the details below."

    # ── Step 3: Save complaint to Neo4j ──
    if action_id in ("file_complaint", "file_cpgrams"):
        try:
            tracking_ref = result.get("cpgrams_ref", "")
            entities = state.get("entities", {})
            saved = save_complaint(state["user_id"], {
                "ref": tracking_ref,
                "incident_type": state.get("incident_type", "general"),
                "complaint_text": result.get("complaint_draft", ""),
                "date_filed": datetime.now().isoformat(),
                "authority": authority_info.get("primary_authority", ""),
                "user_message": state.get("original_message", ""),
                "severity": state.get("severity", "medium"),
                "from_station": entities.get("from_station", ""),
                "to_station": entities.get("to_station", ""),
            })
            if saved:
                result["complaint_saved"] = True
                log.info("[execute] Complaint saved: ref=%s", tracking_ref)
        except Exception as e:
            log.error("[execute] Save failed: %s", e)

    return {
        "response_ready": True,
        "detected_action": None,
        "messages": [AIMessage(content=result["response"])],
        "turn_output": result,
    }


# ── Build Graph ──────────────────────────────────────────────

_checkpointer = MemorySaver()
_compiled_graph = None


def _build_graph() -> StateGraph:
    """
    Manager Agent graph — cyclic.

    START → manager → {classify, execute, respond} → manager → END

    Manager runs multiple times per turn:
    1. Decides: classify needed? → classify → back to manager
    2. Decides: execute or respond? → tool → back to manager
    3. Sees response_ready → done → END
    """
    graph = StateGraph(BotState)

    graph.add_node("manager", manager_node)
    graph.add_node("classify", classify_node)
    graph.add_node("execute", execute_node)
    graph.add_node("respond", respond_node)

    # Entry: always manager first
    graph.add_edge(START, "manager")

    # Manager routes to tools (or END)
    graph.add_conditional_edges("manager", lambda s: s.get("next_step", "done"), {
        "classify": "classify",
        "execute": "execute",
        "respond": "respond",
        "done": END,
    })

    # All tools return to manager (cyclic)
    graph.add_edge("classify", "manager")
    graph.add_edge("execute", "manager")
    graph.add_edge("respond", "manager")

    return graph


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph().compile(checkpointer=_checkpointer)
        log.info("[graph] v3 compiled — manager + 3 tools, cyclic, MemorySaver")
    return _compiled_graph


# ── Entry Point ──────────────────────────────────────────────

async def run_agent(user_id: str, message: str, language: str = "en") -> dict:
    """
    Run the Jan Suraksha Bot v3 agent.

    State persists across turns via LangGraph MemorySaver.
    Per-turn flags are reset here so the manager starts fresh each turn.
    """
    log.info("=" * 60)
    log.info("[run_agent] user=%s, lang=%s, msg=%.80s...", user_id, language, message)

    graph = _get_graph()
    config = {"configurable": {"thread_id": user_id}}

    input_state = {
        "messages": [HumanMessage(content=message)],
        "user_id": user_id,
        "language": language,
        # Reset per-turn flags so manager starts fresh
        # NOTE: sensitive_content is NOT reset — it persists via checkpoint
        # so execute_node on turn 2 still knows to sanitize the original_message
        "classified_this_turn": False,
        "response_ready": False,
        "current_action": None,
        "respond_mode": None,
        "detected_action": None,
    }

    result = await asyncio.to_thread(graph.invoke, input_state, config)

    output = result.get("turn_output", {"response": "Unable to process request."})
    log.info("[run_agent] DONE — output_keys=%s", list(output.keys()))
    log.info("=" * 60)

    return output