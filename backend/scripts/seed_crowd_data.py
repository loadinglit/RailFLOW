"""
RailFlow — Neo4j Seed Script
Generates a comprehensive Mumbai local train timetable + 5000 crowd reports.

Timetable: ~500 trains across WR/CR/HR, 4am to midnight, realistic frequency.
Uses static deterministic timetable from mumbai_timetable.py (real durations/types).
Reports: 5000 over 3 months (Dec 2025 → Feb 2026) with peak-hour weighting.

Run: cd RailFLOW && uv run python backend/scripts/seed_crowd_data.py
"""

import os
import sys
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Add project root so data package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core import run_cypher, get_neo4j_driver
from backend.data.mumbai_timetable import generate_timetable


# ══════════════════════════════════════════════════════════════════════
# STATION DATA
# ══════════════════════════════════════════════════════════════════════

STATIONS = [
    # Western Line (27 stations)
    {"name": "Virar",          "line": "WR", "zone": "outskirts"},
    {"name": "Nala Sopara",    "line": "WR", "zone": "outskirts"},
    {"name": "Vasai Road",     "line": "WR", "zone": "outskirts"},
    {"name": "Bhayander",      "line": "WR", "zone": "suburbs"},
    {"name": "Mira Road",      "line": "WR", "zone": "suburbs"},
    {"name": "Dahisar",        "line": "WR", "zone": "suburbs"},
    {"name": "Borivali",       "line": "WR", "zone": "suburbs"},
    {"name": "Kandivali",      "line": "WR", "zone": "suburbs"},
    {"name": "Malad",          "line": "WR", "zone": "suburbs"},
    {"name": "Goregaon",       "line": "WR", "zone": "western"},
    {"name": "Ram Mandir",     "line": "WR", "zone": "western"},
    {"name": "Jogeshwari",     "line": "WR", "zone": "western"},
    {"name": "Andheri",        "line": "WR", "zone": "western"},
    {"name": "Vile Parle",     "line": "WR", "zone": "western"},
    {"name": "Santacruz",      "line": "WR", "zone": "western"},
    {"name": "Khar Road",      "line": "WR", "zone": "western"},
    {"name": "Bandra",         "line": "WR", "zone": "western"},
    {"name": "Mahim",          "line": "WR", "zone": "central"},
    {"name": "Matunga Road",   "line": "WR", "zone": "central"},
    {"name": "Dadar",          "line": "WR", "zone": "central"},
    {"name": "Prabhadevi",     "line": "WR", "zone": "south"},
    {"name": "Elphinstone",    "line": "WR", "zone": "south"},
    {"name": "Lower Parel",    "line": "WR", "zone": "south"},
    {"name": "Mahalaxmi",      "line": "WR", "zone": "south"},
    {"name": "Mumbai Central", "line": "WR", "zone": "south"},
    {"name": "Grant Road",     "line": "WR", "zone": "south"},
    {"name": "Churchgate",     "line": "WR", "zone": "terminus"},
    # Central Line (18 stations)
    {"name": "Kasara",         "line": "CR", "zone": "outskirts"},
    {"name": "Karjat",         "line": "CR", "zone": "outskirts"},
    {"name": "Kalyan",         "line": "CR", "zone": "suburbs"},
    {"name": "Dombivli",       "line": "CR", "zone": "suburbs"},
    {"name": "Thane",          "line": "CR", "zone": "suburbs"},
    {"name": "Mulund",         "line": "CR", "zone": "suburbs"},
    {"name": "Bhandup",        "line": "CR", "zone": "suburbs"},
    {"name": "Vikhroli",       "line": "CR", "zone": "eastern"},
    {"name": "Ghatkopar",      "line": "CR", "zone": "eastern"},
    {"name": "Vidyavihar",     "line": "CR", "zone": "eastern"},
    {"name": "Kurla",          "line": "CR", "zone": "eastern"},
    {"name": "Sion",           "line": "CR", "zone": "eastern"},
    {"name": "Matunga",        "line": "CR", "zone": "central"},
    {"name": "Dadar",          "line": "CR", "zone": "central"},
    {"name": "Byculla",        "line": "CR", "zone": "south"},
    {"name": "Sandhurst Road", "line": "CR", "zone": "south"},
    {"name": "Masjid",         "line": "CR", "zone": "south"},
    {"name": "CST",            "line": "CR", "zone": "terminus"},
    # Harbour Line (5 stations)
    {"name": "Panvel",         "line": "HR", "zone": "outskirts"},
    {"name": "Vashi",          "line": "HR", "zone": "suburbs"},
    {"name": "Belapur",        "line": "HR", "zone": "suburbs"},
    {"name": "Kurla",          "line": "HR", "zone": "eastern"},
    {"name": "CST",            "line": "HR", "zone": "terminus"},
]


