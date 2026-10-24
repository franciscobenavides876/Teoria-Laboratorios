#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratorio 3 - Diseno y Validacion de Gramaticas (INFO1148)

Implementacion de referencia de la gramatica libre de contexto propuesta en el
informe, junto con:
  * un analizador lexico (tokenizador) del lenguaje,
  * un analizador sintactico descendente recursivo (parser),
  * la validacion de las cadenas de la tabla de la Pregunta 4,
  * la generacion del arbol de derivacion de "z = x + y #".

Uso:
    python gramatica.py            # ejecuta todo y escribe la carpeta salidas/
    python gramatica.py --check    # solo valida (codigo de salida 0 = todo OK)

No requiere dependencias externas.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Terminales del lenguaje
# ---------------------------------------------------------------------------

PALABRAS_RESERVADAS = {"Begin", "End", "Programa", "salida", "si", "entonces", "fin_si"}

# Se ordenan de mas largo a mas corto para aplicar la regla de "maximo munch".
OPERADORES = ["<=", ">=", "==", "!=", "*", "/", "%", "+", "-", "<", ">"]

SIMBOLOS = {"=": "ASIG", "#": "HASH"}

# ---------------------------------------------------------------------------
# 2. Analizador lexico
# ---------------------------------------------------------------------------


@dataclass
class Token:
    tipo: str          # ID, NUM, BEGIN, END, PROGRAMA, SALIDA, SI, ENTONCES, FIN_SI,
                       # OP_ARIT, OP_REL, ASIG, HASH, COMENT
    lexema: str
    linea: int
    columna: int

    def __str__(self) -> str:
        return f"{self.tipo}({self.lexema!r})"


class ErrorLexico(Exception):
    def __init__(self, mensaje: str, linea: int, columna: int):
        super().__init__(f"Error lexico en linea {linea}, columna {columna}: {mensaje}")
        self.linea = linea
        self.columna = columna


def es_letra(c: str) -> bool:
    return c.isalpha() and c.isascii()


def es_digito(c: str) -> bool:
    return c.isdigit() and c.isascii()


def tokenizar(texto: str) -> list[Token]:
    tokens: list[Token] = []
    i, linea, col = 0, 1, 1
    n = len(texto)

    def avanzar(k: int = 1) -> None:
        nonlocal i, linea, col
        for _ in range(k):
            if i < n and texto[i] == "\n":
                linea += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < n:
        c = texto[i]

        # espacios y saltos de linea: se descartan
        if c in " \t\r\n":
            avanzar()
            continue

        # comentario /* ... */
        if texto.startswith("/*", i):
            li, co = linea, col
            fin = texto.find("*/", i + 2)
            if fin == -1:
                raise ErrorLexico("comentario sin cerrar ('*/' faltante)", li, co)
            lexema = texto[i:fin + 2]
            avanzar(len(lexema))
            tokens.append(Token("COMENT", lexema, li, co))
            continue

        # identificadores y palabras reservadas: letra (letra | digito | _)*
        if es_letra(c):
            li, co, inicio = linea, col, i
            while i < n and (es_letra(texto[i]) or es_digito(texto[i]) or texto[i] == "_"):
                avanzar()
            lexema = texto[inicio:i]
            if lexema in PALABRAS_RESERVADAS:
                tokens.append(Token(lexema.upper(), lexema, li, co))
            else:
                tokens.append(Token("ID", lexema, li, co))
            continue

        # numeros: enteros o reales positivos (digitos ['.' digitos])
        if es_digito(c):
            li, co, inicio = linea, col, i
            while i < n and es_digito(texto[i]):
                avanzar()
            if i < n and texto[i] == "." and i + 1 < n and es_digito(texto[i + 1]):
                avanzar()  # el punto
                while i < n and es_digito(texto[i]):
                    avanzar()
            elif i < n and texto[i] == ".":
                raise ErrorLexico("la parte decimal debe tener al menos un digito", linea, col)
            tokens.append(Token("NUM", texto[inicio:i], li, co))
            continue

        # operadores (maximo munch). Se comprueban antes que los simbolos
        # de un caracter para que '==' sea OP_REL y no dos ASIG.
        for op in OPERADORES:
            if texto.startswith(op, i):
                tipo = "OP_REL" if op in {"<", ">", "<=", ">=", "==", "!="} else "OP_ARIT"
                tokens.append(Token(tipo, op, linea, col))
                avanzar(len(op))
                break
        else:
            # simbolos de un caracter
            if c in SIMBOLOS:
                tokens.append(Token(SIMBOLOS[c], c, linea, col))
                avanzar()
                continue
            raise ErrorLexico(f"caracter no permitido {c!r}", linea, col)

    tokens.append(Token("EOF", "<fin de entrada>", linea, col))
    return tokens


