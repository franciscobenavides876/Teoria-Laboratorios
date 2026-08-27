"""
Laboratorio 1 - INFO1148: Autómatas Finitos Deterministas (DFA)
Interfaz Gráfica Interactiva con ipywidgets y Graphviz
"""

from dataclasses import dataclass
from typing import Dict, Set, Tuple, List, Optional
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
import graphviz


# ==========================================
# 1. CLASE DFA BASE Y UTILIDADES GRÁFICAS
# ==========================================
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
            raise ValueError(f"No existe transición definida para el estado '{state}' con entrada '{symbol}'")
        return self.transition[key]

    def simulate(self, input_symbols: List[str]):
        current = self.start_state
        log = []
        for i, sym in enumerate(input_symbols):
            if sym not in self.alphabet:
                raise ValueError(
                    f"Símbolo no permitido: '{sym}'. Alfabeto válido: {sorted(self.alphabet)}"
                )
            nxt = self.step(current, sym)
            log.append((i + 1, current, sym, nxt))
            current = nxt
        return current, log

    def accepts(self, input_symbols: List[str]) -> bool:
        final, _ = self.simulate(input_symbols)
        return final in self.accept_states


def draw_dfa(dfa: DFA, highlight_path: Optional[List[Tuple[str, str, str]]] = None,
             highlight_state: Optional[str] = None):
    """Genera el grafo visual utilizando Graphviz con estilos y resaltados."""
    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="LR", bgcolor="transparent")
    dot.attr("node", fontname="Arial", fontsize="11", style="filled", fillcolor="#ffffff", color="#334155")
    dot.attr("edge", fontname="Arial", fontsize="10", color="#64748b")

    # Nodo invisible inicial
    dot.node("", shape="point", width="0.1", color="#0f172a")

    # Dibujar estados
    for s in sorted(dfa.states):
        is_accept = s in dfa.accept_states
        shape = "doublecircle" if is_accept else "circle"
        fillcolor = "#e0f2fe" if is_accept else "#ffffff"
        color = "#0284c7" if is_accept else "#334155"
        penwidth = "1.5"

        if s == "Error":
            fillcolor = "#fee2e2"
            color = "#ef4444"

        if highlight_state == s:
            fillcolor = "#bbf7d0" if is_accept else ("#fecaca" if s == "Error" else "#fef08a")
            color = "#16a34a" if is_accept else ("#dc2626" if s == "Error" else "#ca8a04")
            penwidth = "3.0"

        dot.node(s, shape=shape, penwidth=penwidth, fillcolor=fillcolor, color=color)

    # Flecha al estado inicial
    dot.edge("", dfa.start_state, color="#0f172a", penwidth="1.8")

    # Agrupar transiciones por origen y destino
    edges_labels = {}
    for (src, sym), dst in dfa.transition.items():
        edges_labels.setdefault((src, dst), []).append(sym)

    highlighted_pairs = set((src, dst) for (src, sym, dst) in (highlight_path or []))

    for (src, dst), syms in edges_labels.items():
        label = ", ".join(sorted(syms))
        if (src, dst) in highlighted_pairs:
            dot.edge(src, dst, label=label, color="#2563eb", penwidth="2.5", fontcolor="#1d4ed8")
        else:
            dot.edge(src, dst, label=label)

    return dot


