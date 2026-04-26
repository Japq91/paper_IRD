"""
plot_bias_estaciones.py — Sesgo relativo de precipitación y mapas de calor
===========================================================================
Descripción:
    Figura 3×5 con sesgos relativos WRF vs observaciones (día/noche) en
    estaciones meteorológicas y heatmaps de precipitación media por experimento.

Autor  : Jonathan 
Fecha  : Abril 2025
"""

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import geopandas as gpd
import numpy as np

from aux_bias import (
    IDS_EXPERIMENTOS, PERIODOS, TITULOS_PANEL, NOMBRES_HEATMAP, XLIM, YLIM,
    cargar_sesgo, configurar_ejes_mapa, etiqueta_fila,
    plot_shapes, plot_sesgo_estaciones, plot_heatmap,
    agregar_colorbar_sesgo, agregar_colorbar_heatmap,
)



ruta_shapes  = "../input_shp"
ruta_input   = "../data/csv_files"
ruta_salida  = "../figures"

lago = gpd.read_file(f"{ruta_shapes}/lago_titikk_2022.shp")
peru = gpd.read_file(f"{ruta_shapes}/peru2.shp")

# nc_dia   = xr.open_dataset(f"{ruta_input}/datos_dia.nc")['Precipitation']
# nc_noche = xr.open_dataset(f"{ruta_input}/datos_noche.nc")['Precipitation']

# =============================================================================
# Figura
# =============================================================================
fig = plt.figure(figsize=(12, 6))
gs  = gridspec.GridSpec(2, 5, figure=fig, hspace=0.015, wspace=0.12,
                        height_ratios=[1.5, 1.5])
# =============================================================================
# Configuración global y rutas
# =============================================================================
plt.rcParams.update({'font.size': 10})
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
# -----------------------------------------------------------------------------
# Filas 0-1: mapas de sesgo relativo (día y noche)
# -----------------------------------------------------------------------------
for row, periodo in enumerate(PERIODOS):

    obs = None  # se guarda para reusar en los heatmaps
    for col, exp_id in enumerate(IDS_EXPERIMENTOS):

        obs, pdf = cargar_sesgo(ruta_input, exp_id, periodo)
        ax  = fig.add_subplot(gs[row, col])
        idx = row * 5 + col

        etiqueta_fila(ax, idx)
        plot_shapes(ax, lago, peru)
        ax.set_xlim(XLIM); ax.set_ylim(YLIM)
        configurar_ejes_mapa(ax, idx)
        plot_sesgo_estaciones(ax, pdf, periodo)
agregar_colorbar_sesgo(fig, pos=[0.91, 0.33, 0.02, 0.33])

# -----------------------------------------------------------------------------
# Fila 2: heatmaps de precipitación media
# -----------------------------------------------------------------------------
# codigos_estacion = obs['code']   # etiquetas de estación del último obs cargado

# ax_dia = fig.add_subplot(gs[2, 0:2])
# plot_heatmap(ax_dia, nc_dia, idx=10,
#              etiquetas_x=NOMBRES_HEATMAP, etiquetas_y=codigos_estacion,
#              niveles=np.arange(1, 7, 1), titulo=TITULOS_PANEL[10])

# ax_noche  = fig.add_subplot(gs[2, 3:5])
# niveles_n = np.arange(1, 6.5, 0.5)
# fondo_n   = plot_heatmap(ax_noche, nc_noche, idx=11,
#                           etiquetas_x=NOMBRES_HEATMAP, etiquetas_y=codigos_estacion,
#                           niveles=niveles_n, titulo=TITULOS_PANEL[11])

# agregar_colorbar_heatmap(fig, fondo_n, niveles_n, pos=[0.91, 0.1, 0.02, 0.18])

# =============================================================================
# Guardado
# =============================================================================
archivo_png = f"{ruta_salida}/dianoche_dif_pr_19abr2025_v2.jpg"
plt.savefig(archivo_png, dpi=100, bbox_inches='tight')
print(f"Figura guardada en: {archivo_png}")
# plt.show()