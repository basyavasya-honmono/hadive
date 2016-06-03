from selenium import webdriver
import time
from bs4 import BeautifulSoup
from PIL import Image
import pylab as pl
import urllib, cStringIO
from urllib import urlretrieve
import numpy as np
import timeit
from Queue import Queue
from threading import Thread

# Using PhantomJS 'headless browser' to parse JS rendered images on a few dotfeeds
# Note this was required only in Python2.7 and for some dotFeed stations
# Create an object that will get the content from a specific url
driver = webdriver.PhantomJS("/home/cusp/pnk230/phantom/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
driver.get("http://207.251.86.238/cctv261.jpg?rand=0.993656320748411") 
time.sleep(3)
html = driver.page_source
# Specify parser - "lxml"
soup = BeautifulSoup(html,"lxml")

URL1 = [x['src'] for x in soup.find_all("img")]

URL = URL1[0]
print 'started'

i = 0
def save_image(q,i):
'''
Saving images as a separate thread to avoid delays in the scraping time
'''
try:
    while True:
            i = i+1
            imges = q.get()
            imges.save(str(i)+'.jpg')
            q.task_done()

except:
    imges.convert('RGB').save(str(i)+'.jpg')
    q.task_done()
    pass




if __name__ == '__main__':

    '''
    Implementing multithreading for scraping and saving the scraped images
    Queue will store incoming objects and simultanouesly save as they come without 
    Interfering the workflow of the scraper - hence scraping and saving become independent of each other
    '''
    
    q = Queue(maxsize=0) # maxsize = 0 means infinte or not specified how long is needed

    # As scraping is the process from where output is to be processed (saved) - 
    # one thread can achieve that (the saving bit)
    # You can specify more than one thread but not recommended as we want the saving in order, more than one
    # thread runnning simultaneously for saving of the scraped images will not result in understandable order
    num_threads = 1

    for i in range(num_threads):
            # Initialize thread object to go to save_image function

            worker = Thread(target=save_image, args=(q,i))
            # Set the thread to daemon for exiting when the scripts ends/exits
            worker.setDaemon(True)
            worker.start()

    while(True):
            try:
                
                file1 = cStringIO.StringIO(urllib.urlopen(URL).read())

                # Add the object in q object - it will keep saving at its own pace
                q.put(Image.open(file1))



            except:
                # Too fast pinging the dot camera might result in server timeout
                # In that case sleep for 5 seconds

                time.sleep(5)
                pass