def render_steps_table(log, final_state, is_accepted):
    """Genera una tabla HTML estética con los pasos de la simulación."""
    badge_bg = "#22c55e" if is_accepted else ("#ef4444" if final_state == "Error" else "#f59e0b")
    badge_text = "CITA AGENDADA (ACEPTADO)" if is_accepted else ("ESTADO DE ERROR" if final_state == "Error" else "EN PROCESO / NO FINALIZADO")
    
    html = f"""
    <div style="font-family: Arial, sans-serif; margin-top: 10px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <span style="background-color: {badge_bg}; color: white; padding: 5px 14px; border-radius: 20px; font-weight: bold; font-size: 13px;">
                {badge_text}
            </span>
            <span style="color: #475569; font-size: 14px;"><b>Estado Final:</b> <code>{final_state}</code></span>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; background-color: #f8fafc; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
            <thead>
                <tr style="background-color: #0f172a; color: #ffffff;">
                    <th style="padding: 9px 12px;">Paso</th>
                    <th style="padding: 9px 12px;">Estado Origen</th>
                    <th style="padding: 9px 12px;">Símbolo Entrada</th>
                    <th style="padding: 9px 12px;">Estado Destino</th>
                </tr>
            </thead>
            <tbody>
    """
    for i, s, sym, nxt in log:
        html += f"""
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px 12px; font-weight: bold; color: #64748b;">#{i}</td>
                    <td style="padding: 8px 12px; color: #1e293b;"><code>{s}</code></td>
                    <td style="padding: 8px 12px; color: #2563eb; font-weight: bold;">{sym}</td>
                    <td style="padding: 8px 12px; color: #0f172a; font-weight: 500;"><code>{nxt}</code></td>
                </tr>
        """
    html += """
            </tbody>
        </table>
    </div>
    """
    return HTML(html)


# ==========================================
# 2. DEFINICIÓN DE LOS 4 AUTÓMATAS
# ==========================================

# --- Ejercicio 1: Selección de Médico ---
states_1 = {"Inicio", "SeleccionarEspecialidad", "SeleccionarMedico", "SeleccionarFecha", "ConfirmarDatos", "CitaAgendada"}
alphabet_1 = {"especialidad", "medico", "fecha", "confirmar", "cancelar"}
trans_1 = {
    ("Inicio", "especialidad"): "SeleccionarEspecialidad",
    ("SeleccionarEspecialidad", "medico"): "SeleccionarMedico",
    ("SeleccionarMedico", "fecha"): "SeleccionarFecha",
    ("SeleccionarFecha", "confirmar"): "ConfirmarDatos",
    ("ConfirmarDatos", "confirmar"): "CitaAgendada",
    ("SeleccionarEspecialidad", "cancelar"): "Inicio",
    ("SeleccionarMedico", "cancelar"): "Inicio",
    ("SeleccionarFecha", "cancelar"): "Inicio",
    ("ConfirmarDatos", "cancelar"): "Inicio"
}
dfa_ej1 = DFA(states_1, alphabet_1, trans_1, "Inicio", {"CitaAgendada"})

# --- Ejercicio 2: Paso de Pago Online ---
states_2 = states_1.union({"Pago"})
alphabet_2 = alphabet_1.union({"pago"})
trans_2 = trans_1.copy()
trans_2[("ConfirmarDatos", "pago")] = "Pago"
del trans_2[("ConfirmarDatos", "confirmar")]
trans_2[("Pago", "confirmar")] = "CitaAgendada"
trans_2[("Pago", "cancelar")] = "Inicio"
dfa_ej2 = DFA(states_2, alphabet_2, trans_2, "Inicio", {"CitaAgendada"})

