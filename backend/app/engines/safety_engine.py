"""
Safety Intelligence Engine — Complaint-Driven Alerts + Police Analytics.

Closes the feedback loop:
  Complaints filed via Jan Suraksha Bot
  → Passenger safety alerts (AI advisory + stats)
  → Police analytics dashboard (charts + patrol recommendation)
"""

import logging
from app.db import get_db
from app.core import get_openai_client, MODEL_FAST

log = logging.getLogger(__name__)


def _hour_to_12h(h: int) -> str:
    """Convert 24h int to '2 PM' format."""
    if h == 0:
        return "12 AM"
    elif h < 12:
        return f"{h} AM"
    elif h == 12:
        return "12 PM"
    else:
        return f"{h - 12} PM"


def _compute_peak_window(hour_counts: dict) -> str:
    """
    Find the densest 1-3 hour cluster from complaint hour counts.
    Returns e.g. "2 PM - 4 PM" or "8 AM - 9 AM".
    """
    if not hour_counts:
        return "N/A"

    # Sort hours that have complaints
    active_hours = sorted(
        [(int(h), c) for h, c in hour_counts.items() if c > 0],
        key=lambda x: x[1],
        reverse=True,
    )
    if not active_hours:
        return "N/A"

    # Start from the hour with most complaints
    peak_h = active_hours[0][0]

    # Expand to adjacent hours if they also have complaints (max 3h window)
    window_start = peak_h
    window_end = peak_h + 1

    # Check hour before
    prev_h = str((peak_h - 1) % 24).zfill(2)
    if hour_counts.get(prev_h, 0) > 0:
        window_start = (peak_h - 1) % 24

    # Check hour after
    next_h = str((peak_h + 1) % 24).zfill(2)
    if hour_counts.get(next_h, 0) > 0:
        window_end = (peak_h + 2) % 24
    else:
        window_end = (peak_h + 1) % 24

    return f"{_hour_to_12h(window_start)} - {_hour_to_12h(window_end)}"


# ── Passenger: Recent Alerts ─────────────────────────────────────

