#!/usr/bin/env python3
"""
Seed Neo4j with the full Mumbai train network graph.

Creates:
  - Station nodes (with lines list)
  - Train nodes (all 1153 trains)
  - STOPS_AT relationships (train → station, with time & sequence)
  - NEXT_ON relationships (adjacent stations per line — track topology)

Junctions are implicit: stations appearing on multiple lines
(e.g., Dadar on WR+CR, CST on CR+HR+HRW).

Usage:
    python backend/scripts/seed_neo4j.py          # incremental (MERGE)
    python backend/scripts/seed_neo4j.py --clear   # wipe & reseed
"""

import sys, os, json, argparse

# Allow imports from project root and scripts directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

from backend.app.core import run_cypher
from seed_crowd_data import get_crowd_distribution, generate_reports
from backend.data.mumbai_timetable import (
    WR_STATIONS_CUMUL, CR_STATIONS_CUMUL,
    HR_STATIONS_CUMUL, HRW_STATIONS_CUMUL,
)

# ── Config ────────────────────────────────────────────────────────

CUMUL_MAPS = {
    "WR":  WR_STATIONS_CUMUL,
    "CR":  CR_STATIONS_CUMUL,
    "HR":  HR_STATIONS_CUMUL,
    "HRW": HRW_STATIONS_CUMUL,
}

JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "llm_timetable_raw.json")

BATCH_SIZE = 300

# Normalize station names from scraped JSON to canonical names in cumul maps
_NAME_FIXES = {
    "Mira Rd": "Mira Road",
    "Nalla Sopara": "Nala Sopara",
    "Diwa": "Diva",
}


def _norm(name: str) -> str:
    return _NAME_FIXES.get(name, name)


def _parse_time(t: str) -> str:
    """Convert '6:08 am' / '10:13 pm' / '12:05 AM' to 24h 'HH:MM'."""
    t = t.strip().lower()
    parts = t.replace("am", "").replace("pm", "").strip().split(":")
    h, m = int(parts[0]), int(parts[1])
    is_pm = "pm" in t
    if is_pm and h != 12:
        h += 12
    if not is_pm and h == 12:
        h = 0
    return f"{h:02d}:{m:02d}"


def _duration_str(dep: str, arr: str) -> str:
    """Compute duration string from HH:MM departure and arrival."""
    dh, dm = map(int, dep.split(":"))
    ah, am = map(int, arr.split(":"))
    total_dep = dh * 60 + dm
    total_arr = ah * 60 + am
    if total_arr < total_dep:
        total_arr += 24 * 60
    diff = total_arr - total_dep
    if diff >= 60:
        return f"{diff // 60}h {diff % 60:02d}m"
    return f"{diff}m"


# ── Load data ─────────────────────────────────────────────────────

def load_json():
    with open(JSON_PATH) as f:
        return json.load(f)


def collect_stations(data):
    """Build {station_name: set_of_lines} from cumul maps + JSON stops."""
    stations = {}
    # From cumul maps (canonical)
    for line, cumul in CUMUL_MAPS.items():
        for name, _ in cumul:
            stations.setdefault(name, set()).add(line)
    # From JSON stops (picks up stations not in cumul, e.g. Naigaon)
    for route_key, route in data.items():
        line = route["line"]
        for t in route["trains"]:
            if not t.get("stops"):
                continue
            for stn in t["stops"]:
                stations.setdefault(_norm(stn), set()).add(line)
    return stations


def _duration_min(dep: str, arr: str) -> int:
    """Compute duration in minutes from HH:MM strings."""
    dh, dm = map(int, dep.split(":"))
    ah, am = map(int, arr.split(":"))
    total = (ah * 60 + am) - (dh * 60 + dm)
    if total < 0:
        total += 24 * 60
    return total


def _peak_label(dep: str) -> str:
    """Classify departure time into peak/off-peak/late."""
    h = int(dep.split(":")[0])
    if 7 <= h <= 10 or 17 <= h <= 21:
        return "PEAK"
    elif 23 <= h or h <= 4:
        return "LATE"
    return "OFF_PEAK"


def _direction(origin: str, dest: str, line: str) -> str:
    """UP = towards terminus (CST/Churchgate), DOWN = away from terminus."""
    termini = {"CST", "Churchgate"}
    if dest in termini:
        return "UP"
    if origin in termini:
        return "DOWN"
    return "DOWN"


