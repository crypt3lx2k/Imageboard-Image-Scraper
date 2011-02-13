#! /usr/bin/python

import os
import sys
import time
import glob
import urllib2
import threading

start = time.time()
maxthreads = 16

try:
    urlname = sys.argv[1]
    boardname  = urlname.split("/")[-3]
    threadname = urlname.split("/")[-1]
except:
    print "Usage: %s linktothread" % (sys.argv[0])
    exit(1)

if not os.path.exists(boardname):
    os.mkdir(boardname)
os.chdir(boardname)

if not os.path.exists(threadname):
    os.mkdir(threadname)
os.chdir(threadname)

class DownloadWorker(threading.Thread):
    def __init__(self, url, sema):
        threading.Thread.__init__(self)
        self.url, self.sema  = url, sema

    def run(self):
        self.sema.acquire()
        print "Starting download of %s" % (self.url)

        fp = open(self.url.split("/")[-1], "w")
        up = urllib2.urlopen(self.url)

        fp.write(up.read())

        up.close()
        fp.close()

        self.sema.release()

websema = threading.BoundedSemaphore(maxthreads)
threadp = urllib2.urlopen(urlname)

for line in threadp:
    if not "http://images.4chan.org/" in line:
        continue

    imgurl = line[line.index("http://images.4chan.org/"):].split("\"")[0]
    tempthread = DownloadWorker(imgurl, websema)
    tempthread.start()

for thread in threading.enumerate():
    if thread is not threading.currentThread():
        thread.join()

end = time.time()

bytes = 0
for filename in glob.glob("*"):
    bytes += os.path.getsize(filename)

print "Downloaded: %d bytes in %g seconds: %g bytes per second" % (bytes, float(end - start), float(bytes)/(end-start))
