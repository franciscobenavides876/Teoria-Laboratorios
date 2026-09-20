from src.lexer import PrologLexer

def ejecutar_bateria_pruebas():
    # 20 Casos de Prueba Válidos
    pruebas_validas = [
        ("padre", "TK_ATOMO"),
        ("'Juan Perez'", "TK_ATOMO"),
        ("X", "TK_VARIABLE"),
        ("_temporal", "TK_VARIABLE"),
        ("_", "TK_VAR_ANONIMA"),
        ("42", "TK_ENTERO"),
        ("3.1415", "TK_REAL"),
        ("1.2e-4", "TK_REAL"),
        ('"cadena con escape \\n"', "TK_CADENA"),
        (":-", "TK_CUELLO"),
        ("?-", "TK_CONSULTA"),
        ("-->", "TK_FLECHA_DCG"),
        ("==", "TK_IDENTICO"),
        ("=<", "TK_MENOR_IGUAL"),
        ("=..", "TK_UNIV"),
        ("//", "TK_DIV_ENTERA"),
        ("**", "TK_POTENCIA"),
        ("is", "TK_IS"),
        ("mod", "TK_MOD"),
        ("\\+", "TK_NEGACION")
    ]

    # 8 Casos de Prueba Inválidos (Errores léxicos)
    pruebas_invalidas = [
        ("`simbolo_invalido", "Carácter no reconocido"),
        ("$100", "Carácter no reconocido"),
        ("#directiva", "Carácter no reconocido"),
        ('"cadena sin cierre', "Cadena de texto sin cierre"),
        ("'atomo sin cierre", "Átomo entrecomillado sin cierre"),
        ("/* comentario sin cierre", "Comentario de bloque sin cierre"),
        ("12.34e+", "Número real con exponente mal formado"),
        ("~invalido", "Carácter no reconocido")
    ]

    print("--- EJECUTANDO PRUEBAS VÁLIDAS ---")
    correctas_val = 0
    for entrada, tipo_esp in pruebas_validas:
        lex = PrologLexer(entrada)
        toks, errs = lex.analizar()
        if toks and toks[0].tipo == tipo_esp and len(errs) == 0:
            correctas_val += 1
        else:
            print(f"Falla en prueba válida: {entrada}")
    print(f"Resultado pruebas válidas: {correctas_val}/{len(pruebas_validas)}")

    print("\n--- EJECUTANDO PRUEBAS INVÁLIDAS ---")
    correctas_inval = 0
    for entrada, msg_esperado in pruebas_invalidas:
        lex = PrologLexer(entrada)
        toks, errs = lex.analizar()
        if errs and msg_esperado in errs[0].mensaje:
            correctas_inval += 1
        else:
            print(f"Falla en prueba inválida: {entrada}")
    print(f"Resultado pruebas inválidas: {correctas_inval}/{len(pruebas_invalidas)}")

if __name__ == "__main__":
    ejecutar_bateria_pruebas()