from ..web      import Links
from ..web.html import unescape

from . import Public, Secure
from . import WebEntity
from . import Post
from . import Image

__all__ = ['Thread']

class Thread (WebEntity):
    """
    Represents a thread.
    """
    default_object = {'posts':[]}

    def __init__ (self, board, thread):
        """
        Initializes an instance from a board and a thread number.
        """
        self.board  = board
        self.thread = thread

    def __repr__ (self):
        """
        Returns a string representation fit for eval.
        """
        return (
            '{self.__class__.__name__}({})'.format (
                ', '.join(map(repr, (self.board, self.thread))),
                self=self
            )
        )

    @property
    def apiurl (self):
        """
        Returns an url to the corresponding API json page.
        """
        return Links.createAPIURL (
            '/{self.board}/thread/{self.thread}.json'.format(self=self)
        )

    @property
    def url (self):
        """
        Returns an url to the thread.
        """
        return Links.createURL (
            '/{self.board}/thread/{self.thread}'.format(self=self)
        )

    def process (self):
        """
        Returns the Post instances you get by evaluating the thread.
        """
        thread = self.download_and_decode()
        posts  = []

        for post in thread['posts']:
            post['trip'] = str(post.get('trip', ''))
            pub_match = Public.pattern.match (post['trip'])
            sec_match = Secure.pattern.search(post['trip'])

            public = Public(pub_match.group(1)) if pub_match else None
            secure = Secure(sec_match.group(1)) if sec_match else None

            name = unescape(post.get('name', ''))
            name = name.encode('utf8')

            if post.has_key('tim') and post.has_key('ext'):
                post['image'] = Image (
                    self.board,
                    post['tim'], post['ext'].encode('utf8'),
                    post['filename'].encode('utf8')
                )

            posts.append (
                Post (
                    name   = name,
                    time   = post['time'],
                    board  = self.board,
                    thread = self.thread,
                    post   = post['no'],
                    public = public,
                    secure = secure,
                    image  = post.get('image')
                )
            )

        return posts
