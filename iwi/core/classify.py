import urlparse

from ..web import Links

from . import WebEntity, Board, Page, Thread

__all__ = ['classify']

def classify (url):
    """
    Classifies an URL and returns the corresponding WebEntity derivative.
    """
    original = url

    if isinstance (url, WebEntity):
        return url

    if not isinstance (url, str):
        raise TypeError ('%s not valid type for 4chan URL' % type(url))

    if url.startswith('/'):
        url = url.lstrip('/')

    if url.endswith('/'):
        url = url.rstrip('/')

    if not '4chan.org' in url:
        url = '{}://{}/{}'.format(Links.scheme, Links.netloc, url)

    if not (
        url.startswith ('http://') or
        url.startswith ('https://')
    ):
        url = '{}://{}'.format(Links.scheme, url)

    path  = urlparse.urlparse(url).path

    match = Links.thread_pattern.match(path)
    if match:
        return Thread(*match.groups())

    match = Links.page_pattern.match(path)
    if match:
        return Page(*match.groups())

    match = Links.board_pattern.match(path)
    if match:
        return Board(*match.groups())

    raise ValueError ('invalid 4chan URL: %s' % repr(original))
