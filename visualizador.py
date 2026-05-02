"""
Genera visualizaciones gráficas del laberinto y análisis
comparativos de los algoritmos usando matplotlib.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation

from matplotlib.colors import LinearSegmentedColormap

from laberinto import Laberinto
from buscadores import ResultadoBusqueda


# ══════════════════════════════════════════════════════════════════════════════
# Paleta de colores
# ══════════════════════════════════════════════════════════════════════════════

_PALETA = {
    "fondo"           : "#0D1117",   # Fondo oscuro
    "libre"           : "#1C2333",   # Celda libre
    "obstaculo"       : "#0D1117",   # Obstáculo = fondo (invisible)
    "inicio"          : "#3FB950",   # Verde
    "meta"            : "#F85149",   # Rojo
    "bfs"             : "#58A6FF",   # Azul claro
    "dfs"             : "#D29922",   # Amarillo ámbar
    "astar_manhattan" : "#BC8CFF",   # Violeta
    "astar_euclidiana": "#FF7B72",   # Salmón
    "explorado_alpha" : 0.35,
    "texto"           : "#C9D1D9",
    "subtexto"        : "#8B949E",
    "borde"           : "#30363D",
}

# Asignación algoritmo → color de ruta
_COLOR_RUTA: dict[str, str] = {
    "BFS (Anchura)"    : _PALETA["bfs"],
    "DFS (Profundidad)": _PALETA["dfs"],
    "A* (Manhattan)"   : _PALETA["astar_manhattan"],
    "A* (Euclidiana)"  : _PALETA["astar_euclidiana"],
}


def _configurar_estilo() -> None:
    """Aplica el estilo visual oscuro global a matplotlib."""
    plt.rcParams.update({
        "figure.facecolor"  : _PALETA["fondo"],
        "axes.facecolor"    : _PALETA["fondo"],
        "axes.edgecolor"    : _PALETA["borde"],
        "axes.labelcolor"   : _PALETA["texto"],
        "xtick.color"       : _PALETA["subtexto"],
        "ytick.color"       : _PALETA["subtexto"],
        "text.color"        : _PALETA["texto"],
        "legend.facecolor"  : "#161B22",
        "legend.edgecolor"  : _PALETA["borde"],
        "grid.color"        : _PALETA["borde"],
        "grid.linestyle"    : "--",
        "grid.alpha"        : 0.5,
        "font.family"       : "monospace",
    })


def _rgb(hex_color: str) -> tuple[float, float, float]:
    """Convierte un color hexadecimal a tupla RGB normalizada [0, 1]."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


# ══════════════════════════════════════════════════════════════════════════════
# Clase principal de visualización
# ══════════════════════════════════════════════════════════════════════════════

