"""
RailFlow — Crowd Intelligence Engine

Computes crowd badges for Mumbai local trains using 3 signals:
  1. Historical crowd reports from Neo4j (weight: 50%)
  2. Crowd Trend Detection — recent vs baseline (weight: 30%)
  3. OpenWeatherMap live weather (weight: 20%)

Badge output: GREEN (Safe) | YELLOW (Caution) | RED (Avoid)
"""

import os
from datetime import datetime, timedelta

import httpx

from app.core import run_cypher, get_openai_client, get_neo4j_driver, MODEL_FAST

# ── API Keys ──────────────────────────────────────────────────────
WEATHER_KEY = os.getenv("OPENWEATHERMAP_KEY", "")


# ── Helpers ───────────────────────────────────────────────────────

def get_day_type(dt: datetime) -> str:
    w = dt.weekday()
    if w == 6:
        return "sunday"
    if w == 5:
        return "saturday"
    return "weekday"


def get_hour_bucket(dt: datetime) -> str:
    h = dt.hour
    return f"{h:02d}:00-{(h+1):02d}:00"


# ── Signal 1: Historical Crowd Score (Neo4j) ─────────────────────

def get_historical_crowd_score(train_number: str, day_type: str, hour_bucket: str) -> dict:
    """
    Queries Neo4j for past CrowdReports for this train x day_type x hour_bucket.
    Returns weighted score 0-100 and total report count.
    """
    results = run_cypher("""
        MATCH (cr:CrowdReport {
            train_number: $train_number,
            day_type: $day_type,
            hour_bucket: $hour_bucket
        })
        RETURN
            count(cr) as total,
            sum(CASE WHEN cr.crowd_level = 'RED'    THEN 1 ELSE 0 END) as red,
            sum(CASE WHEN cr.crowd_level = 'YELLOW' THEN 1 ELSE 0 END) as yellow,
            sum(CASE WHEN cr.crowd_level = 'GREEN'  THEN 1 ELSE 0 END) as green
    """, {
        "train_number": train_number,
        "day_type": day_type,
        "hour_bucket": hour_bucket,
    })

    row = results[0] if results else None
    if not row or row["total"] == 0:
        return {
            "score": 40, "total": 0, "confidence": "low",
            "description": "No historical data — using defaults",
        }

    total = row["total"]
    red_pct = row["red"] / total
    yellow_pct = row["yellow"] / total
    green_pct = row["green"] / total

    # Weighted score: RED=100, YELLOW=50, GREEN=0
    score = int(red_pct * 100 + yellow_pct * 50 + green_pct * 0)
    confidence = "high" if total >= 10 else "medium" if total >= 4 else "low"

    if score >= 70:
        desc = f"Historically very crowded ({int(red_pct*100)}% of {total} reports say packed)"
    elif score >= 40:
        desc = f"Moderately crowded based on {total} past reports"
    else:
        desc = f"Usually comfortable — {int(green_pct*100)}% of {total} reports say spacious"

    return {
        "score": score,
        "total": total,
        "confidence": confidence,
        "description": desc,
        "breakdown": {"red": row["red"], "yellow": row["yellow"], "green": row["green"]},
    }


# ── Signal 2: Crowd Trend Detection ──────────────────────────────