# ---------------------------------------------------------------------------
# 3. Arbol sintactico
# ---------------------------------------------------------------------------


@dataclass
class Nodo:
    simbolo: str
    hijos: list["Nodo"] = field(default_factory=list)
    terminal: bool = False

    def agregar(self, hijo: "Nodo") -> "Nodo":
        self.hijos.append(hijo)
        return hijo


class ErrorSintactico(Exception):
    def __init__(self, mensaje: str, token: Token, esperado: list[str] | None = None):
        self.mensaje = mensaje
        self.token = token
        self.esperado = esperado or []
        detalle = f"{mensaje} (token {token.tipo} {token.lexema!r}, linea {token.linea}, columna {token.columna})"
        if self.esperado:
            detalle += f"; se esperaba: {', '.join(self.esperado)}"
        super().__init__(detalle)


# ---------------------------------------------------------------------------
# 4. Analizador sintactico descendente recursivo
#    Refleja exactamente las producciones del informe.
# ---------------------------------------------------------------------------


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # -- utilidades ---------------------------------------------------------
    @property
    def actual(self) -> Token:
        return self.tokens[self.pos]

    def mirar(self, k: int = 0) -> Token:
        return self.tokens[min(self.pos + k, len(self.tokens) - 1)]

    def consumir(self, tipo: str, esperado: list[str] | None = None) -> Token:
        tok = self.actual
        if tok.tipo != tipo:
            raise ErrorSintactico(f"se encontro {tok.tipo} {tok.lexema!r}", tok, esperado or [tipo])
        self.pos += 1
        return tok

    def consumir_operador(self, permitidos: set[str]) -> Token:
        """Consume un OP_ARIT cuyo lexema este en `permitidos`."""
        tok = self.actual
        if tok.tipo != "OP_ARIT" or tok.lexema not in permitidos:
            raise ErrorSintactico(
                f"se encontro {tok.tipo} {tok.lexema!r}", tok, sorted(permitidos)
            )
        self.pos += 1
        return tok

    def terminal(self, tipo: str, esperado: list[str] | None = None) -> Nodo:
        tok = self.consumir(tipo, esperado)
        return Nodo(tok.lexema, terminal=True)

    # -- <programa> -> Begin Programa <identificador> <lista_instrucciones> End
    def programa(self) -> Nodo:
        nodo = Nodo("<programa>")
        nodo.agregar(self.terminal("BEGIN"))
        nodo.agregar(self.terminal("PROGRAMA"))
        nodo.agregar(self.identificador())
        nodo.agregar(self.lista_instrucciones())
        nodo.agregar(self.terminal("END"))
        return nodo

    # <lista_instrucciones> -> <instruccion> <lista_instrucciones>
    #                       | <instruccion>
    #                       | <comentario> <lista_instrucciones>
    def lista_instrucciones(self) -> Nodo:
        nodo = Nodo("<lista_instrucciones>")
        # <comentario> <lista_instrucciones>
        if self.actual.tipo == "COMENT":
            nodo.agregar(self.comentario())
            nodo.agregar(self.lista_instrucciones())
            return nodo
        # <instruccion> <lista_instrucciones> | <instruccion>
        nodo.agregar(self.instruccion())
        if self.inicia_instruccion() or self.actual.tipo == "COMENT":
            nodo.agregar(self.lista_instrucciones())
        return nodo

    def inicia_instruccion(self) -> bool:
        return self.actual.tipo in {"ID", "SALIDA", "SI"}

    # <instruccion> -> <asignacion> | <salida> | <condicional>
    def instruccion(self) -> Nodo:
        nodo = Nodo("<instruccion>")
        if self.actual.tipo == "ID":
            nodo.agregar(self.asignacion())
        elif self.actual.tipo == "SALIDA":
            nodo.agregar(self.salida())
        elif self.actual.tipo == "SI":
            nodo.agregar(self.condicional())
        else:
            raise ErrorSintactico(
                f"se encontro {self.actual.tipo} {self.actual.lexema!r}",
                self.actual,
                ["ID", "salida", "si"],
            )
        return nodo

    # <asignacion> -> <asignacion_simple> | <asignacion_aritmetica>         (P8, P9)
    def asignacion(self) -> Nodo:
        nodo = Nodo("<asignacion>")
        # La decision se toma mirando si el lado derecho tiene operadores.
        if not self.es_asignacion_aritmetica():
            nodo.agregar(self.asignacion_simple())
        else:
            nodo.agregar(self.asignacion_aritmetica())
        return nodo

    def es_asignacion_aritmetica(self) -> bool:
        """True si entre '=' y '#' aparece al menos un operador aritmetico.

        Es la condicion que separa P10 (asignacion simple) de P11
        (asignacion con expresion): si el lado derecho es un unico
        operando se usa la via simple; si contiene cualquier operador
        (+ - * / %) se usa la via aritmetica.
        """
        if self.mirar(1).tipo != "ASIG":
            return False
        k = 2
        while True:
            tok = self.mirar(k)
            if tok.tipo in {"HASH", "EOF", "OP_REL"}:
                return False
            if tok.tipo == "OP_ARIT":
                return True
            k += 1

    # <asignacion_simple> -> <identificador> = <operando> #
    def asignacion_simple(self) -> Nodo:
        nodo = Nodo("<asignacion_simple>")
        nodo.agregar(self.identificador())
        nodo.agregar(self.terminal("ASIG", ["="]))
        nodo.agregar(self.operando())
        nodo.agregar(self.terminal("HASH", ["#"]))
        return nodo

    # <asignacion_aritmetica> -> <identificador> = <expresion_aritmetica> #
    def asignacion_aritmetica(self) -> Nodo:
        nodo = Nodo("<asignacion_aritmetica>")
        nodo.agregar(self.identificador())
        nodo.agregar(self.terminal("ASIG", ["="]))
        nodo.agregar(self.expresion_aritmetica())
        nodo.agregar(self.terminal("HASH", ["#"]))
        return nodo

    # <expresion_aritmetica> -> <termino> <resto_expresion_aritmetica>      (P12)
    #                        | <termino_aritmetico>                         (P13)
    #
    # Ambas alternativas obligan a que la expresion contenga al menos un
    # operador (para no solaparse con <asignacion_simple>), pero respetan
    # la precedencia: si hay '+' o '-' de nivel superior se usa la primera;
    # si solo hay '*' '/' '%' se usa <termino_aritmetico>.
    def expresion_aritmetica(self) -> Nodo:
        nodo = Nodo("<expresion_aritmetica>")
        if self.hay_suma_en_expresion():
            nodo.agregar(self.termino())
            nodo.agregar(self.resto_expresion_aritmetica())
        else:
            nodo.agregar(self.termino_aritmetico())
        return nodo

    def hay_suma_en_expresion(self) -> bool:
        """True si el nivel superior de la expresion contiene '+' o '-'.

        Como el lenguaje no tiene parentesis, cualquier '+'/'-' antes del
        terminador pertenece al nivel superior. El escaneo se detiene en
        '#', en EOF o en un operador relacional (fin de la expresion en
        una condicion).
        """
        k = 0
        while True:
            tok = self.mirar(k)
            if tok.tipo in {"HASH", "EOF", "OP_REL"}:
                return False
            if tok.tipo == "OP_ARIT" and tok.lexema in {"+", "-"}:
                return True
            k += 1

    # <resto_expresion_aritmetica> -> + <termino> <resto_expresion>         (P14)
    #                               | - <termino> <resto_expresion>         (P15)
    def resto_expresion_aritmetica(self) -> Nodo:
        nodo = Nodo("<resto_expresion_aritmetica>")
        tok = self.consumir_operador({"+", "-"})
        nodo.agregar(Nodo(tok.lexema, terminal=True))
        nodo.agregar(self.termino())
        nodo.agregar(self.resto_expresion())
        return nodo

    # <termino_aritmetico> -> <factor> <resto_termino_aritmetico>           (P16)
    def termino_aritmetico(self) -> Nodo:
        nodo = Nodo("<termino_aritmetico>")
        nodo.agregar(self.factor())
        nodo.agregar(self.resto_termino_aritmetico())
        return nodo

    # <resto_termino_aritmetico> -> * <factor> <resto_termino>              (P17)
    #                             | / <factor> <resto_termino>              (P18)
    #                             | % <factor> <resto_termino>              (P19)
    def resto_termino_aritmetico(self) -> Nodo:
        nodo = Nodo("<resto_termino_aritmetico>")
        tok = self.consumir_operador({"*", "/", "%"})
        nodo.agregar(Nodo(tok.lexema, terminal=True))
        nodo.agregar(self.factor())
        nodo.agregar(self.resto_termino())
        return nodo

    # <expresion> -> <termino> <resto_expresion>                            (P20)
    def expresion(self) -> Nodo:
        nodo = Nodo("<expresion>")
        nodo.agregar(self.termino())
        nodo.agregar(self.resto_expresion())
        return nodo

    # <resto_expresion> -> + <termino> <resto_expresion>                    (P21)
    #                    | - <termino> <resto_expresion>                    (P22)
    #                    | epsilon                                         (P23)
    def resto_expresion(self) -> Nodo:
        nodo = Nodo("<resto_expresion>")
        if self.actual.tipo == "OP_ARIT" and self.actual.lexema in {"+", "-"}:
            nodo.agregar(Nodo(self.consumir("OP_ARIT").lexema, terminal=True))
            nodo.agregar(self.termino())
            nodo.agregar(self.resto_expresion())
        else:
            nodo.agregar(Nodo("ε", terminal=True))
        return nodo

    # <termino> -> <factor> <resto_termino>                                (P24)
    def termino(self) -> Nodo:
        nodo = Nodo("<termino>")
        nodo.agregar(self.factor())
        nodo.agregar(self.resto_termino())
        return nodo

    # <resto_termino> -> * <factor> <resto_termino>                        (P25)
    #                  | / <factor> <resto_termino>                        (P26)
    #                  | % <factor> <resto_termino>                        (P27)
    #                  | epsilon                                           (P28)
    def resto_termino(self) -> Nodo:
        nodo = Nodo("<resto_termino>")
        if self.actual.tipo == "OP_ARIT" and self.actual.lexema in {"*", "/", "%"}:
            nodo.agregar(Nodo(self.consumir("OP_ARIT").lexema, terminal=True))
            nodo.agregar(self.factor())
            nodo.agregar(self.resto_termino())
        else:
            nodo.agregar(Nodo("ε", terminal=True))
        return nodo

    # <factor> -> <operando>                                                (P29)
    def factor(self) -> Nodo:
        nodo = Nodo("<factor>")
        nodo.agregar(self.operando())
        return nodo

    # <operando> -> <identificador> | <numero>                              (P30, P31)
    def operando(self) -> Nodo:
        nodo = Nodo("<operando>")
        if self.actual.tipo == "ID":
            nodo.agregar(self.identificador())
        elif self.actual.tipo == "NUM":
            nodo.agregar(self.numero())
        else:
            raise ErrorSintactico(
                f"se encontro {self.actual.tipo} {self.actual.lexema!r}",
                self.actual,
                ["ID", "NUM"],
            )
        return nodo

    # <salida> -> salida <identificador> #                                   (P32)
    def salida(self) -> Nodo:
        nodo = Nodo("<salida>")
        nodo.agregar(self.terminal("SALIDA", ["salida"]))
        nodo.agregar(self.identificador())
        nodo.agregar(self.terminal("HASH", ["#"]))
        return nodo

    # <condicional> -> si <condicion> entonces <lista_instrucciones> fin_si  (P36)
    def condicional(self) -> Nodo:
        nodo = Nodo("<condicional>")
        nodo.agregar(self.terminal("SI", ["si"]))
        nodo.agregar(self.condicion())
        nodo.agregar(self.terminal("ENTONCES", ["entonces"]))
        nodo.agregar(self.lista_instrucciones())
        nodo.agregar(self.terminal("FIN_SI", ["fin_si"]))
        return nodo

    # <condicion> -> <expresion> <operador_relacional> <expresion>           (P37)
    def condicion(self) -> Nodo:
        nodo = Nodo("<condicion>")
        nodo.agregar(self.expresion())
        nodo.agregar(self.operador_relacional())
        nodo.agregar(self.expresion())
        return nodo

    # <operador_relacional> -> < | > | <= | >= | == | !=                  (P38-P43)
    def operador_relacional(self) -> Nodo:
        nodo = Nodo("<operador_relacional>")
        tok = self.consumir("OP_REL", ["<", ">", "<=", ">=", "==", "!="])
        nodo.agregar(Nodo(tok.lexema, terminal=True))
        return nodo

    # <identificador> -> ID                                                  (P33)
    def identificador(self) -> Nodo:
        nodo = Nodo("<identificador>")
        tok = self.consumir("ID", ["identificador"])
        nodo.agregar(Nodo(tok.lexema, terminal=True))
        return nodo

    # <numero> -> NUM                                                         (P34)
    def numero(self) -> Nodo:
        nodo = Nodo("<numero>")
        tok = self.consumir("NUM", ["numero"])
        nodo.agregar(Nodo(tok.lexema, terminal=True))
        return nodo

    # <comentario> -> COMENT                                                  (P35)
    def comentario(self) -> Nodo:
        nodo = Nodo("<comentario>")
        tok = self.consumir("COMENT")
        nodo.agregar(Nodo(tok.lexema, terminal=True))
        return nodo

    # -- entrada publica ----------------------------------------------------
    def analizar_programa(self) -> Nodo:
        arbol = self.programa()
        self.consumir("EOF", ["fin de entrada"])
        return arbol

    def analizar_instruccion(self) -> Nodo:
        arbol = self.instruccion()
        self.consumir("EOF", ["fin de entrada"])
        return arbol


