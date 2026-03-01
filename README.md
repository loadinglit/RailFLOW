# RailFLOW

**AI-Powered Crowd Intelligence & Safety Platform for Mumbai Suburban Railways**

Built for the mIndicator AI Hackathon 2026 (VJTI) | Team: Bhoomi + Dhruv

---

## What is RailFLOW?

RailFLOW is a three-pillar safety intelligence system for Mumbai's 75 lakh daily suburban commuters:

1. **Crowd Intelligence** — AI-powered GREEN/YELLOW/RED badges per train using Random Forest on historical patterns, user feedback trends, and live weather
2. **Jan Suraksha Bot** — Multilingual (EN/HI/MR) AI complaint assistant that classifies railway crimes, extracts entities, retrieves legal context, and auto-generates real GRP FIR / CPGRAMS / RCT government forms
3. **Safety Intelligence Dashboard** — Police-facing analytics with station hotspots, hourly crime patterns, and AI-generated patrol recommendations

---

## Architecture

![Jan Suraksha Agent Architecture](screenshots/agent-design.png)

**Three-layer system:**

| Layer | Components | Purpose |
|-------|-----------|---------|
| **User Input** | React + Capacitor → FastAPI → LangGraph | Message ingestion, auth, state machine entry |
| **Agent Layer** | Manager → Classify / Execute / Respond (cyclic) | Crime classification, template filing, response generation |
| **Data Layer** | SQLite + Neo4j + Zilliz + Rule-based maps | Users, trains, legal embeddings, authority routing |

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI 0.115 + Uvicorn | Async API server |
| LLM | OpenAI GPT-4o-mini (via LiteLLM) | Classification, response generation, FIR summaries |
| Agent Framework | LangGraph v0.2 | Cyclic state machine with MemorySaver |
| Graph Database | Neo4j AuraDB | 1,153 trains, 38 stations, 10K+ crowd reports |
| Vector Store | Zilliz Cloud (Milvus) | 108 legal chunks (IPC, Railways Act, RCT) with 1536-dim embeddings |
| Relational DB | SQLite (WAL mode) | Users, complaints, auth — zero cloud dependency |
| Frontend | React 19 + Vite 7 + Tailwind CSS 4 | Mobile-first responsive UI |
| Mobile | Capacitor 8 | Native Android APK |
| Weather | OpenWeatherMap API | Live Mumbai weather for crowd multiplier |
| Notifications | Gmail SMTP + Twilio | Email/SMS on complaint status changes |
| PDF Export | jsPDF (client-side) | Complaint PDF generation |

---

## Screenshots

### Train Search with Crowd Intelligence

![Train Search](screenshots/train-search.png)

Passenger searches for trains from Churchgate → Virar. The system shows:
- **Safety Alert card** — AI-generated advisory based on last 24 hours of filed complaints ("9 theft reports... especially around Andheri during 9 AM to 11 AM")
- **Incident stats** — breakdown of theft, assault, robbery, overcrowding, harassment reports with peak time window
- **Recommended train** — the first GREEN badge train (Virar SF 18:36, Safe) is highlighted as RECOMMENDED
- **Route info** — "Sunday · 10 Trains Found · 1889 Crowd Reports" showing data density

### Train Results with Crowd Badges

![Train Results](screenshots/train-results.png)

Each train card displays:
- **Line badge** (WR/CR/HR) and train type (FAST/SLOW/SEMI FAST)
- **Crowd report count** — "8 reports", "68 reports" showing confidence level
- **Departure time, duration, platform number**
- **Crowd badge** — Safe (green) / Caution (yellow) / Avoid (red)
- **AI-generated reason** — natural language explanation matching badge tone ("Avoid the Churchgate SF during peak hou...")
- **Info footer** — "Crowd scores combine crowd trend patterns, weather, and historical reports from commuters like you"

### Jan Suraksha Bot — Incident Report

![Jan Suraksha Chat](screenshots/bot-chat.png)

User reports a robbery in English. The bot:
- Detects incident: **robbery** with auto-extracted entities (8:15 AM, Virar fast local, Andheri station, phone + wallet, man in black jacket)
- Presents **3 action options**: Get complaint letter ready, Who to contact, Know your rights
- Shows **Authority pill**: Government Railway Police (GRP)
- Supports **language toggle** (EN/HI/MR) at the top

### Jan Suraksha Bot — Complaint Filed

