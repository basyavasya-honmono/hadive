import os
import psycopg2
import argparse
import pandas as pd
from shutil import copyfile
from StringIO import StringIO
from lxml.etree import Element, SubElement, tostring, ElementTree

def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description='Create VOC formatted .xml files from dot_pub_cams database & copy .jpg files.')
    parser.add_argument('--path', dest='path', help='Output path for .xml & .jpg files')
    args = parser.parse_args()
    return args

class VOC_xml_format(object):
    """Create and write .xml file in VOC format.
    
    Attributes:
        data: pandas dataframe including all bounding boxes.
        img: image name to include in the xml file.
        xml: VOC formatted xml file (default is None).
    """
    
    def __init__(self, data, img):
        self.data = data
        self.img = img
        self.xml = None

    def create_xml(self):
        """Creates xml in VOC format from provided data."""
        
        top = Element('annotation')
        
        # Create xml header with img info, omitted source and owner.
        folder = SubElement(top, 'folder')
        folder.text = 'NA'
        filename = SubElement(top, 'filename')
        filename.text = self.img
        size = SubElement(top, 'size')
        width = SubElement(size, 'width')
        width.text = '352'
        height = SubElement(size, 'height')
        height.text = '240'
        depth = SubElement(size, 'depth')
        depth.text = '0'
        seg = SubElement(top, 'segmented')
        seg.text = '0'
        
        # Add objects to xml.
        for row in self.data:
            obj = SubElement(top, 'object')
            name = SubElement(obj, 'name')
            name.text = row[4]
            pose = SubElement(obj, 'pose')
            pose.text = 'NA'
            truncated = SubElement(obj, 'truncated')
            truncated.text = '0'
            difficult = SubElement(obj, 'difficult')
            difficult.text = '0'
            bndbox = SubElement(obj, 'bndbox')
            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(min(row[0], row[2]))
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(min(row[1], row[3]))
            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(max(row[0], row[2]))
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(max(row[1], row[3]))
            
        self.xml = top
    
    def write_xml(self, file_path, encoding='utf-8'):
        """Write stored xml document to file
        
        Args:
            file_path (str): output path xml will be written to, 
                including filename.
            encoding (str, optional): encoding format, for output file
                (default is utf-8).
        """
        
        tree = ElementTree(self.xml)
        tree.write(file_path, pretty_print=True, encoding=encoding)
        
    def print_xml(self):
        """Print formatted xml to console."""
        
        print tostring(self.xml, pretty_print=True)
    
def check_xml(labels):
    try:
	labels_ = list()
        for label in labels:
	    xmin, ymin, xmax, ymax, lab = label
            # Fix labels on the edge of the image.
            if xmin < 1:
                xmin = 1
            if ymin < 1:
                ymin = 1
            if xmax > 351:
                xmax = 351
            if ymax > 239:
                ymax = 239
            # print 'xmin: {}, ymin: {}, xmax: {}, ymax: {}, lab: {}'.format(xmin, ymin, xmax, ymax, lab)
            # Remove labels that are too small.
            if xmax - xmin > 2:
		if ymax - ymin > 2:
		    labels_.append((xmin, ymin, xmax, ymax, lab))
	return labels_
    except:
	pass
	
if __name__ == '__main__':
    args = parse_args()
    
    try:
        conn = psycopg2.connect("dbname='dot_pub_cams'")
    except:
        print 'Failure to connect to dot_pub_cams.'
        
    cursor = conn.cursor()
    
    img_sql='''
    SELECT id, image_path, name
    FROM images
    WHERE labeled=True'''
    
    cursor.execute(img_sql)
    images = cursor.fetchall()
    
    if not os.path.exists(args.path + '/JPEGImages/'):
        os.makedirs(args.path + '/JPEGImages/')
    if not os.path.exists(args.path + '/Annotations/'):
        os.makedirs(args.path + '/Annotations/')

    for idx, im_path, name in images:
        label_sql = '''
        SELECT topx, topy, botx, boty, type
        FROM labels
        WHERE image={}'''.format(idx)
        
        if os.path.isfile(os.path.join(im_path, name)): # Check if image exists.
	    cursor.execute(label_sql)
            labels = check_xml(cursor.fetchall()) # Clean up .xml data.
	    if len(labels) > 0: # Check if there are remaining labels.	
	    	copyfile(os.path.join(im_path, name), os.path.join(args.path + '/JPEGImages/', name))
            	VOC_xml = VOC_xml_format(labels, name)
            	VOC_xml.create_xml()
            	VOC_xml.write_xml(args.path + '/Annotations/' + name[:-4] + '.xml')
        
