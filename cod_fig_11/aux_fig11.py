"""
aux_fig11.py — Funciones auxiliares para visualización de precipitación y viento
============================================================================
Descripción:
    Módulo con funciones de plotting reutilizables para graficar campos de
    precipitación (promedio y anomalía) y flujo de humedad horizontal (Q2*viento)
    sobre la región del lago Titicaca, Perú. Compatible con datos WRF/PISCO.
 
Autor  : Jonathan [Apellido]
Fecha  : Febrero 2025
Proyecto: Comparación de experimentos WRF — ciclo diurno de precipitación
"""
 
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
 
 
# ---------------------------------------------------------------------------
# Colormap y niveles compartidos para precipitación en escala logarítmica
# ---------------------------------------------------------------------------
BOUNDS_PR = np.array([1, 2, 3, 4, 5, 7, 10, 15, 30, 45, 60, 100]) / 50
CMAP_PR   = plt.cm.nipy_spectral_r   # colormap para precipitación absoluta
NORM_PR   = mcolors.BoundaryNorm(boundaries=BOUNDS_PR, ncolors=255)
 
 
# ---------------------------------------------------------------------------
# Funciones de configuración de ejes
# ---------------------------------------------------------------------------
 
def configurar_ejes(ax, i, j, idx, titulos, etiquetas):
    """
    Aplica título, etiquetas de ejes, grid y ticks a un subplot.
 
    Parámetros
    ----------
    ax       : Axes de matplotlib
    i        : fila del subplot (0-based)
    j        : columna del subplot (0-based)
    idx      : índice global del panel
    titulos  : lista de títulos centrados para cada panel
    etiquetas: lista de etiquetas laterales (p.ej. 'a)', 'b)', ...)
    """
    ax.set_title(titulos[idx], loc='center')
    ax.set_title(etiquetas[idx], loc='left')
 
    # Ticks de latitud y longitud fijos para la región de estudio
    ax.set_yticks([-17, -16, -15])
    ax.set_xticks([-70, -69])
    ax.set_ylabel('')
    ax.set_xlabel('')
    ax.grid(lw=0.8, ls=':', c='gray')
 
    # Mostrar etiquetas de latitud solo en la columna izquierda
    if j == 0:
        ax.set_yticklabels(["17°S", "16°S", "15°S"])
    else:
        ax.set_yticklabels(["", "", ""])
 
    # Mostrar etiquetas de longitud solo en la fila inferior
    if i == 4:
        ax.set_xticklabels(["70°W", "69°W"])
    else:
        ax.set_xticklabels(["", ""])
 
 
# ---------------------------------------------------------------------------
# Funciones de ploteo de fondo (precipitación)
# ---------------------------------------------------------------------------
 
def plot_fondo(ax, i, j, archivo, tipo):
    """
    Grafica el campo de precipitación como imagen de fondo.
 
    Parámetros
    ----------
    ax      : Axes de matplotlib
    i, j    : fila y columna del subplot (para lógica futura)
    archivo : ruta al archivo NetCDF con variable 'pr'
    tipo    : 'prom' para promedio absoluto, 'anom' para anomalía
 
    Retorna
    -------
    fondo1 : objeto QuadMesh de xarray (para colorbar)
    """
    d = xr.open_dataset(archivo)['pr']
 
    if tipo == 'anom':
        # Anomalías: escala divergente centrada en 0
        mapa = 'RdBu_r'
        leve = np.arange(-0.4, 0.45, 0.05)
        fondo1 = d.plot(ax=ax, add_colorbar=False, cmap=mapa, levels=leve)
    else:
        # Promedio absoluto: escala logarítmica con colormap espectral
        fondo1 = d.plot(ax=ax, add_colorbar=False, cmap=CMAP_PR, norm=NORM_PR)
 
    return fondo1
 
 
