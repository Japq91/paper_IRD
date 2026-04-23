#!/usr/bin/python
import os
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from glob import glob as gb

### RUTAS
exp='EXP1' ### cambiar segun la carpeta de experimento. ejemplo: "EXP8"

r_in='../input_nc'
r_out='../data/nc_files'

os.system(f"mkdir -p {r_out}")

############################################################
### FUNCIONES
############################################################
def ordena_wrf_file(file,var0,var1):
    a2=xr.open_dataset(file)[var1]#+resta
    lati=a2.XLAT[:,0].values
    loni=a2.XLONG[0,:].values
    tiem=pd.date_range('2019-11',freq='D',periods=len(a2.XTIME))
    newdata=a2.values
    d=xr.Dataset({var0:(("time","lat","lon"),newdata)},coords={"lat":lati,"lon":loni,'time':tiem})
    d.to_netcdf('%s/%s_%s_d02_dy.nc'%(r_out,exp,var0)) 
    return d

def plot_prueba(d,var0,expe):
    if 't' in var: d1=d.groupby('time.month').mean()
    else: d1=d.groupby('time.month').sum()
    d1[var0].plot(x="lon", y="lat", col="month", col_wrap=4)
    plt.title(expe)
    plt.savefig(f'{r_out}/{expe}_{var0}.png', dpi=100, bbox_inches='tight') 
    plt.close()

############################################################
### CODIGO
############################################################
file_input=f'{r_in}/{exp}/wrf_d02_dy_{exp}.nc'

for var in ['pr','t2m']:
    if var=='t2m': varfile='T2'
    else: varfile=var
    ds=ordena_wrf_file(file_input,var,varfile)
    plot_prueba(ds,var,exp)

print("DONE! creacion archivos netcdf")