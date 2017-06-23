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
 
 #   det_work = 0
 #   errors = 0
 
    with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
        with conn.cursor() as cursor:
            for iter_ in range(int(args.duration)):
                save = randint(0, len(cams))
                for _, cam in enumerate(cams):
                    message = []
                    start_im = time.time()
                    try:
                        im = get_im(cam[1])
                        end_im = time.time() - start_im
                    except:
                        im = None
                        message.append("Error at dl")
                        end_im = time.time() - start_im

                    start_det = time.time()
                    try:
                        details = get_time(im, 'test')
                        end_det = time.time() - start_det
                    except:
                        details = ['error', 'error', 'error']
                        message.append("Error at details")
                        end_det = time.time() - start_det
                    
                    start_count = time.time()
                    try:
                        count = detect(sess, net, im, float(args.conf))
                        end_count = time.time() - start_count
                    except:
                        count = 0
                        message.append("Error at count")
                        end_count = time.time() - start_count

                    print '{}, {}, {}, {}'.format(cam[0], details[0], details[2], count)
                    
                    sql = """INSERT INTO ped_count VALUES ({}, '{}', '{}', {})
                    """.format(cam[0], details[0], details[2], count)

                    cursor.execute(sql)
                    
                    if _ == save:
                        cv2.imwrite("/home/jmv423/DOT_Faster-RCNN_TF/tools/Images/{}_{}.jpg".format(cam[0], int(time.time())), im) 

#                    end = time.time() - start_im
#                    print 'dl {},det {},count {}, tot {}'.format(end_im, end_det, end_count, end)
#                    print '{}, {}, {}, {}'.format(cam[0], details[0], details[2], count)
#                    if message != []:
#                        errors +=1
#                    try:
#                        if details[2] in ['N', 'S', 'E', 'W']:
#                            det_work += 1
#                    except:
#                        pass
#    print 1.0 * det_work / len(cams)
#    print 1.0 * errors / len(cams)   