![Complaint Filed](screenshots/bot-complaint-filed.png)

After user picks "Get complaint letter ready":
- Shows **summary**: Railway police number (022-22694727), tracking ref (RM-20260301-B6F6BC), follow-up date (31/03/2026)
- **Authority pill**: Government Railway Police (GRP)
- **Compensation pill**: "Eligible for compensation under Railways Act"
- **CPGRAMS ref**: Links to government grievance portal (pgportal.gov.in)
- **Expandable complaint draft** with real FIR template

### Jan Suraksha Bot — GRP FIR Template

![FIR Template](screenshots/bot-fir-template.png)

The actual **FORM - IF1 (Integrated Form)** under Section 154 Cr.P.C. / Section 173 BNSS:
- Pre-filled with: District (Mumbai), P.S. (GRP Andheri), Year (2026), Date (01/03/2026)
- **Slot-filled, not LLM-generated** — zero hallucination on legal documents
- **Download Complaint PDF** button for offline submission
- This is the actual format used by Government Railway Police stations

### Police Dashboard — Tickets

![Police Dashboard](screenshots/police-tickets.png)

Police officer view showing:
- **4 status counters**: 10 Filed, 1 Active, 4 Solved, 3 Closed
- **Status filter chips**: All / Filed / Acknowledged / Resolved / Rejected
- **Incident type dropdown** for filtering
- **Complaint cards** with:
  - Incident icon + severity badge (MEDIUM/CRITICAL)
  - Tracking ref (RM-20260301-08ECDA) and date
  - Complainant name + assigned authority
  - Full complaint text
  - "View Complaint Draft" expandable section
  - **Download FIR / Complaint PDF** button
  - **Action buttons**: Acknowledge (yellow), Resolve (green), Reject (red)
- Rejection requires mandatory officer note (validation enforced)

### Police Dashboard — Analytics

![Police Analytics](screenshots/police-analytics.png)

AI-powered analytics computed from all filed complaints:
- **Top stats**: 20 Total, +20 This Week (trend), Top Crime: Theft
- **Complaints by Type**: Horizontal bar chart — theft (9), robbery (4), assault (3), overcrowding (2), sexual harassment (1), falling (1)
- **Severity Breakdown**: Critical (1), High (9), Medium (10) with color-coded bars
- **Station Hotspots**: Andheri (10), Nallasopara (1) — data-driven, only real station names
- **Hourly Pattern**: Time distribution of incidents
- **AI Patrol Recommendation**: LLM-generated tactical deployment advice using only data-backed station names and peak windows

### Email Notification

![Email Notification](screenshots/email-notification.png)

When police acknowledges a complaint:
- Passenger receives email: "Complaint RM-20260301-67FE25 — Received & Under Investigation"
- Body: "Your complaint has been received by the railway police. An officer is now working on your case."
- Sent via Gmail SMTP (configurable)

### Neo4j Graph Database

![Neo4j Graph](screenshots/neo4j-graph.png)

Neo4j AuraDB browser showing the full graph:
- **11,207 nodes**: Complaint, CrowdReport, CrowdSignal, DetectionEvent, DisruptionEvent, Route, Station, Train, User
- **12,353 relationships**: ARRIVES_AT, DEPARTS_FROM, REPORTS_ON
- **64+ property keys**: annual_deaths, capacity, crowd_level, danger_level, departure_time, etc.
- Visual: Station nodes (yellow hubs) connected to Train nodes (pink) via ARRIVES_AT / DEPARTS_FROM — showing the full Mumbai suburban rail network as a graph

---

## Project Structure

