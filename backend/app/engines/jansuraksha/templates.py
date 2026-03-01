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
                  FORM - IF1 (Integrated Form)
                FIRST INFORMATION REPORT (FIR)
          (Under Section 154 Cr.P.C. / Section 173 BNSS)
═══════════════════════════════════════════════════════════════
                Government Railway Police, Mumbai
           Mumbai Railway Police Commissionerate
═══════════════════════════════════════════════════════════════

1. District: Mumbai          P.S.: GRP {grp_station}
   Year: {report_year}       FIR No.: ________
   Date: {report_date}

2. Acts & Sections: {applicable_sections}

───────────────────────────────────────────────────────────────
3. OCCURRENCE OF OFFENCE
───────────────────────────────────────────────────────────────
   (a) Day: {incident_day}   Date: {incident_date}
       Time Period: {incident_time}
   (b) Information received at P.S.
       Date: {report_date}   Time: {report_time}
   (c) General Diary Ref: Entry No.: ________

4. Type of Information: Written

───────────────────────────────────────────────────────────────
5. PLACE OF OCCURRENCE
───────────────────────────────────────────────────────────────
   (a) Direction & Distance from P.S.: In jurisdiction of
       GRP Station {grp_station}
   (b) Train Name/Number:  {train_number}
       Class of Travel:    {travel_class}
       From Station:       {from_station}
       To Station:         {to_station}
       Platform Number:    {platform}

───────────────────────────────────────────────────────────────
6. COMPLAINANT / INFORMANT
───────────────────────────────────────────────────────────────
   (a) Name:              {name}
   (b) Father's/Husband's Name: [______]
   (c) Date of Birth:     [______]
   (d) Nationality:       Indian
   (e) Occupation:        [______]
   (f) Address:           {address}
   Phone/Mobile:          {phone}

───────────────────────────────────────────────────────────────
7. DETAILS OF KNOWN/SUSPECTED/UNKNOWN ACCUSED
───────────────────────────────────────────────────────────────
{suspect_description}

───────────────────────────────────────────────────────────────
8. REASONS FOR DELAY IN REPORTING (if any): N/A
───────────────────────────────────────────────────────────────

───────────────────────────────────────────────────────────────
9. PARTICULARS OF PROPERTIES STOLEN / INVOLVED
───────────────────────────────────────────────────────────────
{property_details}

10. Total Value of Property:
    Stolen: Rs. [______]    Involved: Rs. [______]

───────────────────────────────────────────────────────────────
11. INQUEST REPORT / U.D. CASE No.: N/A
───────────────────────────────────────────────────────────────

───────────────────────────────────────────────────────────────
12. FIRST INFORMATION (STATEMENT OF COMPLAINANT)
───────────────────────────────────────────────────────────────
{incident_description}

───────────────────────────────────────────────────────────────
INJURIES (if any):
{injuries}

───────────────────────────────────────────────────────────────
13. ACTION TAKEN
───────────────────────────────────────────────────────────────
Since the above report reveals commission of offence(s) u/s
{applicable_sections}, registered the case and directed
investigation. FIR read over to the complainant, admitted to be
correctly recorded and a copy given to the complainant free of
cost.

───────────────────────────────────────────────────────────────
14. Signature / Thumb Impression of Complainant:

____________________

───────────────────────────────────────────────────────────────
15. Date & Time of Despatch to the Court:
    Date: ________     Time: ________

═══════════════════════════════════════════════════════════════
Signature of Officer-in-Charge, Police Station
Name: ________________  Rank: ________  No.: ________
═══════════════════════════════════════════════════════════════
""",

    "hi": """
═══════════════════════════════════════════════════════════════
                फॉर्म - IF1 (एकीकृत फॉर्म)
              प्रथम सूचना रिपोर्ट (एफआईआर)
       (दंड प्रक्रिया संहिता धारा 154 / BNSS धारा 173 के अंतर्गत)
═══════════════════════════════════════════════════════════════
              सरकारी रेलवे पुलिस, मुंबई
           मुंबई रेलवे पुलिस आयुक्तालय
