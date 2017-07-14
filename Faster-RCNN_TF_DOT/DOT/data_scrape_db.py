'''
Detect human off NYC DOT cams
'''
import _init_paths
import tensorflow as tf
import networks.VGGnet_test
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import csv, cv2
import psycopg2
import argparse
import json
import pdb
import os, operator
import shutil
from PIL import Image
from networks.factory import get_network
from get_time import get_time
import string, datetime, time, sys, os, urllib3, cStringIO, glob, schedule, uuid
from bs4 import BeautifulSoup

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-limit', dest='limit', type=int, help='the pages to scrap')
    parser.add_argument('-f', dest='f', action='store_true', help='run a one off')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
                        default='VGGnet_test')
    parser.add_argument('--model', dest='model', help='model path',
                        default='model/VGGnet_fast_rcnn_iter_90000.ckpt')
    args = parser.parse_args()
    return args

def get_cctv_links():
    with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT cam_id, cctv_id FROM cameras""")
            cams = filter(lambda x: x[1].isdigit(), cursor.fetchall())
    return map(lambda x: (x[0], 'http://207.251.86.238/cctv{}.jpg'.format(x[1])), cams)

CLASSES = ('__background__','pos','neg')

def get_count(_dir, url, sess, net, CONF_THRESH = 0.8, NMS_THRESH = 0.3):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:") + str(now.second).zfill(2)  
    http = urllib3.PoolManager()
    r = http.request('GET', url, preload_content=False)
    try:
        im = Image.open(cStringIO.StringIO(r.data)).convert('RGB')
        im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    except Exception as e:
        return now, 0, 'error'
    direction = get_time(im)        
    if direction in ['gray_im', 'black_im', 'rainbow_im']:
        return now, 0, 'no_im'      
    filename = '%s%s_%s.jpg' % (_dir, timestamp, url[26:-4])
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(r, out_file)
        out_file.close()
    scores, boxes = im_detect(sess, net, im)
    cls_boxes = boxes[:, 4:8]
    cls_scores = scores[:, 1]
    dets = np.hstack((cls_boxes,
                      cls_scores[:, np.newaxis])).astype(np.float32)
    keep = nms(dets, NMS_THRESH)
    dets = dets[keep, :]
    count = len(np.where(dets[:, -1] >= CONF_THRESH)[0])
    return now, count, direction        

def scrape_detect(cams, _dir, limit):    
    m = 0
    count = 0
    output = []
    print('Start detecting')
    start = time.time()
    conn = psycopg2.connect("dbname='dot_pedestrian_counts'")
    cursor = conn.cursor()
    while m < limit:
        for k, cam in enumerate(cams):         
            location_id = cam[0]
            url = cam[1]
            try:
                timestamp, count, direction = get_count(_dir, url ,sess, net)
            except Exception as e:
                print(e)
                continue
            sql = """INSERT INTO pedestrians VALUES ('{}', {}, {}, '{}','{}')
                  """.format(timestamp, location_id, count, direction, url[26:-4])
                        #to_date('{}', '%Y-%m-%d %H:%M:')
            try:    
                cursor.execute(sql)
                conn.commit()  
                print('save im')
            except Exception as e:
                print e.message
                try:
                    cursor.close()
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    conn.commit() 
                except:
                    conn.close()
                    conn = psycopg2.connect("dbname='dot_pedestrian_counts'")
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    conn.commit() 
        end = time.time()
        delta = end - start
        m, s = divmod(delta, 60)
        print('min: %i' %m)
    print('Done detecting')
    cursor.close()
    conn.close()

def main(args_limit=900):
    args_links='links.txt'
    output_dir = 'output_dot'
    if not os.path.exists(output_dir):
        print('Making New Directory: %s' % (output_dir))
        os.makedirs(output_dir)
    raw_dir = 'images_dot'
    if not os.path.exists(raw_dir):
        print('Making New Directory: %s' % (raw_dir))
        os.makedirs(raw_dir)
    args_s = raw_dir + '/'
    cams = get_cctv_links()
    print('Scrape Data')
    scrape_detect(cams, args_s, args_limit)
    print('Done!!!')


if __name__ == '__main__':
    args = parse_args()

    cfg.TEST.HAS_RPN = True 
    # init session
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
    # load network
    net = get_network(args.demo_net)
    # load model
    saver = tf.train.Saver(write_version=tf.train.SaverDef.V1)
    saver.restore(sess, args.model) 
    # Warmup on a dummy image
    im = 128 * np.ones((300, 300, 3), dtype=np.uint8)
    for i in xrange(2):
        _, _ = im_detect(sess, net, im)

    if args.f:
        print('Starting one off')
        main(args_limit=args.limit)
    else:
        print('Starting the daily thing')
        schedule.every().day.at("7:00").do(main)
        while True:
            schedule.run_pending()
            time.sleep(1)
