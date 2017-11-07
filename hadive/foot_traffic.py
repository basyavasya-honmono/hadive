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
        

    

    def bin_timeseries(self, interval="15min", full=False):
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

            # set the interval
            if "min" not in interval.lower():
                print("FOOT_TRAFFIC: sampling interval must be in of the "
                      " form 'Xmin' where X is number of minutes!")
                return 
            self.interval = interval

            # resample the counts
            self.counts_bin = self.counts.set_index("date").groupby("cam_id") \
                                    .resample(interval).mean()[["count"]]

            # reindex to make sure time range is covered for all cameras
            self.counts_bin = self.counts_bin.reindex( \
                                pd.MultiIndex.from_product( \
                                    self.counts_bin.index.levels))
                
        return


    
    def select(self, cam_id=None, st=None, en=None, date=None, ind=None):
        """
        ADD DOCS!!!
        """

        # -- alert the user
        if date is not None:
            print("FOOT_TRAFFIC: single date not implemented yet!")
            return None

        # -- check if selecting on cam ID
        if cam_id is None:
            cam_id = slice(None)
            ncam   = len(self.cams)
        else:
            try:
                ncam = len(cam_id)
            except TypeError:
                ncam = 1

        # -- if no start and end times, return cam IDs
        if (st is None) & (en is None) & (ind is None):
            return self.counts_bin.loc[cam_id]
        elif (ind is None) & ((st is None) | (en is None)):
            print("FOOT_TRAFFIC: must set BOTH start and end!")
            return None

        # -- get temporal index
        if ind is None:
            if type(st) is not datetime.datetime:
                st = datetime.datetime(*st)
            if type(en) is not datetime.datetime:
                en = datetime.datetime(*en)

            index = self.counts_bin.index.levels[1]
            ind   = (index >= st) & (index < en)

        # -- return full time series for a given camera
        return self.counts_bin.loc[cam_id].loc[ind.tolist() * ncam]



    def weekdays(self, cam_id=None):
        """
        ADD DOCS!!!
        """

        return self.select(cam_id, ind=self.counts_bin.index \
                               .levels[1].weekday < 5)


    def weekends(self, cam_id=None):
        """
        ADD DOCS!!!
        """

        return self.select(cam_id, ind=self.counts_bin.index \
                               .levels[1].weekday >= 5)


    def counts_matrix(self, sampled=True):
        """
        ADD DOCS!!!
        """

        # -- alert the user
        if not sampled:
            print("FOOT_TRAFFIC: only implemented for sampled data")
            return None
        
        # -- unstack the sampled counts
        ustack = self.counts_bin["count"].unstack(0)

        # -- return the values
        return ustack.values, ustack.index.values, ustack.columns.values
