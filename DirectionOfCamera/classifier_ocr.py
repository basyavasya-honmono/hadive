
import os
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from sklearn import datasets, svm, metrics

import cv2


if __name__ == '__main__':
    print 'hi'
    path = raw_input('Enter path to the data')
    path2 = raw_input('Enter path to Images')
    digits = pd.read_csv(path)
    ls = os.listdir(path2)
    

    ls = [x for x in ls if '.png' in x]
    

    a = np.zeros(shape=(len(ls),20,44))
    
    #Threshold all the images
    for i in range(len(ls)):
        img = cv2.imread(ls[i],0)
        #print np.shape(img)
        ret,thresh2 = cv2.threshold(img,200,255,cv2.THRESH_BINARY_INV)
        a[i,:,:] = thresh2

    print np.shape(a)


    digits.target = map(lambda x: int(x),digits.target)
    digits.target = digits['target'].fillna(0)
    images_and_labels = list(zip(a, digits.target))
    #print images_and_labels, np.shape(images_and_labels)
    for index, (image, label) in enumerate(images_and_labels[:7]):
        plt.subplot(2, 7, index + 1)
        plt.axis('off')
        plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
        plt.title('Train: %i' % label)
       

    # # To apply a classifier on this data, we need to flatten the image, to
    # # turn the data in a (samples, feature) matrix:
    n_samples = len(a)
    

    data = np.reshape(a,(n_samples,-1))
    print np.shape(data)

    # Create a classifier: a support vector classifier
    classifier = svm.SVC(gamma=0.01,kernel='poly',degree=5)
    
    # We learn the digits on the first half of the digits
    classifier.fit(data[:n_samples / 5], digits.target[:n_samples / 5])
    

    # Now predict the value of the digit on the second half:
    expected = digits.target[n_samples / 5:]
    predicted = classifier.predict(data[n_samples / 5:])
    
    
    print("Classification report for classifier %s:\n%s\n"
          % (classifier, metrics.classification_report(expected, predicted)))
    print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))

    images_and_predictions = list(zip(a[n_samples / 5:], predicted))
    for index, (image, prediction) in enumerate(images_and_predictions[:7]):
        plt.subplot(2, 7, index + 8)
        plt.axis('off')
        plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
        plt.title('Pred: %i' % prediction)

    plt.show()