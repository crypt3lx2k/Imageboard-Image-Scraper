from ..web import Links

from . import WebEntity

__all__ = ['Image']

class Image (WebEntity):
    """
    Represents an image.
    """
    def __init__ (self, board, tim, ext, filename, md5, fsize, w, h):
        self.board = board
        self.tim = tim
        self.ext = ext

        self.filename = filename

        self.md5 = md5
        self.fsize = fsize

        self.w = w
        self.h = h

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
                                  self.ext, self.filename,
                                  self.md5, self.fsize,
                                  self.w, self.h
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
