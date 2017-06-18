import os
import sys
import cv2
import time
import string
import urllib
import datetime
import argparse
import _init_paths
import numpy as np
import tensorflow as tf
from bs4 import BeautifulSoup
from utils.timer import Timer
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from networks.factory import get_network

def UrlLocation(links):
    webcams = {i:{'location':None, 'url':None} for i in links}
    transtable = {ord(c): None for c in string.punctuation}
    for i in links:
        if len(i.strip())==0:
            continue
        target = 'document.getElementById(currentImage).src = '
        jpg = 'jpg'
        obj = urllib.urlopen(i.strip())
        html = obj.read()
        soup = BeautifulSoup(html, "lxml")
        location = soup.body.b.string.translate(transtable).replace(' ','_')
        breaker = True
        for idx, j in enumerate(soup.find_all('script')):
            txt = j.string
            if breaker:
                try:
                    if 'function setImage' in txt:
                        start = txt.find(target) + len(target) + 1
                        end = txt[start:].find(jpg) + len(jpg) + start
                        pointer = txt[start:end]
                        breaker = False
                except:
                    pass
            else:
                break
        webcams[i]['location'] = location
        webcams[i]['url'] = pointer
        if breaker:
            print 'There was no webcam link for url: %s' % i
    return webcams

def ScrapeImage(node, _dir):
    location = node['location']
    url = node['url']
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M-") + str(now.second).zfill(2)
    filename = '%s_%s.jpg' % (timestamp, location)
    
    try:
        urllib.urlretrieve(url, _dir + filename)
    except:
        print 'Error Thrown:', node['location']
    return filename

def demo(sess, net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""
    CLASSES = ('__background__', 'pos', 'neg')

    # Load the image
    im_file = os.path.join(cfg.DATA_DIR, 'DOTimages', image_name)
    im = cv2.imread(im_file)
    # Count all pos examples
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
#    print 'Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0])

    CONF_THRESH = 0.6
    NMS_THRESH = 0.3
    for cls_ind, cls in enumerate(CLASSES[1:]):
        if cls == 'pos':
            cls_ind += 1 # because we skipped background
            cls_boxes = boxes[:, 4 * cls_ind: 4 * (cls_ind + 1)]
            cls_scores = scores[:, cls_ind]
            dets = np.hstack((cls_boxes, cls_scores[:, np.newaxis])).astype(np.float32)
            keep = nms(dets, NMS_THRESH)
            dets = dets[keep, :]
            dets = np.where(dets[:, -1] >= CONF_THRESH)[0]
            #print 'People in {}: {}'.format(image_name, len(dets))
	    return len(dets)

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Count pos examples of people in DOT images')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]', default='VGGnet_test')
    parser.add_argument('--model', dest='model', help='Model path', default=' ')
    parser.add_argument('--link', dest='link', help='Link to DOT cam')
    parser.add_argument('--duration', dest='duration', help='duration to count peds (secs)')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    args = parse_args()

    # Start tensorflow
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))          # init session
    net = get_network(args.demo_net)                                             # load network
    saver = tf.train.Saver(write_version=tf.train.SaverDef.V2)                   # load model
    saver.restore(sess, args.model)
    print '\n\nLoaded network {:s}'.format(args.model)

    urlloc = UrlLocation([args.link])
    print 'Filename, Time, Count'
    for _ in range(int(args.duration)):
        start_ = time.time()
	start = time.time()
	start_print = datetime.datetime.now()
	try:
            filename = ScrapeImage(urlloc[args.link], os.path.join(cfg.DATA_DIR, 'DOTimages/'))
            download_time = time.time() - start
            start = time.time()
            count = demo(sess, net, filename)
	    count_time = time.time() - start
            os.remove(os.path.join(cfg.DATA_DIR, 'DOTimages', filename))
	    #print 'Donwload Time: {}, Count Time: {}, Total Time: {}\n'.format(download_time, count_time, time.time() - start_)
	    print '{},{},{}'.format(filename, start_print, count)
	except:
	    pass
	if time.time() - start_ < 1.:
	    time.sleep(1. - (time.time() - start_))

