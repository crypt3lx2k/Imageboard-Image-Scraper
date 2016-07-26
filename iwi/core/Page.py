from ..web import Links

from . import Board
from . import Thread

__all__ = ['Page']

class Page (Board):
    """
    Represents a specific page at a board.
    """
    default_object = {'threads':[]}

    def __init__ (self, board, page):
        """
        Initializes an instance from a board and a page.
        """
        super (Page, self).__init__(board)
        self.page = page

    def __repr__ (self):
        """
        Returns a string representation fit for eval.
        """
        return (
            '{self.__class__.__name__}({self.board!r}, {self.page!r})'.format (
                self=self
            )
        )

    @property
    def apiurl (self):
        """
        Returns an url to the corresponding API json page.
        """
        return Links.createAPIURL (
            '/{self.board}/{self.page}.json'.format(self=self)
        )

    @property
    def url (self):
        """
        Returns an url to the board page.
        """
        return Links.createURL (
            '/{self.board}/{self.page}'.format(self=self)
        )

    def process (self):
        """
        Returns the Thread instances you get by evaluating the page.
        """
        page    = self.download_and_decode()
        threads = []

        for thread in page['threads']:
            threads.append (
                Thread(self.board, thread['posts'][0]['no'])
            )

        return threads