# ---------------------------------------------------------------------------
# 5. Impresion del arbol
# ---------------------------------------------------------------------------


def arbol_texto(nodo: Nodo, prefijo: str = "", es_ultimo: bool = True, raiz: bool = True) -> list[str]:
    conector = "" if raiz else ("└── " if es_ultimo else "├── ")
    lineas = [prefijo + conector + nodo.simbolo]
    if raiz:
        nuevo_prefijo = ""
    else:
        nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
    for k, hijo in enumerate(nodo.hijos):
        lineas.extend(arbol_texto(hijo, nuevo_prefijo, k == len(nodo.hijos) - 1, raiz=False))
    return lineas


def arbol_dot(nodo: Nodo, nombre: str = "Gramatica") -> str:
    lineas = ["digraph arbol {", f'  label="{nombre}";', "  labelloc=t;",
              "  node [shape=box, fontname=Consolas, fontsize=10];"]
    contador = [0]

    def visitar(n: Nodo, padre: int | None = None) -> int:
        actual = contador[0]
        contador[0] += 1
        forma = "box" if not n.terminal else "plaintext"
        etiqueta = n.simbolo.replace('"', '\\"')
        lineas.append(f'  n{actual} [label="{etiqueta}", shape={forma}];')
        if padre is not None:
            lineas.append(f"  n{padre} -> n{actual};")
        for h in n.hijos:
            visitar(h, actual)
        return actual

    visitar(nodo)
    lineas.append("}")
    return "\n".join(lineas)


