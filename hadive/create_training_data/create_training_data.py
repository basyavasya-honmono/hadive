import os
import sqlite3
import numpy as np
from lxml.etree import Element, SubElement, ElementTree, tostring
np.random.seed(1)

def imgs_wo_xmls():
    """Get list of labeled imgs without corresponding xmls."""
    conn = sqlite3.connect("../../data/training/training.db")
    c = conn.cursor()
    # Collect all imgs and xmls
    imgs = set(map(lambda x: x[0][:-4], c.execute("SELECT image FROM images WHERE labeled=1").fetchall()))
    xmls = set(map(lambda x: x[:-4], os.listdir("../../data/training/xml/")))
    conn.close()
    # Return list of imgs without corresponding xmls.
    return list(imgs - xmls)


def train_test_split():
    """Write train & test .txt files with 70/30 split."""
    # Remove existing files.
    os.system("rm ../../data/training/txt/*")
    # Collect all xml files and shuffle names.
    data = map(lambda x: x[:-4], os.listdir("../../data/training/xml/"))
    np.random.shuffle(data)
    # Create 70/30 train-test split.
    split = len(data) * .7
    train = data[:int(np.floor(split))]
    test = data[int(np.ceil(split)):]
    # Write splits to file.
    with open(os.path.join("../../data/training/txt/" + "train.txt"), 'w') as train_txt:
        for i in train:
            train_txt.write("{}\n".format(i))
    with open(os.path.join("../../data/training/txt/" + "test.txt"), 'w') as test_txt:
        for i in test:
            test_txt.write("{}\n".format(i))
    print '{} training images and {} testing images'.format(len(train), len(test))


class xml_writer(object):
    """Create and write xml files in VOC format using labeled data."""


    def __init__(self, img):
        self.img = img + ".jpg"
        self.bboxes = None
        self.xml = None


    def load_data(self):
        """Load labels data from db."""
        conn = sqlite3.connect("../../data/training/training.db")
        c = conn.cursor()
        bboxes = c.execute("SELECT name, xmin, xmax, ymin, ymax FROM labels WHERE image='{}'".format(self.img)).fetchall()
        conn.close()
        # Validate & edit boxes to all be <1 pixel from the image edge
        # and width/height >2 pixels.
        bboxes_validated = []
        for name, xmin, xmax, ymin, ymax in bboxes:
            if xmin < 1:
                xmin = 1
            if ymin < 1:
                ymin = 1
            if xmax > 351:
                xmax = 351
            if ymax > 239:
                ymax = 239
            if xmax - xmin > 2 and ymax - ymin > 2:
                bboxes_validated.append([name, xmin, xmax, ymin, ymax])
        self.bboxes = bboxes_validated


    def create_xml(self):
        """Creates xml file from loaded data."""
        top = Element("annotation")
        # Create xml header with img info.
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
        # Add each bounding box.
        for name, xmin, xmax, ymin, ymax in self.bboxes:
            obj = SubElement(top, 'object')
            name_ = SubElement(obj, 'name')
            name_.text = name
            pose = SubElement(obj, 'pose')
            pose.text = 'NA'
            truncated = SubElement(obj, 'truncated')
            truncated.text = '0'
            difficult = SubElement(obj, 'difficult')
            difficult.text = '0'
            bndbox = SubElement(obj, 'bndbox')
            xmin_ = SubElement(bndbox, 'xmin')
            xmin_.text = str(min(xmin, xmax))
            ymin_ = SubElement(bndbox, 'ymin')
            ymin_.text = str(min(ymin, ymax))
            xmax_ = SubElement(bndbox, 'xmax')
            xmax_.text = str(max(xmin, xmax))
            ymax_ = SubElement(bndbox, 'ymax')
            ymax_.text = str(max(ymin, ymax))
        self.xml = top


    def print_xml(self):
        """Pretty print shortcut."""
        print tostring(self.xml, pretty_print=True)


    def write_xml(self, encoding="utf-8"):
        """Write xml tree to file and update db to labeled=1."""
        tree = ElementTree(self.xml)
        tree.write(os.path.join("../../data/training/xml/", self.img[:-4] + ".xml"), pretty_print=True, encoding=encoding)
        conn = sqlite3.connect("../../data/training/training.db")
        c = conn.cursor()
        c.execute("UPDATE images SET labeled=1 WHERE image='{}'".format(self.img))
        conn.commit()
        conn.close()
        print "Succesfully wrote: {}".format(self.img[:-4] + ".xml")


if __name__ == '__main__':
    # Find all labeled images without a corresponding xml.
    imgs = imgs_wo_xmls()
    if len(imgs) == 0:
        print "All images have a corresponding .xml file."
    # Write an xml file for each image.
    for img in imgs:
        xml = xml_writer(img)
        xml.load_data()
        xml.create_xml()
        xml.write_xml()
    # Rewrite train-test text files.
    train_test_split()
