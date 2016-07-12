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
from sklearn.svm import SVC
from sklearn.cluster import k_means
from sklearn.cluster import KMeans
from hog_signed import hog_signed
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.cross_validation import KFold

if __name__ == '__main__':
	with open('/gws/projects/project-computer_vision_capstone_2016/workspace/share/patch2.pkl') as file:
                data = pickle.load(file)
                data = list(data['path'])
                
	pos_path = filter(lambda x: '_pos_' in x, data)
	neg_path = filter(lambda x: '_neg_' in x, data)[:len(pos_path)]
	
	#files = map(lambda x: pos_path+x, os.listdir(pos_path))[:len(pos_path)] # Create complete imagenames with path
	#files1 = map(lambda x: neg_path+x, os.listdir(neg_path))[:len(pos_path)]
	allfiles = pos_path + neg_path
	# randomly shuffle the list
	allfiles = random.sample(allfiles, len(allfiles))
	#print allfiles[:10]
	# set the length of data
	#print len(allfiles)
	total = len(pos_path)*2
	accuracy = []
	false_neg = []
	false_pos = []
	true_pos = []
	true_neg = []

	false_neg_img = []
	false_pos_img = []
	true_pos_img = []
	true_neg_img = []
	
	
	C_range = np.logspace(-2, 10, 13)
	gamma_range = np.logspace(-9, 3, 13)
	data = allfiles[:total]
	# 80-20 for test and train
	#n_train = int(0.8*total)
	#n_test = total - n_train
	#tuned_parameters = [{'C': [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 50, 70, 80, 90, 100], 'kernel': ['linear']},{'C': [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 50, 70, 80, 90, 100], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},]

	
	# Create label for patches

	y = map(lambda x: 1 if '_pos_' in x else 0, data)
	
	x = map(lambda x: hog_signed(x, n_bins = 36, n_x_cell_pixels = 6, n_y_cell_pixels = 8, signed=True,regularize=False), data)
	# Set the testing and training data apart
	X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.6, random_state=0)
	x_train = map(lambda x: x[0],X_train)
	data_train = map(lambda x: x[1],X_train)
	#print data_train
	x_test = map(lambda x: x[0],X_test)
	data_test = map(lambda x:x[1],X_test)
	# x_train = x[:n_train]
	# x_test = x[n_train:n_test]
	# y_train = y[:n_train]
	# y_test = y[n_train:n_test]
	classifiers = []
	print 'supervised'
	
	for C in C_range:
		for gamma in gamma_range:
			print '\n'
			accuracy = []
			false_neg = []
			false_pos = []
			true_pos = []
			true_neg = []

			false_neg_img = []
			false_pos_img = []
			true_pos_img = []
			true_neg_img = []
			clf = SVC(kernel='rbf',	C = C, gamma = gamma)
			clf.fit(x_train, y_train)
			print 'The parameters are:'
			print 'C: ',C,'gamma: ',gamma
	# classifiers.append([C, gamma, clf])
	# for i in x_test:
	# 	if np.shape(i) == 0:
	# 		print 'yes'
			results = clf.predict(x_test)
			


			
	
			for y1,c1,img in zip(y_test,list(results),data_test):
				
				#cluster.append([img,c1])
				if y1 == 1:
					if c1 == 1:
						true_pos.append(1)
						true_pos_img.append(img)

					else:
						false_neg.append(1)
						false_neg_img.append(img)

				if y1==0:
					#print y1,c1,img[-50:]
					if c1 == 1:
						#print img
						false_pos.append(1)
						false_pos_img.append(img)

					else:
						true_neg.append(1)
						true_neg_img.append(img)

			accuracy = true_pos + true_neg
			accuracy_img = true_pos_img + true_neg_img
			if sum(results)!=0:

				precision = sum(true_pos)*100.0/sum(results)
			else:
				precision = 0
			recall = sum(true_pos)*100.0/sum(y_test)
					
		


	# 		#print 'hi'
	# #print len(y_test)
	# #print sum(yes)
	





			print 'The accuracy is: ',sum(accuracy)*100.0/len(y_test)
			print 'The false pos is: ',sum(false_pos)*100.0/len(y_test)
			print 'The false neg is: ', sum(false_neg)*100.0/len(y_test)
			print 'Precision: ', precision
			print 'Recall: ',recall
			print 'Miss rate:', sum(false_neg)*100.0/sum(y_test)
			print 'Fall-out:', sum(false_pos)*100.0/(len(y_test)-sum(y_test))
			print 'Specificity: ',sum(false_neg)*100.0/(len(y_test)-sum(y_test))
			print '\n'

			
			if sum(accuracy)*100.0/len(y_test)>80.0:
				with open('accuracy_svm.txt','a') as thefile:
					thefile.write("C %s gamma %s" % (C,gamma))
					thefile.write("\n")
					for item in accuracy_img:
						
						thefile.write("%s\n" % item)
				
				with open('false_neg_svm.txt','a') as thefile:
					thefile.write("C %s gamma %s" % (C,gamma))
					thefile.write("\n")
					for item in false_neg_img:
						thefile.write("%s\n" % item)

				with open('false_pos_svm.txt','a') as thefile:
					thefile.write("C %s gamma %s" % (C,gamma))
					thefile.write("\n")
					for item in false_pos_img:
						thefile.write("%s\n" % item)
			

	
	

	
