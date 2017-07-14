import os
import numpy as np
import lxml.etree as etree
import argparse

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Train new dataset')
    parser.add_argument('--xml', dest='annotation_path',
                        type=str)
    parser.add_argument('--class', dest='object_class',
                        type=str)
    parser.add_argument('--txt', dest='text_path', help='File store image name',
                        default='trainval.txt')
    
    args = parser.parse_args()

    return args

class main_file(object):
    def __init__(self, xml_path):
    	'''Create main's files for new dataset
    	Parameters:
    	xml_path - location of .xml file.'''
        self.xml_path = xml_path

 #   xml_path = os.listdir(args.annotation_path + '/Annotations/')

    def get_obj(self):
        '''Identify if the picture contain positive/negative examples of the class'''
        
        tree = etree.parse(self.xml_path)
        obj_elems = tree.findall('object')
        object = -1
        for obj in obj_elems:
            for ele in obj:
                if ele.tag == 'name':
                    if ele.text == args.object_class:
                        object = 1
                        break
        self.obj = object
        return self.obj    

''' Add 1 to file name if it contains any positive example and -1 if vice versa'''
    
    
if __name__ == '__main__':
    args = parse_args()
    with open(args.text_path, 'r') as f:
        for line in f:
            xml_path = args.annotation_path + '/Annotations/' + line + '.xml'
            xml_path = xml_path.replace('\n','')
            im = main_file(xml_path)
            im.get_obj()
            #print(str(im.obj))
            print((line+' '+str(im.obj)).replace('\n',''))
        
    