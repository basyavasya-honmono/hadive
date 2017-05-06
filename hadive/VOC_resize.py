import os
import random
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
        self.by = 1
        self.to_path = 'PATH'
        self.im_orig = None
        self.im = None
        
    def get_boxes(self):
    	'''Takes resize_training_data and extracts bounding boxes from xml'''
        
        tree = etree.parse(self.xml_path)
        obj_elems = tree.findall('object')
        boxes = []
        for obj in obj_elems:
            for ele in obj:
                box = []
                if ele.tag == 'name':
                    label = ele.text
                if ele.tag == 'bndbox':
                    for coor in ele:
                        box.append(int(coor.text))
                    boxes.append((label, box))  
                    
        self.boxes = boxes
        return self.boxes

    def person_size(self, DOT_height, boxes=None):
        '''Calculate best int to resize img
        DOT_height - DOT cam person height to scale to.
        boxes - xml bounding boxes'''
            
        if boxes != None:
            self.boxes = boxes
                
        personboxes = filter(lambda x: x[0] == 'person', self.boxes)
                    
        if len(personboxes) > 0:
            bndboxes = map(lambda x: x[1], personboxes)
            height = map(lambda x: x[3] - x[1], bndboxes)
            height_avg = sum(height) / float(len(height))
                                    
            best_size = (0, 9999) # Placeholder.
            for i in range(1, 10):
                diff = abs(height_avg - DOT_height * i)
                if best_size[1] > diff:
                    best_size = (i, diff)
            self.by = best_size[0]
                                                            
        else:
            self.by = random.choice([1, 2, 3, 4, 5, 6])
                                                                    
        return self.by
    
    def resize(self, to_path, by=1):
    	'''Resizes .jpeg & .xml bounding boxes by factor 'by' and exports files to to_path
    	Parameter:
    	by - factor to resize .jpeg & .xml
    	to_path - path where .jpeg & .xml will be output (in VOC folder structure)'''

        if by != 1:
            self.by = by
        self.to_path = to_path
        
        im = Image.open(self.img_path)
        im_resize = im.resize(tuple(map(lambda x: x / self.by, im.size)), Image.BILINEAR)
        
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
        
        width_obj = tree.findall('size/width')
        height_obj = tree.findall('size/height')

        width_obj[0].text = str(int(width_obj[0].text) / self.by)
        height_obj[0].text = str(int(height_obj[0].text) / self.by)
        
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

def main(training, output, DOT_height):
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
        img_path = training + '/JPEGImages/' + img
        xml_path = training + '/Annotations/' + xml
        
        r_obj = resize_training_data(xml_path, img_path)
        r_obj.get_boxes()
        r_obj.person_size(DOT_height)
        r_obj.resize(output)

if __name__ == '__main__':
	main('/Users/JordanVani/Documents/NYU/GRA/R-CNNs/PASCAL VOC 2007/VOCdevkit/VOC2007/',
		 '/Users/JordanVani/Documents/NYU/GRA/R-CNNs/PASCAL VOC 2007/VOCdevkit/Resampling',
         32.4)
