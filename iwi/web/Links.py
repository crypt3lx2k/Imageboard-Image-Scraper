import re
import urlparse

__all__ = ['Links']

class Links (object):
    """
    Utility class for URL creation.
    """
    scheme = 'http'
    netloc = 'boards.4chan.org'
    apiloc = 'a.4cdn.org'
    imgloc = 'i.4cdn.org'

    board_pattern  = re.compile(r'/(\w+)$')
    page_pattern   = re.compile(r'/(\w+)/(\d+)$')
    thread_pattern = re.compile(r'/(\w+)/thread/(\d+)')

    @classmethod
    def __makeURL (cls, path, netloc, fragment=''):
        """
        Creates an URL based on path, whether it is an API URL and optionally
        a fragment for a specific post.
        """
        return urlparse.urlunparse (
            urlparse.ParseResult (
                scheme   = cls.scheme,
                netloc   = netloc,
                path     = path,
                params   = '',
                query    = '',
                fragment = fragment
            )
        )

    @classmethod
    def createURL (cls, path, fragment=''):
        """
        Generates an URL based on a specific path and an optional fragment.
        """
        return cls.__makeURL(path, cls.netloc, fragment)

    @classmethod
    def createAPIURL (cls, path):
        """
        Generates an API URL based on a specific path.
        """
        return cls.__makeURL(path, cls.apiloc)

    @classmethod
    def createImageURL (cls, path):
        """
        Generates an Image URL based on a specific path.
        """
        return cls.__makeURL(path, cls.imgloc)
