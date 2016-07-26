import socket
import threading
import time

import zlib

import httplib
import urllib2
import urlparse

try:
    import cPickle as pickle
except ImportError:
    import pickle

from . import UniformRetryStrategy

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__all__ = ['WebCache']

class WebCache (object):
    """
    Allows for thread-safe cached downloads, honors last-modified.

    WebCache can also write and read the cache to and from disk.
    """
    # default retry parameters
    retry_times = 3
    retry_lower = 5
    retry_upper = 15

    # default user string
    user_string = "Mozilla/5.0"

    def __init__ (self, cache_file=None, sleeper=None):
        """
        Initializes an instance from an optional cache_file, an optional
        retrier, and an optional sleeper.

        The cache_file parameter may either be a filename or an open file-like
        object.
        If the cache_file parameter is not given the cache is initialized to be
        empty.

        The sleeper parameter must be a function that takes the number of
        seconds to sleep (as a floating point number).
        If the sleeper parameter is not given it is initialized as time.sleep.
        """
        if cache_file is None:
            self.cache = {}
        else:
            self.load(cache_file)

        if sleeper is None:
            self.sleeper = time.sleep

        self.cache_lock = threading.Lock()
        self.set_online_mode()

    def download (self, url, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, bypass_cache=False):
        """
        Downloads the contents from the URL, if something goes wrong it
        registers the exception with the retrier and asks for a sleep time.
        """
        retry = 0.0

        retrier = UniformRetryStrategy ( 
            self.retry_times,
            self.retry_lower,
            self.retry_upper
        )

        while retry is not None:
            if retry:
                logger.debug('sleeping on %s for %s seconds', url, retry)
                self.sleeper(retry)

            try:
                return self.downloader(url, timeout=timeout, bypass_cache=bypass_cache)
            except Exception as e:
                logger.debug('got on %s exception %s', url, e)
                retrier.register_error(e)

            retry = retrier.seconds()

        return ''

    def download_offline (self, url, timeout=None, bypass_cache=False):
        """
        Simulates downloading contents from URL while only looking it up in the
        cache.
        """
        contents = None
        key = self.url_to_key(url)

        if bypass_cache:
            raise ValueError ('Cache bypass doesn\'t make sense in offline mode.')

        if self.has_key(key):
            _, contents = self.get_values(key)
            return zlib.decompress(contents)

        raise urllib2.URLError(OSError('not in cache'))

    def download_online (self, url, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, bypass_cache=False):
        """
        Downloads contents from the URL, using the internal cache if applicable.
        """
        contents = None
        key = self.url_to_key(url)
        request = urllib2.Request(url)
        request.add_header('User-agent', self.user_string)

        if not bypass_cache and self.has_key(key):
            lastmodified, contents = self.get_values(key)

            request.add_header('if-modified-since', lastmodified)

        try:
            connection   = urllib2.urlopen(request, timeout=timeout)
            lastmodified = connection.headers.get('last-modified')
            contents     = connection.read()
            connection.close()
        except urllib2.HTTPError as e:
            if e.code == 304:
                logger.debug (
                    'cache hit %r not modified since %s',
                    key, lastmodified
                )
                return zlib.decompress(contents)
            raise

        if not bypass_cache:
            self.set_values(key, lastmodified, zlib.compress(contents))

        return contents

    def dump (self, outfile):
        """
        Writes internal cache to outfile.

        outfile may be a filename or an open file-like object.
        """
        if isinstance(outfile, str):
            outfile = open(outfile, 'wb')

        pickle.dump(self.cache, outfile, protocol=-1)

    def get_values (self, key):
        """
        Returns the values referred to by key in a thread-safe manner.
        """
        with self.cache_lock:
            logger.debug('getting %r from cache', key)
            return self.cache[key]

    def has_key (self, key):
        """
        Returns if the cache contains entries for key.
        """
        logger.debug('looking for %r in cache', key)
        return key in self.cache

    def keys (self):
        """
        Makes a copy of the list of keys and returns it.
        """
        return self.cache.keys()

    def load (self, infile):
        """
        Loads internal cache from infile.

        infile may be a filename or an open file-like object.
        """
        try:
            if isinstance(infile, str):
                infile = open(infile, 'rb')

            self.cache = pickle.load(infile)
        except IOError:
            self.cache = {}

    def url_to_key (self, url):
        """
        Takes an url and returns a key for use in the cache.
        """
        return urlparse.urlparse(url).path

    def remove_key (self, key):
        """
        Removes an entry from the cache, not thread-safe.
        """
        del self.cache[key]

    def set_offline_mode (self):
        """
        Sets offline mode for the webcache.
        """
        self.downloader = self.download_offline

    def set_online_mode (self):
        """
        Sets online mode for the webcache.
        """
        self.downloader = self.download_online

    def set_values (self, key, *args):
        """
        Sets values in a thread-safe manner.
        """        
        with self.cache_lock:
            logger.debug('storing %r in cache', key)
            self.cache[key] = args
