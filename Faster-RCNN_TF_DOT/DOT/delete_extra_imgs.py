import os, operator
import argparse
import time

def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description='Remove extra image files when testing Faster R-CNN on DOT cameras')
    parser.add_argument('--path', dest='path', help='Path to raw images', default='data_dot')
    args = parser.parse_args()
    return args


def DeleteImage(raw_dir):
        name = filter(lambda x: '.jpg' in x, os.listdir(raw_dir))
        name = [raw_dir + '/' + y for y in name]
        time = map(lambda x: os.stat(x).st_mtime, name)
        sortedFiles = dict(zip(name, time))
        sortedFiles = sorted(sortedFiles.items(), key=operator.itemgetter(1))
        return sortedFiles

if __name__ == '__main__':
    args = parse_args()
    running = True

    while running == True:
        try:
            sortedFiles = DeleteImage(args.path)
            # print(sortedFiles[0][0])
            # print(len(sortedFiles))
            if len(sortedFiles) > 18:
                delete = len(sortedFiles) - 18 # Number of images to be 
                for x in range(0, delete):
                    os.remove(sortedFiles[x][0])
                print('deleted')
            else:
                running == False
        except Exception as e:
            print e

        time.sleep(300)