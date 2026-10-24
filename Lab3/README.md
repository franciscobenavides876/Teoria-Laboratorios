# Laboratorio 3 — Diseño y Validación de Gramáticas

**Asignatura:** Teoría de la Computación — INFO1148
**Tema:** Gramáticas Libres de Contexto (GLC)
**Modalidad:** Laboratorio práctico (parejas)
**Puntaje:** 100 puntos
**Entrega:** Evidencias (validador + gramática + salidas)

Esta carpeta (`Lab3/`) contiene el desarrollo completo de la Pregunta 1 a la Pregunta 4, la
extensión creativa y las evidencias de ejecución del Laboratorio 3.

| Integrante | |
|---|---|
| Francisco Benavides | `franciscobenavides876` |
| Marcelo Matamala | — |

## Estructura

```text
Lab3/
├── README.md
└── gramatica/
    ├── Lab3_gramatica.bnf            ← gramática G = (V, Σ, P, S) en BNF, 45 producciones
    ├── gramatica.py                  ← validador: léxico + sintáctico + árbol + pruebas
    └── salidas/                      ← evidencia generada por gramatica.py
        ├── validacion.txt
        ├── arbol_z_igual_x_mas_y.txt
        ├── arbol_z_igual_x_mas_y.dot
        ├── arbol_z_igual_x_mas_y.mmd
        ├── arbol_z_igual_x_mas_y.png
        └── arbol_programa_referencia.dot
```

## Qué se entrega en cada pregunta

| Pregunta | Puntos | Contenido | Dónde verlo |
|---|:---:|---|---|
| **P1.** Identificación formal | 20 | Terminales clasificados, no terminales, símbolo inicial, `G=(V,Σ,P,S)` y justificación de por qué no se enumeran identificadores/números. | `gramatica/Lab3_gramatica.bnf` + `gramatica/gramatica.py` |
| **P2.** Construcción de la GLC | 30 | 45 producciones numeradas, explicación, distinción asignación simple / aritmética / salida y verificación del programa de referencia. | `gramatica/Lab3_gramatica.bnf` + `gramatica/salidas/validacion.txt` |
| **P3.** Derivaciones y árbol | 25 | Dos derivaciones por la izquierda, árbol de `z = x + y #`, explicación raíz/nodos/hojas y pertenencia de tres cadenas. | `gramatica/salidas/arbol_*` |
| **P4.** Validación y errores | 25 | Análisis de los 8 casos, con el elemento sintáctico faltante o mal ubicado en cada cadena inválida. | `gramatica/salidas/validacion.txt` |
| **Extensión creativa** | (transversal) | Opción A: `si … entonces … fin_si`, formalizada y validated. | `gramatica/gramatica.py` + `gramatica/salidas/validacion.txt` |

## Cómo reproducir la evidencia

Requisitos: **Python 3.9+** (solo biblioteca estándar).

```bash
# Valida el programa de referencia, la tabla de P4 y la extensión
python Lab3/gramatica/gramatica.py

# Comprobación rápida (código de salida 0 = todos los casos coinciden)
python Lab3/gramatica/gramatica.py --check
```

Resultado esperado: `python …` imprime `Fallos: 0`; `python … --check` imprime `Verificacion: OK`. La salida completa queda en `gramatica/salidas/validacion.txt`.

## Notas y decisiones de diseño

- **Terminales como clases de token.** `ID`, `NUM` y `COMENT` are terminales únicos; su forma se define con expresiones regulares. Así Σ y `P` son finitos aunque el lenguaje tenga infinitos identificadores y números.
- **Asignación simple vs. aritmética.** Se separan en `P12` y `P13` para evitar ambigüedad.
- **Precedencia.** `<expresion> → <termino> → <factor> → <operando>` hace que `* / %` liguen más fuerte que `+ -`.
- **Comentarios.** `/* … */` se reconoce como `COMENT` y se admite antes, entre y después de las instrucciones.
- **Extensión.** Se eligió la Opción A (`si … entonces … fin_si`) sin `sino` para mantener la gramática no ambigua.
- **Sin JFLAP.** El árbol se genera con el propio analizador y se exporta a `.dot`/`.mmd`.

## Checklist antes de entregar

- [x] P1: terminales, no terminales, símbolo inicial and `G=(V,Σ,P,S)` definidos
- [x] P2: gramática completa (45 producciones) + verificación del programa de referencia
- [x] P3: derivaciones por la izquierda + árbol + explicación + pertenencia de cadenas
- [x] P4: tabla de los 8 casos + análisis de errores
- [x] Extensión creativa (Opción A) formalizada and validated
- [x] Evidencia ejecutable (`gramatica.py` → `Fallos: 0`)
- [x] Archivos `.dot`/.mmd`/`.txt`/`.png` del árbol de derivación
- [x] Informe entregado desde Overleaf (PDF)
- [x] Integrantes completos: Francisco Benavides y Marcelo Matamala
