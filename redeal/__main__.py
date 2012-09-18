# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from argparse import ArgumentParser
import imp
from os import path
import sys

from .globals import *
from .redeal import *


def generate(n_hands, max_tries, predeal, accept, do, verbose=False):
    """Repeatedly pass hands to an `accept` function until enough are accepted.
    """
    found = 0
    dealer = Deal.prepare(predeal)
    for i in range(max_tries):
        deal = Deal(dealer)
        if accept(deal):
            found += 1
            do(deal)
            if verbose:
                print("(hand #{}, found after {} tries)".format(found, i + 1))
        if found >= n_hands:
            break
    return i + 1


def create_func(name, args, declared, body, g=globals()):
    if body is None:
        return body
    d = {}
    defstr = "def {name}({args}): {declared} {body}".format(
        name=name, args=", ".join(args),
        declared="global {};".format(", ".join(declared)) if declared else "",
        body=body)
    if sys.version_info.major < 3:
        exec("exec {} in g, d".format(defstr))
    else:
        exec("exec({!r}, g, d)".format(defstr))
    return d[name]


def main():
    parser = ArgumentParser(
        description="A reimplementation of Thomas Andrews' Deal in Python.")
    parser.add_argument("-n", type=int, default=10,
        help="the number of requested hands")
    parser.add_argument("--max", type=int,
        help="the maximum number of tries (defaults to 1000*n)")
    parser.add_argument("-l", "--long", action="store_true",
        help="long output for diagrams")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="be verbose")
    parser.add_argument("script", nargs="?",
        help="path to script")
    override = parser.add_argument_group(
        "arguments overriding values given in script")
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
    args = parser.parse_args()

    if args.script is None:
        module = None
    else:
        folder, name = path.split(path.splitext(args.script)[0])
        file, pathname, description = imp.find_module(name, [folder])
        module = imp.load_module(name, file, pathname, description)
        file.close()

    def verbose_getattr(attr, default, transform=lambda x: x):
        args_attr = getattr(args, attr, None)
        if args_attr is not None:
            return transform(args_attr)
        if hasattr(module, attr):
            return getattr(module, attr)
        else:
            if args.verbose:
                print("Using default for {}.".format(attr))
            return default

    predeal = verbose_getattr("predeal", {})
    for seat in SEATS:
        if getattr(args, seat):
            predeal[seat] = H(getattr(args, seat))
    initial = verbose_getattr("initial",
        lambda: None,
        lambda body: create_func("initial", (), args.globals, body))
    accept = verbose_getattr("accept",
        lambda deal: True,
        lambda body: create_func("accept", ("deal",), args.globals, body))
    do = verbose_getattr("do",
        lambda deal: print("{}".format(deal)),
        lambda body: create_func("do", ("deal",), args.globals, body))
    final = verbose_getattr("final",
        lambda n_tries: print("Tries: {}".format(n_tries)),
        lambda body: create_func("final", ("n_tries",), args.globals, body))

    if args.long:
        Deal.__str__ = lambda self: self._long_str
        Deal.__unicode__ = lambda self: self._long_str

    initial()
    tries = generate(args.n, args.max or 1000 * args.n, predeal, accept, do,
                     verbose=args.verbose)
    final(tries)


if __name__ == "__main__":
    main()
