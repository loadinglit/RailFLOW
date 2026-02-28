"""
Neo4j Schema Setup — Run ONCE at hackathon start.

Creates constraints, indexes, and demo user personas.
Both Bhoomi and Dhruv run this before doing anything else.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core import get_neo4j_driver


def setup_schema():
    driver = get_neo4j_driver()
    with driver.session() as session:
        # ── Constraints ────────────────────────────────────────
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Train) REQUIRE t.train_number IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Station) REQUIRE s.name IS UNIQUE",
        ]
        for c in constraints:
            session.run(c)
            print(f"[schema] {c[:60]}...")

        # ── Indexes for fast lookups ───────────────────────────
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (r:Route) ON (r.origin, r.destination)",
            "CREATE INDEX IF NOT EXISTS FOR (cs:CrowdSignal) ON (cs.timestamp)",
            "CREATE INDEX IF NOT EXISTS FOR (de:DisruptionEvent) ON (de.detected_at)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Complaint) ON (c.created_at)",
        ]
        for idx in indexes:
            session.run(idx)
            print(f"[schema] {idx[:60]}...")

        # ── Demo User Personas ─────────────────────────────────
        demo_users = [
            {
                "user_id": "rahul_001",
                "name": "Rahul",
                "origin": "Virar",
                "destination": "Churchgate",
                "line": "WR",
                "usual_train": "Virar Fast 08:05",
                "usual_departure": "08:05",
                "flexibility": 0.6,
            },
            {
                "user_id": "priya_002",
                "name": "Priya",
                "origin": "Thane",
                "destination": "CST",
                "line": "CR",
                "usual_train": "Thane Fast 08:22",
                "usual_departure": "08:22",
                "flexibility": 0.3,
            },
            {
                "user_id": "meena_003",
                "name": "Meena",
                "origin": "Dadar",
                "destination": "Churchgate",
                "line": "WR",
                "usual_train": "Churchgate Fast 09:10",
                "usual_departure": "09:10",
                "flexibility": 0.8,
            },
            {
                "user_id": "arjun_004",
                "name": "Arjun",
                "origin": "Bandra",
                "destination": "Andheri",
                "line": "WR",
                "usual_train": "Borivali Slow 08:30",
                "usual_departure": "08:30",
                "flexibility": 0.5,
            },
        ]

        for u in demo_users:
            session.run("""
                MERGE (user:User {user_id: $user_id})
                SET user.name = $name,
                    user.flexibility_score = $flexibility,
                    user.language_pref = 'hi'

                MERGE (route:Route {origin: $origin, destination: $destination})
                SET route.line = $line

                MERGE (train:Train {train_number: $usual_train})
                SET train.type = 'Fast',
                    train.line = $line

                MERGE (user)-[:HABITUALLY_TRAVELS]->(route)
                MERGE (route)-[:SERVED_BY]->(train)
                MERGE (train)-[:HAS_SLOT]->(:TimeSlot {
                    departure_time: $usual_departure,
                    day_type: 'weekday'
                })
            """, u)
            print(f"[schema] Created user: {u['name']} ({u['origin']} → {u['destination']})")

        # ── Sample Stations (Western Line) ─────────────────────
        wr_stations = [
            "Churchgate", "Marine Lines", "Charni Road", "Grant Road",
            "Mumbai Central", "Mahalaxmi", "Lower Parel", "Prabhadevi",
            "Dadar", "Matunga Road", "Mahim", "Bandra", "Khar Road",
            "Santacruz", "Vile Parle", "Andheri", "Jogeshwari",
            "Goregaon", "Malad", "Kandivali", "Borivali", "Dahisar",
            "Mira Road", "Bhayandar", "Naigaon", "Vasai Road",
            "Nallasopara", "Virar",
        ]
        for i, name in enumerate(wr_stations):
            session.run("""
                MERGE (s:Station {name: $name})
                SET s.line = 'WR', s.sequence = $seq
            """, {"name": name, "seq": i})

        # ── Sample Stations (Central Line) ─────────────────────
        cr_stations = [
            "CST", "Masjid", "Sandhurst Road", "Byculla", "Chinchpokli",
            "Currey Road", "Parel", "Dadar", "Matunga", "Sion",
            "Kurla", "Vidyavihar", "Ghatkopar", "Vikhroli", "Kanjurmarg",
            "Bhandup", "Nahur", "Mulund", "Thane", "Kalwa",
            "Mumbra", "Diva", "Kopar", "Dombivli", "Thakurli",
            "Kalyan",
        ]
        for i, name in enumerate(cr_stations):
            session.run("""
                MERGE (s:Station {name: $name})
                SET s.line = COALESCE(s.line, 'CR'), s.sequence = $seq
            """, {"name": name, "seq": i})

        print(f"[schema] Created {len(wr_stations)} WR + {len(cr_stations)} CR stations")
        print("[schema] Done! Neo4j is ready.")


if __name__ == "__main__":
    setup_schema()
