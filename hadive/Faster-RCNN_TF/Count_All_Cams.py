import os
import sys
import cv2
import time
import string
import urllib
import datetime
import argparse
import psycopg2
import _init_paths
import numpy as np
import tensorflow as tf
from bs4 import BeautifulSoup
from utils.timer import Timer
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from networks.factory import get_network

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Count pos examples of people in DOT images')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]', default='VGGnet_test')
    parser.add_argument('--model', dest='model', help='Model path', default=' ')
    parser.add_argument('--duration', dest='duration', help='duration to count peds (secs)')
    args = parser.parse_args()
    return args

def get_cctv_links():
    with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT cam_id, cctv_id FROM cameras""")
            cams = filter(lambda x: x[1].isdigit(), cursor.fetchall())
    return map(lambda x: (x[0], 'http://207.251.86.238/cctv{}.jpg'.format(x[1])), cams)

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

if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    args = parse_args()

    # Start tensorflow
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))          # init session
    net = get_network(args.demo_net)                                             # load network
    saver = tf.train.Saver(write_version=tf.train.SaverDef.V2)                   # load model
    saver.restore(sess, args.model)
    print '\n\nLoaded network {:s}'.format(args.model)

    cams = get_cctv_links()
        
    start = time.time()
    for _ in range(int(args.duration)):
        for cam in cams:
            filename = str(cam[0]) + '.jpg'
            im_path = os.path.join(cfg.DATA_DIR, 'DOTimages', filename)
            try:
                urllib.urlretrieve(cam[1], im_path)
                time_ = datetime.datetime.now()
                count = demo(sess, net, filename)
                os.remove(im_path)
                print '{},{},{}'.format(cam[0], time_, count)
            except:
                pass
    #print time.time() - start
