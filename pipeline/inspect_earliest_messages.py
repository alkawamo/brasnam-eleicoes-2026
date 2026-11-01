import json
from pathlib import Path

data_dir = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data")
p = data_dir / "whatsapp_channel_ex_rcito_do_lula_2026-10-23 (desde 05-10 ate 23-10).json"

with open(p, "r", encoding="utf-8") as f:
    d = json.load(f)

msgs = d.get("messages", [])
print(f"Total msgs: {len(msgs)}")
for i in range(max(0, len(msgs)-25), len(msgs)):
    m = msgs[i]
    print(f"[{i}] pre={m.get('pre_plain_text')} | text={repr(m.get('text', ''))[:90]}")

