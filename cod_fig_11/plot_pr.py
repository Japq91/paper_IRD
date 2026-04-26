"""
plot_pr.py — Figura de ciclo diurno de precipitación y flujo de humedad
=========================================================================
Descripción:
    Genera una figura de 5×4 paneles comparando experimentos WRF (promedio y
    anomalías de precipitación + flujo de humedad Q2·viento) contra datos
    observados (PISCO + estaciones) para los periodos diurno y nocturno.
    La figura cubre la región del lago Titicaca (sur del Perú).

Autor  : japaredesq@gmail.com 
Fecha  : Febrero 2025
Proyecto: Comparación de experimentos WRF — ciclo diurno de precipitación

"""

# =============================================================================
# 1. Importaciones
# =============================================================================
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import geopandas as gpd
import pandas as pd
import numpy as np
from aux_fig11 import (
    BOUNDS_PR,
    configurar_ejes,
    plot_fondo,
    plot_obs,
    plot_estaciones,
    plot_viento_humedad,
    agregar_referencia_viento,
)


# =============================================================================
# 2. Rutas base y archivos de entrada
# =============================================================================
ruta_shapes   = "../input_shp"
ruta_periodos = "../data/exp_hour_files"
ruta_obs      = "../data/obs_hour_files"
ruta_csv      = "../data/csv_files"
ruta_salida   = "../figures"

# =============================================================================
# 3. Configuración global de matplotlib
# =============================================================================
plt.rcParams.update({'font.size': 10})
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

# Shapefiles de la región de estudio
archivo_lago = f"{ruta_shapes}/lago_titikk_2022.shp"
archivo_peru = f"{ruta_shapes}/peru2.shp"

# Tabla con datos de estaciones meteorológicas (columnas: lon, lat, dia, noche)
archivo_csv  = f"{ruta_csv}/pr_periodos.csv"

# Archivo de salida
archivo_png  = f"{ruta_salida}/dia_noche_pr_Qwind.png"

# =============================================================================
# 4. Carga de datos geoespaciales y estaciones
# =============================================================================
lago = gpd.read_file(archivo_lago)
peru = gpd.read_file(archivo_peru)
df_estaciones = pd.read_csv(archivo_csv)

# =============================================================================
# 5. Metadatos de los paneles
#    Cada lista tiene 20 elementos — uno por panel (5 filas × 4 columnas,
#    recorrido columna a columna, de arriba a abajo).
# =============================================================================

# Índice del experimento WRF (0,1,5,8,10) o 'obs' para observaciones
experimentos = [
    0, 1, 5, 8, 10, 'obs', 1, 5, 8, 10,
    0, 1, 5, 8, 10, 'obs', 1, 5, 8, 10,
]

# Periodo del día para cada panel
periodos = [
    'dia',   'dia',   'dia',   'dia',   'dia',
    'dia',   'dia',   'dia',   'dia',   'dia',
    'noche', 'noche', 'noche', 'noche', 'noche',
    'noche', 'noche', 'noche', 'noche', 'noche',
]

# Tipo de campo: promedio absoluto, observaciones o anomalía respecto al panel anterior
tipos = [
    'prom', 'prom', 'prom', 'prom', 'prom',
    'obs',  'anom', 'anom', 'anom', 'anom',
    'prom', 'prom', 'prom', 'prom', 'prom',
    'obs',  'anom', 'anom', 'anom', 'anom',
]

# Títulos centrados de cada panel (nombre del experimento o diferencia)
titulos_panel = [
    'GMTs\nMOD30_SOM',    'GMTns\nMOD30_SOM', 'GMTns\nEVA_SOM',
    'GMTns\nEVA_SIE',     'GMTns\nEVA_SIE_SST',
    'PISCO &\nStation Data', 'b) - a)', 'c) - b)', 'd) - c)', 'e) - d)',
    'GMTs\nMOD30_SOM',    'GMTns\nMOD30_SOM', 'GMTns\nEVA_SOM',
    'GMTns\nEVA_SIE',     'GMTns\nEVA_SIE_SST',
    'PISCO &\nStation Data', 'l) - k)', 'm) - l)', 'n) - m)', 'o) - n)',
]

