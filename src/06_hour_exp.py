#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para procesar archivos NetCDF de salida de modelo WRF.
Calcula promedios diarios para periodos diurno y nocturno, y anomalías.

Autor: japaredesq@gmail.com
Fecha: 23/04/2026
"""

import os
import pandas as pd
import xarray as xr
from pathlib import Path

# ======================================================================
# 1. PARÁMETROS CONFIGURABLES
# ======================================================================
VAR = 'V10'#'Q2'  #"V10","U10"
RUTA_NC = Path('../input_nc')
RUTA_SALIDA = Path('../data/exp_hour_files')
MODS = [0, 1, 5, 8, 10]
PERIODOS = ['dia', 'noche']

FECHA_INICIO = '2019-12'
FECHA_FIN = '2020-02'
HORAS_DIA = range(8, 20)
HORAS_NOCHE = [h for h in range(24) if h not in HORAS_DIA]

SUFIJO_PROM = 'prom'
SUFIJO_ANOM = 'anom'

# ======================================================================
# 2. FUNCIONES DE PROCESAMIENTO
# ======================================================================

def limpia_exp(a2, var0):
    """ Reasigna coordenadas para simplificar el dataset de WRF. """
    lati = a2.XLAT[:, 0].values
    loni = a2.XLONG[0, :].values
    # Ajuste: se usa el tiempo del dataset original para mantener consistencia
    tiem = pd.date_range('2019-11', freq='D', periods=len(a2.XTIME))
    newdata = a2.values
    return xr.Dataset(
        {var0: (("time", "lat", "lon"), newdata)},
        coords={"lat": lati, "lon": loni, 'time': tiem}
    )

def prom_hr2dy(dataset, es_dia):
    """ Calcula el promedio según el periodo horario seleccionado. """
    d0 = dataset.sel(time=slice(FECHA_INICIO, FECHA_FIN))
    horas = HORAS_DIA if es_dia else HORAS_NOCHE
    return d0.sel(time=d0.time.dt.hour.isin(list(horas))).mean('time')

def calc_anom(file1, file2):
    """ Calcula la diferencia directa entre dos archivos NetCDF. """
    with xr.open_dataset(file1) as d1, xr.open_dataset(file2) as d2:
        return (d1 - d2).load()

# ======================================================================
# 3. EJECUCIÓN (MAIN)
# ======================================================================
RUTA_SALIDA.mkdir(parents=True, exist_ok=True)

# --- PASO A: Calcular promedios ---
for mod in MODS:
    archivo_entrada = RUTA_NC / f'EXP{mod}/vars_d02_hr.nc'
    
    if not archivo_entrada.exists():
        print(f'[!] Saltando: {archivo_entrada} (No existe)')
        continue

    print(f'>>> Procesando EXP{mod}: {archivo_entrada.name}')
    
    with xr.open_dataset(archivo_entrada) as ds_raw:
        ds_limpio = limpia_exp(ds_raw[VAR], VAR)
        
        for peri in PERIODOS:
            ds_prom = prom_hr2dy(ds_limpio, peri == 'dia')
            out_name = RUTA_SALIDA / f'{VAR}_{SUFIJO_PROM}_EXP{mod}_{peri}.nc'
            ds_prom.to_netcdf(out_name)
            print(f'    Guardado promedio: {out_name.name}')

# --- PASO B: Calcular anomalías ---
for i in range(1, len(MODS)):
    mod = MODS[i]
    mod_prev = MODS[i-1]
    
    for peri in PERIODOS:
        f_actual = RUTA_SALIDA / f'{VAR}_{SUFIJO_PROM}_EXP{mod}_{peri}.nc'
        f_prev = RUTA_SALIDA / f'{VAR}_{SUFIJO_PROM}_EXP{mod_prev}_{peri}.nc'
        
        if f_actual.exists() and f_prev.exists():
            print(f'>>> Anomalía: EXP{mod} - EXP{mod_prev} ({peri})')
            anom = calc_anom(f_actual, f_prev)
            f_anom = RUTA_SALIDA / f'{VAR}_{SUFIJO_ANOM}_EXP{mod}_{peri}.nc'
            anom.to_netcdf(f_anom)
            print(f'    Guardado anomalía: {f_anom.name}')

print("\nDONE! Procesamiento finalizado.")