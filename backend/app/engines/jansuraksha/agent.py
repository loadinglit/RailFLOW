"""
Jan Suraksha Bot — LangGraph Agent (v4 — Checkpointing + Intent Detection).

Uses LangGraph's MemorySaver for automatic state persistence across turns.
Conversation history tracked via `add_messages` reducer.
Single compiled graph handles all turns via conditional routing.

Flow:
  Turn 1 (clear intent): "help me file a complaint" → analyze → AUTO-EXECUTE → result
  Turn 1 (no intent):    "someone stole my phone"   → analyze → show options
  Turn 2: User picks option → execute → return result
  Turn 3+: Follow-ups OR pick another option — full conversation context
"""

import json
import asyncio
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage

from app.core import get_openai_client, MODEL_SMART, MODEL_FAST
from app.engines.jansuraksha.neo4j_context import load_user_context
from app.engines.jansuraksha.retrieval import retrieve_legal_context
from app.engines.jansuraksha.tools import identify_authority, draft_complaint, fill_cpgrams
from app.utils.logger import get_logger

log = get_logger("jansuraksha.agent")


# ── State Definition ───────────────────────────────────────────

class BotState(TypedDict, total=False):
    # Conversation history (auto-appended via add_messages reducer)
    messages: Annotated[list[AnyMessage], add_messages]

    # Identity
    user_id: str
    original_message: str
    language: str

    # Analysis (set in Turn 1, persists across turns via checkpoint)
    user_context: dict
    incident_type: str
    detected_action: str  # Auto-detected intent from user's message (or None)
    legal_context: list
    authority_info: dict
    suggested_actions: list

    # Workflow phase tracking
    phase: str  # "options_shown" | "action_done"

    # Per-turn output (overwritten each graph invocation)
    turn_output: dict


# ── Helpers ─────────────────────────────────────────────────────

