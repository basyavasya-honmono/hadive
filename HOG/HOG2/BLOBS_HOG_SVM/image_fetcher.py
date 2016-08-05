import os,sys
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.backends.backend_agg import FigureCanvasAgg
import glob

def quit(event):
	print('press', event.key)
	sys.stdout.flush()
	if event.key == 'q':
		plt.close()
	elif event.key == '0':
		sys.exit()

if __name__ == '__main__':
	img_list = glob.glob('*.jpg')
	print img_list.index('2016-07-17-13-39-11_Flatbush_Ave__Willoughby.jpg')
	i = 1563
	for imgname in img_list[1563:]:
		fig, ax = plt.subplots()
		i = i+1
		print i
		fig.canvas.mpl_connect('key_press_event', quit)
		#img = mpimg.imread(img.strip())
		img = mpimg.imread(imgname)
		imgplot = ax.imshow(img)
		plt.show()
