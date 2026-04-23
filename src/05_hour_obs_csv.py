#!/usr/bin/env python
# coding: utf-8

"""
Script para consolidar metadatos de estaciones con promedios de temperatura/precipitación
por periodos (día/noche).

Autor: japaredesq@gmail.com
Fecha: 23/04/2026
"""

import pandas as pd
from pathlib import Path

# ============================================================================
# Configuración del usuario
# ============================================================================
RUTA_CSV = Path('../input_csv')        
RUTA_SALIDA = Path('../data/csv_files') 

var = 't2m'  # 'pr' o 't2m'

# ============================================================================
# Procesamiento
# ============================================================================

# 1. Preparar salida
RUTA_SALIDA.mkdir(parents=True, exist_ok=True)

# 2. Cargar archivo base con metadatos
# Usamos index_col=0 para evitar el 'Unnamed: 0' desde la carga
file_base = RUTA_CSV / f'{var}_all_experimentos.csv'

try:
    print(f"Cargando archivo base: {file_base.name}")
    df_base = pd.read_csv(file_base, index_col=0)
    
    # Seleccionamos solo las columnas necesarias para el reporte final
    columnas_metadatos = ['est', 'alt', 'lon', 'lat', var]
    df_final = df_base[columnas_metadatos].copy()

    # 3. Consolidar periodos (día y noche)
    for peri in ['dia', 'noche']:
        file_peri = RUTA_CSV / f'{var}_{peri}_mean.csv'
        
        if file_peri.exists():
            print(f"  Procesando periodo: {peri}...")
            # Leer periodo y renombrar columna inmediatamente
            d_peri = pd.read_csv(file_peri, index_col=0)
            
            # Unimos usando 'left join' para mantener las estaciones de la base
            # y usamos el nombre del periodo como nombre de columna
            df_final[peri] = d_peri.iloc[:, 0] # Toma la primera columna de datos
        else:
            print(f"  [!] Advertencia: No se encontró {file_peri.name}")

    # 4. Limpieza final y exportación
    # Solo eliminamos filas si no tienen datos en los nuevos periodos procesados
    df_final = df_final.dropna(subset=['dia', 'noche'], how='any')

    output_file = RUTA_SALIDA / f'{var}_periodos.csv'
    df_final.to_csv(output_file)
    print(f"\nProceso completado. Archivo guardado en: {output_file}")

except FileNotFoundError as e:
    print(f"ERROR CRÍTICO: No se encontró el archivo base. {e}")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")

print("DONE!")