def _get_lang(lang_code: str) -> str:
    return {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(lang_code, "English")


def _get_latest_human_message(state: dict) -> str:
    """Extract the most recent user message from the messages list."""
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def _parse_choice(message: str, actions: list[dict]) -> str | None:
    """Parse user's message as an action choice (number, id, or label match)."""
    msg = message.strip()

    # Number: "1", "2", "3"
    if msg.isdigit():
        idx = int(msg) - 1
        if 0 <= idx < len(actions):
            log.info("[parse_choice] Number %s → %s", msg, actions[idx]["id"])
            return actions[idx]["id"]

    # Exact action id
    msg_lower = msg.lower()
    for action in actions:
        if msg_lower == action["id"]:
            return action["id"]

    # Label keyword match
    for action in actions:
        label_lower = action["label"].lower()
        if label_lower in msg_lower or msg_lower in label_lower:
            return action["id"]

    return None


# ── Router (Conditional Edge from START) ────────────────────────

def route_from_start(state: BotState) -> str:
    """
    Decide which path to take based on conversation phase.

    - No phase → initial analysis pipeline (Turn 1)
    - options_shown + valid choice → execute action (Turn 2)
    - options_shown + invalid → re-analyze as new grievance
    - action_done + valid choice → execute another action
    - action_done + non-choice → follow-up conversation
    """
    phase = state.get("phase")

    if not phase:
        log.info("[router] No phase → initial")
        return "initial"

    latest = _get_latest_human_message(state)
    actions = state.get("suggested_actions", [])

    if phase == "options_shown":
        choice = _parse_choice(latest, actions)
        if choice:
            log.info("[router] options_shown + choice=%s → execute", choice)
            return "execute"
        log.info("[router] options_shown + no match → initial (new grievance)")
        return "initial"

    if phase == "action_done":
        choice = _parse_choice(latest, actions)
        if choice:
            log.info("[router] action_done + another choice=%s → execute", choice)
            return "execute"
        log.info("[router] action_done + follow-up → follow_up")
        return "follow_up"

    return "initial"


# ── Turn 1 Nodes (Analysis Pipeline) ───────────────────────────

def node_load_context(state: BotState) -> dict:
    """Load user context from Neo4j and capture the original message."""
    user_id = state["user_id"]
    original_msg = _get_latest_human_message(state)
    log.info("[load_context] user=%s, message=%.60s...", user_id, original_msg)

    try:
        ctx = load_user_context(user_id)
        log.info("[load_context] Found=%s, name=%s, route=%s→%s (%s)",
                 ctx.get("found"), ctx.get("name"), ctx.get("origin"),
                 ctx.get("destination"), ctx.get("line"))
        return {"user_context": ctx, "original_message": original_msg}
    except Exception as e:
        log.error("[load_context] FAILED: %s", e, exc_info=True)
        return {
            "user_context": {"user_id": user_id, "found": False},
            "original_message": original_msg,
        }


def node_classify_incident(state: BotState) -> dict:
    """
    Classify incident type AND detect user's action intent in one LLM call.

    If the user explicitly asks to DO something (e.g. "help me file a complaint"),
    detected_action is set and the pipeline auto-executes without showing options.
    If the user just describes an incident, detected_action stays None → show options.
    """
    message = state.get("original_message", "")
    log.info("[classify] %.80s...", message)

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {
                    "role": "system",
                    "content": """You are an analyzer for Indian Railway passenger complaints.
Given a message (may be in English, Hindi, or Marathi), determine TWO things:

1. incident_type — what happened
   Must be one of: theft, robbery, assault, sexual_harassment, accident, falling,
   death, platform_gap, overcrowding, delay, nuisance, chain_pulling, corruption,
   staff_misconduct, infrastructure, stampede, general

2. user_intent — what the user wants to DO about it
   - file_complaint: User explicitly asks to file/write/draft a complaint
   - know_authority: User asks WHO to contact, WHERE to go, phone numbers
   - compensation_info: User asks about money/compensation they can claim
   - file_cpgrams: User wants to file a government/official grievance
   - know_rights: User asks about their legal rights/protections
   - none: User is JUST DESCRIBING an incident without a clear action request

IMPORTANT: Only return a user_intent other than "none" when the user EXPLICITLY
asks for a specific action. Describing an incident is NOT an intent.

Examples:
- "someone stole my phone on the train" → theft, none
- "help me file a complaint about robbery" → robbery, file_complaint
- "who should I contact for theft?" → theft, know_authority
- "मला धक्का दिला platform वर पडलो" → falling, none
- "I want to file a complaint to Railway police" → robbery, file_complaint
- "how much compensation can I get for falling?" → falling, compensation_info
- "कहाँ complain करूँ?" → general, know_authority

Respond ONLY with JSON: {"incident_type": "...", "user_intent": "..."}"""
                },
                {"role": "user", "content": message}
            ],
            temperature=0,
            max_tokens=60,
        )
        raw = response.choices[0].message.content
        log.debug("[classify] Raw: %s", raw)
        result = json.loads(raw)
        incident_type = result.get("incident_type", "general")
        user_intent = result.get("user_intent", "none")

        detected = user_intent if user_intent != "none" else None
        log.info("[classify] → incident=%s, intent=%s", incident_type, detected or "none")
        return {"incident_type": incident_type, "detected_action": detected}
    except Exception as e:
        log.error("[classify] FAILED: %s", e, exc_info=True)
        return {"incident_type": "general", "detected_action": None}


def node_retrieve_legal(state: BotState) -> dict:
    """Retrieve relevant legal context from Zilliz vector store."""
    incident_type = state.get("incident_type", "general")
    log.info("[retrieve_legal] incident=%s", incident_type)

    try:
        chunks = retrieve_legal_context(
            query=state.get("original_message", ""),
            mode="legal_basis",
            incident_type=incident_type,
            location_scope="mumbai",
            top_k=5,
        )
        log.info("[retrieve_legal] %d chunks retrieved", len(chunks))
        return {"legal_context": chunks}
    except Exception as e:
        log.error("[retrieve_legal] FAILED: %s", e, exc_info=True)
        return {"legal_context": []}


def node_identify_authority(state: BotState) -> dict:
    """Identify the correct authority for the incident."""
    log.info("[identify_authority] incident=%s", state.get("incident_type"))
    try:
        info = identify_authority(state)
        log.info("[identify_authority] → %s", info.get("primary_authority"))
        return {"authority_info": info}
    except Exception as e:
        log.error("[identify_authority] FAILED: %s", e, exc_info=True)
        return {"authority_info": {"primary_authority": "Unknown", "reason": str(e)}}


def route_after_analysis(state: BotState) -> str:
    """
    After analysis pipeline: auto-execute if user had clear intent,
    otherwise show options and let the user choose.
    """
    detected = state.get("detected_action")
    if detected:
        log.info("[route_after_analysis] Clear intent=%s → auto_execute", detected)
        return "auto_execute"
    log.info("[route_after_analysis] No clear intent → show_options")
    return "show_options"


