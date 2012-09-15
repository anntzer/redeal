# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from argparse import ArgumentParser
import imp
from os import path

from .globals import *
from .mutable import ref
from .redeal import *


def generate(n_hands, max_tries, predeal, accept, verbose=False):
    """Repeatedly pass hands to an `accept` function until enough are accepted.
    """
    found = 0
    dealer = Deal.prepare(predeal)
    for i in range(max_tries):
        deal = Deal(dealer)
        if accept(deal):
            found += 1
            if verbose:
                print("(hand #{}, found after {} tries)".format(found, i + 1))
        if found >= n_hands:
            break
    return i + 1


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
    my_globals = dict(
        globals(),
        print=lambda *args, **kwargs: print(*args, **kwargs) or True)
    override.add_argument("--initial",
        type=lambda s: eval("lambda: " + s, my_globals),
        help='body of "initial" function: "initial = lambda: <INITIAL>"')
    override.add_argument("--accept",
        type=lambda s: eval("lambda deal: " + s, my_globals),
        help='body of "accept" function: "accept = lambda deal: <ACCEPT>"')
    override.add_argument("--final",
        type=lambda s: eval("lambda n_tries: " + s, my_globals),
        help='body of "final" function: "final = lambda n_tries: <FINAL>"')
    override.add_argument("-g", "--global",
        nargs=2, dest="globals", default=[], action="append",
        help="global, '<<'-mutable variable for functions given in the "
        "command-line", metavar=("NAME", "INIT"))
    args = parser.parse_args()

    for name, init in args.globals:
        my_globals[name] = ref(eval(init))

    if args.script is None:
        module = None
    else:
        folder, name = path.split(path.splitext(args.script)[0])
        file, pathname, description = imp.find_module(name, [folder])
        module = imp.load_module(name, file, pathname, description)
        file.close()

    def verbose_getattr(attr, default):
        args_attr = getattr(args, attr, None)
        if args_attr is not None:
            return args_attr
        if hasattr(module, attr):
            return getattr(module, attr)
        else:
            if args.verbose:
                print("Using default for {}.".format(attr))
            return default
    initial = verbose_getattr("initial", lambda: None)
    predeal = verbose_getattr("predeal", {})
    for seat in SEATS:
        if getattr(args, seat):
            predeal[seat] = H(getattr(args, seat))
    accept = verbose_getattr("accept",
        lambda deal: print("{}".format(deal)) or True)
    final = verbose_getattr("final",
                            lambda tries: print("Tries: {}".format(tries)))
    if args.long:
        Deal.__str__ = lambda self: self._long_str
        Deal.__unicode__ = lambda self: self._long_str

    initial()
    tries = generate(args.n, args.max or 1000 * args.n, predeal, accept,
                     verbose=args.verbose)
    final(tries)


if __name__ == "__main__":
    main()
