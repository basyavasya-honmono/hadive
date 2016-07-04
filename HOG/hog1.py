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
	# print('press', event.key)
	# sys.stdout.flush()
	if event.key == 'q':
		plt.close()


def draw_gradients(ax,mag,tans):
	r,c = np.shape(mag)
	print r,c
	
	for i in range(c):
		for j in range(r):
			
			theta = tans[j,i]
			m = mag[j,i]
			
			theta = theta*math.pi/180
			y = np.sin(theta)*m
			x = np.cos(theta)*m
			l = Line2D([i-x/2,i+x/2],[j-y/2,j+y/2]) 
			ax.add_line(l)
	imgplot = ax.imshow(mag,cmap="Greys_r")
	plt.show()

def draw_gradients_cells(ax,cell_hist,mag):
	r,c,m = np.shape(cell_hist)
	
	
	for i in range(c):
		for j in range(r):
			theta = 180.0/5
			for hists in cell_hist[i,j,:]:
				
				m = mag[j,i]
				
				theta = theta*math.pi/180
				y = np.sin(theta)*m
				x = np.cos(theta)*m
				l = Line2D([(i*3+1.5)-x/2,(i*3+1.5)+x/2],[(j*4+2.0)-y/2,(j*4+2.0)+y/2]) 
				ax.add_line(l)
			theta += theta
	imgplot = ax.imshow(mag,cmap="Greys_r")
	plt.show()
	


n_bins = 5
img = cv2.imread("pos.jpg",0)

print '\n'

fig, ax = plt.subplots()
fig.canvas.mpl_connect('key_press_event', press)
# imgplot = ax.imshow(img,cmap= "Greys_r")
# plt.show()




gx, gy = np.gradient(np.array(img).astype('float32'))
mag = np.sqrt(gx**2 + gy**2)
shape = np.shape(mag)
magMean = np.mean(mag)
magStd = np.std(mag)
magMax = np.max(mag)

mag = np.array(map(lambda x:np.abs(x/magMax),mag)).reshape(shape)
print np.min(mag),np.max(mag)


# imgplot = plt.imshow(gy,cmap= "Greys_r")
# plt.show()

tans = np.arctan(gy/gx)
shape = np.shape(tans)
tans[np.isnan(tans)] = 0
tans = tans*180.0/math.pi
tans = np.array(map(lambda x: x + 180 if x<0 else x, tans.flatten())).reshape(shape)




mc = mag[:4,:3]
print '\n'
tanc = tans[:4,:3]
# imgplot = plt.imshow(mag,cmap= "Greys_r")
# plt.show()
# histogram prep
c = 0
div = 180.0/n_bins
x_hist = np.arange(div,180.0+div,div)
cell_hist = []

for rows in range(0,shape[0],4):
	#print rows
	
	for cols in range(0,shape[1],3):
		#print cols
		y_hist = [0]*n_bins
		mc = mag[rows:rows+4, cols:cols+3]
		tanc = tans[rows:rows+4, cols:cols+3]

		for m,t in zip(mc.flatten(), tanc.flatten()):
			#print m,t
			for angle in x_hist:
				mid_bin = angle-div/2
				ratio = np.abs(t - mid_bin)/div
				if t<angle:

					ind = list(x_hist).index(angle)	
					# y_hist[ind] += m
					# break
					
					if angle-t>0.75*div:
						if ind != 0:

							m1 = m*(ratio)
							m2 = m - m1
							y_hist[ind] += m2
							y_hist[ind-1] += m1
						else:
						
							y_hist[ind] += m



					elif angle-t<0.25*div:
						
						if angle != x_hist[-1]:
							m1 = m*(ratio)
							m2 = m - m1
							y_hist[ind] += m2
							y_hist[ind+1] += m1

						else:
						
							y_hist[ind] += m
						

					else:
						
						y_hist[ind] += m

					
					break

		print x_hist,y_hist
		cell_hist.append(y_hist)
		
		c = c+1

# Visualize 
print c,'c'
print cell_hist[:4],':1'
print len(cell_hist[0])
fig, ax = plt.subplots()
imgplot = ax.imshow(img, cmap="Greys_r")
draw_gradients(ax,mag,tans)
plt.show()

# Block normalization
blocks = []

cell_hist = (np.asarray(cell_hist)).reshape(7,7,5)
print cell_hist[0,0,:]
c = 0
for vm in range(7/2+1):

	for hm in range(7/2+1):
		block = np.roll(cell_hist,1,axis=1)[:2,:2,:]
		block = block.flatten()
		blockmag = np.linalg.norm(block)
		block = np.array(map(lambda x: x/blockmag,block))
		blocks.append(block)
		c = c+1

	cell_hist = np.roll(cell_hist, -1,axis=0)

print c,'cb'

# Visualize cell gradients
fig, ax = plt.subplots()
imgplot = ax.imshow(img, cmap="Greys_r")
draw_gradients_cells(ax,cell_hist,mag)
plt.show()






