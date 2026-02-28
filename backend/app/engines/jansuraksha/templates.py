"""
Jan Suraksha Bot v2 — Real Portal-Format Complaint Templates.

Replaces LLM-generated complaints with actual FIR/CPGRAMS/RCT formats.
Slot filling from BotState — missing fields marked [______] for user to fill.
"""

import re
import uuid
from datetime import datetime, timedelta

from app.engines.jansuraksha.mappings import (
    APPLICABLE_SECTIONS_MAP,
    RAILMADAD_TYPE_MAP,
    CPGRAMS_CATEGORY_MAP,
)


# ── GRP FIR Template ─────────────────────────────────────────

GRP_FIR_TEMPLATE = {
    "en": """
═══════════════════════════════════════════════════════════════
                    FIRST INFORMATION REPORT (FIR)
                 Government Railway Police, Mumbai
═══════════════════════════════════════════════════════════════

To,
The Station House Officer,
GRP Station: {grp_station}

Subject: FIR for {incident_label}

Date of Report: {report_date}
Time of Report: {report_time}

───────────────────────────────────────────────────────────────
COMPLAINANT DETAILS
───────────────────────────────────────────────────────────────
Name:           {name}
Address:        {address}
Phone:          {phone}

───────────────────────────────────────────────────────────────
INCIDENT DETAILS
───────────────────────────────────────────────────────────────
Date of Incident:    {incident_date}
Time of Incident:    {incident_time}
Train Name/Number:   {train_number}
Class of Travel:     {travel_class}
From Station:        {from_station}
To Station:          {to_station}
Platform Number:     {platform}

───────────────────────────────────────────────────────────────
OFFENCE DETAILS
───────────────────────────────────────────────────────────────
Type of Offence:     {incident_label}
Applicable Sections: {applicable_sections}

Property Lost/Damaged:
{property_details}

Suspect Description:
{suspect_description}

───────────────────────────────────────────────────────────────
INCIDENT DESCRIPTION
───────────────────────────────────────────────────────────────
{incident_description}

───────────────────────────────────────────────────────────────
INJURIES (if any)
───────────────────────────────────────────────────────────────
{injuries}

───────────────────────────────────────────────────────────────

I hereby declare that the above information is true to the best
of my knowledge and belief.

Signature: ____________________
Date: {report_date}

═══════════════════════════════════════════════════════════════
""",

    "hi": """
═══════════════════════════════════════════════════════════════
                  प्रथम सूचना रिपोर्ट (एफआईआर)
               सरकारी रेलवे पुलिस, मुंबई
═══════════════════════════════════════════════════════════════

सेवा में,
थाना प्रभारी,
जीआरपी थाना: {grp_station}

विषय: {incident_label} के लिए एफआईआर

रिपोर्ट दिनांक: {report_date}
रिपोर्ट समय: {report_time}

───────────────────────────────────────────────────────────────
शिकायतकर्ता विवरण
───────────────────────────────────────────────────────────────
नाम:           {name}
पता:            {address}
फोन:           {phone}

───────────────────────────────────────────────────────────────
घटना विवरण
───────────────────────────────────────────────────────────────
घटना दिनांक:       {incident_date}
घटना समय:         {incident_time}
ट्रेन नाम/नंबर:     {train_number}
यात्रा श्रेणी:       {travel_class}
से स्टेशन:         {from_station}
तक स्टेशन:        {to_station}
प्लेटफॉर्म नंबर:     {platform}

───────────────────────────────────────────────────────────────
अपराध विवरण
───────────────────────────────────────────────────────────────
अपराध प्रकार:      {incident_label}
लागू धाराएं:        {applicable_sections}

खोई/क्षतिग्रस्त संपत्ति:
{property_details}

संदिग्ध का विवरण:
{suspect_description}

───────────────────────────────────────────────────────────────
घटना का विवरण
───────────────────────────────────────────────────────────────
{incident_description}

───────────────────────────────────────────────────────────────
चोटें (यदि कोई हो)
───────────────────────────────────────────────────────────────
{injuries}

───────────────────────────────────────────────────────────────

मैं प्रमाणित करता/करती हूँ कि ऊपर दी गई जानकारी मेरी
जानकारी और विश्वास के अनुसार सत्य है।

हस्ताक्षर: ____________________
दिनांक: {report_date}

═══════════════════════════════════════════════════════════════
""",

    "mr": """
═══════════════════════════════════════════════════════════════
                  प्रथम खबरी अहवाल (एफआयआर)
               सरकारी रेल्वे पोलीस, मुंबई
═══════════════════════════════════════════════════════════════

प्रति,
ठाणे प्रमुख,
जीआरपी ठाणे: {grp_station}

विषय: {incident_label} साठी एफआयआर

अहवाल दिनांक: {report_date}
अहवाल वेळ: {report_time}

───────────────────────────────────────────────────────────────
तक्रारदाराचे तपशील
───────────────────────────────────────────────────────────────
नाव:           {name}
पत्ता:          {address}
फोन:           {phone}

───────────────────────────────────────────────────────────────
घटनेचे तपशील
───────────────────────────────────────────────────────────────
घटना दिनांक:       {incident_date}
घटना वेळ:         {incident_time}
ट्रेन नाव/नंबर:     {train_number}
प्रवास वर्ग:        {travel_class}
कुठून स्टेशन:       {from_station}
कुठे स्टेशन:        {to_station}
प्लॅटफॉर्म नंबर:     {platform}

───────────────────────────────────────────────────────────────
गुन्ह्याचे तपशील
───────────────────────────────────────────────────────────────
गुन्ह्याचा प्रकार:    {incident_label}
लागू कलमे:         {applicable_sections}

हरवलेली/नुकसान झालेली मालमत्ता:
{property_details}

संशयिताचे वर्णन:
{suspect_description}

───────────────────────────────────────────────────────────────
घटनेचे वर्णन
───────────────────────────────────────────────────────────────
{incident_description}

───────────────────────────────────────────────────────────────
जखमा (असल्यास)
───────────────────────────────────────────────────────────────
{injuries}

───────────────────────────────────────────────────────────────

मी प्रमाणित करतो/करते की वरील माहिती माझ्या माहिती आणि
विश्वासानुसार सत्य आहे.

सही: ____________________
दिनांक: {report_date}

═══════════════════════════════════════════════════════════════
""",
}


