import json
from pathlib import Path

p = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data\whatsapp_channel_tropa_do_fl_vio_2026-10-27 (4).json")

with open(p, "r", encoding="utf-8") as f:
    d = json.load(f)

print("Metadata:", d.get("metadata"))
msgs = d.get("messages", [])
print(f"Total messages in file: {len(msgs)}")

print("\n--- ALL MESSAGES IN THIS JSON ---")
for i, m in enumerate(msgs):
    pre = m.get("pre_plain_text", "")
    txt = m.get("text", "")[:120].replace("\n", " ")
    cap = m.get("captured_at_iso", "")
    print(f"[{i:02d}] cap={cap[:19]} | pre={pre.strip()} | text={txt}")
