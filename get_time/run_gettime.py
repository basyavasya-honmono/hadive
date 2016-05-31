from get_time import get_time
import os
#import datetime

# path.txt contains the address of the directory with images

#print (datetime.datetime.now())

with open('path.txt') as f:
	path = f.readlines()[0].rstrip()
print path

images = []
for root, dirs, files in os.walk(path):
	for file in files:
		if file.endswith('.jpg'):
			images.append(os.path.join(root, file))

# Getting addresses of the first 10 images for the camera named "8_Ave__14_St" that were recorded from 7 a.m. to 7 p.m.

i = 0
for im in images:
	i+=1
	print (i)
	print "Old name: " + im
	new_name = get_time(im)+'.jpg'
        os_path = os.path.join( os.path.dirname(im), new_name)
        print "New name: " + os_path
        #os.rename(im, os.path.join(os.path.dirname(im), new_name)) 
	print "\n"

print (i)

#print (datetime.datetime.now())