═══════════════════════════════════════════════════════════════

1. जिला: मुंबई              थाना: जीआरपी {grp_station}
   वर्ष: {report_year}       एफआईआर सं.: ________
   दिनांक: {report_date}

2. अधिनियम व धाराएं: {applicable_sections}

───────────────────────────────────────────────────────────────
3. अपराध की घटना
───────────────────────────────────────────────────────────────
   (क) दिन: {incident_day}   दिनांक: {incident_date}
       समय: {incident_time}
   (ख) थाने में सूचना प्राप्त
       दिनांक: {report_date}   समय: {report_time}
   (ग) जनरल डायरी संदर्भ: प्रविष्टि सं.: ________

4. सूचना का प्रकार: लिखित

───────────────────────────────────────────────────────────────
5. घटनास्थल
───────────────────────────────────────────────────────────────
   ट्रेन नाम/नंबर:     {train_number}
   यात्रा श्रेणी:       {travel_class}
   से स्टेशन:         {from_station}
   तक स्टेशन:        {to_station}
   प्लेटफॉर्म नंबर:     {platform}

───────────────────────────────────────────────────────────────
6. शिकायतकर्ता / सूचनाकर्ता
───────────────────────────────────────────────────────────────
   (क) नाम:              {name}
   (ख) पिता/पति का नाम:  [______]
   (ग) जन्म तिथि:        [______]
   (घ) राष्ट्रीयता:        भारतीय
   (ड.) व्यवसाय:          [______]
   (च) पता:              {address}
   फोन/मोबाइल:          {phone}

───────────────────────────────────────────────────────────────
7. ज्ञात/संदिग्ध/अज्ञात अभियुक्त का विवरण
───────────────────────────────────────────────────────────────
{suspect_description}

───────────────────────────────────────────────────────────────
9. खोई/संलिप्त संपत्ति का विवरण
───────────────────────────────────────────────────────────────
{property_details}

10. संपत्ति का कुल मूल्य:
    चोरी: रु. [______]    संलिप्त: रु. [______]

───────────────────────────────────────────────────────────────
12. प्रथम सूचना (शिकायतकर्ता का बयान)
───────────────────────────────────────────────────────────────
{incident_description}

───────────────────────────────────────────────────────────────
चोटें (यदि कोई हो):
{injuries}

───────────────────────────────────────────────────────────────
13. की गई कार्रवाई
───────────────────────────────────────────────────────────────
उपरोक्त रिपोर्ट में धारा {applicable_sections} के अंतर्गत
अपराध का खुलासा होता है, मुकदमा दर्ज कर जांच का निर्देश
दिया गया। एफआईआर शिकायतकर्ता को पढ़कर सुनाई गई, सही
दर्ज मानी गई और निःशुल्क प्रति दी गई।

───────────────────────────────────────────────────────────────
14. शिकायतकर्ता के हस्ताक्षर / अंगूठे का निशान:

____________________

═══════════════════════════════════════════════════════════════
थाना प्रभारी के हस्ताक्षर
नाम: ________________  पद: ________  सं.: ________
═══════════════════════════════════════════════════════════════
""",

    "mr": """
═══════════════════════════════════════════════════════════════
                फॉर्म - IF1 (एकत्रित फॉर्म)
              प्रथम खबरी अहवाल (एफआयआर)
       (फौजदारी प्रक्रिया संहिता कलम 154 / BNSS कलम 173 अंतर्गत)
═══════════════════════════════════════════════════════════════
              सरकारी रेल्वे पोलीस, मुंबई
           मुंबई रेल्वे पोलीस आयुक्तालय
═══════════════════════════════════════════════════════════════

1. जिल्हा: मुंबई            ठाणे: जीआरपी {grp_station}
   वर्ष: {report_year}       एफआयआर क्र.: ________
   दिनांक: {report_date}

2. कायदे व कलमे: {applicable_sections}

