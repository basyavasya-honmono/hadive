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

        if self.fname.endswith("csv"):
            print("FOOT_TRAFFIC:   dropping NaN rows")
            self.counts_full = pd.read_csv(self.fname, parse_dates=dates) \
                                 .dropna()
        elif self.fname.endswith("feather"):
            self.counts_full = pd.read_feather(self.fname)
        else:
            print("FOOT_TRAFFIC: only .csv and .feather formats supported!")
            
        return


    def select_cams(self, cam_id=None):
        """
        ADD DOCS!!!
        """

        # -- sub-select cameras
        if cam_id is not None:
            ft_cams = self.counts_full.cam_id.unique()
            missing = (~np.in1d(cam_id, ft_cams)).nonzero()[0]

            print("FOOT_TRAFFIC: sub-selecting {0} cameras" \
                  .format(len(cam_id)))

            for ii in missing:
                print("FOOT_TRAFFIC:   cam_id {0} not found" \
                      .format(cam_id[ii]))

            self.counts = self.counts_full[self.counts_full.cam_id \
                                           .isin(cam_id)]

        else:
            try:
                self.cams
            except:
                print("FOOT_TRAFFIC: camera file not yet loaded!")
                return

            self.select_cams(self.cams.cam_id.values)


        return


    def get_cams(self, **kwargs):
        """
        ADD DOCS!!!
        """

        # -- get the camera parameters
        self.cams = get_cam_info(**kwargs)

        return


    def merge_ct_residential(self):
        """
        ADD DOCS!!!
        """

        # -- alert user
        print("FOOT_TRAFFIC: merging with census tracts not yet implemented!")

        return


    def merge_precipitation(self, interval=None):
        """
        ADD DOCS!!!
        """

        # -- alert user
        if interval is None:
            try:
                self.interval
            except:
                print("FOOT_TRAFFIC: must set sampling interval or "
                      "use bin_timeseries!")
            return
        else:
            interval = self.interval    
        
        # -- get the precipitation data and sum to the day
        precip = get_precipitation().set_index("time").resample(interval) \
                                        .interpolate()["precip"].reset_index()

        # -- merge with counts and/or binned counts
        

    

    def bin_timeseries(self, interval="15Min", full=False):
        """
        ADD DOCS!!!
        """

        # -- test for selection
        if not full:
            try:
                self.counts
            except:
                print("FOOT_TRAFFIC: the data has not been sub-selected by "
                      "camera")
                print("FOOT_TRAFFIC:   use get_cams() and full=False")
                return

            print("FOOT_TRAFFIC: binning time series to {0} interval..." \
                  .format(interval))

            self.interval   = interval
            self.counts_bin = self.counts.set_index("date").groupby("cam_id") \
                                    .resample(interval).mean()[["count"]]
        return


    
    def select(self, cam_id=None, year=None, month=None, day=None):
        """
        ADD DOCS!!!
        """

        # -- return full time series for a given camera
        return self.counts_bin.loc[cam_id]

        
# # testing
# 11033247
# counts.loc[counts.index == 11033247, "count"] = np.NaN

# fname = '../data/results/hadive-data.csv'
