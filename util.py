# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals


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