def plot_obs(ax, i, j, archivo):
    """
    Grafica el campo de precipitación observada interpolada (PISCO).
 
    Parámetros
    ----------
    ax      : Axes de matplotlib
    i, j    : fila y columna (para lógica futura)
    archivo : ruta al NetCDF con variable 'p'
 
    Retorna
    -------
    fondo1 : objeto QuadMesh de xarray (para colorbar)
    """
    d = xr.open_dataset(archivo)['p']
    fondo1 = d.plot(ax=ax, add_colorbar=False, cmap=CMAP_PR, norm=NORM_PR)
    return fondo1
 
 
def plot_estaciones(ax, i, j, df, periodo):
    """
    Grafica observaciones de estaciones meteorológicas como puntos dispersos.
 
    Parámetros
    ----------
    ax      : Axes de matplotlib
    i, j    : fila y columna (para lógica futura)
    df      : DataFrame con columnas 'lon', 'lat' y columna con nombre=periodo
    periodo : nombre de la columna de precipitación a graficar ('dia' o 'noche')
    """
    lons  = df["lon"]
    lats  = df["lat"]
    precs = df[periodo]
    ax.scatter(lons, lats, c=precs, cmap=CMAP_PR, norm=NORM_PR,
               edgecolors="k", s=60, lw=0.4, zorder=5)
 
 
# ---------------------------------------------------------------------------
# Funciones de ploteo de viento / flujo de humedad
# ---------------------------------------------------------------------------
 
def plot_viento_humedad(ax, i, j, archivo, tipo):
    """
    Grafica vectores de flujo de humedad horizontal (Q2 * [U10, V10]).
 
    Parámetros
    ----------
    ax      : Axes de matplotlib
    i, j    : fila y columna (para escala de vectores)
    archivo : ruta al NetCDF de Q2 (se reemplaza internamente para U10/V10)
    tipo    : 'anom' o 'prom' — controla la escala de los vectores
 
    Retorna
    -------
    Q2 : objeto Quiver de matplotlib (para quiverkey)
    """
    # Escala de los vectores según tipo de campo
    if tipo == 'anom':
        escala = 0.8
    elif tipo == 'prom':
        escala = 0.008
    else:
        escala = 1.0  # valor de respaldo
 
    m = 8  # submuestreo espacial de vectores (cada 8 puntos de grilla)
 
    # Cargar variables
    dq = xr.open_dataset(archivo)['Q2']
    du = xr.open_dataset(archivo.replace('Q2', 'U10'))['U10']
    dv = xr.open_dataset(archivo.replace('Q2', 'V10'))['V10']
 
    lons = dq.lon
    lats = dq.lat
 
    # Flujo de humedad: Q2 * componentes del viento
    ut = du * dq
    vt = dv * dq
 
    Q2 = ax.quiver(
        lons[::m], lats[::m],
        ut[::m, ::m], vt[::m, ::m],
        scale=1 / escala, width=0.008,
        scale_units='xy', angles='xy', zorder=4
    )
    return Q2
 
 
def agregar_referencia_viento(ax, i, j, tipo, Q2):
    """
    Agrega una flecha de referencia (quiverkey) al panel indicado.
 
    Parámetros
    ----------
    ax   : Axes de matplotlib
    i, j : fila y columna del subplot
    tipo : 'anom' o 'prom'
    Q2   : objeto Quiver retornado por plot_viento_humedad
    """
    if tipo == 'anom':
        vec = 0.4
    elif tipo == 'prom':
        vec = 20
    else:
        vec = 1
 
    # Referencia solo en paneles específicos para no saturar la figura
    if i == 0 and j == 0:
        ax.quiverkey(Q2, 4.25, 1.02, vec,
                     label=r'$%s\frac{m \cdot g}{s \cdot kg}$' % vec,
                     labelpos='N', coordinates='axes')
    elif i == 1 and j == 1:
        ax.quiverkey(Q2, 3.22, 1.02, vec,
                     label=r'$%s\frac{m \cdot g}{s \cdot kg}$' % vec,
                     labelpos='N', coordinates='axes')
 
 
