import os,sys
import numpy as np
import pickle
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg



# import the necessary packages
import numpy as np
 
# Malisiewicz et al.
def non_max_suppression_fast(boxes, overlapThresh):
	# if there are no boxes, return an empty list
	if len(boxes) == 0:
		return []
 
	# if the bounding boxes integers, convert them to floats --
	# this is important since we'll be doing a bunch of divisions
	if boxes.dtype.kind == "i":
		boxes = boxes.astype("float")
 
	# initialize the list of picked indexes	
	pick = []
 
	# grab the coordinates of the bounding boxes
	y1 = boxes[:,0]
	x1 = boxes[:,1]
	y2 = boxes[:,2]
	x2 = boxes[:,3]
 	#print x1,y1,x2,y2
	# compute the area of the bounding boxes and sort the bounding
	# boxes by the bottom-right y-coordinate of the bounding box
	area = (x2 - x1 + 1) * (y2 - y1 + 1)
	idxs = np.argsort(y2)
 
	# keep looping while some indexes still remain in the indexes
	# list
	while len(idxs) > 0:
		# grab the last index in the indexes list and add the
		# index value to the list of picked indexes
		last = len(idxs) - 1
		i = idxs[last]
		pick.append(i)
 
		# find the largest (x, y) coordinates for the start of
		# the bounding box and the smallest (x, y) coordinates
		# for the end of the bounding box
		xx1 = np.maximum(x1[i], x1[idxs[:last]])
		yy1 = np.maximum(y1[i], y1[idxs[:last]])
		xx2 = np.minimum(x2[i], x2[idxs[:last]])
		yy2 = np.minimum(y2[i], y2[idxs[:last]])
 
		# compute the width and height of the bounding box
		w = np.maximum(0, xx2 - xx1 + 1)
		h = np.maximum(0, yy2 - yy1 + 1)
 
		# compute the ratio of overlap
		overlap = (w * h) / area[idxs[:last]]
 
		# delete all indexes from the index list that have
		idxs = np.delete(idxs, np.concatenate(([last],
			np.where(overlap > overlapThresh)[0])))
 
	# return only the bounding boxes that were picked using the
	# integer data type
	return boxes[pick].astype("int")




def extract_arrays(f):
	#print f
	#name = (f[1:-1].split(',',1)[0])
	#str_array =  (f[1:-1].split(',',1)[1])
	ls = np.array(map(lambda x: int(float(x)), re.findall("[-+]?\d+[\.]?\d*", f)))
	if len(ls)>0:
		ls_a = list(np.reshape(ls, (len(ls)/4, 4)))
	else:
		ls_a = ls

	#prob_ = np.array(map(lambda x: int(float(x)), re.findall("[-+]?\d+[\.]?\d*", prob_)))




	return (ls_a)


def extract_probs(f):
	ls = np.array(map(lambda x: float(x), re.findall("[-+]?\d+[\.]?\d*", f)))
	return ls
def draw_rects(img,rects_coords):


	pass



if __name__ == "__main__":
	path = "../../../../../../share/team5/" 
	#print img_list,'imageeeeeeee'
	coords_current = []


	with open('counts.txt') as file:
	
		data = file.readlines()
		data = filter(lambda x:x!='\n',data)
		probs = map(lambda x: x.split('prob_blues'),data)
		
		coords = map(lambda x: x[0].split('Coords'), probs[:])
		coords = map(lambda x: x[1], coords)
		probs = map(lambda x: x[1],probs)
		
		rects = map(lambda x: extract_arrays(x.strip()),coords)
		probs = map(lambda x: extract_probs(x.strip()),probs)
	img_list = os.listdir(path)[30:130]
	#print rects,probs
	i = 0
	#print rects
	#print rects
	#boxes = np.asarray(rects).reshape((len(rects),4))
	for imgname,coords,prob_ in zip(img_list,rects[30:130],probs[30:130]):
		#print coords
		i = i+1
		#array([137, 303, 177, 330])]
		#for c in coords:
		#	if ((coords[0] in range(134,140)) and (coords[3] in range(173,180)) and (coords[2] in range(300,310)) and (coords[1] in range(325,335))):
		#		coords.remove(c)
			
		#[item for sublist in coords for item in sublist]
		
		boxes = np.asarray(coords).reshape((len(coords),4))
		ind = []
		# the ratio should be less the 1
		# chosen here is 0.6
		coords = non_max_suppression_fast(boxes, 0.6)
		
		for c in coords:
			ind.append(int(np.where(c in boxes)[0]))
			
		prob_ = map(lambda x: prob_[x], ind)
		img = mpimg.imread(path+imgname)
		fig1 = plt.figure()
		ax1 = fig1.add_subplot(111, aspect='equal'
		)
		ax1.imshow(img)
		rects_patch = []
		area_patch = []
		rects_to_draw = []
		#print prob_,'PROB'
		for rect,pr in zip(coords,prob_):
			x = rect[1]
			y = rect[0]
			width = rect[3] - rect[1]
			height = rect[2] - rect[0]
			cx = int( x + width/2.0)
			cy = int(y + height/2.0)
			ed = np.sqrt(cx**2 + cy**2)
			#print ed	
			ax1.text(x,y,str(pr),fontsize=8)
			rects_patch.append(patches.Rectangle((x,y),width,height,color='b',fill=False,linewidth=2))
		
		with open('finalcount.txt','a') as f:
			f.write('image %s counts %s' % (imgname,len(rects_patch)))
		for p in rects_patch:
			ax1.add_patch(p)

		#fig1.savefig(str(i)+'.png', dpi=90, bbox_inches='tight')	
		fig1.patch.set_visible(False)
		ax1.axis('off')

		with open('hog_svm_noBLOBS/'+str(i)+'.jpg', 'w') as outfile:
    			fig1.canvas.print_png(outfile)
		plt.show()	
