from PIL import Image
import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time


#Returns the array of all the images in the path in dictionary format , i.e {name of the image: RGBarray}
def rgbDict(path):
	arrays = {}
	for filename in os.listdir(path):
		img = cv2.imread(path+'/'+filename,1)
		
		arrays[filename] = img
		return arrays

#Returns the array of all the images in the path in list format: [RGBarray]
def rgbList(path):
	arrays = {}
	lst = map(lambda filename:cv2.imread(path+'/'+filename,1),os.listdir(path))
	return lst


#Returns the array of all the images in the path in dictionary format , i.e {name of the image: Greyarray}
def greyDict(path):
	arrays = {}
	for filename in os.listdir(path):
		img = cv2.imread(path+'/'+filename,0)
		
		arrays[filename] = img
		return arrays

#Returns the array of all the images in the path in list format: [Greyarray]
def greyList(path):
	arrays = {}
	lst = map(lambda filename:cv2.imread(path+'/'+filename,0),os.listdir(path))
	return lst

#Show all images in the path together
def showAll(path,read=None):
	# Enter any key to close
	if read==None:
		read = 1
	for filename in os.listdir(path):
		# plt.figure()
		# plt.ion()
		img = cv2.imread(path+'/'+filename,read)
		cv2.imshow('image',img)

		cv2.waitKey(0)
		cv2.destroyAllWindows()

#Histogram of all the images together
def histogram(path):

	for i in os.listdir(path):
		img = Image.open(path+'/'+i)
		#img1 = cv2.imread('test/'+i,0)
		arr = np.asarray(img)
		
		hist,bins = np.histogram(arr.flatten(),256,[0,256])
		
		cdf = hist.cumsum()
		cdf_normalized = cdf * hist.max()/ cdf.max()
		meann = np.mean(hist * np.arange(0,256))
		f, ax = plt.subplots(2,1, figsize=(15,15))


		ax[0].imshow(arr, cmap='Greys_r')
		
		plt.title(str(meann),fontsize=24)
		ax[1].plot(cdf_normalized, color = 'b')

		ax[1].hist(arr.flatten(),256,[0,256], color = 'r')
		ax[1].set_xlim([0,256])
		ax[1].legend(('cdf','histogram'), loc = 'upper left')
		plt.show()

		


	










	