def collect_trains(data):
    """Build list of train dicts from JSON routes."""
    trains = []
    seen = set()
    # Pre-count stops per train
    stops_count = {}
    for route in data.values():
        for t in route["trains"]:
            if t.get("stops"):
                stops_count[t["n"]] = len(t["stops"])

    for route_key, route in data.items():
        line = route["line"]
        origin = route["origin"]
        dest = route["destination"]
        for t in route["trains"]:
            num = t["n"]
            if num in seen:
                continue
            seen.add(num)
            dep = _parse_time(t["d"])
            arr = _parse_time(t["a"])
            # Determine type
            raw_type = t.get("t", "SLOW").upper()
            if "AC" in raw_type:
                typ, train_type = "AC", "AC LOCAL"
            elif "SEMI" in raw_type:
                typ, train_type = "SEMI_FAST", "SEMI FAST"
            elif "FAST" in raw_type:
                typ, train_type = "FAST", "FAST"
            else:
                typ, train_type = "SLOW", "SLOW"

            trains.append({
                "number": num,
                "name": f"{origin}-{dest} {train_type}",
                "type": typ,
                "train_type": train_type,
                "line": line,
                "origin": origin,
                "dest": dest,
                "depart": dep,
                "arrive": arr,
                "duration": _duration_str(dep, arr),
                "duration_min": _duration_min(dep, arr),
                "depart_hour": int(dep.split(":")[0]),
                "peak": _peak_label(dep),
                "direction": _direction(origin, dest, line),
                "stops_count": stops_count.get(num, 0),
                "has_stops": num in stops_count,
            })
    return trains


def collect_stops(data):
    """Build list of {train_number, station, time, sequence} from JSON."""
    stops = []
    for route_key, route in data.items():
        for t in route["trains"]:
            if not t.get("stops"):
                continue
            for seq, (station, time) in enumerate(t["stops"].items(), 1):
                stops.append({
                    "number": t["n"],
                    "station": _norm(station),
                    "time": time,
                    "sequence": seq,
                })
    return stops


def collect_next_on():
    """Build NEXT_ON edges: adjacent stations per line with cumul minute diff."""
    edges = []
    for line, cumul in CUMUL_MAPS.items():
        for i in range(len(cumul) - 1):
            a_name, a_min = cumul[i]
            b_name, b_min = cumul[i + 1]
            edges.append({
                "a": a_name,
                "b": b_name,
                "line": line,
                "distance_min": b_min - a_min,
            })
    return edges


# ── Seed functions ────────────────────────────────────────────────

def clear_graph():
    print("Clearing all Train, Station, CrowdReport + relationships...")
    run_cypher("MATCH ()-[r:REPORTS_ON]->() DELETE r")
    run_cypher("MATCH ()-[r:STOPS_AT]->() DELETE r")
    run_cypher("MATCH ()-[r:NEXT_ON]->() DELETE r")
    # DETACH DELETE removes nodes + any remaining relationships
    for label in ["CrowdReport", "WR", "CR", "HR", "HRW", "Junction", "Train", "Station"]:
        run_cypher(f"MATCH (n:{label}) DETACH DELETE n")
    print("  Cleared.")


def create_indexes():
    print("Creating indexes & constraints...")
    run_cypher("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Station) REQUIRE s.name IS UNIQUE")
    run_cypher("CREATE INDEX station_lines IF NOT EXISTS FOR (s:Station) ON (s.lines)")
    run_cypher("CREATE INDEX train_number IF NOT EXISTS FOR (t:Train) ON (t.number)")
    run_cypher("CREATE INDEX train_line IF NOT EXISTS FOR (t:Train) ON (t.line)")
    run_cypher("CREATE INDEX train_depart IF NOT EXISTS FOR (t:Train) ON (t.depart)")
    # CrowdReport indexes — used by crowd_engine.py queries
    run_cypher("CREATE INDEX crowd_train IF NOT EXISTS FOR (c:CrowdReport) ON (c.train_number)")
    run_cypher("CREATE INDEX crowd_day IF NOT EXISTS FOR (c:CrowdReport) ON (c.day_type)")
    run_cypher("CREATE INDEX crowd_hour IF NOT EXISTS FOR (c:CrowdReport) ON (c.hour_bucket)")
    run_cypher("CREATE INDEX crowd_ts IF NOT EXISTS FOR (c:CrowdReport) ON (c.timestamp)")
    print("  Done.")


