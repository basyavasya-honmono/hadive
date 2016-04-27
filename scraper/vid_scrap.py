'''
Scraps images off NYC DOT cams
'''

import string, datetime, time, sys, argparse
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve


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
        if len(i.strip()) == 0:
            continue
        target = 'document.getElementById(currentImage).src = '
        jpg = 'jpg'
        obj = urlopen(i.strip())
        html = obj.read()
        soup = BeautifulSoup(html, "lxml")
        # print(soup.prettify())
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
            print('There was no webcam link for url: %s' % i)
    return webcams


def ScrapeImage(graph, _dir='./', limit=60, records='records.txt'):
    if _dir[-1] != '/':
        _dir+='/'
    m=0
    records = open(_dir+records, 'w')
    start = time.time()
    while m < limit:
        for address in graph.keys():
            node = graph[address]
            location = node['location']
            url = node['url']
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d-%H-%M-") + str(now.second).zfill(2)
            filename = '%s_%s.jpg' % (timestamp, location)
            records.write('%s\t%s\t%s\t%s' % (address, url, location, filename))
            #print(address)
            if type(url) != str:
                continue
            #print(type(url), type(_dir+filename))
            try:
                urlretrieve(url, _dir+filename)
            except:
                print('\nError Thrown\n')
                time.sleep(60)
            time.sleep(1)
            #print(address)
        end = time.time()
        delta = end - start
        m, s = divmod(delta, 60)
        sys.stdout.write('\rtime running %s minutes' % str(m))
        sys.stdout.flush()

    records.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-links', dest='links', help='file with links')
    parser.add_argument('-limit', dest='limit', type=int, help='the pages to scrap')
    parser.add_argument('-s', dest='s', help='directory where the file goes')
    parser.add_argument('-r', dest='r', help='file name for the record text')
    args = parser.parse_args()
    links = Links(args.links)
    #print(links)
    graph = UrlLocation(links)
    #print(graph)
    ScrapeImage(graph, _dir=args.s, limit=args.limit, records=args.r)
    print('\nDONE!!!')

