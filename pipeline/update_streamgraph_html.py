import json
import re
from pathlib import Path

base_dir = Path(r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026")
art_dir = Path(r"C:\Users\alkaw\.gemini\antigravity\brain\45cf57d5-3ace-4cf4-85d3-6f3c4f711ed8")

with open(base_dir / "output" / "topic_streamgraph_timeseries.json", "r", encoding="utf-8") as f:
    stream_data = json.load(f)

time_labels = stream_data["time_labels"]
lula_smooth = stream_data["exercito_do_lula"]["smooth"]
flavio_smooth = stream_data["tropa_do_flavio"]["smooth"]
x_smooth = stream_data["x_brazil_trends"]["smooth"]
ext_curves = stream_data["external_search_telemetry"]

topics = [
    { "name": "Crime Organizado / Caso Talvane & Milícia", "short": "Crime / Talvane / Milícia", "color": "#8E24AA" },
    { "name": "Guerra Algorítmica / Google Bombing / TSE & IA", "short": "Algoritmos / Google Bombing / TSE", "color": "#00897B" },
    { "name": "Debates, Lives & Apuração (Band / Globo / Janones / 24h)", "short": "Debates TV & Apuração (Band/Globo/24h)", "color": "#1E88E5" },
    { "name": "Disputa pelo Nordeste, Piauí & Narrativa de 'Censura'", "short": "Nordeste / Piauí / 'Censura'", "color": "#FB8C00" },
    { "name": "Escândalos, Economia & Direitos (Pandemia / INSS / Lancha / Sigilo)", "short": "Escândalos / Pandemia / INSS / Lancha", "color": "#E53935" },
    { "name": "Mobilização de Rua, Fila / Transporte, Prorrogação & Voto", "short": "Atos de Rua / Transporte / Prorrogação", "color": "#FBC02D" }
]

milestones = [
    { "bin_index": 8, "date": "18/10 13h", "code": "M1a", "short": "M1a: Declaração 'Anti-Algoritmo'", "desc": "Janones declara: 'Não vou mais depender das redes. Vou soltar conteúdo exclusivo aqui e vocês distribuam pra chegar no Brasil inteiro'." },
    { "bin_index": 10, "date": "18/10 21h", "code": "M1b", "short": "M1b: Debate Band + 1º Google Bombing", "desc": "Pico de 279 msgs/dia; ordem explícita para buscar 'Flávio miliciano / CV' no Google para manipular o painel exibido ao vivo na Band." },
    { "bin_index": 15, "date": "19/10 18h", "code": "M2", "short": "M2: Crise Nordeste & Reels Nikolas >100M", "desc": "Tropa do Flávio impulsiona Reels de Nikolas Ferreira sobre o Nordeste e lança tags #FalaNordeste e #naoCalemOsNordestino." },
    { "bin_index": 20, "date": "20/10 16h", "code": "M3", "short": "M3: Busca Diária + Queda IA Google", "desc": "Janones institucionaliza 'um termo de busca a cada 24h' (#PesquiseBolsonaroMandouMatarLula), derrubando o Google AI Overview." },
    { "bin_index": 26, "date": "21/10 15h", "code": "M4", "short": "M4: Ofensiva Pandemia & Liminar TSE (IA)", "desc": "3ª onda de Google Bombing ('Flávio Bolsonaro Esquema Pandemia'); Tropa do Flávio passa a aplicar rótulo 'Conteúdo de IA' após liminar." },
    { "bin_index": 32, "date": "22/10 15h", "code": "M5", "short": "M5: Bombing 'Talvane' (Google=100 / Wiki 1393x)", "desc": "Ordem sem link leva 'Bolsonaro Talvane Albuquerque' a 100 no Google Trends, #1 no X em 24 min e 4.181 leituras na Wikipédia." },
    { "bin_index": 39, "date": "23/10 18h–22h", "code": "M6", "short": "M6: Marca 10M + Debate Globo + Live 24h", "desc": "Exército do Lula bate 10 milhões de inscritos após gamificar ameaça de bloqueio de 48h; guerra em tempo real no Debate da Globo." },
    { "bin_index": 44, "date": "24/10 14h–19h", "code": "M7", "short": "M7: Véspera — Rua, Fiscais PL & AIJE Meta", "desc": "Caminhadas de véspera, #SoMaisUmVotoProLula, convocação em fiscaisdopl.com.br e ação judicial contra a Meta por assimetria algorítmica." },
    { "bin_index": 49, "date": "25/10 10h–15h", "code": "M8", "short": "M8: Dia D: Bloqueio de Ônibus & Prisão TRE-BA", "desc": "Mobilização de Gil do Vigor, denúncias de redução de frota em Salvador e SP (#DeixemONordesteVotar #3 no X) e ordem de prisão pelo TRE-BA." },
    { "bin_index": 51, "date": "25/10 16h–20h", "code": "M9", "short": "M9: Prorrogação de 2h & Engenharia Reversa", "desc": "Luta pela prorrogação de votação por 2h; tutorial para enganar algoritmo do Instagram ('deixem rodar até o final'); Tropa do Flávio em oração/tensão." }
]

lula_examples = {
    3: ["[17/10 20:43] Se tiver algum soldado substituto está autorizada a substituição! Passe o celular pra ele..."],
    7: ["[18/10 10:06] SUBAM TODOS NO X: #HojeTemShowDoLula"],
    8: ["[18/10 13:36] Não vou mais depender das redes. Vou soltar conteúdo exclusivo aqui e vocês distribuam...", "[18/10 14:15] Canal do Lula • 1,8 mi seguidores (Convocação de Spillover)"],
    9: ["[18/10 21:05] Início da operação de guerra no Debate da Band (279 mensagens no dia)"],
    10: ["[18/10 22:10] Vão no Google e pesquisem: Flavio miliciano, Flávio ana Clara, Flávio comando Vermelho. A Band tá anunciando ao vivo!"],
    20: ["[20/10 16:47] A ESTRATÉGIA QUE DECIDIRÁ AS ELEIÇÕES!! A cada 24h enviarei um novo termo de pesquisa (#PesquiseBolsonaroMandouMatarLula)"],
    21: ["[20/10 18:26] Petrolina e Juazeiro! EXPLODIU!!!! #NordestinosComLula"],
    26: ["[21/10 15:56] Pesquisem no Google: FLÁVIO BOLSONARO ESQUEMA PANDEMIA"],
    32: ["[22/10 14:14] Derrubamos a resposta de IA do Google! Vamos subir outra busca já já...", "[22/10 15:36] Joguem todo mundo no Google agora: Bolsonaro Talvane Albuquerque e vejam o que acontece"],
    37: ["[23/10 10:15] Nosso canal deverá sair do ar ainda hoje por decisão do TSE... Meta: 10 milhões de inscritos!"],
    38: ["[23/10 14:59] O CANAL ESTÁ FECHADO ATÉ ATINGIR 10 MILHÕES DE MEMBROS!"],
    39: ["[23/10 17:57] BATEMOS 10 MILHÕES DE INSCRITOS! Início da cobertura do Debate da Globo"],
    40: ["[23/10 22:03] Cobertura ao vivo do Debate da Globo + Caso Ana Clara + Início da Live de 24h"],
    41: ["[24/10 02:14] #ViroteDoExercito e #SoMaisUmVotoProLula na madrugada"],
    44: ["[24/10 14:36] VAMOS GANHAR NO WHATSAPP! Mutirão final de véspera"],
    45: ["[24/10 19:13] Lula na Paulista: São Paulo tomada por mais de dois milhões de brasileiros!"],
    49: ["[25/10 10:43] Gil do Vigor: 'Vamos votar pra manter nosso direito de escolha!!!' (166.851 reações)", "[25/10 13:55] GloboNews: Presidente do TRE-BA determina prisão do secretário de Salvador por travar 75 ônibus"],
    50: ["[25/10 15:47] ATENÇÃO BATALHÃO DE SALVADOR: Ônibus voltou ao normal e é de graça! EXPLODAM! AGORA!", "[25/10 15:53] Caetano Veloso: Crime eleitoral na Bahia e SP! EXIJAM EXTENSÃO DOS HORÁRIOS DE VOTAÇÃO!"],
    51: ["[25/10 17:03] 1. Estamos lutando para estender a votação por mais 2h. 2. Carona solidária! 3. Denunciem prefeitos!", "[25/10 17:16] Manda no aviãozinho pra TODOS no direct, depois no WhatsApp, e DEIXEM O VÍDEO RODAR ATÉ O FINAL pro algoritmo!"],
    52: ["[25/10 19:28] André Janones no Instagram: 'CONVOCAÇÃO!!!' durante o início da apuração oficial"]
}

flavio_examples = {
    10: ["[18/10 22:13] Tropaaaaaa Bora pra cimaaaaa! Dispara pra todo lugar (Debate da Band)"],
    13: ["[19/10 10:48] Nikolas Ferreira - Oficial • Canal • 77 mil seguidores • ATIVE A NOTIFICAÇÃO AGORA"],
    15: ["[19/10 21:05] Coordenador Rogério Marinho rebate ataques no Nordeste"],
    20: ["[20/10 15:13] Nikolas Ferreira no Instagram: 'O Nordeste que foi esquecido' (>100M views)", "[20/10 15:19] Subam no Twitter: NÃO CALEM OS NORDESTINOS (#FalaNordeste)"],
    21: ["[20/10 19:24] O petista calou a Herminia. Vão censurar esse vídeo aqui também?"],
    26: ["[21/10 14:15] Ninguém cala o Nordeste + Primeiras postagens com selo 'Conteúdo de IA'"],
    27: ["[21/10 20:27] AO VIVO EM FORTALEZA: Flávio Bolsonaro, Nikolas e André Fernandes no Bloco do 22"],
    31: ["[22/10 10:47] VOCÊ PODE AJUDAR A FISCALIZAR AS ELEIÇÕES! Cadastro de fiscais"],
    37: ["[23/10 11:52] Seja fiscal de urna · Cadastro do Partido Liberal (fiscaisdopl.com.br)"],
    39: ["[23/10 20:26] AO VIVO: Bloquinho do 22 em Fortaleza + Cobertura do Debate da Globo"],
    40: ["[23/10 23:30] Nikolas Ferreira no Instagram: 'Lula vai acabar com a polícia. Game over.'"],
    44: ["[24/10 15:40] Lucas Pavanato e Nikolas Ferreira: Convocação final para votação no domingo (22)"],
    48: ["[25/10 00:00] Contagem regressiva da meia-noite (26.563 reações)"],
    50: ["[25/10 14:29] Nikolas Ferreira no Instagram: 'Esse é o meu maior desejo.' (8.892 reações)"],
    51: ["[25/10 18:22] Nikolas Ferreira no Instagram: 'Isso é urgente mesmo.' (Reações 😢 em 2º lugar, 8.363 reações)"]
}

data_js = "const DATA = " + json.dumps({
    "time_labels": time_labels,
    "topics": topics,
    "milestones": milestones,
    "lula_smooth": lula_smooth,
    "flavio_smooth": flavio_smooth,
    "lula_examples": lula_examples,
    "flavio_examples": flavio_examples
}, indent=2, ensure_ascii=False) + ";"

# Function to replace in an HTML file
for html_path in [art_dir / "streamgraph_eleicoes_2026.html", art_dir / "streamgraph_inline.html"]:
    if not html_path.exists():
        continue
    content = html_path.read_text(encoding="utf-8")
    
    # Replace const DATA = { ... };
    content = re.sub(r"const DATA = \{[\s\S]*?\n    \};", data_js, content)
    
    # Update title badge / text if present
    content = re.sub(r"N\s*=\s*1\.?057", "N = 1.085", content)
    content = re.sub(r"N\s*=\s*916", "N = 939", content)
    content = re.sub(r"N\s*=\s*141", "N = 146", content)
    content = re.sub(r"916 mensagens", "939 mensagens", content)
    content = re.sub(r"141 mensagens", "146 mensagens", content)
    content = re.sub(r"1\.057 mensagens", "1.085 mensagens", content)
    
    html_path.write_text(content, encoding="utf-8")
    print(f"Updated {html_path.name}")

print("[OK] Streamgraph HTML artifacts updated successfully!")