───────────────────────────────────────────────────────────────
3. गुन्ह्याची घटना
───────────────────────────────────────────────────────────────
   (अ) दिवस: {incident_day}  दिनांक: {incident_date}
       वेळ: {incident_time}
   (ब) ठाण्यात माहिती प्राप्त
       दिनांक: {report_date}   वेळ: {report_time}
   (क) जनरल डायरी संदर्भ: नोंद क्र.: ________

4. माहितीचा प्रकार: लिखित

───────────────────────────────────────────────────────────────
5. घटनास्थळ
───────────────────────────────────────────────────────────────
   ट्रेन नाव/नंबर:     {train_number}
   प्रवास वर्ग:        {travel_class}
   कुठून स्टेशन:       {from_station}
   कुठे स्टेशन:        {to_station}
   प्लॅटफॉर्म नंबर:     {platform}

───────────────────────────────────────────────────────────────
6. तक्रारदार / माहिती देणारा
───────────────────────────────────────────────────────────────
   (अ) नाव:              {name}
   (ब) वडिलांचे/पतीचे नाव: [______]
   (क) जन्म तारीख:       [______]
   (ड) राष्ट्रीयत्व:        भारतीय
   (इ) व्यवसाय:          [______]
   (फ) पत्ता:             {address}
   फोन/मोबाइल:          {phone}

───────────────────────────────────────────────────────────────
7. ज्ञात/संशयित/अज्ञात आरोपीचे तपशील
───────────────────────────────────────────────────────────────
{suspect_description}

───────────────────────────────────────────────────────────────
9. चोरी/संबंधित मालमत्तेचा तपशील
───────────────────────────────────────────────────────────────
{property_details}

10. मालमत्तेचे एकूण मूल्य:
    चोरी: रु. [______]    संबंधित: रु. [______]

───────────────────────────────────────────────────────────────
12. प्रथम खबर (तक्रारदाराचे निवेदन)
───────────────────────────────────────────────────────────────
{incident_description}

───────────────────────────────────────────────────────────────
जखमा (असल्यास):
{injuries}

───────────────────────────────────────────────────────────────
13. केलेली कार्यवाही
───────────────────────────────────────────────────────────────
वरील अहवालात कलम {applicable_sections} अंतर्गत गुन्हा
उघड होतो, गुन्हा दाखल करून तपास सुरू केला. एफआयआर
तक्रारदारास वाचून दाखवली, योग्यरित्या नोंदवली गेली असे
मान्य करून मोफत प्रत दिली.

───────────────────────────────────────────────────────────────
14. तक्रारदाराची सही / अंगठ्याचा ठसा:

____________________

═══════════════════════════════════════════════════════════════
ठाणे अधिकाऱ्याची सही
नाव: ________________  पद: ________  क्र.: ________
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
           CPGRAMS — GRIEVANCE REGISTRATION FORM
    Centralized Public Grievance Redress & Monitoring System
    Department of Administrative Reforms & Public Grievances
                      pgportal.gov.in
═══════════════════════════════════════════════════════════════

Registration No.:   {tracking_ref}
Date of Filing:     {report_date}

───────────────────────────────────────────────────────────────
GRIEVANCE ADDRESSED TO
───────────────────────────────────────────────────────────────
Organisation Type:  Central Government
Ministry:           Ministry of Railways (Rail Mantralaya)
Department:         {department}
Category:           {cpgrams_category}
Grievance pertains to:
   State:           Maharashtra
   District:        Mumbai

───────────────────────────────────────────────────────────────
COMPLAINANT DETAILS
───────────────────────────────────────────────────────────────
Name:               {name}
Gender:             [______]
Phone/Mobile:       {phone}
Email:              [______]
Address:            {address}
Pincode:            [______]
State:              Maharashtra
District:           Mumbai
Senior Citizen:     [ ] Yes  [ ] No
Divyang (PwD):      [ ] Yes  [ ] No

───────────────────────────────────────────────────────────────
GRIEVANCE DETAILS
───────────────────────────────────────────────────────────────
Subject: {incident_label} — {from_station} Station

Description:
{incident_description}

Date of Incident:   {incident_date}
Place of Incident:  {from_station}
Train Name/Number:  {train_number}