def seed_stations(stations):
    """Create Station nodes with metadata + line labels."""
    termini = {"CST", "Churchgate", "Virar", "Kalyan", "Panvel", "Goregaon"}
    print(f"Seeding {len(stations)} stations...")
    rows = [{
        "name": name,
        "lines": sorted(lines),
        "line_count": len(lines),
        "is_junction": len(lines) > 1,
        "is_terminus": name in termini,
    } for name, lines in stations.items()]
    run_cypher("""
        UNWIND $rows AS r
        MERGE (s:Station {name: r.name})
        SET s.lines = r.lines, s.line_count = r.line_count,
            s.is_junction = r.is_junction, s.is_terminus = r.is_terminus
    """, {"rows": rows})
    print(f"  {len(rows)} stations merged.")

    # Add line labels to stations for color coding
    print("Adding line labels to stations...")
    for line in ["WR", "CR", "HR", "HRW"]:
        run_cypher(f"MATCH (s:Station) WHERE $line IN s.lines SET s:{line}", {"line": line})

    # Add Junction label for multi-line stations
    run_cypher("MATCH (s:Station) WHERE s.is_junction = true SET s:Junction")
    jcount = run_cypher("MATCH (s:Junction) RETURN count(s) AS c")
    print(f"  :Junction → {jcount[0]['c'] if jcount else 0} stations")


def seed_next_on(edges):
    """Create NEXT_ON relationships between adjacent stations."""
    print(f"Seeding {len(edges)} NEXT_ON edges...")
    run_cypher("""
        UNWIND $edges AS e
        MATCH (a:Station {name: e.a})
        MATCH (b:Station {name: e.b})
        MERGE (a)-[r:NEXT_ON {line: e.line}]->(b)
        SET r.distance_min = e.distance_min
    """, {"edges": edges})
    print(f"  {len(edges)} edges merged.")


def seed_trains(trains):
    """Create Train nodes in batches with metadata."""
    print(f"Seeding {len(trains)} trains...")
    for i in range(0, len(trains), BATCH_SIZE):
        chunk = trains[i:i + BATCH_SIZE]
        run_cypher("""
            UNWIND $trains AS t
            MERGE (tr:Train {number: t.number})
            SET tr.name = t.name, tr.type = t.type, tr.train_type = t.train_type,
                tr.line = t.line, tr.origin = t.origin, tr.destination = t.dest,
                tr.depart = t.depart, tr.arrive = t.arrive, tr.duration = t.duration,
                tr.duration_min = t.duration_min, tr.depart_hour = t.depart_hour,
                tr.peak = t.peak, tr.direction = t.direction,
                tr.stops_count = t.stops_count, tr.has_stops = t.has_stops
        """, {"trains": chunk})
        print(f"  ... trains {i + 1}-{min(i + BATCH_SIZE, len(trains))}")
    print(f"  {len(trains)} trains merged.")

    # Add line-specific labels for color coding in Neo4j Browser
    print("Adding line labels to trains...")
    for line in ["WR", "CR", "HR", "HRW"]:
        result = run_cypher(f"MATCH (t:Train) WHERE t.line = $line SET t:{line}", {"line": line})
        count = run_cypher(f"MATCH (t:{line}) RETURN count(t) AS c")
        c = count[0]["c"] if count else 0
        print(f"  :{line} → {c} trains")


def seed_stops(stops):
    """Create STOPS_AT relationships in batches."""
    print(f"Seeding {len(stops)} STOPS_AT relationships...")
    for i in range(0, len(stops), BATCH_SIZE):
        chunk = stops[i:i + BATCH_SIZE]
        run_cypher("""
            UNWIND $stops AS s
            MATCH (tr:Train {number: s.number})
            MATCH (st:Station {name: s.station})
            MERGE (tr)-[r:STOPS_AT {sequence: s.sequence}]->(st)
            SET r.time = s.time
        """, {"stops": chunk})
        print(f"  ... stops {i + 1}-{min(i + BATCH_SIZE, len(stops))}")
    print(f"  {len(stops)} STOPS_AT merged.")


def seed_crowd_reports(trains):
    """Generate and insert 10K CrowdReports using real train data + Mumbai crowd patterns."""
    print(f"\nGenerating 10,000 crowd reports from {len(trains)} real trains...")
    reports = generate_reports(trains, n=10000)

    red = sum(1 for r in reports if r["crowd_level"] == "RED")
    yellow = sum(1 for r in reports if r["crowd_level"] == "YELLOW")
    green = sum(1 for r in reports if r["crowd_level"] == "GREEN")
    print(f"  Generated: RED={red}, YELLOW={yellow}, GREEN={green}")

    # Insert CrowdReport nodes in batches
    print(f"Inserting {len(reports)} CrowdReport nodes...")
    for i in range(0, len(reports), 500):
        chunk = reports[i:i + 500]
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
        print(f"  ... reports {i + 1}-{min(i + 500, len(reports))}")

    # Link CrowdReport → Train via REPORTS_ON
    print("Linking CrowdReports to Train nodes...")
    for i in range(0, len(reports), 500):
        chunk = [{"train_number": r["train_number"], "report_id": r["report_id"]}
                 for r in reports[i:i + 500]]
        run_cypher("""
            UNWIND $links AS l
            MATCH (tr:Train {number: l.train_number})
            MATCH (cr:CrowdReport {report_id: l.report_id})
            MERGE (cr)-[:REPORTS_ON]->(tr)
        """, {"links": chunk})

    print(f"  {len(reports)} CrowdReports inserted and linked.")
    return reports


