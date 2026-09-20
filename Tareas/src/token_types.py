from typing import Any, Dict, List, Optional

class Token:
    def __init__(self, tipo: str, lexema: str, linea: int, columna: int, atributo: Optional[Any] = None):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.atributo = atributo

    def __repr__(self) -> str:
        # Formato exacto pedido en la pauta: <TIPO, 'lexema', linea, columna>
        return f"<{self.tipo}, '{self.lexema}', {self.linea}, {self.columna}>"


class ErrorLexico:
    def __init__(self, mensaje: str, fragmento: str, linea: int, columna: int):
        self.mensaje = mensaje
        self.fragmento = fragmento
        self.linea = linea
        self.columna = columna

    def __repr__(self) -> str:
        return f"[ERROR LÉXICO] L:{self.linea} C:{self.columna} -> {self.mensaje}: '{self.fragmento}'"


class TablaLexemas:
    """
    Almacena átomos, variables y literales sin duplicados redundantes,
    asignando un índice único como atributo.
    """
    def __init__(self):
        self._entradas: Dict[str, int] = {}
        self._registros: List[Dict[str, Any]] = []

    def registrar(self, categoria: str, lexema: str) -> int:
        clave = f"{categoria}:{lexema}"
        if clave not in self._entradas:
            nuevo_id = len(self._registros) + 1
            self._entradas[clave] = nuevo_id
            self._registros.append({
                "id": nuevo_id,
                "categoria": categoria,
                "lexema": lexema
            })
            return nuevo_id
        return self._entradas[clave]

    def listar(self) -> List[Dict[str, Any]]:
        return self._registros