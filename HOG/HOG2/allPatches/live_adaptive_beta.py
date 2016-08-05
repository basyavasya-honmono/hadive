import os,sys
sys.path.insert(0,'../hog')
import itertools
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
from sklearn.externals import joblib
import random
from numpy import arange
from sklearn.cross_validation import train_test_split
from matplotlib.patches import Rectangle
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.cross_validation import KFold


class Annotate(object):
	def __init__(self, image,img_org,name,clf):
		self.img = image
		self.clf = clf
		self.img_org = img_org
		self.imgname = name
		self.i = 1
		self.col = 'b' # deafult color for true positive label
		self.ax = plt.gca()
		# Initialize the Reactangle patch object with properties 
		self.rect = Rectangle((0,0), 1, 1, alpha = 1,ls = 'solid',fill = False, clip_on = True,color = self.col,animated=True)
		# Initialize two diagonally opposite co-ordinates of reactangle as None
		self.xc = None
		self.yc = None
		self.x0 = None
		self.y0 = None
		self.x1 = None
		self.y1 = None
		self.sizeModifier = 2
		self.count = 1
		self.w = 30.0
		self.h = 40.0
		self.qkey = None
		self.rc = None
		self.patch_coords = []
		#self.centers
		# The list that will store value of those two co-ordinates of 
		# all the patches for storing into the file later
		self.xy = []
		self.ax.add_patch(self.rect)
		# Initialize mpl connect object 
		connect = self.ax.figure.canvas.mpl_connect
		# Create objects that will handle user initiated events 
		# We are using three events 
		# First event is button press event (on left key click)- 
		# on which on_click function is called
		connect('button_press_event', self.move_through_image)
		self.draw_cid = connect('draw_event', self.grab_background)

	def objCreation(self):
		# The new reactangle object to use after blit function (clearing 
		# the canvas and removing rectangle objects)

		self.rect = Rectangle((0,0), 1, 1, alpha = 1,ls = 'solid',fill = False, clip_on = True)
		self.xc = None # x co-ordinate of patch center
		self.yc = None # y co-ordinate of patch center
		self.x0 = None # top left x co-ordinate of patch center
		self.y0 = None # top left y co-ordinate of patch center
		self.x1 = None # lower right y co-ordinate of patch center
		self.y1 = None # lower right y co-ordinate of patch center
		self.sizeModifier = 2 # The amount by which width/height will increase/decrease
		self.w = 30.0 # Initial width
		self.h = 40.0 # Initial height
		# Aspect Ratio of 3/4
		# Add the patch on the axes object of figure
		self.ax.add_patch(self.rect) 
	def quit(self,event):
		print('press',event)
		sys.stdout.flush()
		if event.key == 'q':
			plt.close()

		if event.key == '0':
			sys.exit()



	def drawOnlyPatches(self,R):
		'''
		Draw only human patches now
		'''
      	        print 'draw ONLY PATCHES BRO'
                i = 0
                for coord in R:
                        print (i)
                        i = i+1

                with open('counts_multiprocessing.txt','a') as file:
                        file.write("Name %s counts %s " % (self.imgname,i))
                        file.write("Coords %s " % (R))
                        file.write("prob_blues %s" % (self.prob_blues))
                        file.write('\n')



	def reprediction(self,patch_tested,ht,hsize,vt,vsize,rc):
		"""
                Reprediction of sliding window patches is implemented here
                The returned values are the new size of the sliding window, the result of the window of human or not(1 or 0) respectively
                and distance from the hyperplace of that window
                """
		# taking perpective into acount and increasing the size vertically more the horizontally results in better prediction as 
		# human figures are sometimes longer than wider (than the chosen AR of 3:4)
		
		if ht+hsize<80:
			hsize = hsize + 3
			vsize = vsize + 0.5
			rc = rc+1
			patch_tested = self.img[ht:ht+hsize,vt:vt+vsize]
			#print np.shape(patch_tested)
			#print 'done'
			hog_features = hog_signed_patch(patch_tested, n_bins = 18, n_x_cell_pixels = 3, n_y_cell_pixels = 4, signed=True,regularize=False)
			#print 'hog'
			results = self.clf.predict([hog_features])
			prob = self.clf.decision_function([hog_features])
			#print 'return'
			return (results[0],prob[0],hsize,vsize)
		elif ht+hsize>80:
			hsize = hsize + 3
                        vsize = vsize + 1.5
                        rc = rc+1
                        patch_tested = self.img[ht:ht+hsize,vt:vt+vsize]
                        #print np.shape(patch_tested)
                        #print 'done'
                        hog_features = hog_signed_patch(patch_tested, n_bins = 18, n_x_cell_pixels = 3, n_y_cell_pixels = 4, signed=True,regularize=False)
                        #print 'hog'
                        results = self.clf.predict([hog_features])
                        prob = self.clf.decision_function([hog_features])
                        #print 'return'
                        return (results[0],prob[0],hsize,vsize)
		#self.predict(patch_tested,ht,hsize,vt,vsize,rc)


	def collect_patches(self,R,prob,view):
		'''
		collect the patches that are classified as human
		'''
		if (prob>=1 and view<=80) or (prob>0.4 and view>=80):
			
			self.count +=1
			self.patch_coords.append(R)


	def predict(self,patch_tested,ht,hsize,vt,vsize,rc):
		'''
		prediction on the patches drawn 
		'''
		rc = 0
		view = ht+hsize
		hog_features = hog_signed_patch(patch_tested, n_bins = 18, n_x_cell_pixels = 3, n_y_cell_pixels = 4, signed=True,regularize=False)
	
		results = self.clf.predict([hog_features])
		prob = self.clf.decision_function([hog_features])[0]
		
		while (results[0]==1 and prob<1.4 and view<80):
			# distant objects have a greater probability of being mistaken as a human, hence a higer threshold is used
			# for sending the patches for reprediction
			rc = rc+1
			r = self.reprediction(patch_tested,ht,hsize,vt,vsize,rc)
			results[0] = r[0]
			prob = r[1]
			hsize = r[2]
			vsize = r[3]
			if (rc>5):
				print prob,'prob in rep'
				self.col = 'b' if prob>=0.9 else 'r'
				break
		rc = 0
		while (results[0]==1 and prob<1.2 and view>80):
                        rc = rc+1
                        r = self.reprediction(patch_tested,ht,hsize,vt,vsize,rc)
                        results[0] = r[0]
			prob = r[1]
                        hsize = r[2]
                        vsize = r[3]
                        #print r
                        if (rc>3):
				self.col = 'b' if np.abs(prob) >=0.8 else 'r'
                               	break		
			
		if (results[0]==0):
			#print prob
			self.col = 'r'
		elif (results[0]==1 and prob>=1.2 and view>=80):
			#print prob,'human'
			self.col = 'b'
		elif (results[0]==1 and prob>=1.4 and view<=80):
			self.col = 'b'
		if self.col == 'b':
			#self.count+=1
			#print prob,'blue patchey'
			#np.save('detected_patches/'+self.imgname[-4:]+str(self.count)+'.npy',self.img[ht:ht+hsize,vt:vt+vsize])
			self.collect_patches([ht,vt,ht+hsize,vt+vsize],prob,view)
		elif self.col == 'r':
			pass#print prob, 'got red'
		#self.col = 'b' if results[0]==1 else 'r'
		#print ht,hsize,vsize,vt
		self.draw(ht,hsize,vt,vsize)

			

	

	def move_through_image(self,event):
		'''
		Sliding window is implemented here
		'''
		i = 0
		# Adaptive window is used taking perspective into account
		# As while labeling, smaller humans at the upper end of images had smaller patch size,
		# using the sliding window of the approximate same size while detecting (extracting features and classifying)
		# is reasonable. Note the size of the window at different places (along the vertical axis)used here
		# is chosen after empirically testing different options
		# All sliding windows maintain the aspect ratio of 3:4, which is the same chosen while labeling
		
		ht = 1
		hsize = 6
		step = 8	
		#hsize = sorted([8, hd, 52])[1]
		for ht in range(0,240, step):
			# move vertically first
				
			#print 'in move '
			if ht+hsize>=260:
				print 'break'
				#self.ax.figure.canvas.mpl_disconnect(cid)
				#self.drawOnlyPatches(self.patch_coords)
				break
				
			for vt in range(0,348,3):
				# move horizontally '
				
				self.rc = 0
				rc = self.rc
				# Reprediction is used to elimate false positives
				# sometimes when the model predicts something as a human (because of the features),
				# which actually is not (might be tree trunk) and the probabilty of it being a positive as
				# predicted by the classifer is in a "gray region"
				# send that sliding window patch for reprediction
				# In reprediction, increase the size of the patch - and classify again - if its a human or not
				# A tree trunk previously detected as a human, would now be detected as a negative, as the sliding window noe covers
				# features of the tree parts(non-human), and the classifier will easily assign it as a negative label

				if ht in range(60,80):
					hsize = 15
					vsize = int(np.ceil(hsize*3.0/4))
				elif ht in range(80,110):
					hsize = 20
					vsize = int(np.ceil(hsize*3.0/4))

				elif ht in range(110,180):
					hsize = 28
					vsize = int(np.ceil(hsize*3.0/4))
				else :
					hsize = 34
					vsize = int(np.ceil(hsize*3.0/4))	
			
				if vt+vsize>352:
					break

				patch_tested = self.img[ht:ht+hsize,vt:vt+vsize]
				patch_saved = self.img_org[ht:ht+hsize, vt:vt+vsize]
				
		
				self.predict(patch_tested,ht,hsize,vt,vsize,rc)


		self.drawOnlyPatches(self.patch_coords)

	def draw(self,ht,hsize,vt,vsize):
		'''
		Draw the patches
		'''
		self.rect = Rectangle((0,0), 1, 1, alpha = 1,ls = 'solid',fill = False, clip_on = True,color = 'r')
		self.ax.add_patch(self.rect)
		self.rect.set_visible(True)
		self.rect.set_width(vsize)
		self.rect.set_height(hsize)
		self.rect.set_xy((vt,ht))
		self.rect.set_color(self.col)
		self.ax.draw_artist(self.rect)
		self.ax.figure.canvas.blit(self.ax.bbox)

		self.ax.figure.canvas.restore_region(self.background)
		




	def safe_draw(self):
		"""Temporarily disconnect the draw_event callback to avoid recursion"""
		canvas = self.ax.figure.canvas
		canvas.mpl_disconnect(self.draw_cid)
		canvas.draw()
		self.draw_cid = canvas.mpl_connect('draw_event', self.grab_background)


	def grab_background(self, event=None):
		"""
		When the figure is resized, hide the rect, draw everything,
		and update the background.
		"""
		self.rect.set_visible(False)
		self.safe_draw()

		# With most backends (e.g. TkAgg), we could grab (and refresh, in
		# self.blit) self.ax.bbox instead of self.fig.bbox, but Qt4Agg, and
		# some others, requires us to update the _full_ canvas, instead.
		self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.figure.bbox)
		self.rect.set_visible(True)
		self.blit()



	def blit(self):
		"""
		Efficiently update the figure, without needing to redraw the
		"background" artists.
		"""
		#self.objCreation()
		self.ax.figure.canvas.restore_region(self.background)
		self.ax.draw_artist(self.rect)
		self.ax.figure.canvas.blit(self.ax.figure.bbox)




if __name__ == '__main__':

	model = joblib.load('../../../../../../share/HOGModels/trainedOnAllPosPatches_NP_2/clf_allPatches.pkl')

	for imgname in os.listdir('../../../../../../share/team_photo_2016-07-17_raw_images/')[1540:]:
		path = "../../../../../../share/team_photo_2016-07-17_raw_images/"
		# Currenlty it run only on our team image at Flatbush Intersection
                # Please uncomment the lines below to run the script for all the images in the temp folder
		# imgname = path+imgname
		# img_org = cv2.imread(imgname,1)
		# img = cv2.imread(imgname,0)
		img_org = cv2.imread('team.jpg',1)[:,:]
		img = cv2.imread('team.jpg',0)[:,:]
		# Create the canvas
		fig = plt.figure()
		ax = fig.add_subplot(111)
		# print type(img)
		ax.imshow(img,cmap="Greys_r")
		a = Annotate(img,img_org,imgname,model)

		plt.show()
	
