# Function that lists "how_many" images in subdirectories of a given "path" for a specific "camera" starting from "from_hour" and ending at "to_hour"
import fnmatch
import os


def list_images(path, camera, from_hour, to_hour, how_many):
  image_list = []
	count = 0
	for root, dirnames, filenames in os.walk(path):
		for filename in fnmatch.filter(filenames, '*.jpg'):
			if camera in filename: 
				if (int(filename.split('-')[3]) >= from_hour and int(filename.split('-')[3]) <= to_hour):
					image_list.append(os.path.join(root, filename))
					count+=1
        			if count == how_many: 
						return image_list
	return image_list 
