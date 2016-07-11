# Generating list of coordinates for patches
# The function returns a set of top left and bottom right coordinates of all possible patches no smaller than 10 and no larger 
# than the maximal allowed width as [(x1, y1, x2, y2)]
import numpy as np

def get_patches():
	# Size of the image
  width = 352
	height = 240
	# Due to the fixed ration of 3:4 width to hight fixing the maximal width that could be used for a patch
	maxwidth = int(height*0.75)
	# patches will be added here
	patches = []
	
	# Going over the sizes of the patches
	for size in range (10, maxwidth):
		# going over the x coordinate
		for w in range (0, width - size):
			y = int(size*1.33)
			# going over the y coordinate
			for h in range (0, height - y):
				# appending the a patch coordinates
				patches.append((w, h, w + size, h + y))
	return patches
