#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pyproj
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gp
from shapely.geometry import Point
from sklearn.decomposition import PCA


# -- Load the camera locations file
cam_file = os.path.join("..", "data", "external", "cameras.csv")
cams     = pd.read_csv(cam_file)
cams     = cams[cams.boro == "Manhattan"]


# -- Load the census tract shapefile
ct_file = os.path.join("..", "data", "external", "nyct2010_17b", 
                       "nyct2010.shp")
ct      = gp.read_file(ct_file)
ct      = ct[ct.BoroName == "Manhattan"]


# -- Load the MapPLUTO manhattan shapefile
mn_file = os.path.join("..", "data", "external", "mappluto", "Manhattan", 
                       "MNMapPLUTO.shp")
mn      = gp.read_file(mn_file)


# -- Load the foot traffic data
ft_file = os.path.join("..", "data", "results", "hadive-data.csv")
ft      = pd.read_csv(ft_file, parse_dates=["date"])


# -- convert cam locations to NY state plane
proj = pyproj.Proj(init="epsg:2263", preserve_units=True)
cams["lat_nys"], cams["lon_nys"] = zip(*[proj(i, j) for i, j in 
                                         zip(cams.long, cams.lat)])


# -- For each camera, assign a census tract
ct_x, ct_y = np.array([(i.x, i.y) for i in ct.centroid]).T
rad2       = 7500.**2 # feet
cam_ct     = []

for ii in range(len(cams)):
    pnt  = Point(cams.iloc[ii].lat_nys, cams.iloc[ii].lon_nys)
    cont = ct[ct.contains(pnt)]
    if len(cont) == 1:
        cam_ct.append(cont.iloc[0].BoroCT2010)
    elif len(cont) == 0:
        cam_ct.append(0)
        print("Census Tract not found for {0}!!!".format(cams.iloc[ii].cam_id))
    else:
        cam_ct.append(0)
        print("{0} Census Tracts found for {1}!!!" \
                  .format(cont.sum(), cams.iloc[ii].cam_id))
        
cams["BoroCT2010"] = cam_ct


# -- For each tax lot assign a census tract (by building centroid)
mn_x, mn_y = np.array([(i.x, i.y) for i in mn.centroid]).T
mn_ct = []
nmn   = len(mn_x)

for ii in range(nmn):
    if (ii + 1) % 100 == 0:
        print("{0} of {1}".format(ii + 1, nmn))

    pnt  = Point(mn_x[ii], mn_y[ii])
    cont = ct[ct.contains(pnt)]

    if len(cont) == 1:
        mn_ct.append(cont.iloc[0].BoroCT2010)
    elif len(cont) == 0:
        mn_ct.append(0)
        print("Census Tract not found for {0}!!!".format(mn.iloc[ii].BBL))
    else:
        mn_ct.append(0)
        print("{0} Census Tracts found for {1}!!!" \
                  .format(len(cont), mn.iloc[ii].BBL))

np.save("mn_ct.npy", np.array(mn_ct))
mn["BoroCT2010"] = mn_ct


# -- calculate the number of residential and commercial units for each CT
mn_sum = mn.groupby("BoroCT2010").sum().reset_index()
resu   = mn_sum.UnitsRes
resc   = mn_sum.UnitsTotal - resu
ct     = ct.merge(mn_sum[["BoroCT2010", "UnitsRes", "UnitsTotal"]], 
                  on="BoroCT2010")
ct["UnitsComm"] = ct.UnitsTotal - ct.UnitsRes
ct["UnitsRat"] = ct.UnitsRes.astype(float) / (ct.UnitsTotal +
                                              (ct.UnitsTotal == 0))

ct = ct.merge(cams.groupby("BoroCT2010").size().reset_index(). \
              rename(columns={0:"NumCams"}), how="left")


# -- For each camera, get the mean weekday/weekend behavior
temp = ft.copy()

temp_wd = temp[temp.date.dt.weekday < 5].copy()
temp_we = temp[temp.date.dt.weekday >= 5].copy()


temp_wd["time"] = temp_wd.date.dt.time
temp_wd["day"] = pd.datetime.today().date()
temp_wd["dtmod"] = [pd.datetime.combine(i, j) for i, j in
                 zip(temp_wd.day, temp_wd.time)]

temp_wd.set_index("dtmod", inplace=True)
wd = temp_wd.groupby("cam_id").resample("1Min").mean()
wd = wd[wd.index.levels[0].isin(cams.cam_id)]



temp_we["time"] = temp_we.date.dt.time
temp_we["day"] = pd.datetime.today().date()
temp_we["dtmod"] = [pd.datetime.combine(i, j) for i, j in
                 zip(temp_we.day, temp_we.time)]

temp_we.set_index("dtmod", inplace=True)
we = temp_we.groupby("cam_id").resample("1Min").mean()


# -- PCA across cameras
vals_wd
vals_we
pca = PCA(n_components=2)


# -- Plot PCA amplitudes vs num of residential units vs num of commercial units
