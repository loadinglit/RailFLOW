# RailFLOW — Complete UI Testing Instructions

> Test every feature through the browser UI.
> Start backend (`uvicorn app.main:app --reload`) and frontend (`npm run dev`).

---

## TEST 1: Authentication

### 1a. Signup — Passenger (English)
1. Open `/login` → Click **Sign Up**
2. Fill:
   - Name: `Raj Kumar`
   - Email: `raj@test.com`
   - Password: `Test@1234`
   - Role: **Passenger**
   - Phone: `9876543210`
   - Address: `Andheri West, Mumbai 400053`
3. Submit → Should redirect to Passenger Home

### 1b. Signup — Passenger (Hindi)
1. Logout → Sign Up again
2. Fill:
   - Name: `Priya Sharma`
   - Email: `priya@test.com`
   - Password: `Test@1234`
   - Role: **Passenger**
   - Language: **Hindi**
   - Phone: `9123456789`
   - Address: `Dadar East, Mumbai`
3. Submit → Should land on Passenger Home

### 1c. Signup — Passenger (Marathi)
1. Logout → Sign Up
2. Fill:
   - Name: `Amit Patil`
   - Email: `amit@test.com`
   - Password: `Test@1234`
   - Role: **Passenger**
   - Language: **Marathi**
   - Phone: `9988776655`
   - Address: `Borivali West, Mumbai`

### 1d. Signup — Police Officer
1. Logout → Sign Up
2. Fill:
   - Name: `Inspector Deshmukh`
   - Email: `deshmukh@police.gov`
   - Password: `Test@1234`
   - Role: **Police**
3. Submit → Should redirect to Police Dashboard

### 1e. Login — Wrong password
1. Logout → Login with `raj@test.com` / `wrongpass`
2. Should show "Invalid email or password" error

### 1f. Login — Correct password
1. Login with `raj@test.com` / `Test@1234`
2. Should redirect to Passenger Home, name shown in header

### What to verify:
- [ ] Passenger lands on PassengerHome, police lands on PoliceDashboard
- [ ] Logout button works, redirects to login
- [ ] Duplicate email signup shows error
- [ ] Name appears in header after login

---

## TEST 2: Train Search + Crowd Intelligence

### 2a. Basic search
1. Login as `raj@test.com`
2. On **Trains** tab:
   - From: `Borivali` (type "Bor" — autocomplete should appear)
   - To: `Churchgate` (type "Chu" — autocomplete)
   - When: Pick current date/time
3. Hit **Search**

### 2b. Verify results
- Each train card should show:
  - Train name + number
  - Departure time + platform
  - Line badge (WR/CR/HR)
  - Crowd badge: GREEN (Safe) / YELLOW (Caution) / RED (Avoid)
  - One-line reason explaining the badge
- First train should have "RECOMMENDED" tag
- Bottom info box explains how badges work

### 2c. Train detail view
1. Tap any train card
2. Should show a bottom sheet with:
   - "Are you boarding this train right now?" prompt
   - Two buttons: "Yes, I'm boarding" / "Just planning"

### 2d. Crowd report flow
1. Tap "Yes, I'm boarding"
2. Three options appear: Very crowded (RED) / Moderate (YELLOW) / Comfortable (GREEN)
3. Tap **Very crowded**
4. Should show "Reported!" confirmation with commuter help count
5. If 2+ people report RED, badge may update to RED

### 2e. Swap stations
1. Click the swap arrow button (↕) between From/To
2. Stations should swap
3. Search again — results should be for the reverse route

### 2f. Time verification
1. Set time to `2:30 PM` in the datetime picker
2. Search → trains should show departures around 2:30 PM, NOT 8 PM or random times

### What to verify:
- [ ] Station autocomplete works (shows dropdown after 2 chars)
- [ ] Search returns trains with color-coded badges
- [ ] Tapping train opens crowd report sheet
- [ ] Crowd report submits and shows confirmation
- [ ] Swap button swaps origin/destination
- [ ] Time in results matches what you selected

---

## TEST 3: Jan Suraksha Bot — Filing Complaints

> Switch to **Suraksha** tab at bottom of Passenger Home.

### 3a. Theft complaint — English (all details in one message)
1. Login as `raj@test.com`, go to Suraksha tab
2. Language: **EN**
3. Type this exact message:

```
My phone and wallet were stolen while boarding the 8:15 AM Virar fast local at Andheri station today. The thief was a man in a black jacket who pushed me and grabbed my pocket.
```

4. Bot should classify as **theft**, extract entities (time: 8:15 AM, station: Andheri, items: phone + wallet, suspect: man in black jacket)
5. Bot shows action options — tap **"1. Get complaint letter ready"** (or similar)
6. Bot generates a **GRP FIR** complaint draft with all fields filled:
   - Your name, phone, address from signup
   - Incident time: 8:15 AM
   - From Station: Andheri
   - Items lost: phone, wallet
   - Suspect: man in black jacket