def mermaid(nodo: Nodo) -> str:
    """Devuelve un diagrama Mermaid (graph TD) del arbol."""
    contador = [0]
    nodos: list[str] = []
    aristas: list[str] = []

    def etiqueta(n: Nodo) -> str:
        txt = n.simbolo
        for car, ent in (("#", "#35;"), ('"', "#quot;"), ("<", "#lt;"), (">", "#gt;")):
            txt = txt.replace(car, ent)
        return txt

    def visitar(n: Nodo) -> str:
        actual = f"n{contador[0]}"
        contador[0] += 1
        nodos.append(f'  {actual}["{etiqueta(n)}"]')
        for h in n.hijos:
            hijo = visitar(h)
            aristas.append(f"  {actual} --> {hijo}")
        return actual

    visitar(nodo)
    return "\n".join(["graph TD", *nodos, *aristas])


# ---------------------------------------------------------------------------
# 6. Cadenas de prueba (Pregunta 4 y extension creativa)
# ---------------------------------------------------------------------------

CASOS_P4 = [
    (1, "x = 10 #", True, "Asignacion simple: identificador, '=', numero y terminador."),
    (2, "z = x + y #", True, "Asignacion aritmetica: operando, operador '+' y expresion."),
    (3, "salida z #", True, "Instruccion de salida completa."),
    (4, "x 10 #", False, "Falta el operador de asignacion '=' entre el identificador y el numero."),
    (5, "z=+xy#", False, "El operador '+' aparece donde deberia empezar un operando: falta el operando izquierdo (el lenguaje no tiene operadores unarios). Si se separa como 'z = + x y #', ademas falta un operador entre 'x' e 'y'."),
    (6, "salida #", False, "Falta el identificador que se desea imprimir antes del '#'."),
    (7, "x = 20", False, "Falta el terminador de instruccion '#'."),
    (8, "Begin\nPrograma prueba\nx = 5 #\nsalida x #\nEnd", True, "Programa completo: Begin Programa <id> <instrucciones> End."),
]

