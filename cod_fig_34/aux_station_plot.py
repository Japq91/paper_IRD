#!/usr/bin/python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import cartopy.crs as ccrs
from glob import glob
from matplotlib.colors import BoundaryNorm

# # ─── dados ────────────────────────────────────────────────────────────────────

def load_bias_data(root, var, group='todas'):
    """
    Lê o CSV de diferenças, calcula bias (ou bias percentual para 'pr') e filtra por grupo.

    Parâmetros
    ----------
    root  : str   — caminho raiz do projeto (ex.: '../')
    var   : str   — variável ('t2m' ou 'pr')
    group : str   — 'todas' | 'corte1' (próx. lago) | 'corte2' (longe do lago)

    Retorna
    -------
    DataFrame com colunas = nomes de experimento (EXP0, EXP1, ...) e linhas = estações.
    """
    df = pd.read_csv(f'{root}data/csv_files/{var}_dif_AllStation.csv', index_col=0)

    if var == 'pr':
        # Coluna observada (precipitação)
        obs = df['pr']
        # Colunas dos experimentos: EXP0_pr, EXP1_pr, ...
        exp_cols = [c for c in df.columns if c.startswith('EXP') and c.endswith(f'_{var}')]
        
        bias = pd.DataFrame(index=df.index)
        for col in exp_cols:
            exp_name = col.replace(f'_{var}', '')      # "EXP9"
            # Evita divisão por zero: onde obs == 0, o bias fica NaN
            bias[exp_name] = 100 * (df[col] - obs) / obs
            bias[exp_name] = bias[exp_name].where(obs != 0, pd.NA)
    else:
        # Comportamento original para t2m (diferença absoluta)
        bias_cols = [c for c in df.columns if c.endswith('-OBS')]
        bias = df[bias_cols].copy()
        bias.columns = [c.replace('-OBS', '') for c in bias_cols]

    # Ordena colunas naturalmente: EXP0, EXP1, ..., EXP9, EXP10, ...
    bias = bias.reindex(
        sorted(bias.columns, key=lambda x: int(x.replace('EXP', ''))),
        axis=1
    )

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

def bias_percentage(df, var):
    """
    Convierte el DataFrame de precipitación crudo a bias porcentual.
    Para otras variables (t2m) devuelve el DataFrame sin cambios.
    
    Parámetros
    ----------
    df  : DataFrame — leído directamente del CSV '*_dif_AllStation.csv'
    var : str       — 'pr' o 't2m'
    
    Retorna
    -------
    DataFrame con las mismas columnas de coordenadas y columnas EXP#-OBS
    (los valores son bias porcentual para 'pr', o los originales para otras).
    """
    if var != 'pr':
        return df   # no hacer nada para temperatura
    
    # Columnas que queremos conservar (ajusta si tu CSV tiene otras)
    coord_cols = ['lon', 'lat', 'est', 'alt']   # también podrías incluir 'pr' si quieres
    obs = df['pr']
    
    new_df = df[coord_cols].copy()
    
    # Identificar columnas de experimentos: 'EXP0_pr', 'EXP1_pr', ...
    exp_cols = [c for c in df.columns if c.startswith('EXP') and c.endswith(f'_{var}')]
    
    for col in exp_cols:
        exp_name = col.replace(f'_{var}', '')              # 'EXP0', 'EXP1', ...
        bias_col = f'{exp_name}-OBS'                      # nombre que espera plot_mapa
        # Cálculo del bias porcentual
        new_df[bias_col] = 100 * (df[col] - obs) / obs
        # Evitar división por cero (donde obs == 0)
        new_df[bias_col] = new_df[bias_col].where(obs != 0, pd.NA)
    
    # Opcional: ordenar las columnas EXP#-OBS numéricamente
    bias_cols = [c for c in new_df.columns if c.endswith('-OBS')]
    sorted_cols = sorted(bias_cols, key=lambda x: int(x.replace('EXP', '').replace('-OBS', '')))
    new_df = new_df[coord_cols + sorted_cols]
    
    return new_df
# ─── mapas ────────────────────────────────────────────────────────────────────
from matplotlib.colors import BoundaryNorm

