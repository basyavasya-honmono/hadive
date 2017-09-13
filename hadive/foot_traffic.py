#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
from utils import *


class FootTraffic(object):
    """
    A container for the HADIVE foot traffic detection results.
    """

    def __init__(self, dpath, dfile=None, dates=["date"]):
        """
        ADD DOCS!!!
        """

        # -- set the file name
        self.fname = dpath if dfile == None else os.path.join(dpath, dfile)

        # -- read the file 
        print("FOOT_TRAFFIC: reading file {0}...".format(self.fname))
        self.data = pd.read_csv(self.fname, parse_dates=dates)

        return


    def select_cams(self, cam_id=None):
        """
        ADD DOCS!!!
        """

        # -- sub-select cameras
        if cam_id is not None:
            ft_cams = self.data.cam_id.unique()
            missing = (~np.in1d(cam_id, ft_cams)).nonzero()[0]

            for ii in missing:
                print("FOOT_TRAFFIC: cam_id {0} not found".format(cam_id[ii]))

            self.data_sub = self.data[self.data.cam_id.isin(cam_id)]

        return


    def get_cams(self, **kwargs):
        """
        AND DOCS!!!
        """

        # -- get the camera parameters
        self.cams = get_cam_info(**kwargs)

        # -- sub-select based on those cameras
        self.select_cams(self.cams.cam_id)

        return
