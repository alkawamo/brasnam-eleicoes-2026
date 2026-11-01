"""
Análise Computacional de Discurso: O 'Janonismo Cultural' e a Retórica de Mobilização
Analisa o corpus textual completo de 'Exército do Lula' (1.144 mensagens) e compara com 'Tropa do Flávio' (149 mensagens).
Mapeia os pilares do enquadramento retórico (framing analysis) identificados no documentário da BBC News.
"""

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DATA_DIR = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data")
OUTPUT_DIR = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Dicionários Temáticos de Enquadramento Discursivo (Framing Categories)
FRAMING_CATEGORIES = {
    "Militarismo_e_Comando": [
        "exercito", "exército", "tropa", "soldado", "soldados", "missao", "missão", 
        "missoes", "missões", "pelotao", "pelotão", "batalhao", "batalhão", "comando", 
        "ordem", "ordens", "general", "combate", "combater", "guerra", "batalha", 
        "capitao", "capitão", "linha de frente", "armas", "alerta", "continencia", "continência"
    ],
    "Urgencia_e_Panico": [
        "agora", "urgente", "urgência", "urgencia", "corram", "rapido", "rápido", 
        "minutos", "segundos", "imediatamente", "ja", "já", "atencao", "atenção", 
        "alerta maximo", "alerta máximo", "pressa", "ultimato", "emergencia", "emergência",
        "agoraaa", "agoraaaa", "socorro", "tempo real", "antes que"
    ],
    "Primeira_Pessoa_Parassocial": [
        "eu", "me", "mim", "meu", "meus", "minha", "minhas", "comigo", 
        "estou", "estive", "peco", "peço", "imploro", "gravei", "disse", 
        "fiz", "avisei", "garanto", "prometo", "minha vida", "minha conta", "meu canal"
    ],
    "Guerrilha_e_Inimigo": [
        "flavio", "flávio", "bolsonaro", "milicia", "milícia", "miliciano", "milicianos", 
        "fake news", "mentira", "mentiras", "criminoso", "crime", "censura", "golpe", 
        "quadrilha", "derrotar", "destruir", "massacre", "esquema", "desesperados", "desespero"
    ],
    "Gamificacao_e_Metas": [
        "meta", "metas", "bater", "milhoes", "milhões", "milhao", "milhão", 
        "canal fechado", "seguidores", "inscritos", "recorde", "curtidas", 
        "comentarios", "comentários", "explodir", "alcance", "algoritmo", "sininho"
    ],
    "Verbos_Imperativos_Acao": [
        "joguem", "pesquisem", "digitem", "busquem", "comentem", "curtam", 
        "compartilhem", "entrem", "espalhem", "cliquem", "vejam", "assistam", 
        "mandem", "repassem", "subam", "chamem", "votem", "salvem"
    ]
}

PORTUGUESE_STOPWORDS = {
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "é", "com", "não", "uma", "os", "no", 
    "se", "na", "por", "mais", "as", "dos", "como", "mas", "foi", "ao", "ele", "das", "tem", "à", "seu", 
    "sua", "ou", "ser", "quando", "muito", "nos", "já", "está", "também", "só", "pelo", "pela", "até", 
    "isso", "ela", "entre", "era", "depois", "sem", "mesmo", "aos", "ter", "seus", "quem", "nas", "me", 
    "esse", "eles", "estão", "você", "tinha", "foram", "essa", "num", "nem", "suas", "meu", "às", "minha", 
    "têm", "numa", "pelos", "elas", "havia", "seja", "qual", "será", "nós", "tenho", "lhe", "deles", 
    "essas", "esses", "pelas", "este", "fosse", "dele", "tu", "te", "vocês", "vos", "lhes", "meus", 
    "minhas", "teu", "tua", "teus", "tuas", "nosso", "nossa", "nossos", "nossas", "dela", "delas", 
    "esta", "estes", "estas", "aquele", "aquela", "aqueles", "aquelas", "isto", "aquilo", "estou", 
    "está", "estamos", "estão", "estive", "esteve", "estivemos", "estiveram", "estava", "estávamos", 
    "estavam", "hei", "há", "havemos", "hão", "houve", "houvemos", "houveram", "houvera", "houvéramos", 
    "haja", "hajamos", "hajam", "houvesse", "houvéssemos", "houvessem", "houver", "houvermos", "houverem", 
    "houverei", "houverá", "houveremos", "houverão", "houveria", "houveríamos", "houveriam", "sou", "somos", 
    "são", "era", "éramos", "eram", "fui", "foi", "fomos", "foram", "fora", "fôramos", "seja", "sejamos", 
    "sejam", "fosse", "fôssemos", "fossem", "for", "formos", "forem", "serei", "será", "seremos", "serão", 
    "seria", "seríamos", "seriam", "tenho", "tem", "temos", "tém", "tinha", "tínhamos", "tinham", "tive", 
    "teve", "tivemos", "tiveram", "tivera", "tivéramos", "tenha", "tenhamos", "tenham", "tivesse", 
    "tivéssemos", "tivessem", "tiver", "tivermos", "tiverem", "terei", "terá", "teremos", "terão", 
    "teria", "teríamos", "teriam", "https", "http", "www", "com", "br", "app", "link", "post", "vídeo", "video"
}

def clean_and_tokenize(text: str) -> list[str]:
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove menções e caracteres estranhos
    text = re.sub(r'[^\w\sáéíóúâêîôûãõàèìòùçÁÉÍÓÚÂÊÎÔÛÃÕÀÈÌÒÙÇ]', ' ', text.lower())
    tokens = text.split()
    return tokens

