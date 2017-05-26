import os
import argparse
import lxml.etree as etree

def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description='Clean training dataset (delete .jpg & .xml files without labels)')
    parser.add_argument('--path', dest='path', help='Output path for .xml & .jpg files')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    xmls = os.listdir(args.path + 'Annotations/')
    
    for xml in xmls:
        tree = etree.parse(args.path + 'Annotations/' + xml)
        objs = tree.findall('object')

        if len(objs) < 1:
            os.remove(args.path + 'Annotations/' + xml)
	    os.remove(args.path + 'JPEGImages/' + xml[:-4] + '.jpg')
	
	for obj in objs:
	    xmin = int(obj.findall('bndbox/xmin')[0].text)
	    xmax = int(obj.findall('bndbox/xmax')[0].text)
	    ymin = int(obj.findall('bndbox/ymin')[0].text)
	    ymax = int(obj.findall('bndbox/ymax')[0].text)
	    xdiff = abs(xmin - xmax)
	    ydiff = abs(ymin - ymax)

	    try:
	        if xdiff < 3:
		    os.remove(args.path + 'Annotations/' + xml)
		    os.remove(args.path + 'JPEGImages/' + xml[:-4] + '.jpg')

	        if ydiff < 3:
                    os.remove(args.path + 'Annotations/' + xml)
                    os.remove(args.path + 'JPEGImages/' + xml[:-4] + '.jpg')

		if xmin < 1:
                    os.remove(args.path + 'Annotations/' + xml)
                    os.remove(args.path + 'JPEGImages/' + xml[:-4] + '.jpg')

		if xmax > 351:
                    os.remove(args.path + 'Annotations/' + xml)
                    os.remove(args.path + 'JPEGImages/' + xml[:-4] + '.jpg')

		if ymin < 1:
                    os.remove(args.path + 'Annotations/' + xml)
                    os.remove(args.path + 'JPEGImages/' + xml[:-4] + '.jpg')

		if ymax > 239:
                    os.remove(args.path + 'Annotations/' + xml)
                    os.remove(args.path + 'JPEGImages/' + xml[:-4] + '.jpg')

	    except:
		continue

    print len(os.listdir(args.path + 'Annotations/')) 
