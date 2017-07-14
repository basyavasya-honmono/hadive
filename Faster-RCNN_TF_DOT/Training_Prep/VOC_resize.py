import os
import numpy as np
import lxml.etree as etree
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

class resize_training_data(object):
    def __init__(self, xml_path, img_path):
    	'''Create resize_training_data object
    	Parameters:
    	xml_path - location of .xml file.
    	img_path - location of .jpeg file.'''
    
        self.xml_path = xml_path
        self.img_path = img_path
        self.boxes = None
        #self.by = 1
        self.to_path = 'PATH'
        
    def get_boxes(self):
    	'''Takes resize_training_data and extracts bounding boxes from xml'''
        
        tree = etree.parse(self.xml_path)
        size_elems = tree.findall('size')
        
        by = 1
        for size in size_elems:
            for ele in size:
                if ele.tag == 'height':
                    by = float(ele.text)/240
                    
        obj_elems = tree.findall('object')
        boxes = []
        count_person = 0
        count_others = 0
        count_total = 0
        for obj in obj_elems:
            for ele in obj:
                box = []
                if ele.tag == 'name':
                    label = ele.text
                    if ele.text == 'person':
                        #by == np.random.uniform(2,4) # need edition for best size
                        count_person =+ 1
                    else:
                        count_others =+ 1
                if count_person > 0 and count_others > 0: #Mark the image having person & other obj
                    count_total = 1            
                if ele.tag == 'bndbox':
                    for coor in ele:
                        box.append(int(coor.text))
                    boxes.append((label, box))  
        for i,ele in enumerate(boxes):
            if ele[0] == 'person':
                person_size=[47.5,57.31,38.55,37.77] 
                by=(ele[1][3]-ele[1][1])/np.random.choice(person_size)
        self.boxes = boxes
        self.by = by
        self.count = count_total
        return self.boxes, self.by, self.count
    
    def resize(self, by, to_path):
    	'''Resizes .jpeg & .xml bounding boxes by factor 'by' and exports files to to_path
    	Parameter:
    	by - factor to resize .jpeg & .xml
    	to_path - path where .jpeg & .xml will be output (in VOC folder structure)'''
        self.by = by
        self.to_path = to_path
        
        im = Image.open(self.img_path)
        im_resize = im.resize(tuple(map(lambda x: int(x / self.by), im.size)), Image.BILINEAR)
        
        self.im_orig = im
        self.im = im_resize
        
        im_resize.save(self.to_path + '/JPEGImages/' + os.path.basename(self.img_path))
        
        tree = etree.parse(self.xml_path)
        obj_elems = tree.findall('object')
        
        for obj_num, obj in enumerate(obj_elems):
            box_elem = obj.findall('bndbox')
            for box in box_elem:
                for coord_num, coord in enumerate(box):
                    coord.text = str(self.boxes[obj_num][1][coord_num] / self.by)
        #Modify image size in xml
        size_elems = tree.findall('size')
        for size in size_elems:
            for ele in size:
                if ele.tag == 'width':
                    ele.text = str(int(ele.text)/self.by)
                if ele.tag == 'height':
                    ele.text = str(int(ele.text)/self.by)
        
        tree.write(self.to_path + '/Annotations/' + os.path.basename(self.xml_path))
        
    def visualize(self):
    	'''Visualize image & boxes before and after resizing'''
        fig, ([ax1, ax2]) = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
        
        ax1.imshow(self.im_orig)
        for box in map(lambda x: x[1], self.boxes):
            ax1.add_patch(
                patches.Rectangle((box[0], box[3]),
                                  (box[2] - box[0]),
                                  (box[1] - box[3]),
                                  fill=False, edgecolor='red'))
        
        ax2.imshow(self.im)
        for box in map(lambda x: x[1], self.boxes):
            ax2.add_patch(
                patches.Rectangle((box[0] / self.by, box[3] / self.by),
                                  (box[2] / self.by - box[0] / self.by),
                                  (box[1] / self.by - box[3] /self.by),
                                  fill=False, edgecolor='red'))

def main(training, output):
    '''Resize all .jpeg & .xml in VOC training data.
    Parameters:
    training - path to training data (dir with both JPEGImages & Annotations)
    output - path to export resized files'''
    
    in_img = os.listdir(training + '/JPEGImages/')
    in_xml = os.listdir(training + '/Annotations/')
    
    try:
        os.mkdir(output + '/JPEGImages/')
        os.mkdir(output + '/Annotations/')
    except:
        pass
    
    for img, xml in zip(in_img, in_xml):
        if not img.startswith('.') and img != 'Thumbs.db':
            img_path = training + '/JPEGImages/' + img
            xml_path = training + '/Annotations/' + xml
        
            r_obj = resize_training_data(xml_path, img_path)
            r_obj.get_boxes()
            r_obj.resize(r_obj.by, output)
            print(r_obj.by)
        
        # Record the image having both person and others classes
            if r_obj.count > 0:
            #print(img)
                text_file = open('PersonwOther.txt', 'a')
                text_file.write(img +'\n')
                text_file.close()
    
if __name__ == '__main__':
	main('/Users/mac/AnacondaProjects/human_detection/Hadive/Faster-RCNN_TF/data/VOCdevkit2007/VOC2007_trial/',
		 '/Users/mac/AnacondaProjects/human_detection/Hadive/Faster-RCNN_TF/data/VOCdevkit2007/VOC2007_resample/')    
    
#	main('/home/ttd255/humandetection/Faster-RCNN_TF/VOCdevkit/VOC2007/b4sample',
#		 '/home/ttd255/humandetection/Faster-RCNN_TF/VOCdevkit/VOC2007/')                    
