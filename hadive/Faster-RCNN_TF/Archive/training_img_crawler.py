import os
import re
from shutil import copyfile
from collections import defaultdict

source_dir = '/projects/projects/project-computer_vision_capstone_2016/workspace/share/dot_images_3'
dest_dir = '/projects/projects/project-computer_vision_capstone_2016/workspace/share/training_data'

try:
    os.mkdir('JPEGImages/')
    os.mkdir('npyFiles/')
except:
    pass

f_dict = defaultdict(list)
dup_img = ''
for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith('.npy'):
            img = re.split('_neg|_pos', file)[0] + '.jpg'
            img_path = os.path.join(root, img)
            if dup_img != img_path:
                try:
                    copyfile(img_path, os.path.join(dest_dir, 'JPEGImages', img))
                except:
                    print 'Permission not granted to copy ' + img 
                dup_img = img_path

            try:
                copyfile(os.path.join(root, file), os.path.join(dest_dir, 'npyFiles', file))
            except:
                print 'Permission not granted to copy ' + file

            f_dict[img].append(file)

print 'Images: {}'.format(len(f_dict.keys()))

npy = set(map(lambda x: re.split('_neg|_pos', x)[0], os.listdir('npyFiles/')))
jpeg = set(map(lambda x: x.rstrip('.jpg'), os.listdir('JPEGImages/')))

del_files = list(npy - jpeg)
for i in del_files:
    os.remove(os.path.join('npyFiles', i))
