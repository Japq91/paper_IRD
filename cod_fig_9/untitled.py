import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# LIBRERÍAS
# =============================================================================
print('Cargando librerías...')
from cartopy.io.shapereader import Reader
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from glob import glob as gb
import cartopy.crs as ccrs
from matplotlib.gridspec import GridSpec
from matplotlib import cm

# Configuración global de matplotlib
plt.rcParams.update({'font.size': 10})
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def agregar_grid(ax, xticks, yticks, i, j, nrows, ncols):
    """
    Añade líneas de grid a un subplot, controlando qué etiquetas se muestran
    según la posición en la matriz de subplots.

    Parámetros:
    -----------
    ax : cartopy.mpl.geoaxis.GeoAxesSubplot
        Eje al que añadir la cuadrícula.
    xticks, yticks : array-like
        Posiciones de las líneas de grid.
    i, j : int
        Índices de columna y fila (0-based).
    nrows, ncols : int
        Número total de filas y columnas.
    """
    # Por defecto sin etiquetas
    draw_left = draw_down = draw_top = draw_right = False

    # Primera columna y no última fila -> etiquetas izquierda
    if i == 0 and j < nrows - 1:
        draw_left = True
    # Última fila y columna >0 -> etiquetas abajo
    elif j == nrows - 1 and i > 0:
        draw_down = True
    # Primera columna y última fila -> etiquetas izquierda y abajo
    elif i == 0 and j == nrows - 1:
        draw_left = draw_down = True
    # Para el resto no se dibujan etiquetas (solo líneas)

    grd = ax.gridlines(xlocs=xticks, ylocs=yticks,
                       color='gray', alpha=0.99,
                       draw_labels=False,
                       linewidth=1, linestyle='--')
    # Actualizar las etiquetas según lo decidido
    grd.left_labels = draw_left
    grd.bottom_labels = draw_down
    grd.top_labels = draw_top
    grd.right_labels = draw_right


def paso_1(archivo, ax, m=10):
    """
    Lee un archivo NetCDF, calcula el flujo de humedad (u*Q2*1000, v*Q2*1000)
    y genera un plot con el campo base (newvar) y vectores de viento.

    Parámetros:
    -----------
    archivo : str
        Ruta del archivo NetCDF.
    ax : cartopy.mpl.geoaxis.GeoAxesSubplot
        Eje donde dibujar.
    m : int
        Paso para submuestrear los vectores (cada m puntos).

    Retorna:
    --------
    fondo : matplotlib.contour.QuadContourSet
        Objeto del gráfico de contornos (para la barra de color).
    qv : matplotlib.quiver.Quiver
        Objeto de los vectores (para la clave de la flecha).
    """
    # Abrir dataset
    dset = xr.open_dataset(archivo)

    # Extraer variables
    u10 = dset['U10']
    v10 = dset['V10']
    q2 = dset['Q2']          # humedad específica en kg/kg
    # Campo base a representar (normalmente una variable 'newvar')
    fondo_var = dset['newvar']

    # Obtener coordenadas lon/lat (asumiendo que existen)
    lon = dset['lon'].values
    lat = dset['lat'].values

    # Calcular flujo de humedad (multiplicado por 1000 para pasar a g/kg)
    u_flux = u10 * q2 * 1000
    v_flux = v10 * q2 * 1000

    # Configuración de colormap y niveles según si es anomalía o no
    if 'anom' in archivo:
        # Para anomalías: colormap divergente RdBu_r, niveles automáticos
        norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)
        fondo = fondo_var.plot(ax=ax, add_colorbar=False,
                               cmap=cm.RdBu_r.resampled(10), norm=norm)
        cscale = 1.0          # escala para flechas en anomalías (sin reescalado extra)
    else:
        # Para promedios: colormap secuencial Greens, niveles fijos
        niveles = np.arange(3, 21, 2)   # de 3 a 19 cada 2
        fondo = fondo_var.plot(ax=ax, add_colorbar=False,
                               cmap='Greens', levels=niveles)
        cscale = 0.01         # factor para ajustar longitud de flechas (valores originales pequeños)

    # Dibujar vectores (submuestreados cada m puntos)
    qv = ax.quiver(lon[::m], lat[::m],
                   u_flux[::m, ::m], v_flux[::m, ::m],
                   transform=ccrs.PlateCarree(),
                   scale=1/cscale,      # escala inversa al factor elegido
                   width=0.01,
                   scale_units='xy',
                   angles='xy')

    # Añadir geometrías de Perú y lago Titicaca
    ax.add_geometries(peru.geometries(), crs=crs,
                      edgecolor='k', facecolor='none',
                      alpha=0.9, linewidth=0.7, zorder=2)
    ax.add_geometries(lago.geometries(), crs=crs,
                      edgecolor='k', facecolor='none',
                      alpha=0.5, linewidth=1, zorder=3)

    return fondo, qv


