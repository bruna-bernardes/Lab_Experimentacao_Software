"""Gera relatorio/relatorio.pdf a partir de relatorio.md.

Uso, a partir de Laboratorio_03/relatorio:

    python gerar_pdf.py
"""
from pathlib import Path

import markdown
from weasyprint import HTML


PASTA = Path(__file__).parent
ORIGEM = PASTA / "relatorio.md"
DESTINO = PASTA / "relatorio.pdf"

ESTILO = """
@page {
  size: A4;
  margin: 1.7cm 1.5cm 1.9cm 1.5cm;
  @bottom-center {
    content: counter(page);
    font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
    font-size: 9pt;
    color: #555;
  }
}
html { font-size: 11pt; }
body {
  font-family: "Liberation Serif", "DejaVu Serif", serif;
  line-height: 1.35;
  color: #1a1a1a;
}
h1 { font-size: 18pt; line-height: 1.2; margin: 0 0 0.6em; }
h2 { font-size: 14pt; margin: 1.2em 0 0.4em; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 1em 0 0.3em; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
a { color: #1f4e79; text-decoration: none; }
code {
  font-family: "Liberation Mono", "DejaVu Sans Mono", monospace;
  font-size: 0.9em;
}
pre {
  background: #f4f6f8;
  border: 1px solid #e1e4e8;
  padding: 0.6em 0.8em;
  white-space: pre-wrap;
  font-size: 9.5pt;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.6em 0 1em;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #c8ced6;
  padding: 0.28em 0.45em;
  vertical-align: top;
}
th { background: #eef3f8; text-align: left; }
figure {
  margin: 0.8em 0 1.1em;
  page-break-inside: avoid;
}
img { width: 100%; height: auto; }
figcaption {
  font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
  font-size: 9pt;
  color: #444;
  margin-top: 0.25em;
}
"""


def html_do_markdown(texto):
    corpo = markdown.markdown(
        texto,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Mineração de métricas DORA</title>
  <style>{ESTILO}</style>
</head>
<body>
{corpo}
</body>
</html>
"""


def legendar_figuras(html):
    """Transforma imagens com texto alternativo em figura com legenda."""
    inicio = 0
    partes = []
    marcador = "<img "
    while True:
        pos = html.find(marcador, inicio)
        if pos == -1:
            partes.append(html[inicio:])
            break
        partes.append(html[inicio:pos])
        fim = html.find(">", pos)
        tag = html[pos:fim + 1]
        alt = ""
        chave = 'alt="'
        i = tag.find(chave)
        if i != -1:
            j = tag.find('"', i + len(chave))
            alt = tag[i + len(chave):j]
        if alt:
            partes.append(f"<figure>{tag}<figcaption>{alt}</figcaption></figure>")
        else:
            partes.append(tag)
        inicio = fim + 1
    return "".join(partes)


def main():
    texto = ORIGEM.read_text(encoding="utf-8")
    html = legendar_figuras(html_do_markdown(texto))
    HTML(string=html, base_url=PASTA).write_pdf(DESTINO)
    print(f"PDF gerado em {DESTINO}")


if __name__ == "__main__":
    main()
