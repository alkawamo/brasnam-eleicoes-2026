import os
import csv
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.patheffects as PathEffects
from pathlib import Path

# Paths
ROOT_DIR = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026")
OUTPUT_DIR = ROOT_DIR / "output"
PAPERS_DIR = ROOT_DIR / "papers"
BRASNAM_DIR = PAPERS_DIR / "paper1_brasnam_sbc"
OSNEM_DIR = PAPERS_DIR / "paper2_elsevier_osnem"

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

COLOR_LULA = "#C62828"    # Vermelho escuro / carmesim
COLOR_FLAVIO = "#1565C0"  # Azul escuro / navy
COLOR_IG = "#E1306C"      # Instagram Magenta
COLOR_X = "#0288D1"       # X / Twitter Ciano/Azul
COLOR_WA = "#2E7D32"      # WhatsApp Verde
COLOR_YT = "#D32F2F"      # YouTube Vermelho
COLOR_SEARCH = "#F57C00"  # Google Search Laranja/Âmbar
COLOR_WEB = "#546E7A"     # Web / Eleitoral Cinza Slate

PLATFORM_COLORS = {
    'Instagram': COLOR_IG,
    'X (Twitter)': COLOR_X,
    'X / Hashtag': COLOR_X,
    'WhatsApp Channel': COLOR_WA,
    'YouTube': COLOR_YT,
    'Google Search': COLOR_SEARCH,
    'Portal / Site Externo': COLOR_WEB,
    'Plataforma Eleitoral': COLOR_WEB,
    'Facebook': '#3b5998'
}

PLATFORM_MARKERS = {
    'Instagram': 'o',
    'X (Twitter)': 's',
    'X / Hashtag': 's',
    'WhatsApp Channel': '^',
    'YouTube': 'v',
    'Google Search': '*',
    'Portal / Site Externo': 'D',
    'Plataforma Eleitoral': 'D',
    'Facebook': 'o'
}

def clean_target_name(t):
    t = t.replace("IG: ", "").replace("WA: ", "").replace("X: ", "").replace("Site: ", "")
    if len(t) > 28:
        t = t[:25] + "..."
    return t

