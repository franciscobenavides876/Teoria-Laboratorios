import sys
import os

# Resuelve la ruta base para ejecutar siempre de forma correcta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.lexer import PrologLexer
from tests.test_runner import ejecutar_bateria_pruebas

def procesar_archivo(ruta: str):
    if not os.path.exists(ruta):
        print(f"\n[Error] El archivo '{ruta}' no existe.")
        return

    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()

    print(f"\n==================================================")
    print(f" ARCHIVO: {ruta}")
    print(f"==================================================")
    lexer = PrologLexer(contenido)
    tokens, errores = lexer.analizar()

    print("\n--- 1. SECUENCIA DE TOKENS ---")
    for t in tokens:
        print(t)

    print("\n--- 2. TABLA DE LEXEMAS ---")
    registros = lexer.tabla.listar()
    if not registros:
        print("(Vacía)")
    else:
        for r in registros:
            print(f"ID {r['id']:<3} | Tipo: {r['categoria']:<12} | Lexema: '{r['lexema']}'")

    print("\n--- 3. ERRORES LÉXICOS DETECTADOS ---")
    if not errores:
        print("✓ Cero errores encontrados. Análisis léxico exitoso.")
    else:
        for err in errores:
            print(err)
    print("==================================================\n")

def menu_interactivo():
    while True:
        print("==================================================")
        print("   ANALIZADOR LÉXICO PROLOG - MENÚ PRINCIPAL")
        print("==================================================")
        print("1. Analizar archivo de pruebas válidas (pruebas_validas.pl)")
        print("2. Analizar archivo con errores léxicos (pruebas_invalidas.pl)")
        print("3. Ejecutar batería de pruebas (20 válidas / 8 inválidas)")
        print("4. Salir")
        print("--------------------------------------------------")
        
        opcion = input("Seleccione una opción (1-4): ").strip()

        if opcion == "1":
            ruta_valida = os.path.join(BASE_DIR, "tests", "pruebas_validas.pl")
            procesar_archivo(ruta_valida)
        elif opcion == "2":
            ruta_invalida = os.path.join(BASE_DIR, "tests", "pruebas_invalidas.pl")
            procesar_archivo(ruta_invalida)
        elif opcion == "3":
            ejecutar_bateria_pruebas()
        elif opcion == "4":
            print("Saliendo del programa.")
            break
        else:
            print("\nOpción no válida. Intente nuevamente.\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--test", "-t"]:
            ejecutar_bateria_pruebas()
        else:
            ruta_arg = sys.argv[1]
            if not os.path.isabs(ruta_arg) and not os.path.exists(ruta_arg):
                ruta_arg = os.path.join(BASE_DIR, ruta_arg)
            procesar_archivo(ruta_arg)
    else:
        menu_interactivo()