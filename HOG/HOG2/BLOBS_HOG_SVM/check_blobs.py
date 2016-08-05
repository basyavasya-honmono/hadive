import os,sys
import pandas as pd
import numpy as np 
sys.path.insert(0,'../../hog')
from sklearn.svm import SVC
from hog_signed_patch import hog_signed_patch
from hog_signed import hog_signed
import time
import pickle
from sklearn.externals import joblib
import random
from numpy import arange
import re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.patches as patches
import glob

def quit(event):
        print('press', event.key)
        sys.stdout.flush()
        if event.key == 'q':
                plt.close()
        elif event.key == '0':
                sys.exit()



def extract_arrays(f):
	#print f
	name = (f[1:-1].split(',',1)[0])[7:]
	str_array =  (f[1:-1].split(',',1)[1])
	ls = np.array(map(lambda x: int(x),re.findall(r'\b\d+\b', str(str_array))))
	ls_a = np.reshape(ls, (len(ls)/2, 2))
	return (name,ls_a)


def repredict(patch_tested,x0,y0,h,w):
	#print x0,y0,'repredict'
	h = h+4
	w = w+1
	y1 = y0+h
	x1 = x0+w
	patch_tested = img[y0:y1,x0:x1]
	#print np.shape(patch_tested)
	hog_features = hog_signed_patch(patch_tested, n_bins = 18, n_x_cell_pixels = 3, n_y_cell_pixels = 4, signed=True,regularize=False)
	#print 'features extracted'
	results = clf.predict([hog_features])[0]
	prob = clf.decision_function([hog_features])[0]	
	return (h,w,results,prob)

	

with open('blobs.txt') as file:
	f = file.readlines()[:]
	counts_per_image = []
	clf = joblib.load('../../../../../../share/HOGModels/trainedOnAllPosPatches_NP_2/clf_allPatches.pkl')
	blobs = map(lambda x: extract_arrays(x.strip()),f)
	#print blobs[]
	names = pd.read_csv('name.csv')
	files = names['filename']
	
	img_names = map(lambda x:x[0],blobs)
	nIndex = map(lambda x: img_names.index(x.split('/')[-1]),files)
	count = 0
	for n in nIndex:
		blue_patches = 0
		image = blobs[n]
		centers = image[1]
		fig = plt.figure(frameon=False)
		ax = fig.add_axes([0., 0., 1., 1.])
		ax.axis('off')	
		fig.canvas.mpl_connect('key_press_event', quit)	
		img = cv2.imread(image[0],0)
		img_color = mpimg.imread(image[0])
		imgplot = ax.imshow(img_color,cmap="Greys_r",interpolation='nearest', aspect='auto')
		centers = filter(lambda x: x[1]>=80,image[1])
		for c in centers:
			
			xc = c[0]
			yc = c[1]
			h = 0
			w = 0
			# Implementing Adaptive Windowing
			if yc>=165:
				h = 40
				w = 30
			elif yc>=120:
				h = 32
				w = 24
			elif yc>=100:
				h =  20
				w = 15
			elif yc>=80:
				h = 10
				w = 8

			x0 = xc-w/2.0
			y0 = yc-h/2.0
			x1 = x0+w
			y1 = y0+h
			# Sometimes the centers are too close to the image boundary, hence creating the window around that point
			# would result in co-orindates of the box to fall outide of the image,resulting in shape of the patch to be 0
			# Due to this, the features would not be extracted and the code would freeze
			# the following lines take care of the situation
			if (((x1-x0)<0) or x0<0 or x1<0):
				# taking care of the patches falling outside the images with centers on the left
				patch_tested = img[y0:y1,0:xc]
				if xc>310:
					 # taking care of the patches falling outside the images with centers on the right
					patch_tested = img[y0:y1,xc-10:xc]
			elif ((y1-y0) or y1<0 or y0<0)<0:
				patch_tested = img[0:yc,x0:x1]
				if yc>200:
                                        patch_tested = img[yc-10:yc,x0:x1]

			elif ((x1-x0)<0 and (y1-y0)<0):
				patch_tested = img[0:yc,0:xc]
				if (yc>200) and (xc>310):
					patch_tested = img[yc-10:yc,xc-10:xc]
			else:
				patch_tested = img[y0:y1,x0:x1]
			# the aspect ratio is not preserved for patches with blob centers on the extreme left or right(half people) due to manipulation 
			# done above to consider the patch itself
			hog_features = hog_signed_patch(patch_tested, n_bins = 18, n_x_cell_pixels = 3, n_y_cell_pixels = 4, signed=True,regularize=False)
               
			results = clf.predict([hog_features])[0]
                	prob = clf.decision_function([hog_features])[0]
			
			if results==1 or (prob>=-0.15 and yc>180):
				col = 'b'
				# Reprediction has not been used. The function is still mainted in the script.
			elif results == 0:
				col = 'r'	
			


			if col == 'b':
				blue_patches += 1
				# blue_patches collects the number of positive/human patches found
				# draw the patches
				ax.add_patch(patches.Rectangle(
					(x0,y0),
					w,h,
					fill = False,
					color = col,
					lw = 2.0
					))
				ax.text(x0,y0,str("%.2f" % prob),fontsize=15)
		counts_per_image.append(blue_patches)
		
		plt.axis('off')
		# save the figure with patches drawn on it
		plt.savefig('blobs_video/'+str(count)+'.jpg', bbox_inches='tight',pad_inches=0)
               		
		with open('blobs_hog.txt','a') as file:
			file.write('%s'%(blue_patches))
			file.write('\n')

		print 'saved image',count
		count +=1
	# save the counts of the human patches per image
	names['blob_hog_count'] = counts_per_image
	names.to_csv('count_metric.csv')
