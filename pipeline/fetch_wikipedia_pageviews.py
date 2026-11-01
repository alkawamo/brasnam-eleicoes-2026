"""
Coletor de Visualizações Absolutas na Wikipédia em Português (Wikimedia REST API)
Serve para calibrar o índice relativo (0-100) do Google Trends com o volume
absoluto de acessos reais aos verbetes alvo de Search Bombing e aos candidatos
desde o início do 2º turno (05/10/2026).
"""

import csv
import json
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = DATA_DIR / "wikipedia_pt_pageviews_2nd_round.csv"

ARTICLES = [
    "Talvane_Albuquerque",
    "Ceci_Cunha",
    "Flávio_Bolsonaro",
    "Luiz_Inácio_Lula_da_Silva",
    "André_Janones",
    "Nikolas_Ferreira",
    "Rubel_(cantor)",
]


def fetch_article_views(article: str) -> list[dict]:
    encoded = urllib.parse.quote(article, safe="")
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/pt.wikipedia/all-access/user/{encoded}/daily/20261005/20261024"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "BRASNAM2026Research/1.0 (https://sbc.org.br; academic-election-study@sbc.org.br)"
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    rows = []
    for item in data.get("items", []):
        ts = item["timestamp"]  # YYYYMMDD00
        date_str = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
        rows.append({
            "date": date_str,
            "article": article,
            "views": item["views"],
        })
    return rows


def main():
    all_rows = []
    for art in ARTICLES:
        try:
            r = fetch_article_views(art)
            all_rows.extend(r)
            total_v = sum(x["views"] for x in r)
            max_day = max(r, key=lambda x: x["views"]) if r else {"date": "-", "views": 0}
            print(f"[OK] {art}: {len(r)} dias | Total={total_v:,} | Pico={max_day['views']:,} em {max_day['date']}")
        except Exception as e:
            print(f"[WARN] {art}: {e}")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "article", "views"])
        writer.writeheader()
        for row in sorted(all_rows, key=lambda x: (x["date"], x["article"])):
            writer.writerow(row)
    print(f"✅ Salvo em {OUT_CSV}")


if __name__ == "__main__":
    main()
