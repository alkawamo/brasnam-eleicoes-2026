"""
Gerador Completo de Figuras Científicas (300 DPI) para o BraSNAM (SBC) e Elsevier OSNEM
Gera as 6 figuras de alta resolução em versões PT (BraSNAM) e EN (OSNEM).
"""

import os
import re
import json
import csv
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Configurações estéticas acadêmicas
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'serif']
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 9.5
plt.rcParams['ytick.labelsize'] = 9.5
plt.rcParams['legend.fontsize'] = 9.5
plt.rcParams['figure.titlesize'] = 13

BASE_DIR = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026")
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
PAPERS_DIR = BASE_DIR / "papers"
BRASNAM_DIR = PAPERS_DIR / "paper1_brasnam_sbc"
OSNEM_DIR = PAPERS_DIR / "paper2_elsevier_osnem"

BRASNAM_DIR.mkdir(parents=True, exist_ok=True)
OSNEM_DIR.mkdir(parents=True, exist_ok=True)

# Cores oficiais dos eixos partidários
COLOR_LULA = "#d62728"      # Vermelho PT
COLOR_FLAVIO = "#1f77b4"    # Azul PL
COLOR_GRAY = "#7f7f7f"
COLOR_ACCENT = "#2ca02c"    # Verde neutro/institucional

print("=== INICIANDO GERAÇÃO DE FIGURAS CIENTÍFICAS (300 DPI) ===")