def node_suggest_actions(state: BotState) -> dict:
    """Suggest relevant actions in the user's language, using simple words."""
    log.info("[suggest_actions] Generating options")
    try:
        client = get_openai_client()
        incident_type = state.get("incident_type", "general")
        authority_info = state.get("authority_info", {})
        legal_context = state.get("legal_context", [])
        language = _get_lang(state.get("language", "en"))

        legal_summary = "\n".join([
            f"- {c['section_ref']}: {c['text'][:150]}" for c in legal_context[:3]
        ])

        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an action recommender for Indian Railway passenger grievances.
Suggest 3-4 MOST RELEVANT actions for this specific incident.

LANGUAGE: Write ALL labels and descriptions in {language}.
Write like you're talking to your grandmother — simple, clear, no English
technical words mixed in. NEVER use abbreviations like GRP, RPF, RCT,
CPGRAMS, FIR, IPC. Say what each option DOES in plain words.

Available actions (pick ONLY relevant ones):
- file_complaint: Get a written complaint letter ready to give to the police/railway office
- know_authority: Find out exactly who to call or visit, with phone numbers
- compensation_info: Know how much money you can claim (ONLY for injury/accident/death)
- file_cpgrams: Prepare a government complaint form for official record
- know_rights: Understand what protection the law gives you

RULES:
- Only include compensation_info for physical injury, accident, falling, or death
- Order by what's most useful RIGHT NOW for this person
- Label: 3-5 simple words in {language}
- Description: 1 short sentence in {language}, specific to THIS incident
- 3-4 actions max

Respond ONLY with JSON array:
[{{"id": "action_id", "label": "in {language}", "description": "in {language}"}}]"""
                },
                {
                    "role": "user",
                    "content": f"""Incident type: {incident_type}
Authority: {authority_info.get('primary_authority', 'Unknown')} — {authority_info.get('reason', '')}
Helpline: {authority_info.get('helpline', '')}
Compensation eligible: {authority_info.get('compensation_eligible', False)}

Legal references:
{legal_summary}"""
                }
            ],
            temperature=0.2,
            max_tokens=400,
        )

        raw = response.choices[0].message.content
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        actions = json.loads(clean)
        log.info("[suggest_actions] %d options: %s", len(actions), [a["id"] for a in actions])
        return {"suggested_actions": actions}

    except Exception as e:
        log.error("[suggest_actions] FAILED: %s", e, exc_info=True)
        lang = state.get("language", "en")
        if lang == "hi":
            return {"suggested_actions": [
                {"id": "file_complaint", "label": "शिकायत पत्र बनाएं", "description": "पुलिस/रेलवे को देने के लिए लिखित शिकायत तैयार करें"},
                {"id": "know_authority", "label": "किसे संपर्क करें", "description": "किसको फोन करें या कहाँ जाएं, नंबर के साथ"},
                {"id": "know_rights", "label": "आपके अधिकार जानें", "description": "कानून आपको क्या सुरक्षा देता है यह समझें"},
            ]}
        elif lang == "mr":
            return {"suggested_actions": [
                {"id": "file_complaint", "label": "तक्रार पत्र तयार करा", "description": "पोलीस/रेल्वेला देण्यासाठी लिखित तक्रार तयार करा"},
                {"id": "know_authority", "label": "कुणाला संपर्क करावा", "description": "कुणाला फोन करायचा किंवा कुठे जायचे, नंबरसह"},
                {"id": "know_rights", "label": "तुमचे अधिकार जाणा", "description": "कायदा तुम्हाला काय संरक्षण देतो ते समजून घ्या"},
            ]}
        else:
            return {"suggested_actions": [
                {"id": "file_complaint", "label": "Get complaint letter ready", "description": "Prepare a written complaint to give to the police or railway office"},
                {"id": "know_authority", "label": "Who to contact", "description": "Find out exactly who to call or visit, with phone numbers"},
                {"id": "know_rights", "label": "Know your rights", "description": "Understand what protection the law gives you"},
            ]}


def node_respond_options(state: BotState) -> dict:
    """Generate empathetic acknowledgment. Options are shown as buttons in the UI."""
    log.info("[respond_options] Generating empathetic response")
    try:
        client = get_openai_client()
        incident_type = state.get("incident_type", "general")
        authority_info = state.get("authority_info", {})
        language = _get_lang(state.get("language", "en"))

        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Jan Suraksha Bot — a helpful assistant for Mumbai train passengers.
Respond in {language}. Talk like a caring friend, not a lawyer.

The user described something that happened to them. Say:
1. One sentence of empathy (acknowledge what happened)
2. One sentence about who can help them (use plain words — "railway police" not "GRP")
3. One sentence asking them to pick an option below

That's it. 3 sentences max. Do NOT list the options. Keep it warm and short."""
                },
                {
                    "role": "user",
                    "content": f"User said: {state.get('original_message')}\nThis is a {incident_type} incident, handled by {authority_info.get('primary_authority')}."
                }
            ],
            temperature=0.4,
            max_tokens=150,
        )

        response_text = response.choices[0].message.content
        return {
            "phase": "options_shown",
            "messages": [AIMessage(content=response_text)],
            "turn_output": {
                "response": response_text,
                "options": state.get("suggested_actions"),
                "authority": authority_info.get("primary_authority"),
            },
        }
    except Exception as e:
        log.error("[respond_options] FAILED: %s", e, exc_info=True)
        fallback = "I understand your concern. Please select an option below so I can help you."
        return {
            "phase": "options_shown",
            "messages": [AIMessage(content=fallback)],
            "turn_output": {
                "response": fallback,
                "options": state.get("suggested_actions"),
            },
        }


