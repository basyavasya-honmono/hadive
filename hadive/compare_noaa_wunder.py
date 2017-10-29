#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd

# -- read noaa
nname = os.path.join("..", "data", "external",
                     "nyc_centralpark_2017precip.csv")
noaa  = pd.read_csv(nname, parse_dates=["DATE"])

# -- read weather underground and sum to date
wname = os.path.join("..", "output", "wunder_knyc_conditions.feather")
wund  = pd.read_feather(wname).set_index("time").resample("D").sum()
wund.reset_index(inplace=True)

# -- merge the two
comb = pd.merge(noaa, wund, how="outer", left_on=["DATE"], right_on=["time"])
comb.dropna(inplace=True)

# -- fit a linear model
m, b = np.polyfit(comb["PRCP"], comb["precip"], 1)

# -- plot it
ax  = comb.plot("PRCP", "precip", kind="scatter", xlim=[0, 7], ylim=[0, 7])
lin = ax.plot(comb["PRCP"], m * comb["PRCP"] + b, color="lime",
              label="{0} * NOAA + {1}".format(np.round(m, 3), np.round(b, 3)))
fig = ax.get_figure()
ax.legend(loc="center right")
ax.set_xlabel("NOAA precipitation [inches]")
ax.set_ylabel("Weather Underground precipitation [inches]")
fig.savefig(os.path.join("..", "output", "compare_noaa_wunder.png"),
            clobber=True, facecolor=fig.get_facecolor())
