#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pyproj
import numpy as np
import pandas as pd
import geopandas as gp
from shapely.geometry import Point


def deg_to_nys(lat, lon):
    """
    Convert lat/lon in degrees to NY State Plane.

    Parameters:
    -----------
    lat : float or ndarray
        Latitude.

    lon : float or ndarray
        Longitude.

    Returns:
    --------
    nys : tuple
        A tuple containing the project lat/lon.
    """

    # -- set up the projection and return
    proj = pyproj.Proj(init="epsg:2263", preserve_units=True)

    return proj(lon, lat)
    


def get_cam_info(boro=None, street=True, nys=True, add_ct=True):
    """
    Read in the camera info and sub-select entries.

    Parameters:
    -----------
    boro : str, optional
        Borough name to sub-select.

    street : bool, optional
        Sub-select only cameras that are likely to produce images that 
        contain humans.

    nys : bool, optional
        Project lat/lon to NY State Plane coordinates and add to output.

    add_ct : bool, optional
        Append the census tract to the output dataframe.

    Returns:
    --------
    cam : dataframe
        A pandas dataframe containing the camera parameters.
    """

    # -- Define the path to the file
    cfile = os.path.join("..", "data", "external", "cameras.csv")

    if not os.path.isfile(cfile):
        print("Camera parameters file {0} NOT found!!!".format(cfile))
        return None


    # -- load to dataframe 
    cams = pd.read_csv(cfile)


    # -- project to NY State Plane if desired
    if nys:
        cams["lat_nys"], cams["lon_nys"] = \
            deg_to_nys(cams.lat.values, cams.long.values)


    # -- subselect and return
    ind  = np.ones(len(cams), dtype=bool) 

    if street:
        print("UTILS: sub-selecting cameras likely to contain humans")
        ind &= cams.people == 1.0

    if boro is not None:
        blist = ["Brooklyn", "Bronx", "Manhattan", "Queens", "Staten Island"]
        if boro not in blist:
            print("UTILS: boro must be one of ")
            print("UTILS:   {0}".format(blist))
        print("UTILS: sub-selecting cameras in {0}".format(boro))
        ind &= cams.boro == boro

    cams = cams[ind]


    # -- add the census tract if desired
    if add_ct:
        if not nys:
            print("UTILS: no NYS projection")
            return None
        print("UTILS: finding census tract for each camera")
        cams["BoroCT2010"] = nys_to_ct(cams.lat_nys.values, 
                                       cams.lon_nys.values)

    return cams



def get_precipitation():
    """ ADD DOCS!!! """

    # -- set the filename
    fname = os.path.join("..", "data", "external",
                         "nyc_centralpark_2017precip.csv")

    

def load_ct_shapes(boro=None):
    """
    ADD DOCS!!!
    """

    # -- set the file name
    fname = os.path.join("..", "data", "external", "nyct2010_17b", 
                         "nyct2010.shp")


    # -- check if file exists and load
    if not os.path.isfile(fname):
        print("UTILS: census tract data {0} not found".format(fname))
        return None


    # -- load the data
    ct = gp.read_file(fname)


    # -- subselect boro
    if boro is not None:
        ct = ct[ct.BoroName == boro]

    return ct



def nys_to_ct(lat, lon, ct=None, **kwargs):
    """
    ADD DOCS!!!
    """

    # -- load the census tracts if need be
    if ct is None:
        ct = load_ct_shapes(**kwargs)


    # -- get the number of input values
    try:
        nlat = len(lat)
        nlon = len(lon)

        if nlat != nlon:
            print("UTILS: different number of lat and lon")
            return None
    except:
        lat  = [lat]
        lon  = [lon]
        nlat = 1


    # -- loop through lat/lon
    labs = []
    for ii in range(nlat):
        cont = ct.contains(Point(lat[ii], lon[ii]))
        nct  = cont.sum()
        if nct == 1:
            labs.append(ct[cont].iloc[0].BoroCT2010)
        elif nct == 0:
            labs.append(u'-1')
            print("UTILS: Census Tract not found for {0}, {1}" \
                      .format(lat[ii], lon[ii]))
        else:
            labs.append(u'-1')
            print("UTILS: {0} Census Tracts found for {1}, {2}" \
                      .format(cont.sum(), lat, lon))

    return labs if nlat > 1 else labs[0]



def load_mappluto_shapes(boro, add_ct=False):
    """
    ADD DOCS!!!
    """

    # -- expand borough name definition
    if boro == "Manhattan":
        boro = "MN"

        
    # -- load the MapPLUTO data
    mpfile = os.path.join("..", "data", "external", "mappluto", boro,
                          boro + "MapPLUTO.shp")

    
    # -- add the census tracts
    if not add_ct:
        return gp.read_file(mn_file)

    mnct_file = os.path.join("..", "output", "{0}MP_ct.npy".format(boro))
    if os.path.isfile(mpct_file):
        mp["BoroCT2010"] = np.load(mpct_file)
    else:
        print("UTILS: {0} MapPLUTO census tracts file ".format(boro) + 
              "not found, generating {0}...".format(mnct_file))

        mpx, mpy = np.array([(i.x, i.y) for i in mp.centroid]).T
        mpct     = []
        nmp      = len(mpx)

        for ii in range(nmp):
            if (ii + 1) % 100 == 0:
                print("\rUTILS:   lot {0} of {1}".format(ii + 1, nmp)),
                sys.stdout.flush()

            pnt  = Point(mpx[ii], mpy[ii])