def analyze_channel_discourse(csv_path: Path, channel_name: str):
    total_messages = 0
    words_total = 0
    token_counter = Counter()
    bigram_counter = Counter()
    trigram_counter = Counter()
    category_counts = defaultdict(int)
    category_messages = defaultdict(int)
    
    notable_quotes = {cat: [] for cat in FRAMING_CATEGORIES}
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_messages += 1
            raw_text = row.get("text", "") or ""
            dt = row.get("datetime_local", "") or row.get("date", "")
            
            tokens = clean_and_tokenize(raw_text)
            words_total += len(tokens)
            
            # Stopword filtering for general keywords
            content_tokens = [t for t in tokens if t not in PORTUGUESE_STOPWORDS and len(t) > 2]
            token_counter.update(content_tokens)
            
            # N-grams
            for i in range(len(content_tokens) - 1):
                bigram_counter[f"{content_tokens[i]} {content_tokens[i+1]}"] += 1
            for i in range(len(content_tokens) - 2):
                trigram_counter[f"{content_tokens[i]} {content_tokens[i+1]} {content_tokens[i+2]}"] += 1
                
            # Category analysis
            text_lower = raw_text.lower()
            matched_cats_in_msg = set()
            for cat, keywords in FRAMING_CATEGORIES.items():
                cat_match = False
                for kw in keywords:
                    # boundary regex match
                    if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                        category_counts[cat] += 1
                        cat_match = True
                if cat_match:
                    category_messages[cat] += 1
                    if len(notable_quotes[cat]) < 5 and len(raw_text) > 20:
                        notable_quotes[cat].append({
                            "timestamp": dt,
                            "text": raw_text.strip()
                        })

    # Proportions (% of messages containing category)
    category_prevalence = {}
    for cat in FRAMING_CATEGORIES:
        msg_count = category_messages[cat]
        pct = (msg_count / total_messages * 100) if total_messages > 0 else 0
        category_prevalence[cat] = {
            "messages_count": msg_count,
            "percentage": round(pct, 2),
            "total_occurrences": category_counts[cat]
        }
        
    return {
        "channel_name": channel_name,
        "total_messages": total_messages,
        "total_words": words_total,
        "vocabulary_size": len(token_counter),
        "top_keywords": token_counter.most_common(30),
        "top_bigrams": bigram_counter.most_common(20),
        "top_trigrams": trigram_counter.most_common(15),
        "framing_categories": category_prevalence,
        "notable_quotes": notable_quotes
    }

print("Iniciando Análise de Discurso Computacional...")

lula_csv = DATA_DIR / "master_exercito_do_lula.csv"
flavio_csv = DATA_DIR / "master_tropa_do_flavio.csv"

lula_analysis = analyze_channel_discourse(lula_csv, "EXÉRCITO DO LULA")
flavio_analysis = analyze_channel_discourse(flavio_csv, "TROPA DO FLÁVIO 🇧🇷")

results = {
    "summary": "Análise Comparativa de Discurso e Framing: Janonismo Cultural vs. Tropa do Flávio",
    "dataset_date": "29/10/2026",
    "exercito_do_lula": lula_analysis,
    "tropa_do_flavio": flavio_analysis
}

output_json = OUTPUT_DIR / "discourse_analysis_janonismo.json"
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"[OK] Análise salva em: {output_json}")

# Gerar Markdown executivo
md_path = OUTPUT_DIR / "discourse_analysis_summary.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# Análise de Discurso e Enquadramento Retórico: O 'Janonismo Cultural' nas Eleições de 2026\n\n")
    f.write(f"Corpus analisado: **{lula_analysis['total_messages']} mensagens do Exército do Lula** vs. **{flavio_analysis['total_messages']} mensagens da Tropa do Flávio**.\n\n")
    
    f.write("## 1. Comparativo de Prevalência dos Enquadramentos (% das mensagens do canal)\n\n")
    f.write("| Categoria de Enquadramento | Exército do Lula (Janones) | Tropa do Flávio | Diferença / Fator |\n")
    f.write("| :--- | :---: | :---: | :---: |\n")
    
    for cat in FRAMING_CATEGORIES:
        lula_pct = lula_analysis["framing_categories"][cat]["percentage"]
        flavio_pct = flavio_analysis["framing_categories"][cat]["percentage"]
        diff = round(lula_pct - flavio_pct, 2)
        ratio = round(lula_pct / (flavio_pct + 0.01), 1)
        f.write(f"| **{cat.replace('_', ' ')}** | {lula_pct}% ({lula_analysis['framing_categories'][cat]['messages_count']}) | {flavio_pct}% ({flavio_analysis['framing_categories'][cat]['messages_count']}) | **{diff:+} pp** ({ratio}x) |\n")
        
    f.write("\n## 2. Palavras-Chave de Conteúdo Mais Frequentes (Top 15)\n\n")
    f.write("### Exército do Lula\n")
    for kw, count in lula_analysis["top_keywords"][:15]:
        f.write(f"- `{kw}`: {count} ocorrências\n")
        
    f.write("\n### Tropa do Flávio\n")
    for kw, count in flavio_analysis["top_keywords"][:15]:
        f.write(f"- `{kw}`: {count} ocorrências\n")

    f.write("\n## 3. Bigramas / Expressões Mais Marcantes (Top 10)\n\n")
    f.write("### Exército do Lula\n")
    for bg, count in lula_analysis["top_bigrams"][:10]:
        f.write(f"- `{bg}`: {count}\n")
        
    f.write("\n### Tropa do Flávio\n")
    for bg, count in flavio_analysis["top_bigrams"][:10]:
        f.write(f"- `{bg}`: {count}\n")

print(f"[OK] Relatório resumido salvo em: {md_path}")
