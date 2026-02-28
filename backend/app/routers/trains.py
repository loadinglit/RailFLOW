"""
RailFlow — Train Search & Crowd Report Router

POST /trains/search  → returns trains with crowd badges
POST /crowd/report   → stores a user's crowd tap
"""

import random
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.engines.crowd_engine import (
    get_day_type,
    get_hour_bucket,
    get_historical_crowd_score,
    get_crowd_trend_score,
    get_weather_score,
    compute_final_badge,
    generate_reason,
    get_trains_for_route,
    get_total_reports_for_route,
    store_crowd_report,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    origin: str
    destination: str
    datetime_str: str  # "2026-02-28T08:00:00"


class CrowdReportRequest(BaseModel):
    train_number: str
    train_name: str
    line: str
    origin: str
    destination: str
    crowd_level: str  # "RED" | "YELLOW" | "GREEN"
    user_hash: str


# ── Search Endpoint ──────────────────────────────────────────────

@router.post("/search")
async def search_trains(req: SearchRequest):
    """
    Main endpoint. Returns trains on route with crowd badges.
    Each train has: number, name, type, line, depart, badge, score, reason, signals
    """
    try:
        dt = datetime.fromisoformat(req.datetime_str)
    except ValueError:
        raise HTTPException(400, "Invalid datetime format. Use ISO8601: 2026-02-28T08:00:00")

    day_type = get_day_type(dt)

    # Fetch trains from Neo4j
    trains = get_trains_for_route(req.origin, req.destination, dt)
    if not trains:
        return {"trains": [], "message": "No trains found for this route"}

    # Fetch shared signals (weather is the same for all trains)
    weather = await get_weather_score()

    results = []
    for train in trains:
        train_num = train.get("number", "")

        # Use the TRAIN's departure hour for crowd lookup (not the search time)
        train_depart = train.get("depart", "08:00")
        depart_hour = int(train_depart.split(":")[0])
        train_hour_bucket = f"{depart_hour:02d}:00-{(depart_hour+1):02d}:00"

        # Per-train signals
        hist = get_historical_crowd_score(train_num, day_type, train_hour_bucket)
        trend = get_crowd_trend_score(train_num, day_type, train_hour_bucket)
        badge = compute_final_badge(hist["score"], trend["score"], weather["score"])
        reason = await generate_reason(train, badge, hist, trend, weather, day_type)

        results.append({
            "train_number": train_num,
            "train_name": train.get("name"),
            "train_type": train.get("type"),
            "line": train.get("line"),
            "origin": train.get("origin"),
            "destination": train.get("destination"),
            "depart": train.get("depart"),
            "platform": random.randint(1, 6),
            "badge": badge["badge"],
            "badge_label": badge["label"],
            "badge_color": badge["color"],
            "badge_score": badge["score"],
            "reason": reason,
            "signals": {
                "historical": hist,
                "crowd_trend": trend,
                "weather": weather,
            },
            "report_count": hist["total"],
        })

    # Sort: safest first (GREEN -> YELLOW -> RED), then by departure time
    order = {"GREEN": 0, "YELLOW": 1, "RED": 2}
    results.sort(key=lambda x: (order.get(x["badge"], 1), x["depart"] or ""))

    return {
        "origin": req.origin,
        "destination": req.destination,
        "datetime": req.datetime_str,
        "day_type": day_type,
        "trains": results,
        "total_route_reports": get_total_reports_for_route(req.origin, req.destination),
    }


# ── Crowd Report Endpoint ────────────────────────────────────────

@router.post("/report")
async def submit_crowd_report(req: CrowdReportRequest):
    """
    Stores a user's crowd tap. Returns updated badge so UI can refresh live.
    """
    now = datetime.now()
    day_type = get_day_type(now)
    hour_bucket = get_hour_bucket(now)
    report_id = f"RPT_{now.strftime('%Y%m%d%H%M%S')}_{req.user_hash[:6]}"

    store_crowd_report(
        report_id=report_id,
        train_number=req.train_number,
        train_name=req.train_name,
        line=req.line,
        origin=req.origin,
        destination=req.destination,
        crowd_level=req.crowd_level,
        user_hash=req.user_hash,
    )

    # Return updated crowd stats so badge refreshes live
    updated = get_historical_crowd_score(req.train_number, day_type, hour_bucket)
    trend = get_crowd_trend_score(req.train_number, day_type, hour_bucket)
    badge = compute_final_badge(updated["score"], trend["score"], 0)
    total_route = get_total_reports_for_route(req.origin, req.destination)

    return {
        "success": True,
        "message": f"Thanks. You just helped {total_route} commuters on this route.",
        "updated_badge": badge["badge"],
        "updated_score": badge["score"],
        "updated_stats": updated,
    }