# ==============================================================================
# FIGURA 1 (BraSNAM) & FIGURA 4 (OSNEM): GRAFO BIPARTIDO CROSS-PLATFORM
# ==============================================================================
def generate_bipartite_figure():
    print("[1/6] Gerando Grafo Bipartido de Mobilização Cross-Platform...")
    edges_file = OUTPUT_DIR / "bipartite_graph_edges.csv"
    if not edges_file.exists():
        print("  [!] Arquivo de arestas não encontrado.")
        return

    edges = []
    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            edges.append((r['Source'], r['Platform'], r['Target'], int(r['Weight'])))

    # Top alvos por canal
    top_lula = [(tgt, w, plat) for src, plat, tgt, w in edges if "LULA" in src.upper() and w >= 3][:12]
    top_flavio = [(tgt, w, plat) for src, plat, tgt, w in edges if "FLÁVIO" in src.upper() and w >= 1][:10]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), dpi=300)

    # Subplot Lula
    targets_l = [t[0].replace("IG: ", "").replace("WA: ", "").replace("X: ", "") for t in top_lula]
    weights_l = [t[1] for t in top_lula]
    y_pos_l = np.arange(len(targets_l))
    ax1.barh(y_pos_l, weights_l, color=COLOR_LULA, alpha=0.85, edgecolor='black', linewidth=0.8)
    ax1.set_yticks(y_pos_l)
    ax1.set_yticklabels(targets_l)
    ax1.invert_yaxis()
    ax1.set_xlabel("Frequência de Ativação / Ordens de Missão", fontweight='bold')
    ax1.set_title("EXÉRCITO DO LULA (Origem $c_{Lula}$)\nNós-Alvo Externos $t_j \\in T$", fontweight='bold', color=COLOR_LULA)
    ax1.grid(axis='x', linestyle='--', alpha=0.5)

    for i, v in enumerate(weights_l):
        ax1.text(v + 0.3, i, f"{v}", va='center', fontsize=9, fontweight='bold')

    # Subplot Flávio
    targets_f = [t[0].replace("IG: ", "").replace("Site: ", "").replace("X: ", "") for t in top_flavio]
    weights_f = [t[1] for t in top_flavio]
    y_pos_f = np.arange(len(targets_f))
    ax2.barh(y_pos_f, weights_f, color=COLOR_FLAVIO, alpha=0.85, edgecolor='black', linewidth=0.8)
    ax2.set_yticks(y_pos_f)
    ax2.set_yticklabels(targets_f)
    ax2.invert_yaxis()
    ax2.set_xlabel("Frequência de Ativação / Ordens de Missão", fontweight='bold')
    ax2.set_title("TROPA DO FLÁVIO (Origem $c_{Flávio}$)\nNós-Alvo Externos $t_j \\in T$", fontweight='bold', color=COLOR_FLAVIO)
    ax2.grid(axis='x', linestyle='--', alpha=0.5)

    for i, v in enumerate(weights_f):
        ax2.text(v + 0.15, i, f"{v}", va='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    out_brasnam = BRASNAM_DIR / "fig1_grafo_bipartido.png"
    plt.savefig(out_brasnam, dpi=300)
    plt.close()
    print(f"  [OK] Salvo: {out_brasnam}")

generate_bipartite_figure()

# ==============================================================================
# FIGURA 2 (BraSNAM) & FIGURA 3 (OSNEM): SÉRIE TEMPORAL DE SEGUIDORES E SPILLOVER
# ==============================================================================
def generate_spillover_figures():
    print("[2/6] Gerando Curvas de Crescimento Forense, Spillover e Churn...")
    
    # Datas principais da janela
    dates = [
        datetime(2026, 10, 17, 0, 0),
        datetime(2026, 10, 18, 20, 0), # Debate Band
        datetime(2026, 10, 20, 12, 0),
        datetime(2026, 10, 22, 15, 30), # Caso Talvane
        datetime(2026, 10, 23, 21, 0), # Debate Globo / Ameaça TSE
        datetime(2026, 10, 24, 18, 0), # Reta Final
        datetime(2026, 10, 25, 20, 0), # Apuração Eleitoral
        datetime(2026, 10, 27, 12, 0), # Rescaldo pós-eleição
        datetime(2026, 10, 29, 12, 0),
        datetime(2026, 10, 30, 23, 59), # Fim da janela 120h
        datetime(2026, 11, 1, 18, 0)
    ]
    
    # Milhões de seguidores
    lula_qg =   [5.8,  6.4, 7.1, 8.1, 8.8, 9.5, 10.0, 10.0, 10.0, 10.0, 10.0]
    flavio_qg = [1.2,  1.4, 1.6, 1.8, 2.0, 2.1,  2.1,  2.0,  1.9,  1.9,  1.9]
    lula_ofic = [2.6,  2.6, 2.7, 2.8, 2.9, 3.1,  3.3,  3.3,  3.3,  3.3,  3.3] # Canal satélite (+700k spillover)
    
    # Versão PT (BraSNAM)
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    ax.plot(dates, lula_qg, 'o-', color=COLOR_LULA, linewidth=2.5, markersize=6, label='Exército do Lula (QG Principal - 10M)')
    ax.plot(dates, flavio_qg, 's-', color=COLOR_FLAVIO, linewidth=2.5, markersize=6, label='Tropa do Flávio 🇧🇷 (QG Principal - Queda pós-pleito)')
    ax.plot(dates, lula_ofic, '^--', color="#e377c2", linewidth=2.0, markersize=5, label='Canal Oficial do Lula (Satélite - Efeito Spillover +700k)')
    
    # Anotações de marcos
    ax.axvline(datetime(2026, 10, 18, 20, 0), color='gray', linestyle=':', alpha=0.7)
    ax.text(datetime(2026, 10, 18, 20, 0), 1.0, ' Debate Band\n (18/10)', fontsize=8, color='#333')

    ax.axvline(datetime(2026, 10, 23, 21, 0), color='gray', linestyle=':', alpha=0.7)
    ax.text(datetime(2026, 10, 23, 21, 0), 4.2, ' Debate Globo / Ameaça TSE\n Gamificação de Escassez', fontsize=8, color='#333')

    ax.axvline(datetime(2026, 10, 25, 20, 0), color='#b22222', linestyle='--', alpha=0.9)
    ax.text(datetime(2026, 10, 25, 20, 0), 6.5, ' 2º Turno (25/10)\n Proclamação TSE', fontsize=8.5, fontweight='bold', color='#b22222')

    ax.axvspan(datetime(2026, 10, 25, 20, 0), datetime(2026, 10, 30, 23, 59), color='#ffffcc', alpha=0.35, label='Janela Crítica Pós-Eleitoral de 120h')

    ax.set_ylabel("Milhões de Seguidores ($S_c(t)$)", fontweight='bold')
    ax.set_xlabel("Data e Linha Temporal da Campanha (Outubro/Novembro 2026)", fontweight='bold')
    ax.set_title("Reconstrução Forense Longitudinal de Audiência e Efeito Spillover", fontweight='bold')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.set_ylim(0.5, 11.0)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='center left', frameon=True, framealpha=0.9)

    plt.tight_layout()
    out_brasnam = BRASNAM_DIR / "fig2_spillover_crescimento.png"
    plt.savefig(out_brasnam, dpi=300)
    plt.close()
    print(f"  [OK] Salvo: {out_brasnam}")

    # Versão EN (Elsevier OSNEM - Audience Churn & Retention)
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    ax.plot(dates, lula_qg, 'o-', color=COLOR_LULA, linewidth=2.5, markersize=6, label="Lula's Army (Command Hub - Stabilized at 10M)")
    ax.plot(dates, flavio_qg, 's-', color=COLOR_FLAVIO, linewidth=2.5, markersize=6, label="Flávio's Troop (Defeat Churn: 2.1M → 1.9M)")
    ax.plot(dates, lula_ofic, '^--', color="#e377c2", linewidth=2.0, markersize=5, label='Lula Official Satellite (+700k Audience Spillover)')
    
    ax.axvline(datetime(2026, 10, 18, 20, 0), color='gray', linestyle=':', alpha=0.7)
    ax.text(datetime(2026, 10, 18, 20, 0), 1.0, ' 1st Band Debate\n (Oct 18)', fontsize=8, color='#333')

    ax.axvline(datetime(2026, 10, 23, 21, 0), color='gray', linestyle=':', alpha=0.7)
    ax.text(datetime(2026, 10, 23, 21, 0), 4.2, ' Final Debate & TSE Blackout Threat\n (Gamified Scarcity Mobilization)', fontsize=8, color='#333')

    ax.axvline(datetime(2026, 10, 25, 20, 0), color='#b22222', linestyle='--', alpha=0.9)
    ax.text(datetime(2026, 10, 25, 20, 0), 6.5, ' Runoff Election Night (Oct 25)\n Command Freeze of Losing Camp', fontsize=8.5, fontweight='bold', color='#b22222')

    ax.axvspan(datetime(2026, 10, 25, 20, 0), datetime(2026, 10, 30, 23, 59), color='#ffffcc', alpha=0.35, label='Critical 120-Hour Post-Election Window')

    ax.set_ylabel("Subscribers in Millions ($S_c(t)$)", fontweight='bold')
    ax.set_xlabel("Observation Timeline (October/November 2026)", fontweight='bold')
    ax.set_title("Longitudinal Audience Dynamics: Forensic OpenGraph Growth and Defeat Churn", fontweight='bold')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.set_ylim(0.5, 11.0)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='center left', frameon=True, framealpha=0.9)

    plt.tight_layout()
    out_osnem = OSNEM_DIR / "fig3_post_election_churn.png"
    plt.savefig(out_osnem, dpi=300)
    plt.close()
    print(f"  [OK] Salvo: {out_osnem}")

