from typing import List, Tuple, Optional
from .token_types import Token, ErrorLexico, TablaLexemas

class PrologLexer:
    # Operadores multi-carácter ordenados de mayor a menor longitud
    OPERADORES = [
        ("-->", "TK_FLECHA_DCG"),
        ("=:=", "TK_EVAL_IGUAL"),
        ("=\\=", "TK_EVAL_DISTINTO"),
        ("\\==", "TK_NO_IDENTICO"),
        ("=..", "TK_UNIV"),
        (":-",  "TK_CUELLO"),
        ("?-",  "TK_CONSULTA"),
        ("==",  "TK_IDENTICO"),
        ("\\=", "TK_NO_UNIFICABLE"),
        ("=<",  "TK_MENOR_IGUAL"),
        (">=",  "TK_MAYOR_IGUAL"),
        ("//",  "TK_DIV_ENTERA"),
        ("**",  "TK_POTENCIA"),
        ("\\+", "TK_NEGACION"),
        ("(",   "TK_PAR_IZQ"),
        (")",   "TK_PAR_DER"),
        ("[",   "TK_COR_IZQ"),
        ("]",   "TK_COR_DER"),
        ("{",   "TK_LLA_IZQ"),
        ("}",   "TK_LLA_DER"),
        ("|",   "TK_BARRA"),
        (",",   "TK_COMA"),
        (";",   "TK_PUNTO_COMA"),
        ("!",   "TK_CORTE"),
        ("+",   "TK_MAS"),
        ("-",   "TK_MENOS"),
        ("*",   "TK_MULT"),
        ("/",   "TK_DIV"),
        ("=",   "TK_UNIFICACION"),
        ("<",   "TK_MENOR"),
        (">",   "TK_MAYOR")
    ]

    PALABRAS_RESERVADAS = {
        "is": "TK_IS",
        "mod": "TK_MOD"
    }

    def __init__(self, fuente: str):
        self.fuente = fuente
        self.longitud = len(fuente)
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.tokens: List[Token] = []
        self.errores: List[ErrorLexico] = []
        self.tabla = TablaLexemas()

    def _mirar(self, desplazamiento: int = 0) -> Optional[str]:
        idx = self.pos + desplazamiento
        return self.fuente[idx] if idx < self.longitud else None

    def _avanzar(self) -> Optional[str]:
        if self.pos >= self.longitud:
            return None
        c = self.fuente[self.pos]
        self.pos += 1
        if c == '\n':
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1
        return c

    def analizar(self) -> Tuple[List[Token], List[ErrorLexico]]:
        while self.pos < self.longitud:
            c = self._mirar()

            # 1. Espacios en blanco, tabulaciones y saltos de línea
            if c.isspace():
                self._avanzar()
                continue

            l_act, c_act = self.linea, self.columna

            # 2. Comentario de línea (%...)
            if c == '%':
                while self._mirar() is not None and self._mirar() != '\n':
                    self._avanzar()
                continue

            # 3. Comentario de bloque (/*...*/)
            if c == '/' and self._mirar(1) == '*':
                self._avanzar(); self._avanzar()
                cerrado = False
                while self._mirar() is not None:
                    if self._mirar() == '*' and self._mirar(1) == '/':
                        self._avanzar(); self._avanzar()
                        cerrado = True
                        break
                    self._avanzar()
                if not cerrado:
                    self.errores.append(ErrorLexico("Comentario de bloque sin cierre", "/*...", l_act, c_act))
                continue

            # 4. Cadenas de texto con comillas dobles ("...")
            if c == '"':
                tok = self._procesar_cadena(l_act, c_act)
                if tok:
                    self.tokens.append(tok)
                continue

            # 5. Átomos entre comillas simples ('...')
            if c == "'":
                tok = self._procesar_atomo_comillas(l_act, c_act)
                if tok:
                    self.tokens.append(tok)
                continue

            # 6. Números enteros y reales
            if c.isdigit():
                tok = self._procesar_numero(l_act, c_act)
                if tok:
                    self.tokens.append(tok)
                continue

            # 7. Identificadores (Átomos regulares, variables o variable anónima)
            if c.isalpha() or c == '_':
                tok = self._procesar_identificador(l_act, c_act)
                self.tokens.append(tok)
                continue

            # 8. Punto de fin de cláusula (.)
            if c == '.':
                sig = self._mirar(1)
                # En Prolog el punto termina la cláusula si va seguido de espacio, comentario o fin de archivo
                if sig is None or sig.isspace() or sig == '%':
                    self._avanzar()
                    self.tokens.append(Token("TK_PUNTO", ".", l_act, c_act))
                    continue

            # 9. Operadores y delimitadores
            if self._procesar_operador(l_act, c_act):
                continue

            # 10. Carácter no admitido / Error de símbolo inválido
            invalido = self._avanzar()
            self.errores.append(ErrorLexico("Carácter no reconocido", invalido, l_act, c_act))

        return self.tokens, self.errores

    def _procesar_cadena(self, l_act: int, c_act: int) -> Optional[Token]:
        self._avanzar()  # Consume comilla inicial
        buffer = []
        cerrado = False
        while self._mirar() is not None:
            char = self._mirar()
            if char == '\n':
                break  # Cadenas no cruzan líneas directamente
            if char == '\\':
                self._avanzar()
                sig = self._avanzar()
                buffer.append('\\' + (sig if sig else ''))
                continue
            if char == '"':
                self._avanzar()
                cerrado = True
                break
            buffer.append(self._avanzar())

        lexema = '"' + "".join(buffer) + ('"' if cerrado else '')
        if not cerrado:
            self.errores.append(ErrorLexico("Cadena de texto sin cierre", lexema, l_act, c_act))
            return None
        idx = self.tabla.registrar("CADENA", lexema)
        return Token("TK_CADENA", lexema, l_act, c_act, atributo=idx)

    def _procesar_atomo_comillas(self, l_act: int, c_act: int) -> Optional[Token]:
        self._avanzar()  # Consume comilla inicial
        buffer = []
        cerrado = False
        while self._mirar() is not None:
            char = self._mirar()
            if char == '\n':
                break
            if char == '\\':
                self._avanzar()
                sig = self._avanzar()
                buffer.append('\\' + (sig if sig else ''))
                continue
            if char == "'":
                self._avanzar()
                cerrado = True
                break
            buffer.append(self._avanzar())

        lexema = "'" + "".join(buffer) + ("'" if cerrado else '')
        if not cerrado:
            self.errores.append(ErrorLexico("Átomo entrecomillado sin cierre", lexema, l_act, c_act))
            return None
        idx = self.tabla.registrar("ATOMO", lexema)
        return Token("TK_ATOMO", lexema, l_act, c_act, atributo=idx)

    def _procesar_numero(self, l_act: int, c_act: int) -> Optional[Token]:
        digitos = []
        while self._mirar() is not None and self._mirar().isdigit():
            digitos.append(self._avanzar())

        # Si viene un punto seguido de otro dígito, es un número real
        if self._mirar() == '.' and (self._mirar(1) is not None and self._mirar(1).isdigit()):
            digitos.append(self._avanzar())  # Consume el '.'
            while self._mirar() is not None and self._mirar().isdigit():
                digitos.append(self._avanzar())

            # Exponente opcional (e.g. 1.2e+3)
            if self._mirar() in ['e', 'E']:
                digitos.append(self._avanzar())
                if self._mirar() in ['+', '-']:
                    digitos.append(self._avanzar())
                if not (self._mirar() and self._mirar().isdigit()):
                    erroneo = "".join(digitos)
                    self.errores.append(ErrorLexico("Número real con exponente mal formado", erroneo, l_act, c_act))
                    return None
                while self._mirar() is not None and self._mirar().isdigit():
                    digitos.append(self._avanzar())

            lexema = "".join(digitos)
            idx = self.tabla.registrar("LIT_REAL", lexema)
            return Token("TK_REAL", lexema, l_act, c_act, atributo=idx)

        lexema = "".join(digitos)
        idx = self.tabla.registrar("LIT_ENTERO", lexema)
        return Token("TK_ENTERO", lexema, l_act, c_act, atributo=idx)

    def _procesar_identificador(self, l_act: int, c_act: int) -> Token:
        buffer = []
        while self._mirar() is not None and (self._mirar().isalnum() or self._mirar() == '_'):
            buffer.append(self._avanzar())
        lexema = "".join(buffer)

        # Variable anónima solitaria
        if lexema == "_":
            return Token("TK_VAR_ANONIMA", lexema, l_act, c_act)

        # Palabras reservadas (is, mod)
        if lexema in self.PALABRAS_RESERVADAS:
            return Token(self.PALABRAS_RESERVADAS[lexema], lexema, l_act, c_act)

        # Variables inician con Mayúscula o _ seguido de caracteres
        if lexema[0].isupper() or lexema[0] == '_':
            idx = self.tabla.registrar("VARIABLE", lexema)
            return Token("TK_VARIABLE", lexema, l_act, c_act, atributo=idx)
        else:
            idx = self.tabla.registrar("ATOMO", lexema)
            return Token("TK_ATOMO", lexema, l_act, c_act, atributo=idx)

    def _procesar_operador(self, l_act: int, c_act: int) -> bool:
        for op, tok_tipo in self.OPERADORES:
            tam = len(op)
            if self.fuente[self.pos : self.pos + tam] == op:
                for _ in range(tam):
                    self._avanzar()
                self.tokens.append(Token(tok_tipo, op, l_act, c_act))
                return True
        return False