7. **"View Complaint Draft"** expandable section shows the full FIR
8. **"Download Complaint PDF"** button opens printable PDF in new tab

### 3b. Theft complaint — Hindi (missing time, bot should ask ONCE)
1. Logout → Login as `priya@test.com`
2. Suraksha tab, Language: **HI**
3. Type:

```
Borivali station pe mera laptop bag chori ho gaya, train se utarte waqt kisi ne chheen liya
```

4. Bot should ask ONE question about when it happened (time missing)
5. Reply:

```
Subah 9 baje hua tha
```

6. Bot should now show action options
7. Pick **file complaint** → should generate Hindi FIR with Borivali station

### 3c. Assault complaint — Marathi (missing station, bot asks ONCE)
1. Logout → Login as `amit@test.com`
2. Suraksha tab, Language: **MR**
3. Type:

```
Aaj sakali 7:30 la train madhe koni tari mala dhakka dila ani maza mobile padla track var, haatala khup laagla
```

4. Bot should ask ONE question about where it happened (station missing)
5. Reply:

```
Dadar station la zala he
```

6. Bot shows options → file complaint → generates Marathi FIR

### 3d. Second theft at Andheri (builds pattern for safety alerts)
1. Login as `raj@test.com` again
2. Suraksha tab, Language: **EN**
3. Type:

```
Someone pickpocketed my earbuds from my bag at Andheri station around 2:30 PM today while waiting for the Churchgate slow local
```

4. Bot classifies, shows options → file complaint
5. This builds a pattern: 2 thefts at Andheri from same user

### 3e. CPGRAMS complaint — Overcrowding
1. Still as Raj, new conversation (refresh page if needed)
2. Type:

```
The 8:05 AM Virar fast from Borivali is dangerously overcrowded every single day. People are hanging from doors. Someone will die. I want to file a government complaint.
```

3. Bot should classify as **overcrowding** and route to CPGRAMS
4. Pick **file CPGRAMS** option
5. Should generate a **CPGRAMS Grievance Form** (different from FIR)
6. Should show: CPGRAMS ref number, follow-up date (30 days), pgportal.gov.in link

### 3f. Compensation query — Accident
1. Refresh, type:

```
My father fell from the train between Dadar and Matunga last week and broke his leg. He was in the general compartment. Can we get compensation?
```

2. Bot should classify as **falling** (accident), detect compensation eligibility
3. Should show: RCT (Railway Claims Tribunal) info, compensation amounts
4. Pick **compensation info** → generates RCT Form II with compensation schedule

### 3g. Status check
1. Type:

```
What is the status of my complaint?
```

2. Bot should detect **check_status** action
3. Shows status of previously filed complaints (filed/acknowledged/resolved)

### 3h. Know your rights
1. Type:

```
What are my legal rights if someone steals my belongings on a Mumbai local train?
```

2. Bot should explain: Right to file FIR, relevant IPC sections, compensation rights, authorities to contact

### 3i. Know authority
1. Type:

```
Who should I contact for reporting a theft on Western Railway?
```

2. Bot should give: GRP station details, helpline numbers (022-22694727), RPF number (182), Rail Madad (139)

### 3j. Quick prompts
1. On empty bot screen, 5 quick prompt buttons should be visible
2. Tap any one (e.g., "Someone stole my phone on the train")
3. Should start a conversation as if you typed it

### What to verify:
- [ ] Bot classifies incident type correctly (theft/assault/overcrowding/accident)
- [ ] Bot asks at most 1 follow-up question for missing required info
- [ ] Bot does NOT ask endless irrelevant questions (no "which direction did they run", no "any witnesses")
- [ ] FIR template fills name/phone/address from user signup profile
- [ ] FIR template fills incident details from the conversation (time, station, items)
- [ ] CPGRAMS form is different from FIR format
- [ ] RCT Form II shows compensation amounts
- [ ] Hindi and Marathi responses are actually in those languages
- [ ] Complaint draft is viewable and downloadable as PDF
- [ ] Authority info shows real helpline numbers
- [ ] Status check shows previously filed complaint statuses
- [ ] Complaint ref number appears (format: RM-YYYYMMDD-XXXXXX)

---

## TEST 4: Safety Intelligence — Passenger Alerts

> This requires complaints to exist (from Test 3). Run Test 3 first.

### 4a. Safety alert on search
1. Login as any passenger
2. Go to **Trains** tab
3. Search any route (e.g., Borivali → Churchgate)
4. Above the train results, a **Safety Alert** card should appear:
   - Shield icon + "Safety Alert" header
   - AI advisory text mentioning specific crime type, count, and peak time
   - Stats line: "X thefts · Y assaults · Peak: 2 PM - 4 PM"