# ══════════════════════════════════════════════════════════════════════
# TIMETABLE — imported from static data module
# ══════════════════════════════════════════════════════════════════════
# generate_timetable is imported from backend.data.mumbai_timetable above.
# It produces ~500 deterministic trains with real durations, arrive times,
# and train types (FAST, SLOW, SEMI FAST, AC LOCAL).


# ══════════════════════════════════════════════════════════════════════
# CROWD REPORT GENERATION
# ══════════════════════════════════════════════════════════════════════

# 200 repeat commuters
_COMMUTER_HASHES = [
    hashlib.md5(f"commuter_{i}".encode()).hexdigest()[:12]
    for i in range(200)
]


def get_crowd_distribution(train, day_type, hour):
    """
    Returns RED/YELLOW/GREEN distribution based on real Mumbai patterns.
    Uses train name, type, line, direction, day, and hour.
    """
    t = train["name"]
    line = train["line"]
    h = int(hour.split(":")[0]) if isinstance(hour, str) else hour
    is_southbound = train["dest"] in ("Churchgate", "CST")
    is_fast = train["type"] in ("FAST", "SEMI_FAST")

    # AC LOCAL trains are always less crowded (premium fare)
    if train["type"] == "AC":
        if day_type == "weekday" and (7 <= h <= 9 or 17 <= h <= 19):
            return {"RED": 5, "YELLOW": 30, "GREEN": 65}
        return {"RED": 2, "YELLOW": 15, "GREEN": 83}

    # ── Western Railway ──
    if line == "WR":
        if is_southbound:
            if "Virar" in t and is_fast:
                if day_type == "weekday":
                    if 7 <= h <= 9:     return {"RED": 72, "YELLOW": 22, "GREEN": 6}
                    if h == 6:          return {"RED": 48, "YELLOW": 38, "GREEN": 14}
                    if h == 5:          return {"RED": 15, "YELLOW": 35, "GREEN": 50}
                    if 10 <= h <= 11:   return {"RED": 30, "YELLOW": 45, "GREEN": 25}
                    return {"RED": 12, "YELLOW": 33, "GREEN": 55}
                if day_type == "saturday":
                    if 8 <= h <= 10:    return {"RED": 38, "YELLOW": 42, "GREEN": 20}
                    return {"RED": 12, "YELLOW": 35, "GREEN": 53}
                return {"RED": 5, "YELLOW": 20, "GREEN": 75}

            if "Borivali" in t and is_fast:
                if day_type == "weekday":
                    if 7 <= h <= 9:     return {"RED": 55, "YELLOW": 32, "GREEN": 13}
                    if h == 6:          return {"RED": 30, "YELLOW": 45, "GREEN": 25}
                    return {"RED": 10, "YELLOW": 35, "GREEN": 55}
                if day_type == "saturday" and 8 <= h <= 10:
                    return {"RED": 22, "YELLOW": 48, "GREEN": 30}
                return {"RED": 5, "YELLOW": 18, "GREEN": 77}

            if "Slow" in t:
                if day_type == "weekday" and 7 <= h <= 9:
                    return {"RED": 32, "YELLOW": 45, "GREEN": 23}
                return {"RED": 8, "YELLOW": 28, "GREEN": 64}

        else:  # northbound (Churchgate → outskirts)
            if "Virar" in t and is_fast:
                if day_type == "weekday":
                    if 17 <= h <= 19:   return {"RED": 68, "YELLOW": 24, "GREEN": 8}
                    if h == 20:         return {"RED": 40, "YELLOW": 38, "GREEN": 22}
                    return {"RED": 10, "YELLOW": 30, "GREEN": 60}
                if day_type == "saturday" and 17 <= h <= 19:
                    return {"RED": 32, "YELLOW": 43, "GREEN": 25}
                return {"RED": 5, "YELLOW": 22, "GREEN": 73}

            if "Borivali" in t:
                if day_type == "weekday":
                    if 17 <= h <= 19:   return {"RED": 50, "YELLOW": 35, "GREEN": 15}
                    if h == 20:         return {"RED": 25, "YELLOW": 40, "GREEN": 35}
                    return {"RED": 8, "YELLOW": 28, "GREEN": 64}
                return {"RED": 5, "YELLOW": 25, "GREEN": 70}

            if "Slow" in t:
                if day_type == "weekday" and 17 <= h <= 19:
                    return {"RED": 35, "YELLOW": 42, "GREEN": 23}
                return {"RED": 6, "YELLOW": 24, "GREEN": 70}

    # ── Central Railway ──
    if line == "CR":
        if is_southbound:
            if ("Kalyan" in t or "Kasara" in t) and is_fast:
                if day_type == "weekday":
                    if 7 <= h <= 9:     return {"RED": 65, "YELLOW": 27, "GREEN": 8}
                    if h == 6:          return {"RED": 35, "YELLOW": 42, "GREEN": 23}
                    if 10 <= h <= 11:   return {"RED": 25, "YELLOW": 42, "GREEN": 33}
                    return {"RED": 10, "YELLOW": 30, "GREEN": 60}
                if day_type == "saturday" and 8 <= h <= 10:
                    return {"RED": 28, "YELLOW": 47, "GREEN": 25}
                return {"RED": 5, "YELLOW": 22, "GREEN": 73}

            if "Thane" in t and is_fast:
                if day_type == "weekday" and 7 <= h <= 9:
                    return {"RED": 45, "YELLOW": 38, "GREEN": 17}
                return {"RED": 8, "YELLOW": 30, "GREEN": 62}

            if "Dombivli" in t:
                if day_type == "weekday" and 7 <= h <= 10:
                    return {"RED": 40, "YELLOW": 40, "GREEN": 20}
                return {"RED": 10, "YELLOW": 32, "GREEN": 58}

            if "Slow" in t:
                if day_type == "weekday" and 7 <= h <= 9:
                    return {"RED": 30, "YELLOW": 45, "GREEN": 25}
                return {"RED": 8, "YELLOW": 28, "GREEN": 64}

            if "Kurla" in t:
                return {"RED": 18, "YELLOW": 42, "GREEN": 40}

        else:  # northbound (CST → outskirts)
            if day_type == "weekday":
                if 17 <= h <= 19:   return {"RED": 58, "YELLOW": 30, "GREEN": 12}
                if h == 20:         return {"RED": 32, "YELLOW": 40, "GREEN": 28}
                return {"RED": 8, "YELLOW": 28, "GREEN": 64}
            if day_type == "saturday" and 17 <= h <= 19:
                return {"RED": 25, "YELLOW": 42, "GREEN": 33}
            return {"RED": 5, "YELLOW": 22, "GREEN": 73}

    # ── Harbour Line ──
    if line == "HR":
        if is_southbound:
            if day_type == "weekday":
                if 7 <= h <= 9:     return {"RED": 38, "YELLOW": 42, "GREEN": 20}
                return {"RED": 10, "YELLOW": 30, "GREEN": 60}
            return {"RED": 5, "YELLOW": 22, "GREEN": 73}
        else:
            if day_type == "weekday" and 17 <= h <= 19:
                return {"RED": 35, "YELLOW": 42, "GREEN": 23}
            return {"RED": 5, "YELLOW": 25, "GREEN": 70}

    # ── Fallback ──
    if day_type == "sunday":
        return {"RED": 4, "YELLOW": 18, "GREEN": 78}
    if day_type == "saturday":
        return {"RED": 8, "YELLOW": 32, "GREEN": 60}
    return {"RED": 12, "YELLOW": 38, "GREEN": 50}


