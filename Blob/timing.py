import image_list
import numpy as np
import cv2
from matplotlib import pyplot as plt


# path.txt contains the address of the directory with images
with open('path.txt') as f:
    path = f.readlines()[0]
print path

# Getting addresses of the first 20 images that were recorded from 7 a.m. to 7 p.m.
day_images = image_list.list_images(path, 7, 19, 20)
print day_images


# Loading the image in grayscale
img = cv2.imread(day_images[0], cv2.IMREAD_GRAYSCALE)

# Measuring time spent of the operations 
c0 = cv2.getTickCount()
# Histogram equalization
heq = cv2.equalizeHist(img)
print "Time spent on standard histogram equalization: ", (cv2.getTickCount() - c0)
c0 = cv2.getTickCount()
# Clahe equalization
clahe = cv2.createCLAHE(clipLimit = 1.6, tileGridSize = (16, 12))
cla = clahe.apply(img)
print "Time spent on CLAHE: ", (cv2.getTickCount() - c0)

# Staking up original, equalized and Clahe equalized images horizontally adding their histograms to the right
res = np.vstack((img, heq, cla))
#es = np.vstack((h1, h2, h3))
#res = np.vstack((np.hstack((img, h1)), np.hstack((heq, h2)), np.hstack((cla, h3))))

# Show the result
plt.imshow(res, cmap='Greys_r')
plt.show()
cv2.destroyAllWindows()

# Histogram calculation
plt.figure(figsize = (350, 240))
h1 = plt.hist(img.ravel(), 256, [0, 256])
h2 = plt.hist(heq.ravel(), 256, [0, 256])
h3 = plt.hist(cla.ravel(), 256, [0, 256])
#res = np.hstack((h1, h2, h3))

plt.show()
cv2.destroyAllWindows()

# Measuring time spent of the histograms based on 20 images
c0 = cv2.getTickCount()
for m in day_images:
	img = cv2.imread(m, cv2.IMREAD_GRAYSCALE)
	heq = cv2.equalizeHist(img)	
# Histogram equalization
c1 = cv2.getTickCount()
print "Average time spent on standard histogram equalization (20 measurements): ", ((c1 - c0)*1.0/20)

c0 = cv2.getTickCount()
clahe = cv2.createCLAHE(clipLimit = 1.6, tileGridSize = (16, 12))
for m in day_images:
	img = cv2.imread(m, cv2.IMREAD_GRAYSCALE)
	cla = clahe.apply(img)
# Histogram equalization
c1 = cv2.getTickCount()
print "Average time spent on CLAHE (20 measurements): ", ((c1 - c0)*1.0/20)

#cv2.imwrite('messigray.png',img)
