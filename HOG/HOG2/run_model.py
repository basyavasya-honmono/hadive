import os,sys
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.backends.backend_agg import FigureCanvasAgg
from sklearn.svm import SVC
from hog_signed_patch import hog_signed_patch
from hog_signed import hog_signed
import cv2
import time
import pickle
import random
from numpy import arange
from sklearn.cross_validation import train_test_split
from matplotlib.patches import Rectangle
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.cross_validation import KFold



if __name__ == '__main__':



	C = 1000.0
	gamma = 0.1

	with open('/gws/projects/project-computer_vision_capstone_2016/workspace/share/patch2.pkl') as file:
                data = pickle.load(file)
                data = list(data['path'])
                
	pos_path = filter(lambda x: '_pos_' in x, data)[:]
	neg_path = filter(lambda x: '_neg_' in x, data)[:len(pos_path)]

	
	#files = map(lambda x: pos_path+x, os.listdir(pos_path))[:len(pos_path)] # Create complete imagenames with path
	#files1 = map(lambda x: neg_path+x, os.listdir(neg_path))[:len(pos_path)]
	allfiles = pos_path + neg_path
	# randomly shuffle the list
	allfiles = random.sample(allfiles, len(allfiles))
	#print allfiles[:10]
	# set the length of data
	#print len(allfiles)
	acc = 0
	total = len(pos_path) + len(neg_path)
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
	
	# Create labels for patches

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

	accuracy = []
	false_neg = []
	false_pos = []
	true_pos = []
	true_neg = []

	false_neg_img = []
	false_pos_img = []
	true_pos_img = []
	true_neg_img = []


	clf = SVC(kernel='rbf',C = C, gamma = gamma)
	clf.fit(x_train+x_test, y_train+y_test)
	import pickle
	from sklearn.externals import joblib
	joblib.dump(clf, 'clf.pkl') 

	print 'Trained'
	print 'Model Saved'
	print "Don't delete the .npy files with it "
	