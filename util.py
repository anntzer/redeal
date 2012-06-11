class Immutable(object):
    """An object whose attributes cannot be set, except reify class attributes.
    """

    def __setattr__(self, attr, val):
        if isinstance(type(self).__dict__.get(attr, None), reify):
            object.__setattr__(self, attr, val)
        else:
            raise Exception("{} is immutable.".format(self))


class reify(object):
    """Auto-destructing property, from Pyramid code."""

    def __init__(self, wrapped):
        self.wrapped = wrapped
        if hasattr(wrapped, "__doc__"):
            self.__doc__ = wrapped.__doc__

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val

