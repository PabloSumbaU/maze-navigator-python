import random
from collections import deque
from nodo import Nodo


class Laberinto:
    """
    Laberinto bidimensional representado como un grafo de Nodos.

    Genera aleatoriamente obstáculos dentro de una cuadrícula de (filas x columnas).
    El punto de inicio es siempre la esquina superior-izquierda (0, 0) y la meta
    la esquina inferior-derecha (filas-1, columnas-1). Los nodos libres adyacentes
    quedan conectados mediante objetos Arista con costo 1.

    Attributes:
        filas        (int)           : Número de filas de la cuadrícula.
        columnas     (int)           : Número de columnas de la cuadrícula.
        densidad     (float)         : Probabilidad de que una celda sea obstáculo.
        semilla      (int|None)      : Semilla para reproducibilidad.
        grid         (list[list])    : Matriz de Nodo|None (None = obstáculo).
        obstaculos   (set[tuple])    : Conjunto de posiciones (fila, col) obstaculizadas.
        nodo_inicio  (Nodo)          : Nodo en la posición (0, 0).
        nodo_meta    (Nodo)          : Nodo en la posición (filas-1, columnas-1).
        total_nodos  (int)           : Número de celdas libres (nodos en el grafo).
    """

    # Desplazamientos para los 4 movimientos cardinales: ↑ ↓ ← →
    _DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(
        self,
        filas: int,
        columnas: int,
        densidad_obstaculos: float = 0.28,
        semilla: int | None = None,
    ):
        """
        Inicializa y genera el laberinto.

        Args:
            filas               (int)  : Filas de la cuadrícula.
            columnas            (int)  : Columnas de la cuadrícula.
            densidad_obstaculos (float): Fracción de celdas que serán obstáculos [0, 1).
            semilla             (int)  : Semilla aleatoria opcional para reproducibilidad.
        """
        if not (0.0 <= densidad_obstaculos < 1.0):
            raise ValueError("densidad_obstaculos debe estar en [0, 1).")

        self.filas       = filas
        self.columnas    = columnas
        self.densidad    = densidad_obstaculos
        self.semilla     = semilla
        self.grid: list[list[Nodo | None]] = []
        self.obstaculos: set[tuple[int, int]] = set()
        self.nodo_inicio: Nodo | None = None
        self.nodo_meta:   Nodo | None = None
        self.total_nodos: int = 0

        self._generar()

    # ------------------------------------------------------------------
    # Construcción del laberinto
    # ------------------------------------------------------------------

    def _generar(self) -> None:
        """Genera el laberinto: coloca obstáculos y conecta los nodos."""
        if self.semilla is not None:
            random.seed(self.semilla)

        # Crear la cuadrícula inicialmente vacía
        self.grid = [[None] * self.columnas for _ in range(self.filas)]

        # Asignar obstáculos y crear nodos en celdas libres
        for f in range(self.filas):
            for c in range(self.columnas):
                # Si el número aleatorio generado es menor que la densidad
                # la celda es un obstáculo, si es False es un nodo libre
                if random.random() < self.densidad:
                    self.obstaculos.add((f, c))
                else:
                    self.grid[f][c] = Nodo(f, c)

        # Garantizar que inicio y meta estén libres
        for pos in [(0, 0), (self.filas - 1, self.columnas - 1)]:
            self.obstaculos.discard(pos)
            f, c = pos
            if self.grid[f][c] is None:
                self.grid[f][c] = Nodo(f, c)

        self.nodo_inicio = self.grid[0][0]
        self.nodo_meta   = self.grid[self.filas - 1][self.columnas - 1]

        # Conectar nodos adyacentes (construir el grafo)
        # Cada nodo se conecta a sus vecinos libres (arriba, abajo, izquierda, derecha)
        self.total_nodos = 0
        for f in range(self.filas):
            for c in range(self.columnas):
                nodo = self.grid[f][c]
                if nodo is None:
                    continue
                self.total_nodos += 1
                for df, dc in self._DIRECCIONES: # Buscar vecinos en las 4 direcciones
                    nf, nc = f + df, c + dc # Posición del vecino
                    if (
                        0 <= nf < self.filas # No se sale por arriba o abajo
                        and 0 <= nc < self.columnas # No se sale por izquierda o derecha
                        and self.grid[nf][nc] is not None # Solo conecta con nodos libres
                    ):
                        nodo.conectar_nodo(self.grid[nf][nc], peso=1)

    # ------------------------------------------------------------------
    # Utilidades de consulta
    # ------------------------------------------------------------------

    def tiene_solucion(self) -> bool:
        """
        Verifica si existe al menos un camino desde inicio hasta meta
        mediante una BFS interna rápida.

        """
        if self.nodo_inicio is None or self.nodo_meta is None:
            return False
        visitados = {self.nodo_inicio}
        cola = deque([self.nodo_inicio])
        while cola:
            actual = cola.popleft()
            if actual == self.nodo_meta:
                return True
            for arista in actual.vecinos:
                v = arista.destino
                if v not in visitados:
                    visitados.add(v)
                    cola.append(v)
        return False

    # ------------------------------------------------------------------
    # Representación textual del objeto
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Laberinto({self.filas}x{self.columnas}, "
            f"obstáculos={len(self.obstaculos)}, "
            f"nodos_libres={self.total_nodos})"
        )