# ── Turn 2: Action Execution ──────────────────────────────────

def _generate_action_response(action_id: str, state: dict) -> dict:
    """
    Execute a chosen action using the persisted analysis state.
    Returns a dict with response + any relevant artifacts.
    """
    lang = _get_lang(state.get("language", "en"))
    client = get_openai_client()
    authority_info = state.get("authority_info", {})

    if action_id == "file_complaint":
        complaint = draft_complaint(state)
        cpgrams = fill_cpgrams(state)

        comp_text = None
        if authority_info.get("compensation_eligible"):
            comp_text = "Eligible for compensation under Railways Act"

        response = client.chat.completions.create(
            model=MODEL_SMART,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Jan Suraksha Bot. Respond in {lang}. Use simple words.
NEVER use abbreviations (GRP, RPF, FIR, CPGRAMS, RCT, IPC). Use plain words.

Give the user a SHORT summary in bullet points:
- Who to call + phone number (use "railway police" not "GRP")
- Your complaint letter is ready (they can view it below)
- Government complaint details are prepared — submit at pgportal.gov.in
- Reference number for tracking
- When to follow up

Maximum 6 bullet points. No paragraphs. No lectures. Just the facts they need."""
                },
                {
                    "role": "user",
                    "content": f"""Incident: {state.get('incident_type')}
Authority: {authority_info.get('primary_authority')} — Helpline: {authority_info.get('helpline')}
Complaint ready: Yes
Reference: {cpgrams.get('tracking_ref', 'N/A')}
Follow up by: {cpgrams.get('follow_up_date', 'N/A')}
Compensation: {authority_info.get('compensation_eligible')}"""
                }
            ],
            temperature=0.3,
            max_tokens=400,
        )

        return {
            "response": response.choices[0].message.content,
            "complaint_draft": complaint.get("complaint_draft"),
            "authority": authority_info.get("primary_authority"),
            "compensation": comp_text,
            "cpgrams_ref": cpgrams.get("tracking_ref"),
            "follow_up_date": cpgrams.get("follow_up_date"),
        }

    elif action_id == "know_authority":
        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Jan Suraksha Bot. Respond in {lang}.
NEVER use abbreviations. Say "railway police" not "GRP", "railway security" not "RPF".

Give ONLY these 3 things:
1. WHO to call — full name + phone number
2. WHERE to go — nearest office/station
3. WHAT to say — a one-line script they can use

Maximum 4-5 lines total. No paragraphs. No extra explanation."""
                },
                {
                    "role": "user",
                    "content": f"Incident: {state.get('incident_type')}\nAuthority: {authority_info.get('primary_authority')}\nHelpline: {authority_info.get('helpline')}\nContact: {authority_info.get('contact')}"
                }
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return {
            "response": response.choices[0].message.content,
            "authority": authority_info.get("primary_authority"),
        }

    elif action_id == "compensation_info":
        legal_context = state.get("legal_context", [])
        comp_chunks = [c for c in legal_context if c.get("compensation_eligible")]
        context = "\n".join([f"- {c['section_ref']}: {c['text'][:200]}" for c in comp_chunks[:3]])

        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Jan Suraksha Bot. Respond in {lang}. Simple words only.

