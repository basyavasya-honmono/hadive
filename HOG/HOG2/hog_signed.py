import os,sys
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
import math
import cv2
import PIL
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.backends.backend_agg import FigureCanvasAgg

def avg_correct(grad_vect):
	'''
	This is to correct the default behavious of np.gradient which takes average of the mean
	'''
	
	grad_vect[1:-1] = grad_vect[1:-1]*2
	
	return grad_vect

def hog_signed(path,n_bins = 18, n_x_cell_pixels = 6, n_y_cell_pixels = 8, signed = True, regularize=False):
	'''
	path : path of the image
	n_bins : number of bins for the histogram
	n_x_cell_pixels : number of pixels in the x direction per cell 
	n_y_cell_pixels : number of pixels in the y direction per cell 
	signed : deafault is True, to take signed orientations (0-360) else signed is (0-180)
	regularize : Default is False. If True results finer binning of magnitude into histogram orientations
	'''
	
	if signed==True:
		hist_angle = 360.0
	else:
		hist_angle = 180.0


	image = cv2.imread(path,0)
	img = cv2.fastNlMeansDenoising(image)
	img = cv2.resize(image, (24, 32))

	#imgplot = plt.imshow(img, cmap="Greys_r",interpolation = "nearest")
	#plt.show()

	
	# Calculate gradients magnitude:
	
	gy, gx = np.gradient(np.array(img).astype('float32'))
	
	gy = np.array(map(lambda x: avg_correct(x), gy))
	gx = np.array(map(lambda x: avg_correct(x), gx))
	# Calculate the magnitude
	magnitude_of_gradients = np.sqrt(gy**2 + gx**2)
	
	
	if signed == True:
		# Calculate angles - signed - preserves the quandrant
		angles = np.arctan2(gy,gx)*180.0/math.pi
		angles = np.array(map(lambda x: x+360 if x<0 else x, angles.flatten())).reshape(np.shape(angles))
	else:
		# Calculate angles - unsigned - does not preserve the quandrant
		angles = np.arctan(gy/gx)*180.0/math.pi
		angles = np.array(map(lambda x: x+180 if x<0 else x, angles.flatten())).reshape(np.shape(angles))
	


	# Unsigned histogram

	bin_width = hist_angle/n_bins

	x_div = list(np.arange(bin_width,hist_angle+ bin_width,bin_width))
	h,w = np.shape(magnitude_of_gradients)
	cell_hist = []
	for vr in range(0,h,n_y_cell_pixels):
		for hr in range(0,w,n_x_cell_pixels):
			cell_mag = magnitude_of_gradients[vr:vr+n_y_cell_pixels, hr:hr+n_x_cell_pixels]
			cell_angle = angles[vr:vr+n_y_cell_pixels, hr:hr+n_x_cell_pixels]
			y_hist = [0]*n_bins

			for m,t in zip(cell_mag.flatten(), cell_angle.flatten()):
				# with and without histogram angle binning

				if regularize == True:
					# With finer binning of magnitude into orientations
					for ang in x_div:
						mid_bin = ang - bin_width/2
						ratio = np.abs(t - mid_bin)/bin_width
					# This loop will move through number of angles of the histogram
					# If we chose number of bins = 6, the angles are going to be 180/6
					# [30,60,90,120,150,180]
						if t <= ang:
							# If the pixel gradient vector has angle 15 degrees
							# It should fall into the bin 1 ranging from 0-30 degrees
							ind = x_div.index(ang)	
							# But the contribution of magnitude needs to be weighted with respect to the orientation
							# If the angle is 25 degrees, part of it should fall in bin 1 [0-30], and part of it in 
							# the second bin [30-60]
							# How much part is determined by the ratio variable above which measures the difference wrt the center of bin
							# Here angle 25 degrees so, ratio 25-15/30 (angle - bin_center)/div_width_in_degrees
							# This rule is applied only to angles that are not within the 50% range of the bin center
							if (ang-t)>0.75*bin_width:
								if ind != 0:

									m1 = m*(ratio)
									m2 = m - m1
									y_hist[ind] += m2
									y_hist[ind-1] += m1
								else:
								
									y_hist[ind] += m



							elif (ang-t)<0.25*bin_width:
								
								if ang != x_div[-1]:
									m1 = m*(ratio)
									m2 = m - m1
									y_hist[ind] += m2
									y_hist[ind+1] += m1

								else:
								
									y_hist[ind] += m
								

							else:
								
								y_hist[ind] += m

							
							break


				else:
					# Simple binning of magnitude into orientation
					# Just on where angle is lesser than set range of angles
					for ang in x_div:
						if t <= ang:
							angle_position_hist = x_div.index(ang)
							y_hist[angle_position_hist] =+ m

							# plt.bar(x_div,y_hist,align="center", tick_label=x_div, width=bin_width)
							# plt.show()
							break

			if np.any(np.isnan(y_hist))== True:
				print path,'path'
				print y_hist
			cell_hist.append(y_hist)


	cell_hist = np.array(cell_hist).reshape(h/n_y_cell_pixels, w/n_x_cell_pixels, n_bins)

	# Block Histogram

	feature_vector = []
	n_xcells = w/n_x_cell_pixels
	n_ycells = h/n_y_cell_pixels
	for vm in range(n_ycells - 1):
		# Move block vertically 
		for hm in range(n_xcells - 1):
			# Move block horizontally
			block = cell_hist[vm:vm+2, hm:hm+2,:].flatten()
			if np.any(np.isnan(block))== True:
				print path,'path'
				print block
			
			if np.linalg.norm(block.flatten())!=0:
				# normalize block if they are all not zero
				# else results in NaNs
				block = block/np.linalg.norm(block.flatten())
			feature_vector.append(block)

	# print len(feature_vector)
	# flatten the array and return
	return ([np.array(feature_vector).flatten(),path])
	
	







	
	