def weighted_choice(dist):
    return random.choices(list(dist.keys()), weights=list(dist.values()), k=1)[0]


def generate_reports(all_trains, n=5000):
    """
    Generate n CrowdReports over 3 months (Dec 1 2025 → Feb 28 2026).
    Peak-hour trains get more reports. Recent week has a crowd spike on WR Virar trains.
    """
    reports = []
    start_date = datetime(2025, 12, 1)
    end_date = datetime(2026, 2, 28)
    total_days = (end_date - start_date).days

    # Build weighted train pool — peak hour trains get more reports
    train_weights = []
    for t in all_trains:
        h = int(t["depart"].split(":")[0])
        w = 1.0
        if 7 <= h <= 9 or 17 <= h <= 19:
            w = 4.0
        elif 6 <= h <= 10 or 16 <= h <= 20:
            w = 2.0
        if t["type"] == "FAST":
            w *= 1.5
        train_weights.append(w)

    for i in range(n):
        # Pick date — bias toward weekdays
        while True:
            days_offset = random.randint(0, total_days)
            report_date = start_date + timedelta(days=days_offset)
            wd = report_date.weekday()
            if wd < 5:
                break
            elif wd == 5 and random.random() < 0.55:
                break
            elif wd == 6 and random.random() < 0.25:
                break

        day_type = "sunday" if wd == 6 else ("saturday" if wd == 5 else "weekday")

        # Pick train (weighted)
        train = random.choices(all_trains, weights=train_weights, k=1)[0]

        # Report time: near train departure (±15 min)
        train_hour = int(train["depart"].split(":")[0])
        train_min = int(train["depart"].split(":")[1])
        offset_min = random.randint(-15, 15)
        report_min = train_min + offset_min
        report_hour = train_hour
        if report_min < 0:
            report_hour = max(0, report_hour - 1)
            report_min += 60
        elif report_min >= 60:
            report_hour = min(23, report_hour + 1)
            report_min -= 60

        timestamp = report_date.replace(
            hour=report_hour,
            minute=report_min,
            second=random.randint(0, 59),
        )

        hour_bucket = f"{train_hour:02d}:00-{(train_hour + 1) % 24:02d}:00"
        dist = get_crowd_distribution(train, day_type, f"{train_hour:02d}:00")

        # TREND SPIKE: Last week of Feb, WR Virar trains get extra RED
        if (report_date >= datetime(2026, 2, 22)
            and train["line"] == "WR"
            and "Virar" in train["name"]
            and day_type == "weekday"):
            dist = {
                "RED": min(92, dist["RED"] + 20),
                "YELLOW": max(4, dist["YELLOW"] - 10),
                "GREEN": max(4, dist["GREEN"] - 10),
            }

        crowd_level = weighted_choice(dist)
        user_hash = random.choice(_COMMUTER_HASHES)

        reports.append({
            "report_id": f"RPT_{i:05d}",
            "train_number": train["number"],
            "train_name": train["name"],
            "train_type": train["type"],
            "line": train["line"],
            "origin": train["origin"],
            "destination": train["dest"],
            "timestamp": timestamp.isoformat(),
            "day_type": day_type,
            "hour_bucket": hour_bucket,
            "crowd_level": crowd_level,
            "user_hash": user_hash,
        })

    return reports


