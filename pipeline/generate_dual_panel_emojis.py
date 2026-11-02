import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import networkx as nx
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.patheffects as PathEffects
from pathlib import Path

# Paths
ROOT_DIR = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026")
PAPERS_DIR = ROOT_DIR / "papers"
BRASNAM_DIR = PAPERS_DIR / "paper1_brasnam_sbc"

# Fontes
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
emoji_prop = fm.FontProperties(fname=r'C:\Windows\Fonts\seguiemj.ttf')

# Cores
COLOR_LULA = "#C62828"    # Vermelho
COLOR_FLAVIO = "#1565C0"  # Azul
BG_COLOR = "#FAFAFA"

# Dados Consolidados
# Lula: N = 1.182 | Flávio: N = 149
emoji_data = [
    {"name": "Coração",     "char": "❤️", "lula": 70.7, "flavio": 48.3, "desc": "Adesão Afetiva"},
    {"name": "Positivo",    "char": "👍", "lula": 69.6, "flavio": 50.3, "desc": "Aprovação Geral"},
    {"name": "Continência", "char": "🫡", "lula": 61.3, "flavio":  0.0, "desc": "Disciplina Militar (Exclusivo Lula)"},
    {"name": "Oração",      "char": "🙏", "lula": 36.6, "flavio": 40.9, "desc": "Apelo Religioso / Fé"},
    {"name": "Deboche",     "char": "😂", "lula": 16.2, "flavio": 41.6, "desc": "Ironia / Riso (2.5x Flávio)"},
    {"name": "Espanto",     "char": "😮", "lula":  7.5, "flavio": 10.7, "desc": "Surpresa / Alerta"},
    {"name": "Tristeza",    "char": "😢", "lula":  3.0, "flavio": 12.1, "desc": "Lamento / Choro (4x Flávio)"}
]

