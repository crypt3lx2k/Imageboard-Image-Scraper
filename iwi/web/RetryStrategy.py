__all__ = ['RetryStrategy']

class RetryStrategy (object):
    """
    Base class for retry strategies.
    """
    def exhaust (self):
        """
        Sets the retry strategy in such a state that it will always return a
        value that indicates that no further sleep attempts should be made.
        """
        raise NotImplementedError (
            'RetryStrategy derivatives must implement this!'
        )

    def register_error (self, error):
        """
        Registers an error with the retry strategy.

        This method should only return if the retry strategy knows how to handle
        the specific exception, if it doesn't the exception should be reraised.
        """
        raise NotImplementedError (
            'RetryStrategy derivatives must implement this!'
        )

    def reset (self):
        """
        Resets the retry strategy to its base state.
        """
        raise NotImplementedError (
            'RetryStrategy derivatives must implement this!'
        )

    def seconds (self):
        """
        Returns the next sleep interval in seconds. If no further sleep attempts
        should be performed the value returned is None.
        """
        raise NotImplementedError (
            'RetryStrategy derivatives must implement this!'
        )
