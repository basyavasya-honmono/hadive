import image_list
import numpy as np
import cv2
from matplotlib import pyplot as plt
from PIL import Image

# path.txt contains the address of the directory with images
with open('path.txt') as f:
    path = f.readlines()[0]
print path

# Getting addresses of the first 10 images for the camera named "8_Ave__14_St" that were recorded from 7 a.m. to 7 p.m.
day_images = image_list.list_images(path, "8_Ave__14_St", 7, 19, 10)
print day_images

# Processing time
c0 = cv2.getTickCount()

edges = []
for image_ in day_images:
# Loading the image in grayscale
	img = cv2.imread(image_, cv2.IMREAD_GRAYSCALE)

# Equalizing histogram
	clahe_ = cv2.createCLAHE(clipLimit = 1, tileGridSize = (1, 1))
	clahe = clahe_.apply(img)

# Filtering out noise and enforcing the edges
	bilateral = cv2.bilateralFilter(clahe, 7, 5, 5)

# Calculating Laplacian
	laplacian = cv2.Laplacian(bilateral, cv2.CV_32F, ksize = 9, scale = 1, delta = 0)
	edges.append(laplacian)

# Calculating background and subtracting it
#av = edges[0]
#for e in edges:
#	av = av + e
#av = av / 11
av = edges[0]*0.05 + edges[1]*0.15 + edges[2]*0.1 + edges[3]*0.1 + edges[4]*0.1 + edges[5]*0.1 + edges[6]*0.1 + edges[7]*0.1 + edges[8]*0.1+edges[9]*0.1
edge1 = edges[0] - av

print "Total processing time is ", (cv2.getTickCount() - c0)

# Blob detection
#sift = cv2.SIFT()

#pic = Image.fromarray(lap3, 'RGB')
#pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
#kp, des = cv2.SIFT().detectAndCompute(pic, None)

#newimg = cv2.drawKeypoints(lap3, kp)
#lap3 = lap3.convertTo(CV_8U);

res = np.hstack((edges[0], edge1))

# Plotting the processed image
plt.imshow(res, cmap = 'Greys_r')

plt.show()
cv2.destroyAllWindows()


'''
# Other 
# Direct edge subtraction
#lap1 = edges[0] - (edges[0] + edges[1])/2
#lap2 = edges[1] - (edges[0] + edges[1])/2
#lap3 = edges[0] - 0.5*edges[1] - 0.5*edges[0]

# Edge detection using Scharr Kernel 
# X component
Gx = cv2.Sobel(bil, cv2.CV_64F, 1, 0, ksize = 1, scale = 1, delta = 0, borderType = cv2.BORDER_DEFAULT)
absGx = cv2.convertScaleAbs(Gx)
# Y component
Gy = cv2.Sobel(bil, cv2.CV_64F, 0, 1, ksize = 1, scale = 1, delta = 0, borderType = cv2.BORDER_DEFAULT)
absGy = cv2.convertScaleAbs(Gy)
# Combining the X and Y components
gra = cv2.addWeighted(absGx, 0.5, absGy, 0.5, 0)

res = cv2.adaptiveThreshold(lap, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 5)
ret, res = cv2.threshold(src = lap, thresh = 50, maxval = 100, type = cv2.THRESH_TOZERO)

img = cv2.rectangle(lap, (135, 54), (135+50, 54 + 50), (255, 255, 255), 10)

res = np.hstack((img, edg, edg2))
'''