# ── Rail Madad Template ──────────────────────────────────────

RAIL_MADAD_TEMPLATE = {
    "en": """
═══════════════════════════════════════════════════════════════
              RAIL MADAD COMPLAINT FORM
              railmadad.indianrailways.gov.in
═══════════════════════════════════════════════════════════════

Complainant Mobile: {phone}

Type:               {railmadad_type}
Sub-Type:           {railmadad_subtype}

───────────────────────────────────────────────────────────────
COMPLAINT DESCRIPTION
───────────────────────────────────────────────────────────────
{incident_description}

Date of Incident:   {incident_date}
Train Name/Number:  {train_number}
Station:            {from_station}

───────────────────────────────────────────────────────────────
Submit at: railmadad.indianrailways.gov.in
Or call: 139
Tracking Reference: {tracking_ref}
═══════════════════════════════════════════════════════════════
""",

    "hi": """
═══════════════════════════════════════════════════════════════
              रेल मदद शिकायत फॉर्म
              railmadad.indianrailways.gov.in
═══════════════════════════════════════════════════════════════

शिकायतकर्ता मोबाइल: {phone}

प्रकार:              {railmadad_type}
उप-प्रकार:           {railmadad_subtype}

───────────────────────────────────────────────────────────────
शिकायत विवरण
───────────────────────────────────────────────────────────────
{incident_description}

घटना दिनांक:        {incident_date}
ट्रेन नाम/नंबर:      {train_number}
स्टेशन:             {from_station}

───────────────────────────────────────────────────────────────
यहाँ जमा करें: railmadad.indianrailways.gov.in
या कॉल करें: 139
ट्रैकिंग संदर्भ: {tracking_ref}
═══════════════════════════════════════════════════════════════
""",

    "mr": """
═══════════════════════════════════════════════════════════════
              रेल मदद तक्रार फॉर्म
              railmadad.indianrailways.gov.in
═══════════════════════════════════════════════════════════════

तक्रारदार मोबाइल:   {phone}

प्रकार:              {railmadad_type}
उप-प्रकार:           {railmadad_subtype}

───────────────────────────────────────────────────────────────
तक्रार वर्णन
───────────────────────────────────────────────────────────────
{incident_description}

घटना दिनांक:        {incident_date}
ट्रेन नाव/नंबर:      {train_number}
स्टेशन:             {from_station}

───────────────────────────────────────────────────────────────
येथे सादर करा: railmadad.indianrailways.gov.in
किंवा कॉल करा: 139
ट्रॅकिंग संदर्भ: {tracking_ref}
═══════════════════════════════════════════════════════════════
""",
}


