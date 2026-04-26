"""
aux_bias.py — Funciones auxiliares para plot_bias_estaciones.py
================================================================
Autor  : Jonathan [Apellido]
Fecha  : Abril 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# =============================================================================
# Constantes compartidas
# =============================================================================

BOUNDS_SESGO = np.arange(-100, 110, 10)   # niveles del colormap de sesgo [%]
CMAP_SESGO   = plt.cm.RdBu_r
NORM_SESGO   = mcolors.BoundaryNorm(BOUNDS_SESGO, CMAP_SESGO.N)

XLIM = (-70.8, -68.3)
YLIM = (-17.05, -14.4)

IDS_EXPERIMENTOS = [0, 1, 5, 8, 10]
PERIODOS         = ['dia', 'noche']

TITULOS_PANEL = [
    'GMTs\nMOD30_SOM',  'GMTns\nMOD30_SOM', 'GMTns\nEVA_SOM',
    'GMTns\nEVA_SIE',   'GMTns\nEVA_SIE_SST',
    'GMTs\nMOD30_SOM',  'GMTns\nMOD30_SOM', 'GMTns\nEVA_SOM',
    'GMTns\nEVA_SIE',   'GMTns\nEVA_SIE_SST',
    'Day', 'Night',
]

NOMBRES_HEATMAP = [
    'Observed\ndata', 'GMTs\nMOD30\nSOM', 'GMTns\nMOD30\nSOM',
    'GMTns\nEVA\nSOM', 'GMTns\nEVA\nSIE', 'GMTns\nEVA\nSIE_SST',
]

ETIQUETAS = [chr(97 + i) + ")" for i in range(12)]


# =============================================================================
# Funciones de datos
# =============================================================================

def calcular_sesgo(obs, mod, periodo):
    """
    Calcula el sesgo relativo (%) entre modelo y observación.
    Retorna un DataFrame con columnas lon, lat y la columna <periodo>.
    """
    pdf = pd.DataFrame(100 * (mod[periodo] - obs[periodo]) / obs[periodo])
    pdf['lon'] = obs['lon']
    pdf['lat'] = obs['lat']
    return pdf


def cargar_sesgo(ruta_input, exp_id, periodo):
    """
    Carga observaciones y modelo para un experimento y periodo dados,
    y retorna el DataFrame de sesgo relativo.
    """
    obs = pd.read_csv(f"{ruta_input}/pr_OBS_{periodo}.csv")
    mod = pd.read_csv(f"{ruta_input}/pr_EXP{exp_id}_{periodo}.csv")
    return obs, calcular_sesgo(obs, mod, periodo)


# =============================================================================
# Funciones de configuración de ejes
# =============================================================================

def configurar_ejes_mapa(ax, idx):
    """
    Aplica título, ticks, grid y etiquetas lat/lon al panel de índice idx.
    Muestra etiquetas de latitud solo en col 0 y de longitud solo en fila 0.
    """
    ax.set_title(TITULOS_PANEL[idx], loc='center')
    ax.set_title(ETIQUETAS[idx], loc='left')
    ax.set_yticks([-17, -16, -15])
    ax.set_xticks([-71, -70, -69])
    ax.grid(lw=0.8, ls=':', c='gray')
    ax.set_yticklabels(["17°S", "16°S", "15°S"] if idx in [0, 5] else ["", "", ""])
    ax.set_xticklabels(["71°W", "70°W", "69°W"] if idx not in [5,6,7,8,9] else ["","",""])


def etiqueta_fila(ax, idx):
    """Agrega etiqueta vertical 'Day' o 'Night' al primer panel de cada fila."""
    if idx == 0:
        ax.text(-0.35, 0.5, 'Day',   transform=ax.transAxes,
                ha='center', va='center', fontsize=12, rotation=90)
    elif idx == 5:
        ax.text(-0.35, 0.5, 'Night', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, rotation=90)


# =============================================================================
# Funciones de ploteo
# =============================================================================

def plot_shapes(ax, lago, peru):
    """Superpone los shapefiles del lago Titicaca y el contorno de Perú."""
    lago.plot(ax=ax, edgecolor='k', facecolor='lightblue', alpha=0.9, linewidth=0.9)
    peru.plot(ax=ax, edgecolor='k', facecolor='none',      alpha=0.9, linewidth=0.7)


def plot_sesgo_estaciones(ax, df, periodo):
    """
    Grafica el sesgo relativo (%) como puntos dispersos.
    Positivos → triángulo rojo ▲ ; Negativos → triángulo azul ▼.
    Tamaño proporcional al valor absoluto del sesgo.
    """
    for mask, marker, color in [
        (df[periodo] > 0, '^', 'r'),
        (df[periodo] < 0, 'v', 'b'),
    ]:
        sub = df[mask]
        if sub.empty:
            print(f'  [aviso] sin datos {">0" if color=="r" else "<0"} en {periodo}')
            continue
        ax.scatter(sub["lon"], sub["lat"],
                   c=sub[periodo], cmap=CMAP_SESGO, norm=NORM_SESGO,
                   s=abs(sub[periodo] * 2), marker=marker,
                   edgecolors=color, alpha=0.95, lw=0.5, zorder=3)


def plot_heatmap(ax, nc, idx, etiquetas_x, etiquetas_y, niveles, titulo):
    """
    Grafica un heatmap de precipitación media (xarray) y configura sus ejes.

    Retorna el objeto de imagen para construir la colorbar.
    """
    ax.text(0.5, 1.06, titulo, transform=ax.transAxes, ha='center', fontsize=12)
    ax.set_title(ETIQUETAS[idx], loc='left')
    fondo = nc.plot(ax=ax, extend='both', levels=niveles,
                    add_colorbar=False, cmap='turbo')
    ax.set_xticks(nc.Data.values)
    ax.set_xticklabels(etiquetas_x)
    ax.set_yticks(nc.Stations.values)
    ax.set_yticklabels(etiquetas_y)
    return fondo


# =============================================================================
# Funciones de colorbars
# =============================================================================

def agregar_colorbar_sesgo(fig, pos):
    """
    Agrega la colorbar de sesgo relativo [%] en la posición indicada.
    pos : [left, bottom, width, height]
    """
    cax = fig.add_axes(pos)
    fig.colorbar(
        plt.cm.ScalarMappable(cmap=CMAP_SESGO, norm=NORM_SESGO),
        cax=cax, orientation="vertical", ticks=BOUNDS_SESGO[::2],
    ).set_label("[%]")


def agregar_colorbar_heatmap(fig, fondo, niveles, pos):
    """
    Agrega la colorbar del heatmap de precipitación [mm/12h].
    pos : [left, bottom, width, height]
    """
    cax = fig.add_axes(pos)
    fig.colorbar(fondo, cax=cax, orientation="vertical",
                 ticks=niveles[::2]).set_label("[mm/12h]")