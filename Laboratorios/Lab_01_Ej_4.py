import os
from dataclasses import dataclass
from typing import Dict, Set, Tuple, List
import graphviz

# Configuración automática del PATH de Graphviz en Windows
rutas_posibles = [
    r"C:\Program Files\Graphviz\bin",
    r"C:\Program Files (x86)\Graphviz\bin",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Graphviz\bin"),
    os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Graphviz\bin"),
]
for ruta in rutas_posibles:
    if os.path.isdir(ruta) and ruta not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + ruta

@dataclass
class DFA:
    states: Set[str]
    alphabet: Set[str]
    transition: Dict[Tuple[str, str], str]
    start_state: str
    accept_states: Set[str]

    def step(self, state: str, symbol: str) -> str:
        key = (state, symbol)
        if key not in self.transition:
            raise ValueError(f"No hay transición definida para {key}")
        return self.transition[key]

    def simulate(self, input_symbols: List[str]):
        current = self.start_state
        log = []
        for i, sym in enumerate(input_symbols):
            if sym not in self.alphabet:
                raise ValueError(f"Símbolo inválido: '{sym}'. Alfabeto: {sorted(self.alphabet)}")
            nxt = self.step(current, sym)
            log.append((i, current, sym, nxt))
            current = nxt
        return current, log

# ---------------------------------------------------------------------------
# 1. Base del Ejercicio 3 (Transiciones válidas)
# ---------------------------------------------------------------------------
states_p3 = {
    "Inicio",
    "EspecialidadBroncopulmonar",
    "EspecialidadRadiologo",
    "SeleccionarMedico",
    "SeleccionarFecha",
    "ConfirmarDatos",
    "Pago",
    "CitaAgendada"
}

alphabet_p4 = {
    "broncopulmonar",
    "radiologo",
    "medico",
    "fecha",
    "confirmar",
    "pago",
    "cancelar"
}

transition_p3 = {
    ("Inicio", "broncopulmonar"): "EspecialidadBroncopulmonar",
    ("Inicio", "radiologo"): "EspecialidadRadiologo",
    ("EspecialidadBroncopulmonar", "medico"): "SeleccionarMedico",
    ("EspecialidadRadiologo", "medico"): "SeleccionarMedico",
    ("SeleccionarMedico", "fecha"): "SeleccionarFecha",
    ("SeleccionarFecha", "confirmar"): "ConfirmarDatos",
    ("ConfirmarDatos", "pago"): "Pago",
    ("Pago", "confirmar"): "CitaAgendada",

    ("EspecialidadBroncopulmonar", "cancelar"): "Inicio",
    ("EspecialidadRadiologo", "cancelar"): "Inicio",
    ("SeleccionarMedico", "cancelar"): "Inicio",
    ("SeleccionarFecha", "cancelar"): "Inicio",
    ("ConfirmarDatos", "cancelar"): "Inicio",
    ("Pago", "cancelar"): "Inicio"
}

# ---------------------------------------------------------------------------
# 2. Definición formal del Ejercicio 4 (DFA Total con Estado Error)
# ---------------------------------------------------------------------------
states_p4 = states_p3.union({"Error"})
transition_p4 = {}

# Mapeo exhaustivo del producto cartesiano Q x Sigma
for s in states_p4:
    for sym in alphabet_p4:
        if s == "CitaAgendada":
            # Estado final: permanece en sí mismo o reinicia si se cancela
            transition_p4[(s, sym)] = "Inicio" if sym == "cancelar" else "CitaAgendada"
        elif s == "Error":
            # Si está en Error, solo sale con cancelar hacia Inicio; cualquier otra entrada se mantiene en Error
            transition_p4[(s, sym)] = "Inicio" if sym == "cancelar" else "Error"
        else:
            # Si la transición es válida se conserva, de lo contrario cae en Error
            if (s, sym) in transition_p3:
                transition_p4[(s, sym)] = transition_p3[(s, sym)]
            else:
                transition_p4[(s, sym)] = "Error"

dfa_p4 = DFA(states_p4, alphabet_p4, transition_p4, "Inicio", {"CitaAgendada"})

