# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
import inspect
import sys


class reify(object):
    """Auto-destructing property, from Pyramid code."""

    def __init__(self, wrapped, doc=None):
        self.wrapped = wrapped
        self.__doc__ = (doc if doc is not None
                        else getattr(wrapped, "__doc__", None))

    def __get__(self, inst, owner):
        if inst is None:
            return self
        value = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, value)
        return value


def exec_(stmt, globals, locals):
    """The exec function/statement, as implemented by six."""
    if sys.version_info.major < 3:
        exec("exec {!r} in globals, locals".format(stmt))
    else:
        exec("exec({!r}, globals, locals)".format(stmt))


def create_func(module, name, argspec, body, one_line=True):
    """Create a method with the given module dict, name, arguments and body.
    """
    if isinstance(body, type(lambda: None)):
        if inspect.ismethod(body):
            return body
        else:
            return staticmethod(body)
    d = {}
    defs = "def {name}{spec}:{newline}{body}".format(
        name=name,
        spec=inspect.formatargspec(*argspec),
        newline=" " if one_line else "\n    ",
        body=body)
    try:
        exec_(defs, {name: getattr(module, name) for name in module.__all__}, d)
    except:
        print("An invalid function definition raised:\n", file=sys.stderr)
        raise
    return d[name]


def n_args(func):
    return len(inspect.getargspec(func).args) - inspect.ismethod(func)
