import re as _re
import os as _os
import sys as _sys
import urllib2 as _urllib2
import threading as _threading

import Link as _Link
import Globals as _Globals
import StaticFiles as _StaticFiles

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
            while True:
                try:
                    return _urllib2.urlopen(self.url).read()
                except _urllib2.HTTPError as e:
                    if self.url in _Globals.globals.links:
                        print >> _sys.stderr, "Recieved `%s' while trying to read link %s, removing it from links." % (
                            e, self.url
                            )

                        _Globals.globals.links.remove(self.url)
                    return ""
                except _urllib2.URLError as e:
                    continue

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
                _re.findall(r"(thread/\d+)",
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

            # Set up Dirs
            if not _os.path.exists(self.url.getDir()):
                _os.makedirs(self.url.getDir())

            if _Globals.globals.save_page:
                if not _os.path.exists(self.url.getStaticDir()):
                    _os.makedirs(self.url.getStaticDir())

            # Get Images
            if _Globals.globals.keep_names:
                images = {}

                pairs = _re.findall(r"<a (?:title=\"([^\"]*?)\" )?href=\"(//i\.4cdn\.org/\w+/\d+\.\w+).*?\>(.*?)\<\/a>", content)

                image_names = []

                for val1, key, val2 in pairs:
                    if val1:
                        value = val1

                        if val1 in image_names:
                            value = key.split('/')[-1]  # no overlapping image names
                    elif val2:
                        value = val2

                        if val2 == 'Spoiler Image' or val2 in image_names:
                            value = key.split('/')[-1]  # spoiler image or overlapping image name

                    image_names.append(value)

                    images[key] = value
            else:
                images = set(
                    _re.findall(r"(//i\.4cdn\.org/\w+/\d+\.\w+)",
                                content)
                    )

            for image in images:
                link = _Link.ImageLink('https:' + image)
                link.setThread(self.url)

                if _Globals.globals.keep_names:
                    link.name = images[image]

                self.push(link)

            # Save page HTML
            if _Globals.globals.save_page and content:  # don't save page html if 404 (thread deleted)
                converted_content = content  # have to change all the links below

                # replacing image URLs
                for original_image_url in images:
                    if _Globals.globals.keep_names:
                        new_name = images[original_image_url]
                    else:
                        link = _Link.ImageLink('https:' + original_image_url)
                        new_name = link.getName()

                    converted_content = converted_content.replace(original_image_url, new_name)

                # replacing thumbnail urls
                thumbnail_list = set(_re.findall(r"\<img src=\"(//[0-9]+\.t\.4cdn\.org/\w+/([0-9]+)s\.jpg)\"", content))

                for url, image_number in thumbnail_list:
                    new_image_filename = None

                    # discover which image it is we're looking for
                    for image_url in images:
                        if image_number in image_url:
                            if _Globals.globals.keep_names:
                                new_image_filename = images[image_url]
                            else:
                                link = _Link.ImageLink('https:' + image_url)
                                new_image_filename = link.getName()

                    if new_image_filename is None:
                        print 'image filename not discovered for thumbnail:', image_number, url  # shouldn't happen
                        continue

                    converted_content = converted_content.replace(url, new_image_filename)

                # downloading static files, and replacing filenames
                static = _StaticFiles.StaticFileHandler()
                for url in static.extract_static_urls(content):
                    static.download(url, self.url.getStaticDir())
                    new_filename = _os.path.join('static', url.lstrip('/'))
                    # we don't wanna load the js, doesn't add much and hits 4ch servers when we load the page
                    if url.endswith('.js'):
                        new_filename += '.dontload'
                    converted_content = converted_content.replace(url, new_filename)

                # Write file
                page_filename = _os.path.join(self.url.getDir(), '{}.html'.format(self.url.getThreadNumber()))
                with open(page_filename, 'w') as page_file:
                    page_file.write(converted_content)

    class ImageWorker(Worker):
        """
        Worker thread that operates on a 4chan image.
        """
        def __init__(self, imageURL, pool):
            super(ThreadPool.ImageWorker, self).__init__(imageURL, pool)

        def run(self):
            absPath = self.url.getAbsPath()

            if _os.path.exists(absPath):
                return

            _Globals.globals.downloadedFiles.append(absPath)

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

        self.spawned = []
