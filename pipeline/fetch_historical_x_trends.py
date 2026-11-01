"""
Consolidador Histórico de Trending Topics do Brasil (X/Twitter) — 2º Turno (05/10 a 24/10/2026)
Extrai o Top 50 e também a trajetória das 8 horas anteriores embutida nos gráficos SVG
de cada snapshot do GetDayTrends + Trends24, gerando `data/x_twitter_brazil_historical_2nd_round.csv`.
"""

import csv
import re
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = DATA_DIR / "x_twitter_brazil_historical_2nd_round.csv"

STEPS_DIR = Path(r"C:\Users\alkaw\.gemini\antigravity\brain\7abe0fa6-eab3-429b-83a0-8b285b4a8cfc\.system_generated\steps")


def parse_saved_getdaytrends_files() -> list[dict]:
    records = {}
    for step_file in sorted(STEPS_DIR.glob("*/content.md")):
        text = step_file.read_text(encoding="utf-8", errors="ignore")
        m_src = re.search(r"Source:\s*https://getdaytrends\.com/brazil/(\d{4}-\d{2}-\d{2})/(\d{1,2})/", text)
        if not m_src:
            continue
        day_str, hour_str = m_src.group(1), m_src.group(2)
        base_dt = datetime.strptime(f"{day_str} {int(hour_str):02d}:00:00", "%Y-%m-%d %H:%M:%S")

        soup = BeautifulSoup(text, "html.parser")
        for tr in soup.select("table.ranking.trends tbody tr"):
            pos_el = tr.select_one("th.pos")
            link_el = tr.select_one("td.main a")
            if not pos_el or not link_el:
                continue
            try:
                rank_now = int(pos_el.get_text(strip=True))
            except ValueError:
                continue
            topic = link_el.get_text(strip=True)

            # Save the exact snapshot hour
            dt_iso = base_dt.strftime("%Y-%m-%d %H:%M:%S")
            records[(dt_iso, rank_now, topic)] = {
                "date_utc": base_dt.strftime("%Y-%m-%d"),
                "hour_utc": base_dt.strftime("%H:%M"),
                "datetime_utc": dt_iso,
                "rank": rank_now,
                "topic": topic,
            }

            # Also reconstruct the 7 preceding hours from the SVG polyline (x=0,20,40,60,80,100,120,140 -> -7h..0h)
            for poly in tr.select("svg.preview polyline"):
                if "grid-h" in (poly.get("class") or []):
                    continue
                pts = (poly.get("points") or "").strip()
                if not pts:
                    continue
                for pair in pts.split():
                    if "," not in pair:
                        continue
                    try:
                        x_str, y_str = pair.split(",")
                        x_val, y_val = int(float(x_str)), int(float(y_str))
                    except ValueError:
                        continue
                    if y_val <= 0 or y_val >= 50:
                        continue
                    hours_back = (140 - x_val) // 20
                    if 1 <= hours_back <= 7:
                        hist_dt = base_dt - timedelta(hours=hours_back)
                        hist_iso = hist_dt.strftime("%Y-%m-%d %H:%M:%S")
                        key = (hist_iso, y_val, topic)
                        if key not in records:
                            records[key] = {
                                "date_utc": hist_dt.strftime("%Y-%m-%d"),
                                "hour_utc": hist_dt.strftime("%H:%M"),
                                "datetime_utc": hist_iso,
                                "rank": y_val,
                                "topic": topic,
                            }

    sorted_rows = sorted(records.values(), key=lambda r: (r["datetime_utc"], r["rank"]))
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date_utc", "hour_utc", "datetime_utc", "rank", "topic"],
        )
        writer.writeheader()
        for r in sorted_rows:
            writer.writerow(r)

    return sorted_rows


if __name__ == "__main__":
    rows = parse_saved_getdaytrends_files()
    print(f"✅ Consolidados {len(rows)} registros históricos (05/10 a 24/10/2026) em {OUT_CSV}")
