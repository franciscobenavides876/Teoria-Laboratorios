# Laboratorio 3 — Diseño y Validación de Gramáticas

**Asignatura:** Teoría de la Computación — INFO1148
**Tema:** Gramáticas Libres de Contexto (GLC)
**Modalidad:** Laboratorio práctico (parejas)
**Puntaje:** 100 puntos
**Entrega:** Informe + evidencias

Esta carpeta (`Lab3/`) contiene el desarrollo completo de la Pregunta 1 a la Pregunta 4, la
extensión creativa y las evidencias de ejecución del Laboratorio 3.

| Integrante | |
|---|---|
| Francisco Benavides | `franciscobenavides876` |
| _(integrante 2)_ | completar antes de entregar |

## Estructura

```
Lab3/
├── README.md                         ← este archivo (guía de la carpeta)
├── informe/
│   ├── Laboratorio_3_Informe.md      ← informe completo (fuente)
│   ├── Laboratorio_3_Informe.html    ← versión imprimible (Ctrl+P → PDF)
│   └── build_html.py                 ← regenera el HTML desde el Markdown
└── gramatica/
    ├── Lab3_gramatica.bnf            ← gramática G = (V, Σ, P, S) en BNF, 41 producciones
    ├── gramatica.py                  ← validador: léxico + sintáctico + árbol + pruebas
    └── salidas/                      ← evidencia generada por gramatica.py
        ├── validacion.txt                    (P2 y P4: resultados completos)
        ├── arbol_z_igual_x_mas_y.txt         (P3: árbol en texto)
        ├── arbol_z_igual_x_mas_y.dot         (P3: árbol en Graphviz)
        ├── arbol_z_igual_x_mas_y.mmd         (P3: árbol en Mermaid)
        └── arbol_programa_referencia.dot     (P2: árbol del programa completo)
```

## Qué se entrega en cada pregunta

| Pregunta | Puntos | Contenido | Dónde verlo |
|---|:---:|---|---|
| **P1.** Identificación formal | 20 | Terminales clasificados, no terminales, símbolo inicial, `G=(V,Σ,P,S)` y justificación de por qué no se enumeran identificadores/números. | Informe §3 |
| **P2.** Construcción de la GLC | 30 | 41 producciones numeradas, explicación de cada no terminal, distinción asignación simple / aritmética / salida y verificación del programa de referencia. | Informe §4 + `gramatica/Lab3_gramatica.bnf` |
| **P3.** Derivaciones y árbol | 25 | Dos derivaciones por la izquierda, árbol de `z = x + y #`, explicación raíz/nodos/hojas y pertenencia de tres cadenas. | Informe §5 + `gramatica/salidas/arbol_*` |
| **P4.** Validación y errores | 25 | Análisis de los 8 casos, con el elemento sintáctico faltante o mal ubicado en cada cadena inválida. | Informe §6 + `gramatica/salidas/validacion.txt` |
| **Extensión creativa** | (transversal) | Opción A: `si … entonces … fin_si`, con sintaxis, gramática modificada, cadenas válida/inválida y derivación. | Informe §7 |

## Cómo reproducir la evidencia

Requisitos: **Python 3.9+** (solo biblioteca estándar para el validador).

```bash
# Valida el programa de referencia, la tabla de la P4 y la extensión,
# y regenera la carpeta gramatica/salidas/
python Lab3/gramatica/gramatica.py

# Comprobación rápida (código de salida 0 = todos los casos coinciden)
python Lab3/gramatica/gramatica.py --check
```

Resultado esperado: `Fallos: 0` y `Verificacion: OK`. La salida completa queda en
`gramatica/salidas/validacion.txt`.

## Cómo generar el PDF del informe

Opción A (recomendada, sin instalar nada más):

```bash
python Lab3/informe/build_html.py      # requiere: pip install markdown-it-py
```

Luego abrir `Lab3/informe/Laboratorio_3_Informe.html` en un navegador y usar
**Imprimir → Guardar como PDF** (A4, márgenes predeterminados, activar «Gráficos de fondo»).
Los diagramas Mermaid se dibujan al abrir el archivo (necesita Internet); el árbol también está
en texto por si no hay conexión.

Opción B: extensión *Markdown PDF* de VS Code sobre `Laboratorio_3_Informe.md`.

> El PDF final se entrega por la vía indicada por el profesor, con la nomenclatura que él
> solicite; esta carpeta guarda la fuente y la evidencia.

## Notas y decisiones de diseño

- **Terminales como clases de token.** `ID`, `NUM` y `COMENT` son terminales únicos; su forma se
  define con expresiones regulares (Anexo A del informe). Así Σ y `P` son finitos aunque el
  lenguaje tenga infinitos identificadores y números.
- **Asignación simple vs. aritmética.** Se separan en `P10` y `P11` para evitar ambigüedad: si
  ambas compartieran una sola producción con `<expresion>`, `x = 20 #` tendría dos árboles.
- **Precedencia.** `<expresion> → <termino> → <factor> → <operando>` hace que `* / %` liguen más
  fuerte que `+ -`, sin necesidad de paréntesis.
- **Comentarios.** `/* … */` se reconoce como un token (`COMENT`) y se admite entre instrucciones
  (`P4`); de otro modo no se podría derivar el programa de referencia completo.
- **Extensión.** Se eligió la Opción A (condicional) por ser la construcción de control más
  representativa; no se agregó `sino` para mantener la gramática no ambigua.
- **Sin JFLAP.** El árbol se genera con el propio analizador y se exporta a `.dot`/`.mmd`, por lo
  que no hace falta adjuntar archivos `.jff` (el enunciado solo los exige «si se utiliza JFLAP»).

## Checklist antes de entregar

- [x] P1: terminales, no terminales, símbolo inicial y `G=(V,Σ,P,S)` definidos
- [x] P2: gramática completa (41 producciones) + verificación del programa de referencia
- [x] P3: derivaciones por la izquierda + árbol + explicación + pertenencia de cadenas
- [x] P4: tabla de los 8 casos + análisis de errores
- [x] Extensión creativa (Opción A) formalizada y validada
- [x] Evidencia ejecutable (`gramatica.py` → `Fallos: 0`)
- [ ] Completar el nombre del segundo integrante en el informe y en este README
- [ ] Exportar el informe a PDF y subirlo por la vía indicada por el profesor
- [ ] Confirmar con el profesor si desea el árbol en JFLAP además del `.dot`/`.mmd`
