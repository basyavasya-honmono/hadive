import cv2
import time
import urllib3
import argparse
import psycopg2
import cStringIO
import _init_paths
import numpy as np
import tensorflow as tf
from PIL import Image
from random import randint
from get_time import get_time
from utils.timer import Timer
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from networks.factory import get_network

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Count pos examples of people in DOT images')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]', default='VGGnet_test')
    parser.add_argument('--model', dest='model', help='Path to .ckpt', default=' ')
    parser.add_argument('--duration', dest='duration', help='Number of loops to detect pedestrians')
    parser.add_argument('--conf', dest='conf', help='Confidence limit for detecting pedestrians', default='0.8')
    args = parser.parse_args()
    return args

def get_cctv_links():
    """Return all cam_id and cctv url for all values in cameras db table"""
    with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT cam_id, cctv_id FROM cameras""")
            cams = filter(lambda x: x[1].isdigit(), cursor.fetchall())
    return map(lambda x: (x[0], 'http://207.251.86.238/cctv{}.jpg'.format(x[1])), cams)

def get_im(url):
    """Get image from DOT camera"""
    http = urllib3.PoolManager()
    r = http.request('GET', url, preload_content=False)
    im = Image.open(cStringIO.StringIO(r.data)).convert('RGB')
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

def detect(sess, net, im, conf):
    """Detect object classes in an image"""
    CLASSES = ('__background__', 'pos', 'neg')
    scores, boxes = im_detect(sess, net, im)

    for cls_ind, cls in enumerate(CLASSES[1:]):
        if cls == 'pos':
            cls_ind += 1 # because we skipped background
            cls_boxes = boxes[:, 4 * cls_ind: 4 * (cls_ind + 1)]
            cls_scores = scores[:, cls_ind]
            dets = np.hstack((cls_boxes, cls_scores[:, np.newaxis])).astype(np.float32)
            keep = nms(dets, 0.3) # NMS_THRESH
            dets = dets[keep, :]
            dets = np.where(dets[:, -1] >= conf)[0] # conf thresh
            return len(dets)

if __name__ == '__main__':
    args = parse_args()

    # Start TensorFlow
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))          # init session
    net = get_network(args.demo_net)                                             # load network
    saver = tf.train.Saver(write_version=tf.train.SaverDef.V2)                   # load model
    saver.restore(sess, args.model)

    cams = get_cctv_links()
    with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
        with conn.cursor() as cursor:
            for iter_ in range(int(args.duration)):
                save = randint(0, len(cams))
                for _, cam in enumerate(cams):
                    # Download image, & get time when url is pinged.
                    try:
                        im_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        im = get_im(cam[1])
                    except:
                        im = None
                        pass
                    
                    # Pull camera direction if availabe (needs to be improved and pull time).
                    try:
                        details = get_time(im)
                    except:
                        details = 'NA'
                    
                    # Count pedestrians in image.
                    try:
                        count = detect(sess, net, im, float(args.conf))
                    except:
                        count = 0
                        im_time = 'Error'
                        pass
                    
                    # Put data in database
                    cursor.execute(
                    """INSERT INTO ped_count (cam_id, date, cam_dir, count) VALUES (%s, %s, %s, %s);""",
                    (cam[0], im_time, details, count))
                    conn.commit()
#                    print '{}, {}, {}, {}'.format(cam[0], im_time, details, count)
                    
                    # Randomly save images.
                    if _ == save:
                        cv2.imwrite("/home/jmv423/DOT_Faster-RCNN_TF/tools/Images/{}_{}.jpg".format(cam[0], int(time.time())), im)

