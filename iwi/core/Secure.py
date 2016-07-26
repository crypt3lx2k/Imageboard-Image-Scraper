import re

from . import Tripcode

__all__ = ['Secure']

class Secure (Tripcode):
    """
    Represents a secure tripcode.
    """
    pattern = re.compile(r'!!([\w\+\/]+)$')

    def __str__ (self):
        """
        Returns a string representation.
        """
        return '!!' + super(Secure, self).__str__()