5. Card border color:
   - **Amber** if < 5 incidents in last 24h
   - **Red** if >= 5 incidents

### 4b. Verify advisory quality
- Advisory should mention real station names from complaints (Andheri, Borivali, Dadar — NOT random stations)
- Should mention specific crime type and count
- Should mention peak time window in AM/PM format
- Should give one concrete action (e.g., "keep phone in inner pocket")
- Should NOT say generic "stay safe"

### 4c. Language-aware advisory
1. If user's language is Hindi → advisory should be in Hindi
2. If Marathi → advisory in Marathi

### What to verify:
- [ ] Safety alert card appears above train results after search
- [ ] Advisory mentions real data (crime type, count, time, stations)
- [ ] Stats line shows breakdown with peak window
- [ ] Color changes based on incident count threshold
- [ ] Advisory language matches user's language preference

---

## TEST 5: Police Dashboard — Ticket Management

### 5a. Login as police
1. Login with `deshmukh@police.gov` / `Test@1234`
2. Should land on Police Dashboard

### 5b. Verify header stats
- 4 stat boxes: Filed (red) / Active (amber) / Solved (green) / Closed (gray)
- Numbers should match actual complaint counts from Test 3

### 5c. View complaint tickets
- Each ticket card shows:
  - Incident type icon + label (THEFT, ASSAULT, etc.)
  - Status badge (FILED/ACKNOWLEDGED/RESOLVED/REJECTED)
  - Severity badge (LOW/MEDIUM/HIGH/CRITICAL)
  - User name + authority
  - Ref number + date
  - User's original message in quotes
  - Expandable "View Complaint Draft" with full FIR/CPGRAMS text
  - "Download FIR / Complaint PDF" button

### 5d. Filter by status
1. Tap **Filed** filter chip → only filed complaints shown
2. Tap **All** → all complaints shown
3. Tap **Resolved** → only resolved (may be empty)

### 5e. Filter by type
1. Use the type dropdown → select "theft"
2. Only theft complaints shown
3. Select "All incident types" to reset

### 5f. Acknowledge a complaint
1. Find a **Filed** complaint
2. Tap **Acknowledge** button
3. Status should change to ACKNOWLEDGED (amber badge)
4. Filed count decreases, Active count increases in header

### 5g. Resolve a complaint
1. Find an acknowledged complaint
2. Tap **Resolve**
3. Modal appears — type a resolution note:

```
Phone recovered from suspect near Andheri station. FIR registered.
```

4. Submit → status changes to RESOLVED (green badge)
5. Officer note appears on the ticket

### 5h. Reject a complaint
1. Find a filed complaint
2. Tap **Reject**
3. Modal appears — note is REQUIRED for rejection
4. Type:

```
Insufficient evidence. No CCTV footage available.
```

5. Submit → status changes to REJECTED (gray badge)

### 5i. Download complaint PDF
1. On any ticket, expand "View Complaint Draft"
2. Click **"Download FIR / Complaint PDF"**
3. New window opens with formatted document
4. Print/Save as PDF button should work

### What to verify:
- [ ] All complaints from Test 3 appear as tickets
- [ ] Status/type filters work
- [ ] Acknowledge/Resolve/Reject flow works
- [ ] Resolution note is optional, rejection note is required
- [ ] Officer note appears on ticket after action
- [ ] Header stat counts update after status changes
- [ ] PDF download opens properly formatted document
- [ ] Refresh button reloads complaint list

---

## TEST 6: Police Analytics Dashboard

### 6a. Switch to Analytics tab
1. On Police Dashboard, tap **Analytics** tab (next to Tickets)
2. Analytics view loads with charts

### 6b. Verify stat cards (top row)
- **Total**: Total number of complaints in DB
- **Trend**: +N or -N (this week vs last week), red if up, green if down
- **Top crime**: Icon + label of most frequent incident type

### 6c. Complaints by Type chart
- Horizontal bar chart
- Each bar: incident icon + type name + bar + count
- Longest bar = most complaints (100% width)
- Should show: theft, assault, overcrowding, falling (from Test 3)

### 6d. Severity Breakdown chart
- Horizontal bars, color-coded:
  - Red = Critical
  - Orange = High
  - Amber = Medium
  - Blue = Low

### 6e. Station Hotspots chart
- Shows stations where incidents were reported
- Horizontal rose-colored bars with station name + count
- Should show: Andheri (2), Borivali (1), Dadar (1) from Test 3
- Only appears if complaints have station data

