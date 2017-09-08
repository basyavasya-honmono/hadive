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


# -- convert cam locations to NY state plane
proj = pyproj.Proj(init="epsg:2263", preserve_units=True)
cams["lat_nys"], cams["lon_nys"] = zip(*[proj(i, j) for i, j in 
                                         zip(cams.long, cams.lat)])


# -- Load the foot traffic data
print("loading the foot traffic data...")
ft_file = os.path.join("..", "data", "results", "hadive-data.csv")
ft      = pd.read_csv(ft_file, parse_dates=["date"])


# -- select only those cameras in both the cams and foot traffic dataframes
ft   = ft[ft.cam_id.isin(cams.cam_id)]
cams = cams[cams.cam_id.isin(ft.cam_id)]


# -- Load the census tract shapefile
ct_file = os.path.join("..", "data", "external", "nyct2010_17b", 
                       "nyct2010.shp")
ct      = gp.read_file(ct_file)
ct      = ct[ct.BoroName == "Manhattan"]


# -- Load the MapPLUTO manhattan shapefile
print("loading MapPLUTO Manhattan...")
mn_file = os.path.join("..", "data", "external", "mappluto", "Manhattan", 
                       "MNMapPLUTO.shp")
mn      = gp.read_file(mn_file)


# -- For each camera, assign a census tract
cam_ct = []

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
mn_ct_file = "mn_ct.npy"

if not os.path.isfile(mn_ct_file):
    mn_x, mn_y = np.array([(i.x, i.y) for i in mn.centroid]).T
    mn_ct      = []
    nmn        = len(mn_x)
    
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
else:
    mn_ct = np.load(mn_ct_file)

mn["BoroCT2010"] = mn_ct


# -- calculate the number of residential and commercial units for each CT
mn_sum = mn.groupby("BoroCT2010").sum().reset_index()
resu   = mn_sum.UnitsRes
resc   = mn_sum.UnitsTotal - resu
ct     = ct.merge(cams.groupby("BoroCT2010").size().reset_index(). \
                      rename(columns={0:"NumCams"}), how="left")
ct     = ct.merge(mn_sum[["BoroCT2010", "UnitsRes", "UnitsTotal"]], 
                  on="BoroCT2010")

ct["UnitsComm"] = ct.UnitsTotal - ct.UnitsRes
ct["UnitsRat"]  = ct.UnitsRes.astype(float) / \
    (ct.UnitsTotal + (ct.UnitsTotal == 0))


# -- For each camera, get the mean weekday/weekend behavior
wd_full = ft[ft.date.dt.weekday < 5].copy()
we_full = ft[ft.date.dt.weekday >= 5].copy()

wd_full["time"]  = wd_full.date.dt.time
wd_full["day"]   = pd.datetime.today().date()
wd_full["dtmod"] = [pd.datetime.combine(i, j) for i, j in
                    zip(wd_full.day, wd_full.time)]

wd_full.set_index("dtmod", inplace=True)
wd = wd_full.groupby("cam_id").resample("5Min").mean()[["count"]].unstack(1)
wd_vals = wd.values
avg = wd_vals.mean(1, keepdims=True)
sig = wd_vals.std(1, keepdims=True)
wd_norm = (wd_vals - avg) / (sig + (sig == 0))
bad     = np.isnan(wd_norm[:, 0])
wd_norm = wd_norm[~bad]

we_full["time"]  = we_full.date.dt.time
we_full["day"]   = pd.datetime.today().date()
we_full["dtmod"] = [pd.datetime.combine(i, j) for i, j in
                    zip(we_full.day, we_full.time)]

we_full.set_index("dtmod", inplace=True)
we = we_full.groupby("cam_id").resample("5Min").mean()[["count"]].unstack(1)
we_vals = we.values
avg = we_vals.mean(1, keepdims=True)
sig = we_vals.std(1, keepdims=True)
we_norm = (we_vals - avg) / (sig + (sig == 0))
bad     = np.isnan(we_norm[:, 0])
we_norm = we_norm[~bad]
## GGD: NOTE THAT cam_id 463 DOES NOT APPEAR IN WEEKEND DATA!!!
wd_norm = wd_norm[~bad]


# -- PCA across cameras
#vals_all = np.hstack((wd_norm, we_norm))
#pca = PCA(n_components=2)




# -- Plot PCA amplitudes vs num of residential units vs num of commercial units