# ── Main ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Seed Neo4j with Mumbai train network")
    parser.add_argument("--clear", action="store_true", help="Wipe and reseed")
    args = parser.parse_args()

    data = load_json()
    stations = collect_stations(data)
    trains = collect_trains(data)
    stops = collect_stops(data)
    edges = collect_next_on()

    if args.clear:
        clear_graph()

    create_indexes()
    seed_stations(stations)
    seed_next_on(edges)
    seed_trains(trains)
    seed_stops(stops)
    seed_crowd_reports(trains)

    # ── Verification stats ──
    print("\n── Verification ──")
    st_count = run_cypher("MATCH (s:Station) RETURN count(s) AS c")
    tr_count = run_cypher("MATCH (t:Train) RETURN count(t) AS c")
    stops_count = run_cypher("MATCH ()-[r:STOPS_AT]->() RETURN count(r) AS c")
    next_count = run_cypher("MATCH ()-[r:NEXT_ON]->() RETURN count(r) AS c")
    cr_count = run_cypher("MATCH (cr:CrowdReport) RETURN count(cr) AS c")
    reports_on = run_cypher("MATCH ()-[r:REPORTS_ON]->() RETURN count(r) AS c")
    junctions = run_cypher("MATCH (s:Station) WHERE size(s.lines) > 1 RETURN s.name AS name, s.lines AS lines")

    print(f"  Stations:     {st_count[0]['c'] if st_count else '?'}")
    print(f"  Trains:       {tr_count[0]['c'] if tr_count else '?'}")
    print(f"  STOPS_AT:     {stops_count[0]['c'] if stops_count else '?'}")
    print(f"  NEXT_ON:      {next_count[0]['c'] if next_count else '?'}")
    print(f"  CrowdReports: {cr_count[0]['c'] if cr_count else '?'}")
    print(f"  REPORTS_ON:   {reports_on[0]['c'] if reports_on else '?'}")
    print(f"  Junctions:    {len(junctions)}")
    for j in junctions:
        print(f"    {j['name']}: {j['lines']}")

    # ── Crowd distribution stats ──
    crowd_dist = run_cypher("""
        MATCH (cr:CrowdReport)
        RETURN cr.crowd_level AS level, count(*) AS total
        ORDER BY total DESC
    """)
    crowd_by_line = run_cypher("""
        MATCH (cr:CrowdReport)
        RETURN cr.line AS line, cr.crowd_level AS level, count(*) AS total
        ORDER BY cr.line, total DESC
    """)
    date_range = run_cypher("""
        MATCH (cr:CrowdReport)
        RETURN min(cr.timestamp) AS earliest, max(cr.timestamp) AS latest
    """)
    virar_sample = run_cypher("""
        MATCH (cr:CrowdReport)
        WHERE (cr.origin = 'Virar' OR cr.destination = 'Virar')
              AND cr.day_type = 'weekday'
              AND cr.hour_bucket STARTS WITH '08'
        RETURN cr.crowd_level AS level, count(*) AS total
        ORDER BY total DESC
    """)

    if crowd_dist:
        print(f"\n  Crowd distribution (overall):")
        for row in crowd_dist:
            print(f"    {row['level']:8s}: {row['total']}")

    if date_range and date_range[0].get("earliest"):
        print(f"  Date range: {date_range[0]['earliest'][:10]} → {date_range[0]['latest'][:10]}")

    if crowd_by_line:
        print(f"\n  Per-line breakdown:")
        for row in crowd_by_line:
            print(f"    {row['line']} {row['level']:8s}: {row['total']}")

    if virar_sample:
        print(f"\n  Virar weekday 8am sample (should be mostly RED):")
        for row in virar_sample:
            print(f"    {row['level']:8s}: {row['total']}")

    print("\nDone!")


if __name__ == "__main__":
    main()
