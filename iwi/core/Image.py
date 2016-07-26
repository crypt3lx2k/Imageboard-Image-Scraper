from ..web import Links

from . import WebEntity

__all__ = ['Image']

class Image (WebEntity):
    """
    Represents an image.
    """
    def __init__ (self, board, tim, ext, filename):
        self.board = board
        self.tim = tim
        self.ext = ext

        self.filename = filename

    def __str__ (self):
        """
        Returns a string representation of the object.
        """
        return self.url

    def __repr__ (self):
        """
        Returns a string representation of the object fit for eval.
        """
        return (
            '{self.__class__.__name__}({})'.format (
                ', '.join(map (
                              repr, (
                                  self.board, self.tim,
                                  self.ext, self.filename
                              )
                )),
                self=self
            )
        )

    @property
    def url (self):
        """
        Returns an url to the image.
        """
        return Links.createImageURL (
            '/{self.board}/{self.tim}{self.ext}'.format(self=self)
        )

    @property
    def apiurl (self):
        """
        Returns an url to the image, included for webcache download.
        """
        return self.url