Has this grievance been filed before?  [ ] Yes  [ ] No
If yes, previous Registration No.: ________

───────────────────────────────────────────────────────────────
SUPPORTING DOCUMENTS
───────────────────────────────────────────────────────────────
[ ] Attach supporting documents (PDF/JPEG, max 5 MB each)
[ ] Identity proof (Aadhaar / PAN / Voter ID)

═══════════════════════════════════════════════════════════════
SUBMISSION INSTRUCTIONS
═══════════════════════════════════════════════════════════════
1. Submit online at: pgportal.gov.in
2. Or visit: Nearest Railway Grievance Cell / DRM Office
3. Resolution timeline: 21 working days (max 60 days)
4. Track status using Registration No.: {tracking_ref}
5. Appeal within 30 days if resolution is unsatisfactory

Follow up after:    {follow_up_date}
═══════════════════════════════════════════════════════════════
""",

    "hi": """
═══════════════════════════════════════════════════════════════
         सीपीजीआरएएमएस — शिकायत पंजीकरण फॉर्म
    केंद्रीकृत लोक शिकायत निवारण एवं निगरानी प्रणाली
    प्रशासनिक सुधार एवं लोक शिकायत विभाग
                      pgportal.gov.in
═══════════════════════════════════════════════════════════════

पंजीकरण सं.:       {tracking_ref}
दाखिल दिनांक:       {report_date}

───────────────────────────────────────────────────────────────
शिकायत प्रेषित
───────────────────────────────────────────────────────────────
संगठन प्रकार:       केंद्र सरकार
मंत्रालय:           रेल मंत्रालय (रेल मंत्रालय)
विभाग:             {department}
श्रेणी:              {cpgrams_category}
शिकायत संबंधित:
   राज्य:           महाराष्ट्र
   जिला:           मुंबई

───────────────────────────────────────────────────────────────
शिकायतकर्ता विवरण
───────────────────────────────────────────────────────────────
नाम:               {name}
फोन/मोबाइल:       {phone}
पता:                {address}
राज्य:              महाराष्ट्र
जिला:              मुंबई

───────────────────────────────────────────────────────────────
शिकायत विवरण
───────────────────────────────────────────────────────────────
विषय: {incident_label} — {from_station} स्टेशन

विवरण:
{incident_description}

घटना दिनांक:       {incident_date}
घटना स्थान:        {from_station}
ट्रेन नाम/नंबर:     {train_number}

═══════════════════════════════════════════════════════════════
जमा करने के निर्देश
═══════════════════════════════════════════════════════════════
1. ऑनलाइन जमा करें: pgportal.gov.in
2. समाधान समय: 21 कार्य दिवस (अधिकतम 60 दिन)
3. पंजीकरण सं. से स्थिति जांचें: {tracking_ref}

फॉलो अप करें:      {follow_up_date}
═══════════════════════════════════════════════════════════════
""",

    "mr": """
═══════════════════════════════════════════════════════════════
         सीपीजीआरएएमएस — तक्रार नोंदणी फॉर्म
    केंद्रीकृत लोक तक्रार निवारण आणि निरीक्षण प्रणाली
    प्रशासकीय सुधारणा आणि लोक तक्रार विभाग
                      pgportal.gov.in
═══════════════════════════════════════════════════════════════

नोंदणी क्र.:         {tracking_ref}
दाखल दिनांक:        {report_date}

───────────────────────────────────────────────────────────────
तक्रार प्रेषित
───────────────────────────────────────────────────────────────
संघटना प्रकार:       केंद्र सरकार
मंत्रालय:           रेल्वे मंत्रालय (रेल मंत्रालय)
विभाग:             {department}
श्रेणी:              {cpgrams_category}
तक्रार संबंधित:
   राज्य:           महाराष्ट्र
   जिल्हा:          मुंबई

───────────────────────────────────────────────────────────────
तक्रारदाराचे तपशील
───────────────────────────────────────────────────────────────
नाव:               {name}
फोन/मोबाइल:       {phone}
पत्ता:              {address}
राज्य:              महाराष्ट्र
जिल्हा:             मुंबई

