class Arista:
    """
    Representa una conexión dirigida entre dos nodos con un peso asociado.

    En el contexto del laberinto, cada arista conecta una celda con una celda
    adyacente (arriba, abajo, izquierda, derecha). El costo de cada paso es 1.

    Attributes:
        destino (Nodo): Nodo al que apunta esta arista.
        peso   (int) : Costo del movimiento (por defecto 1).
    """

    def __init__(self, nodo_destino, peso: int = 1):
        self.destino = nodo_destino
        self.valor   = peso

    def __repr__(self) -> str:
        return f"Arista(-> {self.destino.nombre}, peso={self.valor})"
