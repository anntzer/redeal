# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
import argparse
from argparse import Namespace
import imp
import inspect
from os import path
import random

from . import global_defs, util
try:
    from . import gui
except ImportError:
    gui = None
from . import redeal


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
    parser.add_argument("-o", "--only", default=global_defs.SEATS,
        help="hands to print")
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
    override.add_argument("--initial",
        help='body of "initial" function: "def initial(self): <INITIAL>"')
    override.add_argument("--accept",
        help='body of "accept" function: "def accept(self, deal): <ACCEPT>"')
    override.add_argument("--do",
        help='body of "do" function: "def do(self, deal): <ACCEPT>"')
    override.add_argument("--final",
        help='body of "final" function: "def final(self, n_tries): <FINAL>"')

    func_defaults = [
        (func.__name__,
         inspect.getargspec(func),
         inspect.getsource(func).split("\n", 1)[1].lstrip())
        for func in (getattr(redeal.Simulation, fname)
                     for fname in ("initial", "accept", "do", "final"))]

    def __init__(self):
        self.stop_flag = False
        self.args = Namespace(n=10, max=None, verbose=False)

    def parse_args(self):
        """Parse command line args."""
        self.args = self.parser.parse_args()

        random.seed(self.args.seed)

        if self.args.script is None:
            self.module = None
        else:
            folder, name = path.split(path.splitext(self.args.script)[0])
            file, pathname, description = imp.find_module(name, [folder])
            self.module = imp.load_module(name, file, pathname, description)
            file.close()

        self.given_funcs = [(name, argspec, self.verbose_getattr(name, body))
                            for name, argspec, body in self.func_defaults]
        self.predeal = self.verbose_getattr("predeal", {})
        for seat in global_defs.SEATS:
            try:
                hand = getattr(self.args, seat)
            except AttributeError:
                continue
            self.predeal[seat] = redeal.H(hand)

    _obj = object()
    def verbose_getattr(self, attr, default=_obj):
        """Try to get an attribute:

        Query `self.args` first, then `self.module`, then uses `default`;
        report if `self.verbose is set`."""
        try:
            value = getattr(self.args, attr)
        except AttributeError:
            try:
                value = getattr(self.module, attr)
            except AttributeError:
                if default is not self._obj:
                    if self.args.verbose:
                        print("Using default for {}.".format(attr))
                    return default
                else:
                    raise
        return value

    def generate(self, simulation):
        """Repeatedly generate and process deals until enough are accepted."""
        found = 0
        dealer = redeal.Deal.prepare(self.predeal)
        if util.n_args(simulation.initial) == 1:
            simulation.initial(dealer)
        else:
            simulation.initial()
        for i in range(self.args.max or 1000 * self.args.n):
            if self.stop_flag:
                break
            deal = dealer()
            if simulation.accept(deal):
                found += 1
                simulation.do(deal)
                if self.args.verbose:
                    print("(hand #{}, found after {} tries)".
                          format(found, i + 1))
            if found >= self.args.n:
                break
        simulation.final(i + 1)

    def run(self):
        """Start a GUI or run a simulation."""
        if self.args.gui:
            gui.run_gui(self)
        else:
            try:
                simulation = self.verbose_getattr("simulation")
            except AttributeError:
                simulation = type(
                    str(), (redeal.Simulation,),
                    {name: util.create_func(
                        redeal, name, argspec, body, one_line=False)
                     for name, argspec, body in self.given_funcs})()
            redeal.Hand.set_str_style(redeal.Hand.LONG if self.args.long
                                      else redeal.Hand.SHORT)
            redeal.Deal.set_str_style(redeal.Deal.LONG if self.args.long
                                      else redeal.Deal.SHORT)
            redeal.Deal.set_print_only(
                [seat.upper() for seat in self.args.only])
            self.generate(simulation)


def console_entry():
    main = Main()
    main.parse_args()
    main.run()


def gui_entry():
    main = Main()
    main.parse_args()
    main.args.gui = True
    main.run()


if __name__ == "__main__":
    console_entry()
