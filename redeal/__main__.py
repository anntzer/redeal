# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
import argparse
import imp
from os import path
import random
import sys

from . import globals
try:
    from . import gui
except ImportError:
    gui = None
from . import redeal
redeal_star = {name: getattr(redeal, name) for name in redeal.__all__}


def exec_(stmt, globals, locals):
    """The exec function/statement, as implemented by six."""
    if sys.version_info.major < 3:
        exec("exec {!r} in globals, locals".format(stmt))
    else:
        exec("exec({!r}, globals, locals)".format(stmt))


class Main(object):
    parser = argparse.ArgumentParser(
        description="A reimplementation of Thomas Andrews' Deal in Python.")
    parser.add_argument("--gui", action="store_true",
        help="start the GUI")
    parser.add_argument("-n", type=int, default=10,
        help="the number of requested deals")
    parser.add_argument("--max", type=int,
        help="the maximum number of tries (defaults to 1000*n)")
    parser.add_argument("-l", "--long", action="store_true",
        help="long output for diagrams")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="be verbose")
    parser.add_argument("--seed", type=int,
        help="random number generator seed")
    parser.add_argument("script", nargs="?",
        help="path to script")
    override = parser.add_argument_group(
        "arguments overriding values given in script",
        argument_default=argparse.SUPPRESS)
    override.add_argument("-N",
        help="predealt North hand as a string")
    override.add_argument("-E",
        help="predealt East hand as a string")
    override.add_argument("-S",
        help="predealt West hand as a string")
    override.add_argument("-W",
        help="predealt South hand as a string")
    override.add_argument("-g", "--global",
        dest="globals", default=[], action="append",
        help="variable implicitly global in the following functions...",
        metavar="NAME")
    override.add_argument("--initial",
        help='body of "initial" function: "def initial(): <INITIAL>"')
    override.add_argument("--accept",
        help='body of "accept" function: "def accept(deal): <ACCEPT>"')
    override.add_argument("--do",
        help='body of "do" function: "def do(deal): <ACCEPT>"')
    override.add_argument("--final",
        help='body of "final" function: "def final(n_tries): <FINAL>"')

    func_defaults = [
        ("initial", (), "pass"),
        ("accept", ("deal",), "return True"),
        ("do", ("deal",), 'print("{}".format(deal))'),
        ("final", ("n_tries",), 'print("Tries: {}".format(n_tries))')]

    def __init__(self):
        self.args = self.parser.parse_args()
        if self.args.gui and not gui:
            print("tkinter, and thus the GUI, is not available.")
            sys.exit(1)

        random.seed(self.args.seed)
        self.stop_flag = False

        if self.args.script is None:
            self.module = None
        else:
            folder, name = path.split(path.splitext(self.args.script)[0])
            file, pathname, description = imp.find_module(name, [folder])
            self.module = imp.load_module(name, file, pathname, description)
            file.close()

        self.given_funcs = [(name, signature, self.verbose_getattr(name, body))
                            for name, signature, body in self.func_defaults]
        self.predeal = self.verbose_getattr("predeal", {})
        for seat in globals.SEATS:
            try:
                hand = getattr(self.args, seat)
            except AttributeError:
                continue
            self.predeal[seat] = redeal.H(hand)

    def verbose_getattr(self, attr, default):
        """Try to get an attribute:

        Query `self.args` first, then `self.module`, then uses `default`;
        report if `self.verbose is set`."""
        try:
            value = getattr(self.args, attr)
        except AttributeError:
            try:
                value = getattr(self.module, attr)
            except AttributeError:
                if self.args.verbose:
                    print("Using default for {}.".format(attr))
                return default
        return value

    def create_func(self, name, signature, body, add_globals=False, indent=True):
        """Create a function with the given name, arguments, globals and body."""
        if isinstance(body, type(lambda: None)):
            return body
        d = {}
        if indent:
            format_str = "def {name}({signature}):\n{declared}\n{body}"
        else:
            format_str = "def {name}({signature}): {declared} {body}"
        defstr = format_str.format(
            name=name,
            signature=", ".join(signature),
            declared="    global {};".format(", ".join(self.args.globals))
                     if add_globals and self.args.globals else "",
            body=body)
        try:
            exec_(defstr, redeal_star, d)
        except:
            print("An invalid function definition raised:\n", file=sys.stderr)
            raise
        return d[name]

    def generate(self, funcs):
        """Repeatedly pass deals to `accept` until enough are accepted.
        """
        funcs["initial"]()
        found = 0
        dealer = redeal.Deal.prepare(self.predeal)
        for i in range(self.args.max or 1000 * self.args.n):
            if self.stop_flag:
                break
            deal = redeal.Deal(dealer)
            if funcs["accept"](deal):
                found += 1
                funcs["do"](deal)
                if self.args.verbose:
                    print("(hand #{}, found after {} tries)".
                          format(found, i + 1))
            if found >= self.args.n:
                break
        funcs["final"](i + 1)
        return i + 1

    def run(self):
        if self.args.gui:
            gui.run_gui(self)
        else:
            funcs = {name: self.create_func(name, signature, body,
                                            add_globals=True, indent=False)
                     for name, signature, body in self.given_funcs}
            redeal.Hand.set_str_style(redeal.Hand.LONG if self.args.long
                                      else redeal.Hand.SHORT)
            redeal.Deal.set_str_style(redeal.Deal.LONG if self.args.long
                                      else redeal.Deal.SHORT)
            self.generate(funcs)


def console_entry():
    return Main().run()


def gui_entry():
    main = Main()
    main.args.gui = True
    main.run()


if __name__ == "__main__":
    console_entry()
