import warnings
warnings.filterwarnings("ignore")
# LIBRERIAS
print('Reader')
from cartopy.io.shapereader import Reader; print('pandas')
import pandas as pd; print('xarray')
import xarray as xr; print('numpy')
import numpy as np; print('restantes')
import matplotlib.pyplot as plt
import matplotlib
from glob import glob as gb
import cartopy.crs as ccrs
from matplotlib.gridspec import GridSpec
import math
import matplotlib.patches as patches

plt.rcParams.update({'font.size': 10})
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

def agrega_grid(i,j,numcol,numrow,ax):
    if i==0 and j<numrow-1:
        grd = ax.gridlines(xlocs=xticks, ylocs=yticks, color='gray',alpha=0.99, draw_labels=False,linewidth=1,linestyle='--',)
        grd.left_labels=True;grd.down_labels=grd.top_labels=grd.right_labels=False
    elif i>0 and j==numrow-1:
        grd = ax.gridlines(xlocs=xticks, ylocs=yticks, color='gray',alpha=0.99, draw_labels=True,linewidth=1,linestyle='--',)
        grd.down_labels=True;grd.left_labels=grd.top_labels=grd.right_labels=False
    elif i==0 and j==numrow-1:
        grd = ax.gridlines(xlocs=xticks, ylocs=yticks, color='gray',alpha=0.99, draw_labels=True,linewidth=1,linestyle='--',)
        grd.left_labels=grd.down_labels=True;grd.top_labels=grd.right_labels=False
    else:
        grd = ax.gridlines(xlocs=xticks, ylocs=yticks, color='gray',alpha=0.99, draw_labels=False,linewidth=1,linestyle='--',)
        #grd.left_labels=grd.down_labels=True;grd.top_labels=grd.right_labels=False    

ri='/home/jap/IRD/OVAR/'
ro='%s/out/'%ri
shapes_r='/home/jap/SHAPES/'
lago=Reader(shapes_r+'lago_titikk_2022.shp')
peru=Reader(shapes_r+'peru2.shp')
crs=ccrs.PlateCarree()
xticks,yticks=np.arange(-77,-64.5,1),np.arange(-23,-10,1)
plt.rcParams.update({'font.size': 10})

def paso_2(ax1,fon2,fon1):
    c1=fig.add_axes([.15, 0.09, 0.03, 0.3])
    fig.colorbar(fon1,cax=c1,orientation='vertical')#,label='[g/kg]'
    c2=fig.add_axes([.05, 0.09, 0.03, 0.3])
    fig.colorbar(fon2,cax=c2,orientation='vertical')#,label='[g/kg]'
    fig.tight_layout()

#mods2=['T0L0P0S0','T1L0P0S0','T1L2P0S0','T1L2P3S0','T1L2P3S1']
var='ALBEDO'
tipo='anom'
mods=[0,1,5,8,10]
mods2=['GMTs_MOD30_SOM','GMTns_MOD30_SOM','GMTns_EVA_SOM','GMTns_EVA_SIE','GMTns_EVA_SIE_SST']

def paso_1(de,ax1,var):       
    if 'anom' in file: 
        mapa='RdBu_r';leve=np.linspace(-40,40,11)
        if 'ALBEDO' in var:leve=np.linspace(-.1,.1,11)#np.linspace(-.02,.02,11)
    else: 
        mapa='jet';leve= np.linspace(-20,160,10) #np.linspace(-20,200,10)
        if 'ALBEDO' in var:leve=np.linspace(0,1,11)#np.linspace(0,.5,11)
        elif 'LH' in var: leve=np.linspace(-20,160,10)
    fondo1=de.plot(ax=ax1,add_colorbar=True,cmap=mapa,levels=leve)     
    #fondo1=de.plot(ax=ax1,add_colorbar=False,cmap=mapa,levels=leve)
    ax1.add_geometries(peru.geometries(),crs=crs,edgecolor='k',facecolor='none',alpha=0.9,linewidth=.7,zorder=2)     
    ax1.add_geometries(lago.geometries(),crs=crs,edgecolor='k',facecolor='none',alpha=0.5,linewidth=1,zorder=3)#'lightblue'
    #ax1.set_title(titul1)  
    ax1.set_extent([-70.7,-68.3,-17,-14.7]) 
    return fondo1

def add_cuadrado(ax):
    #square = patches.Rectangle((-16,-70), -15, -69, edgecolor='k', facecolor='none',lw=2,zorder=5)
    square = patches.Rectangle((-69.7,-16), -.4, .5, edgecolor='k', facecolor='none',lw=2,ls='--',zorder=5)
    ax.add_patch(square)

fig=plt.figure(figsize=(12,10))
gs=GridSpec(nrows=3, ncols=3)
n=0
lplt3=['a)','b)','c)','d)','e)','f)','g)','h)','i)','j)']
for j,var in enumerate(['LH','HFX','ALBEDO']):        
    for i,tipo in enumerate(['prom','prom','anom']):
        if i==1: mod=5
        else: mod=1
        ntit=['GMTns_MOD30_SOM','GMTns_EVA_SOM','na'][i]
        if i==2 and j==0: ntit='b) - a)'
        elif i==2 and j==1 : ntit='e) - d)'
        elif i==2 and j==2 :ntit='h) - g)'
        file='clean/%s_%s_d02_2019_2020_dy_EXP%s.nc'%(tipo,var,mod)
        d1=xr.open_dataset(file)[var]
        if i==0: da1=d1.copy()
        elif i==1: da5=d1.copy()
        else: d1=da5-da1
        ax=fig.add_subplot(gs[j,i],projection=crs)
        fon1=paso_1(d1,ax,var)#       
        ax.set_title(ntit)
        ax.set_title(lplt3[n],loc='left')
        if j==0 and i==0: ax.text(-71.3,-15.9,'Latent heat(W/m2)',rotation=90,verticalalignment='center')
        elif j==1 and i==0: ax.text(-71.3,-15.9,'Sensible heat(W/m2)',rotation=90,verticalalignment='center')
        elif j==2 and i==0: ax.text(-71.3,-15.9,'ALBEDO',rotation=90,verticalalignment='center')
        n=n+1
        agrega_grid(i,j,3,3,ax)
        add_cuadrado(ax)
fig.savefig('out/v3_9plots_v3.png', dpi=400, bbox_inches='tight')

