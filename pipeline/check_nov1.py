import json
from collections import Counter
import re
from pathlib import Path

data_dir = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data")

for fname in ["whatsapp_channel_ex_rcito_do_lula_2026-11-01.json", "whatsapp_channel_tropa_do_fl_vio_2026-11-01.json"]:
    p = data_dir / fname
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    msgs = d.get("messages", [])
    dates = Counter()
    for m in msgs:
        txt = m.get("pre_plain_text", "") + " " + m.get("datetime", "") + " " + m.get("date_str", "")
        found = re.findall(r"(\d{2}/\d{2}/\d{4})", txt)
        if found:
            for dt in found:
                dates[dt] += 1
        else:
            dates["NO_DATE"] += 1
    print(f"=== {fname} (total msgs: {len(msgs)}) ===")
    for dt, c in sorted(dates.items()):
        print(f"  {dt}: {c}")
