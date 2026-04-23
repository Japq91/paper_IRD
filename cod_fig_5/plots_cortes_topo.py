#!/usr/bin/python
# Ejecutar con: from aux_topo import *

from aux_topo_plot import *
from matplotlib.gridspec import GridSpec

# ─── configuración ────────────────────────────────────────────────────────────

ROOT = '../'   # ruta raíz del proyecto (un nivel arriba de src/)

# ─── figura ───────────────────────────────────────────────────────────────────

fig = plt.figure(constrained_layout=False, figsize=(11, 7))
gs  = GridSpec(3, 4, figure=fig, hspace=0.5, wspace=0.25)

# ── a) boxplot bias de altitud ────────────────────────────────────────────────
ax = fig.add_subplot(gs[0, 0:1])
fis = sorted(gb(f'{ROOT}input_csv/*_all_*csv'))
bp  = p1_boxplot(ROOT)
adi_boxplot(ax, bp)

# ── b) scatter altitud — corte1 ───────────────────────────────────────────────
ax = fig.add_subplot(gs[0, 1:2])
cort = 'corte1'
mod, obs = crea_mod_obs(ROOT, cort)
text3 = plot_t1(ROOT, cort, mod, ax)
adi_plot_t1(ax, 'NL', text3, 'b)')

# ── c) scatter altitud — corte2 ───────────────────────────────────────────────
ax = fig.add_subplot(gs[0, 2:3])
cort = 'corte2'
mod, obs = crea_mod_obs(ROOT, cort)
text3 = plot_t1(ROOT, cort, mod, ax)
adi_plot_t1(ax, 'FFL', text3, 'c)')

# ── gs[0, 3]: leyenda externa de los paneles b y c ───────────────────────────
legend = ax.legend(markerscale=2, loc='lower left',
                   bbox_to_anchor=(1.065, -0.07), fontsize=10)
legend.get_frame().set_facecolor('none')
legend.get_frame().set_edgecolor('none')

# ── d) perfil topográfico — corte1 ────────────────────────────────────────────
ax = fig.add_subplot(gs[1, :])
cort = 'corte1'
mod, obs = crea_mod_obs(ROOT, cort)
ax3 = plot_b1(mod, obs, 'line', cort, ax, 'no')
adi_plot_b1(ax, ax3, cort, 'NL', 'd)')
pos_label(ax, 'A', 0.006, 0.7, colo='k', tus='si')
pos_label(ax, 'B', 0.995, 0.7, colo='k', tus='si')

# ── e) perfil topográfico — corte2 ────────────────────────────────────────────
ax = fig.add_subplot(gs[2, :])
cort = 'corte2'
mod, obs = crea_mod_obs(ROOT, cort)
ax3 = plot_b1(mod, obs, 'line', cort, ax, 'on')
adi_plot_b1(ax, ax3, cort, 'FFL', 'e)')
pos_label(ax, 'C', 0.006, 0.7, colo='k', tus='si')
pos_label(ax, 'D', 0.995, 0.7, colo='k', tus='si')

# ─── guardar ──────────────────────────────────────────────────────────────────
plt.savefig(f'{ROOT}figures/topo_profiles.png', dpi=100, bbox_inches='tight')
plt.close()
