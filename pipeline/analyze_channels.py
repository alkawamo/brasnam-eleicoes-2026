"""
Pipeline de Análise e Construção de Grafos para o BRASNAM 2026
Estudo Comparativo: "Exército do Lula" vs. "Tropa do Flávio" (Canais do WhatsApp)
"""

import csv
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter, defaultdict


def extract_hashtags(text: str) -> list[str]:
    if not text:
        return []
    return list(dict.fromkeys(re.findall(r"(#[a-zA-Z0-9_\u00C0-\u017F]+)", text)))


def extract_instagram_author(text: str) -> str | None:
    if not text:
        return None
    m = re.search(r"^(.+?)\s+(?:no|on)\s+Instagram", text.strip(), re.IGNORECASE | re.MULTILINE)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"\(@([a-zA-Z0-9_.]+)\)\s*•\s*perfil do Instagram", text)
    if m2:
        return f"@{m2.group(1)}"
    return None


def classify_mission(text: str, urls: list[str], hashtags: list[str]) -> str:
    t = (text or "").lower()
    if "google" in t and any(w in t for w in ["joguem", "pesquis", "busca", "subir outra busca"]):
        return "Google Bombing (Manipulação de Busca)"
    if hashtags or any(w in t for w in ["subam", "suba", "hastag", "hashtag", "subir a tag", "botar essa tag", "primeiro lugar no x", "primeiro lugar do x"]):
        return "Batalha de Hashtags (Trending Topics X)"
    if any(w in t for w in ["fiscal", "fiscaisdopl", "fiscalizar"]):
        return "Mobilização Offline / Fiscais de Urna"
    if any(w in t for w in ["explode", "explodam", "mais curtid", "multirao de seguidor", "mutirão", "sigam o companheiro", "curti e comentar", "colocar pressão no vídeo", "espalha esse vídeo", "espalhe esse vídeo", "dispara pra todo lugar", "disparar esse vídeo"]):
        return "Brigading / Mutirão de Engajamento (IG/YT/X)"
    if any(w in t for w in ["denuncie", "denunciar", "mentira", "fake news", "combater essa fake", "combatermos a maior fake", "boicotar", "território inimigo", "ronda", "censura", "calaram"]):
        return "Contra-Ataque / Narrativa de Censura ou Fake News"
    if any(w in t for w in ["recrutar", "soldados", "trazer mais", "10 milhões", "fechar o canal", "entrem no canal", "ative a notificação"]):
        return "Recrutamento e Ativação de Notificações (Push)"
    if any(w in t for w in ["ao vivo", "live", "debate", "estúdio", "bloco do 22", "bloquinho"]):
        return "Mobilização Sincronizada (Live / Debate / Ato)"
    if "conteúdo de ia" in t:
        return "Mídia Sintética (Rotulada 'Conteúdo de IA')"
    if urls:
        return "Difusão de Conteúdo Cross-Platform"
    return "Comando Interno / Engajamento Moral da Tropa"


def classify_platform(url: str, text: str = "") -> tuple[str, str]:
    try:
        url_clean = url.lstrip("i") if url.startswith("ihttps://") else url
        parsed = urlparse(url_clean)
        domain = parsed.netloc.lower().replace("www.", "")
        path_parts = [p for p in parsed.path.split("/") if p]

        if "instagram.com" in domain:
            ig_author = extract_instagram_author(text)
            if ig_author:
                return "Instagram", f"IG: {ig_author}"
            target = path_parts[0] if path_parts and path_parts[0] not in ("p", "reel", "reels", "stories") else "IG: Reel/Post"
            return "Instagram", f"IG: {target}"
        if "youtube.com" in domain or "youtu.be" in domain:
            return "YouTube", "YouTube Live/Video"
        if "tiktok.com" in domain:
            target = path_parts[0] if path_parts and path_parts[0].startswith("@") else "TikTok Video"
            return "TikTok", target
        if domain in ("x.com", "twitter.com"):
            target = f"X: @{path_parts[0]}" if path_parts else "X/Twitter"
            return "X (Twitter)", target
        if "t.me" in domain or "telegram.me" in domain:
            target = path_parts[0] if path_parts else "Telegram"
            return "Telegram", target
        if "whatsapp.com" in domain or "wa.me" in domain:
            if "0029VbCbRfD7tkj88k3soZ0Y" in url:
                return "WhatsApp Channel", "WA: Exército do Lula (Auto-Link)"
            if "0029VaDH1GU7DAWpJTrCXH39" in url:
                return "WhatsApp Channel", "WA: Canal Oficial do Lula"
            if "0029Vb8kT6E3AzNNDpBkN22J" in url:
                return "WhatsApp Channel", "WA: Tropa do Flávio (Auto-Link)"
            if "0029VbDNtfo4o7qVYbwemy1f" in url:
                return "WhatsApp Channel", "WA: Nikolas Ferreira - Oficial"
            return "WhatsApp Channel", domain
        if "fiscaisdopl.com.br" in domain:
            return "Plataforma Eleitoral", "Site: fiscaisdopl.com.br"
        if "bsky.app" in domain:
            return "Bluesky", "Bluesky Profile"
        if "facebook.com" in domain or "fb.watch" in domain:
            return "Facebook", "Facebook Page"
        return "Portal / Site Externo", domain
    except Exception:
        return "Outro", url


