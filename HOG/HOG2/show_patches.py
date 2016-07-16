import os,sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import glob


if __name__ == "__main__":
	files = glob.glob('*.npy')
	for f in files:
	  arr = np.load(f)
	  imgplot = plt.imshow(arr,cmap="Greys_r")
	  plt.show()
