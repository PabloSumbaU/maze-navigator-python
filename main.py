"""
Módulo: main.py
Descripción: Punto de entrada del programa. Genera laberintos de distintos
             tamaños, ejecuta los cuatro algoritmos de búsqueda en cada uno
             y produce las visualizaciones y tablas comparativas.
"""

import os
import sys

from laberinto  import Laberinto
from buscadores import BuscadorBFS, BuscadorDFS, BuscadorAEstrella, ResultadoBusqueda
from visualizador import Visualizador


# ══════════════════════════════════════════════════════════════════════════════
# Constantes de configuración
# ══════════════════════════════════════════════════════════════════════════════

TAMANOS            = [10, 50, 100]     # Tamaños de laberinto a evaluar
DENSIDAD_OBSTACULOS = 0.28             # Fracción de celdas bloqueadas
SEMILLA_BASE       = 42                # Semilla base para reproducibilidad
CARPETA_SALIDA     = "resultados"      # Directorio de imágenes generadas
MOSTRAR_GRAFICAS   = False             # True para mostrar ventana interactiva
# Opciones de GIF
GUARDAR_GIFS       = True             # True para guardar GIFs de cada búsqueda
GIF_NODOS_POR_FRAME = 6                # Nodos pintados por frame (velocidad)
GIF_FPS            = 24                # FPS para el GIF exportado


# ══════════════════════════════════════════════════════════════════════════════
# Funciones auxiliares
# ══════════════════════════════════════════════════════════════════════════════

def _banner() -> None:
    """Imprime el encabezado del programa."""
    print(
        "\n"
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║                   NAVEGADOR DE LABERINTOS                    ║\n"
        "╚══════════════════════════════════════════════════════════════╝"
    )


def _generar_laberinto_valido(
    tamano: int,
    densidad: float,
    semilla_base: int,
) -> Laberinto:
    """
    Genera un laberinto de (tamano × tamano) que tenga solución.
    Reintenta con semillas consecutivas si el laberinto generado no es solucionable.

    Args:
        tamano      (int)  : Número de filas y columnas.
        densidad    (float): Densidad de obstáculos [0, 1).
        semilla_base(int)  : Primera semilla a probar.

    Returns:
        Laberinto: Instancia garantizada con camino de A a B.
    """
    MAX_INTENTOS = 200
    semilla = semilla_base

    for intento in range(1, MAX_INTENTOS + 1):
        lab = Laberinto(tamano, tamano, densidad_obstaculos=densidad, semilla=semilla)
        if lab.tiene_solucion():
            if intento > 1:
                print(f"    (Encontrado laberinto válido en el intento {intento})")
            return lab
        semilla += 1

    raise RuntimeError(
        f"No se pudo generar un laberinto {tamano}×{tamano} solucionable "
        f"tras {MAX_INTENTOS} intentos."
    )


def _construir_buscadores(laberinto: Laberinto) -> dict[str, object]:
    """
    Instancia los cuatro algoritmos de búsqueda sobre el laberinto dado.

    Args:
        laberinto (Laberinto): Laberinto a explorar.

    Returns:
        dict: {nombre_algoritmo → instancia_buscador}.
    """
    return {
        BuscadorBFS.NOMBRE               : BuscadorBFS(laberinto),
        BuscadorDFS.NOMBRE               : BuscadorDFS(laberinto),
        BuscadorAEstrella.HEURISTICA_MANHATTAN  : BuscadorAEstrella(
            laberinto, BuscadorAEstrella.HEURISTICA_MANHATTAN
        ),
        BuscadorAEstrella.HEURISTICA_EUCLIDIANA : BuscadorAEstrella(
            laberinto, BuscadorAEstrella.HEURISTICA_EUCLIDIANA
        ),
    }


def _ejecutar_busquedas(
    laberinto: Laberinto,
) -> dict[str, ResultadoBusqueda]:
    """
    Ejecuta los cuatro algoritmos en el laberinto y devuelve sus resultados.

    Args:
        laberinto (Laberinto): Laberinto a resolver.

    Returns:
        dict: {nombre_algoritmo → ResultadoBusqueda}.
    """
    buscadores = _construir_buscadores(laberinto)
    resultados: dict[str, ResultadoBusqueda] = {}

    for nombre, buscador in buscadores.items():
        resultado = buscador.buscar()
        resultados[resultado.algoritmo] = resultado
        print(resultado.resumen())

    return resultados

# ══════════════════════════════════════════════════════════════════════════════
# Flujo principal
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """
    Punto de entrada.
    Para cada tamaño de laberinto definido en TAMANOS:
      1. Genera el laberinto.
      2. Ejecuta los 4 algoritmos.
      3. Guarda imagen del laberinto con los caminos.
    Al finalizar todos los tamaños:
      4. Genera y guarda la gráfica comparativa de métricas.
      5. Imprime la tabla resumen.
    """
    _banner()

    # Crear directorio de salida
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    todos_resultados: dict[int, dict[str, ResultadoBusqueda]] = {}
    laberintos:       dict[int, Laberinto]                     = {}

    for tamano in TAMANOS:
        # Generar laberinto con solución garantizada
        lab = _generar_laberinto_valido(tamano, DENSIDAD_OBSTACULOS, SEMILLA_BASE)
        print(f"  {lab}")
        laberintos[tamano] = lab

        # Ejecutar los cuatro algoritmos
        print(f"\n  Ejecutando algoritmos...\n")
        resultados = _ejecutar_busquedas(lab)
        todos_resultados[tamano] = resultados

        # Guardar imagen del laberinto
        ruta_img = os.path.join(CARPETA_SALIDA, f"laberinto_{tamano}x{tamano}.png")
        Visualizador.mostrar_laberinto_con_caminos(
            laberinto    = lab,
            resultados   = list(resultados.values()),
            titulo       = f"Laberinto {tamano}×{tamano}  —  Comparativa de Algoritmos",
            guardar_como = ruta_img,
            mostrar      = MOSTRAR_GRAFICAS,
        )

        # Generar animaciones GIF por algoritmo (opcional)
        if GUARDAR_GIFS:
            print("\n  Generando GIFs de búsqueda (puede tardar)...")
            for nombre_alg, resultado in resultados.items():
                # Normalizar nombre para archivo
                safe_nombre = "".join(ch if ch.isalnum() else "_" for ch in nombre_alg)
                ruta_gif = os.path.join(CARPETA_SALIDA, f"animacion_{tamano}x{tamano}_{safe_nombre}.gif")
                try:
                    Visualizador.guardar_animacion_gif(
                        laberinto = lab,
                        resultado = resultado,
                        archivo_salida = ruta_gif,
                        nodos_por_frame = GIF_NODOS_POR_FRAME,
                        fps = GIF_FPS,
                    )
                except Exception as e:
                    print(f"  ! Error guardando GIF {ruta_gif}: {e}")

    # Gráfica comparativa general
    print(f"\n{'═' * 62}")
    print("    GENERANDO GRÁFICA COMPARATIVA...")
    print("═" * 62)

    tamanos_con_resultado = [t for t in TAMANOS if t in todos_resultados]
    ruta_comp = os.path.join(CARPETA_SALIDA, "comparativa_algoritmos.png")
    Visualizador.mostrar_comparativa(
        todos_resultados = todos_resultados,
        tamanos          = tamanos_con_resultado,
        guardar_como     = ruta_comp,
        mostrar          = MOSTRAR_GRAFICAS,
    )

    # Tabla resumen en consola
    Visualizador.mostrar_tabla_resumen(todos_resultados, tamanos_con_resultado)


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