# --- Ejercicio 3: Múltiples Especialidades ---
states_3 = {
    "Inicio", "EspecialidadBroncopulmonar", "EspecialidadRadiologo",
    "SeleccionarMedico", "SeleccionarFecha", "ConfirmarDatos", "Pago", "CitaAgendada"
}
alphabet_3 = {"broncopulmonar", "radiologo", "medico", "fecha", "confirmar", "pago", "cancelar"}
trans_3 = {
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
dfa_ej3 = DFA(states_3, alphabet_3, trans_3, "Inicio", {"CitaAgendada"})

# --- Ejercicio 4: Manejo de Errores ---
states_4 = states_3.union({"Error"})
alphabet_4 = alphabet_3.copy()
trans_4 = {}
for s in states_4:
    for sym in alphabet_4:
        if s == "CitaAgendada":
            trans_4[(s, sym)] = "Inicio" if sym == "cancelar" else "CitaAgendada"
        elif s == "Error":
            trans_4[(s, sym)] = "Inicio" if sym == "cancelar" else "Error"
        else:
            if (s, sym) in trans_3:
                trans_4[(s, sym)] = trans_3[(s, sym)]
            else:
                trans_4[(s, sym)] = "Error"
dfa_ej4 = DFA(states_4, alphabet_4, trans_4, "Inicio", {"CitaAgendada"})

# Catálogo de Ejercicios
EXERCISES = {
    1: {
        "title": "Ejercicio 1: Médico Específico",
        "desc": "Agrega el subpaso de selección de médico tratante antes de elegir la fecha.",
        "dfa": dfa_ej1,
        "default_seq": "especialidad medico fecha confirmar confirmar"
    },
    2: {
        "title": "Ejercicio 2: Pago Online",
        "desc": "Incorpora la etapa obligatoria de pasarela de pago tras la revisión de datos.",
        "dfa": dfa_ej2,
        "default_seq": "especialidad medico fecha confirmar pago confirmar"
    },
    3: {
        "title": "Ejercicio 3: Múltiples Especialidades",
        "desc": "Bifurca el flujo desde Inicio permitiendo elegir entre Broncopulmonar o Radiólogo.",
        "dfa": dfa_ej3,
        "default_seq": "broncopulmonar medico fecha confirmar pago confirmar"
    },
    4: {
        "title": "Ejercicio 4: Manejo de Errores y Recuperación",
        "desc": "Convierte el autómata en total, derivando entradas inválidas al estado Error y recuperando con cancelar.",
        "dfa": dfa_ej4,
        "default_seq": "broncopulmonar pago cancelar radiologo medico fecha confirmar pago confirmar"
    }
}


# ==========================================
# 3. INTERFAZ GRÁFICA INTERACTIVA
# ==========================================
class LaboratorioUI:
    def __init__(self):
        self.current_ej = 1
        
        # Header HTML
        self.header = widgets.HTML(value="""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); color: white; padding: 18px 24px; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <h2 style="margin: 0 0 6px 0; font-size: 22px; font-family: Arial, sans-serif;">🔬 Simulador Interactivo - Laboratorio 1 (INFO1148)</h2>
            <p style="margin: 0; color: #94a3b8; font-size: 14px; font-family: Arial, sans-serif;">Modelamiento de Citas Médicas con Autómatas Finitos Deterministas</p>
        </div>
        """)
        
        # Botones de navegación de Ejercicios
        self.btn_ej1 = widgets.Button(description="1. Médico", button_style="primary", layout=widgets.Layout(width="24%"))
        self.btn_ej2 = widgets.Button(description="2. Pago", button_style="", layout=widgets.Layout(width="24%"))
        self.btn_ej3 = widgets.Button(description="3. Especialidades", button_style="", layout=widgets.Layout(width="24%"))
        self.btn_ej4 = widgets.Button(description="4. Error & Reset", button_style="", layout=widgets.Layout(width="24%"))
        
        self.btn_ej1.on_click(lambda _: self.select_exercise(1))
        self.btn_ej2.on_click(lambda _: self.select_exercise(2))
        self.btn_ej3.on_click(lambda _: self.select_exercise(3))
        self.btn_ej4.on_click(lambda _: self.select_exercise(4))
        
        self.nav_bar = widgets.HBox(
            [self.btn_ej1, self.btn_ej2, self.btn_ej3, self.btn_ej4],
            layout=widgets.Layout(justify_content="space-between", margin="0 0 14px 0")
        )
        
        # Área de información del ejercicio
        self.info_html = widgets.HTML()
        
        # Input de secuencia y botones de acción
        self.input_seq = widgets.Text(
            value="",
            placeholder="Ingresa los símbolos separados por espacio...",
            description="Secuencia:",
            layout=widgets.Layout(width="60%")
        )
        self.btn_run = widgets.Button(description="▶ Simular", button_style="success", layout=widgets.Layout(width="18%"))
        self.btn_reset = widgets.Button(description="🔄 Cargar Ejemplo", button_style="warning", layout=widgets.Layout(width="20%"))
        
        self.btn_run.on_click(self.on_simulate)
        self.btn_reset.on_click(self.on_load_example)
        
        self.input_bar = widgets.HBox(
            [self.input_seq, self.btn_run, self.btn_reset],
            layout=widgets.Layout(align_items="center", margin="0 0 12px 0")
        )
        
        # Chips de alfabeto interactivo
        self.chips_box = widgets.HBox(layout=widgets.Layout(flex_wrap="wrap", margin="0 0 12px 0"))
        
        # Contenedor de salida
        self.output_area = widgets.Output()
        
        # Contenedor Principal
        self.main_container = widgets.VBox([
            self.header,
            self.nav_bar,
            self.info_html,
            self.chips_box,
            self.input_bar,
            self.output_area
        ], layout=widgets.Layout(padding="10px", border="1px solid #cbd5e1", border_radius="14px", background_color="#f8fafc"))
        
        # Inicializar en el Ejercicio 1
        self.select_exercise(1)

    def select_exercise(self, ej_num: int):
        self.current_ej = ej_num
        
        # Actualizar estilos de botones
        buttons = [self.btn_ej1, self.btn_ej2, self.btn_ej3, self.btn_ej4]
        for i, btn in enumerate(buttons, start=1):
            btn.button_style = "primary" if i == ej_num else ""

        data = EXERCISES[ej_num]
        
        # Actualizar texto explicativo
        self.info_html.value = f"""
        <div style="background-color: #ffffff; border-left: 4px solid #2563eb; padding: 10px 16px; border-radius: 6px; margin-bottom: 10px; font-family: Arial, sans-serif;">
            <b style="color: #0f172a; font-size: 16px;">{data['title']}</b>
            <p style="color: #475569; margin: 4px 0 0 0; font-size: 13px;">{data['desc']}</p>
        </div>
        """
        
        # Crear botones rápidos para insertar símbolos del alfabeto
        chips = [widgets.HTML("<b style='font-size:12px; color:#475569; margin-right:8px; line-height:28px;'>Alfabeto:</b>")]
        for sym in sorted(data['dfa'].alphabet):
            b = widgets.Button(description=sym, layout=widgets.Layout(height="28px", margin="2px 4px"))
            b.on_click(lambda _, s=sym: self.append_symbol(s))
            chips.append(b)
        self.chips_box.children = chips
        
        # Cargar secuencia por defecto y simular
        self.input_seq.value = data['default_seq']
        self.on_simulate(None)

    def append_symbol(self, sym: str):
        val = self.input_seq.value.strip()
        self.input_seq.value = f"{val} {sym}".strip()

    def on_load_example(self, _):
        self.input_seq.value = EXERCISES[self.current_ej]['default_seq']
        self.on_simulate(None)

    def on_simulate(self, _):
        self.output_area.clear_output()
        dfa = EXERCISES[self.current_ej]['dfa']
        raw_text = self.input_seq.value.replace(",", " ").strip()
        seq = [s for s in raw_text.split() if s]

        with self.output_area:
            if not seq:
                display(HTML("<p style='color: #ef4444; font-family: Arial;'>⚠️ Ingresa al menos un símbolo para iniciar la simulación.</p>"))
                display(draw_dfa(dfa))
                return

            try:
                final_state, log = dfa.simulate(seq)
                is_acc = final_state in dfa.accept_states
                
                # Mostrar Tabla y Estado
                display(render_steps_table(log, final_state, is_acc))
                
                # Mostrar Grafo Graphviz con camino resaltado
                hl_path = [(s, sym, nxt) for (_, s, sym, nxt) in log]
                display(draw_dfa(dfa, highlight_path=hl_path, highlight_state=final_state))
                
            except ValueError as e:
                display(HTML(f"""
                <div style="background-color: #fee2e2; border: 1px solid #f87171; color: #991b1b; padding: 10px 14px; border-radius: 8px; font-family: Arial; margin-top: 10px;">
                    <b>❌ Error en Simulación:</b> {str(e)}
                </div>
                """))
                display(draw_dfa(dfa))

    def show(self):
        display(self.main_container)


# ==========================================
# 4. INSTANCIACIÓN Y EJECUCIÓN
# ==========================================
app = LaboratorioUI()
app.show()