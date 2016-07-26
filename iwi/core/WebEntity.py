try:
    import json
except ImportError:
    import simplejson as json

from ..web import WebCache

__all__ = ['WebEntity']

class WebEntity (object):
    """
    Represents a base web entity from the imageboard.

    Classes that derive from this are typically boards, pages and threads.
    """
    timeout = 10.0

    default_object = None
    webcache = WebCache()

    @property
    def apiurl (self):
        """
        Returns an API URL with the relevant contents for the web entity.

        Derivative classes must override this method.
        """
        raise NotImplementedError ('WebEntity derivatives must implement this!')

    @property
    def url (self):
        """
        Returns an URL fit for viewing the web entity in a browser.

        Derivative classes must override this method.
        """
        raise NotImplementedError ('WebEntity derivatives must implement this!')

    def download (self, bypass_cache=False):
        """
        Returns the downloaded contents of the corresponding API URL as a
        string.
        """
        return self.webcache.download (
            self.apiurl,
            timeout=self.timeout, bypass_cache=bypass_cache
        )

    def decode (self, s):
        """
        Decodes and returns the JSON object in s or the default value if it
        fails.
        """
        try:
            return json.loads(s)
        except ValueError:
            return self.default_object

    def download_and_decode (self, bypass_cache=False):
        """
        Downloads the API URL contents, decodes them and returns the resulting
        object, or the default value if that fails.
        """
        return self.decode(self.download(bypass_cache=bypass_cache))

    def process (self):
        """
        Processes the web entity.
        """
        raise NotImplementedError ('WebEntity derivatives must implement this!')