# ══════════════════════════════════════════════════════════════════════
# NEO4J INGESTION
# ══════════════════════════════════════════════════════════════════════

def ingest_all():
    get_neo4j_driver()

    print("Generating timetable...")
    all_trains = generate_timetable()
    wr_count = sum(1 for t in all_trains if t["line"] == "WR")
    cr_count = sum(1 for t in all_trains if t["line"] == "CR")
    hr_count = sum(1 for t in all_trains if t["line"] == "HR")
    print(f"  WR: {wr_count} | CR: {cr_count} | HR: {hr_count} | Total: {len(all_trains)}")

    print("\nGenerating 5000 crowd reports...")
    reports = generate_reports(all_trains, 5000)

    print("\nClearing old data...")
    run_cypher("MATCH (n) DETACH DELETE n")

    # ── Batch: Stations ──
    print(f"Creating {len(STATIONS)} Station nodes (batch)...")
    run_cypher("""
        UNWIND $stations AS s
        MERGE (st:Station {name: s.name})
        SET st.line = s.line, st.zone = s.zone
    """, {"stations": STATIONS})

    # ── Batch: Trains (in chunks of 200) ──
    print(f"Creating {len(all_trains)} Train nodes (batch)...")
    train_rows = [{
        "number": t["number"], "name": t["name"], "type": t["type"],
        "train_type": t.get("train_type", ""),
        "line": t["line"], "origin": t["origin"], "dest": t["dest"],
        "depart": t["depart"], "arrive": t.get("arrive", ""),
        "duration": t.get("duration", ""),
    } for t in all_trains]

    for i in range(0, len(train_rows), 200):
        chunk = train_rows[i:i+200]
        run_cypher("""
            UNWIND $trains AS t
            MERGE (tr:Train {number: t.number})
            SET tr.name = t.name, tr.type = t.type, tr.train_type = t.train_type,
                tr.line = t.line, tr.origin = t.origin, tr.destination = t.dest,
                tr.depart = t.depart, tr.arrive = t.arrive, tr.duration = t.duration
        """, {"trains": chunk})
        print(f"  ... trains {i+1}-{min(i+200, len(train_rows))}")

    # ── Batch: Train → Station links ──
    print("Linking trains to stations (batch)...")
    link_rows = [{"number": t["number"], "origin": t["origin"], "dest": t["dest"]}
                 for t in all_trains]
    for i in range(0, len(link_rows), 200):
        chunk = link_rows[i:i+200]
        run_cypher("""
            UNWIND $links AS l
            MATCH (tr:Train {number: l.number})
            MATCH (orig:Station {name: l.origin})
            MATCH (dest:Station {name: l.dest})
            MERGE (tr)-[:DEPARTS_FROM]->(orig)
            MERGE (tr)-[:ARRIVES_AT]->(dest)
        """, {"links": chunk})

    # ── Batch: CrowdReports (in chunks of 500) ──
    print(f"Inserting {len(reports)} CrowdReport nodes (batch)...")
    for i in range(0, len(reports), 500):
        chunk = reports[i:i+500]
        run_cypher("""
            UNWIND $reports AS r
            CREATE (cr:CrowdReport {
                report_id:     r.report_id,
                train_number:  r.train_number,
                train_name:    r.train_name,
                train_type:    r.train_type,
                line:          r.line,
                origin:        r.origin,
                destination:   r.destination,
                timestamp:     r.timestamp,
                day_type:      r.day_type,
                hour_bucket:   r.hour_bucket,
                crowd_level:   r.crowd_level,
                user_hash:     r.user_hash
            })
        """, {"reports": chunk})
        print(f"  ... reports {i+1}-{min(i+500, len(reports))}")

    # ── Batch: CrowdReport → Train links ──
    print("Linking reports to trains (batch)...")
    for i in range(0, len(reports), 500):
        chunk = [{"train_number": r["train_number"], "report_id": r["report_id"]}
                 for r in reports[i:i+500]]
        run_cypher("""
            UNWIND $links AS l
            MATCH (tr:Train {number: l.train_number})
            MATCH (cr:CrowdReport {report_id: l.report_id})
            MERGE (cr)-[:REPORTS_ON]->(tr)
        """, {"links": chunk})

    print("Creating indexes...")
    run_cypher("CREATE INDEX crowd_train IF NOT EXISTS FOR (c:CrowdReport) ON (c.train_number)")
    run_cypher("CREATE INDEX crowd_day IF NOT EXISTS FOR (c:CrowdReport) ON (c.day_type)")
    run_cypher("CREATE INDEX crowd_hour IF NOT EXISTS FOR (c:CrowdReport) ON (c.hour_bucket)")
    run_cypher("CREATE INDEX crowd_ts IF NOT EXISTS FOR (c:CrowdReport) ON (c.timestamp)")
    run_cypher("CREATE INDEX train_line IF NOT EXISTS FOR (t:Train) ON (t.line)")
    run_cypher("CREATE INDEX train_depart IF NOT EXISTS FOR (t:Train) ON (t.depart)")

    # ── Stats ──
    dist = run_cypher("""
        MATCH (cr:CrowdReport)
        RETURN cr.crowd_level AS level, count(*) AS total
        ORDER BY total DESC
    """)
    line_dist = run_cypher("""
        MATCH (cr:CrowdReport)
        RETURN cr.line AS line, cr.crowd_level AS level, count(*) AS total
        ORDER BY cr.line, total DESC
    """)
    date_range = run_cypher("""
        MATCH (cr:CrowdReport)
        RETURN min(cr.timestamp) AS earliest, max(cr.timestamp) AS latest
    """)
    trains_per_line = run_cypher("""
        MATCH (t:Train)
        RETURN t.line AS line, count(*) AS total
        ORDER BY t.line
    """)

    # Sample: show what Virar Fast 8am weekday looks like
    virar_sample = run_cypher("""
        MATCH (cr:CrowdReport)
        WHERE cr.train_name CONTAINS 'Virar' AND cr.day_type = 'weekday'
              AND cr.hour_bucket STARTS WITH '08'
        RETURN cr.crowd_level AS level, count(*) AS total
        ORDER BY total DESC
    """)

    print(f"\n{'='*50}")
    print(f"SEED COMPLETE")
    print(f"{'='*50}")
    print(f"  Stations:     {len(STATIONS)}")
    print(f"  Trains:       {len(all_trains)}")
    for row in trains_per_line:
        print(f"    {row['line']}: {row['total']}")
    print(f"  CrowdReports: {len(reports)}")
    if date_range:
        print(f"  Date range:   {date_range[0]['earliest'][:10]} → {date_range[0]['latest'][:10]}")

    print(f"\n  Overall distribution:")
    for row in dist:
        print(f"    {row['level']:8s}: {row['total']}")

    print(f"\n  Per-line breakdown:")
    for row in line_dist:
        print(f"    {row['line']} {row['level']:8s}: {row['total']}")

    if virar_sample:
        print(f"\n  Virar Fast (weekday 8am) sample:")
        for row in virar_sample:
            print(f"    {row['level']:8s}: {row['total']}")


if __name__ == "__main__":
    ingest_all()
