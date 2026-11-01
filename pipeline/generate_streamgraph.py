"""
Gera a Figura Poderosa Multi-Plataforma (4 Painéis Sincronizados — Causa -> Efeito):
  - Painel A (Causa Interna 1): Streamflow de Tópicos no WhatsApp — EXÉRCITO DO LULA (N = 939)
  - Painel B (Causa Interna 2): Streamflow de Tópicos no WhatsApp — TROPA DO FLÁVIO (N = 146)
  - Painel C (Efeito Externo 1): Streamflow dos Trending Topics do X/Twitter Brasil (Top 50 hora a hora,
    ponderado por 51 - Rank, classificado nas mesmas 6 frentes temáticas)
  - Painel D (Efeito Externo 2): Choque de Buscas no Google Trends (Web & YouTube) + Pageviews da Wikipédia
"""

import csv
import json
import math
import re
from datetime import datetime, timedelta
from pathlib import Path

TOPIC_DEFINITIONS = [
    (
        "Crime Organizado / Caso Talvane & Milícia",
        "#8E24AA",  # Roxo
        [
            "talvane", "tavane", "albuquerque", "mandou matar", "ceci", "miliciano",
            "milícia", "milicia", "comando vermelho", "facção", "faccao", "crime",
            "criminoso", "bandido", "traficante", "tráfico", "narco", "pcc", "assassino",
            "assassinato", "arma", "tiro", "polícia", "policia", "cadeia", "preso",
            "ana clara", "punhal", "surubinha", "tigrinho"
        ],
    ),
    (
        "Guerra Algorítmica / Google Bombing / TSE & IA",
        "#00897B",  # Verde-azulado (Teal)
        [
            "google", "pesquisem", "pesquise", "joguem", "busca", "trends", "algoritmo",
            "boicote", "boicotar", "derrubar", "bloquear", "bloqueio", "tse", "justiça",
            "ministro", "conteúdo de ia", "inteligência artificial", "meta ", "alcance",
            "sininho", "notificações", "notificacao", "inscritos", "seguidores",
            "10 milhões", "10 milhoes", "9 milhões", "8 milhões", "5 milhões", "canal deles",
            "exercitodolula", "exércitodolula", "ninguemcalanossoexercito", "esquerdadominouasredes",
            "janones", "aviãozinho", "aviao", "direct", "terceiro botão", "deixem o vídeo rodar",
            "deixem rodar"
        ],
    ),
    (
        "Debates, Lives & Apuração (Band / Globo / Janones / 24h)",
        "#1E88E5",  # Azul Royal
        [
            "debate", "band", "globo", "ao vivo", "live", "24h", "24 horas", "24 hs",
            "telão", "telao", "estúdio", "estudio", "esquenta", "transmissão", "transmissao",
            "assistam", "acompanhem", "youtube", "bonner", "sabatina", "showdolula",
            "luladandoshow", "respondeolula", "virotedoexercito", "livedavirada", "convocação",
            "convocacao", "apuração", "apuracao"
        ],
    ),
    (
        "Disputa pelo Nordeste, Piauí & Narrativa de 'Censura'",
        "#FB8C00",  # Laranja Forte
        [
            "nordeste", "nordestino", "nordestinos", "piauí", "piaui", "fonteles",
            "ceará", "bahia", "pernambuco", "seca", "água", "agua", "censura", "censurado",
            "calar", "naocalemosnordestino", "falanordeste", "prosperanordeste",
            "preconceito", "xenofobia", "fortaleza", "maranhão"
        ],
    ),
    (
        "Escândalos, Economia & Direitos (Pandemia / INSS / Lancha / Sigilo)",
        "#E53935",  # Vermelho Coral
        [
            "pandemia", "vacina", "covid", "inss", "aposentado", "aposentadoria",
            "salário", "salario", "mínimo", "minimo", "corta você", "cortar", "direitos",
            "lancha", "mansão", "mansao", "sigilo", "rachadinha", "dinheiro", "imposto",
            "pobre", "fome", "economia", "inflação", "corrupção", "roubo", "esquema",
            "abreosigilo", "flaviobolsonaronlancha", "desculpalula"
        ],
    ),
    (
        "Mobilização de Rua, Fila / Transporte, Prorrogação & Voto",
        "#FBC02D",  # Amarelo Ouro
        [
            "rua", "caminhada", "carreata", "ato ", "paulista", "copacabana", "belo horizonte",
            "liberdade", "vira voto", "virada", "somaisumvotoprolula", "voto", "urna",
            "domingo", "amanhã é", "amanha e", "fiscal", "fiscais", "fiscaisdopl",
            "seção", "secao", "sessões", "sessoes", "mesário", "título", "adesivo", "bandeira", "camisa",
            "lulavaivirar", "comlulanarua", "lulanapaulista", "sabadoucomlula", "rjcomlula",
            "lulaemcopacabana", "nikolas", "flávio", "flavio", "lula", "bolsonaro",
            "ônibus", "onibus", "transporte", "prorrogação", "prorrogacao", "duas horas", "estender",
            "fila", "filas", "carona", "solidária", "solidaria", "salvador", "batalhão"
        ],
    ),
]


