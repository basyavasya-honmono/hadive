import os,sys
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
import math
import cv2
import PIL
import random
import pickle
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.backends.backend_agg import FigureCanvasAgg
from sklearn.cluster import k_means
from sklearn.cluster import KMeans
from hog_signed import hog_signed

if __name__ == '__main__':
	pos_path = "C:\Users\priya\OneDrive\Documents\ComputerVision\HOG/20160626_snapshot_patches.tar/20160626_snapshot_patches/pos/"
	neg_path = "C:\Users\priya\OneDrive\Documents\ComputerVision\HOG/20160626_snapshot_patches.tar/20160626_snapshot_patches/neg/"
	files = map(lambda x: pos_path+x, os.listdir(pos_path))[:1000] # Create complete imagenames with path
	files1 = map(lambda x: neg_path+x, os.listdir(neg_path))[:1000]
	allfiles = files + files1
	# randomly shuffle the list
	allfiles = random.sample(allfiles, len(allfiles))
	#print allfiles[:10]
	# set the length of data
	#print len(allfiles)
	total = 2000
	accuracy = []
	false_neg = []
	false_pos = []

	accuracy_img = []
	false_neg_img = []
	false_pos_img = []
	cluster = []
	
	data = allfiles[:total]
	# 80-20 for test and train
	# n_train = int(0.8*total)
	# n_test = total - n_train
	
	# Create label for patches

	y = map(lambda x: 1 if 'pos' in x else 0, data)
	x = map(lambda x: hog_signed(x, n_bins = 36, n_x_cell_pixels = 6, n_y_cell_pixels = 8, signed=True,regularize=False), data)
	# Set the testing and training data apart
	# x_train = x[:n_train]
	# x_test = x[n_train:n_test]
	# y_train = y[:n_train]
	# y_test = y[n_train:n_test]
	print 'unsupervised'
	# Run k-means with two clusters
	c = k_means(x, n_clusters = 2, n_init=110)
	
	# for y1,c1,img in zip(y,list(c[1]),data):
	# 	cluster.append([img,y1,c1])
	# p = 1
	
	# xp = 5
	# yp = 4
	# #plt.figure(figsize=(18, 18), dpi=200)
	# for i in range(total):
		
	# 		ax = plt.subplot(xp, yp, p)
	# 		p = p+1
	# 		img = mpimg.imread(cluster[i][0])
	# 		# ax = fig.add_subplot(3,1,p)
	# 		ax.set_title('y %s c %s'%(cluster[i][1],cluster[i][2]))
	# 		ax.set_xticklabels([])
	# 		ax.set_yticklabels([])
	# 		ax.imshow(img)
	# #plt.subplots_adjust(wspace=.3, hspace=0.5, left=0, right=0.9, top=0.5, bottom=0)
	# plt.show()

	# check how many were detected right
	# Check for false positives also later
	for y1,c1,img in zip(y,list(c[1]),data):
		#cluster.append([img,c1])
		if y1 == c1:
			accuracy_img.append(img)
			accuracy.append(1)
			# img = mpimg.imread(img)
			# imgplot = plt.imshow(img)
			# plt.title('original label %s clustering label %s'%(y1,c1))
			# plt.show()
		elif (y1 == 1 and c1 == 0):
			# When the actual label is a human and the clustering marks it as non-human i.e. false negatives
			false_neg_img.append(img)
			false_neg.append(1)
			# img = mpimg.imread(img)
			# imgplot = plt.imshow(img)
			# plt.title('original label %s clustering label %s '%(y1,c1))
			# plt.show()
		elif (y1 == 0 and c1 == 1):
			# When the actual img is of a non-human but the clustering makes it a human, i.e. false positives
			# High in our case
			false_pos_img.append(img)
			false_pos.append(1)
			# img = mpimg.imread(img)
			# imgplot = plt.imshow(img)
			# plt.title('original label %s clustering label %s '%(y1,c1))
			# plt.show()
		


			#print 'hi'
	#print len(c[1])
	#print sum(yes)
	





	print 'The accuracy is: ',sum(accuracy)*1.0/len(c[1])
	print 'The false pos is: ',sum(false_pos)*1.0/len(c[1])
	print 'The false neg is: ', sum(false_neg)*1.0/len(c[1])

	with open('accuracy.txt','w') as thefile:
		for item in accuracy_img:
			#print item
			thefile.write("%s\n" % item)
	
	with open('false_neg.txt','w') as thefile:
		for item in false_neg_img:
			thefile.write("%s\n" % item)

	with open('false_pos.txt','w') as thefile:
		for item in false_pos_img:
			thefile.write("%s\n" % item)
	

	# print 'supervised'
	# clf = KMeans(n_clusters =2)
	# clf.fit(x_train,y_train)
	# predict = clf.predict(x_test)
	# print predict

	# print list(c[1])
	# print y
	





