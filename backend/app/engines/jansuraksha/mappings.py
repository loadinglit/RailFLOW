"""
Jan Suraksha Bot v2 — Rule-Based Mappings.

All authority, action, and label lookups — zero LLM calls.
Replaces LLM-generated suggest_actions and identify_authority.
"""


# ── Authority Map: incident_type → authority details ──────────

AUTHORITY_MAP = {
    "theft": {
        "primary": "Government Railway Police (GRP)",
        "helpline": "022-22694727",
        "reason": "Theft is a cognizable IPC offence — file FIR at nearest GRP station",
        "compensation_eligible": False,
    },
    "robbery": {
        "primary": "Government Railway Police (GRP)",
        "helpline": "022-22694727",
        "reason": "Robbery involves force/threat — file FIR at GRP immediately",
        "compensation_eligible": False,
    },
    "assault": {
        "primary": "Government Railway Police (GRP)",
        "helpline": "022-22694727",
        "reason": "Assault is a cognizable IPC offence — file FIR at GRP",
        "compensation_eligible": False,
    },
    "sexual_harassment": {
        "primary": "Government Railway Police (GRP) / Women Helpline",
        "helpline": "182 / 1512",
        "reason": "Sexual harassment — call RPF Women Helpline 182 or nearest GRP",
        "compensation_eligible": False,
    },
    "accident": {
        "primary": "Railway Claims Tribunal (RCT)",
        "helpline": "139",
        "reason": "Railway accident — file claim at RCT under Section 124A Railways Act",
        "compensation_eligible": True,
    },
    "falling": {
        "primary": "Railway Claims Tribunal (RCT)",
        "helpline": "139",
        "reason": "Falling from train — file claim at RCT under Section 124A Railways Act",
        "compensation_eligible": True,
    },
    "death": {
        "primary": "Railway Claims Tribunal (RCT)",
        "helpline": "139",
        "reason": "Death compensation — RCT claim, minimum Rs. 8 lakh under Second Schedule",
        "compensation_eligible": True,
    },
    "platform_gap": {
        "primary": "Railway Claims Tribunal (RCT)",
        "helpline": "139",
        "reason": "Platform gap injury — RCT claim under Section 123 Railways Act",
        "compensation_eligible": True,
    },
    "overcrowding": {
        "primary": "CPGRAMS / Rail Madad",
        "helpline": "pgportal.gov.in",
        "reason": "Systemic overcrowding — file grievance on CPGRAMS or Rail Madad",
        "compensation_eligible": False,
    },
    "delay": {
        "primary": "Rail Madad / CPGRAMS",
        "helpline": "railmadad.indianrailways.gov.in",
        "reason": "Chronic delays — file on Rail Madad for fastest resolution",
        "compensation_eligible": False,
    },
    "nuisance": {
        "primary": "Railway Protection Force (RPF)",
        "helpline": "182",
        "reason": "Nuisance/antisocial behaviour — report to RPF",
        "compensation_eligible": False,
    },
    "chain_pulling": {
        "primary": "Railway Protection Force (RPF)",
        "helpline": "182",
        "reason": "Chain pulling offence under Section 141 Railways Act — report to RPF",
        "compensation_eligible": False,
    },
    "corruption": {
        "primary": "Chief Vigilance Officer (CVO), Railway",
        "helpline": "1064",
        "reason": "Corruption — report to Railway Vigilance or Anti-Corruption Bureau",
        "compensation_eligible": False,
    },
    "staff_misconduct": {
        "primary": "Rail Madad / Divisional Railway Manager",
        "helpline": "139",
        "reason": "Staff misconduct — report on Rail Madad or to DRM office",
        "compensation_eligible": False,
    },
    "infrastructure": {
        "primary": "Rail Madad",
        "helpline": "139",
        "reason": "Infrastructure issues — report on Rail Madad portal",
        "compensation_eligible": False,
    },
    "stampede": {
        "primary": "Government Railway Police (GRP) / District Administration",
        "helpline": "022-22694727 / 112",
        "reason": "Stampede — emergency, contact GRP and local emergency services",
        "compensation_eligible": True,
    },
    "general": {
        "primary": "Rail Madad",
        "helpline": "139",
        "reason": "General complaint — start with Rail Madad for fastest resolution",
        "compensation_eligible": False,
    },
}


# ── Action Map: incident_type → ordered list of relevant action_ids ──

