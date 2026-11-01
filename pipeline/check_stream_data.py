import json
from pathlib import Path

base_dir = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026")
art_dir = Path(r"C:\Users\alkaw\.gemini\antigravity\brain\45cf57d5-3ace-4cf4-85d3-6f3c4f711ed8")

with open(base_dir / "output" / "topic_streamgraph_timeseries.json", "r", encoding="utf-8") as f:
    stream_data = json.load(f)

print("Loaded topic_streamgraph_timeseries.json:")
print("Time labels count:", len(stream_data["time_labels"]))
print("Time labels:", stream_data["time_labels"])

# Let's inspect examples in lula and flavio
lula_ex_map = {}
for i, ex in enumerate(stream_data["exercito_do_lula"]["examples"]):
    if ex:
        lula_ex_map[i] = ex

flavio_ex_map = {}
for i, ex in enumerate(stream_data["tropa_do_flavio"]["examples"]):
    if ex:
        flavio_ex_map[i] = ex

x_tags_map = {}
for i, tags in enumerate(stream_data["x_brazil_trends"]["top_tags"]):
    if tags:
        x_tags_map[i] = tags

# Define enriched milestones
milestones = [
    {
        "bin_index": 8,
        "date": "18/10 13h",
        "code": "M1a",
        "short": "M1a: Declaração 'Anti-Algoritmo'",
        "desc": "Janones declara: 'Não vou mais depender das redes. Vou soltar conteúdo exclusivo aqui e vocês distribuam pra chegar no Brasil inteiro'."
    },
    {
        "bin_index": 10,
        "date": "18/10 21h",
        "code": "M1b",
        "short": "M1b: Debate Band + 1º Google Bombing",
        "desc": "Pico de 279 msgs/dia; ordem explícita para buscar 'Flávio miliciano / CV' no Google para manipular o painel exibido ao vivo na Band."
    },
    {
        "bin_index": 15,
        "date": "19/10 18h",
        "code": "M2",
        "short": "M2: Crise Nordeste & Reels Nikolas >100M",
        "desc": "Tropa do Flávio impulsiona Reels de Nikolas Ferreira sobre o Nordeste e lança tags #FalaNordeste e #naoCalemOsNordestino."
    },
    {
        "bin_index": 20,
        "date": "20/10 16h",
        "code": "M3",
        "short": "M3: Busca Diária + Queda IA Google",
        "desc": "Janones institucionaliza 'um termo de busca a cada 24h' (#PesquiseBolsonaroMandouMatarLula), derrubando o Google AI Overview."
    },
    {
        "bin_index": 26,
        "date": "21/10 15h",
        "code": "M4",
        "short": "M4: Ofensiva Pandemia & Liminar TSE (IA)",
        "desc": "3ª onda de Google Bombing ('Flávio Bolsonaro Esquema Pandemia'); Tropa do Flávio passa a aplicar rótulo 'Conteúdo de IA' após liminar."
    },
    {
        "bin_index": 32,
        "date": "22/10 15h",
        "code": "M5",
        "short": "M5: Bombing 'Talvane' (Google=100 / Wiki 1393x)",
        "desc": "Ordem sem link leva 'Bolsonaro Talvane Albuquerque' a 100 no Google Trends, #1 no X em 24 min e 4.181 leituras na Wikipédia."
    },
    {
        "bin_index": 39,
        "date": "23/10 18h–22h",
        "code": "M6",
        "short": "M6: Marca 10M + Debate Globo + Live 24h",
        "desc": "Exército do Lula bate 10 milhões de inscritos após gamificar ameaça de bloqueio de 48h; guerra em tempo real no Debate da Globo."
    },
    {
        "bin_index": 44,
        "date": "24/10 14h–19h",
        "code": "M7",
        "short": "M7: Véspera — Rua, Fiscais PL & AIJE Meta",
        "desc": "Caminhadas de véspera, #SoMaisUmVotoProLula, convocação em fiscaisdopl.com.br e ação judicial contra a Meta por assimetria algorítmica."
    },
    {
        "bin_index": 49,
        "date": "25/10 10h–15h",
        "code": "M8",
        "short": "M8: Dia D: Bloqueio de Ônibus & Prisão TRE-BA",
        "desc": "Mobilização de Gil do Vigor, disparo de denúncias de redução de frota de ônibus em Salvador e SP (#DeixemONordesteVotar, #3 no X) e prisão do secretário de mobilidade pelo TRE-BA."
    },
    {
        "bin_index": 51,
        "date": "25/10 16h–20h",
        "code": "M9",
        "short": "M9: Prorrogação de Votação & Reverse Engineering",
        "desc": "Ordem de comando para estender horário por 2h; tutorial para burlar algoritmo do Instagram ('deixem rodar até o fim, mandem no direct'); Tropa do Flávio comemora em tom de apreensão/oração."
    }
]

print("Milestones configured:", len(milestones))
