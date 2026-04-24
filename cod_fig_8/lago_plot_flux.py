#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de visualización: Average Lake Surface Temperature (LST; °C) for experiments GMTns_EVA_SIE (a) and GMTns_EVA_SIE_SST (b) and their difference (c). Cloud fraction (CLDFRA, %), sensible heat (HFX, W/m2) and latent heat (LH, W/m2) differences between both experiments (GMTns_EVA_SIE_SST minus GMTns_EVA_SIE), characterizing the impacts of the SST update configuration in d), e), f), respectively.

Autor: japaredesq@gmail.com
Fecha: 23042026
"""

import warnings
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from matplotlib.gridspec import GridSpec

warnings.filterwarnings("ignore")

# ======================================================================
# 1. CONFIGURACIÓN DE RUTAS Y PARÁMETROS
# ======================================================================
DIR_SHAPES = '../input_shp'
DIR_DATA = '../data/lago_files'
OUT_DIR = '../figures'

# Configuración de fuente
plt.rcParams.update({'font.size': 10, 'font.family': 'serif'})
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

# Proyección y Grilla
CRS = ccrs.PlateCarree()
XTICKS = np.arange(-71, -67, 1)
YTICKS = np.arange(-17, -14, 1)

# Shapefiles (Carga única)
SHP_LAGO = Reader(f'{DIR_SHAPES}/lago_titikk_2022.shp')
SHP_PERU = Reader(f'{DIR_SHAPES}/peru2.shp')
SHP_NOLAGO = Reader(f'{DIR_SHAPES}/lago_sin_lago.shp')

titus = ['a)', 'd)', 'b)', 'e)', 'c)', 'f)', 'g)']

# ======================================================================
# 2. FUNCIONES DE APOYO
# ======================================================================

def agrega_grid(i, j, numcol, numrow, ax):
    """ Configura etiquetas de lat/lon siguiendo tu lógica original de bordes. """
    grd = ax.gridlines(xlocs=XTICKS, ylocs=YTICKS, color='gray', alpha=0.99, 
                       draw_labels=True, linewidth=1, linestyle='--')
    grd.top_labels = grd.right_labels = False
    
    # Solo etiquetas a la izquierda si es la primera columna
    grd.left_labels = True if i == 0 else False
    # Solo etiquetas abajo si es la última fila
    grd.bottom_labels = True if j == numrow - 1 else False

def set_lim(var, file_name):
    """ Define los niveles de la barra de colores. """
    if 'CLDFRA' in var: return np.linspace(-2, 2, 11)
    elif 'HFX' in var:  return np.linspace(-20, 20, 11)
    elif 'LH' in var:   return np.linspace(-20, 20, 11)
    else:
        # Para TSK: diferencia (anom) o campo corregido
        if 'anom' in file_name or 'EXP10-EXP8' in file_name:
            return np.linspace(-3, 3, 13)
        else:
            return np.linspace(12, 18, 13)

# ======================================================================
# 3. PROCESAMIENTO Y DIBUJO
# ======================================================================

# Cargar dataset de referencia (SKA)
ska = xr.open_dataset(f'{DIR_DATA}/LU_16_EVA.nc')['LH']

fig = plt.figure(figsize=(12, 6))
gs = GridSpec(nrows=2, ncols=3)
nti = 0

# Bucle Vertical (Tu lógica original i -> j)
for i in range(3):
    for j in range(2):
        ax = fig.add_subplot(gs[j, i], projection=CRS)
        
        # --- A. Selección de archivos y variables ---
        if j == 0:  # Fila superior (TSK)
            if i == 0:   file = f'{DIR_DATA}/v2modif_wrf_d02_dy_EXP8.nc'; var = 'TSK'
            elif i == 1: file = f'{DIR_DATA}/v2modif_wrf_d02_dy_EXP10.nc'; var = 'TSK'
            else:        file = f'{DIR_DATA}/modif_anom_EXP10-EXP8.nc'; var = 'TSK'
            
            # Máscara blanca del lago (NOLAGO)
            ax.add_geometries(SHP_NOLAGO.geometries(), crs=CRS, edgecolor='k', 
                               facecolor='w', alpha=1, linewidth=.7, zorder=2)
            extent = [-70.1, -68.5, -16.7, -15.2]
        else:      # Fila inferior (Anomalías)
            if i == 0:   file = f'{DIR_DATA}/anom_CLDFRA_d02_2019_2020_dy_EXP10.nc'; var = 'CLDFRA'
            elif i == 1: file = f'{DIR_DATA}/anom_HFX_d02_2019_2020_dy_EXP10.nc'; var = 'HFX'
            else:        file = f'{DIR_DATA}/anom_LH_d02_2019_2020_dy_EXP10.nc'; var = 'LH'
            
            ax.add_geometries(SHP_NOLAGO.geometries(), crs=CRS, edgecolor='k', 
                               facecolor='none', alpha=1, linewidth=.7, zorder=2)
            extent = [-70.7, -68.3, -17, -14.7]

        # --- B. Carga y Corrección de Datos ---
        d1 = xr.open_dataset(file)[var]
        if j == 0: d1 = d1 - ska  # Aplicar la resta de ska solo a la fila de TSK
        
        # --- C. Configuración de Color ---
        mapa = 'RdBu_r' if ('anom' in file or 'EXP10-EXP8' in file) else 'jet'
        labe = '[%]' if 'CLDFRA' in var else '[W/m2]' if ('HFX' in var or 'LH' in var) else '[°C]'
        level = set_lim(var, file)

        # Plot Principal
        im = d1.plot(ax=ax, levels=level, cmap=mapa, extend='both', 
                     cbar_kwargs={"label": labe, "shrink": 0.8})

        # --- D. Estética y Cartografía ---
        ax.add_geometries(SHP_PERU.geometries(), crs=CRS, edgecolor='k', 
                           facecolor='none', alpha=1, linewidth=1, zorder=3)
        ax.set_extent(extent)
        
        # Títulos
        if j == 0:
            if i == 0:   ax.set_title('GMTns\nEVA_SIE')
            elif i == 1: ax.set_title('GMTns\nEVA_SIE_SST')
            else:        ax.set_title('b) - a)')
        else:
            ax.set_title(f'{var}_dif')

        # Título de letra (titus[nti])
        ax.set_title(f'{titus[nti]}', loc='left', fontweight='bold')
        nti += 1
        
        # Gridlines (Uso de tu función original)
        agrega_grid(i, j, 3, 2, ax)

plt.tight_layout()
fig.savefig(f'{OUT_DIR}/diferencias_lago_sst.png', dpi=100, bbox_inches='tight')
plt.show()