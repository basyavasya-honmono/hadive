import os
import sys
import pylab as pl 
import numpy as np 
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import time
import pandas as pd 


if __name__ == '__main__':
	
	labels = []
	images = []
	arr = []

	print "Hello Neo, \n \
	Welcome to HaDiVe.\n \
	This is the python script for creating\labelling the training dataset for getting \n direction on the DOT CameraFeed images. Please enter the path for where your images (.png) are"

	print "Images will pop-up, look at it, close them (as plt is a blocking function) and enter \n \
	\n 0 when image in blank or makes no sense, \n\
	\n 1 for East \n\
	\n 2 for West \n\
	\n 3 for North \n\
	\n 4 for South \n \n\
	Enter the path, and Go slow, missed entries might require manual re-checking"

	path = raw_input('Please Enter the path to where your images are stored')
	ls = os.listdir(path)

	ls = [x for x in ls if '.png' in x]
	print len(ls)
	for imges in ls:
		
		images.append(imges)
		img = cv2.imread(imges,0)
		# ret,thresh1 = cv2.threshold(img,200,255,cv2.THRESH_BINARY)
		ret,thresh2 = cv2.threshold(img,200,255,cv2.THRESH_BINARY_INV)
		# -------------------BLOCK CODE BELOW FOR TRYING THRESOLDING------------
		# ret,thresh3 = cv2.threshold(img,200,255,cv2.THRESH_TRUNC)
		# ret,thresh4 = cv2.threshold(img,200,255,cv2.THRESH_TOZERO)
		# ret,thresh5 = cv2.threshold(img,200,255,cv2.THRESH_TOZERO_INV)

		# titles = ['Original Image','BINARY','BINARY_INV','TRUNC','TOZERO','TOZERO_INV']
		# images = [img, thresh1, thresh2, thresh3, thresh4, thresh5]

		# for i in xrange(6):
		#     plt.subplot(2,3,i+1),plt.imshow(images[i],'gray')
		#     plt.title(titles[i])
		#     plt.xticks([]),plt.yticks([])
		# -----------------------------------------------------------------------
		arr.append(np.array(ismg))
		
		plt.imshow(thresh2,'gray')
		plt.show()
		
		

		x = raw_input()
		print x
		labels.append(x)

	df = pd.DataFrame(index= range(len(ls)-1))
	try:
		df['images'] = ls[:-1]
		df['labels'] = labels
		df['array'] = arr

		df.to_csv('labels.csv')	
	except:
		print labels
		pass


