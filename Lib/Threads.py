import re as _re
import os as _os
import urllib2 as _urllib2
import threading as _threading

import Link as _Link

class ThreadPool(object):
    """
    Contains and starts threads either based
    on a string representation or Link objects.
    """
    class Worker(_threading.Thread):
        """
        Base class for Worker threads.
        """
        def __init__(self, url, pool):
            super(ThreadPool.Worker, self).__init__()
            self.url  = url
            self.pool = pool

        def download(self):
            """
            Downloads the contents of the url.
            """
            return _urllib2.urlopen(self.url).read()

        def push(self, url):
            """
            Pushes url onto parent pool.
            """
            self.pool.push(url)

        def acquire(self):
            """
            Acquires the semaphore of parent pool.
            """
            self.pool.semaphore.acquire()

        def release(self):
            """
            Releases the semaphore of parent pool.
            """
            self.pool.semaphore.release()

    class BoardWorker(Worker):
        """
        Worker thread that operates on a 4chan board.
        """
        def __init__(self, boardURL, pool):
            super(ThreadPool.BoardWorker, self).__init__(boardURL, pool)

        def run(self):
            content = self.download()

            # Get threads
            threads = set(
                _re.findall(r"(res/\d+)",
                            content)
                )

            for thread in threads:
                self.push(_os.path.join(self.url, thread))

    class ThreadWorker(Worker):
        """
        Worker thread that operates on a 4chan thread.
        """
        def __init__(self, threadURL, pool):
            super(ThreadPool.ThreadWorker, self).__init__(threadURL, pool)

        def run(self):
            content = self.download()

            # Get Images
            images = set(
                _re.findall(r"(http://images\.4chan\.org/\w+/src/\d+\.\w+)",
                            content)
                )

            # Set up Dirs
            if not _os.path.exists(self.url.getDir()):
                _os.makedirs(self.url.getDir())

            for image in images:
                image = _Link.ImageLink(image)
                image.setParent(self.url)
                self.push(image)

    class ImageWorker(Worker):
        """
        Worker thread that operates on a 4chan image.
        """
        def __init__(self, imageURL, pool):
            super(ThreadPool.ImageWorker, self).__init__(imageURL, pool)

        def run(self):
            absPath = self.url.getAbsPath()

            # Don't re-download existing images.
            if _os.path.exists(absPath):
                return

            self.acquire()

            fp = open(absPath, "w")
            fp.write(self.download())
            fp.close()

            self.release()

    def __init__(self, maxThreads):
        super(ThreadPool, self).__init__()
        self.semaphore = _threading.BoundedSemaphore(maxThreads)
        self.spawned   = []

    def start(self, thread):
        """
        Appends a thread to self.spawned and starts it.
        """
        self.spawned.append(thread)
        thread.start()

    def push(self, url):
        """
        Spawns a new thread based on url and starts it.
        """
        link = _Link.classify(url)

        if isinstance(link, _Link.ThreadLink):
            self.start(ThreadPool.ThreadWorker(link, self))
        elif isinstance(link, _Link.BoardLink):
            self.start(ThreadPool.BoardWorker(link, self))
        elif isinstance(link, _Link.ImageLink):
            self.start(ThreadPool.ImageWorker(link, self))

    def join(self):
        """
        Blocks until each spawned thread is finished.
        """
        for thread in self.spawned:
            thread.join()
