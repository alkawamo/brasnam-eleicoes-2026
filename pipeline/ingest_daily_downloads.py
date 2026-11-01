"""
Script Utilitário de Ingestão Diária
Executa a cópia de novos arquivos baixados em Downloads, desduplica e consolida os dados mestres
SEM precisar regenerar o Streamgraph interativo em cada passo (deixando a renderização para o final).
"""
import shutil
from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PIPELINE_DIR = BASE_DIR / "pipeline"
DOWNLOADS_DIR = Path(r"C:\Users\alkaw\Downloads")

def ingest():
    print("=== INGESTÃO DIÁRIA DE DADOS ===")
    copied = 0
    if DOWNLOADS_DIR.exists():
        for f in DOWNLOADS_DIR.glob("whatsapp_channel_*.json"):
            dest = DATA_DIR / f.name
            # Copia apenas se não existir ou se tiver tamanho diferente
            if not dest.exists() or dest.stat().st_size != f.stat().st_size:
                shutil.copy2(f, dest)
                copied += 1
                print(f"  [+] Copiado: {f.name} ({f.stat().st_size:,} bytes)")
    print(f"Total de arquivos novos/atualizados copiados: {copied}")

    print("\nExecutando desduplicação e agregação (analyze_channels.py)...")
    cmd = [sys.executable, str(PIPELINE_DIR / "analyze_channels.py")]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode == 0:
        print(res.stdout)
        print("[OK] Dados mestres atualizados com sucesso!")
    else:
        print("[ERRO] Falha ao executar analyze_channels.py:")
        print(res.stderr)

if __name__ == "__main__":
    ingest()