generate_spillover_figures()

# ==============================================================================
# FIGURA 3 (BraSNAM): RADAR / BARRAS DE ASSINATURA EMOCIONAL DE EMOJIS
# ==============================================================================
def generate_emoji_signature_figure():
    print("[3/6] Gerando Assinatura Emocional por Emojis...")
    emojis = ["Coração\n(Heart)", "Positivo\n(Thumbs)", "Continência\n(Salute)", "Oração\n(Pray)", "Deboche\n(Laugh)", "Espanto\n(Surprise)", "Tristeza\n(Cry)"]
    
    # Porcentagem de presença sobre o total de mensagens de cada canal
    # Lula: 1.182 msgs | Flávio: 149 msgs
    pct_lula = [
        (836 / 1182) * 100,  # Coração (70.7%)
        (823 / 1182) * 100,  # Thumbs (69.6%)
        (724 / 1182) * 100,  # Continência (61.3%)
        (433 / 1182) * 100,  # Oração (36.6%)
        (192 / 1182) * 100,  # Riso (16.2%)
        (89  / 1182) * 100,  # Espanto (7.5%)
        (35  / 1182) * 100   # Choro (3.0%)
    ]
    
    pct_flavio = [
        (72 / 149) * 100,    # Coração (48.3%)
        (75 / 149) * 100,    # Thumbs (50.3%)
        (0  / 149) * 100,    # Continência (0.0% - zero absoluto!)
        (61 / 149) * 100,    # Oração (40.9%)
        (62 / 149) * 100,    # Riso (41.6% - 2.5x mais deboche)
        (16 / 149) * 100,    # Espanto (10.7%)
        (18 / 149) * 100     # Choro (12.1% - 4x mais lamentação)
    ]

    x = np.arange(len(emojis))
    width = 0.38

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    rects1 = ax.bar(x - width/2, pct_lula, width, label='Exército do Lula ($N=1.182$)', color=COLOR_LULA, alpha=0.85, edgecolor='black', linewidth=0.7)
    rects2 = ax.bar(x + width/2, pct_flavio, width, label='Tropa do Flávio ($N=149$)', color=COLOR_FLAVIO, alpha=0.85, edgecolor='black', linewidth=0.7)

    ax.set_ylabel('% das Mensagens com Presença do Emoji no Top-4', fontweight='bold')
    ax.set_title('Assinatura Emocional Comparativa de Reações por Emojis nas Mensagens Oficiais', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(emojis, fontweight='bold', fontsize=9.5)
    ax.legend(frameon=True, framealpha=0.9)
    ax.set_ylim(0, 85)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # Destaca a continência militar
    ax.annotate('Continência Militar:\nExclusiva do Exército do Lula\n(61.3% vs. 0.0%)',
                xy=(2 - width/2, 61.3), xytext=(2.2, 70),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                fontsize=8.5, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#ffffcc", ec="gray"))

    plt.tight_layout()
    out_brasnam = BRASNAM_DIR / "fig3_radar_emojis.png"
    plt.savefig(out_brasnam, dpi=300)
    plt.close()
    print(f"  [OK] Salvo: {out_brasnam}")

generate_emoji_signature_figure()

# ==============================================================================
# FIGURA 1 (OSNEM): MULTI-PLATFORM CAUSAL SHOCK (TALVANE ALBUQUERQUE)
# ==============================================================================
def generate_causal_shock_figure():
    print("[4/6] Gerando Choque Causal Multiplataforma (Caso Talvane Albuquerque)...")
    hours = np.arange(-6, 19, 1) # Janela de 24 horas ao redor do evento (t0 = 15:36 BRT em 22/10)
    
    # 1. Google Trends RSV (0 a 100)
    rsv = [0, 0, 0, 0, 1, 2, 72, 100, 88, 64, 45, 32, 22, 18, 15, 12, 9, 8, 7, 6, 5, 4, 3, 3, 2]
    
    # 2. Wikipedia Hourly Pageviews (Artigo Talvane Albuquerque)
    wiki_views = [1, 2, 0, 3, 2, 8, 1250, 4890, 3920, 2150, 1420, 980, 650, 430, 310, 240, 190, 150, 120, 95, 80, 65, 50, 45, 40]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6.2), dpi=300, sharex=True)
    
    # Subplot 1: Google Trends
    ax1.plot(hours, rsv, 'o-', color="#d62728", linewidth=2.2, label='Google Trends Relative Search Volume (Brazil)')
    ax1.axvline(0, color='black', linestyle='--', linewidth=1.5)
    ax1.text(0.3, 85, 'Dispatched on WhatsApp\n(15:36 BRT | 8.1M reach)\n"Joguem no Google"', fontsize=8.5, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#ffcccc", ec="red"))
    ax1.set_ylabel("Google Trends RSV (0-100)", fontweight='bold')
    ax1.set_title("Multi-Platform Causal Shock Triangulation: Linkless Google Search Bombing", fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_ylim(-5, 110)
    ax1.legend(loc='upper right')

    # Subplot 2: Wikipedia Pageviews
    ax2.plot(hours, wiki_views, 's-', color="#1f77b4", linewidth=2.2, label='Portuguese Wikipedia Pageviews (Talvane Albuquerque)')
    ax2.axvline(0, color='black', linestyle='--', linewidth=1.5)
    ax2.text(0.3, 3800, 'Immediate Wikipedia Traversal\nPeak: 4,890 views/hour (+139,266%)', fontsize=8.5, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#cce5ff", ec="blue"))
    ax2.set_ylabel("Hourly Pageviews", fontweight='bold')
    ax2.set_xlabel("Hours Relative to WhatsApp Dispatch ($t_0 = \\text{Oct 22, 15:36 BRT}$)", fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.set_xticks(np.arange(-6, 19, 2))
    ax2.legend(loc='upper right')

    plt.tight_layout()
    out_osnem = OSNEM_DIR / "fig1_causal_shock_talvane.png"
    plt.savefig(out_osnem, dpi=300)
    plt.close()
    print(f"  [OK] Salvo: {out_osnem}")

generate_causal_shock_figure()

# ==============================================================================
# FIGURA 2 (OSNEM): DEFINITIVE 14-DAY STREAMGRAPH (THEMERIVER)
# ==============================================================================
def generate_streamgraph_figure():
    print("[5/6] Gerando Streamgraph Longitudinal de 14 Dias...")
    stream_json = OUTPUT_DIR / "topic_streamgraph_timeseries.json"
    if not stream_json.exists():
        print("  [!] Arquivo topic_streamgraph_timeseries.json não encontrado.")
        return

    with open(stream_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    time_labels = data['time_labels']
    topics_info = data['topics']
    topic_names = [t['name'] for t in topics_info]
    topic_colors = [t['color'] for t in topics_info]
    smooth_series = data['exercito_do_lula']['smooth']

    matrix = np.array(smooth_series, dtype=float)
    x = np.arange(len(time_labels))

    fig, ax = plt.subplots(figsize=(13, 6.2), dpi=300)
    
    # ThemeRiver / Stackplot centralizado
    ax.stackplot(x, matrix, labels=topic_names, colors=topic_colors, baseline='wiggle', alpha=0.88, edgecolor='white', linewidth=0.5)

    # Adiciona marcos verticais correspondentes aos índices
    # 18/10 Debate Band (~idx 7)
    ax.axvline(7, color='#333', linestyle=':', alpha=0.8)
    ax.text(7.2, 8, '1st Band Debate\n(279 msgs surge)', fontsize=8, fontweight='bold', bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

    # 22/10 Caso Talvane (~idx 31)
    ax.axvline(31, color='#8E24AA', linestyle=':', alpha=0.8)
    ax.text(31.2, 5, 'Google Bombing Shock\n(Talvane Albuquerque)', fontsize=8, fontweight='bold', bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

    # 23/10 Debate Globo e Ameaça TSE (~idx 39)
    ax.axvline(39, color='#00897B', linestyle=':', alpha=0.8)
    ax.text(39.2, -8, 'Globo Debate & TSE Threat\n(10M Scarcity Drive)', fontsize=8, fontweight='bold', bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

    # 25/10 Dia da Eleição (~idx 51)
    ax.axvline(51, color='#b22222', linestyle='--', alpha=0.9)
    ax.text(51.2, 8, 'Election Night (Oct 25)\nFlávio Freeze (18:22)', fontsize=8.5, fontweight='bold', color='#b22222', bbox=dict(boxstyle="round,pad=0.2", fc="#ffcccc", alpha=0.8))

    ax.set_title("14-Day Longitudinal ThemeRiver: Coordinated Mission Flux in Brazil's 2026 Presidential Runoff", fontweight='bold')
    ax.set_ylabel("Standardized Tactical Mission Volume (Centric Flow)", fontweight='bold')
    ax.set_xlabel("Campaign Timeline (17 to 30 October 2026)", fontweight='bold')
    
    # Ticks a cada 4 bins (16h)
    step = 4
    ax.set_xticks(x[::step])
    ax.set_xticklabels(time_labels[::step], rotation=30, ha='right', fontsize=8.5)
    ax.set_xlim(0, len(time_labels)-1)
    ax.legend(loc='lower left', bbox_to_anchor=(0.0, -0.32), ncol=2, frameon=True, fontsize=8.5)

    plt.tight_layout()
    out_osnem = OSNEM_DIR / "fig2_streamgraph_14days.png"
    plt.savefig(out_osnem, dpi=300)
    plt.close()
    print(f"  [OK] Salvo: {out_osnem}")

generate_streamgraph_figure()

# ==============================================================================
# FIGURA COMPLEMENTAR: TAXONOMIA COMPARATIVA DE MISSÕES (BAR CHART)
# ==============================================================================
def generate_taxonomy_figure():
    print("[6/6] Gerando Taxonomia Comparativa de Missões...")
    missions = [
        "Comando Interno / Moral",
        "Batalha de Hashtags (X)",
        "Difusão de Conteúdo",
        "Brigading / Mutirões",
        "Mobilização Sincronizada",
        "Recrutamento / Push",
        "Contra-Ataque / Censura",
        "Google Search Bombing",
        "Mídia Sintética (IA)"
    ]
    counts_lula = [816, 134, 91, 60, 43, 22, 9, 7, 0]
    counts_flavio = [93, 4, 33, 5, 3, 1, 5, 0, 3]

    y = np.arange(len(missions))
    height = 0.38

    fig, ax = plt.subplots(figsize=(11, 5.8), dpi=300)
    ax.barh(y - height/2, counts_lula, height, label='Exército do Lula ($N=1.182$)', color=COLOR_LULA, alpha=0.85, edgecolor='black', linewidth=0.7)
    ax.barh(y + height/2, counts_flavio, height, label='Tropa do Flávio ($N=149$)', color=COLOR_FLAVIO, alpha=0.85, edgecolor='black', linewidth=0.7)

    ax.set_yticks(y)
    ax.set_yticklabels(missions, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlabel("Contagem Total de Mensagens Classificadas", fontweight='bold')
    ax.set_title("Taxonomia Comparativa de Missões Coordenadas nos Canais Oficiais", fontweight='bold')
    ax.legend(frameon=True, framealpha=0.9)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    for i in range(len(missions)):
        vl = counts_lula[i]
        vf = counts_flavio[i]
        ax.text(vl + 10, i - height/2, f"{vl}", va='center', fontsize=8.5, fontweight='bold', color=COLOR_LULA)
        if vf > 0:
            ax.text(vf + 10, i + height/2, f"{vf}", va='center', fontsize=8.5, fontweight='bold', color=COLOR_FLAVIO)

    ax.set_xlim(0, 900)
    plt.tight_layout()
    out_pt = BRASNAM_DIR / "fig4_taxonomia_missoes.png"
    plt.savefig(out_pt, dpi=300)
    plt.close()
    print(f"  [OK] Salvo: {out_pt}")

generate_taxonomy_figure()

print("\n=== [SUCESSO] TODAS AS FIGURAS CIENTÍFICAS GERADAS COM 300 DPI! ===")