ACTION_MAP = {
    "theft":              ["file_complaint", "know_authority", "know_rights"],
    "robbery":            ["file_complaint", "know_authority", "know_rights"],
    "assault":            ["file_complaint", "know_authority", "know_rights"],
    "sexual_harassment":  ["file_complaint", "know_authority", "know_rights"],
    "accident":           ["file_complaint", "compensation_info", "know_authority", "know_rights"],
    "falling":            ["file_complaint", "compensation_info", "know_authority", "know_rights"],
    "death":              ["file_complaint", "compensation_info", "know_authority"],
    "platform_gap":       ["file_complaint", "compensation_info", "know_authority", "know_rights"],
    "overcrowding":       ["file_cpgrams", "know_authority", "know_rights"],
    "delay":              ["file_cpgrams", "know_authority"],
    "nuisance":           ["file_complaint", "know_authority"],
    "chain_pulling":      ["file_complaint", "know_authority"],
    "corruption":         ["file_cpgrams", "file_complaint", "know_authority"],
    "staff_misconduct":   ["file_cpgrams", "file_complaint", "know_authority"],
    "infrastructure":     ["file_cpgrams", "know_authority"],
    "stampede":           ["file_complaint", "compensation_info", "know_authority"],
    "general":            ["file_cpgrams", "know_authority", "know_rights"],
}


# ── Action Labels: action_id → {en, hi, mr} labels + descriptions ──

ACTION_LABELS = {
    "file_complaint": {
        "en": {"label": "Get complaint letter ready", "description": "Prepare a written complaint to give to the police or railway office"},
        "hi": {"label": "शिकायत पत्र तैयार करें", "description": "पुलिस या रेलवे कार्यालय को देने के लिए लिखित शिकायत तैयार करें"},
        "mr": {"label": "तक्रार पत्र तयार करा", "description": "पोलीस किंवा रेल्वे कार्यालयाला देण्यासाठी लिखित तक्रार तयार करा"},
    },
    "know_authority": {
        "en": {"label": "Who to contact", "description": "Find out exactly who to call or visit, with phone numbers"},
        "hi": {"label": "किसे संपर्क करें", "description": "किसको फोन करें या कहाँ जाएं, नंबर के साथ"},
        "mr": {"label": "कुणाला संपर्क करावा", "description": "कुणाला फोन करायचा किंवा कुठे जायचे, नंबरसह"},
    },
    "compensation_info": {
        "en": {"label": "Know compensation amount", "description": "Find out how much money you can claim and where to apply"},
        "hi": {"label": "मुआवज़ा राशि जानें", "description": "कितना पैसा मिल सकता है और कहाँ आवेदन करें"},
        "mr": {"label": "भरपाई रक्कम जाणा", "description": "किती पैसे मिळू शकतात आणि कुठे अर्ज करावा"},
    },
    "file_cpgrams": {
        "en": {"label": "File government complaint", "description": "Prepare a formal grievance for the government portal"},
        "hi": {"label": "सरकारी शिकायत दर्ज करें", "description": "सरकारी पोर्टल के लिए औपचारिक शिकायत तैयार करें"},
        "mr": {"label": "सरकारी तक्रार दाखल करा", "description": "सरकारी पोर्टलसाठी औपचारिक तक्रार तयार करा"},
    },
    "know_rights": {
        "en": {"label": "Know your rights", "description": "Understand what protection the law gives you"},
        "hi": {"label": "अपने अधिकार जानें", "description": "कानून आपको क्या सुरक्षा देता है यह समझें"},
        "mr": {"label": "तुमचे अधिकार जाणा", "description": "कायदा तुम्हाला काय संरक्षण देतो ते समजून घ्या"},
    },
}


# ── Incident Type Labels (with applicable law sections) ──────

