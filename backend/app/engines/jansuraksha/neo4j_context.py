"""
Jan Suraksha Bot — Neo4j Context Loader.

Pulls user/train/station/line/disruption/language context
so the bot knows who the user is before they say anything.
"""

from app.core import run_cypher
from app.utils.logger import get_logger

log = get_logger("jansuraksha.neo4j")


def load_user_context(user_id: str) -> dict:
    """
    Load full user context from Neo4j Knowledge Graph.

    Returns dict with: name, origin, destination, line, usual_train,
    train_type, language_pref, previous_complaints, active_disruptions,
    station_details.
    """
    log.info("Loading user context for user_id=%s", user_id)

    results = run_cypher("""
        MATCH (u:User {user_id: $user_id})
        OPTIONAL MATCH (u)-[:HABITUALLY_TRAVELS]->(r:Route)
        OPTIONAL MATCH (r)-[:SERVED_BY]->(t:Train)
        OPTIONAL MATCH (u)-[:FILED]->(c:Complaint)
        OPTIONAL MATCH (t)-[:HAS_SLOT]->(ts:TimeSlot)
        RETURN u.name AS name,
               u.language_pref AS language_pref,
               u.flexibility_score AS flexibility_score,
               r.origin AS origin,
               r.destination AS destination,
               r.line AS line,
               t.train_number AS usual_train,
               t.type AS train_type,
               ts.departure_time AS usual_departure,
               count(DISTINCT c) AS previous_complaints
    """, {"user_id": user_id})

    if not results:
        log.warning("User %s NOT FOUND in Neo4j", user_id)
        return {"user_id": user_id, "found": False}

    ctx = results[0]
    ctx["user_id"] = user_id
    ctx["found"] = True
    log.info("User found: name=%s, route=%s→%s, line=%s, train=%s",
             ctx.get("name"), ctx.get("origin"), ctx.get("destination"),
             ctx.get("line"), ctx.get("usual_train"))

    # Check for active disruptions on user's line
    log.debug("Checking active disruptions for user %s", user_id)
    disruptions = run_cypher("""
        MATCH (u:User {user_id: $user_id})-[:HABITUALLY_TRAVELS]->(r:Route)
        OPTIONAL MATCH (d:DisruptionEvent)-[:AFFECTS]->(t:Train)-[:OPERATES_ON]->(:Line {name: r.line})
        WHERE d.active = true
        RETURN d.disruption_type AS disruption_type,
               d.station AS station,
               t.train_number AS affected_train
        LIMIT 5
    """, {"user_id": user_id})

    ctx["active_disruptions"] = [d for d in disruptions if d.get("disruption_type")]
    log.debug("Active disruptions: %d", len(ctx["active_disruptions"]))

    # Get station info for user's origin
    if ctx.get("origin"):
        stations = run_cypher("""
            MATCH (s:Station {name: $station})
            RETURN s.name AS name, s.line AS line, s.sequence AS sequence
        """, {"station": ctx["origin"]})
        ctx["origin_station"] = stations[0] if stations else None
        log.debug("Origin station info: %s", ctx.get("origin_station"))

    return ctx