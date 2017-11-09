#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import numpy as np
execfile("foot_traffic.py")


# -- load the foot traffic
fname = os.path.join("..", "output", "hadive_oct.feather")
ft = FootTraffic(fname)

# -- sub-select cameras
ft.get_cams(boro="Manhattan", add_ct=False)
ft.select_cams()

# -- bin the time series at 15 minute intervals
ft.bin_timeseries()

# -- get the weekends and weekdays
wd = ft.weekdays()
we = ft.weekends()

# # -- plot an example
# cid = 253
# ax = wd.loc[cid].plot(lw=0.3)
# we.loc[cid].plot(ax=ax, lw=0.3)

# -- pull off the values
cnts, dts, cids = ft.counts_matrix()
avg = np.nanmean(cnts, 1)
plot(dts, avg)


# -- test average weekday
foo = wd.copy()

mon.reset_index(inplace=True)
mon["time"] = mon.date.dt.time
mmon = mon.groupby(["cam_id", "time"]).mean()
mmon.loc[1038].plot()

# # -- pull off three cameras for one day
# t0 = time.time()
# vals = ft.select([163, 165, 1038], (2017, 9, 1, 12, 15), (2017, 9, 2))
# print("selected in {0}s".format(time.time() - t0))

# # -- get the precipitation

# # -- get individual camera time series at 5-minute intervals

