"""
Benchmark de Canais Públicos do Telegram (Sem Login) — Eleições 2026
Coleta o número exato de inscritos nos canais públicos oficiais equivalentes no Telegram
para comparar a escala Telegram (2022/2026) vs. WhatsApp Channels (2026).
Salva em `data/telegram_vs_whatsapp_benchmark.csv`.
"""

import csv
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
import urllib.request
from bs4 import BeautifulSoup

BRT = timezone(timedelta(hours=-3))
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = DATA_DIR / "telegram_vs_whatsapp_benchmark.csv"

TELEGRAM_HANDLES = [
    ("Canal do Lula (Telegram)", "LulaNoTelegram"),
    ("Jair Bolsonaro (Telegram)", "jairbolsonarobrasil"),
    ("Nikolas Ferreira (Telegram)", "nikolasferreira"),
]


def fetch_tg_channel(label: str, handle: str) -> dict:
    url = f"https://t.me/{handle}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.select_one(".tgme_page_title")
    extra_el = soup.select_one(".tgme_page_extra")
    title = title_el.get_text(strip=True) if title_el else label
    extra = extra_el.get_text(strip=True) if extra_el else ""

    # Parse subscriber integer from e.g. '1 420 512 subscribers'
    m = re.search(r"([\d\s.,]+)\s*(?:subscribers|members|inscritos)", extra, re.IGNORECASE)
    subs_int = 0
    if m:
        digits = re.sub(r"[^\d]", "", m.group(1))
        subs_int = int(digits) if digits else 0

    return {
        "timestamp_iso": datetime.now(BRT).isoformat(timespec="seconds"),
        "label": label,
        "handle": f"@{handle}",
        "title_detected": title,
        "subscribers_raw": extra,
        "subscribers_int": subs_int,
    }


def main():
    file_exists = OUT_CSV.exists()
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp_iso", "label", "handle", "title_detected", "subscribers_raw", "subscribers_int"],
        )
        if not file_exists:
            writer.writeheader()
        for label, handle in TELEGRAM_HANDLES:
            try:
                row = fetch_tg_channel(label, handle)
                writer.writerow(row)
                print(f"[OK] {label} (@{handle}): {row['subscribers_raw']} -> {row['subscribers_int']:,}")
            except Exception as e:
                print(f"[WARN] {label} (@{handle}): {e}")
    print(f"✅ Benchmark Telegram salvo em {OUT_CSV}")


if __name__ == "__main__":
    main()
