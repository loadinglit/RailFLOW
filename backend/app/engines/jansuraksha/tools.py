"""
Jan Suraksha Bot — LangGraph Tool Functions.

Three tools called by the agent:
1. identify_authority — who to contact (GRP/RPF/RCT)
2. draft_complaint — generate formal complaint letter
3. fill_cpgrams — pre-fill CPGRAMS grievance payload
"""

import uuid
from datetime import datetime, timedelta

from app.core import get_openai_client, MODEL_SMART
from app.engines.jansuraksha.retrieval import retrieve_legal_context
from app.utils.logger import get_logger

log = get_logger("jansuraksha.tools")


def identify_authority(state: dict) -> dict:
    """
    Determine the correct authority (GRP/RPF/RCT/CPGRAMS) based on
    incident type, location, and legal context.
    """
    incident_type = state.get("incident_type", "general")
    station = state.get("user_context", {}).get("origin", "Unknown")
    line = state.get("user_context", {}).get("line", "WR")

    log.info("[identify_authority] incident=%s, station=%s, line=%s", incident_type, station, line)

    # Retrieve jurisdiction-specific chunks
    chunks = retrieve_legal_context(
        query=f"{incident_type} authority jurisdiction {station}",
        mode="identify_authority",
        incident_type=incident_type,
        location_scope="mumbai",
        top_k=3,
    )
    log.debug("[identify_authority] Retrieved %d jurisdiction chunks", len(chunks))

    # Authority mapping based on incident type
    authority_map = {
        "theft": {"primary": "GRP", "helpline": "022-22694727", "reason": "Theft is a cognizable IPC offence handled by Government Railway Police"},
        "robbery": {"primary": "GRP", "helpline": "022-22694727", "reason": "Robbery is an IPC offence — file FIR at GRP station"},
        "assault": {"primary": "GRP", "helpline": "022-22694727", "reason": "Assault/pushing is an IPC offence — file FIR at GRP"},
        "sexual_harassment": {"primary": "GRP", "helpline": "182 / 1512", "reason": "Sexual harassment — call RPF Women Helpline 182 or GRP"},
        "accident": {"primary": "Railway Claims Tribunal", "helpline": "139", "reason": "Railway accident compensation claims go to RCT"},
        "falling": {"primary": "Railway Claims Tribunal", "helpline": "139", "reason": "Falling from train — file at RCT under Section 124A"},
        "death": {"primary": "Railway Claims Tribunal", "helpline": "139", "reason": "Death compensation — file at RCT, minimum Rs. 8 lakh"},
        "platform_gap": {"primary": "Railway Claims Tribunal", "helpline": "139", "reason": "Platform gap injury — RCT claim under Section 123"},
        "overcrowding": {"primary": "CPGRAMS", "helpline": "pgportal.gov.in", "reason": "Systemic overcrowding — file on CPGRAMS under Safety"},
        "delay": {"primary": "CPGRAMS", "helpline": "railmadad.indianrailways.gov.in", "reason": "Chronic delays — file on Rail Madad or CPGRAMS"},
        "nuisance": {"primary": "RPF", "helpline": "182", "reason": "Nuisance/antisocial behavior — report to RPF"},
        "chain_pulling": {"primary": "RPF", "helpline": "182", "reason": "Chain pulling offence handled by RPF under Section 154"},
        "corruption": {"primary": "CVO Railway", "helpline": "1064", "reason": "Corruption — report to Railway Vigilance or ACB"},
        "general": {"primary": "Rail Madad", "helpline": "139", "reason": "General complaint — start with Rail Madad for fastest resolution"},
    }

    auth = authority_map.get(incident_type, authority_map["general"])
    log.info("[identify_authority] → primary=%s, helpline=%s", auth["primary"], auth["helpline"])

    # Enhance with legal context from retrieval
    legal_refs = [c["section_ref"] for c in chunks if c.get("section_ref")]
    compensation = any(c.get("compensation_eligible") for c in chunks)

    return {
        "primary_authority": auth["primary"],
        "reason": auth["reason"],
        "helpline": auth["helpline"],
        "contact": f"Nearest GRP: {station} station ({line} line)" if auth["primary"] == "GRP" else auth["helpline"],
        "legal_references": legal_refs[:3],
        "compensation_eligible": compensation,
        "secondary_options": ["CPGRAMS", "Rail Madad", "Consumer Forum"],
        "retrieved_context": chunks[:2],
    }