def paso_2(ax, qv_prom, qv_anom, fondo_prom, fondo_anom, fig):
    """
    Añade las claves de flechas (quiverkey) y las barras de color a la figura.

    Parámetros:
    -----------
    ax : cartopy.mpl.geoaxis.GeoAxesSubplot
        Último eje creado (se usa como referencia para las claves).
    qv_prom, qv_anom : matplotlib.quiver.Quiver
        Objetos quiver de los paneles de promedios y anomalías.
    fondo_prom, fondo_anom : matplotlib.contour.QuadContourSet
        Objetos de contorno para extraer los límites de color.
    fig : matplotlib.figure.Figure
        Figura a la que añadir las barras de color.
    """
    # Clave para el panel de promedios (escala grande: 25)
    ax.quiverkey(qv_prom, -4.3, -0.35, 25,
                 label=r'$25\ \frac{m\cdot g}{s\cdot kg}$',
                 labelpos='N', coordinates='axes', zorder=10)
    # Clave para el panel de anomalías (escala pequeña: 0.5)
    ax.quiverkey(qv_anom, -3.7, 0.9, 0.5,
                 label=r'$0.5\ \frac{m\cdot g}{s\cdot kg}$',
                 labelpos='N', coordinates='axes', zorder=10)

    # Barras de color verticales, una al lado de la otra
    cax_prom = fig.add_axes([0.05, 0.09, 0.03, 0.3])   # izquierda: promedios
    cax_anom = fig.add_axes([0.15, 0.09, 0.03, 0.3])   # derecha: anomalías

    fig.colorbar(fondo_prom, cax=cax_prom, label='[g/kg]', orientation='vertical')
    fig.colorbar(fondo_anom, cax=cax_anom, label='[g/kg]', orientation='vertical')

    fig.tight_layout()


# =============================================================================
# CONFIGURACIÓN DE RUTAS Y DATOS GEOGRÁFICOS
# =============================================================================

# Ruta base (ajústala según tu sistema)
ri = "/home/jap/IRD/"
ro = f"{ri}GRAFICAS/out/"

# Shapefiles
shapes_r = "/home/jap/SHAPES/"
lago = Reader(f"{shapes_r}lago_titikk_2022.shp")
peru = Reader(f"{shapes_r}peru2.shp")

# Proyección cartográfica y ticks de la cuadrícula
crs = ccrs.PlateCarree()
xticks = np.arange(-77, -64.5, 1)
yticks = np.arange(-23, -10, 1)

# Archivo topográfico (aunque no se usa directamente, se carga por si acaso)
nctopo = xr.open_dataset(f"{ri}GRAFICAS/nc_topo/EXP1_HGT_d02.nc")

# Experimentos: índices numéricos para los archivos y nombres para los títulos
mods = [0, 1, 5, 8, 10]
mods2 = ['GMTs_MOD30_SOM', 'GMTns_MOD30_SOM', 'GMTns_EVA_SOM',
         'GMTns_EVA_SIE', 'GMTns_EVA_SIE_SST']
lplt3 = ['a)', 'b)', 'c)', 'd)', 'e)', 'f)', 'g)', 'h)', 'i)', 'j)']

# =============================================================================
# CREACIÓN DE LA FIGURA PRINCIPAL
# =============================================================================

fig = plt.figure(figsize=(12, 5.3))
gs = GridSpec(nrows=2, ncols=5)

n = 0   # índice global para etiquetas a), b), ...
# Primer bucle sobre tipos: 'prom' (promedio) fila superior, 'anom' (anomalía) fila inferior
for j, tipo in enumerate(['prom', 'anom']):
    for i, (mod, mod2) in enumerate(zip(mods, mods2)):
        # Saltamos la combinación i=0, j=1 (primer experimento en anomalías)
        if i == 0 and j == 1:
            continue

        ax = fig.add_subplot(gs[j, i], projection=crs)
        archivo = f"{ri}GRAFICAS/cods/viento/{tipo}_wind_EXP{mod}.nc"

        # Llamada a la función de dibujo
        if j == 0:   # fila de promedios
            fondo, qv = paso_1(archivo, ax, m=10)
            # Guardamos los objetos del último panel de promedios (para la barra/clave)
            if i == 4:   # último subplot de la fila
                fondo_prom_global = fondo
                qv_prom_global = qv
            ax.set_title(mod2)                     # título del experimento
        else:         # fila de anomalías
            fondo, qv = paso_1(archivo, ax, m=10)
            if i == 4:
                fondo_anom_global = fondo
                qv_anom_global = qv
            # Título combinado: letra del experimento anterior y actual (como en original)
            ax.set_title(f"{lplt3[i][:1]} - {lplt3[i-1][:1]}", loc='center')

        # Etiqueta izquierda global (a), b), ...) y cuadrícula
        ax.set_title(lplt3[n], loc='left')
        agregar_grid(ax, xticks, yticks, i, j, nrows=2, ncols=5)
        n += 1

# Añadir las claves de flechas y las barras de color usando los últimos objetos
paso_2(ax, qv_prom_global, qv_anom_global,
       fondo_prom_global, fondo_anom_global, fig)

# Guardar la figura (ajusta la ruta de salida según necesites)
fig.savefig(f"{ro}monmean_uvQ2_meanday_24abr2024_v2.png",
            dpi=400, bbox_inches='tight')
plt.show()