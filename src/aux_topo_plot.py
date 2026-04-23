# aux_topo.py
# Funciones auxiliares para figura de perfiles topográficos y scatter altitud.
# Importar en el notebook principal con: from aux_topo import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, linregress
from glob import glob as gb

plt.rcParams.update({'font.size': 10})
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']


# ─── datos ────────────────────────────────────────────────────────────────────

def p1_boxplot(root):
    """
    Lee los CSVs de todos los experimentos y calcula bias de altitud (EXP - obs).
    Retorna DataFrame con 4 columnas (exp0..exp3), una fila por estación.

    Archivos esperados en {root}input_csv/:
        all_experimentos.csv       — variables climáticas de todos los experimentos
        topo_all_experimentos.csv  — altitud simulada por cada experimento
    """
    t1 = pd.read_csv(f'{root}input_csv/all_experimentos.csv')
    a1 = pd.read_csv(f'{root}input_csv/topo_all_experimentos.csv')

    # une los dos CSVs horizontalmente y elimina columnas duplicadas
    f1 = pd.concat([t1, a1], axis=1)
    f2 = f1.T.drop_duplicates().T

    # selecciona las 5 primeras columnas con 'alt': [obs, EXP0, EXP1, EXP2, EXP3]
    alt_cols = sorted([c for c in f2.columns if 'alt' in c])
    f32 = f2[alt_cols[:5]]

    # calcula bias con p1()
    f7 = p1(f32, 'alt')

    # convierte a numérico — puede haber strings tras el concat/drop_duplicates
    for i in range(len(f7.columns)):
        f7[f7.columns[i]] = pd.to_numeric(f7[f7.columns[i]], errors='coerce')
    f7.columns = ['exp0', 'exp1', 'exp2', 'exp3']

    return f7


def p1(f4, var):
    """
    Calcula bias para cada experimento restando la columna observada (var).
    f4 debe tener: columna 0 = obs (var), columnas 1..4 = experimentos.
    Usa .values para evitar problemas de alineación con índices duplicados.
    Retorna DataFrame con columnas 'dif_{var}_e0' .. 'dif_{var}_e3'.
    """
    df = None
    for i in range(4):
        data = f4[f4.columns[i + 1]].values - f4[var].values
        col  = f'dif_{var}_e{i}'
        if i == 0:
            df = pd.DataFrame(data=data, columns=[col])
        else:
            df[col] = data
    return df


def crea_mod_obs(root, cort):
    """
    Lee todos los archivos CSV de un corte (pr y t2m) y los combina.
    Separa filas de modelo (tipo=1) y observaciones (tipo=0).

    Archivos esperados: {root}input_csv/*{cort}.csv
    Columnas esperadas: lon, lat, pr/t2m, tipo, distancia, acum_distancia, topo

    Retorna:
        mod : DataFrame — filas con tipo=1 (simulación)
        obs : DataFrame — filas con tipo=0 (observaciones, sin duplicados de lat)
    """
    files = gb(f'{root}input_csv/*{cort}.csv')

    # concatena pr y t2m horizontalmente (join='inner' conserva solo estaciones comunes)
    for i, file in enumerate(files):
        df = pd.read_csv(file)
        if i == 0:
            df2 = df.copy()
        else:
            df2 = pd.concat([df2, df], axis=1, join='inner')

    # elimina columnas duplicadas (lon, lat, tipo, etc. aparecen en cada archivo)
    df4 = df2.T.drop_duplicates().T

    mod = df4[df4['tipo'] == 1].reset_index(drop=True)
    obs = df4[df4['tipo'] == 0].drop_duplicates('lat').reset_index(drop=True)

    return mod, obs


# ─── tendencias ───────────────────────────────────────────────────────────────

def trend_1(ax, x0, y, colo):
    """
    Ajusta y grafica línea de tendencia lineal (polyfit grado 1).
    Reporta correlación de Pearson y significancia (p < 0.05).
    Retorna string: 'r: X.XX sig' o 'r: X.XX non-sig'.
    """
    cor, p_value = pearsonr(x0, y)
    trendline    = np.poly1d(np.polyfit(x0, y, 1))
    ax.plot(x0, trendline(x0), color=colo, linestyle='-', linewidth=1.4, alpha=0.9)
    sig = 'sig' if p_value < 0.05 else 'non-sig'
    return f'r: {cor:.2f} {sig}'


