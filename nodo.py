from arista import Arista


class Nodo:
    """
    Representa una celda en el laberinto bidimensional.

    Cada nodo actúa como un vértice en el grafo del laberinto.
    Sus conexiones (aristas) apuntan a las celdas adyacentes que no son
    obstáculos (movimientos: arriba, abajo, izquierda, derecha).

    Attributes:
        fila    (int)       : Índice de fila en la cuadrícula (0-based).
        columna (int)       : Índice de columna en la cuadrícula (0-based).
        nombre  (str)       : Identificador textual "(fila,columna)".
        vecinos (list[Arista]): Conexiones hacia celdas adyacentes libres.
    """

    def __init__(self, fila: int, columna: int):
        self.fila    = fila
        self.columna = columna
        self.nombre  = f"({fila},{columna})"
        self.vecinos: list[Arista] = []  # Lista de objetos Arista

    # ------------------------------------------------------------------
    # Métodos de construcción del grafo
    # ------------------------------------------------------------------

    def conectar_nodo(self, nodo_destino: "Nodo", peso: int = 1) -> None:
        """
        Crea una arista desde este nodo hacia nodo_destino y la registra.

        Args:
            nodo_destino (Nodo): Nodo vecino al que se conecta.
            peso         (int) : Costo del movimiento (por defecto 1).
        """
        nueva_conexion = Arista(nodo_destino, peso)
        self.vecinos.append(nueva_conexion)

    # ------------------------------------------------------------------
    # Métodos especiales para uso en conjuntos y diccionarios
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Nodo):
            return self.fila == other.fila and self.columna == other.columna
        return False

    def __hash__(self) -> int:
        # Necesario para usar Nodos en sets y como claves de dict
        return hash((self.fila, self.columna))

    def __lt__(self, other: "Nodo") -> bool:
        # Necesario para comparaciones en heapq (A*)
        return (self.fila, self.columna) < (other.fila, other.columna)

    def __repr__(self) -> str:
        return f"Nodo({self.nombre})"
