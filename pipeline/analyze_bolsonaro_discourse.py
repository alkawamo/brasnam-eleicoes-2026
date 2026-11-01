"""
Análise Profunda de Discurso da Campanha de Flávio Bolsonaro (TROPA DO FLÁVIO 🇧🇷)
Mapeia os enquadramentos retóricos específicos da direita:
Vitimização/Censura, Apelo Religioso/Moral, Terceirização para Influenciadores,
Anti-petismo, Mobilização de Fiscais e a Retórica do Silêncio Pós-Derrota.
"""

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DATA_DIR = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data")
OUTPUT_DIR = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\output")

BOLSONARO_FRAMING = {
    "Vitimizacao_e_Censura": [
        "censura", "censurado", "censurar", "calar", "calem", "calaram", "silenciou", 
        "silenciar", "derrubaram", "perseguicao", "perseguição", "injustiça", "injustica",
        "ditadura", "liberdade de expressao", "liberdade de expressão", "verdade", "proibido"
    ],
    "Religiao_Moral_e_Patria": [
        "deus", "jesus", "fe", "fé", "familia", "família", "patria", "pátria", 
        "oracao", "oração", "orando", "abençoe", "abencoe", "bencao", "bênção", 
        "cristao", "cristão", "cristaos", "cristãos", "sagrado", "vida", "valores"
    ],
    "Centralidade_Influenciadores": [
        "nikolas", "ferreira", "pavanato", "gayer", "gustavo gayer", "claudio dantas", 
        "pilhado", "magno malta", "carmelo", "tarcisio", "tarcísio", "michelle", "bolsonaro"
    ],
    "Antipetismo_e_Inimigo": [
        "pt", "petista", "petistas", "lula", "ladrao", "ladrão", "corrupcao", "corrupção", 
        "esquerda", "comunismo", "comunista", "desespero", "mentira", "mentiras", "mentiroso", "fake news"
    ],
    "Mobilizacao_Fiscalizacao_Urnas": [
        "fiscais", "fiscal", "fiscaisdopl", "urna", "urnas", "voto", "votos", 
        "fiscalizar", "apuracao", "apuração", "fraude", "auditoria", "seja fiscal"
    ],
    "Identidade_Regional_Nordeste": [
        "nordeste", "nordestino", "nordestinos", "bahia", "ceara", "ceará", 
        "pernambuco", "prospera", "fala nordeste", "silenciou o nordeste"
    ]
}

def analyze_bolsonaro():
    csv_path = DATA_DIR / "master_tropa_do_flavio.csv"
    messages = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            messages.append(row)
            
    total_msgs = len(messages)
    print(f"Total de mensagens na Tropa do Flávio: {total_msgs}")
    
    cat_counts = defaultdict(int)
    cat_msgs = defaultdict(list)
    
    # Temporal distribution
    date_counts = Counter(m.get("date", "") for m in messages)
    
    for m in messages:
        text = m.get("text", "") or ""
        dt = m.get("datetime_local", "") or m.get("date", "")
        text_lower = text.lower()
        
        for cat, keywords in BOLSONARO_FRAMING.items():
            matched = False
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    cat_counts[cat] += 1
                    matched = True
            if matched:
                cat_msgs[cat].append({
                    "timestamp": dt,
                    "text": text.strip()
                })
                
    # Proportions
    framing_summary = {}
    for cat in BOLSONARO_FRAMING:
        msg_count = len(cat_msgs[cat])
        pct = (msg_count / total_msgs * 100) if total_msgs > 0 else 0
        framing_summary[cat] = {
            "messages_count": msg_count,
            "percentage": round(pct, 2),
            "total_occurrences": cat_counts[cat],
            "sample_quotes": cat_msgs[cat][:5]
        }
        
    result = {
        "channel_name": "TROPA DO FLÁVIO 🇧🇷",
        "total_messages": total_msgs,
        "date_distribution": dict(date_counts),
        "framing_categories": framing_summary
    }
    
    out_json = OUTPUT_DIR / "discourse_analysis_bolsonaro.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        
    # Generate Markdown report
    out_md = OUTPUT_DIR / "discourse_analysis_bolsonaro_summary.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# Análise de Discurso e Retórica: Canal Oficial da Campanha Bolsonaro (TROPA DO FLÁVIO 🇧🇷)\n\n")
        f.write(f"Total de mensagens no corpus: **{total_msgs} mensagens** (Período: 18/10 a 25/10/2026).\n\n")
        
        f.write("## 1. Enquadramentos Retóricos Dominantes (% das Mensagens)\n\n")
        f.write("| Categoria de Enquadramento | Mensagens com a Pauta | % do Canal | Ocorrências Totais |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for cat in BOLSONARO_FRAMING:
            info = framing_summary[cat]
            f.write(f"| **{cat.replace('_', ' ')}** | {info['messages_count']} | **{info['percentage']}%** | {info['total_occurrences']} |\n")
            
        f.write("\n## 2. Exemplos Marcantes por Categoria\n\n")
        for cat in BOLSONARO_FRAMING:
            f.write(f"### {cat.replace('_', ' ')}\n")
            quotes = framing_summary[cat]["sample_quotes"]
            if not quotes:
                f.write("*Nenhum exemplo registrado.*\n\n")
                continue
            for q in quotes:
                f.write(f"- *[{q['timestamp']}]* \"{q['text'][:200]}...\"\n")
            f.write("\n")
            
        f.write("## 3. Dinâmica Temporal e Apagão Pós-Eleição\n\n")
        f.write("| Data | Volume de Mensagens | Contexto Operacional |\n")
        f.write("| :--- | :---: | :--- |\n")
        for d, cnt in sorted(date_counts.items()):
            f.write(f"| {d} | {cnt} msgs | {'Pico de campanha' if cnt > 15 else ('Dia da eleição (até 18h22)' if '25/10' in d else 'Operação normal')} |\n")
        f.write("| 26/10 a 29/10 | **0 msgs** | **Paralisia / Silêncio Operacional Absoluto pós-derrota** |\n")

    print(f"[OK] Análise de Flávio Bolsonaro salva em: {out_json}")
    print(f"[OK] Relatório Markdown em: {out_md}")

if __name__ == "__main__":
    analyze_bolsonaro()
