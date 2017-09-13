#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd


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
