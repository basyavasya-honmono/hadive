import cv2
import urllib3
import argparse
import cStringIO
import numpy as np
from PIL import Image
from get_time import get_time

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Fix get_time.py')
    parser.add_argument('--cctv', dest='cctv', help='cctv id', default=1)
    parser.add_argument('--all', dest='all', help='check all cams', default='N')
    return parser.parse_args()

def get_im(url):
    """Get image from DOT camera"""
    http = urllib3.PoolManager()
    r = http.request('GET', url, preload_content=False)
    im = Image.open(cStringIO.StringIO(r.data)).convert('RGB')
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

if __name__ == '__main__':
    args = parse_args()

    url = 'http://207.251.86.238/cctv{}.jpg'.format(args.cctv)
    im = get_im(url)
    direction, time_ = get_time(im)
    print 'Direction: {}, Time: {}'.format(direction, time_)
    Image.fromarray(im).show()
    
    if args.all == 'Y':
        working = 0
        no_ribbon = 0
        down = 0
        for i in range(2000):
            try:
                url = 'http://207.251.86.238/cctv{}.jpg'.format(i)
                im = get_im(url)
                direction, time_ = get_time(im)
                if time_ == 'Cam not in Service':
                    down += 1
                if time_ == 'No Info Ribbon':
                    no_ribbon += 1
                if direction in ['N', 'S', 'E', 'W']:
                    working += 1
            except:
                pass
        print 'Working {}, No Ribbon {}, Down {}'.format(working, no_ribbon, down)