# ── CPGRAMS Template ─────────────────────────────────────────

CPGRAMS_TEMPLATE = {
    "en": """
═══════════════════════════════════════════════════════════════
            CPGRAMS GRIEVANCE FORM
            Centralized Public Grievance Redress & Monitoring System
            pgportal.gov.in
═══════════════════════════════════════════════════════════════

Ministry:       Ministry of Railways (Rail Mantralaya)
Department:     {department}
Category:       {cpgrams_category}

───────────────────────────────────────────────────────────────
GRIEVANCE DESCRIPTION
───────────────────────────────────────────────────────────────
{incident_description}

Date of Incident:   {incident_date}
Place of Incident:  {from_station}
Train Number:       {train_number}

───────────────────────────────────────────────────────────────
COMPLAINANT DETAILS
───────────────────────────────────────────────────────────────
Name:           {name}
Phone:          {phone}
Address:        {address}

State:          Maharashtra
District:       Mumbai

───────────────────────────────────────────────────────────────
Tracking Reference: {tracking_ref}
Submit at: pgportal.gov.in
Follow up after:    {follow_up_date}
═══════════════════════════════════════════════════════════════
""",

    "hi": """
═══════════════════════════════════════════════════════════════
            सीपीजीआरएएमएस शिकायत फॉर्म
            केंद्रीकृत लोक शिकायत निवारण एवं निगरानी प्रणाली
            pgportal.gov.in
═══════════════════════════════════════════════════════════════

मंत्रालय:       रेल मंत्रालय (रेल मंत्रालय)
विभाग:         {department}
श्रेणी:          {cpgrams_category}

───────────────────────────────────────────────────────────────
शिकायत विवरण
───────────────────────────────────────────────────────────────
{incident_description}

घटना दिनांक:       {incident_date}
घटना स्थान:        {from_station}
ट्रेन नंबर:         {train_number}

───────────────────────────────────────────────────────────────
शिकायतकर्ता विवरण
───────────────────────────────────────────────────────────────
नाम:           {name}
फोन:           {phone}
पता:            {address}

राज्य:          महाराष्ट्र
जिला:          मुंबई

───────────────────────────────────────────────────────────────
ट्रैकिंग संदर्भ: {tracking_ref}
यहाँ जमा करें: pgportal.gov.in
इसके बाद फॉलो अप करें: {follow_up_date}
═══════════════════════════════════════════════════════════════
""",

    "mr": """
═══════════════════════════════════════════════════════════════
            सीपीजीआरएएमएस तक्रार फॉर्म
            केंद्रीकृत लोक तक्रार निवारण आणि निरीक्षण प्रणाली
            pgportal.gov.in
═══════════════════════════════════════════════════════════════

मंत्रालय:       रेल्वे मंत्रालय (रेल मंत्रालय)
विभाग:         {department}
श्रेणी:          {cpgrams_category}

───────────────────────────────────────────────────────────────
तक्रार वर्णन
───────────────────────────────────────────────────────────────
{incident_description}

घटना दिनांक:       {incident_date}
घटना ठिकाण:       {from_station}
ट्रेन नंबर:         {train_number}

───────────────────────────────────────────────────────────────
तक्रारदाराचे तपशील
───────────────────────────────────────────────────────────────
नाव:           {name}
फोन:           {phone}
पत्ता:          {address}

राज्य:          महाराष्ट्र
जिल्हा:         मुंबई

───────────────────────────────────────────────────────────────
ट्रॅकिंग संदर्भ: {tracking_ref}
येथे सादर करा: pgportal.gov.in
यानंतर फॉलो अप करा: {follow_up_date}
═══════════════════════════════════════════════════════════════
""",
}


