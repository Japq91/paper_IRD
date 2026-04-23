#!/usr/bin/python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import cartopy.crs as ccrs
from glob import glob
#  utilitários de plot para análise de bias

# ─── dados ────────────────────────────────────────────────────────────────────

def load_bias_data(root, var, group='todas'):
    """
    Lê o CSV de diferenças, calcula bias (EXP - OBS) e filtra por grupo.

    Parâmetros
    ----------
    root  : str   — caminho raiz do projeto (ex.: '../')
    var   : str   — variável ('t2m' ou 'pr')
    group : str   — 'todas' | 'corte1' (próx. lago) | 'corte2' (longe do lago)

    Retorna
    -------
    DataFrame com colunas = nomes de experimento e linhas = estações.
    """
    df = pd.read_csv(f'{root}data/csv_files/{var}_dif_AllStation.csv', index_col=0)

    # las columnas de bias ya están calculadas en el CSV: "EXP0-OBS", "EXP1-OBS", ...
    bias_cols = [c for c in df.columns if c.endswith('-OBS')]
    bias = df[bias_cols].copy()
    bias.columns = [c.replace('-OBS', '') for c in bias_cols]  # → "EXP0", "EXP1", ...

    if group != 'todas':
        matches = glob(f'{root}input_csv/{group}_*.txt')
        if not matches:
            raise FileNotFoundError(
                f"No se encontró archivo para '{group}'.\n"
                f"Disponibles: {glob(f'{root}input_csv/*.txt')}"
            )
        stations = pd.read_csv(matches[0], sep='\t')['field_1']
        bias = bias.loc[bias.index.isin(stations)]

    return bias

def build_bias_long(root, var):
    """
    Empilha os três grupos (ALL, NL, FFL) em formato longo para o boxplot.
    """
    mapping = {'todas': 'ALL', 'corte1': 'NL', 'corte2': 'FFL'}
    frames = []
    for group, label in mapping.items():
        df = load_bias_data(root, var, group)
        #print(df.columns.tolist())
        melted = df.melt(var_name='EXP', value_name='BIAS')
        melted['STATION'] = label
        frames.append(melted)
    
    return pd.concat(frames, ignore_index=True)


# ─── mapas ────────────────────────────────────────────────────────────────────

def plot_mapa(ax, df, experiment, scale, vmax, shapes):
    """
    Plota scatter de bias positivo (vermelho ▲) e negativo (azul ▼) no mapa.

    Parâmetros
    ----------
    ax         : eixo cartopy
    df         : DataFrame com colunas 'lon', 'lat' e f'{experiment}-OBS'
    experiment : str — nome do experimento
    scale      : float — fator de escala para tamanho dos marcadores
    vmax       : float — valor máximo da colorbar
    shapes     : dict  — {'peru': Reader, 'lago': Reader}

    Retorna
    -------
    (scatter_neg, scatter_pos) — objetos para as colorbars
    """
    col = f'{experiment}-OBS'

    # ── sin datos: panel vacío con texto central ──────────────────────────────
    if col not in df.columns:
        ax.set_extent([-70.8, -68.3, -17.05, -14.4])
        ax.add_geometries(shapes['peru'].geometries(), ccrs.PlateCarree(),
                          edgecolor='k', facecolor='none', alpha=0.4, linewidth=0.7)
        ax.add_geometries(shapes['lago'].geometries(), ccrs.PlateCarree(),
                          edgecolor='k', facecolor='lightblue', alpha=0.4, linewidth=0.9)
        ax.text(0.5, 0.5, 'NO DATA\n!!!', transform=ax.transAxes,
                ha='center', va='center', fontsize=12,
                color='r', style='italic')
        return None, None                      # señal de "vacío" al caller

    # ── con datos: plot normal ────────────────────────────────────────────────
    neg, pos = df[df[col] < 0], df[df[col] >= 0]
    ax.set_extent([-70.8, -68.3, -17.05, -14.4])

    sc_neg = ax.scatter(neg.lon, neg.lat,
                        s=neg[col] * -60 * scale, c=neg[col], marker='v',
                        cmap=plt.cm.get_cmap('Blues_r', vmax * 2),
                        vmin=-vmax, vmax=0, edgecolor='b', zorder=5, alpha=0.8)
    sc_pos = ax.scatter(pos.lon, pos.lat,
                        s=pos[col] * 60 * scale, c=pos[col], marker='^',
                        cmap=plt.cm.get_cmap('Reds', vmax * 2),
                        vmin=0, vmax=vmax, edgecolor='r', zorder=5, alpha=0.8)

    crs = ccrs.PlateCarree()
    ax.add_geometries(shapes['peru'].geometries(), crs=crs,
                      edgecolor='k', facecolor='none', alpha=0.9, linewidth=0.7)
    ax.add_geometries(shapes['lago'].geometries(), crs=crs,
                      edgecolor='k', facecolor='lightblue', alpha=0.9, linewidth=0.9)

    return sc_neg, sc_pos


def setup_axes(ax, i, j, numrow, xticks, yticks):
    """
    Adiciona gridlines ao eixo cartopy conforme sua posição na grade.
    Só exibe rótulos na borda esquerda (coluna 0) e borda inferior (última linha).
    """
    left = (i == 0)
    bot  = (j == numrow - 1)

    grd = ax.gridlines(xlocs=xticks, ylocs=yticks, color='gray', alpha=0.99,
                       draw_labels={'left': left, 'bottom': bot,
                                    'top': False, 'right': False},
                       linewidth=1, linestyle='--')
# ─── boxplot ──────────────────────────────────────────────────────────────────

def plot_boxplot_panel(ax, root, var, exp_labels):
    """
    Desenha o painel de boxplots (ALL / NL / FFL) para todos os experimentos.

    Parâmetros
    ----------
    ax         : eixo matplotlib
    root       : str — caminho raiz
    var        : str — variável
    exp_labels : list[str] — rótulos de eixo (um por experimento, sem o último)
    """
    data = build_bias_long(root, var)
    #print(data.head())
    #print(data.columns.tolist())

    sns.boxplot(y='BIAS', x='EXP', data=data, palette='Paired',
                hue='STATION', ax=ax)
    ax.axhline(0, color='r', linestyle='-.', alpha=0.8, lw=1)
    ax.set_xticks(range(len(exp_labels)), exp_labels, rotation=0)
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.yaxis.tick_right()
    #ax.set_aspect(4.8 / 10 if 't' in var else 4 / 18) # TAMAÑO DE PANEL BOXPLOT
    #ax.set_aspect(4.8 / 10 if 't' in var else 7 / 18) # TAMAÑO DE PANEL BOXPLOT
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0, title='STATION')
    ax.grid(True)