───────────────────────────────────────────────────────────────
तक्रार तपशील
───────────────────────────────────────────────────────────────
विषय: {incident_label} — {from_station} स्टेशन

वर्णन:
{incident_description}

घटना दिनांक:       {incident_date}
घटना ठिकाण:       {from_station}
ट्रेन नाव/नंबर:     {train_number}

═══════════════════════════════════════════════════════════════
सादर करण्याच्या सूचना
═══════════════════════════════════════════════════════════════
1. ऑनलाइन सादर करा: pgportal.gov.in
2. निराकरण कालावधी: 21 कामकाजाचे दिवस (कमाल 60 दिवस)
3. नोंदणी क्र. ने स्थिती तपासा: {tracking_ref}

फॉलो अप करा:       {follow_up_date}
═══════════════════════════════════════════════════════════════
""",
}


# ── RCT Form II Template (Railway Claims Tribunal) ───────────

RCT_FORM_II_TEMPLATE = {
    "en": """
═══════════════════════════════════════════════════════════════
                     FORM II
                   [See Rule 4(1)]
  Application for Compensation under Section 16 of the
  Railway Claims Tribunal Act, 1987 in respect of claims
  arising out of accident / untoward incident
═══════════════════════════════════════════════════════════════

               BEFORE THE RAILWAY CLAIMS TRIBUNAL
                    MUMBAI BENCH AT MUMBAI

Original Application No. ________ of {report_year}

───────────────────────────────────────────────────────────────
                       IN THE MATTER OF:

{name}
{address}
                                            ... Applicant(s)

                          VERSUS

Union of India through
General Manager,
{department},
Mumbai                                      ... Respondent(s)

═══════════════════════════════════════════════════════════════
SECTION I — PERSONAL DETAILS
═══════════════════════════════════════════════════════════════
1. Name of Applicant:           {name}
   Father's/Husband's Name:     [______]
   Address:                     {address}
   Phone/Mobile:                {phone}

2. Name of Injured/Deceased:    {name}
   Age at time of incident:     [______]

3. Occupation:                  [______]
   If employed, Employer:       [______]

4. Marital Status:              [______]
   If married, Name of Spouse:  [______]
   No. of dependent children:   [______]

5. Relationship of Applicant
   to Injured/Deceased:         {relationship}

═══════════════════════════════════════════════════════════════
SECTION II — TRAVEL DETAILS
═══════════════════════════════════════════════════════════════
1. Status of Injured/Deceased:
   [ ] Passenger    [ ] Railway Staff    [ ] Visitor

2. Ticket Particulars:
   Ticket Number:               [______]
   Class of Travel:             {travel_class}
   From Station:                {from_station}
   To Station:                  {to_station}
   Date & Time of Issue:        [______]
   Holding valid ticket:        [ ] Yes  [ ] No

3. Was ticket recovered by police?
   [ ] Yes  [ ] No
   If yes, Seizure Memo No.:    [______]

4. Co-passengers (who can identify injured/deceased):
   Name: [______]              Address: [______]

═══════════════════════════════════════════════════════════════
SECTION III — ACCIDENT / UNTOWARD INCIDENT DETAILS
═══════════════════════════════════════════════════════════════
1. Nature of Incident (tick applicable):
   [ ] Derailment of train
   [ ] Collision of trains
   [ ] Collision with road vehicle at level crossing
   [ ] Accidental fall from train
   [ ] Run over by train
   [ ] Platform gap injury
   [ ] Other: {incident_label}

2. Train Name/Number:           {train_number}
   Date of Incident:            {incident_date}
   Time of Incident:            {incident_time}
   Location (between stations): {from_station} to {to_station}
   Division/Zone:               {department}

3. Applicable Sections:         {applicable_sections}

4. Was victim's name in casualty list?  [ ] Yes  [ ] No
   Was ex-gratia payment received?      [ ] Yes  [ ] No
   If yes, amount: Rs. [______]