```
RailFLOW/
├── backend/
│   ├── app/
│   │   ├── main.py                          # FastAPI app init, CORS, lifespan
│   │   ├── db.py                            # SQLite schema (users, complaints)
│   │   ├── core.py                          # Neo4j, OpenAI, Milvus client init
│   │   ├── auth.py                          # HMAC-SHA256 token auth, password hashing
│   │   ├── routers/
│   │   │   ├── auth.py                      # POST /signup, /login, GET /me
│   │   │   ├── trains.py                    # POST /trains/search, /trains/report
│   │   │   ├── bot.py                       # POST /bot/chat — Jan Suraksha endpoint
│   │   │   ├── complaints.py                # GET/PATCH complaints (police)
│   │   │   └── safety.py                    # GET /safety/alerts, /safety/analytics
│   │   ├── engines/
│   │   │   ├── crowd_engine.py              # 3-signal crowd badge computation
│   │   │   ├── safety_engine.py             # Complaint-driven alerts + analytics
│   │   │   └── jansuraksha/
│   │   │       ├── agent.py                 # LangGraph cyclic agent (manager pattern)
│   │   │       ├── prompts.py               # SMART_CLASSIFY + RESPONSE_GENERATION
│   │   │       ├── mappings.py              # AUTHORITY_MAP, ACTION_MAP, INCIDENT_TYPES
│   │   │       ├── templates.py             # GRP FIR, CPGRAMS, RCT, Rail Madad
│   │   │       ├── tools.py                 # Tool wrappers
│   │   │       ├── retrieval.py             # Legal RAG via Zilliz vector search
│   │   │       └── neo4j_context.py         # User/complaint SQLite layer
│   │   ├── models/
│   │   │   └── schemas.py                   # Pydantic models
│   │   ├── services/
│   │   │   └── notifications.py             # Email (SMTP) + SMS (Twilio) alerts
│   │   └── utils/
│   │       └── logger.py
│   ├── data/
│   │   ├── railflow.db                      # SQLite database
│   │   ├── llm_timetable_raw.json           # 1,153 trains (scraped + LLM-validated)
│   │   ├── mumbai_timetable.py              # Station lists, route maps, cumulative mins
│   │   ├── legal_corpus.py                  # 108 legal chunks for RAG
│   │   └── scraped_timetable.json           # Raw scrape from erail.in
│   └── scripts/
│       ├── seed_neo4j.py                    # Create train graph in Neo4j
│       ├── seed_crowd_data.py               # Generate 10K synthetic crowd reports
│       ├── setup_neo4j_schema.py            # Neo4j indexes + constraints
│       ├── ingest_legal.py                  # Embed + upsert legal corpus to Zilliz
│       ├── scrape_trainhelp.py              # Scrape timetables from trainhelp.in
│       └── fetch_timetable_llm.py           # LLM-enhanced timetable correction
├── frontend/
│   ├── src/
│   │   ├── main.jsx                         # React entry point
│   │   ├── App.jsx                          # Router + auth context
│   │   └── pages/
│   │       ├── PassengerHome.jsx            # Train search + Jan Suraksha bot
│   │       ├── PoliceDashboard.jsx          # Tickets + Analytics tabs
│   │       ├── Login.jsx                    # Auth (shared login/signup)
│   │       └── Signup.jsx
│   ├── capacitor.config.json                # Capacitor mobile config
│   └── package.json
├── dev/
│   ├── README.md                            # ← You are here
│   └── screenshots/                         # App screenshots
├── how-it-works.html                        # Technical explainer page
├── jansuraksha-flowchart.html               # Agent architecture diagram
└── .env.example                             # Environment variables template
```

---

## External APIs & Services

### 1. OpenAI API (GPT-4o-mini)
- **Purpose**: Incident classification, response generation, FIR summaries, crowd badge reasons, safety advisories, patrol recommendations
- **Auth**: `OPENAI_API_KEY` (optional `OPENAI_BASE_URL` for LiteLLM proxy)
- **Model**: `gpt-4o-mini` (aliased as MODEL_FAST)
- **Files that call this API**:
  - `backend/app/core.py:84-95` — `embed_text()` for legal corpus embeddings
  - `backend/app/engines/crowd_engine.py:349-378` — `generate_reason()` for crowd badge explanations
  - `backend/app/engines/safety_engine.py:161-168` — `_generate_advisory()` for passenger safety alerts
  - `backend/app/engines/jansuraksha/agent.py:368-378` — `classify_node()` for crime classification
  - `backend/app/engines/jansuraksha/agent.py:495-511` — `_respond_main()` for response generation
  - `backend/app/engines/jansuraksha/agent.py:562-566` — `_respond_follow_up()` for conversation follow-up
  - `backend/app/engines/jansuraksha/agent.py:624-630` — `_generate_fir_context()` for formal FIR summary

### 2. OpenWeatherMap API
- **Purpose**: Live Mumbai weather data as crowd multiplier signal (rain → more crowding)
- **Auth**: `OPENWEATHERMAP_KEY`
- **Endpoint**: `https://api.openweathermap.org/data/2.5/weather?q=Mumbai&appid={key}&units=metric`
- **File**: `backend/app/engines/crowd_engine.py:210-244` — `get_weather_score()`
- **Fallback**: Simulated monsoon data if API unavailable (June-Sept = rain season)

