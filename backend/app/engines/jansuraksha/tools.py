"""
Jan Suraksha Bot v2 — Thin Tool Wrappers.

All heavy logic moved to mappings.py and templates.py.
These wrappers exist for backward compatibility with the agent.
"""

from app.engines.jansuraksha.mappings import get_authority_info, get_suggested_actions
from app.engines.jansuraksha.templates import fill_template, get_templates_for_action
from app.utils.logger import get_logger

log = get_logger("jansuraksha.tools")


def identify_authority(state: dict) -> dict:
    """Pure dict lookup — zero LLM, zero embed calls."""
    incident_type = state.get("incident_type", "general")
    user_context = state.get("user_context", {})
    log.info("[identify_authority] incident=%s (rule-based)", incident_type)
    return get_authority_info(incident_type, user_context)


def suggest_actions(state: dict) -> list[dict]:
    """Rule-based action suggestions — zero LLM calls."""
    incident_type = state.get("incident_type", "general")
    language = state.get("language", "en")
    log.info("[suggest_actions] incident=%s, lang=%s (rule-based)", incident_type, language)
    return get_suggested_actions(incident_type, language)


def fill_complaint(state: dict) -> dict:
    """
    Fill the appropriate complaint template(s) for the given action.
    Returns dict with filled text, tracking ref, and metadata.
    """
    action_id = state.get("current_action", "file_complaint")
    incident_type = state.get("incident_type", "general")
    log.info("[fill_complaint] action=%s, incident=%s (template-based)", action_id, incident_type)

    template_types = get_templates_for_action(action_id, incident_type)
    if not template_types:
        template_types = ["grp_fir"]

    results = []
    for ttype in template_types:
        result = fill_template(ttype, state)
        results.append(result)
        log.info("[fill_complaint] Filled %s template (%d chars)",
                 ttype, len(result["filled_text"]))

    # Combine multiple templates
    if len(results) == 1:
        return results[0]

    combined_text = "\n\n".join(r["filled_text"] for r in results)
    return {
        "template_type": "+".join(r["template_type"] for r in results),
        "filled_text": combined_text,
        "tracking_ref": results[0]["tracking_ref"],
        "follow_up_date": results[0]["follow_up_date"],
        "language": results[0]["language"],
        "slots_filled": results[0]["slots_filled"],
        "slots_missing": results[0]["slots_missing"],
    }


def fill_cpgrams(state: dict) -> dict:
    """Fill CPGRAMS template — redirects to templates.fill_template."""
    log.info("[fill_cpgrams] Filling CPGRAMS template")
    return fill_template("cpgrams", state)