═══════════════════════════════════════════════════════════════
SECTION IV — INJURY / DEATH DETAILS
═══════════════════════════════════════════════════════════════
1. Description of Injuries:
{injuries}

2. Hospital Name & Address:     [______]
   Date of Admission:           [______]
   Name of Medical Officer:     [______]
   Discharge Diagnosis:         [______]
   Period of Treatment:         [______]
   Disability Assessment:       [______]

3. Death Details (if applicable):
   [ ] Post-mortem report attached
   [ ] Inquest proceedings attached
   [ ] Death certificate attached
   [ ] FIR copy attached

═══════════════════════════════════════════════════════════════
SECTION V — COMPENSATION CLAIMED
═══════════════════════════════════════════════════════════════
As per Second Schedule, Railways Act 1989:
  Death:                        Rs. 8,00,000 (minimum)
  Total permanent disability:   Rs. 8,00,000
  Partial disability:           Rs. 32,000 to Rs. 7,60,000
  Grievous injury:              Rs. 3,20,000
  Simple injury:                Rs. 32,000

Amount Claimed: {compensation_amount}

═══════════════════════════════════════════════════════════════
SECTION VI — LIMITATION
═══════════════════════════════════════════════════════════════
Is application within 3 years of incident?  [ ] Yes  [ ] No
If delayed, No. of days: ________
Reasons for delay: [______]

═══════════════════════════════════════════════════════════════
SECTION VII — UNDERTAKING
═══════════════════════════════════════════════════════════════
The applicant hereby declares and undertakes that no application
for compensation in respect of the same accident / untoward
incident has been filed before any other Bench of the Railway
Claims Tribunal or before any Court.

═══════════════════════════════════════════════════════════════
                          PRAYER
═══════════════════════════════════════════════════════════════
The applicant respectfully prays that this Hon'ble Tribunal
may be pleased to:
(a) Award compensation of Rs. {compensation_amount} along with
    interest @ 12% per annum from the date of filing till
    the date of payment;
(b) Award costs of this application;
(c) Grant such other relief as this Hon'ble Tribunal may deem
    fit and proper.

Place: Mumbai
Date:  {report_date}
                              Signature of Applicant: ________
                              Through Advocate: [______]

═══════════════════════════════════════════════════════════════
                       VERIFICATION
═══════════════════════════════════════════════════════════════
I, {name}, the applicant above named, do hereby verify that
the contents of this application are true and correct to my
knowledge and belief, and nothing material has been concealed.

Verified at Mumbai on {report_date}.

                              Signature of Applicant: ________

═══════════════════════════════════════════════════════════════
DOCUMENTS TO ATTACH (Index — Part II)
═══════════════════════════════════════════════════════════════
[ ] 1. Copy of railway ticket / PNR / season pass
[ ] 2. Copy of FIR (if filed)
[ ] 3. Medical certificate / hospital records
[ ] 4. Photographs of injuries
[ ] 5. Witness statements
[ ] 6. Death certificate (if applicable)
[ ] 7. Post-mortem report (if applicable)
[ ] 8. Identity proof (Aadhaar / Voter ID / PAN)
[ ] 9. Legal heirship certificate (for death claims)
[ ] 10. Income / occupation proof

Note: Application to be filed in TRIPLICATE.
      No court fee for compensation claims under Sec. 16.
      Affidavit (Form VIII) must accompany this application.

═══════════════════════════════════════════════════════════════
Filed at: Railway Claims Tribunal, Mumbai Bench
Date:     {report_date}
Ref:      {tracking_ref}
═══════════════════════════════════════════════════════════════
""",

    "hi": """
═══════════════════════════════════════════════════════════════
                     फॉर्म II
                  [नियम 4(1) देखें]
  रेलवे दावा अधिकरण अधिनियम, 1987 की धारा 16 के अंतर्गत
  दुर्घटना / अनहोनी घटना से उत्पन्न दावों हेतु
  क्षतिपूर्ति आवेदन
═══════════════════════════════════════════════════════════════

             रेलवे दावा अधिकरण के समक्ष
                  मुंबई पीठ, मुंबई

