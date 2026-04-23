#!/usr/bin/env python
# coding: utf-8

"""
Script para procesar datos horarios de PISCO, filtrando periodos de día y noche
y calculando el promedio temporal para el dominio del Lago Titicaca/Perú.

Autor: japaredesq@gmail.com
Fecha: 23/04/2026
"""

import xarray as xr
import numpy as np
import os
from pathlib import Path

# ============================================================================
# Configuración del usuario
# ============================================================================
# Se recomienda usar Pathlib para una gestión de rutas multiplataforma
RUTA_PISCO = Path('../input_nc/PISCO')        
RUTA_SALIDA = Path('../data/obs_hour_files') 

# Selección de archivo (puedes alternar comentando/descomentando)
# FILE_NAME = 'PISCOp_h_2019_2020.nc4'
FILE_NAME = 'PISCOp_h_non-DBC_2019_2020.nc4'

FILE_PATH = RUTA_PISCO / FILE_NAME

# ============================================================================
# Procesamiento
# ============================================================================

# 1. Verificación de existencia del archivo de entrada
if not FILE_PATH.exists():
    print(f"ERROR: No se encontró el archivo en {FILE_PATH}")
    # Aquí podrías salir del script o manejar la excepción
else:
    # Crear directorio de salida de forma segura
    RUTA_SALIDA.mkdir(parents=True, exist_ok=True)
    print(f"Directorio de salida listo: {RUTA_SALIDA.resolve()}")

    try:
        # 2. Carga optimizada: Usamos 'chunks' si el archivo es muy grande (Dask)
        # Seleccionamos la variable 'p' y el slice de tiempo inmediatamente
        with xr.open_dataset(FILE_PATH) as ds:
            print(f"Abriendo {FILE_NAME}...")
            d0 = ds['p'].sel(time=slice('2019-12', '2020-02')).load()

        # 3. Definición de periodos (Diccionario para mayor claridad estética)
        periodos = {
            'dia': np.arange(8, 20),      # 08:00 a 19:00
            'noche': np.delete(np.arange(24), np.arange(8, 20)) # El resto
        }

        for nombre, horas in periodos.items():
            # Construcción dinámica del nombre de salida basada en el input
            tag = "PISCO-nDBC" if "non-DBC" in FILE_NAME else "PISCO"
            ofile = RUTA_SALIDA / f'prom_pr_{tag}_{nombre}.nc'
            
            # 4. Filtrado y cálculo
            # .isin() espera una lista o array, pasamos 'horas' directamente
            d_filtrado = d0.sel(time=d0.time.dt.hour.isin(horas))
            d_promedio = d_filtrado.mean('time')
            
            # 5. Exportación
            d_promedio.to_netcdf(ofile)
            print(f"  Guardado en: {ofile.name}")

    except Exception as e:
        print(f"Ocurrió un error durante el procesamiento: {e}")

print("\nDONE!\nProcesado con éxito.")