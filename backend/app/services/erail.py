"""
erail.in API client — fetches real Mumbai local train timetables.

Register for a free API key at https://api.erail.in
Set ERAIL_API_KEY in your .env file.
"""

import os
import time
from datetime import datetime

import httpx

ERAIL_API_KEY = os.getenv("ERAIL_API_KEY", "")

# ── Station name → erail.in station code ──────────────────────────
_STATION_CODES = {
    # Western Railway
    "Virar": "VR",
    "Nala Sopara": "NSP",
    "Vasai Road": "BSR",
    "Bhayander": "BYR",
    "Mira Road": "MIRA",
    "Dahisar": "DIC",
    "Borivali": "BVI",
    "Kandivali": "KILE",
    "Malad": "MDD",
    "Goregaon": "GMN",
    "Ram Mandir": "RMR",
    "Jogeshwari": "JOS",
    "Andheri": "ADH",
    "Vile Parle": "VLP",
    "Santacruz": "STC",
    "Khar Road": "KHR",
    "Bandra": "BA",
    "Mahim": "MM",
    "Matunga Road": "MTR",
    "Dadar": "DDR",
    "Prabhadevi": "PBD",
    "Elphinstone": "EPR",
    "Lower Parel": "LPR",
    "Mahalaxmi": "MX",
    "Mumbai Central": "BCT",
    "Grant Road": "GTR",
    "Churchgate": "CCG",
    # Central Railway
    "Kasara": "KSRA",
    "Karjat": "KJT",
    "Kalyan": "KYN",
    "Dombivli": "DI",
    "Thane": "TNA",
    "Mulund": "MLND",
    "Bhandup": "BND",
    "Vikhroli": "VK",
    "Ghatkopar": "GC",
    "Vidyavihar": "VVH",
    "Kurla": "CLA",
    "Sion": "SIN",
    "Matunga": "MTN",
    "Byculla": "BY",
    "Sandhurst Road": "SNRD",
    "Masjid": "MSD",
    "CST": "CSMT",
    # Harbour line
    "Panvel": "PNVL",
    "Vashi": "VSHI",
    "Belapur": "BLPR",
}

# ── erail.in type → RailFLOW type mapping ─────────────────────────
_TYPE_MAP = {
    "LOCAL": "SLOW",
    "SEMI FAST": "FAST",
    "FAST": "FAST",
    "AC LOCAL": "AC",
    "AC SEMI FAST": "AC",
    "LADIES SPECIAL": "SLOW",
}


def _map_type(erail_type: str) -> str:
    return _TYPE_MAP.get(erail_type.upper().strip(), "SLOW")


# ── In-memory cache (6-hour TTL) ─────────────────────────────────
_cache: dict[str, tuple[float, list]] = {}
_CACHE_TTL = 6 * 3600  # 6 hours


def _cache_key(from_code: str, to_code: str) -> str:
    return f"{from_code}:{to_code}"


def _get_cached(key: str) -> list | None:
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < _CACHE_TTL:
            return data
        del _cache[key]
    return None


def _set_cache(key: str, data: list) -> None:
    _cache[key] = (time.time(), data)


# ── API call ──────────────────────────────────────────────────────

async def fetch_trains_from_erail(
    origin: str,
    destination: str,
) -> list | None:
    """
    Fetch real train timetable from erail.in.
    Returns list of dicts with keys: number, name, type, erail_type, line,
    origin, destination, depart, arrive, duration.
    Returns None on failure (caller should fall back to Neo4j).
    """
    if not ERAIL_API_KEY:
        return None

    from_code = _STATION_CODES.get(origin.strip().title())
    to_code = _STATION_CODES.get(destination.strip().title())
    if not from_code or not to_code:
        return None

    # Check cache
    key = _cache_key(from_code, to_code)
    cached = _get_cached(key)
    if cached is not None:
        return cached

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "http://api.erail.in/trains/",
                params={
                    "key": ERAIL_API_KEY,
                    "stn_from": from_code,
                    "stn_to": to_code,
                    "date": datetime.now().strftime("%d-%m-%Y"),
                },
            )
            if r.status_code != 200:
                return None

            data = r.json()

        trains_raw = data.get("trains") or data.get("data") or []
        if not trains_raw:
            return None

        # Detect line from station codes
        wr_codes = {"VR", "NSP", "BSR", "BYR", "MIRA", "DIC", "BVI", "KILE",
                     "MDD", "GMN", "RMR", "JOS", "ADH", "VLP", "STC", "KHR",
                     "BA", "MM", "MTR", "DDR", "PBD", "EPR", "LPR", "MX",
                     "BCT", "GTR", "CCG"}
        hr_codes = {"PNVL", "VSHI", "BLPR"}

        if from_code in wr_codes or to_code in wr_codes:
            line = "WR"
        elif from_code in hr_codes or to_code in hr_codes:
            line = "HR"
        else:
            line = "CR"

        results = []
        for t in trains_raw:
            train_number = str(t.get("number") or t.get("train_number") or "")
            erail_type = str(t.get("type") or t.get("train_type") or "LOCAL")
            depart = str(t.get("departure") or t.get("depart") or t.get("dep") or "")
            arrive = str(t.get("arrival") or t.get("arrive") or t.get("arr") or "")
            duration = str(t.get("duration") or t.get("travel_time") or "")
            name = str(t.get("name") or t.get("train_name") or f"{origin} {erail_type}")

            # Normalise depart/arrive to HH:MM
            if depart and len(depart) >= 4:
                depart = depart[:5]  # "06:15:00" → "06:15"
            if arrive and len(arrive) >= 4:
                arrive = arrive[:5]

            results.append({
                "number": train_number,
                "name": name,
                "type": _map_type(erail_type),
                "erail_type": erail_type.strip(),
                "line": line,
                "origin": origin.strip().title(),
                "destination": destination.strip().title(),
                "depart": depart,
                "arrive": arrive,
                "duration": duration,
            })

        _set_cache(key, results)
        return results

    except Exception:
        return None
