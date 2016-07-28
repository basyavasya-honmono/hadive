'''
Scraps images off NYC DOT cams
'''

import string, datetime, time, sys, argparse, os, urllib, cStringIO, glob, schedule, uuid
from bs4 import BeautifulSoup
from get_time import get_time
from multiprocessing import Process


def Links(filename):
    links = []
    with open(filename) as f:
        for row in f:
            links.append(row)
    return links


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


def ScrapeImage(node, _dir, limit):
    if _dir[-1] != '/':
        _dir+='/'
    m=0
    start = time.time()
    while m < limit:
        location = node['location']
        url = node['url']
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H-%M-") + str(now.second).zfill(2)
        filename = '%s_%s.jpg' % (timestamp, location)
        # filename = '%s_%s.jpg' % (location, timestamp)
        try:
            urllib.urlretrieve(url, _dir+filename)
            time.sleep(1)
        except:
            print 'Error Thrown:', node['location']
            time.sleep(10)
        end = time.time()
        delta = end - start
        m, s = divmod(delta, 60)
    print 'This Node is Done: ', node


def callImage(graph, _dir, limit):
    threads = {}
    for jj, k in enumerate(graph.keys()):
        node = graph[k]
        p = Process(target=ScrapeImage, args=(node, _dir, limit,))
        threads[k]=p
        p.start()
    for k, v in threads.items():
        v.join()


def newFileName(_dir, _dir_new):
    paths = glob.glob(_dir+'*')
    for i, im in enumerate(paths):
        new_name = get_time(im)[:-19] + '.jpg'
        os_path = os.path.join(os.path.dirname(_dir_new), new_name)
        os.rename(im, os_path) 
        print "File: %d, old name: %s, new name: %s" % (i, im, os_path) 


def main(args_limit=720):
    # -- point to a text file with the webcam urls
    args_links='links.txt'
    # -- point to the number of minutes to run the scraper
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d")
    raw_dir = '%s_raw_images' % timestamp
    clean_dir = '%s_clean_images' % timestamp
    if os.path.exists(raw_dir):
        uniq = str(uuid.uuid4())
        raw_dir = '%s_%s' % (raw_dir, uniq)
        clean_dir = '%s_%s' % (clean_dir, uniq)
    print 'Making New Directory: %s' % (raw_dir)
    os.makedirs(raw_dir)
    #os.makedirs(clean_dir)
    args_s = raw_dir+'/'
    args_new_dir = clean_dir+'/'
    print 'Parsing Links'
    links = Links(args_links)
    print 'Creating Data Structure'
    graph = UrlLocation(links)
    print 'Scraping Data'
    callImage(graph, args_s, args_limit)
    # print 'Updating File Names'
    # newFileName(args_s, args_new_dir)
    print 'Done!!!'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('-links', dest='links', help='file with links')
    parser.add_argument('-limit', dest='limit', type=int, help='the pages to scrap')
    # parser.add_argument('--feature', dest='feature', action='store_true')
    parser.add_argument('-f', dest='f', action='store_true', help='run a one off')
    args = parser.parse_args()
    # main(args.links, args.limit)

    print 'Starting'
    if args.f:
        print 'Starting one off'
        main(args_limit=args.limit)
    else:
        print 'Starting the daily thing'
        # schedule.every(2).minutes.do(main)
        schedule.every().day.at("7:30").do(main)
        while True:
            schedule.run_pending()
            time.sleep(1)

