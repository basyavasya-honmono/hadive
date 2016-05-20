from get_time import get_time
import image_list
import os
#print get_time('2016-04-16-09-04-56_Grand_St__Allen_St.jpg')

# path.txt contains the address of the directory with images
with open('path.txt') as f:
	path = f.readlines()[0]
print path

# Getting addresses of the first 10 images for the camera named "8_Ave__14_St" that were recorded from 7 a.m. to 7 p.m.
images = image_list.list_images(path, "", 0, 23, 250000)
i = 0
for im in images:
	i+=1
	print (i)
	print "Old name: " + im
	new_name = get_time(im)+'.jpg'
  	print "New name: "+ os.path.join( os.path.dirname(im), new_name)
  	os.rename(im, os.path.join(os.path.dirname(im), new_name)) 
	print "\n"
