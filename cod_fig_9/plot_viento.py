"""
Script 3: Plot del campo de flujo de humedad (U10·Q2, V10·Q2) para 5 experimentos.
Estructura del panel:
  - Fila 0 (j=0): promedios DJF para cada uno de los 5 experimentos.
  - Fila 1 (j=1): anomalías entre experimentos consecutivos (4 paneles; el
                  primero está vacío porque EXP0 no tiene referencia anterior).
"""

import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import cartopy.crs as ccrs
# Importa las funciones auxiliares del módulo local
from test import *

# ── Rutas ─────────────────────────────────────────────────────────────────────
DIR_VIENTO   = "../data/exp_mean_files/wind"
DIR_SALIDA   = "../figures"
DIR_SHAPES   = "../input_shp"                 

# ── Parámetros del plot ───────────────────────────────────────────────────────
MODS   = [0, 1, 5, 8, 10]       # índices de experimentos (orden del panel)
MODS2  = [                       # etiquetas descriptivas para cada experimento
    "GMTs_MOD30_SOM",
    "GMTns_MOD30_SOM",
    "GMTns_EVA_SOM",
    "GMTns_EVA_SIE",
    "GMTns_EVA_SIE_SST",
]
LPLT3  = ["a)", "b)", "c)", "d)", "e)", "f)", "g)", "h)", "i)", "j)"]

XTICKS = np.arange(-77, -64.5, 1)   # marcas de longitud para la grilla
YTICKS = np.arange(-23, -10,   1)   # marcas de latitud para la grilla

M_SKIP = 10      # submuestreo espacial para los vectores (cada M_SKIP puntos)
CRS    = ccrs.PlateCarree()

# ── Configuración tipográfica ─────────────────────────────────────────────────
plt.rcParams.update({"font.size": 10})
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"]  = ["Times New Roman"] + plt.rcParams["font.serif"]

# ── Creación de la figura ─────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 5.3))
gs  = GridSpec(nrows=2, ncols=5, figure=fig)

# Variables que se llenarán durante el bucle para usarlas al final
fondo_prom = fondo_anom = None
quiv_prom  = quiv_anom  = None
ultimo_ax  = None

n = 0   # contador global de paneles para las etiquetas a), b), c)...
# ── Bucle principal: 2 filas × 5 columnas ────────────────────────────────────
for j, tipo in enumerate(["prom", "anom"]):
    for i, (mod, mod2) in enumerate(zip(MODS, MODS2)):

        # El panel [1, 0] (anomalía de EXP0) no existe → se salta
        if i == 0 and j == 1:
            n += 1
            continue

        # Crea el eje con proyección cartográfica
        ax = fig.add_subplot(gs[j, i], projection=CRS)

        # Ruta al archivo correspondiente (prom o anom)
        ruta_nc    = f"{DIR_VIENTO}/{tipo}_wind_EXP{mod}.nc"
        es_anomalia = (j > 0)

        # ── Lee variables del NetCDF
        u, v, q, lons, lats = carga_campo(ruta_nc)

        # ── Dibuja el campo escalar de fondo (humedad)
        fondo = plot_fondo(ax, lons, lats, q, es_anomalia)

        # ── Superpone los vectores de flujo de humedad
        Q = plot_vectores(ax, lons, lats, u, v, q, es_anomalia, m=M_SKIP)

        # ── Añade contornos geográficos (país, lago)
        agrega_geometrias(ax, DIR_SHAPES)

        # ── Títulos: etiqueta descriptiva en fila de promedios,
        #            diferencia entre experimentos en fila de anomalías
        if es_anomalia:
            ax.set_title(f"{LPLT3[i][:1]} - {LPLT3[i-1][:1]}", loc="center")
            fondo_anom = fondo
            quiv_anom  = Q
        else:
            ax.set_title(mod2)
            fondo_prom = fondo
            quiv_prom  = Q

        # Etiqueta posicional (a, b, c…) en la esquina izquierda del panel
        ax.set_title(LPLT3[n], loc="left")

        # ── Añade la grilla con coordenadas
        agrega_grid(ax, i, j, numcol=5, numrow=2, xticks=XTICKS, yticks=YTICKS)

        ultimo_ax = ax
        n += 1

# ── Decoraciones finales ──────────────────────────────────────────────────────

# Barras de color (una para promedios, otra para anomalías)
agregar_colorbars(fig, fondo_prom, fondo_anom)

# Quiverkeys con unidades de referencia de los vectores
agregar_leyendas(ultimo_ax, quiv_anom, quiv_prom)

fig.tight_layout()

# ── Guardar figura ─────────────────────────────────────────────────────────────
ruta_salida = f"{DIR_SALIDA}/monmean_uvQ2_meanday.png"
fig.savefig(ruta_salida, dpi=100, bbox_inches="tight")
print(f"Figura guardada en: {ruta_salida}")
