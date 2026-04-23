#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracción de series temporales WRF en puntos de estaciones observacionales
y cálculo de diferencias modelo-observación para validación.

Procesa precipitación (pr) y temperatura (t2m), comparando múltiples 
experimentos contra datos observacionales de estaciones meteorológicas.
"""

import os
import pandas as pd
import numpy as np
import xarray as xr
from glob import glob as gb

# ============================================================
# CONFIGURACIÓN
# ============================================================

# Experimentos a evaluar usando archivos creados con el script 01_ordena_wrf_files.py
EXPERIMENTOS = [e.split("/")[-1].split("_")[0] for e in gb("../data/nc_files/*t2m.png")]  #['EXP0', 'EXP1']

# Rutas de datos
RUTA_CSV = '../input_csv'          # Observaciones estacionales
RUTA_NC = '../data/nc_files'       # Salidas WRF procesadas
RUTA_SALIDA = '../data/csv_files'  # Resultados de validación

os.makedirs(RUTA_SALIDA, exist_ok=True)

# ============================================================
# FUNCIONES
# ============================================================

def extrae_crea(archivo_nc, df_estaciones, experimento, variable):
    """
    Extrae valores del modelo en coordenadas de estaciones observacionales
    y calcula bias (modelo - observación) para el periodo DJF 2019-2020.
    
    DJF se selecciona por ser el núcleo de la estación de lluvias en el 
    dominio de estudio, donde los sesgos del modelo suelen ser más críticos.
    """
    
    # Cargar simulación y recortar a periodo de validación
    ds = xr.open_dataset(archivo_nc)
    ds_djf = ds.sel(time=slice('2019-12', '2020-02'))
    
    # Promedio espacial sobre DJF (para temperatura) o acumulado (para pr)
    # Nota: La función asume que pr ya viene como acumulado diario en el nc
    ds_media = ds_djf.mean(dim='time')
    
    # Extracción por estación: nearest-neighbor por resolución gruesa del modelo
    lons_mod, lats_mod, vals_mod = [], [], []
    
    for _, fila in df_estaciones.iterrows():
        punto = ds_media.sel(lon=fila.lon, lat=fila.lat, method='nearest')
        
        lons_mod.append(float(punto.lon))
        lats_mod.append(float(punto.lat))
        vals_mod.append(float(punto[variable]))
    
    # Guardar valores del modelo y calcular bias
    col_mod = f"{experimento}_{variable}"
    col_bias = f"{experimento}-OBS"
    
    df_estaciones[col_mod] = vals_mod
    df_estaciones[col_bias] = df_estaciones[col_mod] - df_estaciones[variable]
    
    return df_estaciones


# ============================================================
# PIPELINE DE VALIDACIÓN
# ============================================================

def main():
    
    # Variables a validar: pr (acumulada) y t2m (media)
    for variable in ['pr', 't2m']:
        
        print(f"\n→ Validando: {variable}")
        
        # Cargar observaciones estacionales
        archivo_obs = f"{RUTA_CSV}/{variable}_complete_stations.csv"
        df_obs = pd.read_csv(archivo_obs)
        df_resultado = df_obs.copy()
        
        # Extraer cada experimento y calcular bias
        for exp in EXPERIMENTOS:
            patron = f"{RUTA_NC}/{exp}*{variable}*.nc"
            archivo_mod = gb(patron)[0]
            
            print(f"  {exp}: {os.path.basename(archivo_mod)}")
            df_resultado = extrae_crea(archivo_mod, df_resultado, exp, variable)
        
        # Exportar matriz de validación: obs + mod + bias por experimento
        archivo_salida = f"{RUTA_SALIDA}/{variable}_dif_AllStation.csv"
        df_resultado.to_csv(archivo_salida, index=False)
        print(f"  ✓ Guardado: {archivo_salida}")
    
    print("\n✓ Validación completada")


if __name__ == "__main__":
    main()