def trend_2(ax, x0, y, colo):
    """
    Igual que trend_1 pero reporta la pendiente (tendencia) en vez de r.
    Divide x por 1000 para el ajuste, grafica sobre x0 original.
    Retorna string: 'r: X.X sig' o 'r: X.X non-sig'.
    """
    x = x0 / 1000
    slope, intercept, _, p_value, _ = linregress(x, y)
    trendline = slope * x + intercept
    ax.plot(x0, trendline, color=colo, linestyle='-', linewidth=1.4, alpha=0.9)
    sig = 'sig' if p_value < 0.05 else 'non-sig'
    return f'r: {slope:.1f} {sig}'


# ─── decoración ───────────────────────────────────────────────────────────────

def pos_label(ax, lab, x, y, rota=0, colo='k', tus='no'):
    """
    Coloca texto en coordenadas de ejes normalizadas (0 a 1).
    tus='si' agrega fondo amarillo redondeado — útil para etiquetas A, B, C...
    """
    tu = ax.text(x, y, lab, transform=ax.transAxes,
                 va='center', ha='center', rotation=rota, c=colo)
    if 'no' not in tus:
        tu.set_bbox(dict(facecolor='y', alpha=0.7, edgecolor='y',
                         boxstyle='round,pad=.01'))


def adi_boxplot(ax, bop):
    """
    Decora el panel a): boxplot de bias de altitud.
    bop: DataFrame con 4 columnas de bias (exp0..exp3).
    """
    bop.columns = ['GMT\ns', 'GMT\nns', 'SRT\ns', 'SRT\nns']
    bop.boxplot(ax=ax, zorder=3, rot=0)
    ax.axhline(y=0, color='r', linestyle='-', zorder=2, linewidth=1, alpha=0.7)
    ax.set_title('Topography')
    ax.set_title('a)', loc='left')
    pos_label(ax, '[m]', -0.075, 0.96)


def adi_plot_b1(ax, axn, corte, tipo, letra):
    """
    Decora los paneles d/e): perfil topográfico.
    ax  : eje principal (altitud en m)
    axn : eje twin (temperatura °C y precipitación mm/mon)
    """
    ax.set_title(letra, loc='left')
    ax.set_title(tipo)
    ax.margins(x=0.004)
    axn.grid(linestyle=':', linewidth=0.7, alpha=0.9)
    ax.grid(axis='x', linestyle=':', linewidth=0.6, alpha=0.9)
    ax.set_ylim([3750, 4950])
    axn.set_ylim([0.1, 12])
    pos_label(ax, '[m]',                 -0.017,  0.96)
    pos_label(ax, '[°C]',                 1.02,   0.96, colo='darkred')
    pos_label(ax, r'[$\frac{mm}{mon}$]',  1.022,  0.04, colo='darkgreen')


def adi_plot_t1(ax, tipo, txt, letra):
    """
    Decora los paneles b/c): scatter altitud.
    txt: lista [prc_mod, prc_obs, t2m_mod, t2m_obs] con strings de trend_1.
    Imprime correlaciones del modelo en negro y de observaciones en azul.
    """
    ax.set_title(letra, loc='left')
    ax.set_title(tipo)
    props = dict(boxstyle='round', facecolor='w', alpha=0, ec='none')
    # modelo (negro)
    ax.text(0.45, 0.83,
            '\n'.join([f'prc {txt[0]}', f't2m {txt[2]}']),
            transform=ax.transAxes, fontsize=7,
            verticalalignment='bottom', bbox=props, c='k')
    # observaciones (azul)
    ax.text(0.45, 0.68,
            '\n'.join([f'prc {txt[1]}', f't2m {txt[3]}']),
            transform=ax.transAxes, fontsize=7,
            verticalalignment='bottom', bbox=props, c='b')
    pos_label(ax, '[m]',                  0.96,  -0.09)
    pos_label(ax, '[°C]',                -0.08,   0.96, colo='darkred')
    pos_label(ax, r'[$\frac{mm}{mon}$]', -0.1,    0.04, colo='darkgreen')


# ─── plots ────────────────────────────────────────────────────────────────────

