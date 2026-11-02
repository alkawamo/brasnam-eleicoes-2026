# 🇧🇷 Mobilização Política e Engenharia Algorítmica em Canais de WhatsApp: Eleições Presidenciais de 2026

[![Ciência Aberta](https://img.shields.io/badge/Open_Science-FAIR_Data-blue.svg)](https://en.wikipedia.org/wiki/FAIR_data)
[![Licença: CC-BY 4.0](https://img.shields.io/badge/Dataset_License-CC--BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Código: MIT](https://img.shields.io/badge/Code_License-MIT-green.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)

Repositório de dados abertos e pipeline computacional para coleta, processamento, análise estrutural de redes, codificação multimodal, cascata de conversão de audiência e modelagem temporal de choques algorítmicos nos **Canais de Transmissão do WhatsApp (*WhatsApp Channels*)** durante o 2º turno das Eleições Presidenciais Brasileiras de 2026.

**Pesquisador Responsável:**  
Prof. Dr. **André Luiz Satoshi Kawamoto**  
*Departamento Acadêmico de Computação (DACOM)*  
*Universidade Tecnológica Federal do Paraná (UTFPR) — Campus Campo Mourão*  
Contato: `kawamoto@utfpr.edu.br`

---

## 🗂️ Estrutura do Repositório

```text
├── BRASNAM_2026_Colab_Pipeline.ipynb     # Notebook interativo completo (Google Colab / Jupyter)
├── data/                                 # Datasets limpos e séries temporais consolidadas
│   ├── master_all_messages.csv           # Corpus integral de 1.331 mensagens (Lula + Flávio)
│   ├── master_exercito_do_lula.csv       # Corpus completo do Exército do Lula (1.182 msgs; 36,0M reações)
│   ├── master_tropa_do_flavio.csv        # Corpus completo da Tropa do Flávio (149 msgs; 510,3k reações)
│   ├── followers_live_timeseries.csv     # Telemetria horária de seguidores (10M vs. 1,9M churn)
│   └── x_twitter_brazil_trending_timeseries.csv # Séries temporais dos Trending Topics do X Brasil
├── pipeline/                             # Scripts de processamento, análise e visualização
│   ├── analyze_channels.py               # Ingestão, deduplicação e exportação de grafos bipartidos
│   ├── analyze_discourse.py              # Análise computacional de discurso (CADS / Framing)
│   ├── generate_advanced_analytics.py    # Codificação multimodal, cascata de conversão, IRF e Streamgraph
│   ├── monitor_followers.py              # Sonda HTTP horária de seguidores em canais públicos
│   ├── fetch_x_trends_std.py             # Coletor de tendências horárias do X/Twitter
│   └── generate_streamgraph.py           # Motor temporal do Streamgraph (ThemeRiver)
├── scraper/                              # Extratores de DOM do WhatsApp Web
│   └── whatsapp_channel_extractor.js     # Script de injeção no DOM para captura retroativa
└── output/                               # Resultados estruturados (JSON, CSVs de grafo e figuras 300 DPI)
    ├── figures/                          # Figuras analíticas de alta resolução (300 DPI)
    ├── bipartite_graph_edges.csv         # Arestas ponderadas do grafo bipartido C2 -> Alvos
    ├── brasnam_comparative_summary.json  # Métricas estruturais comparadas
    └── discourse_analysis_janonismo.json # Resultados completos da mineração léxico-semântica
```

---

## 📖 Dicionário de Dados (Codebook)

### `data/master_all_messages.csv`
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `channel` | String | Nome do canal emissor (`EXÉRCITO DO LULA` ou `TROPA DO FLÁVIO 🇧🇷`) |
| `msg_id` | String | Identificador único criptográfico atribuído pelo WhatsApp |
| `date` | String | Data local de envio (`DD/MM/AAAA`) |
| `time` | String | Horário local de envio (`HH:MM` BRT) |
| `datetime_local` | String | Timestamp ISO local da mensagem |
| `datetime_utc` | String | Timestamp ISO normalizado UTC |
| `mission_type` | String | Classificação na taxonomia tática de comando e controle |
| `text` | String | Texto integral da mensagem |
| `urls` | String | Lista delimitada de hiperlinks externos (*deep links* para IG/YT/X/TikTok) |
| `hashtags` | String | Lista delimitada de hashtags identificadas |
| `has_media` | Boolean | Indicador de presença de anexos multimídia (áudios confidenciais, imagens, vídeos) |
| `has_video` | Boolean | Presença de mídia em formato de vídeo |
| `raw_reactions` | JSON | Vetor estruturado dos emojis de reação e suas respectivas contagens no DOM |

---

## ⚖️ Conformidade Ética e Proteção de Dados (LGPD e TSE)

* **Lei Geral de Proteção de Dados (Lei nº 13.709/2018):** Os dados coletados originam-se exclusivamente de **Canais de Transmissão Oficiais Públicos**, unidirecionais e devidamente cadastrados perante a Justiça Eleitoral (Resolução TSE nº 23.610). 
* **Privacidade dos Usuários:** A arquitetura dos Canais do WhatsApp não disponibiliza lista pública de membros, números de telefone, fotos de perfil ou mensagens de cidadãos comuns. Portanto, **nenhum dado pessoal sensível (PII) é capturado, armazenado ou distribuído**.

---

## 🚀 Como Reproduzir

### 1. Clonar o repositório e instalar dependências
```bash
git clone https://github.com/alkawamo/brasnam-eleicoes-2026.git
cd brasnam-eleicoes-2026
pip install -r requirements.txt
```

### 2. Executar a análise de canais e atualização das bases
```bash
python pipeline/analyze_channels.py
```

### 3. Executar a análise computacional de discurso (CADS)
```bash
python pipeline/analyze_discourse.py
```

### 4. Gerar as figuras analíticas avançadas (Multimodal, Conversão, IRF e Streamgraph)
```bash
python pipeline/generate_advanced_analytics.py
```

---

## 📝 Como Citar este Repositório / Dataset

Caso utilize estes dados ou scripts em pesquisas acadêmicas, favor citar:

```bibtex
@misc{kawamoto2026_whatsapp_dataset,
  author       = {Andr{'e} Luiz Satoshi Kawamoto},
  title        = {Dataset e Pipeline de An{'a}lise de Canais de Transmiss{\~a}o do WhatsApp: 2º Turno das Elei{\c{c}}{\~o}es Presidenciais de 2026},
  year         = {2026},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/alkawamo/brasnam-eleicoes-2026}}
}
```
