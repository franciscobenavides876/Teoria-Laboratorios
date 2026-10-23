#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera una version HTML imprimible del informe del Laboratorio 3.

Uso:
    python informe/build_html.py

Produce:
    informe/Laboratorio_3_Informe.html

Abrir ese archivo en un navegador y usar "Imprimir > Guardar como PDF" para
obtener el entregable en PDF (margenes A4 ya configurados).
Requiere: markdown-it-py  (pip install markdown-it-py)
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from markdown_it import MarkdownIt

BASE = Path(__file__).parent
FUENTE = BASE / "Laboratorio_3_Informe.md"
DESTINO = BASE / "Laboratorio_3_Informe.html"

CSS = """
@page { size: A4; margin: 18mm 15mm 16mm 15mm; }

:root { --azul: #1f4e79; --gris: #5a5a5a; --borde: #c9d4df; }

* { box-sizing: border-box; }

body {
  font-family: "Segoe UI", "Calibri", Arial, sans-serif;
  font-size: 10.8pt;
  line-height: 1.45;
  color: #1b1b1b;
  max-width: 980px;
  margin: 0 auto;
  padding: 28px 30px 60px;
  background: #fff;
}

h1 {
  font-size: 21pt;
  color: var(--azul);
  border-bottom: 3px solid var(--azul);
  padding-bottom: 8px;
  margin: 0 0 14px;
  line-height: 1.2;
}

h2 {
  font-size: 14.5pt;
  color: var(--azul);
  border-bottom: 1px solid var(--borde);
  padding-bottom: 4px;
  margin: 26px 0 10px;
  page-break-after: avoid;
}

h3 {
  font-size: 12pt;
  color: #24425c;
  margin: 18px 0 8px;
  page-break-after: avoid;
}

h4 { font-size: 11pt; margin: 14px 0 6px; }

p, li { orphans: 3; widows: 3; }

a { color: #17609b; text-decoration: none; }

strong { color: #14202b; }

hr {
  border: 0;
  border-top: 1px solid var(--borde);
  margin: 22px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0 16px;
  font-size: 8.9pt;
  page-break-inside: auto;
}

thead { display: table-header-group; }
tr { page-break-inside: avoid; }

th, td {
  border: 1px solid var(--borde);
  padding: 4px 6px;
  vertical-align: top;
  text-align: left;
}

th { background: #eaf1f8; font-weight: 600; }

tbody tr:nth-child(even) { background: #fafcfe; }

code {
  font-family: Consolas, "Cascadia Mono", monospace;
  font-size: 0.9em;
  background: #f2f5f8;
  border: 1px solid #e1e8ef;
  border-radius: 3px;
  padding: 0 3px;
}

pre {
  background: #f7f9fb;
  border: 1px solid var(--borde);
  border-left: 4px solid var(--azul);
  border-radius: 3px;
  padding: 9px 11px;
  overflow-x: auto;
  font-size: 8.6pt;
  line-height: 1.38;
  page-break-inside: avoid;
}

pre code {
  background: none;
  border: 0;
  padding: 0;
  font-size: inherit;
}

blockquote {
  margin: 12px 0;
  padding: 8px 14px;
  background: #f3f8fc;
  border-left: 4px solid #7aa8c8;
  color: #24323d;
}

blockquote p { margin: 4px 0; }

ul, ol { margin: 6px 0 10px; padding-left: 24px; }

li { margin: 3px 0; }

.mermaid {
  text-align: center;
  margin: 14px 0;
  page-break-inside: avoid;
}

.mermaid svg { max-width: 100%; height: auto; }

.tabla-scroll { overflow-x: auto; }

@media print {
  body { max-width: none; padding: 0; font-size: 10.4pt; }
  a { color: inherit; }
  .no-print { display: none !important; }
  h1 { font-size: 19pt; }
  h2 { font-size: 13.5pt; }
  table { font-size: 8.4pt; }
  pre { font-size: 8pt; }
}

@media screen {
  body { box-shadow: 0 0 12px rgba(0,0,0,.12); }
  .aviso {
    background: #fff8e1;
    border: 1px solid #f0d58c;
    padding: 8px 12px;
    font-size: 9.5pt;
    margin-bottom: 18px;
  }
}
"""


def main() -> None:
    texto = FUENTE.read_text(encoding="utf-8")

    # Los bloques ```mermaid se renderizan con mermaid.js, no como código.
    bloques: list[str] = []

    def guardar(m: re.Match[str]) -> str:
        bloques.append(m.group(1))
        return f"@@MERMAID{len(bloques) - 1}@@\n"

    texto = re.sub(r"```mermaid\n(.*?)```", guardar, texto, flags=re.S)

    md = MarkdownIt("gfm-like")
    md.options["linkify"] = False
    cuerpo = md.render(texto)

    for i, bloque in enumerate(bloques):
        reemplazo = f'<pre class="mermaid">{html.escape(bloque.strip())}</pre>'
        cuerpo = cuerpo.replace(f"<p>@@MERMAID{i}@@</p>", reemplazo)
        cuerpo = cuerpo.replace(f"@@MERMAID{i}@@", reemplazo)

    plantilla = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Laboratorio 3 - Diseno y Validacion de Gramaticas (INFO1148)</title>
<style>{CSS}</style>
</head>
<body>
<p class="aviso no-print">Para generar el PDF: <strong>Imprimir</strong> (Ctrl+P) &rarr;
<strong>Guardar como PDF</strong>, tamano A4, margenes predeterminados, activar
&ldquo;Graficos de fondo&rdquo;. Los diagramas Mermaid se dibujan al abrir el archivo
(requiere conexion a Internet; si no hay, el arbol tambien esta en texto).</p>
{cuerpo}
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({{ startOnLoad: true, theme: "neutral", flowchart: {{ htmlLabels: true }} }});
</script>
</body>
</html>
"""

    DESTINO.write_text(plantilla, encoding="utf-8")
    print(f"HTML generado: {DESTINO}")
    print(f"Tablas: {cuerpo.count('<table>')} | Diagramas Mermaid: {len(bloques)}")


if __name__ == "__main__":
    main()
