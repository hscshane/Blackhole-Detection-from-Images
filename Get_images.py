# This script is based on the Image_Classification_preprocess.ipynb
# Run this script in background so you can logout your session

from io import BytesIO
from astroquery.simbad import Simbad
from urllib.parse import quote
from urllib import request
import pandas as pd
import numpy as np
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.visualization import astropy_mpl_style
from PIL import Image

df_coord = pd.read_csv('coords.csv')
width = 64
height = 64
fov = 0.05 # in decimal degrees
hips = 'DSS2/red'

df_train = pd.read_csv('train.csv')
df_dev = pd.read_csv('dev.csv')

dic = {'train': df_train, 'dev': df_dev}
for name, df in dic.items():
    # get ra and dec list
    idx = df['index'].to_numpy()
    ras = df['RA'].to_numpy()
    decs = df['DEC'].to_numpy()
    agns = df['AGN'].to_numpy()

    # initialize the image numpy array with shape: (sample_size, width, height, channel)
    url = f'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?hips={quote(hips)}&width={width}&height={height}&fov={fov}&projection=TAN&coordsys=icrs&ra={ras[0]}&dec={decs[0]}&format={"jpg"}'
    res = request.urlopen(url).read()
    img = Image.open(BytesIO(res))
    data = np.asarray(img)
    data = data[:,:,0]
    data = data.reshape(1,data.shape[0], data.shape[1], 1)

    # loop through the whole datasets starting from index=1
    for i in range(1,len(ras)):
        ra = ras[i]
        dec = decs[i]
        url = f'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?hips={quote(hips)}&width={width}&height={height}&fov={fov}&projection=TAN&coordsys=icrs&ra={ra}&dec={dec}&format={"jpg"}'
        res = request.urlopen(url).read()
        img = Image.open(BytesIO(res))
        data1 = np.asarray(img)
        data1 = data1[:,:,0]
        data1 = data1.reshape(1,data1.shape[0], data1.shape[1], 1)
        data = np.concatenate((data, data1), axis=0)
        
    # save to file
    h5f = h5py.File(Image_path+f'{name}.h5', 'w')
    dset1 = h5f.create_dataset(f"{name}_set_x", data=data)
    dset2 = h5f.create_dataset(f"{name}_set_y", data=agns)
    h5f.close()