def parse_msg_datetime(msg: dict) -> datetime | None:
    date_str = msg.get("date_str", "")
    time_str = msg.get("time_label", "")
    pre = msg.get("pre_plain_text", "")

    if (not date_str or date_str == "31/12/1969") and pre:
        m = re.search(r"\[(\d{2}:\d{2}),\s*(\d{2}/\d{2}/\d{4})\]", pre)
        if m:
            time_str, date_str = m.group(1), m.group(2)

    if not date_str or date_str == "31/12/1969":
        return None

    if not time_str or not re.match(r"^\d{1,2}:\d{2}$", time_str.strip()):
        m_end = re.search(r"(\d{1,2}:\d{2})\s*$", (msg.get("text") or "").strip())
        time_str = m_end.group(1) if m_end else "12:00"

    try:
        dt = datetime.strptime(f"{date_str.strip()} {time_str.strip()}", "%d/%m/%Y %H:%M")
        if dt.year < 2026:
            return None
        return dt
    except ValueError:
        return None


def classify_message_topics(text: str, urls: list[str], hashtags: list[str], strict_political: bool = False) -> list[int]:
    combined = f"{text or ''} {' '.join(urls or [])} {' '.join(hashtags or [])}".lower()
    matched = []
    # Percorre os 5 primeiros tópicos específicos antes do tópico 6 geral
    for idx in range(len(TOPIC_DEFINITIONS) - 1):
        _, _, keywords = TOPIC_DEFINITIONS[idx]
        if any(kw.lower() in combined for kw in keywords):
            matched.append(idx)
    if not matched:
        _, _, kw6 = TOPIC_DEFINITIONS[5]
        if any(kw.lower() in combined for kw in kw6):
            matched.append(5)
    return matched


def gaussian_smooth_1d(arr: list[float], sigma: float = 1.1) -> list[float]:
    n = len(arr)
    radius = int(math.ceil(3 * sigma))
    weights = [math.exp(-(k * k) / (2 * sigma * sigma)) for k in range(-radius, radius + 1)]
    w_sum = sum(weights)
    weights = [w / w_sum for w in weights]

    out = []
    for i in range(n):
        acc = 0.0
        for idx_k, k in enumerate(range(-radius, radius + 1)):
            j = min(max(i + k, 0), n - 1)
            acc += arr[j] * weights[idx_k]
        out.append(round(max(0.0, acc), 3))
    return out