### 3. Neo4j AuraDB (Graph Database)
- **Purpose**: Train network graph (1,153 trains, 38 stations), crowd report aggregation, route queries
- **Auth**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **Files that query Neo4j**:
  - `backend/app/core.py:21-40` — `get_neo4j_driver()`, `run_cypher()`
  - `backend/app/engines/crowd_engine.py:41-92` — `get_historical_crowd_score()` (Cypher aggregation)
  - `backend/app/engines/crowd_engine.py:97-205` — `get_crowd_trend_score()` (7-day vs baseline)
  - `backend/app/engines/crowd_engine.py:455+` — `store_crowd_report()` (save user feedback)

### 4. Zilliz Cloud (Managed Milvus)
- **Purpose**: Legal knowledge vector store — 108 chunks of IPC sections, Railways Act, RCT compensation schedules
- **Auth**: `ZILLIZ_URI`, `ZILLIZ_TOKEN`
- **Embedding**: `text-embedding-3-small` (1536 dimensions)
- **Collection**: `legal_corpus` with cosine similarity
- **Files**:
  - `backend/app/core.py:57-72` — `get_milvus_client()`
  - `backend/app/engines/jansuraksha/retrieval.py:75-90` — `retrieve_legal_context()` (filtered vector search)
  - `backend/scripts/ingest_legal.py` — Legal corpus embedding + upsert

### 5. Gmail SMTP (Email Notifications)
- **Purpose**: Notify passengers when complaint status changes (acknowledged/resolved/rejected)
- **Auth**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`
- **File**: `backend/app/services/notifications.py`
- **Optional**: System works without email configured

### 6. Twilio (SMS Notifications)
- **Purpose**: SMS alerts on complaint status changes
- **Auth**: `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_FROM`
- **File**: `backend/app/services/notifications.py`
- **Optional**: System works without Twilio configured

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/signup` | None | Register passenger or police officer |
| POST | `/api/auth/login` | None | Login with email/password |
| GET | `/api/auth/me` | Token | Get current user profile |
| POST | `/api/trains/search` | Token | Search trains with crowd badges |
| POST | `/api/trains/report` | Token | Submit crowd feedback (GREEN/YELLOW/RED) |
| POST | `/api/bot/chat` | Token | Send message to Jan Suraksha Bot |
| GET | `/api/bot/user-context/{id}` | Token | Load user profile for bot context |
| GET | `/api/complaints/` | Token (police) | List all complaints with filters |
| GET | `/api/complaints/{ref}` | Token (police) | Get single complaint by ref |
| PATCH | `/api/complaints/{ref}/status` | Token (police) | Update status (acknowledge/resolve/reject) |
| GET | `/api/safety/alerts` | Token | Get passenger safety alerts (last 24h) |
| GET | `/api/safety/analytics` | Token (police) | Get police analytics + patrol recommendation |
| GET | `/health` | None | Health check |

---

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Neo4j AuraDB account (free tier)
- Zilliz Cloud account (free tier)
- OpenAI API key
- OpenWeatherMap API key (free tier)

### 1. Clone and setup environment

```bash
git clone <repo-url>
cd RailFLOW

# Copy env template
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Seed databases

```bash
# Initialize SQLite schema (auto-creates on first run)
# Seed Neo4j with train network + crowd data
python scripts/seed_neo4j.py
python scripts/seed_crowd_data.py

# Embed and ingest legal corpus into Zilliz
python scripts/ingest_legal.py
```

### 4. Start backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### 5. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 6. Build Android APK (optional)

```bash
cd frontend

# Build web assets
npm run build

# Sync to Capacitor
npx cap sync android

