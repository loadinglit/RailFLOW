"""
RailMind Legal Corpus — Hardcoded legal chunks for Jan Suraksha Bot.

~108 chunks with REAL legal text from:
- Railways Act 1989 (Chapter XIII: Sections 123-129, Chapter XV: Sections 147-154)
- GRP vs RPF jurisdiction rules
- CPGRAMS filing procedures
- Compensation schedule (Second Schedule)
- RCT application procedures
- Helpline directory
- RTI templates

Each chunk has metadata for filtered vector search.
"""

LEGAL_CHUNKS = [
    # ═══════════════════════════════════════════════════════════════
    # RAILWAYS ACT 1989 — CHAPTER XIII: LIABILITY OF RAILWAY FOR ACCIDENTS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Section 123 of the Railways Act 1989 — Extent of liability: When in the course of working a railway, an accident occurs, being either a collision between trains of which one is a train carrying passengers, or the derailment of or other accident to a train or any part of a train carrying passengers, then whether or not there has been any wrongful act, neglect or default on the part of the railway administration such as would entitle a passenger who has been injured or has suffered a loss to maintain an action and recover compensation in a civil court, the railway administration shall be liable to pay compensation to the extent set out in the Second Schedule.",
        "doc_type": "legal_statute",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 123",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Section 124 of the Railways Act 1989 — Application for compensation: An application for compensation under Section 123 shall be made to the Claims Tribunal and shall be accompanied by a fee of such amount as may be prescribed and may be made by the person who has sustained the injury or suffered the loss or, in the case of loss of life, by a dependant of the deceased or by any agent duly authorised by the claimant in this behalf.",
        "doc_type": "legal_statute",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 124",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Section 124A of the Railways Act 1989 — Compensation on account of untoward incidents: When in the course of working a railway an untoward incident occurs, then whether or not there has been any wrongful act, neglect or default on the part of the railway administration, the railway administration shall be liable to pay compensation to the extent set out in the Second Schedule. 'Untoward incident' includes commission of a terrorist act, violent attack, robbery, dacoity, rioting, shootout or arson by any person in or on any train carrying passengers.",
        "doc_type": "legal_statute",
        "incident_type": "assault",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 124A",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Section 125 of the Railways Act 1989 — Interim relief by railway administration: Where a person who has made a claim for compensation under Section 124 desires to be paid interim relief, the railway administration may, if it is of opinion that such a claim is justified, pay to the claimant immediately such sum as it considers reasonable, pending determination of the total compensation.",
        "doc_type": "legal_statute",
        "incident_type": "accident",
        "legal_remedy": "interim_relief",
        "authority": "Railway Administration",
        "section_ref": "Railways Act 1989, Section 125",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Section 126 of the Railways Act 1989 — Extent of liability in respect of accidents at unmanned level crossings: When, in the case of an accident occurring at an unmanned level crossing, compensation is payable by a railway administration, the compensation shall not exceed the amount set out in the Second Schedule.",
        "doc_type": "legal_statute",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 126",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Section 127 of the Railways Act 1989 — Determination of compensation in respect of any accident or untoward incident: The Claims Tribunal may, in addition to the amount of compensation payable under the Second Schedule, make allowance for the medical expenses incurred by the claimant, the loss of earnings due to the injury, and the pain and suffering undergone by the injured person.",
        "doc_type": "legal_statute",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 127",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Section 128 of the Railways Act 1989 — Saving as to certain rights: The right of any person to claim compensation under Section 123 shall not affect the right of any such person to recover compensation payable under the Workmen's Compensation Act 1923 or any other law for the time being in force, but no person shall be entitled to claim compensation more than once in respect of the same accident.",
        "doc_type": "legal_statute",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 128",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Section 129 of the Railways Act 1989 — Power of Claims Tribunal to award compensation in certain cases: Where a person has been injured or has died as a result of an accident, and the injured person or the dependant of the deceased person is unable to establish negligence on the part of the railway administration, the Claims Tribunal may, on the basis of the doctrine of strict liability, award compensation as it deems fit, not exceeding the limits prescribed in the Second Schedule.",
        "doc_type": "legal_statute",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 129",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # RAILWAYS ACT 1989 — CHAPTER XV: OFFENCES & PENALTIES (Sections 137-154)
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Section 137 of the Railways Act 1989 — Penalty for travelling without pass or ticket: If any person, with intent to defraud a railway administration, travels or attempts to travel in a train without a proper pass or ticket, he shall be punishable with imprisonment for a term which may extend to six months, or with fine which may extend to one thousand rupees, or with both.",
        "doc_type": "legal_statute",
        "incident_type": "ticketless_travel",
        "legal_remedy": "criminal_prosecution",
        "authority": "RPF",
        "section_ref": "Railways Act 1989, Section 137",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Section 145 of the Railways Act 1989 — Nuisance: No person shall commit nuisance or act in any indecent or disorderly manner or spit or throw any article on a railway or in any carriage or wagon. Whoever contravenes the provisions of this section shall be punishable with imprisonment for a term which may extend to six months, or with fine which may extend to five hundred rupees, or with both. This covers acts like smoking, playing loud music, blocking doorways, and other antisocial behavior on trains.",
        "doc_type": "legal_statute",
        "incident_type": "nuisance",
        "legal_remedy": "criminal_prosecution",
        "authority": "RPF",
        "section_ref": "Railways Act 1989, Section 145",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Section 147 of the Railways Act 1989 — Penalty for unauthorized entry into carriage reserved for females: Any male person who enters or remains in any carriage or portion of a carriage reserved for females, shall be punishable with fine which may extend to five hundred rupees. In case of any molestation or harassment of a female passenger, the punishment can be enhanced under the Indian Penal Code provisions.",
        "doc_type": "legal_statute",
        "incident_type": "harassment",
        "legal_remedy": "criminal_prosecution",
        "authority": "RPF",
        "section_ref": "Railways Act 1989, Section 147",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Section 148 of the Railways Act 1989 — Penalty for drunkenness or nuisance on railway premises: If any person in a state of intoxication enters or is on a railway or is in a train and refuses to leave when asked, he shall be punishable with imprisonment for a term which may extend to six months, or with fine which may extend to five hundred rupees, or with both. Additionally, such person may be removed by any railway servant or RPF personnel.",
        "doc_type": "legal_statute",
        "incident_type": "nuisance",
        "legal_remedy": "criminal_prosecution",
        "authority": "RPF",
        "section_ref": "Railways Act 1989, Section 148",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Section 150 of the Railways Act 1989 — Penalty for making a false claim: If any person makes a claim for compensation under this Act which he knows to be false or does not believe to be true, he shall be punishable with imprisonment for a term which may extend to three years, or with fine, or with both.",
        "doc_type": "legal_statute",
        "incident_type": "fraud",
        "legal_remedy": "criminal_prosecution",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 150",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Section 152 of the Railways Act 1989 — Penalty for endangering safety of passengers: Whoever does any act, or attempts to do any act, which causes or is likely to cause the engine or any vehicle used on a railway to meet with an accident, or places any obstruction across or under any rail, or displaces or alters the position of any rail, shall be punishable with imprisonment for life, or with imprisonment for a term which may extend to ten years.",
        "doc_type": "legal_statute",
        "incident_type": "safety_endangerment",
        "legal_remedy": "criminal_prosecution",
        "authority": "GRP",
        "section_ref": "Railways Act 1989, Section 152",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Section 153 of the Railways Act 1989 — Penalty for opening or breaking any door or barrier: Whoever opens or breaks any door or barrier at a level crossing, he shall be punishable with imprisonment for a term which may extend to three years, or with fine which may extend to ten thousand rupees, or with both.",
        "doc_type": "legal_statute",
        "incident_type": "safety_endangerment",
        "legal_remedy": "criminal_prosecution",
        "authority": "GRP",
        "section_ref": "Railways Act 1989, Section 153",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Section 154 of the Railways Act 1989 — Penalty for chain pulling: Whoever without reasonable and sufficient cause pulls or operates any communication device in a train to stop it, or tampers with the alarm chain or communication device, shall be punishable with imprisonment for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both. This section is commonly invoked in cases of unnecessary chain pulling on Mumbai suburban trains.",
        "doc_type": "legal_statute",
        "incident_type": "chain_pulling",
        "legal_remedy": "criminal_prosecution",
        "authority": "RPF",
        "section_ref": "Railways Act 1989, Section 154",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # COMPENSATION SCHEDULE (SECOND SCHEDULE TO RAILWAYS ACT 1989)
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Second Schedule to the Railways Act 1989 — Compensation for death: In case of death of a passenger due to a railway accident or untoward incident, the minimum compensation payable is Rs. 8,00,000 (Eight Lakh Rupees). This amount was last revised by the Railway Accidents and Untoward Incidents (Compensation) Amendment Rules 2017. The dependants of the deceased are entitled to claim this compensation from the Railway Claims Tribunal.",
        "doc_type": "compensation_schedule",
        "incident_type": "death",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Second Schedule",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Second Schedule to the Railways Act 1989 — Compensation for grievous hurt: In case a passenger suffers grievous hurt (as defined under Section 320 of IPC) due to a railway accident or untoward incident, the minimum compensation payable is Rs. 7,50,000 (Seven Lakh Fifty Thousand Rupees). Grievous hurt includes loss of limb, permanent disfiguration, loss of hearing or sight, or fracture of bone.",
        "doc_type": "compensation_schedule",
        "incident_type": "grievous_hurt",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Second Schedule",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Second Schedule to the Railways Act 1989 — Compensation for simple hurt: In case a passenger suffers simple hurt due to a railway accident or untoward incident, the minimum compensation payable is Rs. 1,00,000 (One Lakh Rupees). Simple hurt includes bruises, minor fractures, sprains, and other injuries that do not qualify as grievous hurt under Section 320 IPC.",
        "doc_type": "compensation_schedule",
        "incident_type": "simple_hurt",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Second Schedule",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Compensation for loss of property in railway accident: Under Section 123 read with the Second Schedule, the railway administration is liable to compensate for the loss of luggage and personal belongings of a passenger involved in a railway accident. The claim should be supported with evidence of ownership and the value of the items lost. The maximum amount is subject to the limits set out in the Indian Railways tariff.",
        "doc_type": "compensation_schedule",
        "incident_type": "property_loss",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 123",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Compensation for falling from overcrowded train: Passengers who fall from overcrowded Mumbai suburban trains during peak hours are covered under the definition of 'untoward incident' in Section 124A. The Railway Claims Tribunal has consistently held that overcrowding is a systemic failure of the railway administration and the victim or dependants are entitled to the full compensation as prescribed in the Second Schedule — Rs. 8L for death, Rs. 7.5L for grievous hurt.",
        "doc_type": "compensation_schedule",
        "incident_type": "falling",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 124A",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },
    {
        "text": "Platform gap injuries on Mumbai suburban railways: Injuries caused by the gap between the train and the platform are treated as railway accidents under Section 123. The Mumbai Division has recorded over 3,000 such incidents annually. Victims are entitled to claim compensation under the Second Schedule. Documentation required: FIR at GRP station, medical certificate, platform CCTV footage request, and witness statements.",
        "doc_type": "compensation_schedule",
        "incident_type": "platform_gap",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Section 123",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # GRP vs RPF — JURISDICTION RULES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Government Railway Police (GRP) Jurisdiction: The GRP is a state police force that handles all cognizable criminal offences committed on railway premises and in running trains. This includes theft, robbery, murder, assault, sexual harassment, kidnapping, and other IPC offences. GRP has the authority to register FIRs and investigate crimes. GRP stations are located at major railway stations across Mumbai including CST, Dadar, Bandra, Kurla, Thane, Kalyan, and Borivali.",
        "doc_type": "jurisdiction_guide",
        "incident_type": "theft",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "Police Act + Railway Protection Force Act",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },
    {
        "text": "Railway Protection Force (RPF) Jurisdiction: The RPF is a railway force responsible for the protection and security of railway property and passenger areas. RPF handles offences under the Railways Act 1989 such as ticketless travel, chain pulling, trespassing, damage to railway property, and unauthorized vending. RPF can file cases under special railway laws but NOT under IPC. For IPC offences like theft, assault, or murder, the case must go to GRP.",
        "doc_type": "jurisdiction_guide",
        "incident_type": "general",
        "legal_remedy": "complaint",
        "authority": "RPF",
        "section_ref": "Railway Protection Force Act 1957",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "When to approach GRP vs RPF: If you are a victim of THEFT, ROBBERY, ASSAULT, SEXUAL HARASSMENT, or any IPC crime on a train or railway platform — go to GRP. If you are facing issues related to TICKETLESS TRAVEL, CHAIN PULLING, UNAUTHORIZED VENDING, DAMAGE TO RAILWAY PROPERTY, or TRESPASSING — go to RPF. In emergencies, approach the nearest uniformed personnel (either GRP or RPF) and they will coordinate with the appropriate authority.",
        "doc_type": "jurisdiction_guide",
        "incident_type": "general",
        "legal_remedy": "guidance",
        "authority": "GRP/RPF",
        "section_ref": "Railway Protection Force Act + Police Act",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "GRP Station locations in Mumbai Suburban Railway: Western Line — Churchgate, Mumbai Central, Dadar, Bandra, Andheri, Borivali, Virar. Central Line — CST, Dadar, Kurla, Ghatkopar, Thane, Dombivli, Kalyan. Harbour Line — CST, Wadala, Kurla, Vashi, Panvel. Not all stations have GRP posts — at stations without GRP, the regular Maharashtra Police or RPF will record your complaint and forward it to the nearest GRP station.",
        "doc_type": "jurisdiction_guide",
        "incident_type": "general",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "Maharashtra Police SOPs",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },
    {
        "text": "RPF Emergency Helpline and Complaint Process: The Railway Protection Force operates a 24/7 helpline at 182 (Railway Security Helpline). Passengers can call 182 for immediate assistance related to security issues on trains and platforms. RPF also accepts complaints through the Rail Madad portal (railmadad.indianrailways.gov.in). For women's safety, RPF runs 'Meri Saheli' initiative with dedicated women RPF officers on long-distance and suburban trains.",
        "doc_type": "jurisdiction_guide",
        "incident_type": "general",
        "legal_remedy": "helpline",
        "authority": "RPF",
        "section_ref": "RPF Standard Operating Procedures",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # CPGRAMS FILING PROCEDURES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "CPGRAMS (Centralized Public Grievance Redress and Monitoring System) is the Government of India's official platform for filing public grievances. For railway-related grievances, complaints can be filed at pgportal.gov.in. The Ministry of Railways is listed as a separate department. Filing is free and does not require a lawyer. Complaints are automatically assigned to the relevant railway division for resolution.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "CPGRAMS Portal Guidelines",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "How to file a railway grievance on CPGRAMS: Step 1 — Visit pgportal.gov.in and register with mobile number and email. Step 2 — Select Ministry: 'Ministry of Railways'. Step 3 — Select Department/Organisation (e.g., 'Western Railway' or 'Central Railway'). Step 4 — Select Category: Safety, Punctuality, Cleanliness, Catering, Staff Behavior, Corruption, etc. Step 5 — Provide detailed description including train number, date, time, station, and nature of complaint. Step 6 — Upload supporting documents (photos, tickets, medical reports). Step 7 — Submit and note the Registration Number for tracking.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "CPGRAMS Portal Guidelines",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "CPGRAMS tracking and escalation: After filing, complaints are tracked via the Registration Number. The concerned railway authority must respond within 30 days. If no response is received, the complaint is automatically escalated to the next level. You can track progress at pgportal.gov.in using your Registration Number. If dissatisfied with the response, you can request reopening of the grievance within 30 days of closure. Persistent unresolved grievances can be escalated to the Railway Board level.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "CPGRAMS Escalation Policy",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "CPGRAMS categories for railway complaints: 1) Safety & Security — accidents, thefts, assaults. 2) Punctuality — chronic delays, cancellations without notice. 3) Cleanliness — dirty coaches, unclean platforms, clogged toilets. 4) Catering — overcharging, poor quality food. 5) Staff Behavior — rude behavior, corruption, refusal of duty. 6) Booking & Reservation — unauthorized tout, tatkal quota misuse. 7) Infrastructure — broken seats, non-functional fans/lights, water leakage. 8) Medical — inadequate first aid, ambulance availability.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "CPGRAMS Category List",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Rail Madad — Quick complaint resolution: Rail Madad (railmadad.indianrailways.gov.in) is the Indian Railways' own grievance portal, faster than CPGRAMS. Complaints filed on Rail Madad are directly routed to the Station Master, Divisional Office, or Zonal Office depending on severity. Average resolution time is 3-7 days. Available as Android/iOS app. Accepts photo/video evidence. Best for operational complaints (cleanliness, staff behavior, facilities).",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "Rail Madad",
        "section_ref": "Rail Madad Portal",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # RAILWAY CLAIMS TRIBUNAL (RCT) PROCEDURES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Railway Claims Tribunal (RCT) — Overview: The RCT was established under the Railway Claims Tribunal Act 1987 to provide speedy adjudication of claims for compensation for accidents involving railways. The Tribunal has exclusive jurisdiction over accident claims — civil courts cannot entertain such claims. There are multiple RCT benches across India including Mumbai (Western Railway), Mumbai (Central Railway), and other major cities.",
        "doc_type": "legal_statute",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railway Claims Tribunal Act 1987",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "How to file a claim at RCT: Step 1 — Obtain a certified copy of the FIR from GRP. Step 2 — Collect medical records (injury certificate, discharge summary, disability certificate if applicable). Step 3 — Prepare the claim application (Form available at RCT office or online). Step 4 — Attach supporting documents: railway ticket or pass, FIR copy, medical reports, photographs of injuries, witness affidavits. Step 5 — Pay the prescribed court fee. Step 6 — File at the appropriate RCT bench (based on where the accident occurred).",
        "doc_type": "filing_procedure",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railway Claims Tribunal Rules 1989",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "RCT claim time limits: Claims for compensation must be filed within 3 years of the date of the accident. However, the Tribunal may condone the delay if sufficient cause is shown for not filing within the prescribed period. In practice, RCT benches are lenient with time limits for genuine accident victims, especially in cases of serious injury or death where the family may have been in distress.",
        "doc_type": "filing_procedure",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Limitation Act + RCT Act 1987",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "RCT Mumbai Bench details: The Mumbai RCT benches are located at Churchgate (Western Railway jurisdiction) and CST (Central Railway jurisdiction). Operating hours: 10:30 AM to 5:00 PM, Monday to Friday. Free legal aid is available for economically weaker sections through the District Legal Services Authority. Advocates specializing in railway accident claims can be found at the RCT premises.",
        "doc_type": "filing_procedure",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "RCT Mumbai Administrative Orders",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },
    {
        "text": "Documents required for RCT claim filing: 1) Claim application form (available at RCT). 2) Certified copy of FIR from GRP. 3) Original or certified copy of railway ticket/pass. 4) Medical records — injury certificate, X-rays, MRI reports, discharge summary. 5) Death certificate (in fatal cases). 6) Post-mortem report (in fatal cases). 7) Photographs of injuries or accident scene. 8) Witness affidavits. 9) Income certificate of the deceased (for calculating compensation). 10) Family tree/legal heir certificate (for death claims).",
        "doc_type": "filing_procedure",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "RCT Procedural Requirements",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # INCIDENT-SPECIFIC LEGAL GUIDANCE
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Legal remedies for theft on Mumbai suburban trains: 1) Immediately report to GRP at the nearest station. Insist on filing an FIR — GRP cannot refuse to register an FIR for a cognizable offence. 2) Note train number, coach number, time, and direction. 3) If GRP refuses FIR, approach the Senior Divisional Security Commissioner or file a complaint on CPGRAMS. 4) For mobile phone theft, provide IMEI number to GRP for tracking. 5) If the stolen item is recovered, GRP will return it after completing formalities.",
        "doc_type": "legal_statute",
        "incident_type": "theft",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "IPC Section 378/379 + Railways Act",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },
    {
        "text": "Legal remedies for assault/pushing on trains: Pushing incidents on Mumbai suburban trains, especially during peak hours, that result in injury are both criminal offences and grounds for compensation. Criminal complaint: File FIR at GRP under IPC Section 323 (voluntarily causing hurt) or 325 (grievous hurt). Compensation: If the push results in falling from the train, claim under Section 124A (untoward incident). Document injuries with medical certificate immediately. CCTV footage can be requested from railway authorities.",
        "doc_type": "legal_statute",
        "incident_type": "assault",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "IPC Section 323/325 + Railways Act Section 124A",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },
    {
        "text": "Legal remedies for sexual harassment on trains: 1) Call Railway Women Helpline: 182 or 1512. 2) Use SOS button on UTS app (Mumbai suburban). 3) File FIR at GRP under IPC Section 354 (assault on woman with intent to outrage modesty), 354A (sexual harassment), or Section 509 (word/gesture to insult modesty). 4) For serious offences, invoke POCSO Act (if victim is minor). 5) RPF's 'Meri Saheli' initiative deploys women RPF officers on trains — flag them. 6) If GRP/RPF does not respond, file complaint on Rail Madad app.",
        "doc_type": "legal_statute",
        "incident_type": "sexual_harassment",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "IPC Section 354/354A/509 + POCSO Act",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Legal remedies for chain snatching on trains: Chain snatching is treated as robbery under IPC Section 392 (punishment for robbery — up to 10 years imprisonment and fine). File FIR immediately at the nearest GRP station. Provide description of the accused. If the snatching causes injury, additional charges under IPC Section 324/326 (causing hurt with dangerous weapon/means) may apply. Request CCTV footage from the station where the incident occurred.",
        "doc_type": "legal_statute",
        "incident_type": "robbery",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "IPC Section 392 + Railways Act",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Legal remedies for overcrowding complaints: While overcrowding itself is not a criminal offence by passengers, the railway administration has a duty to manage crowd levels. Remedies: 1) File complaint on CPGRAMS under 'Safety' category citing specific train numbers and times. 2) File RTI asking for passenger count data vs train capacity. 3) If overcrowding causes injury/death, claim compensation under Section 124A. 4) PIL (Public Interest Litigation) has been filed in Bombay HC regarding Mumbai suburban overcrowding — refer to Case: Vineet Narain v. Union of India.",
        "doc_type": "legal_statute",
        "incident_type": "overcrowding",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "Railways Act Section 124A + Constitutional Rights",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },
    {
        "text": "Legal remedies for platform accidents and falling between train and platform: 1) Immediately call Railway Emergency Helpline 139. 2) Seek medical attention from the Railway Hospital or First Aid Post at the station. 3) File FIR at GRP station. 4) Collect medical documentation. 5) File claim at RCT under Section 123/124A — the railway administration is strictly liable for platform gap injuries. 6) If the accident is due to poor maintenance or lack of barriers, additional negligence claim can be made. Mumbai suburban has seen courts award Rs. 5L-15L for platform gap injuries.",
        "doc_type": "legal_statute",
        "incident_type": "platform_gap",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act Section 123/124A",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },
    {
        "text": "Legal remedies for death on railway tracks (trespassing vs accident): Deaths on railway tracks are classified differently based on circumstances. If the person was a bona fide passenger who fell from a train — full compensation under Section 124A. If the person was crossing tracks at an unmanned crossing — compensation under Section 126. If the person was trespassing — no compensation under Railways Act, but family can still file civil suit for negligence if railway failed to provide fencing or warning signs.",
        "doc_type": "legal_statute",
        "incident_type": "death",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act Sections 123, 124A, 126",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Legal remedies for injuries caused by stone pelting on trains: Stone pelting on trains is a criminal offence under Section 152 of the Railways Act (punishment up to life imprisonment) and IPC Section 336/337 (endangering life or personal safety). Victims should: 1) Pull emergency chain to stop train if needed. 2) Report to GRP with exact location (between which stations). 3) Seek medical attention. 4) If injured, claim compensation under Section 124A as an 'untoward incident'. Railway is strictly liable even though the pelting was done by outsiders.",
        "doc_type": "legal_statute",
        "incident_type": "stone_pelting",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "Railways Act Section 152 + IPC Section 336/337",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # RTI TEMPLATES FOR RAILWAY COMPLAINTS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "RTI Application Template for Railway Information: To, The Central Public Information Officer (CPIO), [Western Railway/Central Railway Office Address]. Subject: Application under Section 6(1) of the Right to Information Act, 2005. Sir/Madam, Under the provisions of the RTI Act 2005, I request the following information: [Specify information needed]. I am ready to pay the prescribed fee. [Attach Rs. 10 fee via Indian Postal Order/DD]. Name: ___ Address: ___ Phone: ___ Date: ___",
        "doc_type": "rti_template",
        "incident_type": "general",
        "legal_remedy": "rti",
        "authority": "CPIO Railway",
        "section_ref": "Right to Information Act 2005, Section 6",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "RTI for seeking railway accident statistics: Sample RTI text: 'Please provide the following information: 1) Total number of railway accidents (including untoward incidents) on Mumbai suburban railways for the years 2022, 2023, 2024, and 2025. 2) Classification of accidents by type (falling from train, platform gap, collision, etc.). 3) Total compensation paid by railway administration for each year. 4) Number of pending cases at Mumbai RCT bench.' Filing fee: Rs. 10. Address to: CPIO, Western Railway/Central Railway Head Office, Churchgate/CST, Mumbai.",
        "doc_type": "rti_template",
        "incident_type": "accident",
        "legal_remedy": "rti",
        "authority": "CPIO Railway",
        "section_ref": "RTI Act 2005",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },
    {
        "text": "RTI for seeking CCTV footage of railway incident: Sample RTI text: 'Please provide the following information: 1) Whether CCTV cameras are installed at [Station Name] platform number [X]. 2) If yes, provide a copy of the CCTV footage from [Date] between [Time] and [Time] covering platform [X]. 3) The retention period for CCTV footage at this station. 4) If footage has been deleted, the reason for deletion and the officer responsible.' Note: CCTV footage may be denied under Section 8(1)(h) if it impedes investigation. File RTI within 7 days as footage is typically retained for only 7-30 days.",
        "doc_type": "rti_template",
        "incident_type": "general",
        "legal_remedy": "rti",
        "authority": "CPIO Railway",
        "section_ref": "RTI Act 2005, Section 6 and 8",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "RTI for seeking information about train overcrowding: Sample RTI text: 'Please provide: 1) The sanctioned passenger carrying capacity of [Train Number/Name]. 2) The average passenger count during peak hours (8 AM to 10 AM) on this train for the last 3 months. 3) Steps taken by the administration to reduce overcrowding on this route. 4) Any committee recommendations regarding suburban train capacity augmentation.' This RTI is useful as documentary evidence for a compensation claim if overcrowding caused an injury.",
        "doc_type": "rti_template",
        "incident_type": "overcrowding",
        "legal_remedy": "rti",
        "authority": "CPIO Railway",
        "section_ref": "RTI Act 2005",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # HELPLINE DIRECTORY
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Railway Emergency Helpline Numbers for Mumbai: 1) Railway Helpline (General): 139. 2) Railway Security Helpline (RPF): 182. 3) Railway Accident Emergency: 1072. 4) Women Safety Helpline (Railway): 182 or 1512. 5) GRP Control Room Mumbai: 022-22694727. 6) Western Railway Control Room: 022-22032811. 7) Central Railway Control Room: 022-22622540. 8) Rail Madad App: Available on Android/iOS. 9) IRCTC Customer Care: 14646.",
        "doc_type": "helpline_directory",
        "incident_type": "general",
        "legal_remedy": "helpline",
        "authority": "Indian Railways",
        "section_ref": "Railway Emergency Contacts",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },
    {
        "text": "Legal Aid and Free Consultation for Railway Accident Victims: 1) District Legal Services Authority (DLSA) Mumbai — provides free legal aid to economically weaker sections. Phone: 022-22631656. 2) National Legal Services Authority (NALSA) Helpline: 15100. 3) Mumbai Legal Aid Centre at High Court: Free advice on compensation claims. 4) Pro-bono lawyers available at RCT bench Churchgate and CST. Note: Victims with annual income below Rs. 3 lakh are entitled to free legal representation under Legal Services Authorities Act 1987.",
        "doc_type": "helpline_directory",
        "incident_type": "accident",
        "legal_remedy": "legal_aid",
        "authority": "DLSA/NALSA",
        "section_ref": "Legal Services Authorities Act 1987",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },
    {
        "text": "Online complaint and grievance portals for railway issues: 1) CPGRAMS — pgportal.gov.in (for serious grievances to Ministry of Railways). 2) Rail Madad — railmadad.indianrailways.gov.in (for operational complaints, fastest resolution). 3) IRCTC e-Complaint — irctc.co.in (for booking/catering/e-ticket issues). 4) RPF Complaint Portal — rpf.indianrailways.gov.in. 5) Twitter: @RailMinIndia, @WesternRly, @CaborNotCr (Western/Central Railway social media cells respond within hours).",
        "doc_type": "helpline_directory",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "Multiple",
        "section_ref": "Railway Digital Grievance Platforms",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Railway Hospital and Medical Facility contacts in Mumbai: 1) Railway Hospital Byculla: 022-23710782 (largest railway hospital in Mumbai, handles emergency trauma from train accidents). 2) First Aid Post CST: Available 24/7 at platform 1. 3) First Aid Post Dadar: Available at both Western and Central side. 4) First Aid Post Churchgate: Available at platform entrance. 5) Medical vans on emergency call — dial 139. All railway hospitals provide FREE treatment to railway accident victims regardless of whether they have a valid ticket.",
        "doc_type": "helpline_directory",
        "incident_type": "accident",
        "legal_remedy": "medical",
        "authority": "Railway Medical Services",
        "section_ref": "Railway Medical Manual",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # WOMEN SAFETY — SPECIFIC PROVISIONS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Women safety provisions on Indian Railways: 1) Ladies compartments are reserved in all suburban trains — unauthorized entry by males is punishable under Section 147 of Railways Act. 2) RPF 'Meri Saheli' initiative deploys plain-clothes women RPF officers on trains. 3) SOS button on UTS and M-indicator apps directly alerts RPF. 4) CCTV cameras are mandatory in ladies compartments. 5) Under the Sexual Harassment of Women at Workplace Act 2013, railway platforms and trains are 'workplaces' for women railway employees — Internal Complaints Committee exists at each division.",
        "doc_type": "legal_statute",
        "incident_type": "sexual_harassment",
        "legal_remedy": "complaint",
        "authority": "RPF",
        "section_ref": "Railways Act Section 147 + SHW Act 2013",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Zero FIR for women victims on trains: Under the Criminal Law (Amendment) Act 2013, any police station (including GRP) must register a 'Zero FIR' for sexual offences. This means a woman victim does not need to go to the GRP station of the jurisdiction where the offence occurred — she can file at ANY GRP or police station, and it will be transferred. This is especially important for suburban train incidents where the victim may have continued the journey to her destination station.",
        "doc_type": "legal_statute",
        "incident_type": "sexual_harassment",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "Criminal Law Amendment Act 2013 + CrPC Section 154",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # CASE LAW / PRECEDENTS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Landmark case: Union of India v. Rina Devi (2018) — The Supreme Court held that for claiming compensation under Section 124A of the Railways Act, 1989, it is not necessary for the claimant to prove any negligence or fault on the part of the railway administration. The Act imposes strict liability. The claimant need only prove that the accident/untoward incident occurred 'in the course of working of the railway'. This case significantly expanded compensation rights for Mumbai suburban rail victims.",
        "doc_type": "case_law",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Supreme Court",
        "section_ref": "Union of India v. Rina Devi (2018) SC",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Landmark case: Jameela v. Union of India (2021) — The Supreme Court clarified that even if a passenger does not have a valid ticket, they are still entitled to compensation under Section 124A if they sustain injury during an 'untoward incident'. The absence of a ticket does not bar the claim for compensation. This is important for Mumbai suburban commuters who may have monthly passes that expired or daily tickets that were lost during the incident.",
        "doc_type": "case_law",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Supreme Court",
        "section_ref": "Jameela v. Union of India (2021) SC",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Bombay High Court on overcrowding deaths (2019): In a landmark order, the Bombay High Court directed the Central and Western Railways to take concrete steps to reduce overcrowding on Mumbai suburban trains. The court observed that deaths due to overcrowding amount to 'institutional failure' and directed railways to: 1) Install platform screen doors at major stations. 2) Increase train frequency during peak hours. 3) Deploy additional RPF for crowd management. The court also held that all overcrowding-related deaths must be treated as 'untoward incidents' under Section 124A.",
        "doc_type": "case_law",
        "incident_type": "overcrowding",
        "legal_remedy": "compensation",
        "authority": "Bombay High Court",
        "section_ref": "Bombay HC Order on Suburban Rail Safety (2019)",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },
    {
        "text": "RCT precedent on platform gap injuries: The Railway Claims Tribunal (Mumbai bench) in multiple cases including Claim No. WR/2019/0142 has awarded compensation of Rs. 5-15 lakh for platform gap injuries. The Tribunal held that the railway administration is responsible for maintaining adequate infrastructure to prevent passengers from falling between the platform and the train. The age and width of platforms at many Mumbai suburban stations are recognized as systemic hazards.",
        "doc_type": "case_law",
        "incident_type": "platform_gap",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "RCT Mumbai Bench precedents",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # CONSUMER PROTECTION & ADDITIONAL REMEDIES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Consumer Protection Act 2019 and railway services: Railway passengers are 'consumers' under the Consumer Protection Act 2019. For deficiency in service (chronic delays, dirty coaches, rude staff, overcharging), passengers can file complaints at: 1) District Consumer Forum — for claims up to Rs. 1 crore. 2) State Consumer Commission — for claims Rs. 1-10 crore. 3) National Consumer Commission — for claims above Rs. 10 crore. Filing fee: Rs. 200 (District) to Rs. 5,000 (National). No lawyer required.",
        "doc_type": "legal_statute",
        "incident_type": "service_deficiency",
        "legal_remedy": "consumer_complaint",
        "authority": "Consumer Forum",
        "section_ref": "Consumer Protection Act 2019",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Filing a PIL (Public Interest Litigation) for railway safety: Systemic safety issues on Mumbai suburban railways can be addressed through PIL in the Bombay High Court. Individuals or NGOs can file PILs for: 1) Inadequate safety infrastructure. 2) Chronic overcrowding. 3) Lack of medical facilities at stations. 4) Dangerous level crossings. Filing a PIL does not require a lawyer (can be sent by post/email to the HC). The HC has been active in monitoring railway safety reforms through PIL proceedings.",
        "doc_type": "legal_statute",
        "incident_type": "general",
        "legal_remedy": "pil",
        "authority": "Bombay High Court",
        "section_ref": "Article 226, Constitution of India",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # MUMBAI SUBURBAN SPECIFIC — COMMON ISSUES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Mega Block disruption rights: During mega blocks (planned engineering blocks), the railway administration is required to: 1) Announce mega block schedule at least 48 hours in advance. 2) Arrange alternative bus services between affected stations. 3) Display notice at all affected stations. If mega block causes injury or stranding: File complaint on CPGRAMS. If alternative transport was not arranged, file under 'Service Deficiency' at Consumer Forum.",
        "doc_type": "filing_procedure",
        "incident_type": "disruption",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "Railway Board Circular on Mega Blocks",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },
    {
        "text": "Rights during train cancellation or heavy delays: 1) Refund: For cancelled trains, full refund of ticket price (even for monthly passes — pro-rata). 2) If delay exceeds 3 hours, passenger is entitled to drinking water and basic amenities. 3) No automatic compensation for delays under Indian Railways policy (unlike EU regulations). 4) Recourse: File on CPGRAMS for chronic delays (repeated delays on specific train numbers). 5) RTI: Seek information about punctuality performance of specific trains to build a case.",
        "doc_type": "filing_procedure",
        "incident_type": "delay",
        "legal_remedy": "refund",
        "authority": "Railway Administration",
        "section_ref": "Railway Passengers (Cancellation & Refund) Rules",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Unauthorized vendors and hawkers on trains: Unauthorized vending on trains and platforms is an offence under Section 144 of the Railways Act 1989, punishable with fine up to Rs. 2,000. Complaints about aggressive hawkers should be directed to RPF (not GRP). If a hawker causes injury or blocks emergency exits, report to RPF at 182. For systemic hawker issues, file complaint on CPGRAMS under 'Unauthorized Vending' category.",
        "doc_type": "legal_statute",
        "incident_type": "unauthorized_vending",
        "legal_remedy": "complaint",
        "authority": "RPF",
        "section_ref": "Railways Act 1989, Section 144",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Begging and antisocial behavior on trains: Under Section 145 of the Railways Act 1989, begging and other antisocial behavior (including playing loud music, blocking doors, smoking) on railway premises is punishable with imprisonment up to 6 months or fine up to Rs. 500 or both. Report to RPF. For persistent issues on specific routes, file systematic complaint on CPGRAMS with dates, times, and train numbers.",
        "doc_type": "legal_statute",
        "incident_type": "nuisance",
        "legal_remedy": "complaint",
        "authority": "RPF",
        "section_ref": "Railways Act 1989, Section 145",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # FIR PROCEDURES AND POLICE COMPLAINT PROCESSES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "How to file an FIR at GRP station: Step 1 — Visit the GRP station at the nearest major railway station. Step 2 — Clearly state the details: train number, coach, date, time, direction of travel, description of accused (if known). Step 3 — GRP is LEGALLY BOUND to register an FIR for cognizable offences (theft, assault, robbery, sexual harassment). Step 4 — If GRP refuses, note the officer's name and badge number. Step 5 — Write to Senior Divisional Security Commissioner (SDSC) of the railway zone. Step 6 — Alternatively, file E-FIR through Maharashtra Police website (mahapolice.gov.in) for select offences.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "CrPC Section 154",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },
    {
        "text": "What to do if GRP refuses to file FIR: Under Section 154(3) of CrPC, if a police officer refuses to register an FIR, the complainant can send a written complaint to the Superintendent of Police (for GRP, this is the Senior Divisional Security Commissioner). The SP/SDSC is required to either investigate the case or direct a subordinate to investigate. If this also fails: 1) File complaint before the Judicial Magistrate under Section 156(3) CrPC. 2) File complaint on CPGRAMS against the GRP officer. 3) File complaint with State Human Rights Commission. 4) Approach the Railway Board's vigilance department.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "CrPC Section 154(3) and 156(3)",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # COMPENSATION CALCULATION GUIDANCE
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Compensation calculation for railway accident injuries: The compensation under the Second Schedule is a MINIMUM — the RCT can award higher amounts based on: 1) Age of the victim (multiplier tables similar to Motor Vehicle Act). 2) Income of the victim (annual income × remaining working years). 3) Severity of injury (percentage of disability). 4) Medical expenses (past and estimated future). 5) Pain and suffering (discretionary). 6) Loss of earning capacity. For Mumbai suburban victims, recent awards have ranged from Rs. 2L (minor injury) to Rs. 25L (permanent disability) to Rs. 30L+ (death of earning member).",
        "doc_type": "compensation_schedule",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act Second Schedule + RCT Precedents",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Interim relief from Railway Administration: Under Section 125, the Railway Administration may provide interim relief before the final compensation is determined by RCT. How to claim: 1) Submit application at the Divisional Railway Manager's office. 2) Attach medical certificate and FIR copy. 3) Typical interim relief: Rs. 15,000-50,000 for injury, Rs. 50,000-1,00,000 for grievous hurt, Rs. 1,00,000-2,00,000 for death. 4) This does not require filing at RCT — it's an administrative payment. 5) The interim amount is later adjusted against the final compensation.",
        "doc_type": "compensation_schedule",
        "incident_type": "accident",
        "legal_remedy": "interim_relief",
        "authority": "Divisional Railway Manager",
        "section_ref": "Railways Act 1989, Section 125",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # DIGITAL EVIDENCE AND DOCUMENTATION
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Preserving digital evidence for railway complaints: 1) Photograph injuries immediately with timestamp. 2) Video record the scene if possible. 3) Screenshot any relevant messages/alerts from M-indicator or UTS app showing train details. 4) Note down names and phone numbers of witnesses. 5) Save railway ticket/pass — do not discard after journey. 6) Request CCTV footage via RTI within 7 days (footage retention is typically 7-30 days). 7) Record medical treatment details including hospital name, doctor name, and case number. All digital evidence is admissible under Section 65B of the Indian Evidence Act.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "evidence",
        "authority": "General",
        "section_ref": "Indian Evidence Act Section 65B",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Medical documentation requirements for railway accident claims: To support a compensation claim, you need: 1) First Aid Report from railway medical room (free at station). 2) Injury Certificate from treating hospital — must specify nature and extent of injuries. 3) X-ray/MRI/CT scan reports with films. 4) Discharge Summary from hospital. 5) Disability Certificate (if permanent disability) from government hospital — issued by a Medical Board of 3 doctors. 6) Follow-up treatment records. 7) Pharmacy bills for medicines. All documents should ideally be from government/railway hospitals as they carry more evidentiary weight.",
        "doc_type": "filing_procedure",
        "incident_type": "accident",
        "legal_remedy": "evidence",
        "authority": "Medical Authorities",
        "section_ref": "RCT Evidentiary Requirements",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # SPECIAL PROVISIONS FOR DIFFERENTLY-ABLED AND SENIOR CITIZENS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Rights of differently-abled passengers on railways: Under the Rights of Persons with Disabilities Act 2016, Indian Railways must provide: 1) Wheelchair access at stations. 2) Ramps and tactile paths. 3) Reserved berths/seats in trains. 4) Battery-operated vehicles for mobility between platforms. If any of these facilities are missing or non-functional, file complaint on: Rail Madad (quickest), CPGRAMS (for systemic issues), or approach Disability Commissioner. For Mumbai suburban, most major stations have been retrofitted but many intermediate stations lack adequate facilities.",
        "doc_type": "legal_statute",
        "incident_type": "accessibility",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "Rights of Persons with Disabilities Act 2016",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Senior citizen rights and facilities on railways: Senior citizens (60+ years for males, 58+ for females) are entitled to: 1) Concession in ticket fare (40-50% for male, 50% for female). 2) Lower berth preference in reserved coaches. 3) Dedicated queues at booking counters. 4) Wheelchair assistance at major stations (request through 139 helpline). If a senior citizen is injured due to inadequate facilities (e.g., no ramps, no escalators at station), enhanced compensation may be claimed citing the duty of care owed to vulnerable passengers.",
        "doc_type": "legal_statute",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "Railway Administration",
        "section_ref": "Railway Board Circulars on Senior Citizen Facilities",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # ADDITIONAL INCIDENT TYPES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Legal remedies for electrocution on railway premises: Electrocution from overhead wires (OHE) or faulty electrical installations at stations is a serious issue. The railway administration is strictly liable under Section 123 for electrocution injuries on railway premises. Compensation: Same as accident schedule — Rs. 8L for death, Rs. 7.5L for grievous hurt. Additional negligence claim possible. Recent cases: Several Mumbai suburban commuters electrocuted while crossing tracks or touching damaged electrical equipment. File FIR at GRP + claim at RCT.",
        "doc_type": "legal_statute",
        "incident_type": "electrocution",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act Section 123 + Electricity Act 2003",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Legal remedies for food poisoning from railway catering: If a passenger falls ill due to contaminated food served on trains or at railway station food stalls licensed by IRCTC: 1) File complaint on Rail Madad immediately with photos of food and medical report. 2) File complaint at Consumer Forum for deficiency in service. 3) File FIR under Food Safety and Standards Act 2006 if adulteration is suspected. 4) IRCTC catering complaints: irctc.co.in or call 14646. The railway is vicariously liable for food served by its licensed caterers.",
        "doc_type": "legal_statute",
        "incident_type": "food_poisoning",
        "legal_remedy": "consumer_complaint",
        "authority": "Consumer Forum",
        "section_ref": "Food Safety and Standards Act 2006 + Consumer Protection Act",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Legal remedies for damage to personal belongings during travel: Under the Railways Act 1989, the railway administration is a common carrier and is liable for loss or damage to luggage booked through railway booking. However, for personal belongings carried by the passenger (not booked luggage), the passenger must prove negligence. For Mumbai suburban trains — if belongings are damaged due to train derailment, collision, or any 'accident' — claim under Section 123. If damaged by other passengers (e.g., in a stampede) — file FIR at GRP.",
        "doc_type": "legal_statute",
        "incident_type": "property_damage",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Chapter XI",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # STAMPEDE AND CROWD CRUSH INCIDENTS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Legal remedies for stampede at railway station: Stampedes at Mumbai suburban railway stations (notably Elphinstone Road/Prabhadevi 2017 stampede) are classified as 'untoward incidents' under Section 124A. The railway administration is strictly liable. After the Elphinstone stampede, the Railway Board issued special directives for: 1) Width expansion of FOBs (Foot Over Bridges). 2) Installation of crowd monitoring cameras. 3) Deployment of RPF for crowd management during peak hours. Victims: File FIR at GRP + claim at RCT. The 2017 stampede victims were awarded Rs. 5L-15L each.",
        "doc_type": "case_law",
        "incident_type": "stampede",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act Section 124A + Railway Board Circular 2017",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },
    {
        "text": "Crowd management obligations of railway administration: The Bombay High Court has directed that railway administration must: 1) Deploy adequate RPF/GRP at peak hours. 2) Regulate crowd flow at narrow FOBs and staircases. 3) Make public announcements for crowd control. 4) Install crowd density monitors at major stations. 5) Ensure emergency exits are not blocked. Failure to implement these measures makes the railway administration liable for any resulting injuries or deaths. Reference: PIL by Rishi Agarwal v. Union of India (Bombay HC, 2018).",
        "doc_type": "case_law",
        "incident_type": "stampede",
        "legal_remedy": "pil",
        "authority": "Bombay High Court",
        "section_ref": "Bombay HC PIL on Crowd Management",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # INSURANCE AND ADDITIONAL COMPENSATION
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Railway Passenger Insurance: Under the Railway Passenger Insurance Scheme (merged with ticket price since 2016), every bona fide passenger is automatically insured. The insurance covers: death (up to Rs. 10 lakh), permanent total disability (Rs. 7.5 lakh), permanent partial disability (up to Rs. 7.5 lakh), hospitalization (up to Rs. 2 lakh), transportation of mortal remains (Rs. 10,000). This insurance is IN ADDITION to compensation under the Railways Act Second Schedule. Claims are processed by the concerned railway zone.",
        "doc_type": "compensation_schedule",
        "incident_type": "accident",
        "legal_remedy": "insurance",
        "authority": "Railway Administration",
        "section_ref": "Railway Passenger Insurance Scheme",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Ex-gratia payment by railways for accident victims: In addition to statutory compensation, the railway administration provides ex-gratia payments in serious accidents: 1) Death: Rs. 5 lakh ex-gratia (paid immediately, no paperwork). 2) Grievous injury: Rs. 1 lakh ex-gratia. 3) Simple injury: Rs. 50,000 ex-gratia. These payments are made directly by the Divisional Railway Manager's office without requiring any application to RCT. The ex-gratia is in addition to both the Second Schedule compensation and the passenger insurance coverage.",
        "doc_type": "compensation_schedule",
        "incident_type": "accident",
        "legal_remedy": "ex_gratia",
        "authority": "Divisional Railway Manager",
        "section_ref": "Railway Board Guidelines on Ex-Gratia Payments",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # LANGUAGE-SPECIFIC GUIDANCE (MARATHI/HINDI)
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Marathi complaint template for GRP FIR: श्रीमान पोलीस निरीक्षक, GRP [स्टेशन नाव]. विषय: [गुन्ह्याचा प्रकार] बाबत FIR नोंदणी. मी [नाव], [पत्ता], [दिनांक] रोजी [ट्रेन क्रमांक/नाव] या गाडीत [स्टेशन] ते [स्टेशन] दरम्यान प्रवास करत असताना [घटनेचे वर्णन]. कृपया माझ्या तक्रारीची FIR नोंदणी करावी. Note: GRP is legally bound to accept complaints in Marathi as it is the official state language of Maharashtra.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "Maharashtra Official Languages Act + CrPC 154",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },
    {
        "text": "Hindi complaint template for CPGRAMS: सेवा में, मंत्रालय — रेल मंत्रालय. विषय: [शिकायत का प्रकार]. महोदय/महोदया, मैं [नाम], [पता], दिनांक [तारीख] को [ट्रेन नंबर/नाम] में [स्टेशन] से [स्टेशन] यात्रा करते समय [घटना का विवरण]. इस संबंध में मैं निम्नलिखित कार्यवाही की मांग करता/करती हूं: [मांग]. कृपया इस शिकायत पर शीघ्र कार्यवाही करें. Note: CPGRAMS accepts complaints in Hindi and English. Marathi complaints should be transliterated or filed through Rail Madad which supports regional languages.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "Official Languages Act + CPGRAMS Policy",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # STRUCTURAL SAFETY AND INFRASTRUCTURE COMPLAINTS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Complaints about dangerous railway infrastructure: For reporting dangerous infrastructure at stations (broken FOB, damaged platform edge, faulty escalator, water logging, poor lighting): 1) Immediate: Call 139 or tweet to @RailMinIndia/@WesternRly. 2) Formal: File on Rail Madad under 'Infrastructure' category with photos. 3) Systemic: File on CPGRAMS under 'Safety' category. 4) If the dangerous condition has caused or is likely to cause injury — file FIR at GRP citing negligence. 5) RTI: Seek information about when last safety audit was conducted at the station.",
        "doc_type": "filing_procedure",
        "incident_type": "infrastructure",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "Railway Safety Directorate Guidelines",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Water logging at railway stations — rights and remedies: Mumbai suburban railway stations frequently get waterlogged during monsoon. If you are injured due to waterlogging (slipping, falling, electric shock from submerged wires): 1) This is a railway accident — claim compensation under Section 123. 2) File FIR at GRP documenting the dangerous conditions. 3) File complaint on CPGRAMS under 'Safety'. 4) Take photos/videos as evidence. The railway administration has a duty to maintain safe station premises and is liable for injuries caused by foreseeable monsoon flooding.",
        "doc_type": "filing_procedure",
        "incident_type": "waterlogging",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act Section 123 + Municipal Corporation Act",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # ANTI-CORRUPTION AND STAFF MISCONDUCT
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Reporting corruption by railway staff: Corruption by TTE, booking clerks, or other railway staff can be reported through: 1) Railway Vigilance Department — each zone has a Chief Vigilance Officer (CVO). 2) Central Vigilance Commission (CVC) — cvc.gov.in. 3) Anti-Corruption Bureau (ACB) Maharashtra — for GRP/RPF corruption. 4) CPGRAMS under 'Corruption' category. 5) If caught taking bribe — call ACB helpline 1064 and they will arrange a trap operation. Document evidence: audio/video recording of bribe demand is admissible in court.",
        "doc_type": "filing_procedure",
        "incident_type": "corruption",
        "legal_remedy": "complaint",
        "authority": "CVO Railway / CVC",
        "section_ref": "Prevention of Corruption Act 1988",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Reporting rude behavior or dereliction of duty by railway staff: 1) Note the staff member's name and badge/PF number. 2) File complaint on Rail Madad (fastest — usually resolved in 3-7 days). 3) If serious — file on CPGRAMS under 'Staff Behavior'. 4) If the behavior amounts to criminal intimidation — file FIR at GRP. 5) Tweet to @RailMinIndia with details — social media complaints get fast attention. The railway administration takes staff misconduct seriously and the concerned staff member may face departmental inquiry.",
        "doc_type": "filing_procedure",
        "incident_type": "staff_misconduct",
        "legal_remedy": "grievance",
        "authority": "Rail Madad / CPGRAMS",
        "section_ref": "Railway Servants (Discipline & Appeal) Rules",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # TRAIN DELAY AND CANCELLATION SPECIFIC
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Chronic delay compensation and remedies: While Indian Railways does not have an automatic compensation policy for delays (unlike EU Rail Passengers Rights), repeated delays on specific trains can be addressed: 1) RTI: Request punctuality data for the specific train for last 6 months. 2) CPGRAMS: File complaint citing specific dates, train numbers, and extent of delay. 3) Consumer Forum: If delays caused financial loss (missed interview, medical appointment), file complaint for deficiency in service with proof of loss. Courts have awarded Rs. 5,000-50,000 for proven financial loss due to chronic delays.",
        "doc_type": "legal_statute",
        "incident_type": "delay",
        "legal_remedy": "consumer_complaint",
        "authority": "Consumer Forum",
        "section_ref": "Consumer Protection Act 2019 + Railway Board Circulars",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Signal failure and resultant delays — legal recourse: Signal failures on Mumbai suburban railways cause massive disruptions. Remedies: 1) Document the delay with screenshots from M-indicator app showing real-time train status. 2) If stranded for more than 2 hours — tweet to @WesternRly/@CentralRly for real-time updates. 3) If the signal failure causes an accident — full compensation under Section 123. 4) For systemic signal failure issues — file RTI asking for frequency of signal failures on the section and budget allocated for signal upgrades. 5) CPGRAMS complaint under 'Punctuality' category.",
        "doc_type": "filing_procedure",
        "incident_type": "signal_failure",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS",
        "section_ref": "Railway Safety Review + CPGRAMS Policy",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # EMERGENCY PROCEDURES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Emergency procedure when someone falls from a train: 1) IMMEDIATELY pull the emergency chain/alarm (this is NOT an offence under Section 154 when there is a genuine emergency). 2) Note the exact location (between which stations, nearest landmark/kilometer post). 3) Call 139 (Railway Emergency) or 112 (All-India Emergency). 4) If possible, send someone to the nearest station to alert the Station Master. 5) Do NOT attempt to move the injured person unless they are on the tracks with a train approaching. 6) Wait for railway medical team. 7) Note names and contacts of all witnesses.",
        "doc_type": "filing_procedure",
        "incident_type": "falling",
        "legal_remedy": "emergency",
        "authority": "Railway Emergency Services",
        "section_ref": "Railway Emergency Response Manual",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Emergency procedure for fire on train: 1) Pull emergency chain/alarm. 2) Do NOT panic — move to adjacent coach if possible. 3) Use fire extinguisher if available (located near guard's coach and in AC coaches). 4) Break window glass using emergency hammer (available in AC coaches). 5) Call 139 and 112 simultaneously. 6) Help elderly, children, and differently-abled passengers first. 7) Stay low to avoid smoke inhalation. After the incident: File FIR at GRP, collect medical documentation, and file claim at RCT. Railway is strictly liable for fire-related injuries.",
        "doc_type": "filing_procedure",
        "incident_type": "fire",
        "legal_remedy": "emergency",
        "authority": "Railway Emergency Services",
        "section_ref": "Railway Fire Safety Manual + Railways Act Section 123",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # ADDITIONAL LEGAL PROVISIONS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Presumption in favor of passenger — no-fault liability: Under the Railways Act 1989, the railway administration is liable to pay compensation for accidents and untoward incidents on a NO-FAULT basis. This means the passenger does NOT need to prove negligence by the railway. The mere occurrence of the accident/incident 'in the course of working a railway' is sufficient to establish liability. The burden then shifts to the railway to prove that the injury was caused by the passenger's own criminal act or reckless behavior.",
        "doc_type": "legal_statute",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act 1989, Sections 123, 124A (Strict Liability)",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Time limits for various railway complaint remedies: 1) FIR at GRP — should be filed immediately, but can be filed at any time (no statutory time limit for cognizable offences). 2) RCT compensation claim — within 3 years of accident (extendable with cause shown). 3) Consumer Forum complaint — within 2 years of cause of action. 4) CPGRAMS grievance — no time limit, but file as soon as possible for effective resolution. 5) RTI application — no time limit, but CCTV footage request must be within 7-30 days. 6) PIL — no time limit. 7) Insurance claim — within 1 year of incident.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "guidance",
        "authority": "Multiple",
        "section_ref": "Various Acts — Limitation Periods",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # MONSOON-SPECIFIC PROVISIONS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Monsoon safety and rights on Mumbai suburban railways: During monsoon (June-September), Mumbai suburban railways face frequent disruptions. Your rights: 1) Railway must display real-time updates on platform boards and announce cancellations. 2) If stranded, railway should provide drinking water and restroom access. 3) Injuries from waterlogged platforms/tracks — fully compensable under Section 123. 4) For monsoon disruption complaints: Rail Madad or CPGRAMS. 5) If trains are running in dangerous conditions (flooded tracks) — pull chain to stop train and report to 139. Railway is liable for running trains in unsafe conditions.",
        "doc_type": "filing_procedure",
        "incident_type": "waterlogging",
        "legal_remedy": "grievance",
        "authority": "Railway Administration",
        "section_ref": "Railway Board Monsoon Preparedness Circular",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # COMPLAINT ESCALATION HIERARCHY
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Railway complaint escalation hierarchy: Level 1 — Station Master / On-duty RPF (immediate issues). Level 2 — Rail Madad portal (operational issues, 3-7 day resolution). Level 3 — Divisional Railway Manager (DRM) office of the respective division. Level 4 — CPGRAMS to Ministry of Railways (serious grievances). Level 5 — General Manager (GM) of the zonal railway. Level 6 — Railway Board, New Delhi. Level 7 — Minister of Railways office. Level 8 — Parliamentary Committee on Railways / MP intervention. Always start at Level 1-2 and escalate systematically.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "Indian Railways Hierarchy",
        "section_ref": "Railway Board Administrative Structure",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "DRM (Divisional Railway Manager) offices for Mumbai suburban: Western Railway — DRM Mumbai Central office, Phone: 022-23073000. Address: Mumbai Central Terminus Building, Mumbai 400008. Central Railway — DRM Mumbai CST office, Phone: 022-22694040. Address: CSMT Administrative Building, Mumbai 400001. Write formal letters addressed to the DRM for issues not resolved at station level. DRM offices accept walk-in complaints on working days (10 AM - 5 PM).",
        "doc_type": "helpline_directory",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "DRM Office",
        "section_ref": "Railway Administrative Directory",
        "compensation_eligible": False,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # ADDITIONAL INCIDENT TYPES (MUMBAI SPECIFIC)
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Legal recourse for delayed ambulance or medical response at railway stations: If a railway station does not have adequate first aid facilities or delays in providing medical assistance to an accident victim, the railway administration is liable for enhanced compensation. Document: 1) Time of accident. 2) Time first aid was requested. 3) Time medical help arrived. 4) Whether ambulance was available. File: RCT claim citing delayed medical response as aggravating factor. Courts have enhanced compensation by 50-100% in cases of proven delayed medical response.",
        "doc_type": "legal_statute",
        "incident_type": "medical_negligence",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act + Medical Negligence jurisprudence",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Foot Over Bridge (FOB) collapse or structural failure: If a FOB or any railway structure collapses causing injury/death — this is a clear case of railway negligence in addition to strict liability. Compensation: Full amount under Second Schedule PLUS additional compensation for proven negligence. Criminal case: FIR under IPC Section 304A (death by negligence) or 337/338 (causing grievous hurt by negligent act) against responsible railway officials. The Elphinstone Road FOB stampede led to criminal proceedings against railway engineers.",
        "doc_type": "legal_statute",
        "incident_type": "infrastructure_failure",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal + GRP",
        "section_ref": "Railways Act + IPC Sections 304A/337/338",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # MULTI-MODAL TRANSPORT RIGHTS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Rights when railway disruption forces multi-modal travel: When suburban train services are disrupted, passengers often use BEST buses, Metro, or auto-rickshaws as alternatives. The railway administration should: 1) Arrange coordination with BEST for additional bus services. 2) Display alternative route information. 3) While there is no automatic refund for alternative transport costs, you can claim the differential cost through Consumer Forum if the disruption was foreseeable and no alternative arrangement was made. Document all alternative transport expenses with receipts.",
        "doc_type": "filing_procedure",
        "incident_type": "disruption",
        "legal_remedy": "consumer_complaint",
        "authority": "Consumer Forum",
        "section_ref": "Consumer Protection Act + Railway Board Guidelines",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # SUMMARY / QUICK REFERENCE
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Quick Reference — Who to contact for what: THEFT/ROBBERY/ASSAULT/MURDER → GRP (File FIR). SEXUAL HARASSMENT → GRP + RPF Women Helpline 182/1512. TICKETLESS TRAVEL/CHAIN PULLING → RPF. RAILWAY ACCIDENT COMPENSATION → Railway Claims Tribunal. GENERAL GRIEVANCE (service quality) → Rail Madad or CPGRAMS. CORRUPTION → CVO Railway / CVC / ACB. INFRASTRUCTURE ISSUES → Rail Madad or CPGRAMS. EMERGENCY → 139 (Railway) or 112 (All-India). LEGAL AID → DLSA (022-22631656) or NALSA (15100).",
        "doc_type": "jurisdiction_guide",
        "incident_type": "general",
        "legal_remedy": "guidance",
        "authority": "Multiple",
        "section_ref": "Quick Reference Guide",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Quick Reference — Compensation amounts: DEATH → Rs. 8,00,000 (Second Schedule) + Rs. 10,00,000 (Insurance) + Rs. 5,00,000 (Ex-gratia) = Total minimum Rs. 23,00,000. GRIEVOUS HURT → Rs. 7,50,000 (Second Schedule) + Rs. 7,50,000 (Insurance) + Rs. 1,00,000 (Ex-gratia). SIMPLE HURT → Rs. 1,00,000 (Second Schedule) + Rs. 2,00,000 (Insurance) + Rs. 50,000 (Ex-gratia). Note: RCT can award HIGHER amounts based on individual circumstances (income, age, severity).",
        "doc_type": "compensation_schedule",
        "incident_type": "accident",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Second Schedule + Insurance + Ex-Gratia Combined",
        "compensation_eligible": True,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # ADDITIONAL FILING PROCEDURES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Step-by-step process after a railway accident (for the victim or family): 1) Seek immediate medical attention — go to nearest Railway Hospital or government hospital (free for railway accident victims). 2) File FIR at GRP station — get a certified copy. 3) Preserve the railway ticket/pass. 4) Collect medical records (injury certificate, X-rays, discharge summary). 5) Photograph injuries and accident scene. 6) Get witness statements with contact details. 7) Apply for interim relief at DRM office. 8) File compensation claim at RCT within 3 years. 9) File on CPGRAMS for systemic issues. 10) Consider additional claim at Consumer Forum for deficiency in service.",
        "doc_type": "filing_procedure",
        "incident_type": "accident",
        "legal_remedy": "guidance",
        "authority": "Multiple",
        "section_ref": "Post-Accident Procedure Guide",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "How to file a complaint on Rail Madad app (step-by-step): 1) Download Rail Madad app from Play Store/App Store. 2) Register with mobile number. 3) Select complaint category (Cleanliness, Staff Behavior, Safety, Facilities, etc.). 4) Select sub-category. 5) Enter train number or PNR number or station name. 6) Write description of complaint (supports English, Hindi). 7) Attach photos/videos (up to 5 MB). 8) Submit — you get an immediate Reference Number. 9) Track status using the Reference Number. 10) Rate resolution when complaint is closed. Average resolution time: 3-7 days for operational issues.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "grievance",
        "authority": "Rail Madad",
        "section_ref": "Rail Madad User Guide",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # SPECIFIC SECTIONS FOR COMMON MUMBAI SUBURBAN INCIDENTS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Injuries while boarding/alighting running train: A significant number of Mumbai suburban railway accidents occur while passengers attempt to board or alight from moving trains. Legal position: If the train was moving at normal speed and the passenger attempted to board/alight — contributory negligence may reduce compensation but NOT eliminate it entirely (Union of India v. Prabhudayal, SC 2004). If the train started moving while passenger was boarding/alighting — full compensation under Section 123. Document: Which platform, CCTV footage (via RTI), witness statements.",
        "doc_type": "case_law",
        "incident_type": "boarding_alighting",
        "legal_remedy": "compensation",
        "authority": "Railway Claims Tribunal",
        "section_ref": "Railways Act Section 123 + SC Precedent",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },
    {
        "text": "Bag snatching while hanging from train door: Many Mumbai suburban commuters travel by hanging from train doors during peak hours. If a bag is snatched in this situation: 1) Criminal offence — FIR at GRP under IPC 356 (assault in attempt to commit theft) + 379 (theft). 2) If the snatching causes the person to fall — additional FIR under IPC 307 (attempt to murder) or 304 (culpable homicide). 3) Compensation claim at RCT — the act of snatching causing fall is an 'untoward incident' under Section 124A. 4) The railway cannot escape liability by arguing the victim was hanging from the door — overcrowding is a known systemic issue.",
        "doc_type": "legal_statute",
        "incident_type": "robbery",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "IPC 356/379/307/304 + Railways Act 124A",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },

    # ═══════════════════════════════════════════════════════════════
    # NOISE AND ENVIRONMENTAL COMPLAINTS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Noise pollution from trains and railway operations: Residents living near railway tracks who are affected by excessive noise from train operations (horn honking, rail grinding) can: 1) File complaint at Noise Pollution (Regulation and Control) Rules 2000 under Environment Protection Act. 2) Approach local Municipal Corporation. 3) File on CPGRAMS under 'Infrastructure' citing noise levels exceeding permissible limits. 4) File PIL in High Court for systemic noise pollution. The railways are required to use silent zones near hospitals and schools and use restricted horn usage between 10 PM and 6 AM.",
        "doc_type": "legal_statute",
        "incident_type": "noise_pollution",
        "legal_remedy": "grievance",
        "authority": "CPGRAMS / Municipal Corporation",
        "section_ref": "Environment Protection Act 1986 + Noise Pollution Rules",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # ADDITIONAL RTI TEMPLATES
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "RTI for seeking information about safety audits: Sample RTI text: 'Please provide: 1) Date of last safety audit conducted at [Station Name]. 2) Findings of the safety audit including identified hazards. 3) Recommendations made by the safety auditors. 4) Status of implementation of each recommendation. 5) Budget allocated and spent on safety improvements at this station in the last 3 financial years.' Address to: CPIO of the respective railway zone. This RTI is valuable for building evidence for safety-related complaints or PILs.",
        "doc_type": "rti_template",
        "incident_type": "general",
        "legal_remedy": "rti",
        "authority": "CPIO Railway",
        "section_ref": "RTI Act 2005",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "RTI for seeking information about RPF/GRP deployment: Sample RTI text: 'Please provide: 1) Number of RPF personnel deployed at [Station Name] during peak hours (7 AM - 11 AM, 5 PM - 9 PM). 2) Number of GRP personnel at the same station. 3) Number of complaints received at this station in the last 12 months categorized by type. 4) Number of FIRs registered and their current status. 5) Whether any RPF/GRP officer at this station has been disciplined in the last 2 years.' Useful for: Building case for inadequate security deployment.",
        "doc_type": "rti_template",
        "incident_type": "general",
        "legal_remedy": "rti",
        "authority": "CPIO Railway",
        "section_ref": "RTI Act 2005",
        "compensation_eligible": False,
        "location_scope": "national",
    },

    # ═══════════════════════════════════════════════════════════════
    # FINAL: COMPREHENSIVE PROCESS MAPS
    # ═══════════════════════════════════════════════════════════════
    {
        "text": "Complete process for physical assault on train: 1) Ensure personal safety first — move to another coach if possible. 2) Pull emergency chain if the assault is ongoing. 3) Call 182 (RPF) for immediate response. 4) Get down at next station and report to GRP. 5) File FIR under IPC 323 (voluntarily causing hurt) or 325 (grievous hurt) or 326 (dangerous weapons). 6) Get medical examination done ASAP — MLC (Medico-Legal Case) at government hospital. 7) Collect witness statements. 8) If injured, claim compensation at RCT under Section 124A. 9) File on CPGRAMS for security improvement. 10) If GRP is unresponsive, approach SDSC (Senior Divisional Security Commissioner).",
        "doc_type": "filing_procedure",
        "incident_type": "assault",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "IPC 323/325/326 + Railways Act 124A",
        "compensation_eligible": True,
        "location_scope": "national",
    },
    {
        "text": "Complete process for reporting and claiming theft on train: 1) Note exact details: train number, coach number, seat/standing position, time, direction of travel. 2) Check with co-passengers if anyone witnessed the theft. 3) Get down at next major station with GRP post. 4) File FIR at GRP under IPC 379 (theft) or 392 (robbery if force was used). 5) Provide description of stolen items with estimated value. 6) For mobile phones: provide IMEI number (dial *#06# on any phone to find it — note it down now as prevention). 7) Request GRP to check CCTV footage. 8) File on Rail Madad for follow-up. 9) For insurance claim: get copy of FIR.",
        "doc_type": "filing_procedure",
        "incident_type": "theft",
        "legal_remedy": "fir",
        "authority": "GRP",
        "section_ref": "IPC 379/392 + CrPC 154",
        "compensation_eligible": False,
        "location_scope": "national",
    },
    {
        "text": "Complete process for Mumbai suburban daily pass holder filing complaint: Monthly/quarterly pass holders on Mumbai suburban railways have the same rights as single-ticket holders. For pass holders: 1) Your pass is proof of being a bona fide passenger — retain it. 2) Any accident compensation applies fully. 3) For chronic service issues (delays, overcrowding, cancellations), pass holders can collectively file Consumer Forum complaint for deficiency in service — the pass price is the consideration paid. 4) Group complaint on CPGRAMS carries more weight — coordinate with fellow regular commuters.",
        "doc_type": "filing_procedure",
        "incident_type": "general",
        "legal_remedy": "consumer_complaint",
        "authority": "Consumer Forum",
        "section_ref": "Consumer Protection Act + Railways Act",
        "compensation_eligible": True,
        "location_scope": "mumbai",
    },
]

# Total chunks count
CORPUS_SIZE = len(LEGAL_CHUNKS)
