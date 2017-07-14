import os
import numpy as np
import lxml.etree as etree
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageOps 
import cv2

class zero_padding_training_data(object):
    def __init__(self, xml_path, img_path):
    	'''Create Zero-padded_training_data object
    	Parameters:
    	xml_path - location of .xml file.
    	img_path - location of .jpeg file.'''
    
        self.xml_path = xml_path
        self.img_path = img_path
        self.to_path = 'PATH'
        
    
    def zero_padding(self, to_path):
    	'''Zero padding .jpeg & .xml bounding boxes by factor 'by' and exports files to to_path
    	Parameter:
    	to_path - path where .jpeg & .xml will be output (in VOC folder structure)'''
        self.to_path = to_path
        
        zero = [0,0,0]
        im = Image.open(self.img_path)
        w_0 = im.size[0]
        h_0 = im.size[1]
        
        #Modify image size in xml
        tree = etree.parse(self.xml_path)
        obj_elems = tree.findall('object')
        
        w_dif = 0
        h_dif = 0

        size_elems = tree.findall('size')
        for size in size_elems:
            for ele in size:
                if ele.tag == 'width':
                    if w_0 < 300:
                        w_dif = int(np.ceil(300 - w_0))
                        ele.text = str(300)
                    else:
                        ele.text = str(w_0)
                if ele.tag == 'height':
                    if h_0 < 300:
                        h_dif = int(np.ceil(300 - h_0))
                        ele.text = str(300)
                    else:
                        ele.text = str(h_0)
        
#        print((w_dif, h_dif),(w_dif/2, h_dif/2))        
        
        for obj_num, obj in enumerate(obj_elems):
            box_elem = obj.findall('bndbox')

            bbox = obj.find('bndbox')
            bbox.find('xmin').text = str(float(bbox.find('xmin').text) + w_dif/2)
            bbox.find('ymin').text = str(float(bbox.find('ymin').text) + h_dif/2)
            bbox.find('xmax').text = str(float(bbox.find('xmax').text) + w_dif/2)
            bbox.find('ymax').text = str(float(bbox.find('ymax').text) + h_dif/2)
                
               
            
        tree.write(self.to_path + '/Annotations/' + os.path.basename(self.xml_path))
        
        border=(int(w_dif/2),int(h_dif/2),w_dif-int(w_dif/2),h_dif-int(h_dif/2))
        im_zero = ImageOps.expand(im,border=border,fill='black')
        self.im_orig = im
        self.im = im_zero
        
        im_zero.convert('RGB').save(self.to_path + '/JPEGImages/' + os.path.basename(self.img_path))
        
def main(training, output):
    '''Zero padding all .jpeg & .xml in VOC training data.
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
    
    try:
        os.remove(training + '/JPEGImages/' + '.DS_Store')
    except OSError as e:
        print(e)
    
    for img, xml in zip(in_img, in_xml):
        #  if not img.startswith('.') and img != 'Thumbs.db':
        #      print(img,xml)
        img_path = training + '/JPEGImages/' + img
        xml_path = training + '/Annotations/' + xml
        
        r_obj = zero_padding_training_data(xml_path, img_path)
        r_obj.zero_padding(output)

    
if __name__ == '__main__':
#	main('/Users/mac/AnacondaProjects/human_detection/Hadive/Faster-RCNN_TF/data/VOCdevkit2007/VOC2007_resample/',
#		 '/Users/mac/AnacondaProjects/human_detection/Hadive/Faster-RCNN_TF/data/VOCdevkit2007/VOC_zero/')    
    
	main('/home/ttd255/Faster-RCNN_TF/data/VOCdevkit/VOC2007/b4zero',
		 '/home/ttd255/Faster-RCNN_TF/data/VOCdevkit/VOC2007/')                    