def build_channel_topic_data(messages: list[dict], time_grid: list[datetime], bin_hours: int = 4):
    parsed_msgs = []
    for m in messages:
        dt = parse_msg_datetime(m)
        if dt is not None:
            parsed_msgs.append((dt, m))

    parsed_msgs.sort(key=lambda x: x[0])

    n_topics = len(TOPIC_DEFINITIONS)
    n_bins = len(time_grid)
    raw_matrix = [[0.0 for _ in range(n_bins)] for _ in range(n_topics)]
    bin_examples = [[] for _ in range(n_bins)]

    last_topics = [5]
    last_dt = None

    for dt, m in parsed_msgs:
        topics = classify_message_topics(m.get("text", ""), m.get("urls", []), m.get("hashtags", []))
        if not topics:
            if last_dt and (dt - last_dt) <= timedelta(minutes=60):
                topics = last_topics
            else:
                t_low = (m.get("text") or "").lower()
                if any(w in t_low for w in ["tropa", "exército", "exercito", "soldado", "missão", "missao", "bora", "vamos"]):
                    topics = [5]
                else:
                    topics = [1]
        else:
            last_topics = topics
            last_dt = dt

        bin_idx = int((dt - time_grid[0]).total_seconds() // (bin_hours * 3600))
        if 0 <= bin_idx < n_bins:
            weight = 1.0 / len(topics)
            for t_idx in topics:
                raw_matrix[t_idx][bin_idx] += weight
            clean_txt = re.sub(r"\s+", " ", (m.get("text") or "").strip())
            if len(clean_txt) > 15 and len(bin_examples[bin_idx]) < 2:
                bin_examples[bin_idx].append(f"[{dt.strftime('%d/%m %H:%M')}] {clean_txt[:115]}")

    smoothed_matrix = [gaussian_smooth_1d(row, sigma=1.1) for row in raw_matrix]
    return raw_matrix, smoothed_matrix, bin_examples


def build_x_trends_stream(data_dir: Path, time_grid: list[datetime], bin_hours: int = 4):
    n_topics = len(TOPIC_DEFINITIONS)
    n_bins = len(time_grid)
    raw_matrix = [[0.0 for _ in range(n_bins)] for _ in range(n_topics)]
    top_tags_per_bin = [[] for _ in range(n_bins)]
    seen_in_bin = [set() for _ in range(n_bins)]

    hist_csv = data_dir / "x_twitter_brazil_historical_2nd_round.csv"
    if hist_csv.exists():
        with open(hist_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    dt_utc = datetime.strptime(row["datetime_utc"], "%Y-%m-%d %H:%M:%S")
                    dt_brt = dt_utc - timedelta(hours=3)
                    rank = int(row["rank"])
                    topic_str = row["topic"].strip()
                except Exception:
                    continue
                bin_idx = int((dt_brt - time_grid[0]).total_seconds() // (bin_hours * 3600))
                if 0 <= bin_idx < n_bins:
                    matched = classify_message_topics(topic_str, [], [], strict_political=True)
                    if matched:
                        score = (51 - min(rank, 50)) / 10.0
                        for t_idx in matched:
                            raw_matrix[t_idx][bin_idx] += score / len(matched)
                        tag_label = f"#{rank} {topic_str}"
                        if topic_str.lower() not in seen_in_bin[bin_idx] and len(top_tags_per_bin[bin_idx]) < 4:
                            seen_in_bin[bin_idx].add(topic_str.lower())
                            top_tags_per_bin[bin_idx].append(tag_label)

    live_csv = data_dir / "x_twitter_brazil_trending_timeseries.csv"
    if live_csv.exists():
        with open(live_csv, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 4 or parts[0] == "captured_at":
                    continue
                try:
                    dt_brt = datetime.strptime(parts[0][:16], "%Y-%m-%dT%H:%M")
                    rank = int(parts[2])
                    topic_str = parts[3].strip()
                except Exception:
                    continue
                bin_idx = int((dt_brt - time_grid[0]).total_seconds() // (bin_hours * 3600))
                if 0 <= bin_idx < n_bins:
                    matched = classify_message_topics(topic_str, [], [], strict_political=True)
                    if matched:
                        score = (51 - min(rank, 50)) / 10.0
                        for t_idx in matched:
                            raw_matrix[t_idx][bin_idx] += score / len(matched)
                        tag_label = f"#{rank} {topic_str}"
                        if topic_str.lower() not in seen_in_bin[bin_idx] and len(top_tags_per_bin[bin_idx]) < 4:
                            seen_in_bin[bin_idx].add(topic_str.lower())
                            top_tags_per_bin[bin_idx].append(tag_label)

    smoothed_matrix = [gaussian_smooth_1d(row, sigma=1.0) for row in raw_matrix]
    return raw_matrix, smoothed_matrix, top_tags_per_bin


def build_google_and_wiki_series(data_dir: Path, time_grid: list[datetime], bin_hours: int = 4):
    n_bins = len(time_grid)
    google_talvane = [0.0 for _ in range(n_bins)]
    google_punhal = [0.0 for _ in range(n_bins)]
    yt_debate = [0.0 for _ in range(n_bins)]
    wiki_talvane = [0.0 for _ in range(n_bins)]

    g_csv = data_dir / "google_trends_search_bombing.csv"
    if g_csv.exists():
        with open(g_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    dt_utc = datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")
                    dt_brt = dt_utc - timedelta(hours=3)
                    v_talv = max(float(row.get("Talvane Albuquerque", 0)), float(row.get("Bolsonaro Talvane", 0)))
                    v_punh = float(row.get("Punhal Verde e Amarelo", 0))
                except Exception:
                    continue
                bin_idx = int((dt_brt - time_grid[0]).total_seconds() // (bin_hours * 3600))
                if 0 <= bin_idx < n_bins:
                    google_talvane[bin_idx] = max(google_talvane[bin_idx], v_talv)
                    google_punhal[bin_idx] = max(google_punhal[bin_idx], v_punh)

    yt_csv = data_dir / "youtube_trends_debate_cortes.csv"
    if yt_csv.exists():
        with open(yt_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    dt_utc = datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")
                    dt_brt = dt_utc - timedelta(hours=3)
                    v_deb = max(float(row.get("Debate Globo", 0)), float(row.get("Lula debate", 0)))
                except Exception:
                    continue
                bin_idx = int((dt_brt - time_grid[0]).total_seconds() // (bin_hours * 3600))
                if 0 <= bin_idx < n_bins:
                    yt_debate[bin_idx] = max(yt_debate[bin_idx], v_deb)

    w_csv = data_dir / "wikipedia_pt_pageviews_2nd_round.csv"
    if w_csv.exists():
        daily_views = {}
        with open(w_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["article"] in ("Talvane_Albuquerque", "Ceci_Cunha"):
                    d_str = row["date"]
                    daily_views[d_str] = daily_views.get(d_str, 0) + int(row["views"])
        for j, dt in enumerate(time_grid):
            d_key = dt.strftime("%Y-%m-%d")
            if d_key in daily_views:
                # Normaliza para escala 0-100 (pico em 22/10 = 4181 + 1261 = 5442 leituras)
                wiki_talvane[j] = round(min(100.0, (daily_views[d_key] / 5442.0) * 100.0), 1)

    return {
        "google_talvane": google_talvane,
        "google_punhal": google_punhal,
        "yt_debate": yt_debate,
        "wiki_talvane_ceci_norm": wiki_talvane,
    }


def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)

    with open(data_dir / "master_exercito_do_lula.json", "r", encoding="utf-8") as f:
        lula_msgs = json.load(f)["messages"]
    with open(data_dir / "master_tropa_do_flavio.json", "r", encoding="utf-8") as f:
        flavio_msgs = json.load(f)["messages"]

    start_dt = datetime(2026, 10, 17, 6, 0)
    bin_hours = 4

    # Determina end_dt dinamicamente com base na data mais recente encontrada
    max_dt = datetime(2026, 10, 25, 22, 0)
    for m in lula_msgs + flavio_msgs:
        dt = parse_msg_datetime(m)
        if dt and dt > max_dt:
            max_dt = dt
    
    # Ajusta para o próximo intervalo de bin_hours
    end_dt = max_dt
    if end_dt.hour % bin_hours != 2:
        end_dt = end_dt.replace(minute=0, second=0) + timedelta(hours=(bin_hours - (end_dt.hour % bin_hours)))

    n_steps = int((end_dt - start_dt).total_seconds() // (bin_hours * 3600)) + 1
    time_grid = [start_dt + timedelta(hours=i * bin_hours) for i in range(n_steps)]
    time_labels = [dt.strftime("%d/%m %Hh") for dt in time_grid]

    lula_raw, lula_smooth, lula_ex = build_channel_topic_data(lula_msgs, time_grid, bin_hours)
    flavio_raw, flavio_smooth, flavio_ex = build_channel_topic_data(flavio_msgs, time_grid, bin_hours)
    x_raw, x_smooth, x_tags = build_x_trends_stream(data_dir, time_grid, bin_hours)
    external_curves = build_google_and_wiki_series(data_dir, time_grid, bin_hours)

    export_payload = {
        "bin_hours": bin_hours,
        "time_labels": time_labels,
        "topics": [{"name": t[0], "color": t[1]} for t in TOPIC_DEFINITIONS],
        "exercito_do_lula": {"smooth": lula_smooth, "examples": lula_ex},
        "tropa_do_flavio": {"smooth": flavio_smooth, "examples": flavio_ex},
        "x_brazil_trends": {"smooth": x_smooth, "top_tags": x_tags},
        "external_search_telemetry": external_curves,
    }

    out_json = output_dir / "topic_streamgraph_timeseries.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2, ensure_ascii=False)

    print(f"[OK] Matriz Causal Multi-Plataforma salva em: {out_json}")
    for j, tags in enumerate(x_tags):
        if tags:
            print(f"  [{time_labels[j]}] X Top Político: {', '.join(tags[:3])}")


if __name__ == "__main__":
    main()
