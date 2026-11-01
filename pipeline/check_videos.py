import json
import csv
from pathlib import Path

DATA_DIR = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data")

# Check CSV
csv_path = DATA_DIR / "master_exercito_do_lula.csv"
videos_csv = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        has_v = row.get("has_video", "").lower() == "true"
        has_media = row.get("has_media", "").lower() == "true"
        text = row.get("text", "")
        if has_v or has_media or "vídeo" in text.lower() or "video" in text.lower():
            videos_csv.append(row)

print(f"Total de mensagens no CSV: {reader.line_num - 1}")
print(f"Mensagens com flag has_video/has_media ou menção a vídeo: {len(videos_csv)}")

# Check raw JSON to see what properties were extracted
json_path = DATA_DIR / "master_exercito_do_lula.json"
with open(json_path, "r", encoding="utf-8") as f:
    raw_msgs = json.load(f)

media_types = {}
sample_videos = []
for m in raw_msgs:
    # check keys
    media = m.get("media", {}) or {}
    has_vid = m.get("hasVideo", False) or m.get("has_video", False)
    text = m.get("text", "") or m.get("caption", "") or ""
    if has_vid or media or "vídeo" in text.lower():
        sample_videos.append({
            "datetime": m.get("datetime_local", "") or m.get("date", ""),
            "text": text[:160],
            "media": media,
            "hasVideo": has_vid,
            "links": m.get("links", [])
        })

print(f"\nExemplos de mensagens de vídeo nos JSONs:")
for item in sample_videos[:6]:
    print(f"[{item['datetime']}] hasVideo={item['hasVideo']} | Text: {item['text']}")
    if item['links']:
        print(f"  Links: {item['links']}")