def analyze_files(json_paths: list[Path], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    # Agrupa e desduplica mensagens por canal e ID
    by_channel: dict[str, dict[str, dict]] = defaultdict(dict)

    for path in json_paths:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "messages" not in data:
            continue
        default_ch = data.get("metadata", {}).get("channel_name", path.stem)
        for msg in data["messages"]:
            ch = msg.get("channel_name") or default_ch
            # Normaliza nome do canal
            if "LULA" in ch.upper():
                ch = "EXÉRCITO DO LULA"
            elif "FLÁVIO" in ch.upper() or "FLAVIO" in ch.upper():
                ch = "TROPA DO FLÁVIO 🇧🇷"
            msg_id = msg.get("id") or f"{msg.get('pre_plain_text')}_{msg.get('text', '')[:80]}"
            by_channel[ch][msg_id] = msg

    summary_rows = []
    bipartite_edges = defaultdict(int)

    data_out_dir = output_dir.parent / "data"
    all_rows = []

    csv_fields = [
        "channel",
        "message_id",
        "date",
        "time",
        "captured_at_iso",
        "mission_type",
        "text",
        "urls",
        "hashtags",
        "has_image",
        "has_video",
        "has_audio",
        "reactions_heart",
        "reactions_thumbs",
        "reactions_salute",
        "reactions_pray",
        "reactions_laugh",
        "reactions_cry",
        "reactions_surprised",
        "raw_reactions",
    ]

    for ch_key, msg_map in by_channel.items():
        slug = "exercito_do_lula" if "LULA" in ch_key.upper() else "tropa_do_flavio"
        master_path = data_out_dir / f"master_{slug}.json"
        with open(master_path, "w", encoding="utf-8") as mf:
            json.dump(
                {
                    "metadata": {
                        "channel_name": ch_key,
                        "total_messages": len(msg_map),
                    },
                    "messages": list(msg_map.values()),
                },
                mf,
                indent=2,
                ensure_ascii=False,
            )

        channel_rows = []
        for msg in msg_map.values():
            pre = msg.get("pre_plain_text", "")
            text = msg.get("text", "")
            urls = msg.get("urls", [])
            tags = msg.get("hashtags") or extract_hashtags(text)
            media = msg.get("media", {})
            reactions = msg.get("reactions", {})

            date_str = ""
            time_str = msg.get("time_label", "")
            m_dt = re.search(r"\[(\d{1,2}:\d{2}),\s*(\d{1,2}/\d{1,2}/\d{2,4})\]", pre)
            if m_dt:
                time_str = m_dt.group(1)
                date_str = m_dt.group(2)
            elif not date_str:
                m_d = re.search(r"(\d{2}/\d{2}/\d{4})", pre)
                if m_d:
                    date_str = m_d.group(1)

            mission = classify_mission(text, urls, tags)

            row = {
                "channel": ch_key,
                "message_id": msg.get("id", ""),
                "date": date_str,
                "time": time_str,
                "captured_at_iso": msg.get("captured_at_iso", ""),
                "mission_type": mission,
                "text": text.replace("\r\n", " ").replace("\n", " ").strip(),
                "urls": " | ".join(urls),
                "hashtags": " ".join(tags),
                "has_image": media.get("has_image", False),
                "has_video": media.get("has_video", False),
                "has_audio": media.get("has_audio", False),
                "reactions_heart": reactions.get("❤", ""),
                "reactions_thumbs": reactions.get("👍", ""),
                "reactions_salute": reactions.get("🫡", ""),
                "reactions_pray": reactions.get("🙏", ""),
                "reactions_laugh": reactions.get("😂", ""),
                "reactions_cry": reactions.get("😢", ""),
                "reactions_surprised": reactions.get("😮", ""),
                "raw_reactions": json.dumps(reactions, ensure_ascii=False),
            }
            channel_rows.append(row)
            all_rows.append(row)

        ch_csv_path = data_out_dir / f"master_{slug}.csv"
        with open(ch_csv_path, "w", newline="", encoding="utf-8") as cf:
            writer = csv.DictWriter(cf, fieldnames=csv_fields)
            writer.writeheader()
            writer.writerows(channel_rows)

    all_csv_path = data_out_dir / "master_all_messages.csv"
    with open(all_csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(all_rows)

    for channel_name, msg_map in by_channel.items():
        messages = list(msg_map.values())
        mission_counts = Counter()
        platform_counts = Counter()
        emoji_presence = Counter()
        hashtags_counter = Counter()
        target_counter = Counter()
        dates_counter = Counter()
        ai_labeled_count = 0
        total_urls = 0

        for msg in messages:
            text = msg.get("text", "")
            urls = msg.get("urls", [])
            reactions = msg.get("reactions", {})
            top_emojis = msg.get("top_emojis", list(reactions.keys()))
            pre_plain = msg.get("pre_plain_text", "")

            dt_m = re.search(r"(\d{2}/\d{2}/\d{4})", pre_plain)
            if dt_m:
                dates_counter[dt_m.group(1)] += 1

            if "conteúdo de ia" in text.lower():
                ai_labeled_count += 1

            tags = msg.get("hashtags") or extract_hashtags(text)
            for tag in tags:
                hashtags_counter[tag] += 1
                bipartite_edges[(channel_name, "X / Hashtag", tag)] += 1
                target_counter[f"Tag: {tag}"] += 1

            m_type = classify_mission(text, urls, tags)
            mission_counts[m_type] += 1

            if m_type == "Google Bombing (Manipulação de Busca)":
                bipartite_edges[(channel_name, "Google Search", "Google Search Bombing")] += 1
                target_counter["Google Search Bombing"] += 1

            for em in top_emojis:
                emoji_presence[em] += 1

            for u in urls:
                total_urls += 1
                plat, target = classify_platform(u, text)
                platform_counts[plat] += 1
                bipartite_edges[(channel_name, plat, target)] += 1
                target_counter[target] += 1

        summary_rows.append({
            "channel": channel_name,
            "total_messages": len(messages),
            "dates_covered": dict(sorted(dates_counter.items())),
            "total_links_shared": total_urls,
            "total_hashtags_dispatched": sum(hashtags_counter.values()),
            "ai_content_labels_detected": ai_labeled_count,
            "unique_hashtags": dict(hashtags_counter.most_common(20)),
            "top_external_targets": dict(target_counter.most_common(15)),
            "mission_breakdown": dict(mission_counts.most_common()),
            "platform_targets": dict(platform_counts.most_common()),
            "top_emojis_frequency": dict(emoji_presence.most_common(10)),
        })

    report_path = output_dir / "brasnam_comparative_summary.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary_rows, f, indent=2, ensure_ascii=False)

    edges_csv = output_dir / "bipartite_graph_edges.csv"
    with open(edges_csv, "w", encoding="utf-8") as f:
        f.write("Source,Platform,Target,Weight\n")
        for (src, plat, tgt), weight in sorted(bipartite_edges.items(), key=lambda x: -x[1]):
            f.write(f'"{src}","{plat}","{tgt}",{weight}\n')

    print(json.dumps(summary_rows, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)

    json_files = [p for p in data_dir.glob("*.json") if "metadata" not in p.name]

    if not json_files:
        print(f"Coloque os arquivos .json em: {data_dir}")
    else:
        analyze_files(json_files, base_dir / "output")