INCIDENT_TYPE_LABELS = {
    "theft": {
        "en": "Theft (IPC Section 379)",
        "hi": "चोरी (आईपीसी धारा 379)",
        "mr": "चोरी (आयपीसी कलम 379)",
    },
    "robbery": {
        "en": "Robbery (IPC Section 392)",
        "hi": "लूट/डकैती (आईपीसी धारा 392)",
        "mr": "लूट/दरोडा (आयपीसी कलम 392)",
    },
    "assault": {
        "en": "Assault (IPC Section 351/323)",
        "hi": "मारपीट (आईपीसी धारा 351/323)",
        "mr": "मारहाण (आयपीसी कलम 351/323)",
    },
    "sexual_harassment": {
        "en": "Sexual Harassment (IPC 354A / POSH Act)",
        "hi": "यौन उत्पीड़न (आईपीसी 354A / पॉश अधिनियम)",
        "mr": "लैंगिक छळ (आयपीसी 354A / पॉश कायदा)",
    },
    "accident": {
        "en": "Railway Accident (Railways Act Section 124)",
        "hi": "रेल दुर्घटना (रेलवे अधिनियम धारा 124)",
        "mr": "रेल्वे अपघात (रेल्वे कायदा कलम 124)",
    },
    "falling": {
        "en": "Falling from Train (Railways Act Section 124A)",
        "hi": "ट्रेन से गिरना (रेलवे अधिनियम धारा 124A)",
        "mr": "ट्रेनवरून पडणे (रेल्वे कायदा कलम 124A)",
    },
    "death": {
        "en": "Death in Railway Incident (Railways Act Section 124A)",
        "hi": "रेल घटना में मृत्यु (रेलवे अधिनियम धारा 124A)",
        "mr": "रेल्वे घटनेत मृत्यू (रेल्वे कायदा कलम 124A)",
    },
    "platform_gap": {
        "en": "Platform Gap Injury (Railways Act Section 123)",
        "hi": "प्लेटफॉर्म गैप चोट (रेलवे अधिनियम धारा 123)",
        "mr": "प्लॅटफॉर्म गॅप इजा (रेल्वे कायदा कलम 123)",
    },
    "overcrowding": {
        "en": "Overcrowding (Railways Act Section 71)",
        "hi": "भीड़भाड़ (रेलवे अधिनियम धारा 71)",
        "mr": "गर्दी (रेल्वे कायदा कलम 71)",
    },
    "delay": {
        "en": "Train Delay / Cancellation",
        "hi": "ट्रेन में देरी / रद्दीकरण",
        "mr": "ट्रेन उशीर / रद्द",
    },
    "nuisance": {
        "en": "Nuisance (Railways Act Section 145)",
        "hi": "उपद्रव (रेलवे अधिनियम धारा 145)",
        "mr": "उपद्रव (रेल्वे कायदा कलम 145)",
    },
    "chain_pulling": {
        "en": "Chain Pulling (Railways Act Section 141)",
        "hi": "चेन खींचना (रेलवे अधिनियम धारा 141)",
        "mr": "चेन खेचणे (रेल्वे कायदा कलम 141)",
    },
    "corruption": {
        "en": "Corruption (Prevention of Corruption Act)",
        "hi": "भ्रष्टाचार (भ्रष्टाचार निवारण अधिनियम)",
        "mr": "भ्रष्टाचार (भ्रष्टाचार प्रतिबंधक कायदा)",
    },
    "staff_misconduct": {
        "en": "Staff Misconduct",
        "hi": "कर्मचारी दुर्व्यवहार",
        "mr": "कर्मचारी गैरवर्तन",
    },
    "infrastructure": {
        "en": "Infrastructure Issue",
        "hi": "बुनियादी ढाँचे की समस्या",
        "mr": "पायाभूत सुविधा समस्या",
    },
    "stampede": {
        "en": "Stampede (IPC Section 304A / Railways Act)",
        "hi": "भगदड़ (आईपीसी धारा 304A / रेलवे अधिनियम)",
        "mr": "चेंगराचेंगरी (आयपीसी कलम 304A / रेल्वे कायदा)",
    },
    "general": {
        "en": "General Railway Complaint",
        "hi": "सामान्य रेलवे शिकायत",
        "mr": "सामान्य रेल्वे तक्रार",
    },
}


# ── Applicable Law Sections per incident ─────────────────────

APPLICABLE_SECTIONS_MAP = {
    "theft":              "IPC Section 379 (Theft), Railways Act Section 153 (Penalty for trespass and theft on railway)",
    "robbery":            "IPC Section 392 (Robbery), IPC Section 397 (Robbery with attempt to cause death/grievous hurt)",
    "assault":            "IPC Section 351 (Assault), IPC Section 323 (Voluntarily causing hurt), Railways Act Section 145",
    "sexual_harassment":  "IPC Section 354A (Sexual harassment), POSH Act 2013, Railways Act Section 145",
    "accident":           "Railways Act Section 124 (Extent of liability), Section 124A (Compensation for untoward incidents)",
    "falling":            "Railways Act Section 124A (Compensation for untoward incidents including falling from train)",
    "death":              "Railways Act Section 124A, Second Schedule (Minimum Rs. 8 lakh for death)",
    "platform_gap":       "Railways Act Section 123 (Extent of liability for platform gap incidents)",
    "overcrowding":       "Railways Act Section 71 (Overcrowding prohibited), Section 167 (Penalty)",
    "delay":              "Railways Act Section 15 (Punctuality), Consumer Protection Act 2019",
    "nuisance":           "Railways Act Section 145 (Nuisance), IPC Section 290 (Public nuisance)",
    "chain_pulling":      "Railways Act Section 141 (Penalty for pulling alarm chain without cause — Rs. 1000 fine or 1 year imprisonment)",
    "corruption":         "Prevention of Corruption Act 1988, Section 7 (Public servant taking gratification)",
    "staff_misconduct":   "Railways Act Section 153, Railway Servants (Discipline & Appeal) Rules 1968",
    "infrastructure":     "Railways Act Section 13 (General duties of Railway Administration)",
    "stampede":           "IPC Section 304A (Causing death by negligence), Railways Act Section 124A",
    "general":            "Railways Act 1989, Consumer Protection Act 2019",
}