CASOS_EXTENSION = [
    ("si x > 10 entonces y = x + 1 # fin_si", True,
     "Condicional valido: condicion con operador relacional y bloque de instrucciones."),
    ("si x > 10 entonces y = x + 1 #", False,
     "Falta el cierre 'fin_si' del condicional."),
    ("si entonces y = 1 # fin_si", False,
     "Falta la condicion entre 'si' y 'entonces'."),
    ("si x >= 10 entonces salida x # fin_si", True,
     "Condicional con operador relacional de dos caracteres y salida interna."),
    ("si x == 10 entonces y = 1 # fin_si", True,
     "Condicional con el operador de igualdad '==' (dos caracteres)."),
]

# Control de precedencia: se comprueba la forma de la raiz de
# <expresion_aritmetica> para asegurar que '*' '/' no absorben un '+'/'-'.
CASOS_PRECEDENCIA = [
    ("z = x + y #", ["<termino>", "<resto_expresion_aritmetica>"]),
    ("z = a * b + c #", ["<termino>", "<resto_expresion_aritmetica>"]),
    ("z = a + b * c #", ["<termino>", "<resto_expresion_aritmetica>"]),
    ("z = a * b #", ["<termino_aritmetico>"]),
]

PROGRAMA_REFERENCIA = """\
Begin
Programa operativo_01_02

x = 1.345 #
y = 20 #

/* operaciones y salidas */

z = x + y #
z2 = x + y #
h = z - x #
h2 = z - x #
k = h * y #
t = k / z #
m = k % 10 #

salida z #
salida h #
salida k #
salida t #
salida m #

temporal = 0 #
temporal = x #
x = y #
y = temporal #

salida x #
salida y #

End
"""