def get_crowd_trend_score(train_number: str, day_type: str, hour_bucket: str) -> dict:
    """
    Compares recent crowd reports (last 7 days) vs all-time baseline
    for the same train + day_type + hour_bucket.

    If recent reports are MORE RED than the historical average → trending worse (score ↑)
    If recent reports are MORE GREEN than average → trending better (score ↓)
    If no recent data → neutral (score 30, slight caution)
    """
    # Recent window: last 7 days
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()

    # Get ALL-TIME baseline for this train/day/hour
    baseline = run_cypher("""
        MATCH (cr:CrowdReport {
            train_number: $train_number,
            day_type: $day_type,
            hour_bucket: $hour_bucket
        })
        RETURN
            count(cr) as total,
            sum(CASE WHEN cr.crowd_level = 'RED'    THEN 1 ELSE 0 END) as red,
            sum(CASE WHEN cr.crowd_level = 'YELLOW' THEN 1 ELSE 0 END) as yellow,
            sum(CASE WHEN cr.crowd_level = 'GREEN'  THEN 1 ELSE 0 END) as green
    """, {
        "train_number": train_number,
        "day_type": day_type,
        "hour_bucket": hour_bucket,
    })

    # Get RECENT reports (last 7 days)
    recent = run_cypher("""
        MATCH (cr:CrowdReport {
            train_number: $train_number,
            day_type: $day_type,
            hour_bucket: $hour_bucket
        })
        WHERE cr.timestamp >= $cutoff
        RETURN
            count(cr) as total,
            sum(CASE WHEN cr.crowd_level = 'RED'    THEN 1 ELSE 0 END) as red,
            sum(CASE WHEN cr.crowd_level = 'YELLOW' THEN 1 ELSE 0 END) as yellow,
            sum(CASE WHEN cr.crowd_level = 'GREEN'  THEN 1 ELSE 0 END) as green
    """, {
        "train_number": train_number,
        "day_type": day_type,
        "hour_bucket": hour_bucket,
        "cutoff": cutoff,
    })

    b_row = baseline[0] if baseline else None
    r_row = recent[0] if recent else None

    # No data at all → neutral
    if not b_row or b_row["total"] == 0:
        return {
            "score": 30, "trend": "unknown",
            "description": "No trend data — using default caution",
            "recent_reports": 0, "baseline_reports": 0,
        }

    b_total = b_row["total"]
    b_red_pct = b_row["red"] / b_total

    # No recent data → slight caution (can't confirm improvement)
    if not r_row or r_row["total"] == 0:
        return {
            "score": 25, "trend": "stable",
            "description": f"No recent reports — baseline shows {int(b_red_pct*100)}% packed",
            "recent_reports": 0, "baseline_reports": b_total,
        }

    r_total = r_row["total"]
    r_red_pct = r_row["red"] / r_total
    r_yellow_pct = r_row["yellow"] / r_total

    # Trend = how much worse recent is vs baseline
    red_shift = r_red_pct - b_red_pct  # positive = worsening

    if red_shift > 0.20:
        # 20%+ more RED reports recently → major spike
        score = 85
        trend = "spiking"
        desc = f"Crowd surge detected — {int(r_red_pct*100)}% packed reports this week vs {int(b_red_pct*100)}% average"
    elif red_shift > 0.10:
        score = 60
        trend = "worsening"
        desc = f"Crowding up — {int(r_red_pct*100)}% packed vs {int(b_red_pct*100)}% usual"
    elif red_shift > -0.05:
        # Within normal range
        score = 30
        trend = "stable"
        desc = f"Normal pattern — {r_total} reports this week match baseline"
    elif red_shift > -0.15:
        score = 10
        trend = "improving"
        desc = f"Less crowded lately — only {int(r_red_pct*100)}% packed vs {int(b_red_pct*100)}% usual"
    else:
        score = 0
        trend = "clear"
        desc = f"Significantly less crowded — {int(r_red_pct*100)}% packed vs {int(b_red_pct*100)}% usual"

    return {
        "score": score,
        "trend": trend,
        "description": desc,
        "recent_reports": r_total,
        "baseline_reports": b_total,
    }


# ── Signal 3: Weather Score ──────────────────────────────────────

async def get_weather_score(city: str = "Mumbai") -> dict:
    """Returns weather condition + crowd score contribution (0-100)."""
    if WEATHER_KEY:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={"q": city, "appid": WEATHER_KEY, "units": "metric"},
                )
                data = r.json()
                rain = data.get("rain", {}).get("1h", 0)
                weather_id = data["weather"][0]["id"]
                main = data["weather"][0]["main"]

                if rain > 10 or weather_id < 300:
                    return {"condition": "heavy_rain", "score": 80,
                            "description": f"Heavy rain ({rain:.1f}mm/hr) — expect +30% crowd"}
                elif rain > 2 or 300 <= weather_id < 600:
                    return {"condition": "rain", "score": 45,
                            "description": "Rain — moderate crowd increase expected"}
                else:
                    return {"condition": "clear", "score": 0,
                            "description": f"{main} — no weather impact"}
        except Exception:
            pass

    # Simulated: Feb/Mar Mumbai is dry season, so mostly clear
    now = datetime.now()
    month = now.month
    if month in (6, 7, 8, 9):  # monsoon
        return {"condition": "rain", "score": 45,
                "description": "Monsoon season — moderate crowd increase expected"}
    else:
        return {"condition": "clear", "score": 0,
                "description": "Clear skies — no weather impact"}


# ── Badge Computation ────────────────────────────────────────────