Give ONLY:
1. How much money they can claim (exact amounts in Rupees)
2. Where to apply (one line)
3. What documents to bring (short list)

Maximum 5-6 lines. No paragraphs. Just the numbers and steps."""
                },
                {
                    "role": "user",
                    "content": f"Incident: {state.get('incident_type')}\nLegal context:\n{context}"
                }
            ],
            temperature=0.3,
            max_tokens=250,
        )
        return {
            "response": response.choices[0].message.content,
            "compensation": "See details in response",
        }

    elif action_id == "file_cpgrams":
        cpgrams = fill_cpgrams(state)

        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Jan Suraksha Bot. Respond in {lang}. Simple words only.

Tell the user in 4 lines:
1. We have PREPARED (not submitted) all details for a government complaint
2. To submit: visit pgportal.gov.in or go to the nearest railway office
3. Your reference number is [give it]
4. Follow up after [date] if no response

Do NOT say the form is "filed" or "pre-filled" — we only prepared the details."""
                },
                {
                    "role": "user",
                    "content": f"Reference: {cpgrams.get('tracking_ref', 'N/A')}\nFollow-up: {cpgrams.get('follow_up_date', 'N/A')}"
                }
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return {
            "response": response.choices[0].message.content,
            "cpgrams_ref": cpgrams.get("tracking_ref"),
            "follow_up_date": cpgrams.get("follow_up_date"),
        }

    elif action_id == "know_rights":
        legal_context = state.get("legal_context", [])
        context = "\n".join([f"- {c['section_ref']}: {c['text'][:200]}" for c in legal_context[:4]])

        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are Jan Suraksha Bot. Respond in {lang}. Simple words only.

Tell the user their 3 most important rights for this situation.
Each right: one sentence. You can mention the law section number but
ALWAYS explain what it means in plain words right after.

Maximum 3-4 bullet points. No paragraphs."""
                },
                {
                    "role": "user",
                    "content": f"Incident: {state.get('incident_type')}\nLegal context:\n{context}"
                }
            ],
            temperature=0.3,
            max_tokens=250,
        )
        return {"response": response.choices[0].message.content}

    else:
        log.warning("[execute] Unknown action: %s", action_id)
        return {"response": "Unknown action. Please try again."}


def node_execute_action(state: BotState) -> dict:
    """
    Execute an action — either auto-detected from Turn 1 intent,
    or manually chosen by the user in Turn 2+.
    """
    # 1. Check for auto-detected action (Turn 1 with clear intent)
    action_id = state.get("detected_action")

    # 2. Otherwise parse from user's message (Turn 2+ option selection)
    if not action_id:
        latest = _get_latest_human_message(state)
        actions = state.get("suggested_actions", [])
        action_id = _parse_choice(latest, actions)

    log.info("[execute_action] action=%s", action_id)

    if not action_id:
        fallback = "I didn't understand your choice. Please select an option."
        return {
            "messages": [AIMessage(content=fallback)],
            "turn_output": {"response": fallback},
        }

    result = _generate_action_response(action_id, state)
    response_text = result.get("response", "")

    return {
        "phase": "action_done",
        "detected_action": None,  # Clear after use so it doesn't persist
        "messages": [AIMessage(content=response_text)],
        "turn_output": result,
    }


# ── Turn 3+: Follow-up ────────────────────────────────────────

def node_follow_up(state: BotState) -> dict:
    """Handle follow-up messages using full conversation history from checkpoint."""
    language = _get_lang(state.get("language", "en"))
    authority_info = state.get("authority_info", {})
    user_ctx = state.get("user_context", {})

    log.info("[follow_up] %d messages in history", len(state.get("messages", [])))

    client = get_openai_client()

    system_msg = f"""You are Jan Suraksha Bot — a helpful assistant for Mumbai train passengers.
Respond in {language}. Use simple everyday language. Talk like a caring friend.
NEVER use abbreviations (GRP, RPF, RCT, CPGRAMS, FIR, IPC). Use plain words.