def plot_mapa(ax, df, experiment, scale, vmax, shapes, clip_range=None, step=None):
    col = f'{experiment}-OBS'

    # ── sin datos: panel vacío ──────────────────────────────────────────────
    if col not in df.columns:
        ax.set_extent([-70.8, -68.3, -17.05, -14.4])
        ax.add_geometries(shapes['peru'].geometries(), ccrs.PlateCarree(),
                          edgecolor='k', facecolor='none', alpha=0.4, linewidth=0.7)
        ax.add_geometries(shapes['lago'].geometries(), ccrs.PlateCarree(),
                          edgecolor='k', facecolor='lightblue', alpha=0.4, linewidth=0.9)
        ax.text(0.5, 0.5, 'NO DATA\n!!!', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='r', style='italic')
        return None, None

    # ── datos: aplicar clipping si se solicita ──────────────────────────────
    valores = df[col].copy()
    if clip_range is not None:
        vmin_clip, vmax_clip = clip_range
        valores_clip = valores.clip(lower=vmin_clip, upper=vmax_clip)
        vmax_efectivo = vmax_clip
    else:
        valores_clip = valores
        vmax_efectivo = vmax

    # ── configurar norm y cmap según step (discreto o continuo) ─────────────
    if step is not None:
        # Límites para el lado negativo: desde -vmax_efectivo hasta 0 (paso step)
        neg_boundaries = np.arange(-vmax_efectivo, 0 + step, step)
        # Límites para el lado positivo: desde 0 hasta vmax_efectivo (paso step)
        pos_boundaries = np.arange(0, vmax_efectivo + step, step)
        neg_norm = BoundaryNorm(neg_boundaries, ncolors=len(neg_boundaries)-1)
        pos_norm = BoundaryNorm(pos_boundaries, ncolors=len(pos_boundaries)-1)
        neg_cmap = plt.cm.get_cmap('Blues_r', len(neg_boundaries)-1)
        pos_cmap = plt.cm.get_cmap('Reds',   len(pos_boundaries)-1)
    else:
        # Comportamiento original continuo
        neg_norm = None
        pos_norm = None
        neg_cmap = plt.cm.get_cmap('Blues_r', int(vmax_efectivo * 2))
        pos_cmap = plt.cm.get_cmap('Reds',    int(vmax_efectivo * 2))

    # ── separar datos negativos y positivos ────────────────────────────────
    mask_neg = valores < 0
    mask_pos = valores >= 0
    neg = df[mask_neg]
    pos = df[mask_pos]

    ax.set_extent([-70.8, -68.3, -17.05, -14.4])

    # Scatter negativo
    if not neg.empty:
        if step is not None:
            sc_neg = ax.scatter(neg.lon, neg.lat,
                                s=valores_clip[mask_neg] * -60 * scale,
                                c=valores_clip[mask_neg], marker='v',
                                cmap=neg_cmap, norm=neg_norm,
                                edgecolor='b', zorder=5, alpha=0.8)
        else:
            sc_neg = ax.scatter(neg.lon, neg.lat,
                                s=valores_clip[mask_neg] * -60 * scale,
                                c=valores_clip[mask_neg], marker='v',
                                cmap=neg_cmap, vmin=-vmax_efectivo, vmax=0,
                                edgecolor='b', zorder=5, alpha=0.8)
    else:
        sc_neg = None

    # Scatter positivo
    if not pos.empty:
        if step is not None:
            sc_pos = ax.scatter(pos.lon, pos.lat,
                                s=valores_clip[mask_pos] * 60 * scale,
                                c=valores_clip[mask_pos], marker='^',
                                cmap=pos_cmap, norm=pos_norm,
                                edgecolor='r', zorder=5, alpha=0.8)
        else:
            sc_pos = ax.scatter(pos.lon, pos.lat,
                                s=valores_clip[mask_pos] * 60 * scale,
                                c=valores_clip[mask_pos], marker='^',
                                cmap=pos_cmap, vmin=0, vmax=vmax_efectivo,
                                edgecolor='r', zorder=5, alpha=0.8)
    else:
        sc_pos = None

    # ── añadir geometrías ───────────────────────────────────────────────────
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
