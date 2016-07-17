import os,sys
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.backends.backend_agg import FigureCanvasAgg


def quit(event):
	print('press', event.key)
	sys.stdout.flush()
	if event.key == 'q':
		plt.close()
	elif event.key == '0':
		sys.exit()

if __name__ == '__main__':
	with open('false_pos_svm_fixed.txt') as file:
		img_list = file.readlines()
		img_list = filter(lambda x: x[:2]!='C ',img_list)
		print len(img_list)
		for img in img_list:
			fig, ax = plt.subplots()
			fig.canvas.mpl_connect('key_press_event', quit)
			#img = mpimg.imread(img.strip())
			img = np.load(img.strip())
			imgplot = ax.imshow(img)
			plt.show()
