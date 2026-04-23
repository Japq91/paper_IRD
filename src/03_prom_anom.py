#!/usr/bin/env python
# coding: utf-8

"""
Script para calcular la media estacional (DJF 2019-2020) de precipitación o temperatura
a partir de salidas WRF, y las anomalías entre experimentos.
Autor: japaredesq@gmail.com
Fecha: 23042026
"""

import xarray as xr
from pathlib import Path

# ============================================================================
# Configuración del usuario
# ============================================================================
VAR = 't2m'                     # Variable: 'pr' (precipitación) o 't2m' (temperatura a 2 m)
EXPERIMENTOS = [0, 1, 5, 8, 10] # IDs de los experimentos WRF

# Rutas (usando pathlib para compatibilidad entre SO)
RUTA_NC = Path('../data/nc_files')                # Archivos NetCDF originales
RUTA_SALIDA = Path(f'../data/mean_anom_files/{VAR}') # Donde guardar medias y anomalías

# Crear directorio de salida si no existe
RUTA_SALIDA.mkdir(parents=True, exist_ok=True)
print(f"Directorio de salida: {RUTA_SALIDA.resolve()}")

# ============================================================================
# Funciones auxiliares
# ============================================================================
def media_djf(archivo):
    """
    Calcula la media temporal para el trimestre diciembre-enero-febrero (DJF).
    
    Parámetros
    ----------
    archivo : Path o str
        Ruta al archivo NetCDF con dimensión 'time'.
    
    Retorna
    -------
    xarray.Dataset
        Dataset con la media temporal en el período DJF 2019-2020.
    """
    ds = xr.open_dataset(archivo)
    # Seleccionar los meses de diciembre (2019), enero y febrero (2020)
    ds_djf = ds.sel(time=slice('2019-12', '2020-02'))
    media = ds_djf.mean('time', keep_attrs=True)
    # Conservar atributos globales y de variable
    media.attrs['description'] = f'Media estacional DJF para {archivo.name}'
    return media

def calcular_anomalia(archivo_mod, archivo_ref):
    """
    Calcula la anomalía (diferencia) entre dos experimentos: mod - ref.
    
    Parámetros
    ----------
    archivo_mod : Path o str
        Archivo del experimento (minuendo).
    archivo_ref : Path o str
        Archivo del experimento de referencia (sustraendo).
    
    Retorna
    -------
    xarray.Dataset
        Dataset con la anomalía (mod - ref).
    """
    ds_mod = xr.open_dataset(archivo_mod)
    ds_ref = xr.open_dataset(archivo_ref)
    anom = ds_mod - ds_ref
    anom.attrs['description'] = f'Anomalía: {archivo_mod.stem} - {archivo_ref.stem}'
    return anom

# ============================================================================
# Cálculo de medias estacionales
# ============================================================================
print("\n--- Calculando medias estacionales DJF ---")

for exp in EXPERIMENTOS:
    # Nombre del archivo de entrada: ej. "../data/nc_files/EXP0_pr_d02_dy.nc"
    archivo_entrada = RUTA_NC / f'EXP{exp}_{VAR}_d02_dy.nc'
    
    if not archivo_entrada.exists():
        print(f"  [ADVERTENCIA] No existe {archivo_entrada}, se omite.")
        continue
    
    # Archivo de salida: "../data/mean_nc_files/t2m/prom_EXP0.nc"
    archivo_salida = RUTA_SALIDA / f'prom_EXP{exp}.nc'
    
    print(f"  Procesando EXP{exp} -> {archivo_salida.name}")
    ds_media = media_djf(archivo_entrada)
    ds_media.to_netcdf(archivo_salida)    
    print(f"    Guardado: {archivo_salida}")

# ============================================================================
# Cálculo de anomalías (diferencias entre experimentos consecutivos)
# ============================================================================

print("\n--- Calculando anomalías (EXPn - EXP(n-1)) ---")
for i in range(1, len(EXPERIMENTOS)):
    mod_actual = EXPERIMENTOS[i]
    mod_prev   = EXPERIMENTOS[i-1]
    
    archivo_actual = RUTA_SALIDA / f'prom_EXP{mod_actual}.nc'
    archivo_prev   = RUTA_SALIDA / f'prom_EXP{mod_prev}.nc'
    archivo_anom   = RUTA_SALIDA / f'anom_EXP{mod_actual}.nc'
    
    print(f"  {mod_actual} - {mod_prev} -> {archivo_anom.name}")
    anom = calcular_anomalia(archivo_actual, archivo_prev)  # o tu función calcular_anomalia
    anom.to_netcdf(archivo_anom)
 
print("\n¡Proceso completado con éxito!")