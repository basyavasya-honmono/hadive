import os
import glob
import time
import argparse

def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description='Remove extra .ckpt file when training Faster R-CNN')
    parser.add_argument('--path', dest='path', help='Output path of ckpts')
    parser.add_argument('--iters', dest='iters', help='Num of training iters')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    running = True

    while running == True:
        try:
	    f = filter(lambda x: '.ckpt' in x, os.listdir(args.path))
            num = str(sorted(map(lambda x: int(filter(str.isdigit, x)), f))[0]) + '.'
        
            if len(f) > 4:
                for ckpt in f:
                    if num in ckpt:
                        os.remove(os.path.join(args.path, ckpt))

            for ckpt in f:
                if args.iters in f:
                    running = False
	except:
		pass

        time.sleep(60)
