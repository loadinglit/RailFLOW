"""
RailFlow — Neo4j Seed Data Script
Generates 2500 realistic CrowdReport nodes for Mumbai local trains.
Covers 3 months (Dec 2025 → Feb 2026) with historically accurate patterns.
Reports have proper ISO timestamps, train metadata, and repeat-commuter user hashes.

Run: cd RailFLOW && uv run python backend/scripts/seed_crowd_data.py
"""

import os
import sys
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# Fix imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core import run_cypher, get_neo4j_driver

# ── TRAIN DATA ──────────────────────────────────────────────────────
# Morning southbound (to Churchgate/CST) + Evening northbound (from Churchgate/CST)

WESTERN_TRAINS = [
    # Morning southbound (peak 7-10am)
    {"number": "90001", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Virar",      "dest": "Churchgate", "depart": "05:05"},
    {"number": "90003", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Virar",      "dest": "Churchgate", "depart": "06:05"},
    {"number": "90005", "name": "Borivali Fast",  "type": "FAST",  "line": "WR", "origin": "Borivali",   "dest": "Churchgate", "depart": "06:12"},
    {"number": "90007", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Virar",      "dest": "Churchgate", "depart": "07:05"},
    {"number": "90009", "name": "Borivali Slow",  "type": "SLOW",  "line": "WR", "origin": "Borivali",   "dest": "Churchgate", "depart": "07:28"},
    {"number": "90011", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Virar",      "dest": "Churchgate", "depart": "07:52"},
    {"number": "90013", "name": "Borivali Fast",  "type": "FAST",  "line": "WR", "origin": "Borivali",   "dest": "Churchgate", "depart": "08:05"},
    {"number": "90015", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Virar",      "dest": "Churchgate", "depart": "08:18"},
    {"number": "90017", "name": "Borivali Slow",  "type": "SLOW",  "line": "WR", "origin": "Borivali",   "dest": "Churchgate", "depart": "08:32"},
    {"number": "90019", "name": "Andheri Slow",   "type": "SLOW",  "line": "WR", "origin": "Andheri",    "dest": "Churchgate", "depart": "08:45"},
    {"number": "90021", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Virar",      "dest": "Churchgate", "depart": "09:05"},
    {"number": "90033", "name": "Borivali Fast",  "type": "FAST",  "line": "WR", "origin": "Borivali",   "dest": "Churchgate", "depart": "09:28"},
    {"number": "90035", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Virar",      "dest": "Churchgate", "depart": "10:05"},
    {"number": "90037", "name": "Borivali Slow",  "type": "SLOW",  "line": "WR", "origin": "Borivali",   "dest": "Churchgate", "depart": "11:15"},
    {"number": "90039", "name": "Virar Slow",     "type": "SLOW",  "line": "WR", "origin": "Virar",      "dest": "Churchgate", "depart": "13:20"},
    {"number": "90041", "name": "Borivali Slow",  "type": "SLOW",  "line": "WR", "origin": "Borivali",   "dest": "Churchgate", "depart": "15:40"},
    # Evening northbound (peak 5-8pm)
    {"number": "90023", "name": "Borivali Fast",  "type": "FAST",  "line": "WR", "origin": "Churchgate", "dest": "Borivali",   "depart": "17:10"},
    {"number": "90025", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Churchgate", "dest": "Virar",      "depart": "17:35"},
    {"number": "90027", "name": "Borivali Fast",  "type": "FAST",  "line": "WR", "origin": "Churchgate", "dest": "Borivali",   "depart": "18:05"},
    {"number": "90029", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Churchgate", "dest": "Virar",      "depart": "18:22"},
    {"number": "90031", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Churchgate", "dest": "Virar",      "depart": "19:05"},
    {"number": "90043", "name": "Borivali Slow",  "type": "SLOW",  "line": "WR", "origin": "Churchgate", "dest": "Borivali",   "depart": "19:32"},
    {"number": "90045", "name": "Virar Fast",     "type": "FAST",  "line": "WR", "origin": "Churchgate", "dest": "Virar",      "depart": "20:05"},
    {"number": "90047", "name": "Borivali Slow",  "type": "SLOW",  "line": "WR", "origin": "Churchgate", "dest": "Borivali",   "depart": "21:10"},
]

CENTRAL_TRAINS = [
    # Morning southbound
    {"number": "11001", "name": "Kasara Fast",    "type": "FAST",  "line": "CR", "origin": "Kasara",     "dest": "CST",        "depart": "05:30"},
    {"number": "11003", "name": "Kalyan Fast",    "type": "FAST",  "line": "CR", "origin": "Kalyan",     "dest": "CST",        "depart": "06:15"},
    {"number": "11005", "name": "Thane Fast",     "type": "FAST",  "line": "CR", "origin": "Thane",      "dest": "CST",        "depart": "07:08"},
    {"number": "11007", "name": "Kalyan Fast",    "type": "FAST",  "line": "CR", "origin": "Kalyan",     "dest": "CST",        "depart": "07:45"},
    {"number": "11009", "name": "Thane Slow",     "type": "SLOW",  "line": "CR", "origin": "Thane",      "dest": "CST",        "depart": "08:02"},
    {"number": "11011", "name": "Kalyan Fast",    "type": "FAST",  "line": "CR", "origin": "Kalyan",     "dest": "CST",        "depart": "08:22"},
    {"number": "11013", "name": "Kurla Slow",     "type": "SLOW",  "line": "CR", "origin": "Kurla",      "dest": "CST",        "depart": "08:40"},
    {"number": "11015", "name": "Thane Fast",     "type": "FAST",  "line": "CR", "origin": "Thane",      "dest": "CST",        "depart": "09:10"},
    {"number": "11025", "name": "Dombivli Fast",  "type": "FAST",  "line": "CR", "origin": "Dombivli",   "dest": "CST",        "depart": "09:45"},
    {"number": "11027", "name": "Kalyan Slow",    "type": "SLOW",  "line": "CR", "origin": "Kalyan",     "dest": "CST",        "depart": "10:30"},
    {"number": "11029", "name": "Thane Slow",     "type": "SLOW",  "line": "CR", "origin": "Thane",      "dest": "CST",        "depart": "12:15"},
    {"number": "11031", "name": "Kalyan Slow",    "type": "SLOW",  "line": "CR", "origin": "Kalyan",     "dest": "CST",        "depart": "14:40"},
    # Evening northbound
    {"number": "11017", "name": "Kalyan Fast",    "type": "FAST",  "line": "CR", "origin": "CST",        "dest": "Kalyan",     "depart": "17:25"},
    {"number": "11019", "name": "Thane Fast",     "type": "FAST",  "line": "CR", "origin": "CST",        "dest": "Thane",      "depart": "18:10"},
    {"number": "11021", "name": "Kalyan Fast",    "type": "FAST",  "line": "CR", "origin": "CST",        "dest": "Kalyan",     "depart": "18:45"},
    {"number": "11023", "name": "Kasara Fast",    "type": "FAST",  "line": "CR", "origin": "CST",        "dest": "Kasara",     "depart": "19:15"},
    {"number": "11033", "name": "Dombivli Fast",  "type": "FAST",  "line": "CR", "origin": "CST",        "dest": "Dombivli",   "depart": "19:50"},
    {"number": "11035", "name": "Thane Slow",     "type": "SLOW",  "line": "CR", "origin": "CST",        "dest": "Thane",      "depart": "20:30"},
]

HARBOUR_TRAINS = [
    {"number": "21001", "name": "Panvel Fast",    "type": "FAST",  "line": "HR", "origin": "Panvel",     "dest": "CST",        "depart": "06:30"},
    {"number": "21003", "name": "Vashi Slow",     "type": "SLOW",  "line": "HR", "origin": "Vashi",      "dest": "CST",        "depart": "07:45"},
    {"number": "21005", "name": "Panvel Fast",    "type": "FAST",  "line": "HR", "origin": "Panvel",     "dest": "CST",        "depart": "08:15"},
    {"number": "21007", "name": "Belapur Fast",   "type": "FAST",  "line": "HR", "origin": "Belapur",    "dest": "CST",        "depart": "08:50"},
    {"number": "21013", "name": "Vashi Slow",     "type": "SLOW",  "line": "HR", "origin": "Vashi",      "dest": "CST",        "depart": "09:30"},
    {"number": "21009", "name": "Panvel Fast",    "type": "FAST",  "line": "HR", "origin": "CST",        "dest": "Panvel",     "depart": "17:50"},
    {"number": "21011", "name": "Vashi Fast",     "type": "FAST",  "line": "HR", "origin": "CST",        "dest": "Vashi",      "depart": "18:30"},
    {"number": "21015", "name": "Panvel Slow",    "type": "SLOW",  "line": "HR", "origin": "CST",        "dest": "Panvel",     "depart": "19:20"},
]

ALL_TRAINS = WESTERN_TRAINS + CENTRAL_TRAINS + HARBOUR_TRAINS

STATIONS = [
    # Western Line
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
    # Central Line
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
    # Harbour Line
    {"name": "Panvel",         "line": "HR", "zone": "outskirts"},
    {"name": "Vashi",          "line": "HR", "zone": "suburbs"},
    {"name": "Belapur",        "line": "HR", "zone": "suburbs"},
]


# ── COMMUTER POOL ────────────────────────────────────────────────────
# 200 repeat commuters — same person reports multiple times (realistic)

_COMMUTER_HASHES = [
    hashlib.md5(f"commuter_{i}".encode()).hexdigest()[:12]
    for i in range(200)
]


# ── CROWD PATTERN RULES ────────────────────────────────────────────

def get_crowd_distribution(train, day_type, hour):
    """
    Returns weighted distribution for RED/YELLOW/GREEN based on real Mumbai patterns.
    Patterns are calibrated to match Mumbai local train reality:
    - Virar Fast at 8am weekday = 70% RED (famous for being the most packed)
    - Slow locals = slightly less crowded than fast (fewer long-distance commuters)
    - Evening return = almost as crowded as morning
    - Sundays = mostly empty
    """
    t = train["name"]
    line = train["line"]
    h = int(hour.split(":")[0]) if isinstance(hour, str) else hour

    # ── Western Railway ──
    if line == "WR":
        # Virar Fast → Churchgate (morning): THE most crowded trains in Mumbai
        if "Virar" in t and train["dest"] == "Churchgate":
            if day_type == "weekday":
                if 7 <= h <= 9:     return {"RED": 72, "YELLOW": 22, "GREEN": 6}
                if h == 6:          return {"RED": 48, "YELLOW": 38, "GREEN": 14}
                if h == 5:          return {"RED": 15, "YELLOW": 35, "GREEN": 50}
                if 10 <= h <= 11:   return {"RED": 30, "YELLOW": 45, "GREEN": 25}
                return {"RED": 12, "YELLOW": 33, "GREEN": 55}
            if day_type == "saturday":
                if 8 <= h <= 10:    return {"RED": 38, "YELLOW": 42, "GREEN": 20}
                return {"RED": 12, "YELLOW": 35, "GREEN": 53}
            # Sunday
            return {"RED": 5, "YELLOW": 20, "GREEN": 75}

        # Borivali Fast → Churchgate: Very crowded but slightly less than Virar
        if "Borivali" in t and "Fast" in t and train["dest"] == "Churchgate":
            if day_type == "weekday":
                if 7 <= h <= 9:     return {"RED": 55, "YELLOW": 32, "GREEN": 13}
                if h == 6:          return {"RED": 30, "YELLOW": 45, "GREEN": 25}
                return {"RED": 10, "YELLOW": 35, "GREEN": 55}
            if day_type == "saturday":
                if 8 <= h <= 10:    return {"RED": 22, "YELLOW": 48, "GREEN": 30}
                return {"RED": 8, "YELLOW": 30, "GREEN": 62}
            return {"RED": 5, "YELLOW": 18, "GREEN": 77}

        # Borivali Slow → Churchgate: Slow locals = moderate crowd
        if "Borivali" in t and "Slow" in t and train["dest"] == "Churchgate":
            if day_type == "weekday":
                if 7 <= h <= 9:     return {"RED": 35, "YELLOW": 45, "GREEN": 20}
                return {"RED": 10, "YELLOW": 30, "GREEN": 60}
            return {"RED": 5, "YELLOW": 25, "GREEN": 70}

        # Andheri Slow: Short-distance = less packed
        if "Andheri" in t:
            if day_type == "weekday" and 8 <= h <= 9:
                return {"RED": 28, "YELLOW": 48, "GREEN": 24}
            return {"RED": 8, "YELLOW": 30, "GREEN": 62}

        # Evening return: Churchgate → Virar/Borivali
        if train["origin"] == "Churchgate":
            if "Virar" in train.get("dest", ""):
                if day_type == "weekday":
                    if 17 <= h <= 19:   return {"RED": 68, "YELLOW": 24, "GREEN": 8}
                    if h == 20:         return {"RED": 40, "YELLOW": 38, "GREEN": 22}
                    return {"RED": 10, "YELLOW": 30, "GREEN": 60}
                if day_type == "saturday" and 17 <= h <= 19:
                    return {"RED": 32, "YELLOW": 43, "GREEN": 25}
                return {"RED": 5, "YELLOW": 22, "GREEN": 73}
            if "Borivali" in train.get("dest", ""):
                if day_type == "weekday":
                    if 17 <= h <= 19:   return {"RED": 50, "YELLOW": 35, "GREEN": 15}
                    if h == 20:         return {"RED": 25, "YELLOW": 40, "GREEN": 35}
                    return {"RED": 8, "YELLOW": 28, "GREEN": 64}
                return {"RED": 5, "YELLOW": 25, "GREEN": 70}

    # ── Central Railway ──
    if line == "CR":
        # Kasara/Kalyan Fast → CST: Long-distance = packed
        if ("Kalyan" in t or "Kasara" in t) and "Fast" in t and train["dest"] == "CST":
            if day_type == "weekday":
                if 7 <= h <= 9:     return {"RED": 65, "YELLOW": 27, "GREEN": 8}
                if h == 6:          return {"RED": 35, "YELLOW": 42, "GREEN": 23}
                if 10 <= h <= 11:   return {"RED": 25, "YELLOW": 42, "GREEN": 33}
                return {"RED": 10, "YELLOW": 30, "GREEN": 60}
            if day_type == "saturday":
                if 8 <= h <= 10:    return {"RED": 28, "YELLOW": 47, "GREEN": 25}
                return {"RED": 8, "YELLOW": 32, "GREEN": 60}
            return {"RED": 5, "YELLOW": 22, "GREEN": 73}

        # Thane Fast → CST
        if "Thane" in t and "Fast" in t and train["dest"] == "CST":
            if day_type == "weekday":
                if 7 <= h <= 9:     return {"RED": 45, "YELLOW": 38, "GREEN": 17}
                return {"RED": 10, "YELLOW": 35, "GREEN": 55}
            return {"RED": 5, "YELLOW": 25, "GREEN": 70}

        # Slow locals on CR
        if "Slow" in t and train["dest"] == "CST":
            if day_type == "weekday" and 7 <= h <= 9:
                return {"RED": 30, "YELLOW": 45, "GREEN": 25}
            return {"RED": 8, "YELLOW": 28, "GREEN": 64}

        # Dombivli Fast
        if "Dombivli" in t and train["dest"] == "CST":
            if day_type == "weekday" and 9 <= h <= 10:
                return {"RED": 40, "YELLOW": 40, "GREEN": 20}
            return {"RED": 10, "YELLOW": 32, "GREEN": 58}

        # Kurla Slow: Short-distance
        if "Kurla" in t:
            return {"RED": 18, "YELLOW": 42, "GREEN": 40}

        # Evening return: CST → outskirts
        if train["origin"] == "CST":
            if day_type == "weekday":
                if 17 <= h <= 19:   return {"RED": 58, "YELLOW": 30, "GREEN": 12}
                if h == 20:         return {"RED": 32, "YELLOW": 40, "GREEN": 28}
                return {"RED": 8, "YELLOW": 28, "GREEN": 64}
            if day_type == "saturday" and 17 <= h <= 19:
                return {"RED": 25, "YELLOW": 42, "GREEN": 33}
            return {"RED": 5, "YELLOW": 22, "GREEN": 73}

    # ── Harbour Line ──
    if line == "HR":
        if train["dest"] == "CST":
            if day_type == "weekday":
                if 7 <= h <= 9:     return {"RED": 38, "YELLOW": 42, "GREEN": 20}
                return {"RED": 10, "YELLOW": 30, "GREEN": 60}
            return {"RED": 5, "YELLOW": 22, "GREEN": 73}
        if train["origin"] == "CST":
            if day_type == "weekday" and 17 <= h <= 19:
                return {"RED": 35, "YELLOW": 42, "GREEN": 23}
            return {"RED": 5, "YELLOW": 25, "GREEN": 70}

    # ── Fallback defaults ──
    if day_type == "sunday":
        return {"RED": 4, "YELLOW": 18, "GREEN": 78}
    if day_type == "saturday":
        return {"RED": 8, "YELLOW": 32, "GREEN": 60}
    return {"RED": 12, "YELLOW": 38, "GREEN": 50}


def weighted_choice(distribution):
    choices = list(distribution.keys())
    weights = list(distribution.values())
    return random.choices(choices, weights=weights, k=1)[0]


# ── REPORT GENERATION ─────────────────────────────────────────────────

def generate_reports(n=2500):
    """
    Generate n CrowdReports over 3 months (Dec 1, 2025 → Feb 28, 2026).
    - Peak hour trains get MORE reports (commuters report when it matters)
    - Weekdays get 5x more reports than Sundays
    - Recent week (Feb 22-28) has a slight crowd spike on WR Virar trains
      (to demonstrate trend detection)
    """
    reports = []
    start_date = datetime(2025, 12, 1)
    end_date = datetime(2026, 2, 28)
    total_days = (end_date - start_date).days

    # Build a weighted train pool — peak hour trains get more reports
    train_weights = []
    for t in ALL_TRAINS:
        h = int(t["depart"].split(":")[0])
        # Peak morning (7-9) and evening (17-19) get 3x weight
        if 7 <= h <= 9 or 17 <= h <= 19:
            w = 3.0
        elif 6 <= h <= 10 or 16 <= h <= 20:
            w = 2.0
        else:
            w = 1.0
        # FAST trains get reported more (more commuters)
        if t["type"] == "FAST":
            w *= 1.5
        train_weights.append(w)

    for i in range(n):
        # Pick a random date — bias toward weekdays
        while True:
            days_offset = random.randint(0, total_days)
            report_date = start_date + timedelta(days=days_offset)
            wd = report_date.weekday()
            # Weekdays: always keep. Saturday: 60% keep. Sunday: 30% keep.
            if wd < 5:
                break
            elif wd == 5 and random.random() < 0.60:
                break
            elif wd == 6 and random.random() < 0.30:
                break

        if wd == 6:
            day_type = "sunday"
        elif wd == 5:
            day_type = "saturday"
        else:
            day_type = "weekday"

        # Pick a train (weighted)
        train = random.choices(ALL_TRAINS, weights=train_weights, k=1)[0]

        # Report time: within ±20 min of train departure (commuters report near boarding)
        train_hour = int(train["depart"].split(":")[0])
        train_min = int(train["depart"].split(":")[1])
        offset_min = random.randint(-20, 20)
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

        hour_bucket = f"{train_hour:02d}:00-{(train_hour+1):02d}:00"
        dist = get_crowd_distribution(train, day_type, f"{train_hour:02d}:00")

        # TREND SPIKE: Last week of Feb, WR Virar trains get extra RED
        # (simulates a real-world surge — festival, exam season, etc.)
        if (report_date >= datetime(2026, 2, 22) and
            train["line"] == "WR" and "Virar" in train["name"] and
            day_type == "weekday"):
            # Push distribution more RED
            dist = {"RED": min(90, dist["RED"] + 20),
                    "YELLOW": max(5, dist["YELLOW"] - 10),
                    "GREEN": max(5, dist["GREEN"] - 10)}

        crowd_level = weighted_choice(dist)

        # Pick a repeat commuter (not unique per report — realistic)
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


# ── NEO4J INGESTION ─────────────────────────────────────────────────

def ingest_all():
    # Verify connection
    get_neo4j_driver()

    reports = generate_reports(2500)

    print("Clearing old data...")
    run_cypher("MATCH (n) DETACH DELETE n")

    print(f"Creating {len(STATIONS)} Station nodes...")
    for s in STATIONS:
        run_cypher("""
            MERGE (st:Station {name: $name})
            SET st.line = $line, st.zone = $zone
        """, {"name": s["name"], "line": s["line"], "zone": s["zone"]})

    print(f"Creating {len(ALL_TRAINS)} Train nodes...")
    seen = set()
    for t in ALL_TRAINS:
        if t["number"] not in seen:
            run_cypher("""
                MERGE (tr:Train {number: $number})
                SET tr.name = $name, tr.type = $type, tr.line = $line,
                    tr.origin = $origin, tr.destination = $dest, tr.depart = $depart
            """, {
                "number": t["number"], "name": t["name"], "type": t["type"],
                "line": t["line"], "origin": t["origin"], "dest": t["dest"],
                "depart": t["depart"],
            })
            seen.add(t["number"])

    # Batch insert reports (50 at a time for speed)
    print(f"Inserting {len(reports)} CrowdReport nodes...")
    batch_size = 50
    for batch_start in range(0, len(reports), batch_size):
        batch = reports[batch_start:batch_start + batch_size]
        for r in batch:
            run_cypher("""
                CREATE (cr:CrowdReport {
                    report_id:     $report_id,
                    train_number:  $train_number,
                    train_name:    $train_name,
                    train_type:    $train_type,
                    line:          $line,
                    origin:        $origin,
                    destination:   $destination,
                    timestamp:     $timestamp,
                    day_type:      $day_type,
                    hour_bucket:   $hour_bucket,
                    crowd_level:   $crowd_level,
                    user_hash:     $user_hash
                })
            """, r)

            run_cypher("""
                MATCH (tr:Train {number: $train_number})
                MATCH (cr:CrowdReport {report_id: $report_id})
                MERGE (cr)-[:REPORTS_ON]->(tr)
            """, {"train_number": r["train_number"], "report_id": r["report_id"]})

        done = min(batch_start + batch_size, len(reports))
        if done % 500 == 0 or done == len(reports):
            print(f"  ... {done}/{len(reports)} reports inserted")

    print("Creating indexes...")
    run_cypher("CREATE INDEX crowd_train IF NOT EXISTS FOR (c:CrowdReport) ON (c.train_number)")
    run_cypher("CREATE INDEX crowd_day IF NOT EXISTS FOR (c:CrowdReport) ON (c.day_type)")
    run_cypher("CREATE INDEX crowd_hour IF NOT EXISTS FOR (c:CrowdReport) ON (c.hour_bucket)")
    run_cypher("CREATE INDEX crowd_timestamp IF NOT EXISTS FOR (c:CrowdReport) ON (c.timestamp)")

    # Sanity check
    dist = run_cypher("""
        MATCH (cr:CrowdReport)
        RETURN cr.crowd_level AS level, count(*) AS total
        ORDER BY total DESC
    """)

    # Per-line breakdown
    line_dist = run_cypher("""
        MATCH (cr:CrowdReport)
        RETURN cr.line AS line, cr.crowd_level AS level, count(*) AS total
        ORDER BY cr.line, total DESC
    """)

    # Date range check
    date_range = run_cypher("""
        MATCH (cr:CrowdReport)
        RETURN min(cr.timestamp) AS earliest, max(cr.timestamp) AS latest
    """)

    print(f"\nSeed complete!")
    print(f"  Stations:     {len(STATIONS)}")
    print(f"  Trains:       {len(seen)}")
    print(f"  CrowdReports: {len(reports)}")

    if date_range:
        print(f"  Date range:   {date_range[0]['earliest'][:10]} → {date_range[0]['latest'][:10]}")

    print(f"\n  Overall distribution:")
    for row in dist:
        print(f"    {row['level']:8s}: {row['total']}")

    print(f"\n  Per-line breakdown:")
    for row in line_dist:
        print(f"    {row['line']} {row['level']:8s}: {row['total']}")


if __name__ == "__main__":
    ingest_all()
