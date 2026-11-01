"""
Coletor Automatizado de Trending Topics do Brasil (X/Twitter via Trends24)
Preserva o histórico hora a hora para cruzar com os disparos dos Canais de WhatsApp.
"""
import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
import urllib.request
from bs4 import BeautifulSoup

BRT = timezone(timedelta(hours=-3))
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
TRENDS_CSV = DATA_DIR / "x_twitter_brazil_trending_timeseries.csv"


def fetch_x_trends_brazil(only_latest: bool = False):
    url = "https://trends24.in/brazil/"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    soup = BeautifulSoup(html, "html.parser")
    now_iso = datetime.now(BRT).isoformat(timespec="seconds")

    ols = soup.find_all("ol")
    if only_latest and ols:
        ols = ols[:1]

    rows = []
    for block_idx, ol in enumerate(ols):
        parent = ol.parent
        heading = parent.find(["h3", "h4", "time", "div"]) if parent else None
        block_label = (
            heading.get("data-timestamp")
            or (heading.get_text(strip=True) if heading else None)
            or f"hours_ago_{block_idx}"
        )
        block_label = f"block_{block_idx}_{str(block_label)[:50]}"
        for rank, li in enumerate(ol.find_all("li"), start=1):
            a = li.find("a")
            topic = a.get_text(strip=True) if a else li.get_text(strip=True)
            count_span = li.find("span", class_="tweet-count")
            tweet_count = count_span.get_text(strip=True) if count_span else ""
            rows.append({
                "collected_at_iso": now_iso,
                "snapshot_label": block_label,
                "rank": rank,
                "topic": topic,
                "tweet_count": tweet_count,
            })

    file_exists = TRENDS_CSV.exists()
    with open(TRENDS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["collected_at_iso", "snapshot_label", "rank", "topic", "tweet_count"],
        )
        if not file_exists:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return rows


if __name__ == "__main__":
    rows = fetch_x_trends_brazil(only_latest=False)
    print(f"Salvos {len(rows)} registros de Trending Topics do Brasil em {TRENDS_CSV}")
