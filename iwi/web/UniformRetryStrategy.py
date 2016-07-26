import random

from . import URLOpenErrorStrategy

__all__ = ['UniformRetryStrategy']

class UniformRetryStrategy (URLOpenErrorStrategy):
    """
    A retry strategy that yields numbered sleep intervals that are uniformly
    distributed.
    """
    def __init__ (self, times, lower, upper):
        """
        Initializes an instance from number of times to try, and lower and upper
        bounds to sleep (in seconds).
        """
        self.times = times
        self.lower = lower
        self.upper = upper

        self.counter = 0

    @classmethod
    def from_average (cls, times, average, span):
        """
        Initializes an instance from number of times to try, average sleep time
        and span from the average sleep time (in seconds).
        """
        return cls(times, average-span, average+span)

    def exhaust (self):
        """
        Sets the retry strategy in such a state that it will always return a
        value that indicates that no further sleep attempts should be made.
        """
        self.counter = self.times

    def reset (self):
        """
        Resets the retry strategy to its base state.
        """
        self.counter = 0

    def seconds (self):
        """
        Returns the next sleep interval in seconds. If no further sleep attempts
        should be performed the value returned is None.
        """
        if self.counter == self.times:
            return None

        self.counter += 1
        return random.uniform(self.lower, self.upper)
