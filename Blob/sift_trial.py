import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import sift
from PIL import Image


imname = 'sift1.jpg'
im1 = np.array(Image.open(imname).convert('L'))
sift.process_image(imname,'sift1.sift')
l1, d1 = sift.read_features_from_file('sift1.sift')

plt.figure()
plt.gray()
sift.plot_features(im1, l1, circle=True)
plt.show()