# ── RCT Form II Template (Railway Claims Tribunal) ───────────

RCT_FORM_II_TEMPLATE = {
    "en": """
═══════════════════════════════════════════════════════════════
            RAILWAY CLAIMS TRIBUNAL — FORM II
            Application for Compensation
            (Under Section 124A, Railways Act 1989)
═══════════════════════════════════════════════════════════════

In the Railway Claims Tribunal at Mumbai

───────────────────────────────────────────────────────────────
APPLICANT DETAILS
───────────────────────────────────────────────────────────────
Name:               {name}
Address:            {address}
Phone:              {phone}
Relationship to victim: {relationship}

───────────────────────────────────────────────────────────────
INCIDENT DETAILS
───────────────────────────────────────────────────────────────
Nature of Incident: {incident_label}
Date of Incident:   {incident_date}
Time of Incident:   {incident_time}
Train Name/Number:  {train_number}
Class of Travel:    {travel_class}
From Station:       {from_station}
To Station:         {to_station}

───────────────────────────────────────────────────────────────
INJURY / DEATH DETAILS
───────────────────────────────────────────────────────────────
{injuries}

───────────────────────────────────────────────────────────────
COMPENSATION CLAIMED
───────────────────────────────────────────────────────────────
As per Second Schedule, Railways Act 1989:
- Death:                    Rs. 8,00,000 (minimum)
- Total permanent disability: Rs. 8,00,000
- Partial disability:       Rs. 32,000 to Rs. 7,60,000
- Simple injury:            Rs. 32,000
- Grievous injury:          Rs. 3,20,000

Amount Claimed: {compensation_amount}

───────────────────────────────────────────────────────────────
SUPPORTING DOCUMENTS (checklist)
───────────────────────────────────────────────────────────────
[ ] Copy of railway ticket / PNR / season pass
[ ] FIR copy (if filed)
[ ] Medical certificate / hospital records
[ ] Photographs of injury
[ ] Witness statements
[ ] Death certificate (if applicable)
[ ] Post-mortem report (if applicable)
[ ] Identity proof of applicant

───────────────────────────────────────────────────────────────
Applicable Section: {applicable_sections}

Filed at: Railway Claims Tribunal, Mumbai
Date of Filing: {report_date}
═══════════════════════════════════════════════════════════════
""",

    "hi": """
═══════════════════════════════════════════════════════════════
            रेलवे दावा अधिकरण — फॉर्म II
            क्षतिपूर्ति आवेदन
            (रेलवे अधिनियम 1989 की धारा 124A के अंतर्गत)
═══════════════════════════════════════════════════════════════

रेलवे दावा अधिकरण, मुंबई में

───────────────────────────────────────────────────────────────
आवेदक विवरण
───────────────────────────────────────────────────────────────
नाम:               {name}
पता:                {address}
फोन:               {phone}
पीड़ित से संबंध:      {relationship}

───────────────────────────────────────────────────────────────
घटना विवरण
───────────────────────────────────────────────────────────────
घटना का प्रकार:     {incident_label}
घटना दिनांक:        {incident_date}
घटना समय:          {incident_time}
ट्रेन नाम/नंबर:      {train_number}
यात्रा श्रेणी:        {travel_class}
से स्टेशन:          {from_station}
तक स्टेशन:         {to_station}

───────────────────────────────────────────────────────────────
चोट / मृत्यु विवरण
───────────────────────────────────────────────────────────────
{injuries}

───────────────────────────────────────────────────────────────
दावा राशि
───────────────────────────────────────────────────────────────
रेलवे अधिनियम 1989 की दूसरी अनुसूची के अनुसार:
- मृत्यु:                   रु. 8,00,000 (न्यूनतम)
- पूर्ण स्थायी अक्षमता:      रु. 8,00,000
- आंशिक अक्षमता:          रु. 32,000 से रु. 7,60,000
- साधारण चोट:             रु. 32,000
- गंभीर चोट:              रु. 3,20,000

दावा राशि: {compensation_amount}

───────────────────────────────────────────────────────────────
सहायक दस्तावेज़ (चेकलिस्ट)
───────────────────────────────────────────────────────────────
[ ] रेलवे टिकट / पीएनआर / सीज़न पास की प्रति
[ ] एफआईआर की प्रति (यदि दर्ज की गई हो)
[ ] चिकित्सा प्रमाणपत्र / अस्पताल रिकॉर्ड
[ ] चोट की तस्वीरें
[ ] गवाहों के बयान
[ ] मृत्यु प्रमाणपत्र (यदि लागू हो)
[ ] पोस्ट-मॉर्टम रिपोर्ट (यदि लागू हो)
[ ] आवेदक का पहचान प्रमाण

───────────────────────────────────────────────────────────────
लागू धारा: {applicable_sections}

दर्ज स्थान: रेलवे दावा अधिकरण, मुंबई
दर्ज दिनांक: {report_date}
═══════════════════════════════════════════════════════════════
""",

    "mr": """
═══════════════════════════════════════════════════════════════
            रेल्वे दावे न्यायाधिकरण — फॉर्म II
            भरपाई अर्ज
            (रेल्वे कायदा 1989 कलम 124A अंतर्गत)
═══════════════════════════════════════════════════════════════

रेल्वे दावे न्यायाधिकरण, मुंबई येथे

───────────────────────────────────────────────────────────────
अर्जदाराचे तपशील
───────────────────────────────────────────────────────────────
नाव:               {name}
पत्ता:              {address}
फोन:               {phone}
पीडितेशी संबंध:     {relationship}

───────────────────────────────────────────────────────────────
घटनेचे तपशील
───────────────────────────────────────────────────────────────
घटनेचा प्रकार:     {incident_label}
घटना दिनांक:        {incident_date}
घटना वेळ:          {incident_time}
ट्रेन नाव/नंबर:      {train_number}
प्रवास वर्ग:         {travel_class}
कुठून स्टेशन:        {from_station}
कुठे स्टेशन:         {to_station}

───────────────────────────────────────────────────────────────
जखम / मृत्यू तपशील
───────────────────────────────────────────────────────────────
{injuries}

───────────────────────────────────────────────────────────────
दावा रक्कम
───────────────────────────────────────────────────────────────
रेल्वे कायदा 1989 दुसऱ्या अनुसूचीनुसार:
- मृत्यू:                   रु. 8,00,000 (किमान)
- पूर्ण कायमस्वरूपी अपंगत्व: रु. 8,00,000
- आंशिक अपंगत्व:          रु. 32,000 ते रु. 7,60,000
- साधी जखम:              रु. 32,000
- गंभीर जखम:             रु. 3,20,000

दावा रक्कम: {compensation_amount}

───────────────────────────────────────────────────────────────
सहाय्यक कागदपत्रे (चेकलिस्ट)
───────────────────────────────────────────────────────────────
[ ] रेल्वे तिकीट / पीएनआर / सीझन पासची प्रत
[ ] एफआयआरची प्रत (दाखल केली असल्यास)
[ ] वैद्यकीय प्रमाणपत्र / रुग्णालय नोंदी
[ ] जखमेचे फोटो
[ ] साक्षीदारांचे जबाब
[ ] मृत्यू प्रमाणपत्र (लागू असल्यास)
[ ] शवविच्छेदन अहवाल (लागू असल्यास)
[ ] अर्जदाराचा ओळखपत्र

───────────────────────────────────────────────────────────────
लागू कलम: {applicable_sections}

दाखल ठिकाण: रेल्वे दावे न्यायाधिकरण, मुंबई
दाखल दिनांक: {report_date}
═══════════════════════════════════════════════════════════════
""",
}


