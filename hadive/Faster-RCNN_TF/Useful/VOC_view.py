import os
import pylab
import random
import argparse
import lxml.etree as etree
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from matplotlib.image import imread

def parse_args():
    """Parse input arguments"""
    
    parser = argparse.ArgumentParser(description='Compare two VOC images')
    parser.add_argument('--orig_path', dest='orig_path',
                        help='Location to original VOC data')
    parser.add_argument('--resized_path', dest='resized_path',
                        help='Location of resized VOC data')
    parser.add_argument('--img_num', dest='img_num',
                        help='VOC image number to compare')
    
    args = parser.parse_args()
    return args

def parse_xml(path):
    """Parse VOC .xml files and returns all bounding boxes.
    
    Args:
        path (str): path to .xml file.
    
    Returns:
        List of lists representing each bounding box (e.g., [[xmin, ymin, xmax, ymax]]
    """
    
    tree = etree.parse(path)
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
    return boxes
    
class compare_img(object):
    """Compare two VOC images side-by-side (original and resized).
    
    Attributes:
        orig_path (str): path to original VOC dataset including JPEGImages and Annotations folders.
        resized_path (str): path to resized VOC dataset including JPEGImages and Annotations folders.
        img_num (str): VOC img to be compared (e.g., 000001).
        orig_boxes: bounding boxes of original image.
        resized_boxes: bounding boxes of resized image.
    """
    
    def __init__(self, orig_path, resized_path, img_num):
        self.orig_path = orig_path
        self.resized_path = resized_path
        self.img_num = img_num
        self.orig_boxes = None
        self.resized_boxes = None

    def get_boxes(self):
        """Parse .xml files for original and resized images."""
        
        orig_xml = os.path.join(self.orig_path, 'Annotations', str(self.img_num) + '.xml')
        resized_xml = os.path.join(self.resized_path, 'Annotations', str(self.img_num) + '.xml')
        
        self.orig_boxes = parse_xml(orig_xml)
        self.resized_boxes = parse_xml(resized_xml)
    
    def visualize(self):
        """Plot original and resized images with bounding boxes side-by-side."""
        
        orig_img = os.path.join(self.orig_path, 'JPEGImages', str(self.img_num) + '.jpg')
        resized_img = os.path.join(self.resized_path, 'JPEGImages', str(self.img_num) + '.jpg')
        orig = imread(orig_img)
        resized = imread(resized_img)
        fig, ([ax1, ax2]) = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
        
        ax1.imshow(orig)
        for box in map(lambda x: x[1], self.orig_boxes):
            ax1.add_patch(
                patches.Rectangle((box[0], box[3]),
                                  (box[2] - box[0]),
                                  (box[1] - box[3]),
                                  fill=False, edgecolor='red'))
        
        ax2.imshow(resized)
        for box in map(lambda x: x[1], self.resized_boxes):
            ax2.add_patch(
                patches.Rectangle((box[0], box[3]),
                                  (box[2] - box[0]),
                                  (box[1] - box[3]),
                                  fill=False, edgecolor='red'))
        pylab.show()

if __name__ == '__main__':
    args = parse_args()
    print 'Called with args:\n{}'.format(args)
    
    test = compare_img(args.orig_path, args.resized_path, args.img_num)
    test.get_boxes()
    test.visualize()
