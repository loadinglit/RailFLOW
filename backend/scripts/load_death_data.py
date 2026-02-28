"""
Load station death data into Neo4j.
Updates existing Station nodes with safety statistics.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core import run_cypher

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "deaths", "station_deaths.json")


def load_death_data():
    with open(DATA_FILE) as f:
        data = json.load(f)

    stations = data["stations"]
    print(f"[load] Loading death data for {len(stations)} stations...")

    for s in stations:
        run_cypher("""
            MERGE (st:Station {name: $name})
            SET st.line = $line,
                st.annual_deaths = $annual_deaths,
                st.trespass_deaths = $trespass_deaths,
                st.footboard_deaths = $footboard_deaths,
                st.has_fob = $has_fob,
                st.fob_adequate = $fob_adequate,
                st.platform_count = $platform_count,
                st.daily_footfall = $daily_footfall,
                st.lat = $lat,
                st.lng = $lng,
                st.notes = $notes
        """, {
            "name": s["name"],
            "line": s["line"],
            "annual_deaths": s["annual_deaths"],
            "trespass_deaths": s["trespass_deaths"],
            "footboard_deaths": s["footboard_deaths"],
            "has_fob": s["has_fob"],
            "fob_adequate": s.get("fob_adequate", True),
            "platform_count": s["platform_count"],
            "daily_footfall": s["daily_footfall"],
            "lat": s["lat"],
            "lng": s["lng"],
            "notes": s.get("notes", ""),
        })
        print(f"  {s['name']} ({s['line']}) — {s['annual_deaths']} deaths/yr")

    # Add DetectionEvent constraint and indexes
    run_cypher("CREATE CONSTRAINT IF NOT EXISTS FOR (d:DetectionEvent) REQUIRE d.id IS UNIQUE")
    run_cypher("CREATE INDEX IF NOT EXISTS FOR (d:DetectionEvent) ON (d.timestamp)")
    print(f"\n[load] Done. {len(stations)} stations updated with safety data.")


if __name__ == "__main__":
    load_death_data()
