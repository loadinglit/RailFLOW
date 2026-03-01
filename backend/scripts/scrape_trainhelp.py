"""
Scrape real Mumbai local train timetable data from trainhelp.in.

Extracts per-station times from:
  - Harbour Line grid tables (CSMT↔Panvel, 736 trains, 35 stations)
  - Trans-Harbour grid tables (Thane→Panvel, 131 trains, 17 stations)
  - AC Local per-train tables (108 trains with full station stops)
  - Port Line tables (40 trains, 9 stations)
  - WR simple tables (245 trains, origin→dest only)
  - CR/WR list items (origin→dest only)

Output: backend/data/scraped_timetable.json with per-station stops for each train.

Usage:
    python backend/scripts/scrape_trainhelp.py --dump     # Phase 1: dump HTML
    python backend/scripts/scrape_trainhelp.py             # Phase 2: extract from dumps
    python backend/scripts/scrape_trainhelp.py --live      # Fetch + extract
"""

import argparse
import json
import re
import time
from pathlib import Path

PAGES = {
    "wr_main": "https://www.trainhelp.in/churchgate-to-virar-virar-to-churchgate-local-train-time-table/",
    "trans_harbour": "https://www.trainhelp.in/thane-vashi-mumbai-local-train-time-table/",
    "ac_local": "https://www.trainhelp.in/mumbai-local-ac-train/",
    "hub": "https://www.trainhelp.in/mumbai-local-train-time-table/",
}

DATA_DIR = Path(__file__).parent.parent / "data"
DUMP_DIR = DATA_DIR / "trainhelp_dumps"


# ─── Utility ────────────────────────────────────────────────────

def _strip(s: str) -> str:
    """Remove HTML tags and decode entities."""
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace('&nbsp;', ' ').replace('&amp;', '&')
    s = s.replace('&#8211;', '-').replace('\xa0', ' ')
    return s.strip()


def _is_time(s: str) -> bool:
    """Check if string looks like a time value."""
    return bool(re.match(r'\d{1,2}[:.]\d{2}', s.strip()))


def _norm_time_24h(raw: str) -> str:
    """Normalize to 'HH:MM' 24-hour format."""
    raw = raw.strip().replace('.', ':')
    m = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?', raw)
    if not m:
        return raw
    h, mi = int(m.group(1)), int(m.group(2))
    ampm = (m.group(3) or '').upper()
    if ampm == 'PM' and h != 12:
        h += 12
    elif ampm == 'AM' and h == 12:
        h = 0
    return f"{h:02d}:{mi:02d}"


def _norm_time_12h(raw: str) -> str:
    """Normalize to '04:15 AM' format."""
    raw = raw.strip().replace('.', ':')
    m = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)', raw)
    if m:
        h, mi, ampm = int(m.group(1)), m.group(2), m.group(3).upper()
        return f"{h:02d}:{mi} {ampm}"
    # Try 24h
    m = re.match(r'(\d{1,2}):(\d{2})', raw)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if h == 0:
            return f"12:{mi:02d} AM"
        elif h < 12:
            return f"{h:02d}:{mi:02d} AM"
        elif h == 12:
            return f"12:{mi:02d} PM"
        else:
            return f"{h - 12:02d}:{mi:02d} PM"
    return raw


def _norm_type(raw: str) -> str:
    """Normalize train type."""
    raw = raw.upper().strip()
    if "AC" in raw:
        return "AC LOCAL"
    if raw in ("F", "FAST"):
        return "FAST"
    if raw in ("S", "SLOW"):
        return "SLOW"
    if "SEMI" in raw or "SF" in raw:
        return "SEMI FAST"
    return "SLOW"


# ─── Phase 1: Dump HTML ─────────────────────────────────────────

def dump_html():
    from playwright.sync_api import sync_playwright
    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for name, url in PAGES.items():
            print(f"[dump] {name}: {url}")
            try:
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle", timeout=15000)
                time.sleep(2)
                html = page.content()
                (DUMP_DIR / f"trainhelp_{name}.html").write_text(html, encoding="utf-8")
                print(f"  -> {len(html):,} bytes")
            except Exception as e:
                print(f"  -> ERROR: {e}")
        browser.close()


# ─── Harbour Line grid tables (batched format) ──────────────────

