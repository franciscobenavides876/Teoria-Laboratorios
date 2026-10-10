#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratorio 2 - Expresiones Regulares con JFLAP (INFO1148)
Genera y valida los archivos .jff de las cuatro preguntas.

Para cada pregunta:
  1. Define el automata (AFN estilo conversion ER->AFN de JFLAP con
     transiciones lambda; AFD obtenido por eliminacion de no determinismo).
  2. Valida TODAS las cadenas hasta longitud 7 contra el lenguaje formal
     (predicado de la expresion regular) y, en P3/P4, verifica que el AFN y
     el AFD son equivalentes.
  3. Ejecuta los casos de prueba del PDF y imprime las tablas del informe.
  4. Escribe el archivo .jff en formato JFLAP y lo re-lee para comprobar
     que el XML generado es valido (round-trip).

Uso:  python generar_jff.py
"""

import os
import itertools
import xml.etree.ElementTree as ET

ALFABETOS = {"P1": "01", "P2": "ab", "P3": "01", "P4": "ab"}

# ---------------------------------------------------------------------------
# Estructura basica de automata
# ---------------------------------------------------------------------------

class Automata:
    def __init__(self, nombre, estados, transiciones, inicial, finales, alfabeto):
        """estados: lista de ids (enteros); transiciones: lista de
        (origen, destino, simbolo|None) donde None representa lambda."""
        self.nombre = nombre
        self.estados = list(estados)
        self.transiciones = list(transiciones)
        self.inicial = inicial
        self.finales = set(finales)
        self.alfabeto = alfabeto

    # -- validacion estructural ------------------------------------------------
    def validar_estructura(self):
        ids = set(self.estados)
        assert len(ids) == len(self.estados), f"{self.nombre}: ids de estado duplicados"
        assert self.inicial in ids, f"{self.nombre}: estado inicial inexistente"
        assert self.finales <= ids, f"{self.nombre}: estado final inexistente"
        for (o, d, s) in self.transiciones:
            assert o in ids and d in ids, f"{self.nombre}: transicion con estado inexistente ({o}->{d})"
            assert s is None or s in self.alfabeto, f"{self.nombre}: simbolo invalido {s!r}"

    def es_determinista(self):
        vistos = set()
        for (o, _d, s) in self.transiciones:
            if s is None:
                return False
            if (o, s) in vistos:
                return False
            vistos.add((o, s))
        return True

    def cantidad_lambda(self):
        return sum(1 for t in self.transiciones if t[2] is None)

    # -- simulacion ------------------------------------------------------------
    def _cierre_lambda(self, conjunto):
        pila = list(conjunto)
        alcanzados = set(conjunto)
        while pila:
            e = pila.pop()
            for (o, d, s) in self.transiciones:
                if o == e and s is None and d not in alcanzados:
                    alcanzados.add(d)
                    pila.append(d)
        return alcanzados

    def acepta(self, cadena):
        actuales = self._cierre_lambda({self.inicial})
        for simbolo in cadena:
            siguientes = set()
            for e in actuales:
                for (o, d, s) in self.transiciones:
                    if o == e and s == simbolo:
                        siguientes.add(d)
            actuales = self._cierre_lambda(siguientes)
            if not actuales:
                return False
        return bool(actuales & self.finales)

    # -- escritura .jff (formato JFLAP) ----------------------------------------
    def escribir_jff(self, ruta, coords):
        lineas = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>']
        lineas.append("<structure>")
        lineas.append("\t<type>fa</type>")
        lineas.append("\t<automaton>")
        for i, e in enumerate(self.estados):
            x, y = coords[e]
            attrs = f'id="{e}" x="{float(x)}" y="{float(y)}" name="q{i}"'
            if e == self.inicial:
                attrs += ' initial="true"'
            if e in self.finales:
                attrs += ' final="true"'
            lineas.append(f"\t\t<state {attrs}>")
            lineas.append("\t\t</state>")
        for (o, d, s) in self.transiciones:
            lineas.append("\t\t<transition>")
            lineas.append(f"\t\t\t<from>{o}</from>")
            lineas.append(f"\t\t\t<to>{d}</to>")
            if s is not None:
                lineas.append(f"\t\t\t<read>{s}</read>")
            lineas.append("\t\t</transition>")
        lineas.append("\t</automaton>")
        lineas.append("</structure>")
        with open(ruta, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lineas) + "\n")

    # -- lectura .jff (round-trip) --------------------------------------------
    @staticmethod
    def leer_jff(ruta, alfabeto):
        arbol = ET.parse(ruta)
        raiz = arbol.getroot()
        assert raiz.tag == "structure", "raiz != structure"
        assert raiz.findtext("type") == "fa", "type != fa"
        aut = raiz.find("automaton")
        estados, inicial, finales = [], None, set()
        for st in aut.findall("state"):
            sid = int(st.get("id"))
            estados.append(sid)
            if st.get("initial") == "true":
                inicial = sid
            if st.get("final") == "true":
                finales.add(sid)
        transiciones = []
        for tr in aut.findall("transition"):
            o = int(tr.findtext("from"))
            d = int(tr.findtext("to"))
            reads = tr.findall("read")
            if not reads:
                transiciones.append((o, d, None))
            else:
                for r in reads:
                    transiciones.append((o, d, r.text))
        nombre = os.path.basename(ruta)
        return Automata(nombre, estados, transiciones, inicial, finales, alfabeto)


def coords_fila(estados, x0=60, paso=110, y=150):
    return {e: (x0 + paso * i, y) for i, e in enumerate(estados)}


# ---------------------------------------------------------------------------
# Definicion de los automatas
# ---------------------------------------------------------------------------

def p1_afn():
    """ER: (0+1)*01  -> AFN con lambda (Thompson / estilo JFLAP).
    q0..q3 : (0+1)*   (q0 inicio, q1-q2 el 0+1, q3 final de la estrella)
    q4..q7 : concatenacion 0, lambda, 1   (q7 final)"""
    estados = list(range(8))
    trans = [
        (0, 1, None), (0, 3, None),          # lambda del estado inicial de la estrella
        (2, 1, None), (2, 3, None),          # lambda al repetir o salir de la estrella
        (1, 2, "0"), (1, 2, "1"),            # 0+1
        (3, 4, None),                        # concatenacion con "01"
        (4, 5, "0"), (5, 6, None), (6, 7, "1"),
    ]
    return Automata("P1_AFN", estados, trans, 0, {7}, ALFABETOS["P1"])


def p2_afn():
    """ER: a(a+b)*b -> AFN con lambda.
    q0 -a-> q1  |  estrella en q2..q5  |  q6 -b-> q7 (final)"""
    estados = list(range(8))
    trans = [
        (0, 1, "a"),                         # a inicial obligatorio
        (1, 2, None),                        # concatenacion
        (2, 3, None), (2, 5, None),          # inicio de la estrella
        (3, 4, "a"), (3, 4, "b"),            # a+b
        (4, 3, None), (4, 5, None),          # repetir o salir
        (5, 6, None),                        # concatenacion
        (6, 7, "b"),                         # b final obligatorio
    ]
    return Automata("P2_AFN", estados, trans, 0, {7}, ALFABETOS["P2"])


def p3_afn():
    """ER: (0+1)*101(0+1)* -> AFN con lambda.
    q0..q3 estrella | q4-q5 '1' | q6-q7 '0' | q8-q9 '1' | q10..q13 estrella"""
    estados = list(range(14))
    trans = [
        (0, 1, None), (0, 3, None), (2, 1, None), (2, 3, None),
        (1, 2, "0"), (1, 2, "1"),            # (0+1)*
        (3, 4, None),                        # concatenacion
        (4, 5, "1"), (5, 6, None),           # 1
        (6, 7, "0"), (7, 8, None),           # 0
        (8, 9, "1"), (9, 10, None),          # 1
        (10, 11, None), (10, 13, None),      # inicio de la estrella final
        (12, 11, None), (12, 13, None),      # repetir o salir
        (11, 12, "0"), (11, 12, "1"),        # (0+1)*
    ]
    return Automata("P3_AFN", estados, trans, 0, {13}, ALFABETOS["P3"])


def p3_afd():
    """AFD por eliminacion de no determinismo (o conjunto de subconjuntos).
    q0: nada | q1: vio '1' | q2: vio '10' | q3: encontro '101' (final)"""
    estados = list(range(4))
    trans = [
        (0, 0, "0"), (0, 1, "1"),
        (1, 2, "0"), (1, 1, "1"),
        (2, 0, "0"), (2, 3, "1"),
        (3, 3, "0"), (3, 3, "1"),
    ]
    return Automata("P3_AFD", estados, trans, 0, {3}, ALFABETOS["P3"])


def p4_afn():
    """ER: (a+b)*a(a+b)*bb -> AFN con lambda.
    q0..q3 estrella | q4 -a-> q5 | q6..q9 estrella | q10 -b-> q11 -b-> q12.."""
    estados = list(range(14))
    trans = [
        (0, 1, None), (0, 3, None), (2, 1, None), (2, 3, None),
        (1, 2, "a"), (1, 2, "b"),            # primera (a+b)*
        (3, 4, None),                        # concatenacion
        (4, 5, "a"),                         # la 'a' que garantiza "al menos una a"
        (5, 6, None),                        # concatenacion
        (6, 7, None), (6, 9, None),          # inicio de la segunda estrella
        (8, 7, None), (8, 9, None),          # repetir o salir
        (7, 8, "a"), (7, 8, "b"),            # a+b
        (9, 10, None),                       # concatenacion
        (10, 11, "b"), (11, 12, None), (12, 13, "b"),  # bb final
    ]
    return Automata("P4_AFN", estados, trans, 0, {13}, ALFABETOS["P4"])


def p4_afd():
    """AFD equivalente (minimo): q0 sin 'a' aun | q1 con 'a' sin b final |
    q2 con 'a' y una b final | q3 termina en bb con al menos una a (final)"""
    estados = list(range(4))
    trans = [
        (0, 1, "a"), (0, 0, "b"),
        (1, 1, "a"), (1, 2, "b"),
        (2, 1, "a"), (2, 3, "b"),
        (3, 1, "a"), (3, 3, "b"),
    ]
    return Automata("P4_AFD", estados, trans, 0, {3}, ALFABETOS["P4"])


# ---------------------------------------------------------------------------
# Lenguajes formales (predicados de las ER) para verificacion exhaustiva
# ---------------------------------------------------------------------------

def lenguaje_p1(w):   return w.endswith("01")
def lenguaje_p2(w):   return len(w) >= 2 and w[0] == "a" and w[-1] == "b"
def lenguaje_p3(w):   return "101" in w
def lenguaje_p4(w):   return ("a" in w) and w.endswith("bb")


def todas_las_cadenas(alfabeto, longitud_max):
    for n in range(longitud_max + 1):
        for t in itertools.product(alfabeto, repeat=n):
            yield "".join(t)


# ---------------------------------------------------------------------------
# Casos de prueba del PDF
# ---------------------------------------------------------------------------

CASOS = {
    "P1": ["01", "101", "1101", "0001", "10", "111", "0100", "10101"],
    "P2": ["ab", "aab", "abb", "abab", "aabab", "b", "a", "ba", "bb", "aba",
           "baba", "aababab"],
    "P3": ["101", "0101", "1010", "11011", "000", "111", "1001", "1101010"],
    "P4": ["abb", "aabb", "babbb", "ababbb", "babb",
           "bb", "aaa", "aba", "baba", "abab",
           "bab", "ab"],
}


def main():
    aqui = os.path.dirname(os.path.abspath(__file__))
    LONG_MAX = 7

    fabrica = {
        "P1_AFN.jff": (p1_afn, lenguaje_p1, None),
        "P2_AFN.jff": (p2_afn, lenguaje_p2, None),
        "P3_AFN.jff": (p3_afn, lenguaje_p3, lenguaje_p3),
        "P3_AFD.jff": (p3_afd, lenguaje_p3, lenguaje_p3),
        "P4_AFN.jff": (p4_afn, lenguaje_p4, lenguaje_p4),
        "P4_AFD.jff": (p4_afd, lenguaje_p4, lenguaje_p4),
    }

    print("=" * 78)
    print("VERIFICACION EXHAUSTIVA (todas las cadenas de longitud <= %d)" % LONG_MAX)
    print("=" * 78)
    fallos = 0
    for archivo, (fab, lenguaje, _) in fabrica.items():
        a = fab()
        a.validar_estructura()
        malas = [w for w in todas_las_cadenas(a.alfabeto, LONG_MAX) if a.acepta(w) != lenguaje(w)]
        estado = "OK" if not malas else "FALLOS: %r" % malas[:5]
        fallos += len(malas)
        print(f"  {archivo:12s} lenguaje correcto sobre {len(list(todas_las_cadenas(a.alfabeto, LONG_MAX)))} cadenas -> {estado}")

    # Equivalencia AFN vs AFD (P3 y P4)
    for par, lenguaje in ((("P3_AFN.jff", "P3_AFD.jff"), lenguaje_p3),
                          (("P4_AFN.jff", "P4_AFD.jff"), lenguaje_p4)):
        afn = fabrica[par[0]][0]()
        afd = fabrica[par[1]][0]()
        difs = [w for w in todas_las_cadenas(afn.alfabeto, LONG_MAX)
                if afn.acepta(w) != afd.acepta(w)]
        fallos += len(difs)
        print(f"  {par[0]} == {par[1]} ? {'OK (equivalentes)' if not difs else 'DIFERENTES: %r' % difs[:5]}")

    # AFD realmente determinista y sin lambda
    for archivo in ("P3_AFD.jff", "P4_AFD.jff"):
        a = fabrica[archivo][0]()
        assert a.es_determinista() and a.cantidad_lambda() == 0, f"{archivo} no es un AFD valido"
    print("  Los AFD no tienen lambda y son deterministas -> OK")
    print()

    # -- escribir .jff y re-leerlos (round-trip) -------------------------------
    print("=" * 78)
    print("GENERACION DE ARCHIVOS .jff")
    print("=" * 78)
    inventario = {}
    for archivo, (fab, _, _) in fabrica.items():
        a = fab()
        ruta = os.path.join(aqui, archivo)
        a.escribir_jff(ruta, coords_fila(a.estados))
        b = Automata.leer_jff(ruta, a.alfabeto)
        assert b.estados == a.estados, f"{archivo}: round-trip de estados fallido"
        assert sorted(b.transiciones) == sorted(a.transiciones), f"{archivo}: round-trip de transiciones fallido"
        assert b.inicial == a.inicial and b.finales == a.finales, f"{archivo}: round-trip de estados de aceptacion fallido"
        inventario[archivo] = b
        print(f"  {archivo:12s} {len(a.estados):2d} estados, "
              f"{len(a.transiciones):2d} transiciones ({a.cantidad_lambda()} lambda), "
              f"determinista={'si' if a.es_determinista() else 'no'} -> OK (re-leido)")

    # -- casos de prueba del PDF ----------------------------------------------
    print()
    print("=" * 78)
    print("CASOS DE PRUEBA DEL PDF")
    print("=" * 78)
    for p in ("P1", "P2", "P3", "P4"):
        print(f"\n[{p}]")
        if p in ("P3", "P4"):
            print("  Cadena        Esperado    AFN    AFD    Coinciden")
            for w in CASOS[p]:
                afn = inventario[f"{p}_AFN.jff"]
                afd = inventario[f"{p}_AFD.jff"]
                esp = lenguaje_p3(w) if p == "P3" else lenguaje_p4(w)
                r_afn, r_afd = afn.acepta(w), afd.acepta(w)
                ok = (r_afn == r_afd == esp)
                fallos += 0 if ok else 1
                print(f"  {w:<13s} {'Aceptada' if esp else 'Rechazada':<11s} "
                      f"{'Acept.' if r_afn else 'Rech.':<6s} {'Acept.' if r_afd else 'Rech.':<6s} "
                      f"{'Si' if ok else 'NO'}")
        else:
            print("  Cadena        Esperado    JFLAP    Coinciden")
            lenguaje = lenguaje_p1 if p == "P1" else lenguaje_p2
            afn = inventario[f"{p}_AFN.jff"]
            for w in CASOS[p]:
                esp = lenguaje(w)
                r = afn.acepta(w)
                ok = (r == esp)
                fallos += 0 if ok else 1
                print(f"  {w:<13s} {'Aceptada' if esp else 'Rechazada':<11s} "
                      f"{'Acept.' if r else 'Rech.':<8s} {'Si' if ok else 'NO'}")

    print()
    if fallos:
        print(f"*** {fallos} FALLO(S): revisar antes de entregar ***")
        raise SystemExit(1)
    print("TODAS LAS VERIFICACIONES PASARON.")


if __name__ == "__main__":
    main()
