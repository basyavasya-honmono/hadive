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

		self.w = 30.0
		self.h = 40.0
		self.qkey = None

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
		# connect('close_event', self.handle_close)


		# Second event to draw, in case a mistake in labelling is made, 
		# deleting the patch requires redrawing the original canvas
		# self.draw_cid = connect('draw_event', self.grab_background)

		# # Third event - key press event
		# # To change color of the patches when you want to switch between 
		# # true postive and false postive labels
		# connect('key_press_event',self.colorChange)


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

		if event.key == 'x':
			sys.exit()

	def move_through_image(self,event):
		i = 0
		print np.shape(self.img)
		
		ht = 1
		hsize = 8
		
		#hsize = sorted([8, hd, 52])[1]
		for ht in range(0,128, 8):
			
			
			
			if ht+hsize>200:
				break
				
			for vt in range(0,352,6):
				self.rect = Rectangle((0,0), 1, 1, alpha = 1,ls = 'solid',fill = False, clip_on = True,color = 'r')
				self.ax.add_patch(self.rect)
				
				
				if ht in range(0,20):
					hsize = 10
					vsize = int(np.ceil(hsize*3.0/4))
				elif ht in range(20,50):
					hsize = 20
					vsize = int(np.ceil(hsize*3.0/4))

				elif ht in range(50,120):
					hsize = 32
					vsize = int(np.ceil(hsize*3.0/4))
				else :
					hsize = 40
					vsize = int(np.ceil(hsize*3.0/4))


			
				if vt+vsize>352:
					break

				patch_tested = self.img[ht:ht+hsize,vt:vt+vsize]
				patch_saved = self.img_org[ht:ht+hsize, vt:vt+vsize]
				#print np.shape(patch_tested)
				if patch_tested!=[]:
					hog_features = hog_signed_patch(patch_tested, n_bins = 36, n_x_cell_pixels = 6, n_y_cell_pixels = 8, signed=True,regularize=False)
					#print hog_features
					results = self.clf.predict([hog_features])
					if results[0]==1:
						self.col = 'b'
						i = i + 1
						np.save(str(i)+'.npy',patch_saved)
					else:
						self.col = 'r'

				# print 'number',i
				# i = i+1


				self.rect.set_visible(True)
				self.rect.set_width(vsize)
				self.rect.set_height(hsize)
				self.rect.set_xy((vt,ht))
				self.rect.set_color(self.col)
				self.ax.draw_artist(self.rect)
				time.sleep(0.1)
				
				#self.grab_background()
				#self.rect.set_visible(False)
				self.ax.figure.canvas.blit(self.ax.bbox)

				self.ax.figure.canvas.restore_region(self.background)
				


				# img1 = img[ht:ht+hsize,vt:vt+vsize]
				# fig,ax = plt.subplots()
				# fig.canvas.mpl_connect('key_press_event',quit)
				# imgplot = plt.imshow(img1,cmap = "Greys_r")
				# plt.show()



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

	def hog_patch_image(img):

		pass




if __name__ == '__main__':

	model = joblib.load('clf.pkl')

	for imgname in os.listdir('images/'):
		img_org = cv2.imread(imgname,1)[60:,:]
		img = cv2.imread(imgname,0)[60:,:]
		
		# Create the canvas
		fig = plt.figure()
		ax = fig.add_subplot(111)
		# print type(img)
		ax.imshow(img,cmap="Greys_r")
		a = Annotate(img,img_org,imgname,model)

		plt.show()
	