def parse_harbour_grids(html: str) -> list[dict]:
    """
    Parse Harbour Line grid tables (tablepress-1141 to 1145).
    These have a batched structure:
      - "Stations" row with train numbers in columns
      - Empty row
      - 35 station rows with times per train
      - Repeat
    """
    results = []
    table_ids = ["tablepress-1141", "tablepress-1142", "tablepress-1143",
                 "tablepress-1144", "tablepress-1145"]

    for tid in table_ids:
        m = re.search(
            rf'<table id="{tid}"[^>]*>(.*?)</table>', html, re.DOTALL
        )
        if not m:
            continue
        table_html = m.group(1)

        # Determine direction from table ID
        # 1141-1143 = Down (CSMT→Panvel), 1144-1145 = Up (Panvel→CSMT)
        is_down = tid in ("tablepress-1141", "tablepress-1142", "tablepress-1143")

        # Get all rows
        rows = re.findall(r'<tr class="row-\d+">(.*?)</tr>', table_html, re.DOTALL)

        current_trains = []  # list of train numbers for current batch
        station_data = []    # list of (station_name, [time_per_train])
        batch_count = 0

        for row_html in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if not cells:
                continue

            first_cell = _strip(cells[0])

            # Detect "Stations" header row = start of new batch
            if first_cell.upper().startswith("STATION"):
                # Flush previous batch
                if current_trains and station_data:
                    results.extend(
                        _build_trains_from_grid(current_trains, station_data, tid, is_down)
                    )
                    batch_count += 1

                # Parse train numbers from header columns
                current_trains = []
                for cell in cells[1:]:
                    text = _strip(cell)
                    num_match = re.search(r'(\d{5})', text)
                    if num_match:
                        current_trains.append(num_match.group(1))
                    else:
                        current_trains.append("")
                station_data = []
                continue

            # Skip separator/empty rows
            if not first_cell or first_cell.upper().startswith("HARBOUR"):
                continue

            # Station data row
            station_name = first_cell
            times = []
            for cell in cells[1:]:
                t = _strip(cell)
                if _is_time(t):
                    times.append(_norm_time_24h(t))
                else:
                    times.append("")  # train doesn't stop here
            station_data.append((station_name, times))

        # Flush last batch
        if current_trains and station_data:
            results.extend(
                _build_trains_from_grid(current_trains, station_data, tid, is_down)
            )
            batch_count += 1

        print(f"  [Harbour] {tid}: {batch_count} batches, direction={'DOWN' if is_down else 'UP'}")

    print(f"  [Harbour] Total: {len(results)} trains with per-station stops")
    return results


def _build_trains_from_grid(train_nums, station_data, source, is_down):
    """Build train dicts from a grid batch."""
    trains = []
    for col_idx, train_num in enumerate(train_nums):
        if not train_num:
            continue

        stops = {}
        first_station = first_time = None
        last_station = last_time = None

        for station_name, times in station_data:
            if col_idx < len(times) and times[col_idx]:
                stops[station_name] = times[col_idx]
                if first_station is None:
                    first_station = station_name
                    first_time = times[col_idx]
                last_station = station_name
                last_time = times[col_idx]

        if first_station and last_station and first_station != last_station and len(stops) >= 2:
            trains.append({
                "number": train_num,
                "origin": first_station,
                "destination": last_station,
                "departure": first_time,
                "arrival": last_time,
                "type": "SLOW",
                "stops": stops,
                "source": f"hub/{source}",
                "line": "HR",
                "direction": "DOWN" if is_down else "UP",
            })
    return trains


# ─── Trans-Harbour grid tables (connected-cells format) ─────────

