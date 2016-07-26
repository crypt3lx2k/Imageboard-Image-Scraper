__all__ = ['Tripcode']

class Tripcode (object):
    """
    Base class for tripcodes.
    """
    def __init__ (self, cipher, key=None):
        """
        Initializes a new instance from a ciphertext and an optional key.
        """
        self.cipher = cipher
        self.key    = key

    def __cmp__ (self, other):
        """
        Compares two tripcodes.
        """
        if isinstance(other, Tripcode):
            return cmp(self.cipher, other.cipher)
        else:
            return cmp(type(self), type(other))

    def __hash__ (self):
        """
        Returns a hash value for this tripcode.
        """
        return hash(self.cipher)

    def __repr__ (self):
        """
        Returns a string representation fit for eval.
        """
        return '{self.__class__.__name__}({})'.format (
            ', '.join(map(repr, (self.cipher, self.key))),
            self=self
        )

    def __str__ (self):
        """
        Returns a string representation.
        """
        return self.cipher

    def solve (self, solver):
        """
        Attempts to solve tripcode using a solver.

        If the tripcode is already solved (key is not None) then no action is
        taken.
        """
        if self.key is None:
            self.key = solver.solve(self.cipher)

    def solved (self):
        """
        Returns whether the tripcode is solved or not.
        """
        return self.key is not None
