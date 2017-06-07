import os
import random
import argparse

def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description='Create train & test .txt excluding one cam from training.')
    parser.add_argument('--cam', dest='cam', help='unique cam string to pull.')
    parser.add_argument('--path', dest='path', help='path to train & test .txt files.')
    args = parser.parse_args()
    return args

class pullcam(object):
    """Create train.txt and test.txt with one camera exclusively in 
    the test set.
    
    Attributes:
        cam: unique camera string identifier
        data_path: location to original train & test .txt files
        train_count: occurences of cam in training set
    """
    
    def __init__(self, cam, data_path):
        self.cam = cam
        self.data_path = data_path
        self.train_count = None
        self.train = data_path + 'train.txt'
        self.test = data_path + 'test.txt'
        self.train_out = data_path + 'train_' + self.cam + '.txt'
        self.test_out = data_path+ 'test_' + self.cam + '.txt'

    
    def pull_from_train(self):
        '''Iterate through train.txt, write lines excluding 'cam' to 
        new file and count lines including 'cam'.
        '''
        
        self.train_count = 0
        with open(self.train, 'r') as train_in, open(self.train_out, 'w') as train_out_, open(self.test_out, 'w') as test_out_:
            for line in train_in:
                if self.cam in line:
                    self.train_count += 1
                    test_out_.write(line)
                else:
                    train_out_.write(line)
    
    def replace_from_test(self):
        '''Iterate through test.txt, append necessary # of lines to 
        new train .txt file, append others to new test .txt file'''
        
        replacements = list()
        with open(self.test, 'r') as test_in, open(self.test_out, 'a') as test_out_:
            for line in test_in:
                if self.cam not in line:
                    if len(replacements) < self.train_count:
                        replacements.append(line)
                    else:
                        test_out_.write(line)
                else:
                    test_out_.write(line)
                    
        with open(self.train_out, 'a') as train_out_:
            for line in replacements:
                train_out_.write(line)
    
    def shuffle_files(self):
        '''Shuffle order of new train and test .txt files.'''
	os.system('shuf {0} -o {0}'.format(self.train_out))
        os.system('shuf {0} -o {0}'.format(self.test_out))

if __name__ == '__main__':
    args = parse_args()
    
    run = pullcam(args.cam, args.path)
    run.pull_from_train()
    run.replace_from_test()
    run.shuffle_files()

