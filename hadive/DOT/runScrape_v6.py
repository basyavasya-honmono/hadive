'''
Scraps images off NYC DOT cams
'''
# from __future__ import absolute_import, division, print_function
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
import argparse
import json
import pdb
import os, operator
import shutil
import threading
from PIL import Image
from networks.factory import get_network
import string, datetime, time, sys, argparse, os, urllib, urllib3, cStringIO, glob, schedule, uuid
from bs4 import BeautifulSoup
from get_time import get_time
from multiprocessing import Process
import multiprocessing as mp

def Extract(output):
    with open('output_dot/output.csv', 'ab') as f:
        writer = csv.writer(f) 
        writer.writerows(output)
        f.close()
        # print('stored detection')
        output = []
        # Timer(60, Extract(output)).start()

# def DeleteImage():
#         name = filter(lambda x: '.jpg' in x, os.listdir(raw_dir))
#         name = [raw_dir + '/' + y for y in f]
#         time = map(lambda x: os.stat(x).st_mtime, f_)
#         sortedFiles = dict(zip(name, time))
#         sortedFiles = sorted(sortedFiles.items(), key=operator.itemgetter(1))
#         if len(sortedFiles) > 18:
#             delete = len(sortedFiles) - 18 # Number of images to be 
#         for x in range(0, delete):
#             os.remove(sortedFiles[x][0])
#             print('deleted')


CLASSES = ('__background__','pos','neg')

def Detection(graph, _dir, limit):    
    m = 0
    count = 0
    output = []
    # output = [('date','time', 'location', 'count')]
    print('Start detecting')
    start = time.time()
    # t = threading.Timer(60.0, DeleteImage)
    # t.start()
    while m < limit:
        for jj, k in enumerate(graph.keys()):
            node = graph[k]         
            location = node['location']
            url = node['url']
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d-%H-%M-") + str(now.second).zfill(2)
            filename = '%s%s_%s.jpg' % (_dir, timestamp, location)
            try:
                timer = Timer()
                timer.tic()
                # print('Start read')
                # print(url)
                http = urllib3.PoolManager()
                r = http.request('GET', url, preload_content=False)
                im = Image.open(cStringIO.StringIO(r.data)).convert('RGB')
                im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
                # name = get_time(im,filename)
                scores, boxes = im_detect(sess, net, im)
                # except Exception as e:
                #     print(e)
                CONF_THRESH = 0.8
                NMS_THRESH = 0.3
                cls_boxes = boxes[:, 4:8]
                cls_scores = scores[:, 1]
                dets = np.hstack((cls_boxes,
                                  cls_scores[:, np.newaxis])).astype(np.float32)
                keep = nms(dets, NMS_THRESH)
                dets = dets[keep, :]
                count = len(np.where(dets[:, -1] >= CONF_THRESH)[0])                
                timer.toc()
                print ('Detection took {:.3f}s for '
                        '{:d} object proposals').format(timer.total_time, count)
                output.append((timestamp[:10],timestamp[11:19],location,count))
                # name.append(count)
                # output.append(name)
            except Exception as e:
                print(e, url)
                graph.pop(k, None)  
                time.sleep(2)
            end = time.time()
            delta = end - start
            m, s = divmod(delta, 60)
            # t, d = divmod(delta, 120)
        # print(m)
        if m % 2 == 0:
            print('store record')
            Extract(output)
    Extract(output)
    print(('This Node is : ', node))

def Scrape(graph, _dir, limit):    
    m = 0
    count = 0
    output = []
    start = time.time()
    while m < limit:
        for jj, k in enumerate(graph.keys()):
            node = graph[k]         
            location = node['location']
            url = node['url']
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d-%H-%M-") + str(now.second).zfill(2)
            filename = '%s%s_%s.jpg' % (_dir, timestamp, location)
            try:
                http = urllib3.PoolManager()
                with http.request('GET', url, preload_content=False) as r, open(filename, 'wb') as out_file:       
                    shutil.copyfileobj(r, out_file)
                time.sleep(0.1)
            except Exception as e:
                print(e) 
            end = time.time()
            delta = end - start
            m, s = divmod(delta, 60)
    print(('This Node is Done: ', node))

def detect_store(graph, _dir, limit):
    output = []
    d = threading.Thread(target= Detection, args=(graph, _dir, limit))
    s = threading.Thread(target= Scrape, args=(graph, _dir, limit))
    d.start()
    s.start()
    d.join()
    s.join()

def main(args_limit=720):
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
    # links = Links(args_links)
    print('Creating Data Structure')
    # graph = UrlLocation(links)
    with open('cameras.json','r') as f:
        graph = json.load(f)
    print('Scraping Data')
    detect_store(graph, args_s, args_limit)
    print('Done!!!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-limit', dest='limit', type=int, help='the pages to scrap')
    parser.add_argument('-f', dest='f', action='store_true', help='run a one off')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
                        default='VGGnet_test')
    parser.add_argument('--model', dest='model', help='model path',
                        default='model/VGGnet_fast_rcnn_iter_70000.ckpt')
    args = parser.parse_args()

    cfg.TEST.HAS_RPN = True 
# # init session
    # tf.reset_default_graph()
    # tf.get_variable_scope().reuse == True
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
        # schedule.every(2).minutes.do(main)
        schedule.every().day.at("7:30").do(main)
        while True:
            schedule.run_pending()
            time.sleep(1)