### 6f. Hourly Pattern chart
- Vertical mini bars for each hour of the day (0-23)
- X-axis labels in AM/PM: 12a, 4a, 8a, 12p, 4p, 8p
- Bars only appear for hours with complaints
- Count number shown above each active bar

### 6g. AI Patrol Recommendation
- Blue card at bottom with robot icon
- 2-3 sentence recommendation
- Should mention:
  - Real station names from data (Andheri, Borivali) — NOT hallucinated names
  - Peak time window in AM/PM format
  - What officers should look for based on top crime type
- Should NOT mention stations like CST, Dadar if those aren't in the data

### 6h. Refresh button
- Click "Refresh Analytics" at bottom
- Should reload all data

### What to verify:
- [ ] All 5 chart sections render (type, severity, station, hourly, patrol rec)
- [ ] Numbers match actual complaint data
- [ ] Station hotspots show only stations from actual complaints
- [ ] Hourly chart uses AM/PM labels (not 24h format)
- [ ] AI patrol recommendation references real stations only
- [ ] Trend arrow is correct (up/down/stable)
- [ ] Toggle between Tickets and Analytics works smoothly

---

## TEST 7: Full Feedback Loop (Demo Flow)

> This is the critical end-to-end test showing the system works as a whole.

### Step 1: File complaints (as passengers)
1. Login as `raj@test.com` → Suraksha tab → file theft at Andheri (Test 3a)
2. Login as `priya@test.com` → file theft at Borivali (Test 3b)
3. Login as `amit@test.com` → file assault at Dadar (Test 3c)
4. Login as `raj@test.com` → file another theft at Andheri (Test 3d)

### Step 2: Passenger sees safety alert
1. Login as any passenger
2. Go to Trains tab → search any route
3. **Safety Alert card** should appear showing:
   - "3 theft reports, 1 assault in the last 24 hours"
   - Peak window (e.g., "7 AM - 9 AM")
   - Actionable tip mentioning Andheri station

### Step 3: Police sees analytics
1. Login as `deshmukh@police.gov`
2. Go to **Analytics** tab
3. Should see:
   - Total: 4 complaints
   - Top crime: Theft
   - Station Hotspots: Andheri (2), Borivali (1), Dadar (1)
   - AI recommends patrolling Andheri during peak hours

### Step 4: Police takes action
1. Switch to **Tickets** tab
2. Acknowledge all 4 complaints
3. Resolve the Andheri theft — add note: "Suspect apprehended"

### Step 5: Verify loop closes
1. Login as `raj@test.com`
2. Go to Suraksha tab → ask "What is the status of my complaint?"
3. Bot should say complaint is resolved/acknowledged
4. Safety alert on train search should still show pattern (data persists)

### What to verify:
- [ ] Complaints flow from bot → DB → safety alerts → analytics
- [ ] Passenger sees alerts based on recent complaints
- [ ] Police sees real station names in analytics
- [ ] Police actions (acknowledge/resolve) reflect in status checks
- [ ] No hallucinated data anywhere in the pipeline

---

## TEST 8: Edge Cases

### 8a. Empty bot message
- Send empty message to bot → should handle gracefully (no crash)

### 8b. Same origin and destination
- Search Andheri → Andheri → should show error "Origin and destination cannot be the same"

### 8c. No complaints scenario
- If DB is fresh with zero complaints:
  - Safety alert should NOT appear on search
  - Analytics should show "No complaint data yet"
  - Patrol recommendation: "Analytics will appear as complaints are filed"

### 8d. Bot language switching
- Start conversation in English
- Switch language toggle to Hindi mid-conversation
- Next response should be in Hindi

### 8e. Multiple complaint types
- File complaints of different types (theft, overcrowding, accident)
- Analytics should show all types in the bar chart
- Patrol recommendation should reference the most common type

---

## Test Accounts Summary

| Role | Name | Email | Password |
|------|------|-------|----------|
| Passenger (EN) | Raj Kumar | raj@test.com | Test@1234 |
| Passenger (HI) | Priya Sharma | priya@test.com | Test@1234 |
| Passenger (MR) | Amit Patil | amit@test.com | Test@1234 |
| Police | Inspector Deshmukh | deshmukh@police.gov | Test@1234 |

---

## Complaint Types Tested

| Query | Type | Authority | Template |
|-------|------|-----------|----------|
| Phone stolen at Andheri | theft | GRP | FIR |
| Laptop bag snatched at Borivali | theft | GRP | FIR (Hindi) |
| Pushed on train, mobile fell on track | assault | GRP | FIR (Marathi) |
| Pickpocketed earbuds at Andheri | theft | GRP | FIR |
| Overcrowding on Virar fast | overcrowding | CPGRAMS | CPGRAMS Form |
| Father fell from train, broke leg | falling | RCT | RCT Form II |