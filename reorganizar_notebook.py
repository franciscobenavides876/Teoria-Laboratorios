#!/usr/bin/env python3
"""
Script para reorganizar el notebook Lab01_Cita_medica.ipynb
Traslada la interfaz gráfica (visualización con graphviz) hacia el final
separándola de la lógica del DFA.
"""

import json
from pathlib import Path

notebook_path = Path(__file__).parent / "Lab01_Cita_medica.ipynb"

print(f"Leyendo notebook: {notebook_path}")

# Leer el notebook
with open(notebook_path, 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Obtener la última celda (Actividad 4)
last_cell = notebook['cells'][-1]
all_lines = last_cell['source']

print(f"Última celda contiene {len(all_lines)} líneas")

# Encontrar donde comienza la visualización (búsqueda de "# Visualización")
viz_start_idx = None
for i, line in enumerate(all_lines):
    if "Visualización del DFA" in line:
        viz_start_idx = i
        break

if viz_start_idx is None:
    # Si no encuentra el comentario, usa índice aproximado (línea 75 en 0-based)
    viz_start_idx = 75

print(f"Visualización comienza en línea {viz_start_idx}")

# Dividir en dos partes
logic_lines = all_lines[:viz_start_idx]
viz_lines = all_lines[viz_start_idx:]

print(f"Parte 1 (Lógica del DFA): {len(logic_lines)} líneas")
print(f"Parte 2 (Visualización): {len(viz_lines)} líneas")

# Actualizar la última celda con solo la lógica
last_cell['source'] = logic_lines

# Crear la nueva celda de visualización
viz_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "viz_actividad_4",
    "metadata": {},
    "outputs": [],
    "source": viz_lines
}

# Agregar la nueva celda al final
notebook['cells'].append(viz_cell)

print(f"\nEstructura del notebook después de la reorganización:")
print(f"Total de celdas: {len(notebook['cells'])}")
print(f"Última celda tiene {len(notebook['cells'][-1]['source'])} líneas de visualización")

# Guardar el notebook modificado
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"\n✓ Notebook reorganizado y guardado exitosamente en:")
print(f"  {notebook_path}")
print("\nLa interfaz gráfica (visualización) ahora está al final del notebook.")
