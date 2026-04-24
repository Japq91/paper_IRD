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
import os 

# ============================================================================
# Variable y archivos de entrada
# ============================================================================
var = 'pr'  # 'pr' = precipitación, 't2m' = temperatura
outfile = f'../figures/test1_{var}.png'

SHP_RUTA = '../input_shp'
CSV_RUTA = '../input_csv'
OBS_RUTA = '../data/obs_mean_files'
NC_RUTA = '../data/mean_exp_files'

files=[f'{CSV_RUTA}/{var}_all_experimentos.csv', f'{OBS_RUTA}/obs_CHIRPS.nc', 
       f'{OBS_RUTA}/obs_CMORPH.nc', f'{OBS_RUTA}/obs_GPM.nc', f'{OBS_RUTA}/obs_PISCO.nc',
       f'{NC_RUTA}/{var}/prom_EXP0.nc', f'{NC_RUTA}/{var}/prom_EXP1.nc', f'{NC_RUTA}/{var}/prom_EXP5.nc', 
       f'{NC_RUTA}/{var}/prom_EXP8.nc', f'{NC_RUTA}/{var}/prom_EXP10.nc', f'{NC_RUTA}/{var}/anom_EXP1.nc',
       f'{NC_RUTA}/{var}/anom_EXP5.nc', f'{NC_RUTA}/{var}/anom_EXP8.nc', f'{NC_RUTA}/{var}/anom_EXP10.nc',
      ]

# ============================================================================
# Carga de shapefiles (fronteras)
# ============================================================================
lago = gpd.read_file(f'{SHP_RUTA}/lago_titikk_2022.shp')
peru = gpd.read_file(f'{SHP_RUTA}/peru2.shp')

# Etiquetas para cada subplot
exps2 = ['Station Data', 'CHIRPS', 'CMORPH', 'GPM', 'PISCO', 'GMTs\nMOD30_SOM', 'GMTns\nMOD30_SOM', 
         'GMTns\nEVA_SOM','GMTns\nEVA_SIE', 'GMTns\nEVA_SIE_SST','g) - f)', 'h) - g)', 'i) - h)', 'j) - i)']

# ============================================================================
# Configuración global de gráficos
# ============================================================================
plt.rcParams.update({'font.size': 10})
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

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
        norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=256)
        cmap = plt.cm.nipy_spectral_r
    return cmap, bounds, norm

def format_axis(ax, i, j, idx, labels, titles):
    """Ajusta títulos, etiquetas y grilla de cada subplot."""
    ax.set_title(titles[idx], loc='left', fontsize=11)
    ax.set_title(labels[idx], loc='center', fontsize=10)
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

def fondo_mapa(ax,lago,peru):
    lago.plot(ax=ax, edgecolor='b', facecolor='none', alpha=0.9, linewidth=0.85)
    peru.plot(ax=ax, edgecolor='k', facecolor='none', alpha=0.9, linewidth=0.7)
    ax.set_ylim(-17.05, -14.5)
    ax.set_xlim(-70.75, -68.2)    

# ============================================================================
# Creación de figura con GridSpec
# ============================================================================
print("Generando figura...")
fig = plt.figure(figsize=(10, 7.5))
gs = gridspec.GridSpec(3, 5, figure=fig, wspace=0.05, hspace=0.04)
titles = [chr(97 + i) + ")" for i in range(24)]  # a), b), c)...

idx = 0
im = None       # Inicializamos en None para seguridad en las barras de color
im_anom = None  # Inicializamos en None para seguridad en las barras de color

for i in range(3):
    for j in range(5):
        if (i, j) in [(2, 0)]:  # posición tachada (sin datos)
            continue
        ax = fig.add_subplot(gs[i, j])
        
        # Leer datos según el índice
        file = files[idx]
        print(f"  Procesando {file}...")
        cmap, bounds, norm = get_cmap_norm(file)
        
        # BLOQUE TRY-EXCEPT PARA MANEJO DE ARCHIVOS FALTANTES
        try:
            if idx == 0:
                # Datos de estaciones (CSV)
                df = pd.read_csv(file)
                lons, lats, precs = df["lon"], df["lat"], df[var]            
                sc = ax.scatter(lons, lats, c=precs, cmap=cmap, norm=norm,  ec="k", s=60, lw=0.4)
                im = sc  # para referencia de colorbar
            else:
                # Datos NetCDF utilizando un context manager (with)
                with xr.open_dataset(file) as ds:
                    data = ds[var].load() # Cargamos a memoria para poder cerrar el archivo
                    
                if 'anom' in file:
                    im_anom = data.plot(ax=ax, cmap=cmap, levels=bounds, add_colorbar=False, extend='both')
                else:
                    im = data.plot(ax=ax, cmap=cmap, norm=norm, add_colorbar=False, extend='both')
        
        except FileNotFoundError:
            print(f"    [!] Advertencia: Archivo no encontrado -> {file}")
            # Añadimos texto centrado en color rojo y negrita
            ax.text(0.5, 0.5, "NO DATA", color='red', weight='bold', fontsize=12,
                    ha='center', va='center', transform=ax.transAxes)
        
        # Agregar barras de color en posiciones específicas (ahora verificando que existan)
        if (i, j) == (1, 4) and im is not None:
            cax = fig.add_axes([0.91, 0.42, 0.02, 0.41])
            cbar = fig.colorbar(im, cax=cax, ticks=bounds[1:-1:2],
                                label="[mm/day]", extend='both')
        if (i, j) == (2, 4) and im_anom is not None:
            cax = fig.add_axes([0.91, 0.14, 0.02, 0.18])
            cbar = fig.colorbar(im_anom, cax=cax, ticks=bounds[1:-1:2],
                                label="[mm/day]", extend='both')
        
        # Dibujar fronteras y ajustar límites (esto se dibuja haya datos o no)
        fondo_mapa(ax,lago,peru)
        format_axis(ax, i, j, idx, exps2, titles)
        idx += 1

# Guardar y mostrar
# Crear directorio si no existe para evitar errores en savefig
os.makedirs(os.path.dirname(outfile), exist_ok=True)
plt.savefig(outfile, dpi=100, bbox_inches='tight')
print(f"Figura guardada en {outfile}")
plt.close()
print("DONE! figura 6-7 creada")