def draft_complaint(state: dict) -> dict:
    """
    Generate a formal complaint letter using GPT-4o,
    citing actual section numbers and in the user's language.
    """
    user_ctx = state.get("user_context", {})
    incident_type = state.get("incident_type", "general")
    message = state.get("original_message", "")
    language = state.get("language", "en")
    authority_info = state.get("authority_info", {})

    log.info("[draft_complaint] Drafting for incident=%s, lang=%s, authority=%s",
             incident_type, language, authority_info.get("primary_authority"))

    # Retrieve legal basis for the complaint
    legal_chunks = retrieve_legal_context(
        query=f"{incident_type} legal section compensation remedy",
        mode="legal_basis",
        incident_type=incident_type,
        top_k=4,
    )
    log.debug("[draft_complaint] Retrieved %d legal chunks for context", len(legal_chunks))

    legal_context = "\n\n".join([
        f"[{c['section_ref']}]: {c['text'][:300]}" for c in legal_chunks
    ])

    lang_instruction = {
        "en": "Write the complaint in formal English.",
        "hi": "Write the complaint in formal Hindi (Devanagari script).",
        "mr": "Write the complaint in formal Marathi (Devanagari script).",
    }.get(language, "Write in formal English.")

    log.info("[draft_complaint] Calling LLM (%s) for complaint generation...", MODEL_SMART)
    client = get_openai_client()
    response = client.chat.completions.create(
        model=MODEL_SMART,
        messages=[
            {
                "role": "system",
                "content": f"""You are a legal complaint drafter for Indian Railway passengers.
Draft a formal complaint letter based on the incident described.
{lang_instruction}

IMPORTANT RULES:
- Cite specific section numbers from the Railways Act 1989
- Include the relevant authority (GRP/RPF/RCT) and their jurisdiction
- Include compensation amounts from the Second Schedule if applicable
- Be factual and formal — this is a legal document
- Include date, place, train details, and incident description
- End with a specific demand/request for action

Legal context for reference:
{legal_context}"""
            },
            {
                "role": "user",
                "content": f"""Draft a complaint for:
Complainant: {user_ctx.get('name', 'Passenger')}
User's route: {user_ctx.get('origin', '?')} to {user_ctx.get('destination', '?')} ({user_ctx.get('line', '?')} line)
Train: {user_ctx.get('usual_train', 'Unknown')}
Incident type: {incident_type}
Incident description: {message}
Authority to address: {authority_info.get('primary_authority', 'Railway Authority')}
Date: {datetime.now().strftime('%d/%m/%Y')}"""
            }
        ],
        temperature=0.3,
        max_tokens=1500,
    )

    complaint_text = response.choices[0].message.content
    log.info("[draft_complaint] Complaint generated, length=%d chars", len(complaint_text))

    return {
        "complaint_draft": complaint_text,
        "addressed_to": authority_info.get("primary_authority", "Railway Authority"),
        "sections_cited": [c["section_ref"] for c in legal_chunks],
        "compensation_eligible": any(c.get("compensation_eligible") for c in legal_chunks),
    }


def fill_cpgrams(state: dict) -> dict:
    """
    Generate pre-filled CPGRAMS grievance payload.
    """
    user_ctx = state.get("user_context", {})
    incident_type = state.get("incident_type", "general")
    message = state.get("original_message", "")

    log.info("[fill_cpgrams] Generating payload for incident=%s", incident_type)

    # Map incident types to CPGRAMS categories
    category_map = {
        "theft": "Safety & Security",
        "robbery": "Safety & Security",
        "assault": "Safety & Security",
        "sexual_harassment": "Safety & Security",
        "accident": "Safety & Security",
        "falling": "Safety & Security",
        "overcrowding": "Safety & Security",
        "delay": "Punctuality of Trains",
        "nuisance": "Cleanliness & Hygiene",
        "corruption": "Corruption / Malpractice",
        "staff_misconduct": "Staff Behavior",
        "infrastructure": "Infrastructure",
        "general": "General",
    }

    # Map line to railway zone
    zone_map = {
        "WR": "Western Railway",
        "CR": "Central Railway",
        "HR": "Harbour Line (Central Railway)",
    }

    line = user_ctx.get("line", "WR")
    tracking_ref = f"RM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    cpgrams_payload = {
        "ministry": "Ministry of Railways (Rail Mantralaya)",
        "department": zone_map.get(line, "Western Railway"),
        "category": category_map.get(incident_type, "General"),
        "sub_category": incident_type.replace("_", " ").title(),
        "description": f"""Incident Report — {incident_type.replace('_', ' ').title()}

Complainant: {user_ctx.get('name', 'Passenger')}
Route: {user_ctx.get('origin', 'N/A')} to {user_ctx.get('destination', 'N/A')}
Line: {line}
Train: {user_ctx.get('usual_train', 'N/A')}
Date: {datetime.now().strftime('%d/%m/%Y')}
Time: {user_ctx.get('usual_departure', 'N/A')}

Incident Description:
{message}

Requested Action:
1. Investigation into the incident
2. Appropriate action against the responsible parties
3. Measures to prevent recurrence
4. Compensation as applicable under the Railways Act 1989

Reference: {tracking_ref}""",
        "state": "Maharashtra",
        "district": "Mumbai",
        "tracking_ref": tracking_ref,
        "follow_up_date": (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y"),
    }

    log.info("[fill_cpgrams] tracking_ref=%s, category=%s, department=%s",
             tracking_ref, cpgrams_payload["category"], cpgrams_payload["department"])

    return cpgrams_payload