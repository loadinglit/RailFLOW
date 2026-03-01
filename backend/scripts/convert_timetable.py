"""
Convert scraped timetable data → llm_timetable_raw.json format.

Now includes per-station stops for trains that have real data (Harbour, Trans-Harbour,
AC locals). Falls back to origin→dest only for WR/CR main line trains where
trainhelp.in doesn't provide intermediate station times.

Output: backend/data/llm_timetable_raw.json

Usage:
    python backend/scripts/convert_timetable.py
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SCRAPED_PATH = DATA_DIR / "scraped_timetable.json"
OUTPUT_PATH = DATA_DIR / "llm_timetable_raw.json"
TIMETABLE_PY = DATA_DIR / "mumbai_timetable.py"


# ─── Station name normalization ──────────────────────────────────

# Map trainhelp.in station names → our canonical names
STATION_ALIASES = {
    # Harbour Line
    "Mumbai CSMT": "CST",
    "Belapur CBD": "Belapur",
    "Mahim Jn": "Mahim",
    "King's Circle": "Kings Circle",
    "GTB Nagar": "GTB Nagar",
    "Seawood Darave": "Seawood",
    "Vileparle": "Vile Parle",
    # Trans-Harbour
    "TNA": "Thane",
    "DIGH": "Diva",
    "AIRL": "Airoli",
    "RABE": "Rabale",
    "GNSL": "Ghansoli",
    "KPHN": "Kopar Khairane",
    "TUH": "Turbhe",
    "SNPD": "Sanpada",
    "VSH": "Vashi",
    "JNJ": "Juinagar",
    "NEU": "Nerul",
    "SWDV": "Seawood",
    "BEPR": "Belapur",
    "KHAG": "Kharghar",
    "MANR": "Mansarovar",
    "KNDS": "Khandeshwar",
    "PNVL": "Panvel",
    # Port Line
    "NERUL": "Nerul",
    "SEAWOODS DARAVE": "Seawood",
    "BELAPUR": "Belapur",
    "BAMANDONGRI": "Bamandongri",
    "KHARKOPAR": "Kharkopar",
    "SHEMATIKHAR": "Shematikhar",
    "NHAVE-SHEVA": "Nhava Sheva",
    "DRONAGIRI": "Dronagiri",
    "URAN": "Uran",
    # CR
    "Church Gate": "Churchgate",
    "Thane": "Thane",
    "THANE": "Thane",
    "Vashi": "Vashi",
    "CSMT": "CST",
    "Kanjur Marg": "Kanjurmarg",
}


def normalize_station(name: str) -> str:
    """Normalize station name to canonical form."""
    name = name.strip()
    return STATION_ALIASES.get(name, name)


def normalize_stops(stops: dict) -> dict:
    """Normalize all station names in a stops dict."""
    return {normalize_station(k): v for k, v in stops.items()}


# ─── Time helpers ────────────────────────────────────────────────

def _parse_to_minutes(t: str) -> int:
    """Parse 'HH:MM' (24h) or 'HH:MM AM/PM' to minutes since midnight."""
    t = t.strip().upper().replace('.', ':')
    m = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', t)
    if m:
        h, mi, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
        if ampm == "AM" and h == 12:
            h = 0
        elif ampm == "PM" and h != 12:
            h += 12
        return h * 60 + mi
    m = re.match(r'(\d{1,2}):(\d{2})', t)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    return 0


def _minutes_to_12h(mins: int) -> str:
    """Convert minutes since midnight to '04:15 AM' format."""
    mins = mins % (24 * 60)
    h, m = mins // 60, mins % 60
    if h == 0:
        return f"12:{m:02d} AM"
    elif h < 12:
        return f"{h:02d}:{m:02d} AM"
    elif h == 12:
        return f"12:{m:02d} PM"
    else:
        return f"{h - 12:02d}:{m:02d} PM"


def _24h_to_12h(t: str) -> str:
    """Convert '05:20' to '05:20 AM'."""
    return _minutes_to_12h(_parse_to_minutes(t))


# ─── Data loading ────────────────────────────────────────────────

def load_scraped() -> list[dict]:
    with open(SCRAPED_PATH) as f:
        return json.load(f)


def extract_inline_arrays() -> dict[str, list[tuple]]:
    """Parse _RAW arrays from mumbai_timetable.py."""
    source = TIMETABLE_PY.read_text(encoding="utf-8")
    arrays = {}
    for m in re.finditer(
        r'^(_\w+_RAW)\s*=\s*\[(.*?)\]', source, re.MULTILINE | re.DOTALL
    ):
        tuples = []
        for tm in re.finditer(
            r'\(\s*"(\d+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)',
            m.group(2)
        ):
            tuples.append((tm.group(1), tm.group(2), tm.group(3), tm.group(4)))
        if tuples:
            arrays[m.group(1)] = tuples
    return arrays


def _inline_to_12h(raw: list[tuple]) -> list[tuple]:
    """Normalize inline tuple times to 12h format."""
    result = []
    for num, dep, arr, typ in raw:
        result.append((num, _24h_to_12h(dep), _24h_to_12h(arr), typ))
    return result


# ─── Route building ──────────────────────────────────────────────

def make_route(line, origin, dest, trains_data):
    """
    Build route entry. trains_data is list of:
      (number, dep_12h, arr_12h, type, stops_dict_or_None)
    Deduplicates by train number (keeps first occurrence).
    """
    trains = []
    seen = set()
    for num, dep, arr, typ, stops in trains_data:
        if num in seen:
            continue
        seen.add(num)
        entry = {"n": num, "d": dep, "a": arr, "t": typ}
        if stops:
            entry["stops"] = stops
        trains.append(entry)
    return {
        "line": line,
        "origin": origin,
        "destination": dest,
        "trains": trains,
    }


def main():
    scraped = load_scraped()
    inline = extract_inline_arrays()

    print(f"Scraped: {len(scraped)} trains")
    print(f"Inline arrays: {len(inline)}")
    for name, data in inline.items():
        print(f"  {name}: {len(data)} trains")

    output = {}

    # ── Harbour Line (real per-station data!) ──────────────────
    # HR = East branch (CST ↔ Panvel via Vashi)
    # HRW = West branch (CST ↔ Goregaon via Bandra)

    WEST_MARKERS = {"Andheri", "Bandra", "Mahim", "Goregaon", "Kings Circle",
                    "Khar Road", "Santacruz", "Vile Parle", "Jogeshwari", "Ramnagar"}

    hr_down = []      # CST → Panvel (east)
    hr_up = []        # Panvel → CST (east)
    hr_bel_down = []  # CST → Belapur (east, shorter runs)
    hr_bel_up = []    # Belapur/Nerul → CST (east, shorter runs)
    hrw_down = []     # CST → Goregaon (west)
    hrw_up = []       # Goregaon → CST (west)

    for t in scraped:
        if t["line"] != "HR" or not t.get("stops"):
            continue

        stops = normalize_stops(t["stops"])
        dep = _24h_to_12h(t["departure"])
        arr = _24h_to_12h(t["arrival"])
        origin = normalize_station(t["origin"])
        dest = normalize_station(t["destination"])

        entry = (t["number"], dep, arr, "SLOW", stops)

        # Classify by branch based on station presence
        is_west = bool(set(stops.keys()) & WEST_MARKERS)

        if is_west:
            # West branch: CST ↔ Goregaon via Bandra
            if t["direction"] == "DOWN":
                hrw_down.append(entry)
            else:
                hrw_up.append(entry)
        elif t["direction"] == "DOWN":
            if "Panvel" in dest:
                hr_down.append(entry)
            elif "Belapur" in stops:
                bel_time = _24h_to_12h(stops["Belapur"])
                hr_bel_down.append((t["number"], dep, bel_time, "SLOW", stops))
        elif t["direction"] == "UP":
            if "Panvel" in origin:
                hr_up.append(entry)
            elif "CST" in dest:
                hr_bel_up.append(entry)

    # Sort by departure time
    for lst in [hr_down, hr_up, hr_bel_down, hr_bel_up, hrw_down, hrw_up]:
        lst.sort(key=lambda x: _parse_to_minutes(x[1]))

    output["HR_CST_to_Panvel"] = make_route("HR", "CST", "Panvel", hr_down)
    output["HR_Panvel_to_CST"] = make_route("HR", "Panvel", "CST", hr_up)
    output["HR_CST_to_Belapur"] = make_route("HR", "CST", "Belapur", hr_bel_down)
    output["HR_Belapur_to_CST"] = make_route("HR", "Belapur", "CST", hr_bel_up)
    output["HRW_CST_to_Goregaon"] = make_route("HRW", "CST", "Goregaon", hrw_down)
    output["HRW_Goregaon_to_CST"] = make_route("HRW", "Goregaon", "CST", hrw_up)

    print(f"\nHR CST→Panvel: {len(hr_down)}, Panvel→CST: {len(hr_up)}")
    print(f"HR CST→Belapur: {len(hr_bel_down)}, Belapur→CST: {len(hr_bel_up)}")
    print(f"HRW CST→Goregaon: {len(hrw_down)}, Goregaon→CST: {len(hrw_up)}")

    # ── WR (from WR simple tables — origin→dest only) ─────────
    wr_down_raw = []  # Churchgate → Virar
    wr_up_raw = []    # Virar → Churchgate

    for t in scraped:
        if t["line"] != "WR" or t.get("stops"):
            continue

        dep = t["departure"]
        arr = t["arrival"]
        typ = t["type"]
        origin = normalize_station(t["origin"])
        dest = normalize_station(t["destination"])

        # Fix midnight crossing errors
        dep_min = _parse_to_minutes(dep)
        arr_min = _parse_to_minutes(arr)
        if dep_min >= 22 * 60 and arr_min >= 12 * 60 and arr_min <= 14 * 60:
            arr = arr.replace("PM", "AM")

        if origin == "Churchgate" and dest == "Virar":
            wr_down_raw.append((dep, arr, typ))
        elif origin == "Virar" and dest == "Churchgate":
            wr_up_raw.append((dep, arr, typ))

    wr_down_raw.sort(key=lambda x: _parse_to_minutes(x[0]))
    wr_up_raw.sort(key=lambda x: _parse_to_minutes(x[0]))

    # Assign sequential train numbers
    wr_down = [(str(90002 + i * 2), dep, arr, typ, None)
               for i, (dep, arr, typ) in enumerate(wr_down_raw)]
    wr_up = [(str(90001 + i * 2), dep, arr, typ, None)
             for i, (dep, arr, typ) in enumerate(wr_up_raw)]

    output["WR_Churchgate_to_Virar"] = make_route("WR", "Churchgate", "Virar", wr_down)
    output["WR_Virar_to_Churchgate"] = make_route("WR", "Virar", "Churchgate", wr_up)

    print(f"\nWR Churchgate→Virar: {len(wr_down)}, Virar→Churchgate: {len(wr_up)}")

    # ── CR (from inline arrays — real train numbers/times) ─────
    for key, array_name, line, origin, dest in [
        ("CR_Kalyan_to_CST", "_CR_KALYAN_TO_CST_RAW", "CR", "Kalyan", "CST"),
        ("CR_CST_to_Kalyan", "_CR_CST_TO_KALYAN_RAW", "CR", "CST", "Kalyan"),
    ]:
        if array_name not in inline:
            continue
        tuples = _inline_to_12h(inline[array_name])
        trains = [(n, d, a, t, None) for n, d, a, t in tuples]
        output[key] = make_route(line, origin, dest, trains)
        print(f"CR {origin}→{dest}: {len(trains)}")

    # ── Merge AC Local per-station data into CR/WR routes ──────
    # AC trains have real per-station stops — add them to the appropriate routes
    ac_trains = [t for t in scraped if t["type"] == "AC LOCAL" and t.get("stops")]
    ac_added = 0
    for t in ac_trains:
        stops = normalize_stops(t["stops"])
        origin = normalize_station(t["origin"])
        dest = normalize_station(t["destination"])
        dep = _24h_to_12h(t["departure"])
        arr = _24h_to_12h(t["arrival"])
        entry = (t["number"], dep, arr, "AC LOCAL", stops)

        # Determine which route this AC train belongs to
        if origin == "CST" and dest == "Kalyan":
            output.setdefault("CR_CST_to_Kalyan", make_route("CR", "CST", "Kalyan", []))
            output["CR_CST_to_Kalyan"]["trains"].append(
                {"n": t["number"], "d": dep, "a": arr, "t": "AC LOCAL", "stops": stops}
            )
            ac_added += 1
        elif origin in ("CST", "CSMT") and "Kalyan" in dest:
            output.setdefault("CR_CST_to_Kalyan", make_route("CR", "CST", "Kalyan", []))
            output["CR_CST_to_Kalyan"]["trains"].append(
                {"n": t["number"], "d": dep, "a": arr, "t": "AC LOCAL", "stops": stops}
            )
            ac_added += 1
        elif dest in ("CST", "CSMT", "Mumbai CSMT"):
            # UP direction — add to appropriate route
            if "Kalyan" in origin or "Thane" in origin or "Dombivli" in origin:
                output.setdefault("CR_Kalyan_to_CST", make_route("CR", "Kalyan", "CST", []))
                output["CR_Kalyan_to_CST"]["trains"].append(
                    {"n": t["number"], "d": dep, "a": arr, "t": "AC LOCAL", "stops": stops}
                )
                ac_added += 1
        elif origin == "Churchgate" or dest == "Churchgate":
            # WR AC trains
            if origin == "Churchgate":
                output.setdefault("WR_Churchgate_to_Virar", make_route("WR", "Churchgate", "Virar", []))
                output["WR_Churchgate_to_Virar"]["trains"].append(
                    {"n": t["number"], "d": dep, "a": arr, "t": "AC LOCAL", "stops": stops}
                )
                ac_added += 1
            else:
                output.setdefault("WR_Virar_to_Churchgate", make_route("WR", "Virar", "Churchgate", []))
                output["WR_Virar_to_Churchgate"]["trains"].append(
                    {"n": t["number"], "d": dep, "a": arr, "t": "AC LOCAL", "stops": stops}
                )
                ac_added += 1

    print(f"\nAC trains merged into routes: {ac_added}")

    # ── Write output ──────────────────────────────────────────
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    total = sum(len(r["trains"]) for r in output.values())
    with_stops = sum(
        1 for r in output.values()
        for t in r["trains"] if t.get("stops")
    )
    print(f"\n{'='*60}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Routes: {len(output)}")
    print(f"Total trains: {total}")
    print(f"With per-station stops: {with_stops}")
    print(f"Without (fallback to _compute_stops): {total - with_stops}")
    print(f"{'='*60}")
    for key, route in output.items():
        n = len(route["trains"])
        ns = sum(1 for t in route["trains"] if t.get("stops"))
        print(f"  {key:30s}: {n:>4} trains ({ns} with real stops)")


if __name__ == "__main__":
    main()