# ---------------------------------------------------------------------------
# 3. Simulación con caso de error y recuperación
# ---------------------------------------------------------------------------
# Prueba: El usuario elige especialidad, luego intenta pagar inmediatamente (error),
# cancela para recuperarse al Inicio, y completa el agendamiento correctamente.
secuencia_p4 = [
    "broncopulmonar",
    "pago",        # Símbolo no permitido en este paso -> Pasa a Error
    "cancelar",    # Mecanismo de recuperación -> Vuelve a Inicio
    "radiologo",
    "medico",
    "fecha",
    "confirmar",
    "pago",
    "confirmar"
]

estado_final_p4, log_p4 = dfa_p4.simulate(secuencia_p4)

print("\n" + "=" * 60)
print(" RESULTADOS DE EJECUCIÓN - EJERCICIO 4")
print("=" * 60)
print(f"Secuencia ingresada : {secuencia_p4}")
print(f"Estado final        : {estado_final_p4}")
print(f"¿Cita agendada?     : {estado_final_p4 in dfa_p4.accept_states}")

print("\n" + "-" * 60)
print(f"{'#':<3} | {'Estado actual':<26} | {'Entrada':<15} | {'Nuevo estado'}")
print("-" * 60)
for i, curr, sym, nxt in log_p4:
    print(f"{i:<3} | {curr:<26} | {sym:<15} | {nxt}")
print("-" * 60)

# Generación del archivo PNG
def guardar_grafo(dfa: DFA, log: List, final_state: str, filename="ejercicio_4"):
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR")
    dot.node("", shape="point")

    for s in dfa.states:
        shape = "doublecircle" if s in dfa.accept_states else "circle"
        penwidth = "3" if s == final_state else "1"
        color = "green" if s == final_state and s in dfa.accept_states else ("red" if s == "Error" else "black")
        dot.node(s, shape=shape, penwidth=penwidth, color=color)

    dot.edge("", dfa.start_state)

    edges_labels = {}
    for (src, sym), dst in dfa.transition.items():
        edges_labels.setdefault((src, dst), []).append(sym)

    highlighted_pairs = set((src, dst) for (_, src, sym, dst) in log)

    for (src, dst), syms in edges_labels.items():
        label = ", ".join(sorted(syms))
        if (src, dst) in highlighted_pairs:
            dot.edge(src, dst, label=label, color="blue", penwidth="2")
        else:
            # Para mantener la legibilidad visual, las transiciones estándar a Error se muestran discretas
            color = "gray" if dst == "Error" else "black"
            dot.edge(src, dst, label=label, color=color)

    try:
        dot.render(filename, cleanup=True)
        print(f"\n[OK] Imagen del grafo guardada como: {filename}.png")
    except Exception as e:
        print(f"\n[Aviso] Graphviz no pudo renderizar directamente: {e}")
        print("\nCódigo DOT para dreampuf.github.io/GraphvizOnline:")
        print(dot.source)

guardar_grafo(dfa_p4, log_p4, estado_final_p4)

# ---------------------------------------------------------------------------
# Justificación de las decisiones de diseño (Ejercicio 4)
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print(" JUSTIFICACIÓN DE DISEÑO - EJERCICIO 4")
print("=" * 60)
print(
    "- Se agregó un único estado 'Error' (no uno por cada tipo de fallo) para\n"
    "  mantener el autómata simple: no importa qué símbolo inválido se haya\n"
    "  ingresado, el sistema solo necesita informar que la acción no es\n"
    "  válida en el contexto actual y ofrecer una forma de recuperarse.\n"
    "- El DFA se 'totaliza' recorriendo el producto cartesiano Estados x\n"
    "  Alfabeto: toda combinación (estado, símbolo) que no estaba definida\n"
    "  en el Ejercicio 3 pasa explícitamente a 'Error'. Esto cumple con la\n"
    "  definición formal de un DFA, que exige una función de transición\n"
    "  total (definida para todo par estado-símbolo).\n"
    "- Desde 'Error' solo 'cancelar' es una transición válida y lleva de\n"
    "  vuelta a 'Inicio'; cualquier otro símbolo mantiene al autómata en\n"
    "  'Error' (auto-transición), evitando que el usuario quede 'atascado'\n"
    "  sin una vía de escape clara.\n"
    "- Desde 'CitaAgendada' (estado de aceptación) también se totalizó la\n"
    "  función: cualquier símbolo que no sea 'cancelar' mantiene al usuario\n"
    "  en 'CitaAgendada' (la cita ya está hecha, no hay más acciones\n"
    "  posibles), y 'cancelar' permite iniciar un nuevo proceso desde cero."
)