# ---------------------------------------------------------------------------
# 7. Ejecucion
# ---------------------------------------------------------------------------


def validar_programa(texto: str) -> tuple[bool, str, Nodo | None]:
    try:
        tokens = tokenizar(texto)
        parser = Parser(tokens)
        arbol = parser.analizar_programa()
        return True, "Cadena valida", arbol
    except ErrorLexico as e:
        return False, str(e), None
    except ErrorSintactico as e:
        return False, str(e), None


def validar_instruccion(texto: str) -> tuple[bool, str, Nodo | None]:
    try:
        tokens = tokenizar(texto)
        parser = Parser(tokens)
        arbol = parser.analizar_instruccion()
        return True, "Cadena valida", arbol
    except ErrorLexico as e:
        return False, str(e), None
    except ErrorSintactico as e:
        return False, str(e), None


def etiquetas_hijas(arbol: Nodo | None, simbolo: str) -> list[str] | None:
    """Etiquetas de los hijos del primer nodo con `simbolo` (o None)."""
    if arbol is None:
        return None
    if arbol.simbolo == simbolo:
        return [h.simbolo for h in arbol.hijos]
    for h in arbol.hijos:
        encontrado = etiquetas_hijas(h, simbolo)
        if encontrado is not None:
            return encontrado
    return None