def generate_dual_panel_figure():
    print("[*] Gerando Figura 3 em Painel Duplo (Rede Afetiva + Barras Divergentes)...")

    fig = plt.figure(figsize=(16, 7.5), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    # Grid de subplots: ax1 (Rede Afetiva à esquerda), ax2 (Barras divergentes à direita)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.18)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    ax1.set_facecolor(BG_COLOR)
    ax2.set_facecolor(BG_COLOR)

    # =========================================================================
    # PAINEL (a): SUBGRAFO DE REDE AFETIVA BIPARTIDA G_aff = (C, Emojis, E, W)
    # =========================================================================
    ax1.set_title("(a) Topologia da Rede Social Afetiva $G_{\\text{aff}} = (C, \\mathcal{E}, W)$\nMapeamento de Atração e Centralidade Emocional das Tropas",
                  fontsize=11.5, fontweight='bold', pad=14, color="#212121")

    # Coordenadas fixas e harmônicas para layout de rede afetiva
    # Hubs de comando nas pontas
    pos_c_lula = np.array([-1.25, 0.0])
    pos_c_flavio = np.array([1.25, 0.0])

    # Posicionamento dos nós de emojis no espaço central
    # Emojis compartilhados no centro vertical
    # Continência inclinada para o lado do Lula
    # Deboche e Tristeza inclinados para o lado do Flávio
    emoji_positions = {
        "❤️": np.array([-0.05,  1.10]), # Topo compartilhado
        "👍": np.array([ 0.05,  0.55]), # Centro-alto compartilhado
        "🫡": np.array([-0.55,  0.00]), # Exclusivo Lula (puxado forte para esquerda)
        "🙏": np.array([ 0.05, -0.05]), # Centro neutro
        "😂": np.array([ 0.55, -0.55]), # Forte Flávio (puxado para direita)
        "😮": np.array([-0.10, -0.65]), # Neutro baixo
        "😢": np.array([ 0.50, -1.15])  # Flávio baixo (puxado para direita)
    }

    # Desenhar arestas ponderadas com arcos curvados
    for d in emoji_data:
        char = d['char']
        pos_e = emoji_positions[char]
        
        # Aresta Lula -> Emoji
        w_lula = d['lula']
        if w_lula > 0:
            lw_l = 0.8 + 2.8 * (w_lula / 75.0)
            alpha_l = 0.4 + 0.45 * (w_lula / 75.0)
            rad_l = 0.08 if pos_e[1] >= 0 else -0.08
            ax1.annotate("",
                         xy=pos_e, xycoords='data',
                         xytext=pos_c_lula, textcoords='data',
                         arrowprops=dict(arrowstyle="->,head_length=0.35,head_width=0.22",
                                         color=COLOR_LULA,
                                         lw=lw_l,
                                         alpha=alpha_l,
                                         connectionstyle=f"arc3,rad={rad_l}",
                                         shrinkA=26, shrinkB=18))

        # Aresta Flávio -> Emoji
        w_flavio = d['flavio']
        if w_flavio > 0:
            lw_f = 0.8 + 2.8 * (w_flavio / 75.0)
            alpha_f = 0.4 + 0.45 * (w_flavio / 75.0)
            rad_f = -0.08 if pos_e[1] >= 0 else 0.08
            ax1.annotate("",
                         xy=pos_e, xycoords='data',
                         xytext=pos_c_flavio, textcoords='data',
                         arrowprops=dict(arrowstyle="->,head_length=0.35,head_width=0.22",
                                         color=COLOR_FLAVIO,
                                         lw=lw_f,
                                         alpha=alpha_f,
                                         connectionstyle=f"arc3,rad={rad_f}",
                                         shrinkA=22, shrinkB=18))

    # Desenhar nós de comando C
    ax1.scatter(pos_c_lula[0], pos_c_lula[1], s=2800, c=COLOR_LULA, edgecolors="#1A1A1A",
                linewidths=2.5, zorder=10, alpha=0.95)
    ax1.text(pos_c_lula[0], pos_c_lula[1], "EXÉRCITO\nDO LULA\n(10M seg.)", color="white",
             fontsize=9.0, fontweight='bold', ha='center', va='center', zorder=11,
             path_effects=[PathEffects.withStroke(linewidth=2, foreground='#1A1A1A')])

    ax1.scatter(pos_c_flavio[0], pos_c_flavio[1], s=2000, c=COLOR_FLAVIO, edgecolors="#1A1A1A",
                linewidths=2.5, zorder=10, alpha=0.95)
    ax1.text(pos_c_flavio[0], pos_c_flavio[1], "TROPA\nDO FLÁVIO\n(1.9M seg.)", color="white",
             fontsize=8.5, fontweight='bold', ha='center', va='center', zorder=11,
             path_effects=[PathEffects.withStroke(linewidth=2, foreground='#1A1A1A')])

    # Desenhar nós de emojis com círculos e ícones reais
    for d in emoji_data:
        char = d['char']
        name = d['name']
        pos_e = emoji_positions[char]
        
        # Cor de destaque de borda conforme dominância
        diff = d['lula'] - d['flavio']
        if d['flavio'] == 0:
            border_c = "#D32F2F"
            fc = "#FFEBEE"
            lw = 3.0
        elif diff > 15:
            border_c = COLOR_LULA
            fc = "#FFFFFF"
            lw = 1.8
        elif diff < -15:
            border_c = COLOR_FLAVIO
            fc = "#FFFFFF"
            lw = 1.8
        else:
            border_c = "#757575"
            fc = "#F5F5F5"
            lw = 1.2

        # Círculo base do nó
        ax1.scatter(pos_e[0], pos_e[1], s=1200, c=fc, edgecolors=border_c,
                    linewidths=lw, zorder=12, alpha=0.95)
        # Ícone do Emoji centralizado
        ax1.text(pos_e[0], pos_e[1], char, fontproperties=emoji_prop,
                 fontsize=20, ha='center', va='center', zorder=13)
        # Rótulo de texto abaixo
        ax1.text(pos_e[0], pos_e[1] - 0.15, name, fontsize=8.0,
                 fontweight='bold', ha='center', va='top', zorder=14, color="#212121",
                 bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#CCCCCC", lw=0.5, alpha=0.85))

    # Destaque de Continência Militar (Exclusiva)
    pos_salute = emoji_positions["🫡"]
    ax1.annotate("Marcador Exclusivo\n(61.3% vs. 0.0%)",
                 xy=(pos_salute[0], pos_salute[1] + 0.14),
                 xytext=(pos_salute[0] - 0.15, pos_salute[1] + 0.40),
                 arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=1.2),
                 fontsize=8.0, fontweight='bold', color="#B71C1C",
                 bbox=dict(boxstyle="round,pad=0.2", fc="#FFF9C4", ec="#FBC02D", lw=0.8))

    ax1.set_xlim(-1.55, 1.55)
    ax1.set_ylim(-1.45, 1.45)
    ax1.axis('off')

    # =========================================================================
    # PAINEL (b): BARRAS DIVERGENTES ESPELHADAS (BUTTERFLY CHART)
    # =========================================================================
    ax2.set_title("(b) Perfil Comparativo Divergente de Reações (% de Mensagens)\nContraste Direto entre Exército do Lula e Tropa do Flávio",
                  fontsize=11.5, fontweight='bold', pad=14, color="#212121")

    # Ordem das categorias (de baixo para cima)
    cats = list(reversed(emoji_data))
    y_pos = np.arange(len(cats))

    lula_vals = [c['lula'] for c in cats]
    flavio_vals = [c['flavio'] for c in cats]

    # Barras Lula (para a esquerda, valores negativos no eixo para espelhar)
    bars_l = ax2.barh(y_pos, [-v for v in lula_vals], height=0.55, color=COLOR_LULA,
                      edgecolor="#1A1A1A", linewidth=0.8, alpha=0.88, label="Exército do Lula (N=1.182)")
    # Barras Flávio (para a direita)
    bars_f = ax2.barh(y_pos, flavio_vals, height=0.55, color=COLOR_FLAVIO,
                      edgecolor="#1A1A1A", linewidth=0.8, alpha=0.88, label="Tropa do Flávio (N=149)")

    # Rótulos de dados numéricos nas barras
    for i, (vl, vf) in enumerate(zip(lula_vals, flavio_vals)):
        # Lula (esquerda)
        if vl > 0:
            ax2.text(-vl - 2.5, i, f"{vl:.1f}%", ha='right', va='center',
                     fontsize=8.5, fontweight='bold', color="#B71C1C")
        else:
            ax2.text(-2.5, i, "0.0%", ha='right', va='center', fontsize=8.5, color="#757575")

        # Flávio (direita)
        if vf > 0:
            ax2.text(vf + 2.5, i, f"{vf:.1f}%", ha='left', va='center',
                     fontsize=8.5, fontweight='bold', color="#0D47A1")
        else:
            ax2.text(2.5, i, "0.0%", ha='left', va='center', fontsize=8.5, color="#757575")

    # Linha central divisória
    ax2.axvline(0, color="#424242", linewidth=1.5, linestyle="-")

    # Eixo Y sem texto, pois colocaremos o Emoji no centro
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([])

    # Colocar ícones dos emojis e nomes na coluna central
    for i, c in enumerate(cats):
        # Caixa central com emoji e texto
        ax2.text(0, i + 0.12, c['char'], fontproperties=emoji_prop,
                 fontsize=15, ha='center', va='center', zorder=20)
        ax2.text(0, i - 0.22, c['name'], fontsize=7.5, fontweight='bold',
                 ha='center', va='center', color="#212121", zorder=20,
                 bbox=dict(boxstyle="round,pad=0.15", fc="#FFFFFF", ec="#BDBDBD", lw=0.6, alpha=0.9))

    # Formatação do eixo X
    ax2.set_xlim(-90, 90)
    xticks = [-80, -60, -40, -20, 0, 20, 40, 60, 80]
    ax2.set_xticks(xticks)
    ax2.set_xticklabels([f"{abs(x)}%" for x in xticks], fontsize=8.5)
    ax2.set_xlabel("← % Mensagens (Exército do Lula) | % Mensagens (Tropa do Flávio) →",
                   fontsize=9.0, fontweight='bold', labelpad=8, color="#333333")

    ax2.grid(axis='x', linestyle='--', alpha=0.45)
    ax2.legend(loc="upper right", fontsize=8.2, framealpha=0.92, edgecolor="#BDBDBD")

    # Salvar figura
    plt.tight_layout()
    out_file = BRASNAM_DIR / "fig3_radar_emojis.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Figura 3 Painel Duplo salva em: {out_file}")

if __name__ == "__main__":
    generate_dual_panel_figure()