def parse_trans_harbour_grids(html: str) -> list[dict]:
    """Parse Trans-Harbour grid tables (tablepress-661, 740, etc.)."""
    results = []

    for m in re.finditer(
        r'<table id="(tablepress-\d+)"[^>]*class="[^"]*connected-cells[^"]*"[^>]*>(.*?)</table>',
        html, re.DOTALL
    ):
        tid = m.group(1)
        table_html = m.group(2)

        # Skip Harbour tables (already handled)
        if tid in ("tablepress-1141", "tablepress-1142", "tablepress-1143",
                    "tablepress-1144", "tablepress-1145"):
            continue

        # Parse header for train numbers
        thead = re.search(r'<thead>(.*?)</thead>', table_html, re.DOTALL)
        if not thead:
            continue
        header_cells = re.findall(r'<th[^>]*>(.*?)</th>', thead.group(1), re.DOTALL)
        if len(header_cells) < 2:
            continue

        train_nums = []
        for cell in header_cells[1:]:
            text = _strip(cell)
            num_match = re.search(r'(\d{5})', text)
            train_nums.append(num_match.group(1) if num_match else "")

        # Parse station rows
        station_data = []
        body_rows = re.findall(r'<tr class="row-\d+">(.*?)</tr>', table_html, re.DOTALL)
        for row_html in body_rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if not cells:
                continue
            station = _strip(cells[0])
            if not station or station.upper().startswith("TRAIN"):
                continue
            times = []
            for cell in cells[1:]:
                t = _strip(cell)
                times.append(_norm_time_24h(t) if _is_time(t) else "")
            station_data.append((station, times))

        # Build trains
        for col_idx, train_num in enumerate(train_nums):
            if not train_num:
                continue
            stops = {}
            first_station = first_time = last_station = last_time = None
            for station, times in station_data:
                if col_idx < len(times) and times[col_idx]:
                    stops[station] = times[col_idx]
                    if first_station is None:
                        first_station = station
                        first_time = times[col_idx]
                    last_station = station
                    last_time = times[col_idx]

            if first_station and last_station and first_station != last_station and len(stops) >= 2:
                results.append({
                    "number": train_num,
                    "origin": first_station,
                    "destination": last_station,
                    "departure": first_time,
                    "arrival": last_time,
                    "type": "SLOW",
                    "stops": stops,
                    "source": f"hub/{tid}",
                    "line": "TH",
                    "direction": "DOWN",
                })

        print(f"  [Trans-Harbour] {tid}: {len(train_nums)} trains")

    print(f"  [Trans-Harbour] Total: {len(results)} trains with per-station stops")
    return results


# ─── Port Line tables ───────────────────────────────────────────

def parse_port_line(html: str) -> list[dict]:
    """Parse Port Line tables (tablepress-1092, 1093)."""
    results = []
    for tid, direction in [("tablepress-1092", "DOWN"), ("tablepress-1093", "UP")]:
        m = re.search(rf'<table id="{tid}"[^>]*>(.*?)</table>', html, re.DOTALL)
        if not m:
            continue
        table_html = m.group(1)

        # These are regular tables with station names as row headers
        # and train times in columns
        thead = re.search(r'<thead>(.*?)</thead>', table_html, re.DOTALL)
        if not thead:
            continue

        header_cells = re.findall(r'<th[^>]*>(.*?)</th>', thead.group(1), re.DOTALL)
        train_nums = []
        for cell in header_cells[1:]:
            text = _strip(cell)
            num_match = re.search(r'(\d{5})', text)
            train_nums.append(num_match.group(1) if num_match else "")

        station_data = []
        body_rows = re.findall(r'<tr class="row-\d+">(.*?)</tr>', table_html, re.DOTALL)
        for row_html in body_rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if not cells:
                continue
            station = _strip(cells[0])
            if not station:
                continue
            times = []
            for cell in cells[1:]:
                t = _strip(cell)
                times.append(_norm_time_24h(t) if _is_time(t) else "")
            station_data.append((station, times))

        for col_idx, train_num in enumerate(train_nums):
            if not train_num:
                continue
            stops = {}
            first_station = first_time = last_station = last_time = None
            for station, times in station_data:
                if col_idx < len(times) and times[col_idx]:
                    stops[station] = times[col_idx]
                    if first_station is None:
                        first_station = station
                        first_time = times[col_idx]
                    last_station = station
                    last_time = times[col_idx]

            if first_station and last_station and first_station != last_station:
                results.append({
                    "number": train_num,
                    "origin": first_station,
                    "destination": last_station,
                    "departure": first_time,
                    "arrival": last_time,
                    "type": "SLOW",
                    "stops": stops,
                    "source": f"hub/{tid}",
                    "line": "PORT",
                    "direction": direction,
                })

    print(f"  [Port Line] {len(results)} trains with per-station stops")
    return results


# ─── AC Local per-train tables ──────────────────────────────────