# Open in Android Studio
npx cap open android
```

---

## Test Accounts

| Role | Email | Password | Language |
|------|-------|----------|----------|
| Passenger | `raj@test.com` | `Test@1234` | English |
| Passenger | `priya@test.com` | `Test@1234` | Hindi |
| Passenger | `amit@test.com` | `Test@1234` | Marathi |
| Police | `deshmukh@police.gov` | `Test@1234` | English |

---

## Key Technical Decisions

### Why LangGraph (not a simple chatbot)?
The Jan Suraksha bot is a **cyclic state machine** with a central Manager node that makes all routing decisions using pure Python (zero LLM). This ensures:
- Max 3 LLM calls per turn (classify + execute + respond)
- Manager shortcut: if user picks "1", skips classify entirely
- Legal context cached on re-entry — no duplicate embeddings
- Sensitive content bypass: regex + pre-written responses, zero LLM, avoids Azure content filter

### Why slot-filling (not LLM-generated legal documents)?
GRP FIR, CPGRAMS, and RCT templates are **real government forms** with slot-filling. The LLM never writes legal text — it only generates an incident summary that goes into a specific slot. This prevents hallucination of IPC section numbers, compensation amounts, and authority names.

### Why Neo4j (not just SQL)?
Train networks are inherently graph-structured. A train STOPS_AT stations with time + sequence. Adjacent stations are linked by NEXT_ON relationships per line. Crowd reports are connected to trains via REPORTS_ON. Cypher queries for "find all trains from A to B at time T with crowd data" are natural graph traversals, not JOIN-heavy SQL.

### Why 3-signal fusion (not simple average)?
Each signal captures different information:
- **Historical (50%)** — baseline crowd pattern for this train/day/hour
- **Trend (30%)** — is this week worse or better than usual?
- **Weather (20%)** — rain multiplier for Mumbai monsoon season
Adaptive: when weather API is unavailable, weights shift to 60%/40% without dilution.

---

## Database Schemas

### SQLite

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'passenger',    -- 'passenger' | 'police'
    language_pref TEXT DEFAULT 'en',  -- 'en' | 'hi' | 'mr'
    phone TEXT,
    address TEXT,
    origin TEXT,                      -- usual origin station
    destination TEXT,                 -- usual destination station
    line TEXT,                        -- WR | CR | HR
    usual_train TEXT,
    created_at TEXT
);

CREATE TABLE complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref TEXT UNIQUE NOT NULL,         -- RM-YYYYMMDD-XXXXXX
    user_id TEXT REFERENCES users(id),
    incident_type TEXT,               -- theft, robbery, assault, ...
    severity TEXT,                    -- low, medium, high, critical
    status TEXT DEFAULT 'filed',      -- filed, acknowledged, resolved, rejected
    complaint_text TEXT,              -- filled FIR/CPGRAMS template
    user_message TEXT,                -- original user messages
    authority TEXT,                   -- GRP, RPF, RCT, etc.
    officer_note TEXT,
    from_station TEXT,
    to_station TEXT,
    date_filed TEXT,
    updated_at TEXT
);
```

### Neo4j Graph

**Nodes:** Station, Train, CrowdReport, User, Route, Complaint, CrowdSignal, DetectionEvent, DisruptionEvent

**Key Relationships:**
- `(Train)-[:ARRIVES_AT {time, sequence}]->(Station)`
- `(Train)-[:DEPARTS_FROM {time, sequence}]->(Station)`
- `(CrowdReport)-[:REPORTS_ON]->(Train)`
- `(Station)-[:NEXT_ON {distance_min}]->(Station)` per line

### Zilliz/Milvus Vector Store

**Collection:** `legal_corpus`
- **Dimension:** 1536 (text-embedding-3-small)
- **Metric:** Cosine similarity
- **Fields:** text, doc_type, incident_type, section_ref, authority, compensation_eligible, location_scope, legal_remedy
- **108 chunks** from: Railways Act 1989, IPC sections, RCT compensation schedules, CPGRAMS procedures, jurisdiction guides

---

## Environment Variables

```bash
# ═══ REQUIRED ═══

# Neo4j AuraDB
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# OpenAI (GPT-4o-mini + text-embedding-3-small)
OPENAI_API_KEY=sk-xxxx
OPENAI_BASE_URL=                    # Optional: LiteLLM proxy URL

# OpenWeatherMap (free tier: 1000 calls/day)
OPENWEATHERMAP_KEY=xxxx

# Zilliz Cloud (managed Milvus)
ZILLIZ_URI=https://xxxx.serverless.cloud.zilliz.com
ZILLIZ_TOKEN=xxxx

# ═══ OPTIONAL ═══

# Email notifications (Gmail SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=app_specific_password

# SMS notifications (Twilio)
TWILIO_SID=
TWILIO_TOKEN=
TWILIO_FROM=+1234567890
```

---

## License

Built for the mIndicator AI Hackathon 2026 at VJTI, Mumbai.

**Team:** Bhoomi Singh & Dhruv Jitendra Patel
