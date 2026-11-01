import subprocess
import os
import re

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PANDOC_PATH = r"C:\Program Files\Pandoc\pandoc.exe"

ACADEMIC_CSS = """
@page {
    size: A4;
    margin: 20mm 20mm 20mm 20mm;
}
body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 11pt;
    line-height: 1.45;
    color: #111;
    margin: 0 auto;
    padding: 0;
    max-width: 100%;
}
h1.title {
    font-size: 17pt;
    text-align: center;
    font-weight: bold;
    margin-bottom: 12pt;
    line-height: 1.25;
}
.author, .institution {
    text-align: center;
    font-size: 10.5pt;
    margin-bottom: 4pt;
}
.abstract-box {
    margin: 16pt 15pt;
    padding: 8pt 12pt;
    background: #fdfdfd;
    border-top: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
    font-size: 9.5pt;
    text-align: justify;
}
.abstract-box h2 {
    font-size: 10pt;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2pt;
    margin-bottom: 4pt;
}
h1, h2, h3, h4 {
    color: #000;
    font-family: 'Times New Roman', Times, serif;
}
h1 {
    font-size: 13pt;
    border-bottom: 1px solid #222;
    padding-bottom: 2pt;
    margin-top: 16pt;
    margin-bottom: 6pt;
}
h2 {
    font-size: 11.5pt;
    margin-top: 12pt;
    margin-bottom: 4pt;
}
h3 {
    font-size: 11pt;
    font-style: italic;
    margin-top: 10pt;
    margin-bottom: 3pt;
}
p {
    text-align: justify;
    text-indent: 1.25em;
    margin: 4pt 0;
}
.placeholder-box {
    border: 2px dashed #004085;
    background: #e9f2fb;
    padding: 16pt;
    margin: 14pt 0;
    text-align: center;
    border-radius: 4px;
}
.placeholder-box h4 {
    margin: 0 0 6pt 0;
    color: #004085;
    font-size: 11pt;
}
.placeholder-box p {
    text-align: center;
    text-indent: 0;
    font-size: 9.5pt;
    color: #222;
    margin: 2pt 0;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 12pt 0;
    font-size: 9.5pt;
}
th, td {
    border-top: 1px solid #bbb;
    border-bottom: 1px solid #bbb;
    padding: 5pt 6pt;
    text-align: left;
}
th {
    border-top: 2px solid #222;
    border-bottom: 1.5px solid #222;
    font-weight: bold;
}
tr:last-child td {
    border-bottom: 2px solid #222;
}
blockquote {
    border-left: 3px solid #666;
    margin: 8pt 16pt;
    padding-left: 10pt;
    font-style: italic;
    color: #333;
}
code {
    font-family: 'Courier New', Courier, monospace;
    background: #f4f4f4;
    padding: 1px 4px;
    font-size: 9pt;
    border-radius: 2px;
}
pre {
    background: #f4f4f4;
    padding: 8pt;
    border-radius: 4px;
    font-size: 8.5pt;
    overflow-x: auto;
}
ul, ol {
    margin: 4pt 0;
    padding-left: 20pt;
}
li {
    margin-bottom: 3pt;
    text-align: justify;
}
"""

def compile_latex_to_pdf(tex_path, output_pdf_path, title_override=None):
    tex_dir = os.path.dirname(os.path.abspath(tex_path))
    base_name = os.path.splitext(os.path.basename(tex_path))[0]
    html_path = os.path.join(tex_dir, f"{base_name}_styled.html")
    
    print(f"[1/3] Converting {tex_path} to HTML via Pandoc...")
    # Run pandoc
    cmd = [
        PANDOC_PATH,
        tex_path,
        "-s",
        "--mathjax",
        "-o", html_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=tex_dir)
    if res.returncode != 0:
        print(f"Pandoc error: {res.stderr}")
        return False
        
    print(f"[2/3] Post-processing HTML with Academic CSS...")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # Inject academic CSS
    css_injection = f"<style>{ACADEMIC_CSS}</style>"
    html = html.replace("</head>", f"{css_injection}\n</head>")
    
    # Improve placeholder styling
    html = re.sub(
        r'<div class="center">\s*<div class="parbox">([\s\S]*?)</div>\s*</div>',
        r'<div class="placeholder-box">\1</div>',
        html
    )
    # Wrap abstract if present
    html = re.sub(
        r'<div class="abstract">([\s\S]*?)</div>',
        r'<div class="abstract-box">\1</div>',
        html
    )
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"[3/3] Printing HTML to PDF via Headless Chrome/Edge...")
    profile_dir = os.path.join(os.path.dirname(output_pdf_path), "browser_profile")
    os.makedirs(profile_dir, exist_ok=True)
    
    browser_bin = CHROME_PATH if os.path.exists(CHROME_PATH) else EDGE_PATH
    browser_cmd = [
        browser_bin,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        f"--user-data-dir={profile_dir}",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_pdf_path}",
        html_path
    ]
    browser_res = subprocess.run(browser_cmd, capture_output=True, text=True)
    if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
        print(f"[SUCCESS] Generated: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")
        return True
    else:
        # Fallback to Edge with --headless
        print(f"Retrying with alternative flags...")
        fallback_cmd = [
            EDGE_PATH,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={profile_dir}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={output_pdf_path}",
            html_path
        ]
        fb_res = subprocess.run(fallback_cmd, capture_output=True, text=True)
        if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
            print(f"[SUCCESS via Edge] Generated: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")
            return True
        print(f"[ERROR] Browser failed to generate PDF. Stderr: {browser_res.stderr}\nFallback: {fb_res.stderr}")
        return False

if __name__ == "__main__":
    paper1_tex = r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\papers\paper1_brasnam_sbc\main_brasnam.tex"
    paper1_pdf = r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\papers\paper1_brasnam_sbc\artigo_brasnam_previa.pdf"
    
    paper2_tex = r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\papers\paper2_elsevier_osnem\main_elsevier_osnem.tex"
    paper2_pdf = r"C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\papers\paper2_elsevier_osnem\artigo_elsevier_osnem_preview.pdf"
    
    print("=== Compilando Artigo 1 (BRASNAM / SBC) ===")
    compile_latex_to_pdf(paper1_tex, paper1_pdf)
    
    print("\n=== Compilando Artigo 2 (Elsevier OSNEM) ===")
    compile_latex_to_pdf(paper2_tex, paper2_pdf)