def generate_true_bipartite_graph():
    print("[1/2] Gerando Grafo Bipartido Direcionado G = (C, T, E, w)...")
    edges_file = OUTPUT_DIR / "bipartite_graph_edges.csv"
    df = pd.read_csv(edges_file)

    # Filtrar alvos mais relevantes para clareza visual máxima
    # Lula: top 15 alvos
    df_lula = df[df['Source'].str.contains('LULA', case=False)].sort_values(by='Weight', ascending=False)
    top_lula = df_lula.head(15)
    
    # Flávio: top 12 alvos
    df_flavio = df[df['Source'].str.contains('FLÁVIO', case=False)].sort_values(by='Weight', ascending=False)
    top_flavio = df_flavio.head(12)

    df_selected = pd.concat([top_lula, top_flavio]).drop_duplicates(subset=['Source', 'Target'])

    # Criar DiGraph
    B = nx.DiGraph()

    # Nós de comando
    B.add_node("c_Lula", label="EXÉRCITO DO LULA\n(10M seg. | 1.182 msgs)", node_type="command", campaign="Lula", size=3200, color=COLOR_LULA)
    B.add_node("c_Flavio", label="TROPA DO FLÁVIO\n(1.9M seg. | 149 msgs)", node_type="command", campaign="Flavio", size=2400, color=COLOR_FLAVIO)

    # Nós alvos
    for _, row in df_selected.iterrows():
        tgt = row['Target']
        plat = row['Platform']
        w = int(row['Weight'])
        clean_name = clean_target_name(tgt)
        
        if tgt not in B:
            B.add_node(tgt, label=clean_name, node_type="target", platform=plat,
                       color=PLATFORM_COLORS.get(plat, "#757575"),
                       marker=PLATFORM_MARKERS.get(plat, 'o'),
                       total_weight=w)
        else:
            B.nodes[tgt]['total_weight'] += w

        # Arestas
        src_node = "c_Lula" if "LULA" in row['Source'].upper() else "c_Flavio"
        B.add_edge(src_node, tgt, weight=w, platform=plat, campaign="Lula" if src_node == "c_Lula" else "Flavio")

    # Layout Customizado Topológico Elegante
    # c_Lula à esquerda (-1.4, 0), c_Flavio à direita (+1.4, 0)
    # Alvos em colunas harmônicas
    pos = {}
    pos["c_Lula"] = np.array([-1.45, 0.0])
    pos["c_Flavio"] = np.array([1.45, 0.0])

    # Separar alvos por afiliação
    lula_exclusive = [n for n in B.nodes() if B.nodes[n]['node_type'] == 'target' and B.has_edge("c_Lula", n) and not B.has_edge("c_Flavio", n)]
    flavio_exclusive = [n for n in B.nodes() if B.nodes[n]['node_type'] == 'target' and B.has_edge("c_Flavio", n) and not B.has_edge("c_Lula", n)]
    shared = [n for n in B.nodes() if B.nodes[n]['node_type'] == 'target' and B.has_edge("c_Lula", n) and B.has_edge("c_Flavio", n)]

    # Ordenar por peso
    lula_exclusive.sort(key=lambda n: B.nodes[n]['total_weight'], reverse=True)
    flavio_exclusive.sort(key=lambda n: B.nodes[n]['total_weight'], reverse=True)

    # Posicionar alvos do Lula em 2 colunas suaves à esquerda
    for i, n in enumerate(lula_exclusive):
        col = 0 if i % 2 == 0 else 1
        x = -0.85 if col == 0 else -0.42
        # y varia de +1.2 a -1.2
        num_in_col = (len(lula_exclusive) + 1) // 2 if col == 0 else len(lula_exclusive) // 2
        rank_in_col = i // 2
        y = np.linspace(1.15, -1.15, num_in_col)[rank_in_col]
        pos[n] = np.array([x, y])

    # Posicionar alvos do Flávio em 2 colunas à direita
    for i, n in enumerate(flavio_exclusive):
        col = 0 if i % 2 == 0 else 1
        x = 0.42 if col == 0 else 0.85
        num_in_col = (len(flavio_exclusive) + 1) // 2 if col == 0 else len(flavio_exclusive) // 2
        rank_in_col = i // 2
        y = np.linspace(1.05, -1.05, num_in_col)[rank_in_col]
        pos[n] = np.array([x, y])

    # Posicionar nó-ponte compartilhado no centro exato (0, 0)
    for n in shared:
        pos[n] = np.array([0.0, 0.0])

    # Plotagem
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor('#FFFFFF')

    # Desenhar arestas curvadas com transparência e espessura ponderada
    for u, v, d in B.edges(data=True):
        w = d['weight']
        is_lula = d['campaign'] == "Lula"
        edge_color = COLOR_LULA if is_lula else COLOR_FLAVIO
        alpha = 0.45 if w == 1 else (0.65 if w < 10 else 0.85)
        lw = 0.8 + 1.2 * np.log1p(w)

        # Curvatura
        rad = 0.08 if is_lula else -0.08
        if v in shared:
            rad = 0.15 if is_lula else -0.15

        ax.annotate("",
                    xy=pos[v], xycoords='data',
                    xytext=pos[u], textcoords='data',
                    arrowprops=dict(arrowstyle="->,head_length=0.4,head_width=0.25",
                                    color=edge_color,
                                    lw=lw,
                                    alpha=alpha,
                                    connectionstyle=f"arc3,rad={rad}",
                                    shrinkA=22, shrinkB=16))

    # Desenhar nós de comando
    for n in ["c_Lula", "c_Flavio"]:
        d = B.nodes[n]
        ax.scatter(pos[n][0], pos[n][1], s=d['size'], c=d['color'], edgecolors="#1A1A1A",
                   linewidths=2.5, zorder=10, alpha=0.95)
        # Rótulo centralizado no nó de comando
        ax.text(pos[n][0], pos[n][1], d['label'], color="white", fontsize=10.5,
                fontweight='bold', ha='center', va='center', zorder=11,
                path_effects=[PathEffects.withStroke(linewidth=2, foreground='#1A1A1A')])

    # Desenhar nós alvos
    target_nodes = [n for n in B.nodes() if B.nodes[n]['node_type'] == 'target']
    for n in target_nodes:
        d = B.nodes[n]
        w = d['total_weight']
        node_size = 280 + 75 * np.sqrt(w) * 3
        marker = d['marker']
        c = d['color']

        # Destaque especial para nó compartilhado (ponte)
        if n in shared:
            ax.scatter(pos[n][0], pos[n][1], s=1600, c='#FF0000', edgecolors="#FFD700",
                       linewidths=3.5, marker='v', zorder=12, label="Nó-Ponte Compartilhado")
            ax.text(pos[n][0], pos[n][1] - 0.14, f"★ {d['label']} ★\n(Lula: w=10 | Flávio: w=2)",
                    fontsize=9.5, fontweight='bold', ha='center', va='top', zorder=13,
                    color="#900C3F",
                    bbox=dict(boxstyle="round,pad=0.25", fc="#FFF9C4", ec="#FBC02D", lw=1.2, alpha=0.95))
        else:
            ax.scatter(pos[n][0], pos[n][1], s=node_size, c=c, edgecolors="#333333",
                       linewidths=1.2, marker=marker, zorder=8, alpha=0.9)
            
            # Label
            x_offset = -0.02 if pos[n][0] < 0 else 0.02
            ha = 'right' if pos[n][0] < 0 else 'left'
            label_text = f"{d['label']} (w={w})"
            ax.text(pos[n][0] + x_offset, pos[n][1], label_text, fontsize=8.2,
                    ha=ha, va='center', zorder=9, color="#1A1A1A",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#CCCCCC", lw=0.6, alpha=0.85))

    # Regiões conceituais sutis no fundo
    ax.axvspan(-1.6, -0.15, color=COLOR_LULA, alpha=0.03, zorder=0)
    ax.axvspan(0.15, 1.6, color=COLOR_FLAVIO, alpha=0.03, zorder=0)
    ax.axvline(0, color="#BDBDBD", linestyle="--", lw=1.0, alpha=0.7, zorder=1)
    ax.text(0, 1.30, "ZONA DE CONVERGÊNCIA / INTERSEÇÃO", ha='center', va='center',
            fontsize=8.5, fontweight='bold', color="#757575",
            bbox=dict(boxstyle="round,pad=0.2", fc="#EEEEEE", ec="#BDBDBD", lw=0.8))

    # Títulos e Anotações
    ax.set_title("Topologia do Grafo Bipartido Direcionado $G = (C, T, E, w)$ de Mobilização Cross-Platform\n"
                 "Mapeamento de Ordens Táticas dos Canais Centrais do WhatsApp para Alvos Externos (2º Turno 2026)",
                 fontsize=13, fontweight='bold', pad=18, color="#212121")

    # Legendas Científicas
    legend_elements_plat = [
        Line2D([0], [0], marker='o', color='w', label='Instagram', markerfacecolor=COLOR_IG, markersize=9),
        Line2D([0], [0], marker='s', color='w', label='X (Twitter / Hashtag)', markerfacecolor=COLOR_X, markersize=9),
        Line2D([0], [0], marker='^', color='w', label='WhatsApp Satélite', markerfacecolor=COLOR_WA, markersize=9),
        Line2D([0], [0], marker='v', color='w', label='YouTube (Live/Debate)', markerfacecolor=COLOR_YT, markersize=9),
        Line2D([0], [0], marker='*', color='w', label='Google Search Bombing', markerfacecolor=COLOR_SEARCH, markersize=11),
        Line2D([0], [0], marker='D', color='w', label='Portal / Web / TSE', markerfacecolor=COLOR_WEB, markersize=8),
    ]

    legend_elements_edges = [
        Line2D([0], [1], color=COLOR_LULA, lw=3.0, label='Comando Exército do Lula ($w \geq 1$)'),
        Line2D([0], [1], color=COLOR_FLAVIO, lw=3.0, label='Comando Tropa do Flávio ($w \geq 1$)'),
        Patch(facecolor='#FFF9C4', edgecolor='#FBC02D', label='Nó-Ponte Bipartido Compartilhado'),
    ]

    leg1 = ax.legend(handles=legend_elements_plat, title="Plataformas dos Alvos ($T$)", loc="lower left",
                     fontsize=8.5, title_fontsize=9.5, framealpha=0.92, edgecolor="#BDBDBD")
    ax.add_artist(leg1)
    ax.legend(handles=legend_elements_edges, title="Origem de Comando ($C$)", loc="lower right",
              fontsize=8.5, title_fontsize=9.5, framealpha=0.92, edgecolor="#BDBDBD")

    ax.set_xlim(-1.65, 1.65)
    ax.set_ylim(-1.35, 1.40)
    ax.axis('off')
    plt.tight_layout()

    out_file1 = BRASNAM_DIR / "fig1_grafo_bipartido.png"
    plt.savefig(out_file1, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Figura 1 salva em: {out_file1}")


def generate_unipartite_projection_graph():
    print("[2/2] Gerando Grafo da Projeção Unipartida no Espaço de Alvos P = B^T B...")
    edges_file = OUTPUT_DIR / "bipartite_graph_edges.csv"
    df = pd.read_csv(edges_file)

    # Selecionar top alvos
    top_targets = df.groupby('Target')['Weight'].sum().sort_values(ascending=False).head(22).index.tolist()
    if 'YouTube Live/Video' not in top_targets:
        top_targets.append('YouTube Live/Video')

    df_sub = df[df['Target'].isin(top_targets)]

    # Construir grafo de projeção ponderada P = B^T B
    # Conecta dois nós se ambos foram ativados pela mesma campanha
    G = nx.Graph()

    for t in top_targets:
        # Metadados do nó
        sub = df[df['Target'] == t]
        plat = sub['Platform'].iloc[0]
        w_total = sub['Weight'].sum()
        c_lula = sub[sub['Source'].str.contains('LULA', case=False)]['Weight'].sum()
        c_flavio = sub[sub['Source'].str.contains('FLÁVIO', case=False)]['Weight'].sum()
        
        # Afiliação ideológica
        if c_lula > 0 and c_flavio > 0:
            affil = "Shared"
            node_color = "#9C27B0" # Roxo para híbrido/ponte
        elif c_lula > 0:
            affil = "Lula"
            node_color = COLOR_LULA
        else:
            affil = "Flavio"
            node_color = COLOR_FLAVIO

        G.add_node(t, label=clean_target_name(t), platform=plat,
                   weight=w_total, affil=affil, color=node_color)

    # Adicionar arestas ponderadas
    # Se ambos foram ativados por Lula, aresta com peso proporcional
    targets_list = list(G.nodes())
    for i in range(len(targets_list)):
        for j in range(i + 1, len(targets_list)):
            t1, t2 = targets_list[i], targets_list[j]
            # Co-ativação por Lula
            w1_l = df[(df['Target'] == t1) & (df['Source'].str.contains('LULA', case=False))]['Weight'].sum()
            w2_l = df[(df['Target'] == t2) & (df['Source'].str.contains('LULA', case=False))]['Weight'].sum()
            # Co-ativação por Flávio
            w1_f = df[(df['Target'] == t1) & (df['Source'].str.contains('FLÁVIO', case=False))]['Weight'].sum()
            w2_f = df[(df['Target'] == t2) & (df['Source'].str.contains('FLÁVIO', case=False))]['Weight'].sum()

            co_weight = 0
            edge_camp = None
            if w1_l > 0 and w2_l > 0:
                co_weight += np.sqrt(w1_l * w2_l)
                edge_camp = "Lula"
            if w1_f > 0 and w2_f > 0:
                co_weight += np.sqrt(w1_f * w2_f)
                edge_camp = "Flavio" if edge_camp is None else "Shared"

            if co_weight > 0:
                G.add_edge(t1, t2, weight=co_weight, camp=edge_camp)

    # Layout de mola (Spring Layout) com semente fixa para reprodutibilidade científica
    pos = nx.spring_layout(G, k=0.45, iterations=80, seed=42)

    # Plotagem
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor('#FFFFFF')

    # Desenhar arestas
    for u, v, d in G.edges(data=True):
        camp = d['camp']
        w = d['weight']
        if camp == "Lula":
            c = COLOR_LULA
            alpha = 0.25
        elif camp == "Flavio":
            c = COLOR_FLAVIO
            alpha = 0.35
        else:
            c = "#FF9800"
            alpha = 0.6
        lw = 0.6 + 0.8 * np.log1p(w)
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                color=c, lw=lw, alpha=alpha, zorder=1)

    # Desenhar nós
    for n in G.nodes():
        d = G.nodes[n]
        w = d['weight']
        node_size = 200 + 70 * np.sqrt(w) * 3
        c = d['color']
        
        if d['affil'] == "Shared":
            ax.scatter(pos[n][0], pos[n][1], s=1300, c='#FF0000', edgecolors="#FFD700",
                       linewidths=3.0, marker='v', zorder=5)
            ax.text(pos[n][0], pos[n][1] + 0.08, f"★ {d['label']} ★\n(Ponte Cross-Ideológica)",
                    fontsize=9.0, fontweight='bold', ha='center', va='bottom', zorder=6,
                    color="#B71C1C",
                    bbox=dict(boxstyle="round,pad=0.2", fc="#FFF9C4", ec="#FBC02D", lw=1.0, alpha=0.9))
        else:
            ax.scatter(pos[n][0], pos[n][1], s=node_size, c=c, edgecolors="#263238",
                       linewidths=1.2, zorder=3, alpha=0.9)
            ax.text(pos[n][0], pos[n][1] - 0.06, d['label'], fontsize=8.0,
                    ha='center', va='top', zorder=4, color="#212121",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#BDBDBD", lw=0.5, alpha=0.85))

    ax.set_title("Projeção Unipartida no Espaço de Alvos ($P = B^T B$): Detecção de Comunidades e Polarização Estrutural\n"
                 "Evidência de Segregação Topológica Completa com 'YouTube Live' como Único Vórtice de Convergência",
                 fontsize=12.5, fontweight='bold', pad=16, color="#212121")

    # Legenda
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Cluster Governista (Alvos Exército do Lula)', markerfacecolor=COLOR_LULA, markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Cluster Oposição (Alvos Tropa do Flávio)', markerfacecolor=COLOR_FLAVIO, markersize=10),
        Line2D([0], [0], marker='v', color='w', label='Nó-Ponte de Convergência (YouTube Live)', markerfacecolor='#FF0000', markeredgecolor='#FFD700', markersize=12),
        Line2D([0], [1], color=COLOR_LULA, lw=2.0, alpha=0.6, label='Co-ativação Intra-Governista'),
        Line2D([0], [1], color=COLOR_FLAVIO, lw=2.0, alpha=0.6, label='Co-ativação Intra-Oposição')
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=8.5, framealpha=0.92, edgecolor="#BDBDBD")

    ax.axis('off')
    plt.tight_layout()

    out_file4 = BRASNAM_DIR / "fig4_taxonomia_missoes.png" # ou salvar como fig4_taxonomia_missoes.png para substituir o placeholder!
    plt.savefig(out_file4, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Projeção Unipartida salva em: {out_file4}")

if __name__ == "__main__":
    generate_true_bipartite_graph()
    generate_unipartite_projection_graph()
