#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import calmap
import pandas as pd
import matplotlib.pyplot as plt

def uptime(data, verbose=True):
    """
    Plot the uptime of the counter.
    """

    # -- check if input is a file
    if type(data) is str:
        if verbose:
            print("reading pedestrian data from {0}...".format(data))
        data = pd.read_feather(data)

    # -- count number of images processed
    if verbose:
        print("counting number of images processed per day...")
        t0   = time.time()
        impd = data.set_index("date").resample("D").size()
        print("  finished in {0}s for {1} entries.".format(time.time() - t0,
                                                           len(data)))

    # -- make the plot
    fig, [ax] = calmap.calendarplot(impd[impd != 0], cmap="viridis_r",
                                    fig_kws=dict(figsize=(5, 2)))
    ax.set_ylabel("")
    ax.set_xlim(6 * 4, 12*4)
    ax.tick_params(axis="both", which="both", labelsize=12)

    # -- show and write to file
    oname = os.path.join("..", "output", "up_time.png")
    fig.savefig(oname, clobber=True)
    plt.show()

    return
