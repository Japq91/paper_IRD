"""
plot_utils.py — Funciones auxiliares para el plot de viento y humedad.

Módulo importado por el script de ploteo (plot_wind_mean.py).
Contiene:
  - agrega_grid      : añade líneas de grilla y etiquetas a los ejes cartopy.
  - carga_campo      : lee un NetCDF y devuelve las variables necesarias.
  - plot_fondo       : dibuja el campo escalar (humedad) como pcolor/contourf.
  - plot_vectores    : superpone los vectores de viento ponderado por humedad.
  - agrega_geometrias: añade shapefiles de costa/lago sobre el mapa.
  - agregar_colorbars: posiciona y dibuja las dos barras de color del panel.
  - agregar_leyendas : añade las quiverkeys con las unidades de referencia.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import xarray as xr
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader

# ── Proyección común ──────────────────────────────────────────────────────────
CRS = ccrs.PlateCarree()


# ─────────────────────────────────────────────────────────────────────────────
def agrega_grid(ax, i, j, numcol, numrow, xticks, yticks):
    """
    Control de etiquetas:
    - Longitud (bottom): Solo si es la última fila (j == numrow - 1).
    - Latitud (left): Solo si es la primera columna (i == 0).
    """
    # Importante: draw_labels debe ser True para que las propiedades funcionen
    grd = ax.gridlines(xlocs=xticks, ylocs=yticks, color='gray', alpha=0.9,
                       linewidth=1, linestyle='--', draw_labels=True)
    # Desactivamos etiquetas superiores y derechas siempre
    grd.top_labels = False
    grd.right_labels = False    
    # Solo activa etiquetas de la izquierda si es la columna 0
    grd.left_labels = (i == 0)    
    # Solo activa etiquetas de abajo si es la última fila    
    grd.bottom_labels = (j == numrow - 1)

# ─────────────────────────────────────────────────────────────────────────────
def carga_campo(ruta_nc: str) -> tuple:
    """
    Lee un NetCDF de viento y devuelve las variables U10, V10, Q2,
    así como las coordenadas lat/lon.

    Parámetros
    ----------
    ruta_nc : str  Ruta completa al archivo NetCDF (prom o anom).

    Retorna
    -------
    u, v, q   : DataArrays de viento zonal, meridional y humedad específica.
    lons, lats: DataArrays de longitud y latitud.
    """
    ds   = xr.open_dataset(ruta_nc)
    u    = ds["U10"]
    v    = ds["V10"]
    q    = ds["Q2"]
    lons = ds["XLONG"][0,:] # if "lon" in ds else ds["XLONG"].isel(Time=0)
    lats = ds["XLAT"][:,0] # if "lat" in ds else ds["XLAT"].isel(Time=0)
    return u, v, q, lons, lats


# ─────────────────────────────────────────────────────────────────────────────
def plot_fondo(ax, lons: xr.DataArray, lats: xr.DataArray,
               q: xr.DataArray, es_anomalia: bool):
    """
    Dibuja el campo escalar de humedad específica (Q2 * 1000 → g/kg)
    como fondo coloreado sobre el eje cartopy.

    Para promedios usa colormap 'Greens' con niveles 3-19 g/kg.
    Para anomalías usa 'RdBu_r' normalizado entre -1 y 1 g/kg.

    Parámetros
    ----------
    ax          : eje cartopy de destino.
    lons, lats  : coordenadas 2-D del campo.
    q           : DataArray de humedad específica (kg/kg).
    es_anomalia : bool, True si el archivo es de anomalía.

    Retorna
    -------
    fondo : objeto QuadMesh/ContourSet de matplotlib (para la colorbar).
    """
    q_gkg = q * 1000  # convertir a g/kg

    dps = xr.Dataset(
        {"newvar": (("lat", "lon"), q_gkg.values)},
        coords={"lat": lats.values, "lon": lons.values}
    )

    if es_anomalia:
        norm  = matplotlib.colors.Normalize(vmin=-1, vmax=1)
        fondo = dps["newvar"].plot(
            ax=ax, add_colorbar=False,
            cmap=cm.RdBu_r.resampled(10), norm=norm
        )
    else:
        niveles = np.arange(3, 21, 2)
        fondo   = dps["newvar"].plot(
            ax=ax, add_colorbar=False,
            cmap="Greens", levels=niveles
        )
    return fondo


# ─────────────────────────────────────────────────────────────────────────────
def plot_vectores(ax, lons: xr.DataArray, lats: xr.DataArray,
                  u: xr.DataArray, v: xr.DataArray,
                  q: xr.DataArray, es_anomalia: bool, m: int = 10):
    """
    Superpone vectores de flujo de humedad (u*q, v*q) sobre el eje cartopy.

    La escala es diferente para promedios (c1=0.01) y anomalías (c1=1),
    de modo que los vectores sean legibles en ambos casos.

    Parámetros
    ----------
    ax          : eje cartopy de destino.
    lons, lats  : coordenadas 2-D.
    u, v        : componentes de viento (m/s).
    q           : humedad específica (kg/kg).
    es_anomalia : bool, controla la escala de los vectores.
    m           : paso de submuestreo espacial (cada m puntos).

    Retorna
    -------
    Q : objeto Quiver de matplotlib (para la quiverkey).
    """
    # flujo en m·g/(s·kg)
    flu_u = (u * q * 1000).values
    flu_v = (v * q * 1000).values

    # ESCALA ORIGINAL: 
    # c1 = 0.01 para promedios, c1 = 1 para anomalías
    c1 = 1 if es_anomalia else 0.01
    valor_scale = 1 / c1

    Q = ax.quiver(
        lons[::m], lats[::m],
        flu_u[::m, ::m], flu_v[::m, ::m],
        transform=CRS,
        scale=valor_scale, 
        width=0.01,         # Tu width original
        scale_units='xy',   # Tu unidad original
        angles='xy'         # Tu ángulo original
    )
    return Q

# ─────────────────────────────────────────────────────────────────────────────
def agrega_geometrias(ax, ruta_shapes: str) -> None:
    """
    Agrega los shapefiles de contorno de país (peru) y lago (Titicaca)
    sobre el mapa como líneas sin relleno.

    Parámetros
    ----------
    ax          : eje cartopy de destino.
    ruta_shapes : str, directorio raíz donde están los .shp.
    """
    peru = Reader(f"{ruta_shapes}/peru2.shp")
    lago = Reader(f"{ruta_shapes}/lago_titikk_2022.shp")

    ax.add_geometries(
        peru.geometries(), CRS,
        edgecolor="k", facecolor="none", alpha=0.9, linewidth=0.7, zorder=2
    )
    ax.add_geometries(
        lago.geometries(), CRS,
        edgecolor="k", facecolor="none", alpha=0.5, linewidth=1, zorder=3
    )


# ─────────────────────────────────────────────────────────────────────────────
def agregar_colorbars(fig, fondo_prom, fondo_anom) -> None:
    """
    Añade dos barras de color al panel completo:
      - Izquierda (x≈0.05): colorbar para anomalías [g/kg].
      - Centro-izquierda (x≈0.15): colorbar para promedios [g/kg].

    Parámetros
    ----------
    fig        : figura matplotlib padre.
    fondo_prom : objeto retornado por plot_fondo() para la fila de promedios.
    fondo_anom : objeto retornado por plot_fondo() para la fila de anomalías.
    """
    ax_prom = fig.add_axes([0.15, 0.09, 0.03, 0.3])
    fig.colorbar(fondo_prom, cax=ax_prom, label="[g/kg]", orientation="vertical")

    ax_anom = fig.add_axes([0.05, 0.09, 0.03, 0.3])
    fig.colorbar(fondo_anom, cax=ax_anom, label="[g/kg]", orientation="vertical")


# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def agregar_leyendas(fig, q_anom, q_prom) -> None:
    """
    Posiciona las leyendas usando tus magnitudes originales.
    q_prom: promedio (U=25)
    q_anom: anomalía (U=0.5)
    """
    # 1. Referencia para Promedios (Tu valor original: 25)
    # x=0.165 para que caiga sobre la barra verde
    fig.quiverkey(
        q_prom, 0.165, 0.42, 25, 
        label=r"$25 \frac{m \cdot g}{s \cdot kg}$",
        labelpos="N", coordinates="figure"
    )

    # 2. Referencia para Anomalías (Tu valor original: 0.5)
    # x=0.065 para que caiga sobre la barra azul-roja
    fig.quiverkey(
        q_anom, 0.065, 0.42, 0.5, 
        label=r"$0.5 \frac{m \cdot g}{s \cdot kg}$",
        labelpos="N", coordinates="figure"
    )