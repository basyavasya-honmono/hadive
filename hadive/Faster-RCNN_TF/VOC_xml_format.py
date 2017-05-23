import psycopg2
import argparse
import pandas as pd
from StringIO import StringIO
from lxml.etree import Element, SubElement, tostring, ElementTree

def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description='Create VOC formatted .xml files from dot_pub_cams database.')
    parser.add_argument('--path', dest='path', help='Output path for .xml files')
    args = parser.parse_args()
    return args

class VOC_xml_format(object):
    """Create and write .xml file in VOC format.
    
    Attributes:
        data: pandas dataframe including all bounding boxes.
        xml: VOC formatted xml file (default is None).
    """
    
    def __init__(self, data):
        self.data = data
        self.xml = None

    def create_xml(self):
        """Creates xml in VOC format from provided data."""
        
        top = Element('annotation')
        
        # Create xml header with img info, omitted source and owner.
        folder = SubElement(top, 'folder')
        folder.text = 'NA'
        filename = SubElement(top, 'filename')
        filename.text = self.data.img.unique()[0] # .img placeholder
        size = SubElement(top, 'size')
        width = SubElement(size, 'width')
        width.text = str(self.data.width.unique()[0]) # .width placeholder
        height = SubElement(size, 'height')
        height.text = str(self.data.height.unique()[0]) # .height placeholder
        depth = SubElement(size, 'depth')
        depth.text = '0'
        seg = SubElement(top, 'segmented')
        seg.text = '0'
        
        # Add objects to xml.
        for idx, row in self.data.iterrows():
            obj = SubElement(top, 'object')
            name = SubElement(obj, 'name')
            name.text = row.label # .label placeholder
            pose = SubElement(obj, 'pose')
            pose.text = 'NA'
            truncated = SubElement(obj, 'truncated')
            truncated.text = '0'
            difficult = SubElement(obj, 'difficult')
            difficult.text = '0'
            bndbox = SubElement(obj, 'bndbox')
            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(row.xmin) # .xmin placeholder
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(row.ymin) # .ymin placeholder
            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(row.xmax) # .xmax placeholder
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(row.ymax) # .ymax placeholder
            
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

if __name__ == '__main__':
    args = parse_args()
    
    try:
        conn = psycopg2.connect("dbname='dot_pub_cams'")
    except:
        print 'Failure to connect to dot_pub_cams.'
        
    cursor = conn.cursor()
    
    img_sql='''
    SELECT id, name
    FROM images
    WHERE labeled=True'''
    
    cursor.execute(img_sql)
    data = cursor.fetchall()
    
    for idx, name in data:
        label_sql = '''
        SELECT topx, topy, botx, boty, type
        FROM labels
        WHERE image={}'''.format(idx)
        
        cursor.execute(label_sql)
        VOC_xml = VOC_xml_format(cursor.fetchall(), name)
        VOC_xml.create_xml()
        VOC_xml.write_xml(args.path + name[:-4] + '.xml')
        