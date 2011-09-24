#! /usr/bin/env python

import re
import threading
import urllib2

import sys
import os
import time

maxthreads = 32
downloadedFiles = []

def usage():
    print """Usage: %s linktothread""" % (sys.argv[0])
    exit(1)

try:
    url = sys.argv[1]

    boardname, threadname = \
        re.search(r"http://boards\.4chan\.org/(\w+)/res/(\d+)",
                  url).groups()
except AttributeError as e:
    print "%s is not a valid 4chan thread url!" % (url)
    usage()
except:
    usage()

if not os.path.exists(boardname):
    os.mkdir(boardname)
os.chdir(boardname)

if not os.path.exists(threadname):
    os.mkdir(threadname)
os.chdir(threadname)

class DownloadWorker(threading.Thread):
    def __init__(self, url, sema):
        super(DownloadWorker, self).__init__()
        self.url, self.sema  = url, sema

    def run(self):
        filename, = \
            re.search(r"http://images\.4chan\.org/\w+/src/(\d+\.\w+)",
                      self.url).groups()

        if os.path.exists(filename):
            return

        sys.stdout.write("Starting download of %s\n" % (self.url))
        
        self.sema.acquire()

        fp = open(filename, "w")
        up = urllib2.urlopen(self.url)
        fp.write(up.read())

        self.sema.release()

        up.close()
        fp.close()

        downloadedFiles.append(filename)

websema = threading.BoundedSemaphore(maxthreads)
thread  = urllib2.urlopen(url)
imageurls = \
    set(re.findall(r"(http://images\.4chan\.org/\w+/src/\d+\.\w+)",
                   thread.read()))

start = time.time()

for imageurl in imageurls:
    tempthread = DownloadWorker(imageurl, websema)
    tempthread.start()

for thread in threading.enumerate():
    if thread is not threading.currentThread():
        thread.join()

end = time.time()

if downloadedFiles:
    bytes = 0
    for filename in downloadedFiles:
        bytes += os.path.getsize(filename)

    print "Downloaded: %d bytes in %g seconds: %g bytes per second" % (bytes, float(end - start), float(bytes)/(end-start))
