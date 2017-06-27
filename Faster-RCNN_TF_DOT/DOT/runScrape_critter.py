'''
Scraps images off NYC DOT cams
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
import threading
from PIL import Image
from networks.factory import get_network
from get_time import get_time
import string, datetime, time, sys, argparse, os, urllib, urllib3, cStringIO, glob, schedule, uuid
from bs4 import BeautifulSoup
from multiprocessing import Process
import multiprocessing as mp

def Extract(output):
    with open('output_dot/output.csv', 'ab') as f:
        writer = csv.writer(f) 
        writer.writerows(output)
        f.close()
        output = []

def get_cctv_links():
    with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT cam_id, cctv_id FROM cameras""")
            cams = filter(lambda x: x[1].isdigit(), cursor.fetchall())
    return map(lambda x: (x[0], 'http://207.251.86.238/cctv{}.jpg'.format(x[1])), cams)

CLASSES = ('__background__','pos','neg')

def check_cams(cams):
    timer = Timer()
    timer.tic()
    no_img = []
    black_img = []
    gray_img = []
    rainbow_img = []
    n = 0
    while n < 3:
        n += 1 
        for k, cam in enumerate(cams):         
            location_id = cam[0]
            url = cam[1]
            try:
                http = urllib3.PoolManager()
                r = http.request('GET', url, preload_content=False)
                im = Image.open(cStringIO.StringIO(r.data)).convert('RGB')
                im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
                direction = get_time(im)
                if direction == 'black_im':
                    if url[-7:-4] not in black_img:
                        black_img.append(url[-7:-4])
                        cams.pop(k)
                        continue
                if direction == 'gray_im':
                    if url[-7:-4] not in gray_img:
                        gray_img.append(url[-7:-4])
                        cams.pop(k)
                        continue
                if direction == 'rainbow_im':
                    if url[-7:-4] not in rainbow_img:
                        rainbow_img.append(url[-7:-4])
                        cams.pop(k)
                        continue
            except IOError as e:
                if url[-7:-4] not in no_img:
                    no_img.append(url[-7:-4])
                    cams.pop(k)
            time.sleep(2)
    timer.toc()
    print('left:%i, others: %i, %i, %i, %i'%(len(cams),len(no_img),len(black_img),\
          len(gray_img), len(rainbow_img)))
    print(timer.total_time)
    print(no_img)
    print(black_img)
    print(gray_img)
    print(rainbow_img)
   

def Detection(cams, _dir, limit):    
    m = 0
    count = 0
    output = []
    print('Start detecting')
    start = time.time()
    with psycopg2.connect("dbname='dot_pedestrian_counts'") as conn:
        with conn.cursor() as cursor:
            while m < limit:
                for k, cam in enumerate(cams):         
                    location_id = cam[0]
                    url = cam[1]
                    now = datetime.datetime.now()
                    timestamp = now.strftime("%Y-%m-%d %H:%M:") + str(now.second).zfill(2)
                    try:
                        timer = Timer()
                        timer.tic()
                        http = urllib3.PoolManager()
                        r = http.request('GET', url, preload_content=False)
                        im = Image.open(cStringIO.StringIO(r.data)).convert('RGB')
                        im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
                        direction = get_time(im)
                        scores, boxes = im_detect(sess, net, im)
                        CONF_THRESH = 0.8
                        NMS_THRESH = 0.3
                        cls_boxes = boxes[:, 4:8]
                        cls_scores = scores[:, 1]
                        dets = np.hstack((cls_boxes,
                                  cls_scores[:, np.newaxis])).astype(np.float32)
                        keep = nms(dets, NMS_THRESH)
                        dets = dets[keep, :]
                        count = len(np.where(dets[:, -1] >= CONF_THRESH)[0])                
                        # timer.toc()
                        # print ('Detection took {:.3f}s for '
                        # '{:d} object proposals').format(timer.total_time, count)
                        output.append((timestamp,location_id, url[-7:-4], direction, count))
                        sql = """INSERT INTO pedestrian_count VALUES ('{}', {}, {}, '{}','{}')
                              """.format(timestamp, location_id, count, direction, url[26:-4])
                        cursor.execute(sql)
                    except IOError as e:
                        print(e, url)
                        cams.pop(k)  
                    except Exception as e:
                        print(e, url)
                        continue
                    end = time.time()
                    delta = end - start
                    m, s = divmod(delta, 60)
                # print(len(cams))
            # if m % 2 == 0:
            #     print('store record')
            #     Extract(output)
    # Extract(output)
            print('Done detecting')

def Scrape(cams, _dir, limit):    
    m = 0
    count = 0
    output = []
    start = time.time()
    while m < limit:
        for k, cam in enumerate(cams):         
            location_id = cam[0]
            url = cam[1]
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d-%H-%M-") + str(now.second).zfill(2)
            filename = '%s%s_%s.jpg' % (_dir, timestamp, location_id)
            try:
                http = urllib3.PoolManager()
                with http.request('GET', url, preload_content=False) as r, open(filename, 'wb') as out_file:       
                    shutil.copyfileobj(r, out_file)
            except Exception as e:
                print(e) 
            end = time.time()
            delta = end - start
            m, s = divmod(delta, 60)
            time.sleep(1)
    print('Done scraping')

def detect_scrape(cams, _dir, limit):
    output = []
    d = threading.Thread(target= Detection, args=(cams, _dir, limit))
    s = threading.Thread(target= Scrape, args=(cams, _dir, limit))
    d.start()
    s.start()
    d.join()
    s.join()

def main(args_limit=900):
    args_links='links.txt'
    output_dir = 'output_dot'
    if not os.path.exists(output_dir):
        print('Making New Directory: %s' % (output_dir))
        os.makedirs(output_dir)
    raw_dir = 'data_dot'
    if not os.path.exists(raw_dir):
        print('Making New Directory: %s' % (raw_dir))
        os.makedirs(raw_dir)
    args_s = raw_dir + '/'
    print('Parsing Links')
    print('Creating Data Structure')
    cams = get_cctv_links()
    check_cams(cams)
    print('Scraping Data')
    detect_scrape(cams, args_s, args_limit)
    print('Done!!!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-limit', dest='limit', type=int, help='the pages to scrap')
    parser.add_argument('-f', dest='f', action='store_true', help='run a one off')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
                        default='VGGnet_test')
    parser.add_argument('--model', dest='model', help='model path',
                        default='model/VGGnet_fast_rcnn_iter_90000.ckpt')
    args = parser.parse_args()

    cfg.TEST.HAS_RPN = True 
# # init session
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

    print('Starting')
    if args.f:
        print('Starting one off')
        main(args_limit=args.limit)
    else:
        print('Starting the daily thing')
        schedule.every().day.at("8:00").do(main)
        while True:
            schedule.run_pending()
            time.sleep(1)