class Visualizador:
    """
    Genera y guarda visualizaciones del laberinto y métricas comparativas.

    Métodos principales:
        - mostrar_laberinto_con_caminos : Cuatro paneles, uno por algoritmo.
        - mostrar_comparativa           : Gráfica de tiempo y frontera vs tamaño.
        - mostrar_tabla_resumen         : Tabla detallada de resultados.
    """

    @staticmethod
    def mostrar_laberinto_con_caminos(
        laberinto: Laberinto,
        resultados: list[ResultadoBusqueda],
        titulo: str = "Laberinto",
        guardar_como: str | None = None,
        mostrar: bool = True,
    ) -> None:
        """
        Dibuja el laberinto cuatro veces, una por algoritmo, resaltando
        los nodos explorados y el camino solución de cada uno.

        Args:
            laberinto   (Laberinto)           : Laberinto a dibujar.
            resultados  (list[ResultadoBusqueda]): Resultados de los 4 algoritmos.
            titulo      (str)                 : Título superior de la figura.
            guardar_como(str|None)            : Ruta de archivo para guardar la imagen.
            mostrar     (bool)                : Si True, llama a plt.show().
        """
        _configurar_estilo()

        filas, cols = laberinto.filas, laberinto.columnas
        n = len(resultados)

        fig, axes = plt.subplots(1, n, figsize=(5.5 * n, 6))
        if n == 1:
            axes = [axes]

        fig.patch.set_facecolor(_PALETA["fondo"])

        for ax, resultado in zip(axes, resultados):
            nombre_alg = resultado.algoritmo
            color_ruta = _COLOR_RUTA.get(nombre_alg, "#FFFFFF")
            explorados_set = set(resultado.explorados)
            camino_set     = set(resultado.camino)

            # — Construir imagen RGB —
            img = np.zeros((filas, cols, 3), dtype=float)

            # Celdas libres (fondo suave)
            libre_rgb = _rgb(_PALETA["libre"])
            for f in range(filas):
                for c in range(cols):
                    if laberinto.grid[f][c] is not None:
                        img[f, c] = libre_rgb

            # Obstáculos (color de fondo → invisibles)
            obst_rgb = _rgb(_PALETA["obstaculo"])
            for f, c in laberinto.obstaculos:
                img[f, c] = obst_rgb

            # Nodos explorados (versión atenuada del color de ruta)
            exp_rgb = _rgb(color_ruta)
            factor  = 0.22  # Intensidad del explorado
            for nodo in resultado.explorados:
                if nodo not in camino_set:
                    img[nodo.fila, nodo.columna] = (
                        img[nodo.fila, nodo.columna] * (1 - factor)
                        + np.array(exp_rgb) * factor
                    )

            # Camino solución
            ruta_rgb = _rgb(color_ruta)
            for nodo in resultado.camino:
                img[nodo.fila, nodo.columna] = ruta_rgb

            # Inicio (A) y Meta (B)
            img[0, 0]                             = _rgb(_PALETA["inicio"])
            img[filas - 1, cols - 1]              = _rgb(_PALETA["meta"])

            # — Dibujar —
            ax.imshow(img, interpolation="nearest", aspect="equal")
            ax.set_xticks([])
            ax.set_yticks([])

            # Etiquetas A y B (solo visibles en laberintos pequeños)
            font_s = max(4, min(10, 80 // max(filas, cols)))
            ax.text(
                0, 0, "A", ha="center", va="center",
                fontsize=font_s, fontweight="bold", color="white",
            )
            ax.text(
                cols - 1, filas - 1, "B", ha="center", va="center",
                fontsize=font_s, fontweight="bold", color="white",
            )

            # Título del panel
            estado_str = "✓" if resultado.encontrado else "✗"
            ax.set_title(
                f"{estado_str} {nombre_alg}\n"
                f"Pasos: {resultado.longitud}  |  Explorados: {resultado.nodos_explorados}\n"
                f"Frontera: {resultado.max_frontera}  |  {resultado.tiempo * 1_000:.2f} ms",
                fontsize=8,
                color=_PALETA["texto"],
                pad=6,
            )

            # Marco de color por algoritmo
            for spine in ax.spines.values():
                spine.set_edgecolor(color_ruta)
                spine.set_linewidth(2)

        # Leyenda de colores
        parches = [
            mpatches.Patch(color=_PALETA["inicio"],          label="Inicio (A)"),
            mpatches.Patch(color=_PALETA["meta"],            label="Meta (B)"),
            mpatches.Patch(color=_PALETA["bfs"],             label="BFS"),
            mpatches.Patch(color=_PALETA["dfs"],             label="DFS"),
            mpatches.Patch(color=_PALETA["astar_manhattan"], label="A* Manhattan"),
            mpatches.Patch(color=_PALETA["astar_euclidiana"],label="A* Euclidiana"),
        ]
        fig.legend(
            handles=parches,
            loc="lower center",
            ncol=6,
            fontsize=7,
            frameon=True,
            fancybox=True,
        )

        fig.suptitle(titulo, fontsize=13, fontweight="bold", color=_PALETA["texto"], y=1.01)
        plt.tight_layout(rect=[0, 0.04, 1, 1])

        if guardar_como:
            plt.savefig(guardar_como, dpi=160, bbox_inches="tight",
                        facecolor=_PALETA["fondo"])
            print(f"  → Imagen guardada: {guardar_como}")

        if mostrar:
            plt.show()
        plt.close()

    # ------------------------------------------------------------------

    @staticmethod
    def mostrar_comparativa(
        todos_resultados: dict[int, dict[str, ResultadoBusqueda]],
        tamanos: list[int],
        guardar_como: str | None = None,
        mostrar: bool = True,
    ) -> None:
        """
        Genera una figura con cuatro subgráficas comparativas:
          1. Tiempo de ejecución (ms) vs tamaño.
          2. Frontera máxima (nodos) vs tamaño.
          3. Nodos explorados vs tamaño.
          4. Longitud del camino vs tamaño.

        Args:
            todos_resultados (dict): {tamaño → {nombre_alg → ResultadoBusqueda}}.
            tamanos          (list): Lista ordenada de tamaños de laberinto.
            guardar_como     (str) : Ruta de archivo para guardar la imagen.
            mostrar          (bool): Si True, llama a plt.show().
        """
        _configurar_estilo()

        # Determinar el orden fijo de algoritmos
        nombres_fijos = [
            "BFS (Anchura)",
            "DFS (Profundidad)",
            "A* (Manhattan)",
            "A* (Euclidiana)",
        ]
        colores_fijos = [
            _PALETA["bfs"],
            _PALETA["dfs"],
            _PALETA["astar_manhattan"],
            _PALETA["astar_euclidiana"],
        ]
        marcadores = ["o", "s", "^", "D"]

        fig = plt.figure(figsize=(16, 10))
        fig.patch.set_facecolor(_PALETA["fondo"])
        gs = gridspec.GridSpec(2, 2, hspace=0.45, wspace=0.35)

        metricas = [
            ("tiempo",        "Tiempo de Ejecución (ms)",    "Tiempo (ms)",       True),
            ("max_frontera",  "Frontera Máxima (nodos)",      "Nodos en frontera", False),
            ("nodos_explorados", "Nodos Explorados",          "Nodos",             False),
            ("longitud",      "Longitud del Camino (pasos)",  "Pasos",             False),
        ]

        for idx, (metrica, titulo_sub, ylabel, es_tiempo) in enumerate(metricas):
            ax = fig.add_subplot(gs[idx // 2, idx % 2])

            for nombre, color, marcador in zip(nombres_fijos, colores_fijos, marcadores):
                valores = []
                for t in tamanos:
                    r = todos_resultados[t].get(nombre)
                    if r is not None:
                        v = r.tiempo * 1_000 if es_tiempo else getattr(r, metrica)
                        valores.append(v)
                    else:
                        valores.append(0)

                ax.plot(
                    tamanos, valores,
                    marker=marcador, label=nombre,
                    color=color, linewidth=2.2, markersize=7,
                )
                # Anotar valores sobre los puntos
                for x, y in zip(tamanos, valores):
                    ax.annotate(
                        f"{y:.1f}" if es_tiempo else f"{int(y):,}",
                        (x, y), textcoords="offset points",
                        xytext=(0, 7), ha="center",
                        fontsize=6.5, color=color,
                    )

            ax.set_title(titulo_sub, fontsize=11, fontweight="bold", color=_PALETA["texto"])
            ax.set_xlabel("Tamaño del laberinto (N×N)", fontsize=9, color=_PALETA["subtexto"])
            ax.set_ylabel(ylabel, fontsize=9, color=_PALETA["subtexto"])
            ax.set_xticks(tamanos)
            ax.set_xticklabels([f"{t}×{t}" for t in tamanos])
            ax.grid(True)
            ax.legend(fontsize=7)

        fig.suptitle(
            "Análisis Comparativo de Algoritmos de Búsqueda en Laberintos",
            fontsize=14, fontweight="bold", color=_PALETA["texto"],
        )

        if guardar_como:
            plt.savefig(guardar_como, dpi=160, bbox_inches="tight",
                        facecolor=_PALETA["fondo"])
            print(f"  → Gráfica comparativa guardada: {guardar_como}")

        if mostrar:
            plt.show()
        plt.close()

    # ------------------------------------------------------------------

    @staticmethod
    def mostrar_tabla_resumen(
        todos_resultados: dict[int, dict[str, ResultadoBusqueda]],
        tamanos: list[int],
    ) -> None:
        """
        Imprime en consola una tabla ASCII con las métricas de todos los
        algoritmos para cada tamaño de laberinto.

        Args:
            todos_resultados (dict): {tamaño → {nombre_alg → ResultadoBusqueda}}.
            tamanos          (list): Lista de tamaños evaluados.
        """
        nombres = [
            "BFS (Anchura)",
            "DFS (Profundidad)",
            "A* (Manhattan)",
            "A* (Euclidiana)",
        ]

        cabecera = (
            f"\n{'═'*80}\n"
            f"{'TABLA COMPARATIVA DE RESULTADOS':^80}\n"
            f"{'═'*80}"
        )
        print(cabecera)

        col_w = 16
        print(
            f"{'Algoritmo':<22}"
            f"{'Tamaño':>{col_w}}"
            f"{'Pasos':>{col_w}}"
            f"{'Explorados':>{col_w}}"
            f"{'Frontera':>{col_w}}"
            f"{'Tiempo(ms)':>{col_w}}"
        )
        print("─" * 90)

        for t in tamanos:
            for nombre in nombres:
                r = todos_resultados[t].get(nombre)
                if r is None:
                    continue
                print(
                    f"  {nombre:<20}"
                    f"{f'{t}×{t}':>{col_w}}"
                    f"{r.longitud:>{col_w},}"
                    f"{r.nodos_explorados:>{col_w},}"
                    f"{r.max_frontera:>{col_w},}"
                    f"{r.tiempo * 1_000:>{col_w}.3f}"
                )
            print("─" * 90)

        print("═" * 80)

    # Guardar animación GIF del proceso de búsqueda
    @staticmethod
    def guardar_animacion_gif(
        laberinto: Laberinto,
        resultado: ResultadoBusqueda,
        archivo_salida: str = "animacion.gif",
        nodos_por_frame: int = 5,
        fps: int = 30
    ) -> None:
        """
        Genera y guarda una animación GIF del proceso de búsqueda.

        Args:
            laberinto       (Laberinto)       : Laberinto a resolver.
            resultado       (ResultadoBusqueda): El resultado de un algoritmo.
            archivo_salida  (str)             : Nombre del archivo (.gif).
            nodos_por_frame (int)             : Velocidad de exploración (nodos pintados por cuadro).
            fps             (int)             : Cuadros por segundo del GIF.
        """
        _configurar_estilo()
        filas, cols = laberinto.filas, laberinto.columnas
        nombre_alg = resultado.algoritmo
        color_ruta = _COLOR_RUTA.get(nombre_alg, "#FFFFFF")

        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor(_PALETA["fondo"])

        # — 1. Construir la imagen base (fondo, obstáculos, inicio y meta) —
        img_array = np.zeros((filas, cols, 3), dtype=float)
        libre_rgb = _rgb(_PALETA["libre"])
        obst_rgb = _rgb(_PALETA["obstaculo"])
        
        for f in range(filas):
            for c in range(cols):
                img_array[f, c] = libre_rgb
                
        for f, c in laberinto.obstaculos:
            img_array[f, c] = obst_rgb

        img_array[0, 0] = _rgb(_PALETA["inicio"])
        img_array[filas - 1, cols - 1] = _rgb(_PALETA["meta"])

        # Dibujar la base
        im = ax.imshow(img_array, interpolation="nearest", aspect="equal", animated=True)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Estilo del marco
        for spine in ax.spines.values():
            spine.set_edgecolor(color_ruta)
            spine.set_linewidth(2)

        # Título dinámico
        titulo = ax.set_title(f"Iniciando {nombre_alg}...", color=_PALETA["texto"], fontsize=12)

        # — 2. Preparar los datos para la animación —
        exp_rgb = _rgb(color_ruta)
        factor = 0.22 # Intensidad de la "mancha" de exploración
        
        # Agrupamos los nodos explorados para que la animación no sea eterna
        frames_exploracion = [
            resultado.explorados[i : i + nodos_por_frame]
            for i in range(0, len(resultado.explorados), nodos_por_frame)
        ]
        
        total_frames = len(frames_exploracion) + len(resultado.camino) + 15 # +15 frames de pausa al final

        def init():
            return [im, titulo]

        def update(frame_idx):
            # Fase 1: Exploración
            if frame_idx < len(frames_exploracion):
                nodos = frames_exploracion[frame_idx]
                for nodo in nodos:
                    if (nodo.fila, nodo.columna) not in [(0, 0), (filas - 1, cols - 1)]:
                        actual = img_array[nodo.fila, nodo.columna]
                        # Mezclar color actual con la capa translúcida
                        img_array[nodo.fila, nodo.columna] = (
                            actual * (1 - factor) + np.array(exp_rgb) * factor
                        )
                titulo.set_text(f"Explorando: {nombre_alg}")
            
            # Fase 2: Trazar el camino óptimo encontrado
            elif frame_idx < len(frames_exploracion) + len(resultado.camino):
                idx_camino = frame_idx - len(frames_exploracion)
                nodo = resultado.camino[idx_camino]
                if (nodo.fila, nodo.columna) not in [(0, 0), (filas - 1, cols - 1)]:
                    img_array[nodo.fila, nodo.columna] = exp_rgb
                titulo.set_text(f"¡Ruta encontrada! ({resultado.longitud} pasos)")
            
            # Fase 3: Pausa final (el array ya no se modifica)
            else:
                titulo.set_text(f"¡Completado! ({resultado.longitud} pasos)")

            im.set_array(img_array)
            return [im, titulo]

        # — 3. Generar y guardar —
        print(f"Generando animación para {nombre_alg} ({total_frames} frames)... esto puede tomar unos segundos.")
        ani = animation.FuncAnimation(
            fig, update, frames=total_frames, init_func=init, blit=True, repeat=False
        )

        # Exportar a GIF
        ani.save(archivo_salida, writer='pillow', fps=fps)
        plt.close()
        print(f"  → Animación guardada con éxito: {archivo_salida}")
