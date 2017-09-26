import os
import cv2
import time
import json
import urllib3
import sqlite3
import argparse
import cStringIO
import _init_paths
import numpy as np
import tensorflow as tf
from PIL import Image
from random import randint
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
    parser.add_argument('--folder', dest='folder', help='Folde containing ims', default=' ')
    parser.add_argument('--conf', dest='conf', help='Confidence limit for detecting pedestrians', default='0.8')
    args = parser.parse_args()
    return args


def detect(sess, net, im_file_path, conf):
    """Detect object classes in an image"""
    CLASSES = ('__background__', 'pos', 'neg')

    im = cv2.imread(im_file_path)
    scores, boxes = im_detect(sess, net, im)

    for cls_ind, cls in enumerate(CLASSES[1:]):
        if cls == 'pos':
            cls_ind += 1 # because we skipped background
            cls_boxes = boxes[:, 4 * cls_ind: 4 * (cls_ind + 1)]
            cls_scores = scores[:, cls_ind]
            dets = np.hstack((cls_boxes, cls_scores[:, np.newaxis])).astype(np.float32)
            keep = nms(dets, 0.3) # NMS_THRESH
            dets = dets[keep, :]
            dets = filter(lambda x: x[-1] >= float(conf), dets)
            return dets

if __name__ == '__main__':
    args = parse_args()

    # Start TensorFlow
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))          # init session
    net = get_network(args.demo_net)                                             # load network
    saver = tf.train.Saver(write_version=tf.train.SaverDef.V2)                   # load model
    saver.restore(sess, args.model)

    demo_path = os.path.join("..", "data", "demo", args.folder)
    demo_ims = filter(lambda x: x.endswith(".jpg"), os.listdir(demo_path))

    data = {}
    for im_file in demo_ims:
        try:
            im_file_path = os.path.join(demo_path, im_file)
            dets = detect(sess, net, im_file_path, args.conf)
            print im_file, len(dets)
            data[im_file] = {"count": len(dets), "bboxes": [x.tolist() for x in dets]}
        except:
            pass

    with open("detections.json", "w") as f:
        json.dump(data, f)
