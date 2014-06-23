import os as _os
import re as _re

class Link(str):
    """
    Base class for Links.
    """
    def __init__(self, url):
        if isinstance(self, Link):
            return self

        super(Link, self).__init__(url)

class BoardLink(Link):
    """
    Link that refers to a 4chan board.
    """
    def __init__(self, url):
        super(BoardLink, self).__init__(url)
        self.board = None

    def getBoard(self):
        """
        Returns the name of the board.
        """
        if self.board is None:
            self.board, = _re.search(r"https?://(?:www|boards)\.4chan\.org/(\w+)",
                                     self).groups()

        return self.board

class ImageLink(Link):
    """
    Link that refers to a 4chan image.
    """
    def __init__(self, url):
        super(ImageLink, self).__init__(url)
        self.name    = None
        self.thread  = None
        self.absPath = None

    def setThread(self, thread):
        """
        Stores the thread which contains the image.
        """
        self.thread = thread

    def getName(self):
        """
        Returns the name of the image.
        """
        if self.name is None:
            self.name, = _re.search(r"https?://i\.4cdn\.org/\w+/(\d+\.\w+)",
                                    self).groups()

        return self.name

    def getAbsPath(self):
        """
        Returns the absolute path of the image in the directory hierarchy.
        """
        if self.absPath is None:
            self.absPath = _os.path.join(self.getDir(),
                                         self.getName())

        return self.absPath

    def getBoard(self):
        """
        Returns the board that contains the image.
        """
        return self.thread.getBoard()

    def getThreadNumber(self):
        """
        Returns the thread that contains the image.
        """
        return self.thread.getThreadNumber()

    def getDir(self):
        """
        Returns the directory that will contain the image.
        """
        return self.thread.getDir()

class ThreadLink(Link):
    """
    Link that refers to a 4chan thread.
    """
    def __init__(self, url):
        super(ThreadLink, self).__init__(url)
        self.board  = None
        self.thread = None
        self.dir    = None
        self.static_dir = None

    def getDir(self):
        """
        Returns the directory that every image in this thread will be saved in.
        """
        if self.dir is None:
            self.dir = _os.path.join(self.getBoard(),
                                     self.getThreadNumber())

        return self.dir

    def getStaticDir(self):
        """
        Returns the directory that holds the static (css/js/etc) files for this thread.
        """
        if self.static_dir is None:
            self.static_dir = _os.path.join(self.getBoard(),
                                            self.getThreadNumber(),
                                            'static')

        return self.static_dir

    def _parseURL(self):
        """
        Stores board name and thread number.
        """
        self.board, self.thread = \
            _re.search(r"https?://(?:www|boards)\.4chan\.org/(\w+)/thread/(\d+)",
                       self).groups()        

    def getBoard(self):
        """
        Returns board that contains this thread.
        """
        if self.board is None:
            self._parseURL()

        return self.board

    def getThreadNumber(self):
        """
        Returns thread number of this thread.
        """
        if self.thread is None:
            self._parseURL()

        return self.thread

def classify(link):
    """
    Classifies link and returns the corresponding Link object.
    """
    if isinstance(link, Link):
        return link

    if not isinstance(link, str):
        raise TypeError("%s object is not convertible to link." % (type(link)))

    if not (link.startswith("http://") or link.startswith("https://")):
        link = "https://" + link

    link = link.replace("www", "boards", 1)

    if _re.search(r"(https?://boards\.4chan\.org/\w+/thread/\d+)",
                  link):
        return ThreadLink(link)
    elif _re.search(r"(https?://boards\.4chan\.org/\w+)",
                    link):
        return BoardLink(link)
    else:
        raise ValueError("invalid 4chan url: %s" % (link))
