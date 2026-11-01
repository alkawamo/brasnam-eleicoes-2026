# 🇧🇷 Mobilização Política e Engenharia Algorítmica em Canais de WhatsApp: Eleições Presidenciais de 2026

[![Ciência Aberta](https://img.shields.io/badge/Open_Science-FAIR_Data-blue.svg)](https://en.wikipedia.org/wiki/FAIR_data)
[![Licença: CC-BY 4.0](https://img.shields.io/badge/Dataset_License-CC--BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Código: MIT](https://img.shields.io/badge/Code_License-MIT-green.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)

Repositório oficial com os scripts de extração, bases de dados longitudinais consolidadas, análises de redes e pacotes de replicação para as pesquisas sobre os **Canais de Transmissão do WhatsApp (*WhatsApp Channels*)** no 2º turno das Eleições Presidenciais Brasileiras de 2026.

**Autor Principal / Pesquisador Responsável:**  
Prof. Dr. **André Luiz Satoshi Kawamoto**  
*Departamento Acadêmico de Computação (DACOM)*  
*Universidade Tecnológica Federal do Paraná (UTFPR) — Campus Campo Mourão*  
Contato: `kawamoto@utfpr.edu.br`

---

## 📚 Publicações Vinculadas

1. **Artigo 1 (BraSNAM / SBC 2026):**  
   *“Ative o Sininho para Receber as Missões”: Topologia Bipartida, Reconstrução Forense de Audiência e Efeito Spillover em Canais de Mobilização no WhatsApp nas Eleições de 2026.*  
   *Veículo:* Anais do XIV Brazilian Workshop on Social Network Analysis and Mining (BraSNAM / CSBC).
   *Pacote Overleaf:* [`papers/overleaf_brasnam_sbc.zip`](papers/overleaf_brasnam_sbc.zip)

2. **Artigo 2 (Elsevier OSNEM - Q1):**  
   *Weaponizing Broadcast Channels: Command-and-Control Mobilization, Search Engine Manipulation, and Judicial AI Regulation in Brazil's 2026 Presidential Runoff.*  
   *Veículo:* Online Social Networks and Media (OSNEM), Elsevier.
   *Pacote Overleaf:* [`papers/overleaf_elsevier_osnem.zip`](papers/overleaf_elsevier_osnem.zip)

---

## 🗂️ Estrutura do Repositório

```text
├── data/                                 # Datasets limpos e séries temporais consolidadas
│   ├── master_all_messages.csv           # Todas as 1.293+ mensagens unificadas (Lula + Flávio)
│   ├── master_exercito_do_lula.csv       # Corpus completo do Exército do Lula (1.144 msgs)
│   ├── master_tropa_do_flavio.csv        # Corpus completo da Tropa do Flávio (149 msgs)
│   ├── followers_live_timeseries.csv     # Telemetria horária de seguidores (10M vs. 1,9M churn)
│   └── x_twitter_brazil_trending_timeseries.csv # Séries temporais dos Trending Topics do X Brasil
├── pipeline/                             # Scripts de processamento, análise e visualização
│   ├── analyze_channels.py               # Ingestão, deduplicação e exportação de grafos bipartidos
│   ├── analyze_discourse.py              # Análise computacional de discurso (CADS / Framing)
│   ├── monitor_followers.py              # Sonda HTTP horária de seguidores em canais públicos
│   ├── fetch_x_trends_std.py             # Coletor de tendências horárias do X/Twitter
│   └── generate_streamgraph.py           # Motor temporal do Streamgraph (ThemeRiver)
├── scraper/                              # Extratores de DOM do WhatsApp Web
│   └── whatsapp_channel_extractor.js     # Script de injeção no DOM para captura retroativa
├── papers/                               # Manuscritos científicos e pacotes Overleaf
│   ├── paper1_brasnam_sbc/               # Artigo BraSNAM (LaTeX, .bib, template SBC e PDF)
│   ├── paper2_elsevier_osnem/            # Artigo Elsevier OSNEM (LaTeX, .bib e PDF)
│   ├── overleaf_brasnam_sbc.zip          # Arquivo ZIP pronto para 1-clique no Overleaf
│   └── overleaf_elsevier_osnem.zip       # Arquivo ZIP pronto para 1-clique no Overleaf
└── output/                               # Resultados estruturados (JSON, CSVs de grafo e relatórios)
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
| `mission_type` | String | Classificação na taxonomia tática de 8 dimensões de comando |
| `text` | String | Texto integral da mensagem |
| `links` | String | Lista delimitada por pipe (`\|`) de hiperlinks externos |
| `hashtags` | String | Lista delimitada por pipe de hashtags identificadas |
| `has_media` | Boolean | Indicador de presença de anexos multimídia |
| `has_video` | Boolean | Presença de mídia em formato de vídeo |
| `reactions_json` | JSON | Vetor estruturado dos emojis de reação e suas respectivas contagens |

---

## ⚖️ Conformidade Ética e Proteção de Dados (LGPD e TSE)

* **Lei Geral de Proteção de Dados (Lei nº 13.709/2018):** Os dados coletados originam-se exclusivamente de **Canais de Transmissão Oficiais Públicos**, unidirecionais e devidamente cadastrados perante a Justiça Eleitoral (Resolução TSE nº 23.610). 
* **Privacidade dos Usuários:** A arquitetura dos Canais do WhatsApp não disponibiliza lista pública de membros, números de telefone, fotos de perfil ou mensagens de cidadãos comuns. Portanto, **nenhum dado pessoal sensível (PII) é capturado, armazenado ou distribuído**.

---

## 🚀 Como Reproduzir

### 1. Clonar o repositório e instalar dependências
```bash
git clone https://github.com/kawamoto-utfpr/brasnam-eleicoes-2026.git
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

---

## 📝 Como Citar

```bibtex
@inproceedings{kawamoto2026brasnam,
  author    = {Andr{'e} Luiz Satoshi Kawamoto},
  title     = {``Ative o Sininho para Receber as Miss{\~o}es'': Topologia Bipartida, Reconstru{\c{c}}{\~a}o Forense de Audi{\^e}ncia e Efeito Spillover em Canais de Mobiliza{\c{c}}{\~a}o no {WhatsApp} nas Elei{\c{c}}{\~o}es de 2026},
  booktitle = {Anais do XIV Brazilian Workshop on Social Network Analysis and Mining (BraSNAM / CSBC)},
  year      = {2026},
  publisher = {SBC}
}

@article{kawamoto2026osnem,
  author    = {Andr{'e} Luiz Satoshi Kawamoto},
  title     = {Weaponizing Broadcast Channels: Command-and-Control Mobilization, Search Engine Manipulation, and Judicial AI Regulation in {Brazil}'s 2026 Presidential Runoff},
  journal   = {Online Social Networks and Media},
  year      = {2026},
  publisher = {Elsevier}
}
```
