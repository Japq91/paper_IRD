#!/usr/bin/env python
# coding: utf-8

"""
Script para visualizar precipitación media (mm/día) de estaciones,
productos satelitales (CHIRPS, CMORPH, GPM, PISCO) y simulaciones WRF (EXP0,1,5,8,10)
con anomalías, en el dominio del Lago Titicaca y Perú.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import geopandas as gpd
import pandas as pd
import xarray as xr
import matplotlib.colors as mcolors
import numpy as np

# ============================================================================
# Configuración global de gráficos
# ============================================================================
plt.rcParams.update({'font.size': 10})
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

# ============================================================================
# Carga de shapefiles (fronteras)
# ============================================================================
print("Cargando shapefiles...")
lago = gpd.read_file('/home/jonathan/SHAPE/lago_titikk_2022.shp')
peru = gpd.read_file('/home/jonathan/SHAPE/peru2.shp')
print("Shapefiles cargados.")

# ============================================================================
# Variable y archivos de entrada
# ============================================================================
var = 'pr'  # 'pr' = precipitación, 't2m' = temperatura
files = ['../input_csv/%s_all_experimentos.csv' % var,
         'prec_files/mon/obs_CHIRPS.nc', 'prec_files/mon/obs_CMORPH.nc',
    'prec_files/mon/obs_GPM.nc', 'prec_files/mon/obs_PISCO.nc',
    'nc_files/clean/%s/prom_EXP0.nc' % var, 'nc_files/clean/%s/prom_EXP1.nc' % var,
    'nc_files/clean/%s/prom_EXP5.nc' % var, 'nc_files/clean/%s/prom_EXP8.nc' % var,
    'nc_files/clean/%s/prom_EXP10.nc' % var,
    'nc_files/clean/%s/anom_EXP1.nc' % var, 'nc_files/clean/%s/anom_EXP5.nc' % var,
    'nc_files/clean/%s/anom_EXP8.nc' % var, 'nc_files/clean/%s/anom_EXP10.nc' % var
]

# Etiquetas para cada subplot
exps2 = [
    'Station Data', 'CHIRPS', 'CMORPH', 'GPM', 'PISCO',
    'GMTs\nMOD30_SOM', 'GMTns\nMOD30_SOM', 'GMTns\nEVA_SOM',
    'GMTns\nEVA_SIE', 'GMTns\nEVA_SIE_SST',
    'g) - f)', 'h) - g)', 'i) - h)', 'j) - i)'
]

# ============================================================================
# Funciones auxiliares
# ============================================================================
def get_cmap_norm(filepath):
    """Define colormap y normalización según si es anomalía o precipitación."""
    if 'anom' in filepath:
        cmap = 'BrBG'
        bounds = np.arange(-5, 6, 1)
        norm = None  # para levels en plot
    else:
        bounds = np.array([1, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.2, 4.5, 4.8, 5.1, 5.4,
                           5.7, 6, 8, 10, 15, 20, 30, 40, 100])
        cmap = plt.cm.nipy_spectral_r
        norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=256)
    return cmap, bounds, norm

def format_axis(ax, i, j, idx, labels, titles):
    """Ajusta títulos, etiquetas y grilla de cada subplot."""
    ax.set_title(titles[idx], loc='left', fontsize=10)
    ax.set_title(labels[idx], loc='center', fontsize=9)
    ax.set_yticks([-17, -16, -15])
    ax.set_xticks([-70, -69])
    ax.grid(lw=0.8, ls=':', c='gray')
    if j == 0:
        ax.set_yticklabels(["17°S", "16°S", "15°S"])
    else:
        ax.set_yticklabels(["", "", ""])
    if i == 2:
        ax.set_xticklabels(["70°W", "69°W"])
    else:
        ax.set_xticklabels(["", ""])
    ax.set_xlabel('')
    ax.set_ylabel('')

# ============================================================================
# Creación de figura con GridSpec
# ============================================================================
print("Generando figura...")
fig = plt.figure(figsize=(12, 9))
gs = gridspec.GridSpec(3, 5, figure=fig, wspace=0.05, hspace=0.04)
titles = [chr(97 + i) + ")" for i in range(24)]  # a), b), c)...

idx = 0
for i in range(3):
    for j in range(5):
        if (i, j) in [(2, 0)]:  # posición tachada (sin datos)
            continue
        ax = fig.add_subplot(gs[i, j])
        
        # Leer datos según el índice
        file = files[idx]
        print(f"  Procesando {file}...")
        
        if idx == 0:
            # Datos de estaciones (CSV)
            df = pd.read_csv(file)
            lons, lats, precs = df["lon"], df["lat"], df[var]
            cmap, bounds, norm = get_cmap_norm(file)
            sc = ax.scatter(lons, lats, c=precs, cmap=cmap, norm=norm,
                            ec="k", s=60, lw=0.4)
            im = sc  # para referencia de colorbar
        else:
            # Datos NetCDF
            ds = xr.open_dataset(file)[var]
            cmap, bounds, norm = get_cmap_norm(file)
            if 'anom' in file:
                im = ds.plot(ax=ax, cmap=cmap, levels=bounds,
                             add_colorbar=False, extend='both')
            else:
                im = ds.plot(ax=ax, cmap=cmap, norm=norm,
                             add_colorbar=False, extend='both')
        
        # Agregar barras de color en posiciones específicas
        if (i, j) == (1, 4):
            cax = fig.add_axes([0.91, 0.42, 0.02, 0.41])
            cbar = fig.colorbar(im, cax=cax, ticks=bounds[1:-1:2],
                                label="[mm/day]", extend='both')
        if (i, j) == (2, 4):
            cax = fig.add_axes([0.91, 0.14, 0.02, 0.18])
            cbar = fig.colorbar(im, cax=cax, ticks=bounds[1:-1:2],
                                label="[mm/day]", extend='both')
        
        # Dibujar fronteras y ajustar límites
        lago.plot(ax=ax, edgecolor='b', facecolor='none', alpha=0.9, linewidth=0.85)
        peru.plot(ax=ax, edgecolor='k', facecolor='none', alpha=0.9, linewidth=0.7)
        ax.set_ylim(-17.05, -14.5)
        ax.set_xlim(-70.75, -68.2)
        format_axis(ax, i, j, idx, exps2, titles)
        idx += 1

# Guardar y mostrar
outfile = 'out/test_pr.png'
plt.savefig(outfile, dpi=100, bbox_inches='tight')
print(f"Figura guardada en {outfile}")
plt.close()
print("Proceso completado.")