def plot_t1(root, cort, mod, ax1):
    """
    Panel b/c): scatter precipitación y temperatura vs altitud con tendencias.

    mod  : DataFrame modelo devuelto por crea_mod_obs() — columnas topo, pr, t2m
    Grafica modelo como círculos blancos y obs (archivo .txt) como círculos de color.
    Retorna lista de 4 strings: [prc_mod, prc_obs, t2m_mod, t2m_obs].
    """
    # lee el archivo de estaciones de referencia del corte
    f = pd.read_csv(gb(f'{root}input_csv/{cort}*.txt')[0], sep='\t')

    datos_caja = []
    for var, plab, ec in [('pr',  'Precipitation', 'darkgreen'),
                           ('t2m', 'Temperature',   'darkred')]:
        x1, y1 = mod['topo'], mod[var]
        x2, y2 = f['alt'],    f[var]

        ax1.scatter(x1, y1, c='w', edgecolor=ec, alpha=0.8, s=15,
                    label=f'GMTns_EVA_SIE {plab}')
        ax1.scatter(x2, y2, c=ec, edgecolor='.2', linewidth=0.71)

        datos_caja.append(trend_1(ax1, x1, y1, 'k'))  # tendencia modelo (negro)
        datos_caja.append(trend_1(ax1, x2, y2, 'b'))  # tendencia obs (azul)

    ax1.set_xlim([3800, 4980])
    ax1.set_ylim([2, 14])
    return datos_caja


def plot_b1(f6, ob, tipo, cut, ax2, legend):
    """
    Panel d/e): perfil topográfico con líneas de temperatura y precipitación.

    f6     : DataFrame modelo con columnas acum_distancia, topo, pr, t2m
    ob     : DataFrame observaciones con las mismas columnas
    tipo   : 'line' dibuja líneas + scatter; otro valor dibuja solo scatter
    legend : 'on' muestra leyenda, cualquier otro valor la oculta
    Retorna el eje twin ax1 para que adi_plot_b1 pueda ajustar sus límites.
    """
    # relleno topográfico (área gris = altitud del modelo)
    ax2.set_facecolor('0.98')
    ax2.plot(f6.acum_distancia, f6.topo,
             c='0.3', linewidth=0.5, linestyle=':', zorder=1)
    ax2.fill_between(f6.acum_distancia, f6.topo,
                     color='0.7', label='GMTns_EVA_SIE Altitude', alpha=1)
    ax2.scatter(ob.acum_distancia, ob['topo'],
                label='Observed Altitude', marker='x', c='.2', s=50, zorder=8)

    ax1 = ax2.twinx()  # eje derecho para temperatura y precipitación

    if 'line' in tipo:
        ax1.plot(f6.acum_distancia, f6['pr'],
                 label='GMTns_EVA_SIE Precipitation',
                 c='darkgreen', lw=1.7, zorder=2, alpha=1)
        ax1.plot(f6.acum_distancia, f6['t2m'],
                 label='GMTns_EVA_SIE Temperature',
                 c='firebrick', lw=1.7, zorder=1, alpha=1)
        ax1.scatter(ob.acum_distancia, ob['pr'],
                    label='Observed Precipitation',
                    marker='o', c='darkgreen', s=70, ec='.2', zorder=2, lw=0.71)
        ax1.scatter(ob.acum_distancia, ob['t2m'],
                    label='Observed Temperature',
                    marker='o', c='firebrick', s=70, ec='.2', zorder=2, lw=0.71)
    else:
        ax1.scatter(f6.acum_distancia, f6['pr'],
                    label='Temperature', marker='o', c='w', s=40,
                    edgecolor='teal', zorder=5)
        ax1.scatter(f6.acum_distancia, f6['t2m'],
                    label='Precipitation', marker='o', c='w', s=40,
                    edgecolor='firebrick', zorder=5)

    if 'on' in legend:
        # bbox_to_anchor en coordenadas del eje twin — ajustar si cambia figsize
        ax2.legend(loc='upper left', bbox_to_anchor=(0.752, 3.08), frameon=False)
        ax1.legend(loc='upper left', bbox_to_anchor=(0.750, 4.02), frameon=False)

    ax1.set_ylim([2, 14])
    return ax1