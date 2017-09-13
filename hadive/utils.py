#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pyproj
import numpy as np
import pandas as pd


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
    


def get_cam_info(boro=None, street=True, nys=True):
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
        ind &= cams.people == 1.0

    if boro is not None:
        ind &= cams.boro == boro

    return cams[ind]
