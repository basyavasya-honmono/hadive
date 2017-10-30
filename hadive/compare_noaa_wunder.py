#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -- read noaa
nname = os.path.join("..", "data", "external",
                     "nyc_centralpark_2017precip.csv")
noaa  = pd.read_csv(nname, parse_dates=["DATE"])

# -- read weather underground and sum to date
wname = os.path.join("..", "output", "wunder_knyc_conditions.feather")
wundr = pd.read_feather(wname)
wund  = wundr.set_index("time").resample("D").sum()["precip"].reset_index()

# -- add daily total
wund["daily_precip"] = wundr.set_index("time").resample("D") \
                                        .first().reset_index()["daily_precip"]

# -- merge the two
comb = pd.merge(noaa, wund, how="outer", left_on=["DATE"], right_on=["time"])
comb.dropna(inplace=True)

# -- fit a linear model
ml, bl = np.polyfit(comb["PRCP"], comb["precip"], 1)
mr, br = np.polyfit(comb["daily_precip"], comb["precip"], 1)

# -- plot it
fig, [axl, axr, axb] = plt.subplots(1, 3, figsize=[10, 3.5])

comb.plot("PRCP", "precip", kind="scatter", xlim=[0, 7], ylim=[0, 7], ax=axl)
linl = axl.plot(comb["PRCP"], ml * comb["PRCP"] + bl, color="lime",
                label="{0} * NOAA + {1}".format(np.round(ml, 3),
                                                np.round(bl, 3)))
fig = axl.get_figure()
axl.legend(loc="lower right", fontsize="small")
axl.set_xlabel("NOAA daily precipitation [inches]")
axl.set_ylabel("WU summed precipitation [inches]")

comb.plot("daily_precip", "precip", kind="scatter", xlim=[0, 7], ylim=[0, 7],
          ax=axr, color="skyblue")
linr = axr.plot(comb["PRCP"], mr * comb["PRCP"] + br, color="mediumpurple",
                label="{0} * WU + {1}".format(np.round(mr, 3),
                                              np.round(br, 3)))
axr.legend(loc="lower right", fontsize="small")
axr.set_xlabel("WU daily precipitation [inches]")
axr.set_ylabel("")
axr.set_yticklabels("")

comb.plot("PRCP", "daily_precip", kind="scatter", xlim=[0, 4], ylim=[0, 4],
          ax=axb, color="gold")
axb.set_yticks(range(5))
axb.set_xlabel("NOAA daily precipitation [inches]")
axb.set_ylabel("WU daily precipitation [inches]")

fig.savefig(os.path.join("..", "output", "compare_noaa_wunder.png"),
            clobber=True, facecolor=fig.get_facecolor())