def parse_ac_trains(html: str) -> list[dict]:
    """Parse AC local page — each train has an h4 heading + station table."""
    results = []

    # Split by h4 headings
    sections = re.split(r'(?=<h4[^>]*>)', html)

    for section in sections:
        # Extract heading
        h4 = re.search(r'<h4[^>]*>(.*?)</h4>', section, re.DOTALL)
        if not h4:
            continue
        heading = _strip(h4.group(1))
        num_match = re.search(r'(\d{5})', heading)
        if not num_match:
            continue
        train_num = num_match.group(1)

        # Determine line from heading
        line = "CR"
        if any(w in heading.upper() for w in ["CHURCHGATE", "VIRAR", "BORIVALI", "ANDHERI"]):
            line = "WR"

        # Extract origin/dest from <li> items
        origin = dep_time = dest = arr_time = None
        for li in re.finditer(r'<li>(.*?)</li>', section):
            li_text = _strip(li.group(1))
            m = re.search(r'Starting\s+from\s+([\w\s]+?)\s+at\s+([\d.:]+)', li_text, re.I)
            if m:
                origin = m.group(1).strip()
                dep_time = _norm_time_24h(m.group(2))
            m = re.search(r'Ending\s+at\s+([\w\s]+?)\s+at\s+([\d.:]+)', li_text, re.I)
            if m:
                dest = m.group(1).strip()
                arr_time = _norm_time_24h(m.group(2))

        # Extract per-station times from the table
        stops = {}
        table = re.search(r'<table[^>]*>(.*?)</table>', section, re.DOTALL)
        if table:
            rows = re.findall(r'<tr>(.*?)</tr>', table.group(1), re.DOTALL)
            for row in rows:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if len(cells) >= 2:
                    station = _strip(cells[0])
                    time_val = _strip(cells[1])
                    if station and _is_time(time_val) and station.lower() not in ("station", "time"):
                        stops[station] = _norm_time_24h(time_val)

            # Handle degenerate format: all stations in one cell with <br>
            if not stops and len(rows) >= 2:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', rows[-1] if len(rows) > 1 else rows[0], re.DOTALL)
                if len(cells) >= 2:
                    stations = [_strip(s) for s in cells[0].split('<br')]
                    times = [_strip(t) for t in cells[1].split('<br')]
                    for s, t in zip(stations, times):
                        s = re.sub(r'[/>]', '', s).strip()
                        t = re.sub(r'[/>]', '', t).strip()
                        if s and _is_time(t) and s.lower() not in ("station", "time"):
                            stops[s] = _norm_time_24h(t)

        if not origin or not dest:
            # Try to get from stops
            if stops:
                stop_list = list(stops.items())
                origin = origin or stop_list[0][0]
                dep_time = dep_time or stop_list[0][1]
                dest = dest or stop_list[-1][0]
                arr_time = arr_time or stop_list[-1][1]
            else:
                continue

        results.append({
            "number": train_num,
            "origin": origin,
            "destination": dest,
            "departure": dep_time,
            "arrival": arr_time,
            "type": "AC LOCAL",
            "stops": stops,
            "source": "ac_local",
            "line": line,
            "direction": "",
        })

    print(f"  [AC Local] {len(results)} trains, {sum(1 for r in results if r['stops'])} with per-station stops")
    return results


# ─── WR simple tables (origin→dest only) ────────────────────────