# ── Rail Madad Type Mapping ──────────────────────────────────

RAILMADAD_TYPE_MAP = {
    "theft":              ("Safety & Security", "Theft / Robbery"),
    "robbery":            ("Safety & Security", "Theft / Robbery"),
    "assault":            ("Safety & Security", "Assault / Violence"),
    "sexual_harassment":  ("Safety & Security", "Eve Teasing / Molestation"),
    "accident":           ("Safety & Security", "Train Accident"),
    "falling":            ("Safety & Security", "Falling from Train"),
    "death":              ("Safety & Security", "Death / Fatal Incident"),
    "platform_gap":       ("Safety & Security", "Platform Gap Incident"),
    "overcrowding":       ("Safety & Security", "Overcrowding"),
    "delay":              ("Punctuality", "Train Delay / Cancellation"),
    "nuisance":           ("Cleanliness & Hygiene", "Nuisance / Antisocial Behavior"),
    "chain_pulling":      ("Safety & Security", "Unnecessary Chain Pulling"),
    "corruption":         ("Corruption / Malpractice", "Bribery / Illegal Charging"),
    "staff_misconduct":   ("Staff Behavior", "Rude / Abusive Staff"),
    "infrastructure":     ("Infrastructure", "Broken / Non-functional Facilities"),
    "stampede":           ("Safety & Security", "Stampede / Crowd Crush"),
    "general":            ("General", "General Complaint"),
}


# ── CPGRAMS Category Mapping ────────────────────────────────

CPGRAMS_CATEGORY_MAP = {
    "theft":              "Safety & Security",
    "robbery":            "Safety & Security",
    "assault":            "Safety & Security",
    "sexual_harassment":  "Safety & Security",
    "accident":           "Safety & Security",
    "falling":            "Safety & Security",
    "overcrowding":       "Safety & Security",
    "platform_gap":       "Safety & Security",
    "death":              "Safety & Security",
    "stampede":           "Safety & Security",
    "delay":              "Punctuality of Trains",
    "nuisance":           "Cleanliness & Hygiene",
    "corruption":         "Corruption / Malpractice",
    "staff_misconduct":   "Staff Behavior",
    "infrastructure":     "Infrastructure",
    "chain_pulling":      "Safety & Security",
    "general":            "General",
}


# ── Lookup Functions ─────────────────────────────────────────

def get_authority_info(incident_type: str, user_context: dict = None) -> dict:
    """
    Pure dict lookup + station enrichment. Zero LLM calls.
    Returns authority_info dict compatible with v1 shape.
    """
    user_context = user_context or {}
    auth = AUTHORITY_MAP.get(incident_type, AUTHORITY_MAP["general"])
    station = user_context.get("origin", "your nearest station")
    line = user_context.get("line", "")

    # Build contact string with station info
    if "GRP" in auth["primary"]:
        contact = f"Nearest railway police station: {station} ({line} line)" if line else f"Nearest railway police station: {station}"
    else:
        contact = auth["helpline"]

    return {
        "primary_authority": auth["primary"],
        "reason": auth["reason"],
        "helpline": auth["helpline"],
        "contact": contact,
        "compensation_eligible": auth["compensation_eligible"],
        "secondary_options": ["CPGRAMS (pgportal.gov.in)", "Rail Madad (139)", "Consumer Forum"],
    }


def get_suggested_actions(incident_type: str, language: str = "en") -> list[dict]:
    """
    Returns list of ActionOption-shaped dicts from rule-based mapping.
    Zero LLM calls — instant, deterministic, multilingual.
    """
    action_ids = ACTION_MAP.get(incident_type, ACTION_MAP["general"])

    actions = []
    for action_id in action_ids:
        labels = ACTION_LABELS.get(action_id, {}).get(language)
        if not labels:
            labels = ACTION_LABELS.get(action_id, {}).get("en", {"label": action_id, "description": ""})

        actions.append({
            "id": action_id,
            "label": labels["label"],
            "description": labels["description"],
        })

    return actions