def compute_final_badge(hist_score: int, trend_score: int, weather_score: int) -> dict:
    """Combines three signals into final badge."""
    if weather_score > 0:
        final = (hist_score * 0.50) + (trend_score * 0.30) + (weather_score * 0.20)
    else:
        final = (hist_score * 0.60) + (trend_score * 0.40)
    final = round(final)

    if final >= 70:
        return {"badge": "RED", "label": "Avoid", "color": "#EF4444", "score": final}
    elif final >= 40:
        return {"badge": "YELLOW", "label": "Caution", "color": "#F59E0B", "score": final}
    else:
        return {"badge": "GREEN", "label": "Safe", "color": "#22C55E", "score": final}


# ── Recent Report Consensus ─────────────────────────────────────

MIN_REPORTS_TO_SHIFT = 2  # badge only changes if 2+ users agree

def get_recent_report_counts(train_number: str, hour_bucket: str) -> dict:
    """
    Count crowd reports in the last 1 hour for this train.
    Returns {"RED": n, "YELLOW": n, "GREEN": n, "total": n}.
    """
    cutoff = (datetime.now() - timedelta(hours=1)).isoformat()

    results = run_cypher("""
        MATCH (cr:CrowdReport {
            train_number: $train_number,
            hour_bucket: $hour_bucket
        })
        WHERE cr.timestamp >= $cutoff
        RETURN
            count(cr) as total,
            sum(CASE WHEN cr.crowd_level = 'RED'    THEN 1 ELSE 0 END) as red,
            sum(CASE WHEN cr.crowd_level = 'YELLOW' THEN 1 ELSE 0 END) as yellow,
            sum(CASE WHEN cr.crowd_level = 'GREEN'  THEN 1 ELSE 0 END) as green
    """, {"train_number": train_number, "hour_bucket": hour_bucket, "cutoff": cutoff})

    row = results[0] if results else None
    if not row:
        return {"RED": 0, "YELLOW": 0, "GREEN": 0, "total": 0}
    return {
        "RED": row["red"], "YELLOW": row["yellow"], "GREEN": row["green"],
        "total": row["total"],
    }


def apply_badge_threshold(baseline_badge: dict, live_badge: dict,
                          recent_counts: dict) -> dict:
    """
    Only allow the badge to change from baseline if 2+ recent reports
    agree on the direction. Prevents one user from flipping a badge.

    Checks the DOMINANT reported level (what users actually tapped),
    not the computed badge level.
    """
    if baseline_badge["badge"] == live_badge["badge"]:
        return live_badge  # no change — no threshold needed

    # Find what level users are actually reporting most
    dominant = max(["RED", "YELLOW", "GREEN"],
                   key=lambda l: recent_counts.get(l, 0))
    dominant_count = recent_counts.get(dominant, 0)

    if dominant_count >= MIN_REPORTS_TO_SHIFT:
        return live_badge  # 2+ users agree — allow the change

    # Not enough consensus — keep the baseline badge
    return baseline_badge


# ── Reason Generation ────────────────────────────────────────────

