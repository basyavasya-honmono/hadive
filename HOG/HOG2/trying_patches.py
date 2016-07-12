import os,sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pickle


if __name__ == "__main__":
	

	with open('/gws/projects/project-computer_vision_capstone_2016/workspace/share/patch2.pkl') as file:
		data = pickle.load(file)
		data = list(data['path'])
		path = data[1]
		img = np.load(path)
		imgplot = plt.imshow(img)
		plt.show()
