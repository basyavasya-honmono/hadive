''' This is a sample of running a blob detector count. 
	The detector counts blobs on the first image. 2 others are used to estimate the background.
	Currently works with 3 consecutive images. The less the time difference, the better.
'''
from blob_detection import detector
print detector(['1.jpg', '2.jpg', '3.jpg'])
