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
# Definición formal del Ejercicio 2 (Agrega Pago conservando Ejercicio 1)
# ---------------------------------------------------------------------------
states_p2 = {
    "Inicio",
    "SeleccionarEspecialidad",
    "SeleccionarMedico",
    "SeleccionarFecha",
    "ConfirmarDatos",
    "Pago",
    "CitaAgendada"
}

alphabet_p2 = {"especialidad", "medico", "fecha", "confirmar", "pago", "cancelar"}

transition_p2 = {
    ("Inicio", "especialidad"): "SeleccionarEspecialidad",
    ("SeleccionarEspecialidad", "medico"): "SeleccionarMedico",
    ("SeleccionarMedico", "fecha"): "SeleccionarFecha",
    ("SeleccionarFecha", "confirmar"): "ConfirmarDatos",
    ("ConfirmarDatos", "pago"): "Pago",
    ("Pago", "confirmar"): "CitaAgendada",

    # Cancelaciones hacia el estado inicial
    ("SeleccionarEspecialidad", "cancelar"): "Inicio",
    ("SeleccionarMedico", "cancelar"): "Inicio",
    ("SeleccionarFecha", "cancelar"): "Inicio",
    ("ConfirmarDatos", "cancelar"): "Inicio",
    ("Pago", "cancelar"): "Inicio"
}

dfa_p2 = DFA(states_p2, alphabet_p2, transition_p2, "Inicio", {"CitaAgendada"})

# ---------------------------------------------------------------------------
# Simulación
# ---------------------------------------------------------------------------
secuencia_p2 = ["especialidad", "medico", "fecha", "confirmar", "pago", "confirmar"]
estado_final_p2, log_p2 = dfa_p2.simulate(secuencia_p2)

print("\n" + "=" * 60)
print(" RESULTADOS DE EJECUCIÓN - EJERCICIO 2")
print("=" * 60)
print(f"Secuencia ingresada : {secuencia_p2}")
print(f"Estado final        : {estado_final_p2}")
print(f"¿Cita agendada?     : {estado_final_p2 in dfa_p2.accept_states}")

print("\n" + "-" * 60)
print(f"{'#':<3} | {'Estado actual':<24} | {'Entrada':<12} | {'Nuevo estado'}")
print("-" * 60)
for i, curr, sym, nxt in log_p2:
    print(f"{i:<3} | {curr:<24} | {sym:<12} | {nxt}")
print("-" * 60)

# Generación del archivo PNG
def guardar_grafo(dfa: DFA, log: List, final_state: str, filename="ejercicio_2"):
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR")
    dot.node("", shape="point")

    for s in dfa.states:
        shape = "doublecircle" if s in dfa.accept_states else "circle"
        penwidth = "3" if s == final_state else "1"
        color = "green" if s == final_state and s in dfa.accept_states else "black"
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
            dot.edge(src, dst, label=label)

    try:
        dot.render(filename, cleanup=True)
        print(f"\n[OK] Imagen del grafo guardada como: {filename}.png")
    except Exception as e:
        print(f"\n[Aviso] Graphviz no pudo renderizar directamente: {e}")
        print("\nCódigo DOT para dreampuf.github.io/GraphvizOnline:")
        print(dot.source)

guardar_grafo(dfa_p2, log_p2, estado_final_p2)