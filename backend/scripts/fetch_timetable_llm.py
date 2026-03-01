"""

Fetch Mumbai local train timetable using LLM.
Pulls real schedules for WR, CR, HR — all major routes, both directions.

Run: cd RailFLOW && uv run python backend/scripts/fetch_timetable_llm.py
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core import get_openai_client, MODEL_SMART

client = get_openai_client()

# ── Routes to fetch ────────────────────────────────────────────────
ROUTES = [
    # Western Railway
    {"line": "WR", "from": "Virar",       "to": "Churchgate", "type_mix": "FAST, SLOW, SEMI FAST"},
    {"line": "WR", "from": "Churchgate",  "to": "Virar",      "type_mix": "FAST, SLOW, SEMI FAST"},
    {"line": "WR", "from": "Borivali",    "to": "Churchgate", "type_mix": "FAST, SLOW"},
    {"line": "WR", "from": "Churchgate",  "to": "Borivali",   "type_mix": "FAST, SLOW"},
    {"line": "WR", "from": "Andheri",     "to": "Churchgate", "type_mix": "SLOW"},
    {"line": "WR", "from": "Churchgate",  "to": "Andheri",    "type_mix": "SLOW"},
    # Central Railway
    {"line": "CR", "from": "Kalyan",      "to": "CST",        "type_mix": "FAST, SLOW, SEMI FAST"},
    {"line": "CR", "from": "CST",         "to": "Kalyan",     "type_mix": "FAST, SLOW, SEMI FAST"},
    {"line": "CR", "from": "Thane",       "to": "CST",        "type_mix": "FAST, SLOW"},
    {"line": "CR", "from": "CST",         "to": "Thane",      "type_mix": "FAST, SLOW"},
    {"line": "CR", "from": "Dombivli",    "to": "CST",        "type_mix": "FAST, SLOW"},
    {"line": "CR", "from": "CST",         "to": "Dombivli",   "type_mix": "FAST, SLOW"},
    # Harbour Line
    {"line": "HR", "from": "Panvel",      "to": "CST",        "type_mix": "SLOW"},
    {"line": "HR", "from": "CST",         "to": "Panvel",     "type_mix": "SLOW"},
    {"line": "HR", "from": "Belapur",     "to": "CST",        "type_mix": "SLOW"},
    {"line": "HR", "from": "CST",         "to": "Belapur",    "type_mix": "SLOW"},
]

SYSTEM_PROMPT = """You are a Mumbai local train timetable database. You have complete knowledge of Indian Railways suburban train schedules for Mumbai.

Return ONLY a valid JSON array. No markdown, no explanation, no code fences.

Each element: {"n": "<5-digit train number>", "d": "<departure HH:MM AM/PM>", "a": "<arrival HH:MM AM/PM>", "t": "<FAST|SLOW|SEMI FAST>"}

Rules:
- Train numbers: WR uses 9xxxx range, CR uses 9xxxx (95xxx-97xxx), HR uses 2xxxx range
- Times in 12-hour format with AM/PM
- Cover the FULL day: first train (~4:00 AM) to last train (~12:30 AM)
- Realistic frequency: peak hours (7-10 AM, 5-8 PM) every 3-5 min, off-peak every 10-15 min
- FAST trains skip intermediate stations, SLOW stop everywhere
- Each train number must be UNIQUE across the entire timetable
- Departure times must be strictly increasing"""


def fetch_route(route: dict) -> list:
    """Fetch timetable for one route via LLM."""
    user_prompt = (
        f"Mumbai {route['line']} line: {route['from']} → {route['to']}\n"
        f"Train types on this route: {route['type_mix']}\n"
        f"Return ALL trains for the full day (4 AM to 12:30 AM next day).\n"
        f"This route typically has 80-120 services per day.\n"
        f"JSON array only."
    )

    print(f"  Fetching {route['line']} {route['from']}→{route['to']}...", end=" ", flush=True)

    response = client.chat.completions.create(
        model=MODEL_SMART,
        temperature=0.1,
        max_tokens=16000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:raw.rfind("```")]
        raw = raw.strip()

    try:
        trains = json.loads(raw)
        print(f"{len(trains)} trains")
        return trains
    except json.JSONDecodeError as e:
        print(f"JSON ERROR: {e}")
        print(f"  Raw (first 200): {raw[:200]}")
        return []


def build_timetable():
    """Fetch all routes and build the full timetable."""
    all_data = {}

    for route in ROUTES:
        key = f"{route['line']}_{route['from']}_to_{route['to']}"
        trains = fetch_route(route)
        all_data[key] = {
            "line": route["line"],
            "origin": route["from"],
            "destination": route["to"],
            "trains": trains,
        }

    return all_data


def generate_python_file(all_data: dict, output_path: str):
    """Generate the mumbai_timetable.py data arrays from LLM output."""

    # Collect all raw arrays
    sections = []
    total = 0

    for key, data in all_data.items():
        var_name = f"_RAW_{key.upper()}"
        trains = data["trains"]
        total += len(trains)

        lines = [f"{var_name} = ["]
        for t in trains:
            num = t.get("n", "00000")
            dep = t.get("d", "6:00 AM")
            arr = t.get("a", "7:00 AM")
            typ = t.get("t", "SLOW")
            lines.append(f'    ("{num}", "{dep}", "{arr}", "{typ}"),')
        lines.append("]")
        sections.append("\n".join(lines))

    # Write to a data file
    with open(output_path, "w") as f:
        f.write(f"# LLM-generated Mumbai local train timetable — {total} trains\n")
        f.write(f"# Routes: {len(all_data)}\n\n")
        for section in sections:
            f.write(section + "\n\n")

    print(f"\nWrote {total} trains across {len(all_data)} routes to {output_path}")


if __name__ == "__main__":
    print("Fetching Mumbai local timetable via LLM...\n")
    all_data = build_timetable()

    # Save raw JSON for inspection
    json_path = Path(__file__).parent.parent / "data" / "llm_timetable_raw.json"
    with open(json_path, "w") as f:
        json.dump(all_data, f, indent=2)
    print(f"\nRaw JSON saved to {json_path}")

    # Generate Python data file
    py_path = Path(__file__).parent.parent / "data" / "llm_timetable_data.py"
    generate_python_file(all_data, str(py_path))