You are already helping this user with a railway incident:
- Incident type: {state.get('incident_type')}
- Authority: {authority_info.get('primary_authority')} (helpline: {authority_info.get('helpline')})
- Route: {user_ctx.get('origin', '?')} → {user_ctx.get('destination', '?')} ({user_ctx.get('line', '?')} line)
- Name: {user_ctx.get('name', 'Passenger')}

The user is sending a follow-up — additional details, a question, or a request for more help.
Respond helpfully and concisely. Maximum 4-5 sentences.
If they give new details (time, platform, etc.), acknowledge them and explain
how it helps their case."""

    # Convert LangGraph messages to OpenAI chat format
    llm_messages = [{"role": "system", "content": system_msg}]
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            llm_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            llm_messages.append({"role": "assistant", "content": msg.content})

    response = client.chat.completions.create(
        model=MODEL_FAST,
        messages=llm_messages,
        temperature=0.3,
        max_tokens=300,
    )

    response_text = response.choices[0].message.content
    return {
        "messages": [AIMessage(content=response_text)],
        "turn_output": {"response": response_text},
    }


# ── Build & Compile Graph ─────────────────────────────────────

_checkpointer = MemorySaver()
_compiled_graph = None


def _build_graph() -> StateGraph:
    """
    Build a single graph that handles all conversation turns.

    START → route_from_start (conditional)
      ├─ "initial" → load_context → classify → retrieve → authority → route_after_analysis
      │     ├─ "auto_execute" → execute_action → END   (user had clear intent)
      │     └─ "show_options" → suggest → respond_options → END   (ask user)
      ├─ "execute"   → execute_action → END   (Turn 2 option selection)
      └─ "follow_up" → follow_up → END         (Turn 3+ conversation)
    """
    graph = StateGraph(BotState)

    # Turn 1 nodes (initial analysis pipeline)
    graph.add_node("load_context", node_load_context)
    graph.add_node("classify_incident", node_classify_incident)
    graph.add_node("retrieve_legal", node_retrieve_legal)
    graph.add_node("identify_authority", node_identify_authority)
    graph.add_node("suggest_actions", node_suggest_actions)
    graph.add_node("respond_options", node_respond_options)

    # Action execution node (shared by auto-execute and manual selection)
    graph.add_node("execute_action", node_execute_action)

    # Turn 3+ node
    graph.add_node("follow_up", node_follow_up)

    # ── Routing from START based on conversation phase ──
    graph.add_conditional_edges(START, route_from_start, {
        "initial": "load_context",
        "execute": "execute_action",
        "follow_up": "follow_up",
    })

    # ── Turn 1 pipeline ──
    graph.add_edge("load_context", "classify_incident")
    graph.add_edge("classify_incident", "retrieve_legal")
    graph.add_edge("retrieve_legal", "identify_authority")

    # After analysis: auto-execute if clear intent, else show options
    graph.add_conditional_edges("identify_authority", route_after_analysis, {
        "auto_execute": "execute_action",
        "show_options": "suggest_actions",
    })

    graph.add_edge("suggest_actions", "respond_options")
    graph.add_edge("respond_options", END)

    # Terminal edges
    graph.add_edge("execute_action", END)
    graph.add_edge("follow_up", END)

    return graph


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph().compile(checkpointer=_checkpointer)
        log.info("[graph] Compiled with MemorySaver checkpointer")
    return _compiled_graph


# ── Entry Point ────────────────────────────────────────────────

async def run_agent(user_id: str, message: str, language: str = "en") -> dict:
    """
    Run the Jan Suraksha Bot agent.

    State is automatically persisted across turns via LangGraph's MemorySaver.
    Each user_id maps to a separate thread — full conversation isolation.
    No manual session store needed.
    """
    log.info("=" * 60)
    log.info("[run_agent] user=%s, lang=%s, message=%.80s...", user_id, language, message)

    graph = _get_graph()
    config = {"configurable": {"thread_id": user_id}}

    input_state = {
        "messages": [HumanMessage(content=message)],
        "user_id": user_id,
        "language": language,
    }

    result = await asyncio.to_thread(graph.invoke, input_state, config)

    output = result.get("turn_output", {"response": "Unable to process request."})
    log.info("[run_agent] DONE — phase=%s, output_keys=%s",
             result.get("phase"), list(output.keys()))
    log.info("=" * 60)

    return output