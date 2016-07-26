import re

from . import Tripcode

__all__ = ['Public']

class Public (Tripcode):
    """
    Represents a regular tripcode.
    """
    pattern = re.compile(r'^!([\w\.\/]+)')

    def __str__ (self):
        """
        Returns a string representation.
        """
        return '!' + super(Public, self).__str__()
