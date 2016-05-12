#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob

if __name__=="__main__":

    # -- get the file list
    flist = sorted(glob.glob("../../../share/output_20160501/*.jpg"))

    # -- peel off the camera names
    cams = ["_".join(i.split("_")[2:]).replace(".jpg","") for i in flist]

    # -- create camera name directories
    cmd = "mkdir dot_images/{0}"
    dum = [os.system(cmd.format(i)) for i in unique(cams)]

    # -- copy the images to the different camera directories
    cmd2 = "cp {0} ../dot_images/{1}/."
    for ii in range(len(flist)):
        if (ii+1)%10000==0:
            print("finished copying {0} of {1}...".format(ii+1,len(flist)))

        os.system(cmd2.format(flist[ii],cams[ii]))
