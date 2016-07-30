from ..web import Links

from . import Public, Secure
from . import WebEntity

__all__ = ['Post']

class Post (WebEntity):
    """
    Represents a post with a tripcode.
    """
    def __init__ (self,
                  board=None,  thread=None, post=None,
                  name=None,   time=None,
                  public=None, secure=None, image=None):
        self.board, self.thread = board, thread
        self.post = post

        self.name, self.time = name, time

        self.public = public
        self.secure = secure

        self.image = image

        if not self.name:
            self.name = 'Nameless'

    def __cmp__ (self, other):
        """
        Returns a comparison value between two Posts.
        """
        c = cmp(self.name, other.name)
        if c: return c

        c = cmp(self.board, other.board)
        if c: return c

        c = cmp(self.public, other.public)
        if c: return c

        c = cmp(self.secure, other.secure)
        return c

    def __repr__ (self):
        """
        Returns a string representation of the object fit for eval.
        """
        return ''.join ((
                '{self.__class__.__name__}(name={self.name!r}, '
                'time={self.time!r}, board={self.board!r}, '
                'thread={self.thread!r}, post={self.post!r}, '
                'public={self.public!r}, secure={self.secure!r}, '
                'image={self.image!r})'
        )).format(self=self)

    def __str__ (self):
        """
        Returns a string representation of the object.
        """
        tripcode = ''
        if self.public:
            tripcode += str(self.public)
        if self.secure:
            tripcode += str(self.secure)

        if not self.solved():
            return '{self.url} {self.name} {}'.format (
                tripcode, self=self
            )

        solutions = '#'
        if self.public and self.public.solved():
            solutions += self.public.key
        if self.secure and self.secure.solved():
            solutions += '#' + self.secure.key

        return '{self.url} {self.name} {} => {}'.format (
            solutions, tripcode, self=self
        )

    def process (self):
        """
        Does nothing, returns an iterable for uniformity with the other
        WebEntity derivatives.
        """
        return tuple()

    @property
    def url (self):
        """
        Returns an url to the post.
        """
        return Links.createURL (
            '/{self.board}/thread/{self.thread}'.format(self=self),
            'p{self.post}'.format(self=self)
        )

    @property
    def apiurl (self):
        """
        Returns an API URL with the relevant contents for the Post.
        """
        return self.thread.apiurl

    @property
    def imageurl (self):
        """
        Returns an url to the image of this post.
        """
        return self.image.url

    def solved (self):
        """
        Returns whether this post has any solved tripcodes.
        """
        return (
            (self.public and self.public.solved()) or
            (self.secure and self.secure.solved())
        )
