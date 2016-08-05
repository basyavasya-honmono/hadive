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

def press(event):
	'''
	press key events
	'''
	# print('press', event.key)
	# sys.stdout.flush()
	if event.key == 'q':
		# quit the plot
		plt.close()

	



def draw_gradients(ax,mag,tans):
	'''
	Visualize the gradients by pixel
	'''
	r,c = np.shape(mag)
	print r,c
	fig, ax = plt.subplots()
	fig.canvas.mpl_connect('key_press_event', press)
	
	for i in range(c):
		for j in range(r):
			
			theta = tans[j,i]
			m = mag[j,i]
			
			theta = theta*math.pi/180
			y = np.sin(theta)*m
			x = np.cos(theta)*m
			l = Line2D([i-x/2,i+x/2],[j-y/2,j+y/2]) 
			ax.add_line(l)

	ax.set_title('Gradients Per pixel')
	imgplot = ax.imshow(mag,cmap="Greys_r")
	plt.show()

def draw_gradients_cells(ax,cell_hist,mag):
	'''
	Visualize the gradients by cell
	'''

	r,c,m = np.shape(cell_hist)
	fig, ax = plt.subplots()
	fig.canvas.mpl_connect('key_press_event', press)
	
	
	for i in range(c):
		for j in range(r):
			theta = 180.0/5
			for hists in cell_hist[i,j,:]:
				
				m = mag[j,i]
				
				theta = theta*math.pi/180
				y = np.sin(theta)*m*4
				x = np.cos(theta)*m*3
				l = Line2D([(i*3+1.5)-x/2,(i*3+1.5)+x/2],[(j*4+2.0)-y/2,(j*4+2.0)+y/2]) 
				ax.add_line(l)
			theta += theta
	ax.set_title('Gradients Per Cell')
	imgplot = ax.imshow(mag,cmap="Greys_r",interpolation="nearest")
	plt.show()
	


	

