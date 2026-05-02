"""
Implementa los algoritmos de búsqueda en el laberinto: BFS, DFS, A* (Manhattan) y A* (Euclidiana).
"""

import time
import heapq
import math
from collections import deque

from nodo import Nodo
from laberinto import Laberinto


# ══════════════════════════════════════════════════════════════════════════════
# Clase de resultado
# ══════════════════════════════════════════════════════════════════════════════

class ResultadoBusqueda:
    """
    Datos producidos por una búsqueda:
        algoritmo        (str)       : Nombre del algoritmo empleado.
        camino           (list[Nodo]): Secuencia de nodos desde inicio hasta meta.
        explorados       (list[Nodo]): Nodos expandidos en orden cronológico.
        max_frontera     (int)       : Tamaño pico de la estructura de frontera.
        nodos_explorados (int)       : Total de nodos extraídos/expandidos.
        tiempo           (float)     : Tiempo de ejecución en segundos.
        longitud         (int)       : Número de pasos del camino (aristas recorridas).
        encontrado       (bool)      : True si se halló camino hasta la meta.
    """

    def __init__(
        self,
        algoritmo: str,
        camino: list[Nodo],
        explorados: list[Nodo],
        max_frontera: int,
        tiempo: float,
    ):
        self.algoritmo        = algoritmo
        self.camino           = camino
        self.explorados       = explorados
        self.max_frontera     = max_frontera
        self.nodos_explorados = len(explorados)
        self.tiempo           = tiempo
        self.longitud         = len(camino) - 1 if camino else 0
        self.encontrado       = bool(camino)

    def resumen(self) -> str:
        """Devuelve un resumen de los resultados."""
        estado = "ENCONTRADO" if self.encontrado else "NO ENCONTRADO"
        return (
            f"\n  ╔═══ {self.algoritmo} ═══╗\n"
            f"  ║ Estado          : {estado}\n"
            f"  ║ Longitud camino : {self.longitud} pasos\n"
            f"  ║ Nodos explorados: {self.nodos_explorados}\n"
            f"  ║ Frontera máxima : {self.max_frontera} nodos\n"
            f"  ║ Tiempo          : {self.tiempo * 1_000:.4f} ms\n"
            f"  ╚{'═' * (len(self.algoritmo) + 8)}"
        )

    def __repr__(self) -> str:
        return (
            f"ResultadoBusqueda(alg={self.algoritmo!r}, "
            f"longitud={self.longitud}, "
            f"explorados={self.nodos_explorados}, "
            f"tiempo={self.tiempo:.6f}s)"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Clase base abstracta
# ══════════════════════════════════════════════════════════════════════════════

class BuscadorBase:
    """
    Clase base para todos los algoritmos de búsqueda de caminos.
    Interfaz común (buscar) y el método de reconstrucción del camino
    a partir del diccionario de padres generado durante la búsqueda.
    """

    def __init__(self, laberinto: Laberinto):
        self.laberinto = laberinto

    def _reconstruir_camino(
        self, padres: dict[Nodo, Nodo | None], nodo_meta: Nodo
    ) -> list[Nodo]:
        """
        Reconstruye el camino óptimo desde el inicio hasta la meta
        recorriendo el diccionario de padres en sentido inverso.
        """
        camino: list[Nodo] = []
        actual: Nodo | None = nodo_meta
        while actual is not None:
            camino.append(actual)
            actual = padres.get(actual)
        camino.reverse()
        return camino

    def buscar(self) -> ResultadoBusqueda:
        """
        Ejecuta el algoritmo de búsqueda.
        Devuelve un objeto con todos los datos del resultado.
        """
        raise NotImplementedError("Las subclases deben implementar buscar().")


# ══════════════════════════════════════════════════════════════════════════════
# BFS — Búsqueda en Anchura (Breadth-First Search)
# ══════════════════════════════════════════════════════════════════════════════

class BuscadorBFS(BuscadorBase):
    """
    Búsqueda en Amplitud (BFS).
    Utiliza una cola FIFO (deque) como frontera.
    """

    NOMBRE = "BFS (Amplitud)"

    def buscar(self) -> ResultadoBusqueda:
        """
        Ejecuta BFS desde nodo_inicio hasta nodo_meta.
        """
        inicio = self.laberinto.nodo_inicio
        meta   = self.laberinto.nodo_meta

        # Frontera: cola FIFO
        cola: deque[Nodo] = deque([inicio])

        visitados: set[Nodo]            = {inicio}
        padres:    dict[Nodo, Nodo | None] = {inicio: None}
        explorados: list[Nodo]          = []
        max_frontera: int               = 1

        t_inicio = time.perf_counter()

        while cola:
            max_frontera = max(max_frontera, len(cola))
            nodo_actual  = cola.popleft()          # Extracción FIFO
            explorados.append(nodo_actual)

            # Condición de termino
            if nodo_actual == meta:
                t_fin  = time.perf_counter()
                camino = self._reconstruir_camino(padres, meta)
                return ResultadoBusqueda(
                    self.NOMBRE, camino, explorados, max_frontera, t_fin - t_inicio
                )

            # Expansión de vecinos
            for arista in nodo_actual.vecinos:
                vecino = arista.destino
                if vecino not in visitados:
                    visitados.add(vecino)
                    padres[vecino] = nodo_actual
                    cola.append(vecino)

        t_fin = time.perf_counter()
        return ResultadoBusqueda(
            self.NOMBRE, [], explorados, max_frontera, t_fin - t_inicio
        )


# ══════════════════════════════════════════════════════════════════════════════
# DFS — Búsqueda en Profundidad (Depth-First Search)
# ══════════════════════════════════════════════════════════════════════════════

class BuscadorDFS(BuscadorBase):
    """
    Búsqueda en Profundidad (DFS).
    Utiliza una pila LIFO como frontera.
    """

    NOMBRE = "DFS (Profundidad)"

    def buscar(self) -> ResultadoBusqueda:
        """
        Ejecuta DFS desde nodo_inicio hasta nodo_meta.
        """
        inicio = self.laberinto.nodo_inicio
        meta   = self.laberinto.nodo_meta

        # Frontera: pila LIFO
        pila: list[Nodo] = [inicio]

        visitados: set[Nodo]               = {inicio}
        padres:    dict[Nodo, Nodo | None] = {inicio: None}
        explorados: list[Nodo]             = []
        max_frontera: int                  = 1

        t_inicio = time.perf_counter()

        while pila:
            max_frontera = max(max_frontera, len(pila))
            nodo_actual  = pila.pop()              # Extracción LIFO
            explorados.append(nodo_actual)

            # Condición de éxito
            if nodo_actual == meta:
                t_fin  = time.perf_counter()
                camino = self._reconstruir_camino(padres, meta)
                return ResultadoBusqueda(
                    self.NOMBRE, camino, explorados, max_frontera, t_fin - t_inicio
                )

            # Expansión de vecinos (en orden inverso para explorar igual que BFS)
            for arista in reversed(nodo_actual.vecinos):
                vecino = arista.destino
                if vecino not in visitados:
                    visitados.add(vecino)
                    padres[vecino] = nodo_actual
                    pila.append(vecino)

        t_fin = time.perf_counter()
        return ResultadoBusqueda(
            self.NOMBRE, [], explorados, max_frontera, t_fin - t_inicio
        )


# ══════════════════════════════════════════════════════════════════════════════
# A* — Búsqueda Heurística Informada
# ══════════════════════════════════════════════════════════════════════════════

class BuscadorAEstrella(BuscadorBase):
    """
    Búsqueda A* con heurística configurable.

    A* combina el costo acumulado g(n) desde el inicio con una estimación
    h(n) del costo restante hasta la meta:  f(n) = g(n) + h(n).
    Utiliza un heap mínimo (cola de prioridad) como frontera.
    """

    HEURISTICA_MANHATTAN  = "Manhattan"
    HEURISTICA_EUCLIDIANA = "Euclidiana"

    def __init__(self, laberinto: Laberinto, heuristica: str = HEURISTICA_MANHATTAN):
        """
        Args:
            laberinto  (Laberinto): Laberinto a explorar.
            heuristica (str)      : Tipo de heurística:
                                    'Manhattan' (por defecto) o 'Euclidiana'.
        """
        super().__init__(laberinto)
        if heuristica not in (self.HEURISTICA_MANHATTAN, self.HEURISTICA_EUCLIDIANA):
            raise ValueError(
                f"Heurística desconocida: {heuristica!r}. "
                f"Use {self.HEURISTICA_MANHATTAN!r} o {self.HEURISTICA_EUCLIDIANA!r}."
            )
        self.heuristica = heuristica

    # ------------------------------------------------------------------
    # Heurísticas
    # ------------------------------------------------------------------

    def _h_manhattan(self, nodo: Nodo) -> int:
        """
        Heurística de distancia Manhattan: |Δfila| + |Δcolumna|.

        Adecuada para grillas con movimientos cardinales (no diagonales).
        Es consistente: nunca sobreestima el costo real del movimiento.

        Returns:
            int: Estimación entera del costo restante.
        """
        meta = self.laberinto.nodo_meta
        return abs(nodo.fila - meta.fila) + abs(nodo.columna - meta.columna)

    def _h_euclidiana(self, nodo: Nodo) -> float:
        """
        Heurística de distancia Euclidiana: √(Δfila² + Δcolumna²).

        Es admisible (nunca sobreestima) pero puede subestimar en exceso
        porque el camino real sigue solo pasos ortogonales.
        Esto provoca que A* explore más nodos innecesarios que con Manhattan.

        Returns:
            float: Estimación de punto flotante del costo restante.
        """
        meta = self.laberinto.nodo_meta
        df   = nodo.fila    - meta.fila
        dc   = nodo.columna - meta.columna
        return math.sqrt(df * df + dc * dc)

    def _calcular_h(self, nodo: Nodo) -> float:
        """Despacha al método de heurística seleccionado."""
        if self.heuristica == self.HEURISTICA_MANHATTAN:
            return self._h_manhattan(nodo)
        return self._h_euclidiana(nodo)

    # ------------------------------------------------------------------
    # Búsqueda principal
    # ------------------------------------------------------------------

    def buscar(self) -> ResultadoBusqueda:
        """
        Ejecuta A* desde nodo_inicio hasta nodo_meta.
        """
        inicio = self.laberinto.nodo_inicio
        meta   = self.laberinto.nodo_meta
        nombre = f"A* ({self.heuristica})"

        # — Frontera: min-heap  (f_score, contador_unico, nodo) —
        # El contador evita comparar Nodos directamente cuando f_scores son iguales.
        contador: int = 0
        heap: list[tuple] = [(self._calcular_h(inicio), contador, inicio)]

        g_scores: dict[Nodo, float]            = {inicio: 0.0}
        padres:   dict[Nodo, Nodo | None]       = {inicio: None}
        cerrados: set[Nodo]                     = set()   # nodos ya expandidos
        explorados: list[Nodo]                  = []
        max_frontera: int                       = 1

        t_inicio = time.perf_counter()

        while heap:
            max_frontera = max(max_frontera, len(heap))
            f, _, nodo_actual = heapq.heappop(heap)

            # Ignorar entradas obsoletas del heap (lazy deletion)
            if nodo_actual in cerrados:
                continue

            cerrados.add(nodo_actual)
            explorados.append(nodo_actual)

            # Condición de éxito
            if nodo_actual == meta:
                t_fin  = time.perf_counter()
                camino = self._reconstruir_camino(padres, meta)
                return ResultadoBusqueda(
                    nombre, camino, explorados, max_frontera, t_fin - t_inicio
                )

            # Expansión de vecinos
            for arista in nodo_actual.vecinos:
                vecino = arista.destino
                if vecino in cerrados:
                    continue

                nuevo_g = g_scores[nodo_actual] + arista.valor

                if vecino not in g_scores or nuevo_g < g_scores[vecino]:
                    g_scores[vecino] = nuevo_g
                    padres[vecino]   = nodo_actual
                    f_score          = nuevo_g + self._calcular_h(vecino)
                    contador        += 1
                    heapq.heappush(heap, (f_score, contador, vecino))

        t_fin = time.perf_counter()
        return ResultadoBusqueda(
            nombre, [], explorados, max_frontera, t_fin - t_inicio
        )
