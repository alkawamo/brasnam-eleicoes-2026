"""
Monitor de Seguidores em Tempo Real (Sem Login) — BRASNAM 2026
Consulta a página pública de convite dos Canais do WhatsApp e grava a série
temporal de seguidores em `data/followers_live_timeseries.csv`.

Encerramento Automático:
- Roda de hora em hora até Quarta-feira, 28/10/2026 às 23:59 (72h após o 2º turno).
- Após essa data, remove automaticamente a tarefa agendada do Windows.
"""

import csv
import re
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path

# Data/hora limite automática da coleta (Janela crítica de 120h até sexta-feira)
AUTO_STOP_DATETIME = datetime(2026, 10, 30, 23, 59, 59)

CHANNELS = [
    ("EXÉRCITO DO LULA", "0029VbCbRfD7tkj88k3soZ0Y"),
    ("TROPA DO FLÁVIO 🇧🇷", "0029Vb8kT6E3AzNNDpBkN22J"),
    ("Canal Oficial do Lula", "0029VaDH1GU7DAWpJTrCXH39"),
    ("Nikolas Ferreira - Oficial", "0029VbDNtfo4o7qVYbwemy1f"),
]


def parse_followers_string(raw_str: str) -> int:
    """Converte '10M', '2.1M', '9,8 mi', '110 mil', '77K' em inteiro."""
    if not raw_str:
        return 0
    s = raw_str.lower().replace("\xa0", " ").strip()
    mult = 1
    if "mil" in s or "k" in s:
        mult = 1_000
        s = re.sub(r"(mil|k)", "", s).strip()
    elif "mi" in s or "m" in s:
        mult = 1_000_000
        s = re.sub(r"(mi|m)", "", s).strip()

    s = s.replace(",", ".")
    try:
        return int(float(s) * mult)
    except ValueError:
        return 0


def fetch_channel_followers(channel_id: str) -> tuple[str, int, str]:
    url = f"https://whatsapp.com/channel/{channel_id}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    m = re.search(
        r"(?:Channel|Canal)\s*(?:&#x2022;|•)\s*([\d.,]+\s*(?:mil|mi|M|K)?)\s*(?:followers|seguidores)",
        html,
        re.IGNORECASE,
    )
    raw_followers = m.group(1).replace("\xa0", " ").strip() if m else ""
    parsed_int = parse_followers_string(raw_followers)

    status = "ACTIVE" if raw_followers else ("REMOVED_OR_UNAVAILABLE" if "pageTitle" not in html else "UNKNOWN")
    return raw_followers, parsed_int, status


def record_snapshot():
    now_local = datetime.now()
    if now_local > AUTO_STOP_DATETIME:
        subprocess.run(
            ["schtasks", "/Delete", "/TN", "BRASNAM2026_FollowerMonitor", "/F"],
            capture_output=True,
        )
        return []

    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    csv_path = data_dir / "followers_live_timeseries.csv"

    file_exists = csv_path.exists()
    now_iso = now_local.astimezone().isoformat(timespec="seconds")

    rows_added = []
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp_iso", "channel_name", "channel_id", "followers_raw", "followers_int", "status"])

        for name, cid in CHANNELS:
            try:
                raw_f, int_f, status = fetch_channel_followers(cid)
            except Exception as e:
                raw_f, int_f, status = "", 0, f"ERROR: {e}"
            row = [now_iso, name, cid, raw_f, int_f, status]
            writer.writerow(row)
            rows_added.append(row)
            print(f"[{now_iso}] {name}: {raw_f} ({int_f:,}) | Status: {status}")

    try:
        from fetch_x_trends import fetch_x_trends_brazil
        fetch_x_trends_brazil(only_latest=True)
    except Exception as e:
        print(f"[{now_iso}] Aviso ao coletar X Trends: {e}")

    return rows_added


if __name__ == "__main__":
    record_snapshot()