def image_gradients(path):

	n_bins = 5
	n_cells = 2
	x = 3
	y = 2
	# read the image/patch
	# img = cv2.imread("pos1.jpg",0)
	# img = Image.open('C:\Users\priya\OneDrive\Documents\ComputerVision\HOG/20160626_snapshot_patches.tar/20160626_snapshot_patches\pos/59031eaa-7b39-491a-a918-f1c94f5deaf8.jpg').convert('L')
	image = cv2.imread(path,0)
	try:
		img = cv2.resize(image, (24, 32))
	except:
		pass
	# img = img.resize((24, 32), Image.ANTIALIAS)
	img = np.array(img)
	print '\n'
	fig, ax = plt.subplots()
	fig.canvas.mpl_connect('key_press_event', press)
	ax.set_title("Original Patch Image")
	imgplot = ax.imshow(img,cmap= "Greys_r")
	# Display the image
	# Press  key 'q' to quit
	plt.show()

	# For the patch calculate gradients
	# Gradients calculated here are the basic gradient vectors
	# By subtracting pixel values adjacent to the one considered in X and Y direction
	gx, gy = np.gradient(np.array(img).astype('float32'))
	# The magnitude of pixel gradient vectors
	mag = np.sqrt(gx**2 + gy**2)
	
	shape = np.shape(mag)
	# The normalization of the magnitude array is done for visualizing the gradients per pixel
	magMean = np.mean(mag)
	magStd = np.std(mag)
	magMax = np.max(mag)
	# Normalizing just by dividing by maximum value of the magnitude array
	magVis = np.array(map(lambda x:np.abs(x/magMax),mag)).reshape(shape)
	
	# Computing the direction of the gradient vectors
	tans = np.arctan(gy/gx)
	# shape = np.shape(tans)
	tans[np.isnan(tans)] = 0
	# By default, numpy calculates tan in radians, so we convert into degrees
	tans = tans*180.0/math.pi
	# tan(x+180) = tan(x)
	# Makes all negative values positive
	tans = np.array(map(lambda x: x + 180 if x<0 else x, tans.flatten())).reshape(shape)

	# Plot the gradients across the X direction
	fig, ax = plt.subplots()
	fig.canvas.mpl_connect('key_press_event', press)
	ax.set_title("Gradients along X direction")
	imgplot = ax.imshow(gx, cmap="Greys_r",interpolation="nearest")
	plt.show()


	# Plot the gradients across the Y direction
	fig, ax = plt.subplots()
	fig.canvas.mpl_connect('key_press_event', press)
	ax.set_title("Gradients along Y direction")
	imgplot = ax.imshow(gy, cmap="Greys_r",interpolation="nearest")
	plt.show()

	# Plot the magnitude
	fig, ax = plt.subplots()
	fig.canvas.mpl_connect('key_press_event', press)
	ax.set_title("Gradients")
	imgplot = ax.imshow(mag, cmap="Greys_r",interpolation="nearest")
	plt.show()

	mc = mag[:y,:x]
	print '\n'
	tanc = tans[:y,:x]
	
	c = 0
	div = 180.0/n_bins
	x_hist = np.arange(div, 180.0+div, div)
	cell_hist = []

	# Preparing the histogram of gradients per cell

	for rows in range(0,shape[0],y):
		#print rows
		
		for cols in range(0,shape[1],x):
			#print cols
			# Moving along each row
			y_hist = [0]*n_bins
			mc = mag[rows:rows+4, cols:cols+3]
			# taking the cell in consideration
			tanc = tans[rows:rows+4, cols:cols+3]

			for m,t in zip(mc.flatten(), tanc.flatten()):
				
				
				# m = magnitude of the gradient vector per cell
				# t = angle of the gradient vector per cell
				for angle in x_hist:
					mid_bin = angle-div/2
					ratio = np.abs(t - mid_bin)/div
					# This loop will move through number of angles of the histogram
					# If we chose number of bins = 6, the angles are going to be 180/6
					# [30,60,90,120,150,180]
					if t <= angle:
						# If the pixel gradient vector has angle 15 degrees
						# It should fall into the bin 1 ranging from 0-30 degrees
						ind = list(x_hist).index(angle)	
						# But the contribution of magnitude needs to be weighted with respect to the orientation
						# If the angle is 25 degrees, part of it should fall in bin 1 [0-30], and part of it in 
						# the second bin [30-60]
						# How much part is determined by the ratio variable above which measures the difference wrt the center of bin
						# Here angle 25 degrees so, ratio 25-15/30 (angle - bin_center)/div_width_in_degrees
						# This rule is applied only to angles that are not within the 50% range of the bin center
						if (angle-t)>0.75*div:
							if ind != 0:

								m1 = m*(ratio)
								m2 = m - m1
								y_hist[ind] += m2
								y_hist[ind-1] += m1
							else:
							
								y_hist[ind] += m



						elif (angle-t)<0.25*div:
							
							if angle != x_hist[-1]:
								m1 = m*(ratio)
								m2 = m - m1
								y_hist[ind] += m2
								y_hist[ind+1] += m1

							else:
							
								y_hist[ind] += m
							

						else:
							if m==0:
								print 'yo'
							
							y_hist[ind] += m

						
						break


			
			if np.all(np.isnan(y_hist)):
				print ratio,'ratio'
				print y_hist,'y_hist'

				print m,t
			#print x_hist,y_hist
			# fig, ax = plt.subplots()
			# fig.canvas.mpl_connect('key_press_event', press)
			# ax.set_title("Pixel histogram")
			# ax.bar(x_hist,y_hist)
			# plt.show

			cell_hist.append(y_hist) # Save the histogram per cell for Block Normalization later
			
			c = c+1



	# Cell Gradients subplot
	p = 1
	

	# Visualize 
	print c,'c'
	#print cell_hist[:4],':1'

	print len(cell_hist[0])
	
	# Visualize the gradients by cell
	draw_gradients(ax,magVis,tans)
	plt.show()


	# Block normalization
	# blocks = []

	# cell_hist = (np.asarray(cell_hist)).reshape(shape[0]/y + shape[0]%y,shape[1]/x + shape[1]%y,n_bins)
	# br = shape[0]/y
	# bc = shape[1]/x
	# #print cell_hist[0,0,:]
	# c = 0
	# for vm in range(br/2+1):

	# 	for hm in range(bc/2+1):
	# 		block = cell_hist[hm:hm+n_cells,vm:vm+n_cells]
	# 		# block = np.roll(cell_hist,1,axis=1)[:2,:2,:]
	# 		block = block.flatten()
	# 		blockmag = np.linalg.norm(block)
	# 		block = np.array(map(lambda x: x/blockmag,block))
	# 		blocks.append(block)
	# 		c = c+1

	# 	cell_hist = np.roll(cell_hist, -1,axis=0)

	# # print c,'cb'
	# # print len(blocks[0])
	# feature_vector = [item for sublist in blocks for item in sublist]

	# Visualize cell gradients
	
	#draw_gradients_cells(ax,cell_hist,magVis)
	

if __name__ == '__main__':
	
	image_gradients('pos.jpg')
	



