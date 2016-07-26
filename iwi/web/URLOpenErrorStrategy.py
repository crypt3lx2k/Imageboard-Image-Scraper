import httplib
import urllib2
import socket

from . import RetryStrategy

__all__ = ['URLOpenErrorStrategy']

class URLOpenErrorStrategy (RetryStrategy):
    """
    A base class for retry strategies that want to handle common urllib2.urlopen
    errors in a sensible manner.
    """
    def register_error (self, error):
        """
        Registers an error with the retry strategy.

        This method should only return if the retry strategy knows how to handle
        the specific exception, if it doesn't the exception should be reraised.
        """
        try:
            raise error
        except httplib.BadStatusLine:
            self.exhaust()
        except httplib.IncompleteRead:
            pass
        except urllib2.HTTPError as e:
            if e.code == 408:
                return
            if e.code == 429:
                return
            if e.code >= 300:
                self.exhaust()
        except socket.timeout:
            pass
        except urllib2.URLError as e:
            if isinstance(e.reason, OSError):
                self.exhaust()
