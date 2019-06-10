# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
import inspect
import sys


def create_func(module, name, signature_str, body):
    """Create a method with the given module dict, name, arguments and body."""
    if isinstance(body, type(lambda: None)):
        if inspect.ismethod(body):
            return body
        else:
            return staticmethod(body)
    defs = "def {name}{spec}:\n{body}".format(
        name=name,
        spec=signature_str,
        body=indent(body, "    "))
    if module not in create_func.globals:
        # This allows us to share globals between callbacks.
        create_func.globals[module] = {
            name: getattr(module, name) for name in dir(module)}
    d = {}
    try:
        exec_(defs, create_func.globals[module], d)
    except Exception:
        print("An invalid function definition raised:\n", file=sys.stderr)
        raise
    return d[name]


create_func.globals = {}


def exec_(stmt, globals, locals):
    """The exec function/statement, as implemented by six."""
    if sys.version_info < (3,):
        exec("exec {!r} in globals, locals".format(stmt))
    else:
        exec("exec({!r}, globals, locals)".format(stmt))


# Backported from Python 3.
def indent(text, prefix, predicate=None):
    """
    Adds 'prefix' to the beginning of selected lines in 'text'.

    If 'predicate' is provided, 'prefix' will only be added to the lines
    where 'predicate(line)' is True. If 'predicate' is not provided,
    it will default to adding 'prefix' to all non-empty lines that do not
    consist solely of whitespace characters.
    """
    if predicate is None:
        def predicate(line):
            return line.strip()

    def prefixed_lines():
        for line in text.splitlines(True):
            yield (prefix + line if predicate(line) else line)
    return ''.join(prefixed_lines())


def n_args(func):
    return len(inspect.getargspec(func).args) - inspect.ismethod(func)


class reify(object):
    """Auto-destructing property, from Pyramid code."""

    def __init__(self, wrapped, doc=None, name=None):
        self.wrapped = wrapped
        self.__doc__ = (doc if doc is not None
                        else getattr(wrapped, "__doc__", None))
        self.name = name if name is not None else wrapped.__name__

    def __get__(self, inst, owner):
        if inst is None:
            return self
        value = self.wrapped(inst)
        setattr(inst, self.name, value)
        return value