def get_recent_alerts(language: str = "en") -> dict:
    """
    Get recent complaint patterns for passenger safety card.
    Returns: { has_alerts, advisory, stats }
    """
    try:
        db = get_db()
        rows = db.execute("""
            SELECT incident_type, severity, date_filed,
                   strftime('%H', date_filed) as hour,
                   from_station
            FROM complaints
            WHERE date_filed >= datetime('now', '-24 hours')
            ORDER BY date_filed DESC
        """).fetchall()
        incidents = [dict(r) for r in rows]
        db.close()
    except Exception as e:
        log.error("[safety] DB query failed: %s", e)
        return {"has_alerts": False, "advisory": "", "stats": None}

    if not incidents:
        return {"has_alerts": False, "advisory": "", "stats": None}

    # Aggregate by type, hour, and station
    type_counts = {}
    hour_counts = {}
    station_counts = {}
    for inc in incidents:
        t = inc["incident_type"] or "general"
        type_counts[t] = type_counts.get(t, 0) + 1
        h = inc.get("hour") or "00"
        hour_counts[h] = hour_counts.get(h, 0) + 1
        stn = inc.get("from_station")
        if stn:
            station_counts[stn] = station_counts.get(stn, 0) + 1

    top_type = max(type_counts, key=type_counts.get)
    peak_window = _compute_peak_window(hour_counts)

    # Top stations sorted by count
    top_stations = sorted(station_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    stats = {
        "count": len(incidents),
        "top_type": top_type,
        "top_type_count": type_counts[top_type],
        "peak_window": peak_window,
        "type_breakdown": type_counts,
        "stations": [{"name": s, "count": c} for s, c in top_stations],
        "details": [
            f"{type_counts[t]} {t} report{'s' if type_counts[t] > 1 else ''}"
            for t in sorted(type_counts, key=type_counts.get, reverse=True)
        ],
    }

    # 1 LLM call — advisory in user's language
    advisory = _generate_advisory(stats, language)

    return {"has_alerts": True, "advisory": advisory, "stats": stats}


def _generate_advisory(stats: dict, language: str) -> str:
    """Generate a 2-sentence actionable safety tip. 1 LLM call."""
    lang_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(language, "English")

    # Station info for the prompt
    stations = stats.get("stations", [])
    if stations:
        station_str = ", ".join(f"{s['name']} ({s['count']})" for s in stations[:3])
    else:
        station_str = "various stations on the route"

    prompt = f"""You are a Mumbai local train safety advisor.

Recent complaints (last 24 hours): {stats['count']} total
Breakdown: {', '.join(stats['details'])}
Peak window: {stats['peak_window']}
Top crime: {stats['top_type']} ({stats['top_type_count']} reports)
Reported at: {station_str}

Generate a 2-sentence ACTIONABLE safety tip in {lang_name}:
- Mention the specific crime type and count
- Mention the peak time window
- If station names are available, mention them — ONLY stations from the data above
- Give one concrete action (e.g. "keep phone in inner pocket", "avoid door area", "travel in groups")
- Sound like a caring local friend, not a robot
- Do NOT use generic "stay safe" — be SPECIFIC about the data above
- Do NOT invent station names not listed above"""

    try:
        client = get_openai_client()
        resp = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
            max_tokens=150,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log.error("[safety] Advisory LLM call failed: %s", e)
        # Fallback — rule-based advisory
        return f"{stats['top_type_count']} {stats['top_type']} reports in the last 24 hours (peak: {stats['peak_window']}). Please keep your belongings secure."


# ── Police: Analytics Dashboard ──────────────────────────────────

def get_analytics() -> dict:
    """Aggregate complaint data for police analytics dashboard."""
    try:
        db = get_db()

        by_type = db.execute("""
            SELECT incident_type, COUNT(*) as count
            FROM complaints GROUP BY incident_type
            ORDER BY count DESC
        """).fetchall()

        by_status = db.execute("""
            SELECT status, COUNT(*) as count
            FROM complaints GROUP BY status
        """).fetchall()

        by_severity = db.execute("""
            SELECT severity, COUNT(*) as count
            FROM complaints GROUP BY severity
            ORDER BY CASE severity
                WHEN 'critical' THEN 1 WHEN 'high' THEN 2
                WHEN 'medium' THEN 3 WHEN 'low' THEN 4 ELSE 5 END
        """).fetchall()

        by_hour = db.execute("""
            SELECT strftime('%H', date_filed) as hour, COUNT(*) as count
            FROM complaints GROUP BY hour ORDER BY hour
        """).fetchall()

        this_week = db.execute("""
            SELECT COUNT(*) as count FROM complaints
            WHERE date_filed >= datetime('now', '-7 days')
        """).fetchone()["count"]

        last_week = db.execute("""
            SELECT COUNT(*) as count FROM complaints
            WHERE date_filed >= datetime('now', '-14 days')
            AND date_filed < datetime('now', '-7 days')
        """).fetchone()["count"]

        total = db.execute(
            "SELECT COUNT(*) as count FROM complaints"
        ).fetchone()["count"]

        recent = db.execute("""
            SELECT ref, incident_type, severity, status, date_filed
            FROM complaints ORDER BY date_filed DESC LIMIT 5
        """).fetchall()

        # Station hotspots — count incidents per station
        by_station = db.execute("""
            SELECT from_station, COUNT(*) as count
            FROM complaints
            WHERE from_station IS NOT NULL AND from_station != ''
            GROUP BY from_station
            ORDER BY count DESC
        """).fetchall()

        db.close()
    except Exception as e:
        log.error("[safety] Analytics DB query failed: %s", e)
        return {
            "total_complaints": 0, "by_type": [], "by_status": [],
            "by_severity": [], "by_hour": [], "this_week": 0,
            "last_week": 0, "trend": "stable", "recent": [],
            "patrol_recommendation": "Database unavailable.",
        }

    by_type_list = [dict(r) for r in by_type]
    by_hour_list = [dict(r) for r in by_hour]
    by_station_list = [dict(r) for r in by_station]

    # AI patrol recommendation (1 LLM call)
    patrol_rec = _generate_patrol_recommendation(
        by_type_list, by_hour_list, by_station_list, this_week
    )

    trend = "up" if this_week > last_week else (
        "down" if this_week < last_week else "stable"
    )

    return {
        "total_complaints": total,
        "by_type": by_type_list,
        "by_status": [dict(r) for r in by_status],
        "by_severity": [dict(r) for r in by_severity],
        "by_hour": by_hour_list,
        "by_station": by_station_list,
        "this_week": this_week,
        "last_week": last_week,
        "trend": trend,
        "recent": [dict(r) for r in recent],
        "patrol_recommendation": patrol_rec,
    }


def _generate_patrol_recommendation(
    by_type: list[dict], by_hour: list[dict],
    by_station: list[dict], this_week: int,
) -> str:
    """Generate AI patrol deployment recommendation. 1 LLM call."""
    if not by_type:
        return "No complaint data yet. Analytics will appear as complaints are filed."

    top_crime = by_type[0]["incident_type"]
    top_count = by_type[0]["count"]

    # Compute peak window in AM/PM format
    hour_map = {h["hour"]: h["count"] for h in by_hour}
    peak_window = _compute_peak_window(hour_map)

    # Station data — real stations from complaints or "no station data"
    if by_station:
        station_str = ", ".join(
            f"{s['from_station']} ({s['count']} reports)" for s in by_station[:5]
        )
    else:
        station_str = "No specific station data available"

    prompt = f"""You are a Mumbai Railway Police intelligence advisor.

Data from complaint database:
- Total this week: {this_week} complaints
- Top crime: {top_crime} ({top_count} reports)
- Crime types: {', '.join(f"{r['incident_type']}({r['count']})" for r in by_type[:5])}
- Peak window: {peak_window}
- Reported stations: {station_str}

Generate a 2-3 sentence patrol deployment recommendation:
- Mention the peak time window ({peak_window})
- If station data is available, mention ONLY those specific stations from the data above — do NOT add any other stations
- If no station data, say "across the network" instead of guessing station names
- What officers should look for based on the top crime type ({top_crime})

CRITICAL: ONLY mention stations that appear in "Reported stations" above. Do NOT invent or guess any station names."""

    try:
        client = get_openai_client()
        resp = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log.error("[safety] Patrol LLM call failed: %s", e)
        return f"Top crime: {top_crime} ({top_count} reports). Peak hour: {peak_hour}:00. Deploy additional patrols during this window."