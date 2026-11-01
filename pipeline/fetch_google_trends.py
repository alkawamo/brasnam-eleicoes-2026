"""
Coletor Automático do Google Trends (Web + YouTube) — BRASNAM & Elsevier OSNEM 2026
Salva localmente:
1. `data/google_trends_search_bombing.csv`: Série horária de Search Bombing na Web (gprop="")
2. `data/youtube_trends_debate_cortes.csv`: Série horária de busca por Cortes do Debate no YouTube (gprop="youtube")
"""

from pathlib import Path
import time


def fetch_trends():
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    web_csv = out_dir / "google_trends_search_bombing.csv"
    yt_csv = out_dir / "youtube_trends_debate_cortes.csv"

    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="pt-BR", tz=180)

        # 1. Google Web Search Bombing
        kw_web = ["Talvane Albuquerque", "Bolsonaro Talvane", "Punhal Verde e Amarelo"]
        pytrends.build_payload(kw_web, cat=0, timeframe="now 7-d", geo="BR", gprop="")
        df_web = pytrends.interest_over_time()
        if not df_web.empty:
            df_web.to_csv(web_csv, encoding="utf-8")
            print(f"✅ Google Web Trends salvo em: {web_csv} ({len(df_web)} pontos horários)")

        time.sleep(2)

        # 2. YouTube Search (Cortes do Debate e termos de campanha)
        kw_yt = ["Debate Globo", "Lula debate", "Flavio Bolsonaro debate", "cortes debate"]
        pytrends.build_payload(kw_yt, cat=0, timeframe="now 7-d", geo="BR", gprop="youtube")
        df_yt = pytrends.interest_over_time()
        if not df_yt.empty:
            df_yt.to_csv(yt_csv, encoding="utf-8")
            print(f"✅ YouTube Search Trends salvo em: {yt_csv} ({len(df_yt)} pontos horários)")
            print(df_yt.tail(15))

    except Exception as e:
        print(f"⚠️ Aviso pytrends: {e}")


if __name__ == "__main__":
    fetch_trends()
