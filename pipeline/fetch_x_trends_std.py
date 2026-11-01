"""
Coletor Automatizado de Trending Topics do Brasil (X/Twitter via Trends24)
100% biblioteca padrão (urllib, html.parser, re, csv) - Zero dependências externas
"""
import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
import re
import urllib.request
from html.parser import HTMLParser

BRT = timezone(timedelta(hours=-3))
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
TRENDS_CSV = DATA_DIR / "x_twitter_brazil_trending_timeseries.csv"


class Trends24Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_ol = False
        self.in_li = False
        self.in_a = False
        self.in_span = False
        self.current_ol_idx = -1
        self.current_rank = 0
        self.current_topic = ""
        self.current_count = ""
        self.results = []
        self.block_label = "latest"

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "ol":
            self.in_ol = True
            self.current_ol_idx += 1
            self.current_rank = 0
            self.block_label = f"block_{self.current_ol_idx}"
        elif self.in_ol and tag == "li":
            self.in_li = True
            self.current_rank += 1
            self.current_topic = ""
            self.current_count = ""
        elif self.in_li and tag == "a":
            self.in_a = True
        elif self.in_li and tag == "span" and "tweet-count" in attrs_dict.get("class", ""):
            self.in_span = True

    def handle_endtag(self, tag):
        if tag == "ol":
            self.in_ol = False
        elif tag == "li" and self.in_ol:
            self.in_li = False
            if self.current_topic.strip():
                self.results.append({
                    "snapshot_label": self.block_label,
                    "rank": self.current_rank,
                    "topic": self.current_topic.strip(),
                    "tweet_count": self.current_count.strip(),
                })
        elif tag == "a":
            self.in_a = False
        elif tag == "span":
            self.in_span = False

    def handle_data(self, data):
        if self.in_li:
            if self.in_span:
                self.current_count += data
            elif self.in_a or not self.current_topic:
                self.current_topic += data


def fetch_and_save():
    url = "https://trends24.in/brazil/"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    )
    print("Acessando trends24.in/brazil...")
    with urllib.request.urlopen(req, timeout=25) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    parser = Trends24Parser()
    parser.feed(html)
    now_iso = datetime.now(BRT).isoformat(timespec="seconds")

    print(f"Encontrados {len(parser.results)} tópicos na página.")
    if not parser.results:
        # Fallback via regex simples
        matches = re.findall(r'<li[^>]*><a[^>]*>([^<]+)</a>(?:<span[^>]*class="tweet-count"[^>]*>([^<]*)</span>)?', html)
        for r, (t, c) in enumerate(matches[:50], start=1):
            parser.results.append({
                "snapshot_label": "block_0",
                "rank": r,
                "topic": t.strip(),
                "tweet_count": c.strip(),
            })
        print(f"Fallback regex extraiu {len(parser.results)} tópicos.")

    rows = []
    for item in parser.results:
        rows.append({
            "collected_at_iso": now_iso,
            "snapshot_label": item["snapshot_label"],
            "rank": item["rank"],
            "topic": item["topic"],
            "tweet_count": item["tweet_count"],
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

    print(f"[OK] Gravados {len(rows)} registros em {TRENDS_CSV.name}")
    print("\n--- TOP 10 TÓPICOS AGORA NO BRASIL ---")
    for r in rows[:15]:
        if r["snapshot_label"] == "block_0":
            print(f"#{r['rank']:02d}: {r['topic']} ({r['tweet_count'] or 'sem contagem'})")


if __name__ == "__main__":
    fetch_and_save()