async def generate_reason(train: dict, badge: dict, hist: dict,
                          trend: dict, weather: dict, day_type: str) -> str:
    """
    Produces a single-sentence reason for the badge.
    Falls back to rule-based reason if LLM is unavailable.
    """
    # Rule-based fallback (always works)
    reasons = []
    if trend.get("trend") in ("spiking", "worsening"):
        reasons.append(trend["description"].split("—")[-1].strip().lower())
    if weather["condition"] in ["rain", "heavy_rain"]:
        reasons.append(weather["description"].split("—")[0].strip().lower())
    if hist["total"] > 0:
        reasons.append(hist["description"].lower())
    if day_type == "weekday" and not reasons:
        reasons.append("weekday peak hour pattern")

    if badge["badge"] == "RED":
        base = f"Avoid — {' + '.join(reasons[:2]) if reasons else 'historically very crowded'}."
    elif badge["badge"] == "YELLOW":
        base = f"Moderate — {' + '.join(reasons[:2]) if reasons else 'some crowding expected'}."
    else:
        base = f"Usually comfortable{' — ' + reasons[0] if reasons else ''}."

    try:
        client = get_openai_client()

        tone_guide = {
            "GREEN": "This train is SAFE and comfortable. Say something positive — easy ride, low crowd, good option.",
            "YELLOW": "This train has MODERATE crowd. Mention slight crowding or minor delays, but still manageable.",
            "RED": "This train is DANGEROUS to board. Warn about heavy crowd, packed coaches, or serious delays.",
        }

        response = client.chat.completions.create(
            model=MODEL_FAST,
            max_tokens=40,
            messages=[{
                "role": "system",
                "content": (
                    "You write ONE sentence (max 12 words) about a Mumbai local train's crowd level. "
                    "Sound like a local friend giving advice. No emojis. "
                    f"IMPORTANT — the badge is {badge['badge']}. {tone_guide.get(badge['badge'], '')} "
                    "Your sentence MUST match this tone. Never contradict the badge."
                ),
            }, {
                "role": "user",
                "content": (
                    f"Train: {train.get('name', '')} ({train.get('type', '')}). "
                    f"Day: {day_type}. Crowd trend: {trend.get('trend', 'stable')}. "
                    f"Weather: {weather['condition']}. "
                    f"Reports: {hist['total']}. Write one sentence matching {badge['badge']} badge."
                ),
            }],
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return base


# ── Train Search ─────────────────────────────────────────────────

# Station lists ordered: outskirts → terminus (index 0 = farthest, last = terminus)
_WR_STATIONS = [
    "Virar", "Nala Sopara", "Vasai Road", "Bhayander", "Mira Road",
    "Dahisar", "Borivali", "Kandivali", "Malad", "Goregaon",
    "Ram Mandir", "Jogeshwari", "Andheri", "Vile Parle", "Santacruz",
    "Khar Road", "Bandra", "Mahim", "Matunga Road", "Dadar",
    "Prabhadevi", "Elphinstone", "Lower Parel", "Mahalaxmi",
    "Mumbai Central", "Grant Road", "Churchgate",
]
_CR_STATIONS = [
    "Kasara", "Karjat", "Kalyan", "Dombivli", "Thane", "Mulund",
    "Bhandup", "Vikhroli", "Ghatkopar", "Vidyavihar", "Kurla",
    "Sion", "Matunga", "Dadar", "Byculla", "Sandhurst Road",
    "Masjid", "CST",
]
_HR_STATIONS = ["Panvel", "Vashi", "Belapur", "Kurla", "CST"]


def _station_index(name: str, stations: list) -> int:
    t = name.strip().title()
    return stations.index(t) if t in stations else -1


def get_trains_for_route(origin: str, destination: str, dt: datetime) -> list:
    """
    Returns up to 10 trains for the route, filtered by time window.
    Uses static timetable with per-station departure times.
    """
    from data.mumbai_timetable import search_trains

    from_dt = dt - timedelta(minutes=5)
    until_dt = dt + timedelta(hours=3)
    search_from = f"{from_dt.hour:02d}:{from_dt.minute:02d}"
    search_until = f"{until_dt.hour:02d}:{until_dt.minute:02d}"
    wraps_midnight = until_dt.day != dt.day

    return search_trains(
        origin=origin,
        destination=destination,
        from_time=search_from,
        until_time=search_until,
        wraps_midnight=wraps_midnight,
        limit=10,
    )


def get_total_reports_for_route(origin: str, destination: str) -> int:
    """Total crowd reports on this route — used for 'helped X commuters' count."""
    results = run_cypher("""
        MATCH (cr:CrowdReport)
        WHERE cr.origin = $origin OR cr.destination = $destination
        RETURN count(cr) as total
    """, {"origin": origin, "destination": destination})

    row = results[0] if results else None
    return row["total"] if row else 0


# ── Store Crowd Report ───────────────────────────────────────────

def store_crowd_report(
    report_id: str,
    train_number: str,
    train_name: str,
    line: str,
    origin: str,
    destination: str,
    crowd_level: str,
    user_hash: str,
) -> None:
    """Store a user's crowd report in Neo4j."""
    now = datetime.now()
    day_type = get_day_type(now)
    hour_bucket = get_hour_bucket(now)

    run_cypher("""
        CREATE (cr:CrowdReport {
            report_id:     $report_id,
            train_number:  $train_number,
            train_name:    $train_name,
            line:          $line,
            origin:        $origin,
            destination:   $destination,
            timestamp:     $timestamp,
            day_type:      $day_type,
            hour_bucket:   $hour_bucket,
            crowd_level:   $crowd_level,
            delay_minutes: 0,
            user_hash:     $user_hash
        })
    """, {
        "report_id": report_id,
        "train_number": train_number,
        "train_name": train_name,
        "line": line,
        "origin": origin,
        "destination": destination,
        "timestamp": now.isoformat(),
        "day_type": day_type,
        "hour_bucket": hour_bucket,
        "crowd_level": crowd_level,
        "user_hash": user_hash,
    })

    # Link to Train node
    run_cypher("""
        MATCH (tr:Train {number: $train_number})
        MATCH (cr:CrowdReport {report_id: $report_id})
        MERGE (cr)-[:REPORTS_ON]->(tr)
    """, {"train_number": train_number, "report_id": report_id})
