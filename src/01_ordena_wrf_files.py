#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de post-procesamiento de salidas WRF (Weather Research and Forecasting).
Convierte archivos NetCDF crudos a formatos estandarizados con coordenadas 
temporales, latitud y longitud, y genera figuras de verificación mensuales.

Autor: japaredesq@gmail.com
Fecha: 2026-04-22
"""

# ============================================================
# IMPORTS
# ============================================================
import os
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from glob import glob as gb

# ============================================================
# CONFIGURACIÓN DEL EXPERIMENTO
# ============================================================

# Nombre del experimento (debe coincidir con la carpeta de entrada)
# Ejemplos válidos: "EXP5", "EXP8", etc.
EXP = 'EXP1'

# Rutas de entrada/salida (relativas al directorio de ejecución)
RUTA_ENTRADA = '../input_nc'      # Datos WRF brutos
RUTA_SALIDA = '../data/nc_files'  # Resultados procesados

# Crear directorio de salida si no existe
os.makedirs(RUTA_SALIDA, exist_ok=True)

# ============================================================
# FUNCIONES PRINCIPALES
# ============================================================

def ordena_wrf_file(archivo, nombre_salida, variable_wrf):
    """
    Estandariza un archivo NetCDF de WRF renombrando variables y coordenadas.
    
    Parámetros:
    -----------
    archivo : str
        Ruta al archivo NetCDF de entrada (salida WRF).
    nombre_salida : str
        Nombre estandarizado para la variable (ej: 'pr', 't2m').
    variable_wrf : str
        Nombre exacto de la variable dentro del archivo WRF (ej: 'T2', 'pr').
    
    Retorna:
    --------
    xr.Dataset
        Dataset con coordenadas renombradas: time, lat, lon.
    
    Guarda:
    -------
    Archivo NetCDF en RUTA_SALIDA con formato: {EXP}_{nombre_salida}_d02_dy.nc
    """
    
    # Abrir dataset y extraer la variable de interés
    ds = xr.open_dataset(archivo)[variable_wrf]
    
    # Extraer coordenadas geográficas (asume malla regular WRF d02)
    latitudes = ds.XLAT[:, 0].values   # Vector de latitudes (dimensión Y)
    longitudes = ds.XLONG[0, :].values # Vector de longitudes (dimensión X)
    
    # Generar eje temporal: desde Nov-2019, frecuencia diaria
    # NOTA: El número de periodos se infiere de la dimensión temporal del archivo
    n_tiempos = len(ds.XTIME)
    fechas = pd.date_range(start='2019-11', freq='D', periods=n_tiempos)
    
    # Crear nuevo dataset con coordenadas estandarizadas (CF-convention friendly)
    datos = ds.values
    ds_estandar = xr.Dataset(
        {nombre_salida: (("time", "lat", "lon"), datos)},
        coords={
            "lat": latitudes,
            "lon": longitudes,
            "time": fechas
        }
    )
    
    # Guardar resultado
    nombre_archivo = f"{RUTA_SALIDA}/{EXP}_{nombre_salida}_d02_dy.nc"
    ds_estandar.to_netcdf(nombre_archivo)
    print(f"  ✓ Guardado: {nombre_archivo}")
    
    return ds_estandar


def plot_prueba(dataset, variable, experimento):
    """
    Genera figuras de verificación con promedios o sumas mensuales.
    
    Parámetros:
    -----------
    dataset : xr.Dataset
        Dataset procesado con coordenadas time, lat, lon.
    variable : str
        Nombre de la variable a visualizar.
    experimento : str
        Identificador del experimento para el título/filename.
    
    Guarda:
    -------
    Imagen PNG en RUTA_SALIDA con formato: {experimento}_{variable}.png
    """
    
    # Agregación temporal según tipo de variable:
    # - Temperatura (t2m): promedio mensual (estado medio)
    # - Precipitación (pr): suma mensual (acumulado)
    if 't' in variable:
        mensual = dataset.groupby('time.month').mean(dim='time')
        titulo_agregacion = "Promedio mensual"
    else:
        mensual = dataset.groupby('time.month').sum(dim='time')
        titulo_agregacion = "Suma mensual"
    
    # Crear figura con paneles mensuales (faceting)
    fig = mensual[variable].plot(
        x="lon", 
        y="lat", 
        col="month", 
        col_wrap=4,        # 4 columnas por fila (3 filas para 12 meses)
        cmap='viridis',    # Colormap perceptualmente uniforme
        robust=True        # Ignora outliers para mejor contraste
    )
    
    # Ajustar título general de la figura
    plt.suptitle(f"{experimento} | {variable.upper()} | {titulo_agregacion}", 
                 y=1.02, fontsize=12)
    
    # Guardar figura
    ruta_figura = f"{RUTA_SALIDA}/{experimento}_{variable}.png"
    plt.savefig(ruta_figura, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ Figura guardada: {ruta_figura}")


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def main():
    """Pipeline de procesamiento WRF."""
    
    # Diccionario de mapeo: nombre_estandar -> nombre_variable_wrf
    # Esto permite procesar múltiples variables en un solo bucle
    VARIABLES = {
        'pr': 'pr',    # Precipitación (ya en formato correcto)
        't2m': 'T2'    # Temperatura a 2m (nombre nativo WRF)
    }
    
    # Archivo de entrada del experimento
    archivo_input = f"{RUTA_ENTRADA}/{EXP}/wrf_d02_dy_{EXP}.nc"
    
    print(f"{'='*50}")
    print(f"Procesando experimento: {EXP}")
    print(f"Archivo fuente: {archivo_input}")
    print(f"{'='*50}\n")
    
    # Verificar existencia del archivo
    if not os.path.exists(archivo_input):
        raise FileNotFoundError(f"No se encontró: {archivo_input}")
    
    # Procesar cada variable
    for var_estandar, var_wrf in VARIABLES.items():
        print(f"\n→ Procesando variable: {var_estandar}")
        
        # Paso 1: Estandarizar NetCDF
        ds = ordena_wrf_file(archivo_input, var_estandar, var_wrf)
        
        # Paso 2: Generar figura de verificación
        plot_prueba(ds, var_estandar, EXP)
    
    print(f"\n{'='*50}")
    print("✓ Procesamiento completado exitosamente")
    print(f"Resultados en: {os.path.abspath(RUTA_SALIDA)}")
    print(f"{'='*50}")


# Punto de entrada del script
if __name__ == "__main__":
    main()