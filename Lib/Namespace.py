class Namespace(object):
    def __init__(self, *args, **kwargs):
        self.__dict__ = kwargs

        for arg in args:
            self.acquire(arg)

    def __str__(self):
        vals = []

        for var in self.__dict__:
            vals.append(
                "%s=%s" % (
                    var,
                    str(self.__dict__[var])
                )
            )

        return "Namespace(%s)" % (', '.join(vals))

    def __repr__(self):
        return str(self)

    def acquire(self, other):
        if not isinstance(other, dict):
            other = other.__dict__

        for var in other:
            self.__dict__[var] = other[var]

    def pollute(self, other):
        if not isinstance(other, dict):
            other = other.__dict__

        for var in self.__dict__:
            other[var] = self.__dict__[var]