# Etiquetas alfabéticas de esquina izquierda: a), b), ..., t)
etiquetas = [chr(97 + i) + ")" for i in range(20)]

# Paneles que muestran observaciones (no campos WRF)
paneles_obs = [(0, 1), (0, 3)]  # (fila, columna) — columnas con PISCO + estaciones

# Extensión geográfica de todos los paneles (región Titicaca)
XLIM = (-70.75, -68.2)
YLIM = (-17.05, -14.5)

# =============================================================================
# 6. Construcción de la figura
# =============================================================================
fig = plt.figure(figsize=(11, 17))

# GridSpec de 5 filas × 4 columnas con separación mínima entre paneles
gs = gridspec.GridSpec(5, 4, figure=fig, wspace=0.05, hspace=0.04)

idx = 0  # índice global del panel (0..19)

for j in range(4):       # columnas
    for i in range(5):   # filas

        ax = fig.add_subplot(gs[i, j])

        # -----------------------------------------------------------------
        # 6a. Panel observacional: PISCO interpolado + puntos de estación
        # -----------------------------------------------------------------
        if (i, j) in paneles_obs:
            obs_file = f"{ruta_obs}/prom_pr_PISCO-nDBC_{periodos[idx]}.nc"
            #obs_file = f"{ruta_obs}/prom_pr_PISCO_{periodos[idx]}.nc"            
            plot_obs(ax, i, j, obs_file)
            plot_estaciones(ax, i, j, df_estaciones, periodos[idx])

        # -----------------------------------------------------------------
        # 6b. Panel WRF: fondo de precipitación + vectores de flujo humedad
        # -----------------------------------------------------------------
        else:
            # Archivo de precipitación del experimento
            pfile = f"{ruta_periodos}/pr_{tipos[idx]}_EXP{experimentos[idx]}_{periodos[idx]}.nc"
            fondo = plot_fondo(ax, i, j, pfile, tipos[idx])

            # Archivo de flujo de humedad (Q2) del mismo experimento
            qfile = f"{ruta_periodos}/Q2_{tipos[idx]}_EXP{experimentos[idx]}_{periodos[idx]}.nc"
            q2 = plot_viento_humedad(ax, i, j, qfile, tipos[idx])

            # Colorbar de precipitación promedio (solo primer panel de prom)
            if i == 0 and j == 0:
                cax1 = fig.add_axes([0.91, 0.755, 0.02, 0.1])
                fig.colorbar(fondo, cax=cax1, label='[mm/hour]',
                             extend='both', ticks=BOUNDS_PR)
                agregar_referencia_viento(ax, i, j, tipos[idx], q2)

            # Colorbar de anomalías (solo primer panel de anom)
            if i == 1 and j == 1:
                cax2 = fig.add_axes([0.91, 0.60, 0.02, 0.1])
                fig.colorbar(fondo, cax=cax2, label='[mm/hour]', extend='both')
                agregar_referencia_viento(ax, i, j, tipos[idx], q2)

        # -----------------------------------------------------------------
        # 6c. Decoraciones comunes a todos los paneles
        # -----------------------------------------------------------------
        configurar_ejes(ax, i, j, idx, titulos_panel, etiquetas)

        ax.set_xlim(XLIM)
        ax.set_ylim(YLIM)

        # Superposición de shapefiles de la región
        lago.plot(ax=ax, edgecolor='b', facecolor='none',
                  alpha=0.9, linewidth=0.85)
        peru.plot(ax=ax, edgecolor='k', facecolor='none',
                  alpha=0.9, linewidth=0.7)

        idx += 1

# =============================================================================
# 7. Guardado y visualización
# =============================================================================
plt.savefig(archivo_png, dpi=100, bbox_inches='tight')
print(f"Figura guardada en: {archivo_png}")
plt.close()