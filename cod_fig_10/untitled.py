#!/usr/bin/python

import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from matplotlib.gridspec import GridSpec
import matplotlib.patches as patches

# --- CONFIGURACIÓN ESTÉTICA ---
plt.rcParams.update({'font.size': 10, 'font.family': 'serif'})
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

# --- RUTAS ---
ri = '/home/jap/IRD/OVAR'
shapes_r = '/home/jap/SHAPES'
DIR_NC = f'{ri}/clean'
OUT_DIR = f'{ri}/out'

DIR_SHAPES = '../input_shp'
DIR_DATA = '../data/lago_files'
OUT_DIR = '../figures'

# Recursos cartográficos
LAGO = Reader(f'{shapes_r}/lago_titikk_2022.shp')
PERU = Reader(f'{shapes_r}/peru2.shp')
CRS = ccrs.PlateCarree()
XTICKS, YTICS = np.arange(-77, -64.5, 1), np.arange(-23, -10, 1)

# --- FUNCIONES ---

def agrega_grid(ax, i, j, numcol, numrow):
    """ Etiquetas de longitud solo abajo, latitud solo izquierda. """
    grd = ax.gridlines(xlocs=XTICKS, ylocs=YTICS, color='gray', alpha=0.5, 
                       draw_labels=True, linewidth=1, linestyle='--')
    grd.top_labels = grd.right_labels = False
    grd.left_labels = (i == 0)
    grd.bottom_labels = (j == numrow - 1)

def add_cuadrado(ax):
    """ Resalta el área de estudio con un cuadro punteado. """
    square = patches.Rectangle((-69.7, -16), 0.4, 0.5, edgecolor='k', 
                               facecolor='none', lw=1.5, ls='--', zorder=5)
    ax.add_patch(square)

def paso_1(data, ax, var, tipo):
    """ Maneja el ploteo y los niveles según variable y experimento. """
    if tipo == 'anom':
        mapa = 'RdBu_r'
        leve = np.linspace(-.1, .1, 11) if 'ALBEDO' in var else np.linspace(-40, 40, 11)
    else:
        mapa = 'jet'
        leve = np.linspace(0, 1, 11) if 'ALBEDO' in var else np.linspace(-20, 160, 10)

    # Plot principal
    im = data.plot(ax=ax, add_colorbar=True, cmap=mapa, levels=leve, 
                   cbar_kwargs={'shrink': 0.8, 'label': ''})
    
    # Capas cartográficas
    ax.add_geometries(PERU.geometries(), crs=CRS, edgecolor='k', facecolor='none', linewidth=.7, zorder=2)
    ax.add_geometries(LAGO.geometries(), crs=CRS, edgecolor='k', facecolor='none', alpha=0.5, linewidth=1, zorder=3)
    
    ax.set_extent([-70.7, -68.3, -17, -14.7]) 
    return im

# --- EJECUCIÓN DEL PLOT ---

fig = plt.figure(figsize=(12, 10))
gs = GridSpec(nrows=3, ncols=3, hspace=0.3, wspace=0.2)
lplt3 = ['a)', 'b)', 'c)', 'd)', 'e)', 'f)', 'g)', 'h)', 'i)']
n = 0

for j, var_name in enumerate(['LH', 'HFX', 'ALBEDO']):
    for i, tipo_exp in enumerate(['prom', 'prom', 'anom']):
        # Selección de experimento
        mod = 5 if i == 1 else 1
        
        # Lógica de títulos
        if i == 0: ntit = 'GMTns_MOD30_SOM'
        elif i == 1: ntit = 'GMTns_EVA_SOM'
        else: ntit = f'{lplt3[n-1][0]} - {lplt3[n-2][0]}' # Ejemplo: b) - a)

        # Carga de datos
        path_nc = f'{DIR_NC}/{tipo_exp}_{var_name}_d02_2019_2020_dy_EXP{mod}.nc'
        
        try:
            ds = xr.open_dataset(path_nc)[var_name]
            
            # Cálculo de anomalía manual para la tercera columna
            if i == 0: da_ref1 = ds.copy()
            elif i == 1: da_ref5 = ds.copy()
            else: ds = da_ref5 - da_ref1
            
            ax = fig.add_subplot(gs[j, i], projection=CRS)
            paso_1(ds, ax, var_name, tipo_exp)
            
            # Títulos y etiquetas de fila
            ax.set_title(ntit, fontsize=10)
            ax.set_title(lplt3[n], loc='left', fontweight='bold')
            
            if i == 0:
                row_labels = {'LH': 'Latent Heat (W/m²)', 'HFX': 'Sensible Heat (W/m²)', 'ALBEDO': 'ALBEDO'}
                ax.text(-71.1, -15.85, row_labels[var_name], rotation=90, 
                        va='center', fontweight='bold', fontsize=11)

            agrega_grid(ax, i, j, 3, 3)
            add_cuadrado(ax)
            n += 1
            
        except FileNotFoundError:
            print(f"Archivo no encontrado: {path_nc}")

# Guardado final
fig.savefig(f'{OUT_DIR}/v3_9plots_final.png', dpi=400, bbox_inches='tight')
plt.show()