def hojas(arbol: Nodo) -> list[str]:
    """Hojas terminales de izquierda a derecha, sin los nodos epsilon."""
    if not arbol.hijos:
        return [] if arbol.simbolo == "ε" else [arbol.simbolo]
    resultado: list[str] = []
    for h in arbol.hijos:
        resultado.extend(hojas(h))
    return resultado


def main() -> int:
    salida = Path(__file__).parent / "salidas"
    salida.mkdir(exist_ok=True)

    lineas: list[str] = []
    fallos = 0

    # --- Pregunta 2: programa de referencia ---------------------------------
    ok, msg, arbol = validar_programa(PROGRAMA_REFERENCIA)
    lineas.append("=" * 78)
    lineas.append("PREGUNTA 2 - Programa de referencia completo")
    lineas.append("=" * 78)
    lineas.append(f"Resultado: {'ACEPTADO' if ok else 'RECHAZADO'} - {msg}")
    lineas.append("")
    if ok and arbol is not None:
        # El arbol completo es muy grande: se resume y se exporta en formato DOT.
        conteo = {"<asignacion_simple>": 0, "<asignacion_aritmetica>": 0, "<salida>": 0,
                  "<condicional>": 0, "<comentario>": 0}

        def contar(n: Nodo) -> None:
            if n.simbolo in conteo:
                conteo[n.simbolo] += 1
            for h in n.hijos:
                contar(h)

        contar(arbol)
        lineas.append("Instrucciones reconocidas en el programa de referencia:")
        lineas.append(f"  - asignaciones simples      : {conteo['<asignacion_simple>']}")
        lineas.append(f"  - asignaciones aritmeticas  : {conteo['<asignacion_aritmetica>']}")
        lineas.append(f"  - instrucciones de salida   : {conteo['<salida>']}")
        lineas.append(f"  - comentarios               : {conteo['<comentario>']}")
        total = sum(conteo.values())
        lineas.append(f"  - total de elementos        : {total}")
        lineas.append("(arbol completo exportado en salidas/arbol_programa_referencia.dot)")
        lineas.append("")
        (salida / "arbol_programa_referencia.dot").write_text(
            arbol_dot(arbol, "Programa de referencia"), encoding="utf-8"
        )
    else:
        fallos += 1

    # --- Pregunta 4 ---------------------------------------------------------
    lineas.append("=" * 78)
    lineas.append("PREGUNTA 4 - Validacion de cadenas")
    lineas.append("=" * 78)
    lineas.append(f"{'Caso':<6}{'Cadena':<30}{'Esperado':<11}{'Obtenido':<11}Estado")
    for numero, cadena, esperado, motivo in CASOS_P4:
        es_programa = cadena.lstrip().startswith("Begin")
        if es_programa:
            ok, msg, _ = validar_programa(cadena)
        else:
            ok, msg, _ = validar_instruccion(cadena)
        obtenido = "VALIDA" if ok else "INVALIDA"
        resultado = "OK" if ok == esperado else "FALLO"
        if ok != esperado:
            fallos += 1
        plana = cadena.replace("\n", " ")
        if len(plana) > 28:
            plana = plana[:25] + "..."
        lineas.append(f"{numero:<6}{plana:<30}{'VALIDA' if esperado else 'INVALIDA':<11}{obtenido:<11}{resultado}")
        if es_programa:
            lineas.append(f"{'':<6}Cadena completa (los saltos de linea se muestran como ' / '):")
            lineas.append(f"{'':<6}{cadena.replace(chr(10), ' / ')}")
        lineas.append(f"{'':<6}Analisis: {msg}")
        lineas.append(f"{'':<6}Justificacion: {motivo}")
    lineas.append("")

    # --- Extension creativa -------------------------------------------------
    lineas.append("=" * 78)
    lineas.append("EXTENSION CREATIVA (opcion A) - condicional si ... entonces ... fin_si")
    lineas.append("=" * 78)
    for cadena, esperado, motivo in CASOS_EXTENSION:
        ok, msg, _ = validar_instruccion(cadena)
        if ok != esperado:
            fallos += 1
        lineas.append(f"Cadena   : {cadena}")
        lineas.append(f"Esperado : {'VALIDA' if esperado else 'INVALIDA'}")
        lineas.append(f"Obtenido : {'VALIDA' if ok else 'INVALIDA'} - {msg}")
        lineas.append(f"Motivo   : {motivo}")
        lineas.append("")
    lineas.append("")

    # --- Pregunta 3: derivacion y arbol de 'z = x + y #' --------------------
    objetivo = "z = x + y #"
    ok, msg, arbol = validar_instruccion(objetivo)
    lineas.append("=" * 78)
    lineas.append(f"PREGUNTA 3 - Arbol de derivacion de {objetivo!r}")
    lineas.append("=" * 78)
    lineas.append(f"Resultado: {'ACEPTADO' if ok else 'RECHAZADO'} - {msg}")
    lineas.append("")
    if ok and arbol is not None:
        texto = "\n".join(arbol_texto(arbol))
        lineas.append(texto)
        lineas.append("")
        (salida / "arbol_z_igual_x_mas_y.txt").write_text(texto + "\n", encoding="utf-8")
        (salida / "arbol_z_igual_x_mas_y.dot").write_text(
            arbol_dot(arbol, "z = x + y #"), encoding="utf-8"
        )
        (salida / "arbol_z_igual_x_mas_y.mmd").write_text(mermaid(arbol) + "\n", encoding="utf-8")
        # hojas de izquierda a derecha (sin contar epsilon)
        lineas.append(f"Fronda (hojas de izquierda a derecha): {' '.join(hojas(arbol))}")
        lineas.append("")
    else:
        fallos += 1

    # --- escritura ----------------------------------------------------------
    texto_final = "\n".join(lineas)
    (salida / "validacion.txt").write_text(texto_final + "\n", encoding="utf-8")
    print(texto_final)
    print()
    print(f"Archivos generados en: {salida}")
    print(f"Fallos: {fallos}")
    return 0 if fallos == 0 else 1