# ── Template → Action Mapping ────────────────────────────────

# Which template to fill per action + incident
ACTION_TO_TEMPLATE_MAP = {
    "file_complaint": {
        # RCT-eligible incidents get RCT Form II alongside FIR
        "accident": ["grp_fir", "rct_form_ii"],
        "falling": ["grp_fir", "rct_form_ii"],
        "death": ["grp_fir", "rct_form_ii"],
        "platform_gap": ["grp_fir", "rct_form_ii"],
        "stampede": ["grp_fir", "rct_form_ii"],
        # All others get GRP FIR
        "_default": ["grp_fir"],
    },
    "file_cpgrams": {
        "_default": ["cpgrams"],
    },
    "compensation_info": {
        "_default": ["rct_form_ii"],
    },
}

# Zone mapping
ZONE_MAP = {
    "WR": "Western Railway",
    "CR": "Central Railway",
    "HR": "Harbour Line (Central Railway)",
}


# Known Mumbai suburban stations → railway zone
# This is factual geographic data, not a "rule"
_WR_STATIONS = {
    "churchgate", "marine lines", "charni road", "grant road", "mumbai central",
    "mahalaxmi", "lower parel", "elphinstone", "dadar", "matunga road",
    "mahim", "bandra", "khar road", "santacruz", "vile parle", "andheri",
    "jogeshwari", "goregaon", "malad", "kandivali", "borivali", "dahisar",
    "mira road", "bhayander", "naigaon", "vasai road", "nallasopara", "virar",
}
_CR_STATIONS = {
    "csmt", "cst", "masjid", "sandhurst road", "byculla", "chinchpokli",
    "currey road", "parel", "dadar", "matunga", "sion", "kurla", "ghatkopar",
    "vikhroli", "kanjurmarg", "bhandup", "nahur", "mulund", "thane",
    "kalwa", "mumbra", "diva", "dombivli", "kalyan", "badlapur", "ambernath",
    "ulhasnagar", "kasara", "karjat", "khopoli",
}
_HR_STATIONS = {
    "csmt", "masjid", "sandhurst road", "wadala", "guru tegh bahadur nagar",
    "chunabhatti", "tilak nagar", "chembur", "govandi", "mankhurd",
    "vashi", "sanpada", "juinagar", "nerul", "seawoods", "cbd belapur",
    "kharghar", "mansarovar", "khandeshwar", "panvel",
}