def parse_wr_simple(html: str) -> list[dict]:
    """Parse WR Churchgate↔Virar simple tables (no per-station data)."""
    results = []
    for m in re.finditer(
        r'<table id="(tablepress-\d+)"[^>]*>(.*?)</table>', html, re.DOTALL
    ):
        tid = m.group(1)
        table_html = m.group(2)
        if "connected-cells" in m.group(0):
            continue

        thead = re.search(r'<thead>(.*?)</thead>', table_html, re.DOTALL)
        if not thead:
            continue
        headers = [_strip(h) for h in re.findall(r'<th[^>]*>(.*?)</th>', thead.group(1))]
        if len(headers) < 2:
            continue

        origin_name = headers[0].split('(')[0].strip()
        dest_name = headers[1].split('(')[0].strip()
        has_type = len(headers) >= 3

        data_rows = re.findall(r'<tr class="row-\d+">(.*?)</tr>', table_html, re.DOTALL)
        for row_html in data_rows:
            cells = [_strip(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', row_html)]
            if len(cells) < 2 or not _is_time(cells[0]):
                continue
            raw_type = cells[2] if len(cells) > 2 and has_type else "S"
            results.append({
                "number": "",
                "origin": origin_name,
                "destination": dest_name,
                "departure": _norm_time_12h(cells[0]),
                "arrival": _norm_time_12h(cells[1]),
                "type": _norm_type(raw_type),
                "stops": {},
                "source": f"wr_main/{tid}",
                "line": "WR",
                "direction": "",
            })

    print(f"  [WR Simple] {len(results)} trains (origin→dest only, no per-station)")
    return results


# ─── CR/WR list items (origin→dest only) ────────────────────────

def parse_list_items(html: str) -> list[dict]:
    """Parse <li> elements with train data from hub page."""
    results = []
    for li in re.finditer(r'<li>(.*?)</li>', html, re.DOTALL):
        text = _strip(li.group(1))
        if "Train No" not in text:
            continue

        num_match = re.search(r'Train No\.?\s*(\d{5})', text)
        if not num_match:
            num_match = re.search(r'Train No\.?\s*\w+\s+(\d{5})', text)
        if not num_match:
            continue
        train_num = num_match.group(1)

        origin = dep = dest = arr = None
        m = re.search(r'(?:Starting|start)\s+from\s+([\w\s]+?)\s+at\s+([\d.:]+)', text, re.I)
        if m:
            origin, dep = m.group(1).strip(), m.group(2).replace('.', ':')
        if not origin:
            m = re.search(r'From\s+([\w\s]+?)\s+at\s+([\d.:]+)', text, re.I)
            if m:
                origin, dep = m.group(1).strip(), m.group(2).replace('.', ':')

        m = re.search(r'Ending\s+at\s+([\w\s]+?)\s+at\s+([\d.:]+)', text, re.I)
        if m:
            dest, arr = m.group(1).strip(), m.group(2).replace('.', ':')
        if not dest:
            m = re.search(r'To\s+([\w\s]+?)\s+at\s+([\d.:]+)', text, re.I)
            if m:
                dest, arr = m.group(1).strip(), m.group(2).replace('.', ':')

        if not origin or not dest or not dep or not arr:
            continue

        # Determine line
        line = "WR"
        wr_stations = {"Churchgate", "Virar", "Borivali", "Andheri", "Bandra",
                       "Bhayandar", "Dadar", "Mumbai Central", "Mahalakshmi"}
        if not any(s.lower() in origin.lower() or s.lower() in dest.lower() for s in wr_stations):
            line = "CR"

        train_type = "SLOW"
        if "AC" in text.upper():
            train_type = "AC LOCAL"

        results.append({
            "number": train_num,
            "origin": origin,
            "destination": dest,
            "departure": _norm_time_24h(dep),
            "arrival": _norm_time_24h(arr),
            "type": train_type,
            "stops": {},
            "source": "hub/list",
            "line": line,
            "direction": "",
        })

    print(f"  [List Items] {len(results)} trains (origin→dest only)")
    return results


# ─── Phase 2: Extract ───────────────────────────────────────────

def extract_from_dumps():
    """Parse all dumped HTML files."""
    all_trains = []

    # Hub page — richest source
    hub_path = DUMP_DIR / "trainhelp_hub.html"
    if hub_path.exists():
        html = hub_path.read_text(encoding="utf-8")
        print("\n--- Hub page ---")
        all_trains.extend(parse_harbour_grids(html))
        all_trains.extend(parse_trans_harbour_grids(html))
        all_trains.extend(parse_port_line(html))
        all_trains.extend(parse_list_items(html))

    # AC Local page
    ac_path = DUMP_DIR / "trainhelp_ac_local.html"
    if ac_path.exists():
        html = ac_path.read_text(encoding="utf-8")
        print("\n--- AC Local page ---")
        all_trains.extend(parse_ac_trains(html))

    # WR Main page
    wr_path = DUMP_DIR / "trainhelp_wr_main.html"
    if wr_path.exists():
        html = wr_path.read_text(encoding="utf-8")
        print("\n--- WR Main page ---")
        all_trains.extend(parse_wr_simple(html))

    # Save
    out_path = DATA_DIR / "scraped_timetable.json"
    out_path.write_text(json.dumps(all_trains, indent=2, ensure_ascii=False), encoding="utf-8")

    # Summary
    total = len(all_trains)
    with_stops = sum(1 for t in all_trains if t.get("stops"))
    print(f"\n{'='*60}")
    print(f"Total trains: {total}")
    print(f"With per-station stops: {with_stops}")
    print(f"Without (origin→dest only): {total - with_stops}")
    print(f"{'='*60}")

    by_line = {}
    for t in all_trains:
        key = t.get("line", "?")
        by_line.setdefault(key, {"total": 0, "with_stops": 0})
        by_line[key]["total"] += 1
        if t.get("stops"):
            by_line[key]["with_stops"] += 1

    for line, counts in sorted(by_line.items()):
        print(f"  {line}: {counts['total']} trains ({counts['with_stops']} with per-station stops)")

    print(f"\nSaved to {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    if args.dump:
        dump_html()
    elif args.live:
        dump_html()
        extract_from_dumps()
    else:
        extract_from_dumps()


if __name__ == "__main__":
    main()