if __name__ == "__main__":
    if "--check" in sys.argv:
        errores = 0
        for numero, cadena, esperado, _ in CASOS_P4:
            if cadena.lstrip().startswith("Begin"):
                ok, _, _ = validar_programa(cadena)
            else:
                ok, _, _ = validar_instruccion(cadena)
            errores += ok != esperado
        ok, _, _ = validar_programa(PROGRAMA_REFERENCIA)
        errores += not ok
        for cadena, esperado, _ in CASOS_EXTENSION:
            ok, _, _ = validar_instruccion(cadena)
            errores += ok != esperado
        for cadena, esperado in CASOS_PRECEDENCIA:
            ok, _, arbol = validar_instruccion(cadena)
            errores += not (
                ok and etiquetas_hijas(arbol, "<expresion_aritmetica>") == esperado
            )
        objetivo = "z = x + y #"
        ok, _, arbol = validar_instruccion(objetivo)
        esperado_hojas = [t.lexema for t in tokenizar(objetivo) if t.tipo != "EOF"]
        errores += not (ok and arbol is not None and hojas(arbol) == esperado_hojas)
        print(f"Verificacion: {'OK' if errores == 0 else f'{errores} fallo(s)'}")
        sys.exit(0 if errores == 0 else 1)
    sys.exit(main())
