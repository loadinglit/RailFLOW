"""
One-time script — Create demo users + routes in Neo4j so the bot and notifications work.
Run once: python backend/scripts/set_demo_emails.py
"""
import sys
sys.path.insert(0, "backend")

from app.core import run_cypher

DEMO_USERS = [
    {
        "user_id": "rahul_001",
        "name": "Rahul Patel",
        "email": "pateldhruvv2004@gmail.com",
        "language_pref": "en",
        "origin": "Virar",
        "destination": "Churchgate",
        "line": "WR",
        "usual_train": "Virar Fast",
        "train_type": "fast",
    },
    {
        "user_id": "priya_002",
        "name": "Priya Singh",
        "email": "singhbling2003@gmail.com",
        "language_pref": "hi",
        "origin": "Thane",
        "destination": "CST",
        "line": "CR",
        "usual_train": "Thane Fast",
        "train_type": "fast",
    },
    {
        "user_id": "meena_003",
        "name": "Meena Deshmukh",
        "email": "dhruvpatel150204@gmail.com",
        "language_pref": "mr",
        "origin": "Dadar",
        "destination": "Churchgate",
        "line": "WR",
        "usual_train": "Dadar Slow",
        "train_type": "slow",
    },
    {
        "user_id": "arjun_004",
        "name": "Arjun Sharma",
        "email": "dhruv.patel@valiancesolutions.com",
        "language_pref": "en",
        "origin": "Bandra",
        "destination": "Andheri",
        "line": "WR",
        "usual_train": "Andheri Fast",
        "train_type": "fast",
    },
]

for u in DEMO_USERS:
    result = run_cypher("""
        MERGE (user:User {user_id: $user_id})
        SET user.name = $name,
            user.email = $email,
            user.language_pref = $language_pref
        MERGE (route:Route {origin: $origin, destination: $destination, line: $line})
        MERGE (user)-[:HABITUALLY_TRAVELS]->(route)
        MERGE (train:Train {train_number: $usual_train, type: $train_type})
        MERGE (route)-[:SERVED_BY]->(train)
        RETURN user.user_id AS id, user.name AS name, user.email AS email
    """, u)

    if result:
        r = result[0]
        print(f"  {r['id']} ({r['name']}) -> {r['email']}")
    else:
        print(f"  {u['user_id']} — FAILED")

print("\nDone. All demo users created with routes and emails.")