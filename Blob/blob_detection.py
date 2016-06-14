import numpy as np
import cv2
# Script to see what blobs look like
# from matplotlib import pyplot as plt
from scipy import ndimage


def detector(image_list):
	edges = []
	for i in image_list:
# Loading the image in grayscale
		img = cv2.imread(i, cv2.IMREAD_GRAYSCALE)

# Equalizing histogram
		clahe_ = cv2.createCLAHE(clipLimit = 1, tileGridSize = (1, 1))
		clahe = clahe_.apply(img)

# Filtering out noise and enforcing the edges
		bilateral = cv2.bilateralFilter(clahe, 7, 5, 5)

# Calculating Laplacian
		laplacian = cv2.Laplacian(bilateral, cv2.CV_32F, ksize = 5, scale = 1, delta = 0)
		edges.append(laplacian)

# Calculating background and subtracting it
	differences = []
	for i in range(1, len(edges)):
		differences.append(abs(edges[0]-edges[i]))
			
# Finding the minimal values pixelwise
	minimal = np.minimum(differences[0], differences[1])
	#minimal = np.where(minimal>np.percentile(minimal, 98), np.percentile(minimal, 100), np.percentile(minimal,96))
	n_blobs = 0

# Joining the smaller blobs together
	minimal = ndimage.gaussian_filter(minimal, 4)
	
# Identifying and counting the blobs
	label_, n_blobs = ndimage.label(minimal> 50) 

# Script to see what blobs look like	
#	plt.imshow(minimal, cmap = 'Greys_r')
#	plt.show()

	return n_blobs