मूल आवेदन सं. ________ सन् {report_year}

───────────────────────────────────────────────────────────────
                       विषय में:

{name}
{address}
                                           ... आवेदक

                        बनाम

भारत संघ, महाप्रबंधक के माध्यम से,
{department},
मुंबई                                       ... प्रतिवादी

═══════════════════════════════════════════════════════════════
खंड I — व्यक्तिगत विवरण
═══════════════════════════════════════════════════════════════
1. आवेदक का नाम:             {name}
   पिता/पति का नाम:           [______]
   पता:                       {address}
   फोन/मोबाइल:               {phone}

2. घायल/मृतक का नाम:          {name}
   घटना के समय आयु:          [______]

3. व्यवसाय:                   [______]
4. वैवाहिक स्थिति:             [______]
5. आवेदक का संबंध:           {relationship}

═══════════════════════════════════════════════════════════════
खंड II — यात्रा विवरण
═══════════════════════════════════════════════════════════════
   यात्रा श्रेणी:              {travel_class}
   से स्टेशन:                {from_station}
   तक स्टेशन:               {to_station}
   वैध टिकट:                 [ ] हाँ  [ ] नहीं

═══════════════════════════════════════════════════════════════
खंड III — दुर्घटना / अनहोनी घटना विवरण
═══════════════════════════════════════════════════════════════
   घटना का प्रकार:            {incident_label}
   ट्रेन नाम/नंबर:             {train_number}
   घटना दिनांक:               {incident_date}
   घटना समय:                 {incident_time}
   स्थान:                     {from_station} से {to_station}
   मंडल/क्षेत्र:                {department}
   लागू धाराएं:               {applicable_sections}

═══════════════════════════════════════════════════════════════
खंड IV — चोट / मृत्यु विवरण
═══════════════════════════════════════════════════════════════
{injuries}

   अस्पताल:                  [______]
   चिकित्सा अधिकारी:          [______]

═══════════════════════════════════════════════════════════════
खंड V — दावा राशि
═══════════════════════════════════════════════════════════════
रेलवे अधिनियम 1989 की दूसरी अनुसूची के अनुसार:
  मृत्यु:                     रु. 8,00,000 (न्यूनतम)
  पूर्ण स्थायी अक्षमता:        रु. 8,00,000
  गंभीर चोट:                 रु. 3,20,000
  साधारण चोट:               रु. 32,000

दावा राशि: {compensation_amount}

═══════════════════════════════════════════════════════════════
                        प्रार्थना
═══════════════════════════════════════════════════════════════
आवेदक प्रार्थना करता है कि यह माननीय अधिकरण कृपया
रु. {compensation_amount} की क्षतिपूर्ति 12% वार्षिक ब्याज
सहित प्रदान करें।

स्थान: मुंबई
दिनांक: {report_date}
                            आवेदक के हस्ताक्षर: ________

═══════════════════════════════════════════════════════════════
                       सत्यापन
═══════════════════════════════════════════════════════════════
मैं, {name}, प्रमाणित करता/करती हूँ कि इस आवेदन की
सामग्री मेरी जानकारी और विश्वास के अनुसार सत्य है।

मुंबई में {report_date} को सत्यापित।
                            आवेदक के हस्ताक्षर: ________

═══════════════════════════════════════════════════════════════
दर्ज स्थान: रेलवे दावा अधिकरण, मुंबई पीठ
दिनांक:     {report_date}
संदर्भ:      {tracking_ref}
═══════════════════════════════════════════════════════════════
""",

    "mr": """
═══════════════════════════════════════════════════════════════
                     फॉर्म II
                  [नियम 4(1) पहा]
  रेल्वे दावे न्यायाधिकरण कायदा, 1987 कलम 16 अंतर्गत
  अपघात / अनपेक्षित घटनेतून उद्भवलेल्या दाव्यांसाठी
  भरपाई अर्ज
═══════════════════════════════════════════════════════════════

             रेल्वे दावे न्यायाधिकरणासमोर
                  मुंबई पीठ, मुंबई

मूळ अर्ज क्र. ________ सन {report_year}

