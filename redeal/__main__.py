import argparse
from argparse import Namespace
import inspect
import random
import runpy

from . import global_defs, gui, redeal, util


class Main:
    parser = argparse.ArgumentParser(
        description="A reimplementation of Thomas Andrews' Deal in Python.")
    parser.add_argument(
        "--gui", action="store_true",
        help="start the GUI")
    parser.add_argument(
        "-n", type=int, default=10,
        help="the number of requested deals")
    parser.add_argument(
        "--max", type=int,
        help="the maximum number of tries (defaults to 1000*n)")
    parser.add_argument(
        "-f", "--format", choices=["short", "long", "pbn"],
        default="short", help="set diagram print style")
    parser.add_argument(
        "-o", "--only",
        default="".join(seat.name for seat in global_defs.Seat),
        help="hands to print")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="be verbose")
    parser.add_argument(
        "--seed", type=int,
        help="random number generator seed")
    parser.add_argument(
        "script", nargs="?",
        help="path to script")
    override = parser.add_argument_group(
        "arguments overriding values given in script",
        argument_default=argparse.SUPPRESS)
    override.add_argument(
        "-N",
        help="predealt North hand as a string")
    override.add_argument(
        "-E",
        help="predealt East hand as a string")
    override.add_argument(
        "-S",
        help="predealt West hand as a string")
    override.add_argument(
        "-W",
        help="predealt South hand as a string")
    override.add_argument(
        "--initial",
        help='body of "initial" function: "def initial(self): <INITIAL>"')
    override.add_argument(
        "--accept",
        help='body of "accept" function: "def accept(self, deal): <ACCEPT>"')
    override.add_argument(
        "--do",
        help='body of "do" function: "def do(self, deal): <ACCEPT>"')
    override.add_argument(
        "--final",
        help='body of "final" function: "def final(self, n_tries): <FINAL>"')

    func_defaults = [
        (func.__name__,
         str(inspect.signature(func)),
         inspect.getsource(func).split("\n", 1)[1].lstrip())
        for func in (getattr(redeal.Simulation, fname)
                     for fname in ("initial", "accept", "do", "final"))]

    def __init__(self):
        self.stop_flag = False
        self.args = Namespace(n=10, max=None, verbose=False)

    def parse_args(self, argv=None):
        """Parse command line args."""
        self.args = self.parser.parse_args(argv)

        random.seed(self.args.seed)

        if self.args.script is None:
            self.script_dict = {}
        else:
            self.script_dict = runpy.run_path(self.args.script)

        self.given_funcs = [
            (name, signature_str, self.verbose_get(name, body))
            for name, signature_str, body in self.func_defaults]
        self.predeal = {
            global_defs.Seat[seat_name]: hand
            for seat_name, hand in self.verbose_get("predeal", {}).items()}
        for seat in global_defs.Seat:
            try:
                hand = getattr(self.args, seat.name)
            except AttributeError:
                continue
            self.predeal[seat] = redeal.H(hand)

    _obj = object()

    def verbose_get(self, attr, default=_obj):
        """
        Try to get an attribute:

        Query `self.args` first, then `self.globals`, then uses `default`;
        report if `self.verbose is set`.
        """
        try:
            value = getattr(self.args, attr)
        except AttributeError:
            try:
                value = self.script_dict[attr]
            except KeyError:
                if default is not self._obj:
                    if self.args.verbose:
                        print(f"Using default for {attr}.")
                    return default
                else:
                    raise
        return value

    def generate(self, simulation):
        """Repeatedly generate and process deals until enough are accepted."""
        found = 0
        dealer = redeal.Deal.prepare(self.predeal)
        try:
            inspect.signature(simulation.initial).bind(dealer)
        except TypeError:
            simulation.initial()
        else:
            simulation.initial(dealer)
        for i in range(self.args.max or 1000 * self.args.n):
            if self.stop_flag:
                break
            deal = dealer()
            if simulation.accept(deal):
                found += 1
                simulation.do(deal)
                if self.args.verbose:
                    progress = ("(hand #{}, found after {} tries)".
                                format(found, i + 1))
                    print(progress, end="\r", flush=True)
                    print(" " * len(progress) + "\b" * len(progress), end="")
            if found >= self.args.n:
                break
        print()
        simulation.final(i + 1)

    def run(self):
        """Start a GUI or run a simulation."""
        if self.args.gui:
            gui.run_gui(self)
        else:
            try:
                simulation = self.verbose_get("simulation")
            except LookupError:
                simulation = type(
                    str(), (redeal.Simulation,),
                    {name: util.create_func(redeal, name, signature_str, body)
                     for name, signature_str, body in self.given_funcs})()
            redeal.Hand.set_str_style(self.args.format)
            redeal.Deal.set_str_style(self.args.format)
            redeal.Deal.set_print_only(
                [global_defs.Seat[seat] for seat in self.args.only])
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
