#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd


def get_cam_info(boro=None, street=True):
    """
    Read in the camera info and sub-select entries.

    Parameters:
    -----------
    boro : str, optional
        Borough name to sub-select.

    street : bool, optional
        Sub-select only cameras that are likely to produce images that 
        contain humans.

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

    # -- load to dataframe and subselect
    cams = pd.read_csv(cfile)
    ind  = np.ones(len(cams), dtype=bool) 

    if street:
        ind &= cams.people == 1.0

    if boro is not None:
        ind &= cams.boro == boro

    return cams[ind]