───────────────────────────────────────────────────────────────
                       या विषयात:

{name}
{address}
                                           ... अर्जदार

                        विरुद्ध

भारत संघ, महाव्यवस्थापकांमार्फत,
{department},
मुंबई                                       ... प्रतिवादी

═══════════════════════════════════════════════════════════════
खंड I — वैयक्तिक तपशील
═══════════════════════════════════════════════════════════════
1. अर्जदाराचे नाव:            {name}
   वडिलांचे/पतीचे नाव:        [______]
   पत्ता:                      {address}
   फोन/मोबाइल:               {phone}

2. जखमी/मृत व्यक्तीचे नाव:     {name}
   घटनेच्या वेळी वय:           [______]

3. व्यवसाय:                   [______]
4. वैवाहिक स्थिती:             [______]
5. अर्जदाराचे नाते:           {relationship}

═══════════════════════════════════════════════════════════════
खंड II — प्रवास तपशील
═══════════════════════════════════════════════════════════════
   प्रवास वर्ग:               {travel_class}
   कुठून स्टेशन:              {from_station}
   कुठे स्टेशन:               {to_station}
   वैध तिकीट:                [ ] होय  [ ] नाही

═══════════════════════════════════════════════════════════════
खंड III — अपघात / अनपेक्षित घटना तपशील
═══════════════════════════════════════════════════════════════
   घटनेचा प्रकार:             {incident_label}
   ट्रेन नाव/नंबर:             {train_number}
   घटना दिनांक:               {incident_date}
   घटना वेळ:                  {incident_time}
   ठिकाण:                    {from_station} ते {to_station}
   विभाग/क्षेत्र:               {department}
   लागू कलमे:                {applicable_sections}

═══════════════════════════════════════════════════════════════
खंड IV — जखम / मृत्यू तपशील
═══════════════════════════════════════════════════════════════
{injuries}

   रुग्णालय:                  [______]
   वैद्यकीय अधिकारी:          [______]

═══════════════════════════════════════════════════════════════
खंड V — दावा रक्कम
═══════════════════════════════════════════════════════════════
रेल्वे कायदा 1989 दुसऱ्या अनुसूचीनुसार:
  मृत्यू:                     रु. 8,00,000 (किमान)
  पूर्ण कायमस्वरूपी अपंगत्व:   रु. 8,00,000
  गंभीर जखम:                रु. 3,20,000
  साधी जखम:                 रु. 32,000

दावा रक्कम: {compensation_amount}

═══════════════════════════════════════════════════════════════
                       प्रार्थना
═══════════════════════════════════════════════════════════════
अर्जदार प्रार्थना करतो/करते की हे मा. न्यायाधिकरण कृपया
रु. {compensation_amount} भरपाई 12% वार्षिक व्याजासह
प्रदान करावी.

ठिकाण: मुंबई
दिनांक: {report_date}
                            अर्जदाराची सही: ________

═══════════════════════════════════════════════════════════════
                       सत्यापन
═══════════════════════════════════════════════════════════════
मी, {name}, प्रमाणित करतो/करते की या अर्जातील मजकूर
माझ्या माहिती आणि विश्वासानुसार सत्य आहे.

मुंबई येथे {report_date} रोजी सत्यापित.
                            अर्जदाराची सही: ________

═══════════════════════════════════════════════════════════════
दाखल ठिकाण: रेल्वे दावे न्यायाधिकरण, मुंबई पीठ
दिनांक:      {report_date}
संदर्भ:       {tracking_ref}
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
    # Day name for FIR
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    incident_day = day_names[now.weekday()]

    slots = {
        "name": _get_slot_value(user_ctx.get("name")),
        "address": _get_slot_value(user_ctx.get("address")),
        "phone": _get_slot_value(user_ctx.get("phone")),
        "report_date": now.strftime("%d/%m/%Y"),
        "report_time": now.strftime("%H:%M"),
        "report_year": now.strftime("%Y"),
        "incident_date": now.strftime("%d/%m/%Y"),
        "incident_day": incident_day,
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