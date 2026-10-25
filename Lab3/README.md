# Laboratorio 3: Gramáticas Libres de Contexto

**Integrantes:** Francisco Benavides · Marcelo Matamala  
**Asignatura:** Teoría de la Computación – INFO1148  
**Carrera:** Ingeniería Civil en Informática  
**Docente:** Marcos Lévano

## Objetivo

Diseñar, analizar y validar una Gramática Libre de Contexto (GLC) que represente la estructura sintáctica de un lenguaje de programación simplificado. El trabajo consiste en identificar sus componentes formales, construir las producciones, realizar derivaciones por la izquierda, generar el árbol sintáctico y comprobar la pertenencia de cadenas válidas e inválidas.

## ¿Qué se trabajó?

Este laboratorio aborda los siguientes aspectos:

- **Componentes formales**: Se definieron los símbolos terminales (incluyendo clases de token como ID, NUM y COMENT), los símbolos no terminales, el símbolo inicial y la gramática G = (V, Σ, P, S).
- **Construcción de la GLC**: Se plantearon las producciones necesarias para reconocer un bloque Begin ... End, un identificador de programa, asignaciones simples y aritméticas, instrucciones de salida, comentarios y una o más instrucciones.
- **Jerarquía de expresiones**: Se estructuró la gramática con precedencia para los operadores aritméticos (+ - * / %), distinguiendo correctamente entre una asignación simple (x = 20 #) y una asignación con expresión aritmética (z = x + y #).
- **Derivaciones y árbol sintáctico**: Se realizaron derivaciones por la izquierda para cadenas solicitadas, se construyó el árbol de derivación correspondiente y se justificó la relación entre nodos, hojas, terminales y no terminales.
- **Validación sintáctica**: Se analizaron cadenas válidas e inválidas, identificando el primer error sintáctico con su token, línea, columna y el símbolo esperado.
- **Extensión creativa**: Se incorporó el condicional si ... entonces ... fin_si (Opción A), reutilizando la jerarquía de expresiones y la lista de instrucciones, sin agregar sino para mantener la gramática no ambigua.

## Estructura del repositorio

`	ext
Lab3/
├── README.md
└── gramatica/
    ├── Lab3_gramatica.bnf      # Gramática en BNF con 45 producciones numeradas P1–P45
    ├── gramatica.py            # Analizador léxico-sintáctico descendente recursivo
    └── salidas/
        ├── validacion.txt                # Evidencia de validación (programa de referencia, P4, extensión)
        ├── arbol_z_igual_x_mas_y.txt     # Árbol de derivación en formato texto
        ├── arbol_z_igual_x_mas_y.dot     # Árbol en formato Graphviz
        ├── arbol_z_igual_x_mas_y.mmd     # Árbol en formato Mermaid
        ├── arbol_z_igual_x_mas_y.png     # Captura del árbol de derivación
        └── arbol_programa_referencia.dot # Árbol del programa de referencia completo
`

## Funcionamiento

El archivo gramatica/gramatica.py implementa un **lexer y parser descendente recursivo** que sigue exactamente las producciones definidas en Lab3_gramatica.bnf. A partir de este analizador se generan las evidencias en la carpeta salidas/, entre ellas la validación del programa de referencia, la tabla de casos de prueba, los resultados de la extensión y el árbol de derivación.

Para reproducir la evidencia:

`ash
# Validación completa y generación de salidas
python Lab3/gramatica/gramatica.py

# Verificación rápida
python Lab3/gramatica/gramatica.py --check
`

El resultado esperado es Verificacion: OK con Fallos: 0.
