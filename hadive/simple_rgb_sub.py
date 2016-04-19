#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import matplotlib.pyplot as plt

# -- open the video
cap    = cv2.VideoCapture("video_name.avi")
st, fr = cap.read()

# -- initialize the images and background
img0 = fr.mean(-1)
img  = 1.0*np.zeros_like(fr)
bkg  = 1.0*np.zeros_like(fr)

# -- utilities
alpha = 0.01

# -- initialize visualization
fig, ax = plt.subplots(1,2,figsize=[15,8])
fig.subplots_adjust(0.05,0.05,0.95,0.95)
[i.axis("off") for i in ax]
fi = ax[0].imshow(fr[:,:,::--1])
im = ax[1].imshow(img0,"gist_gray",interpolation="nearest",clim=[0,1])

# -- loop through frames
print("burning in background...")
for ii in range(200):
    st, fr[:,:,:] = cap.read()
    img[:,:,:]    = fr
    bkg[:,:,:]    = (1.0-alpha)*bkg + alpha*img

for ii in range(1000):
    st, fr[:,:,:] = cap.read()
    img[:,:,:]    = fr
    bkg[:,:,:]    = (1.0-alpha)*bkg + alpha*img

    fi.set_data(fr[:,:,::-1])
    im.set_data(np.abs(img-bkg).max(2)>30)
    fig.canvas.draw()
    plt.pause(1e-3)
