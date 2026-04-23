#!/usr/bin/python
from aux_station_plot import *
from cartopy.io.shapereader import Reader
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')
############################################################
plt.rcParams.update({'font.size': 10})
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
############################################################
# ─── CONFIGURACION ─────────────────────────────────────────────────────────────
############################################################
ROOT    = '../'
VAR     = 'pr'           # 't2m' ou 'pr'
NUMCOL  = 5
NUMROW  = 3
CRS     = ccrs.PlateCarree()

SHAPES  = {
    'lago': Reader(f'{ROOT}input_shp/lago_titikk_2022.shp'),
    'peru': Reader(f'{ROOT}input_shp/peru2.shp'),
}

XTICKS  = np.arange(-77, -64, 1)
YTICKS  = np.arange(-23, -10, 1)
############################################################
# ─── metadados da variável ────────────────────────────────────────────────────
############################################################
META = {
    't2m': dict(name='Surface temperature', vmax=3, scale=1.5, unit='[°C]',  ylim=(-4,  2)),
    'pr':  dict(name='Precipitation',       vmax=5, scale=1.0, unit='[mm/day]', ylim=(-4, 8)),
}
m = META[VAR]
############################################################
# ─── rótulos dos experimentos ─────────────────────────────────────────────────
############################################################
EXP_IDS = [f'EXP{i}' for i in range(11)] + ['boxplot']
print(EXP_IDS)
EXP_LABELS_boxplot = ['GMTs\nMOD30\nSOM',  'GMTns\nMOD30\nnSOM', 'SRTs\nMOD30\nSOM', 'SRTns\nMOD30\nSOM', 
              'GMTns\nMOD15\nSOM',  'GMTns\nEVA\nSOM', 'GMTns\nEVA\nTRO',   'GMTns\nEVA\nCON',    
              'GMTns\nEVA\nSIE', 'GMTns\nEVA\nMAM',   'GMTns\nEVA\nSIE_SST','BOXPLOTS',]
EXP_LABELS = ['GMTs\nMOD30_SOM','GMTns\nMOD30_nSOM','SRTs\nMOD30_SOM','SRTns\nMOD30_SOM',
              'GMTns\nMOD15_SOM','GMTns\nEVA_SOM', 'GMTns\nEVA_TRO', 'GMTns\nEVA_CON',
              'GMTns\nEVA_SIE', 'GMTns\nEVA_MAM','GMTns\nEVA_SIE_SST','BOXPLOTS']
PANEL_LABELS = list('abcdefghijkl')   # 'a)' … 'l)'

# ─── figura principal ─────────────────────────────────────────────────────────

df = pd.read_csv(f'{ROOT}data/csv_files/{VAR}_dif_AllStation.csv', index_col=0)

fig = plt.figure(figsize=(12, 9))
fig.suptitle(f'{m["name"]} biases', fontsize=16,)
gs = GridSpec(nrows=NUMROW, ncols=NUMCOL, hspace=0.095, wspace=0.05)

sc_neg = sc_pos = None

for k, (exp_id, label, panel) in enumerate(zip(EXP_IDS, EXP_LABELS, PANEL_LABELS)):
    j, i = divmod(k, NUMCOL)

    if i == 1 and j == NUMROW - 1:
        ax = fig.add_subplot(gs[j, i:])
        plot_boxplot_panel(ax, ROOT, VAR, EXP_LABELS_boxplot[:-1])

    else:
        ax = fig.add_subplot(gs[j, i], projection=CRS)
        neg, pos = plot_mapa(ax, df, exp_id, m['scale'], m['vmax'], SHAPES)
        setup_axes(ax, i, j, NUMROW, XTICKS, YTICKS)

        if neg is not None:             # solo sobreescribe si hay datos reales
            sc_neg, sc_pos = neg, pos

        if i == 0 and j == NUMROW - 1:
            ax.text(-56.5, -10.6 if 't' in VAR else -11.1,
                    m['unit'], rotation='vertical')

    ax.set_title(label,       loc='center')
    ax.set_title(f'{panel})', loc='left')
############################################################
# colorbars — solo si al menos un panel tuvo datos
if sc_neg is not None:
    cbar_neg = fig.add_axes([0.91, 0.50, 0.03, 0.15])
    cbar_pos = fig.add_axes([0.91, 0.65, 0.03, 0.15])
    fig.colorbar(sc_neg, cax=cbar_neg, extend='neither', spacing='proportional')
    fig.colorbar(sc_pos, cax=cbar_pos, extend='neither', spacing='proportional')
print("DONE! figura creada")
plt.savefig(f'{ROOT}figures/general_dif_{VAR}.jpg', dpi=100, bbox_inches='tight')
plt.close()