def _detect_zone(station_name: str | None) -> str:
    """Detect railway zone from station name. Falls back to generic."""
    if not station_name:
        return "Mumbai Suburban Railway"
    s = station_name.strip().lower()
    if s in _WR_STATIONS:
        return "Western Railway"
    if s in _HR_STATIONS:
        return "Harbour Line (Central Railway)"
    if s in _CR_STATIONS:
        return "Central Railway"
    return "Mumbai Suburban Railway"


def _get_slot_value(value, fallback="[______]"):
    """Return value if truthy, else the fill-in blank marker."""
    if value and str(value).strip() and str(value).strip().lower() not in ("none", "null", "n/a"):
        return str(value).strip()
    return fallback


def _format_items_list(items):
    """Format a list of items as numbered lines."""
    if not items:
        return "[______]"
    if isinstance(items, list):
        return "\n".join(f"  {i+1}. {item}" for i, item in enumerate(items))
    return str(items)


def fill_template(template_type: str, state: dict) -> dict:
    """
    Fill a complaint template from BotState data.
    Missing fields are marked [______] for the user to fill manually.
    The user's own words become the incident description (legally valid).

    Args:
        template_type: "grp_fir" | "rail_madad" | "cpgrams" | "rct_form_ii"
        state: BotState dict with user_context, entities, incident_type, etc.

    Returns:
        Dict with filled template text and metadata.
    """
    user_ctx = state.get("user_context", {})
    entities = state.get("entities", {})
    incident_type = state.get("incident_type", "general")
    language = state.get("language", "en")
    original_message = state.get("original_message", "")
    now = datetime.now()
    tracking_ref = f"RM-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    follow_up_date = (now + timedelta(days=30)).strftime("%d/%m/%Y")

    # Get incident label in user's language
    from app.engines.jansuraksha.mappings import INCIDENT_TYPE_LABELS
    incident_labels = INCIDENT_TYPE_LABELS.get(incident_type, INCIDENT_TYPE_LABELS["general"])
    incident_label = incident_labels.get(language, incident_labels.get("en", incident_type))

    # Rail Madad type/subtype
    rm_type, rm_subtype = RAILMADAD_TYPE_MAP.get(incident_type, ("General", "General Complaint"))

    # Incident summary (LLM-generated) or raw message as fallback
    incident_summary = state.get("incident_summary") or original_message or "[______]"

    # All location/travel fields come from LLM entity extraction, NOT from profile
    # Only name, phone, address come from user profile (signup)
    slots = {
        "name": _get_slot_value(user_ctx.get("name")),
        "address": _get_slot_value(user_ctx.get("address")),
        "phone": _get_slot_value(user_ctx.get("phone")),
        "report_date": now.strftime("%d/%m/%Y"),
        "report_time": now.strftime("%H:%M"),
        "incident_date": now.strftime("%d/%m/%Y"),
        "incident_time": _get_slot_value(entities.get("time")),
        "train_number": _get_slot_value(entities.get("train_name")),
        "travel_class": _get_slot_value(entities.get("travel_class")),
        "from_station": _get_slot_value(entities.get("from_station")),
        "to_station": _get_slot_value(entities.get("to_station")),
        "platform": _get_slot_value(entities.get("platform"), "N/A"),
        "incident_label": incident_label,
        "applicable_sections": APPLICABLE_SECTIONS_MAP.get(incident_type, "Railways Act 1989"),
        "property_details": _format_items_list(entities.get("items_lost")),
        "suspect_description": _get_slot_value(entities.get("accused_description")),
        "incident_description": incident_summary,
        "injuries": _get_slot_value(entities.get("injuries"), "None reported"),
        "grp_station": _get_slot_value(entities.get("from_station"), "Mumbai"),
        "relationship": "[______] (self / family member)",
        "compensation_amount": _get_slot_value(state.get("compensation_amount")),
        "department": _detect_zone(entities.get("from_station")),
        "cpgrams_category": CPGRAMS_CATEGORY_MAP.get(incident_type, "General"),
        "railmadad_type": rm_type,
        "railmadad_subtype": rm_subtype,
        "tracking_ref": tracking_ref,
        "follow_up_date": follow_up_date,
    }

    # Select template
    templates = {
        "grp_fir": GRP_FIR_TEMPLATE,
        "rail_madad": RAIL_MADAD_TEMPLATE,
        "cpgrams": CPGRAMS_TEMPLATE,
        "rct_form_ii": RCT_FORM_II_TEMPLATE,
    }

    template_dict = templates.get(template_type, GRP_FIR_TEMPLATE)
    template_str = template_dict.get(language, template_dict.get("en", ""))

    # Fill slots
    filled = template_str.format(**slots)

    return {
        "template_type": template_type,
        "filled_text": filled.strip(),
        "tracking_ref": tracking_ref,
        "follow_up_date": follow_up_date,
        "language": language,
        "slots_filled": {k: v for k, v in slots.items() if v != "[______]"},
        "slots_missing": [k for k, v in slots.items() if v == "[______]"],
    }


def get_templates_for_action(action_id: str, incident_type: str) -> list[str]:
    """Get list of template types to fill for a given action + incident."""
    action_templates = ACTION_TO_TEMPLATE_MAP.get(action_id, {})
    return action_templates.get(incident_type, action_templates.get("_default", []))