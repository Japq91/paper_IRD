#!/usr/bin/python
import os
import pandas as pd
import numpy as np
import xarray as xr
from glob import glob as gb

# RUTAS
#exps=['EXP%s'%e for e in np.arange(11)] # ALL experimentos
exps=['EXP0',"EXP1"] #test

r_csv='../input_csv'
r_nc='../data/nc_files'
r_out="../data/csv_files"

############################################################
### FUNCIONES 
############################################################
def extrae_crea(namefile,dataframe,expe):
    ds=xr.open_dataset(namefile)
    ds1=ds.sel(time=slice('2019-12','2020-02'))
    ds2=ds1.mean(dim='time')
    dlo,dla,dto=[],[],[]
    for esta,lo,la in zip(dataframe.est,dataframe.lon,dataframe.lat):
        p1=ds2.sel(lon=lo,lat=la, method='nearest')
        x1,y1,z1=float(p1.lon),float(p1.lat),float(p1[var])
        dlo.append(x1),dla.append(y1),dto.append(z1)
    dataframe['%s_%s'%(expe,var)]=dto
    dataframe['%s-OBS'%expe]=dataframe['%s_%s'%(expe,var)]-dataframe[var]
    return dataframe

############################################################
### CODIGO -> CREA DIFERENCIAS
############################################################
for var in ['pr','t2m']: 
    ifile='%s/%s_complete_stations.csv'%(r_csv,var)
    ofile='%s/%s_dif_AllStation.csv'%(r_out,var)
    df=pd.read_csv(ifile)
    df2=df.copy()
    print(var)
    for exp in exps[:]:
        file=gb('%s/%s*%s*.nc'%(r_nc,exp,var))[0]
        df2=extrae_crea(file,df2,exp)
    df2.to_csv(ofile,index=False)
    
print('DONE! diferencias .CSV creadas')