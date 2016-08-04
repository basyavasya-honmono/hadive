import os,sys
sys.insert('../hog/')
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
	with open('../../../../../../share/patch2.pkl') as file:
                data = pickle.load(file)
                data = list(data['path'])
                
	pos_path = filter(lambda x: '_pos_' in x, data)
	neg_path = filter(lambda x: '_neg_' in x, data)[:len(pos_path)]
	
	allfiles = pos_path + neg_path
	# randomly shuffle the list
	allfiles = random.sample(allfiles, len(allfiles))
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
	
	
	C_range = np.logspace(2, 3, 30)
	gamma_range = np.logspace(-3, 3, 50)
	data = allfiles[:total]
	y = map(lambda x: 1 if '_pos_' in x else 0, data)
	
	x = map(lambda x: hog_signed(x, n_bins = 36, n_x_cell_pixels = 6, n_y_cell_pixels = 8, signed=True,regularize=False), data)
	# Set the testing and training data apart
	X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.6, random_state=0)
	x_train = map(lambda x: x[0],X_train)
	data_train = map(lambda x: x[1],X_train)
	#print data_train
	x_test = map(lambda x: x[0],X_test)
	data_test = map(lambda x:x[1],X_test)
	classifiers = []
	print 'supervised'
	
	for C in C_range:
		for gamma in gamma_range:
			# DO a prameter sweep for values of C and gamma
			# Save the accuracy,precision, recall for each set of values for gamma and C
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
					
			with open('results_svm.txt','a') as file:
				file.write('\n')
				file.write('C %s gamma %s'%(C,gamma))
				file.write('\n')
				file.write('The accuracy is:%s '% str(sum(accuracy)*100.0/len(y_test)))
				file.write('The false pos is: %s' % str(sum(false_pos)*100.0/len(y_test)))
				file.write('The false neg is:%s '% str(sum(false_neg)*100.0/len(y_test)))
				file.write('Precision:%s '% str(precision))
				file.write('Recall: %s'% str(recall))
				file.write('Miss rate:%s'% str(sum(false_neg)*100.0/sum(y_test)))
				file.write('Fall-out:%s'% str(sum(false_pos)*100.0/(len(y_test)-sum(y_test))))
				file.write('Specificity:%s '% str(sum(false_neg)*100.0/(len(y_test)-sum(y_test))))
				file.write('\n')

			
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
			

	
	

	
