# the current version takes in 3 consecutive images and returns the list of the blob centroids 
import numpy as np
import cv2
from matplotlib import pyplot as plt
from scipy import ndimage

def detector(image_list):
	params = cv2.SimpleBlobDetector_Params()

# Change thresholds
	params.minThreshold = 10
	params.maxThreshold = 200

# Filter by Area.
	params.filterByArea = True
	params.minArea = 100
	params.maxArea = 1000

# Filter by Circularity
	params.filterByCircularity = True
	params.minCircularity = 0.05

# Filter by Convexity
	params.filterByConvexity = True
	params.minConvexity = 0.05

# Filter by Inertia
	params.filterByInertia = False
	params.minInertiaRatio = 0.01


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
	im = cv2.imread(image_list[0])

# Finding the minimal values pixelwise
	minimal = np.minimum(differences[0], differences[1])
	#minimal = np.where(minimal>np.percentile(minimal, 98), np.percentile(minimal, 100), np.percentile(minimal,96))
	
# Joining the smaller blobs together
	minimal = ndimage.gaussian_filter(minimal, 5)
	mini = np.min(minimal)
	maxi = np.max(minimal)

# Scaling the brightnesses to 0..25
	minimal = minimal / maxi * 255
	minimal = minimal.astype(int)
#minimal = cv2.cvtColor(minimal, cv2.CV_8U)
# Identifying and counting the blobs
	#label_, n_blobs = ndimage.label(minimal> np.percentile(minimal, 60)) 

# Detecting centroids
	detector = cv2.SimpleBlobDetector(params)
	keypoints = detector.detect(im)
	centroids = []
	

	for k in keypoints:
		centroids.append([k.pt[0], k.pt[1]])

# Script to see what blobs look like	
	#plt.imshow(minimal, cmap = 'Greys_r')
	#plt.show()

	return centroids
