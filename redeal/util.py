import inspect
import sys
import textwrap


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
        body=textwrap.indent(body, "    "))
    if module not in create_func.globals:
        # This allows us to share globals between callbacks.
        create_func.globals[module] = {
            name: getattr(module, name) for name in dir(module)}
    d = {}
    try:
        exec(defs, create_func.globals[module], d)
    except Exception:
        print("An invalid function definition raised:\n", file=sys.stderr)
        raise
    return d[name]


create_func.globals = {}


class reify:
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
