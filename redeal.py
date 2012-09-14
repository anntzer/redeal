#!/usr/bin/env python
# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from argparse import ArgumentParser
from array import array
from bisect import bisect
from functools import reduce
import imp
from itertools import permutations, product
from os import path
import random

from globals import *
from mutable import ref
from util import reify
try:
    from dds import solve_board
except OSError:
    def solve_board(deal, strain, declarer):
        raise Exception("Unable to load DDS.  `solve_board` is unavailable.")
from smartstack import SmartStack, _SmartStack


__all__ = ["solve_board", "Shape", "balanced", "semibalanced",
           "Deal", "Hand", "Holding", "Contract", "SmartStack", "H", "C",
           "defvector", "matchpoints", "imps",
           "RANKS"]


class Shape(object):
    """A shape specification, as a 0-1 table, intended as immutable.
    
    {min,max}_ls are hints for smartstacking, guaranteed to be correct but not
    necessarily optimal. _cls_cache and _op_cache cache Shape instantiations
    and additions/substractions -- useful if the accept function is given as a
    lambda form, for example.
    """

    JOKER = "x"
    TABLE = {JOKER: -1, "t": 10, "j": 11, "q": 12, "k": 13, "(": "(", ")": ")"}
    TABLE.update({str(n): n for n in range(10)})
    _cls_cache = {}

    def __new__(cls, init=None):
        """Initialize with a string."""
        try:
            return cls._cls_cache[init]
        except KeyError:
            self = object.__new__(cls)
            self.table = array(str("b"))
            self.table.fromlist([0] * (PER_SUIT + 1) ** N_SUITS)
            self.min_ls = [PER_SUIT for _ in range(N_SUITS)]
            self.max_ls = [0 for _ in range(N_SUITS)]
            self._op_cache = {}
            if init:
                self.insert([self.TABLE[char.lower()] for char in init])
                cls._cls_cache[init] = self
            return self

    @classmethod
    def from_table(cls, table, min_max_hint=None):
        """Initialize from a table."""
        self = cls()
        self.table = array(str("b"))
        self.table.fromlist(list(table))
        if min_max_hint is not None:
            self.min_ls, self.max_ls = min_max_hint
        else:
            self.min_ls = [PER_SUIT for _ in range(N_SUITS)]
            self.max_ls = [0 for _ in range(N_SUITS)]
            for nonflat in product(*[range(PER_SUIT + 1)
                                     for _ in range(N_SUITS)]):
                if self.table[self.flatten(nonflat)]:
                    for dim, coord in enumerate(nonflat):
                        self.min_ls[dim] = min(self.min_ls[dim], coord)
                        self.max_ls[dim] = max(self.max_ls[dim], coord)
        return self

    @classmethod
    def from_cond(cls, func):
        self = cls()
        for nonflat in product(*[range(PER_SUIT + 1)
                                 for _ in range(N_SUITS)]):
            if sum(nonflat) == PER_SUIT and func(*nonflat):
                self.table[self.flatten(nonflat)] = True
                for dim, coord in enumerate(nonflat):
                    self.min_ls[dim] = min(self.min_ls[dim], coord)
                    self.max_ls[dim] = max(self.max_ls[dim], coord)
        return self

    @staticmethod
    def flatten(index):
        s, h, d, c = index
        mul = PER_SUIT + 1
        return ((((s * mul + h) * mul) + d) * mul) + c

    def insert1(self, shape, safe=True):
        """Insert an element, possibly with "x" but no "()" terms."""
        jokers = any(l == -1 for l in shape)
        pre_set = sum(l for l in shape if l >= 0)
        if not jokers:
            if pre_set == PER_SUIT:
                self.table[self.flatten(shape)] = 1
                for suit in range(N_SUITS):
                    self.min_ls[suit] = min(self.min_ls[suit], shape[suit])
                    self.max_ls[suit] = max(self.max_ls[suit], shape[suit])
            elif safe:
                raise Exception("Wrong number of cards in shape.")
        else:
            if pre_set > PER_SUIT:
                raise Exception("Invalid ambiguous shape.")
            for i, l in enumerate(shape):
                if l == -1:
                    for ll in range(PER_SUIT - pre_set + 1):
                        self.insert1(shape[:i] + (ll,) + shape[i+1:],
                                     safe=False)

    def insert(self, it, acc=()):
        """Insert an element, possibly with "()" or "x" terms."""
        if not it:
            self.insert1(acc, safe=False)
            return
        if it[0] == "(":
            try:
                closing = it.index(")")
            except ValueError:
                raise Exception("Unbalanced parentheses.")
            head, it = it[1:closing], it[closing+1:]
        else:
            head, it = it[0:1], it[1:]
        for perm in permutations(head):
            self.insert(it, acc + perm)

    def __contains__(self, int_shape):
        return self.table[self.flatten(int_shape)]

    def __call__(self, hand):
        return hand.shape in self

    def __add__(self, other):
        try:
            return self._op_cache["+", other]
        except KeyError:
            table = array(str("b"))
            table.fromlist([x or y for x, y in zip(self.table, other.table)])
            min_ls = [min(self.min_ls[suit], other.min_ls[suit])
                      for suit in range(N_SUITS)]
            max_ls = [max(self.max_ls[suit], other.max_ls[suit])
                      for suit in range(N_SUITS)]
            result = Shape.from_table(table, (min_ls, max_ls))
            self._op_cache["+", other] = result
            return result

    def __sub__(self, other):
        try:
            return self._op_cache["-", other]
        except KeyError:
            table = array("b")
            table.fromlist([x and not y for x, y in zip(self.table, other.table)])
            result = Shape.from_table(table, (self.min_ls, self.max_ls))
            self._op_cache["-", other] = result
            return result


balanced = Shape("(4333)") + Shape("(4432)") + Shape("(5332)")
semibalanced = balanced + Shape("(5422)") + Shape("(6322)")


class Deal(tuple, object):
    """A deal, represented as a tuple of hands."""

    @staticmethod
    def prepare(predeal):
        """Prepare a seat -> [Hand | SmartStack] map into a dealer.
        
        There can be at most one SmartStack entry.
        """
        predeal = predeal or {}
        smartstacks = [(k, v) for k, v in predeal.items()
                       if isinstance(v, SmartStack)]
        predeal = {seat: getattr(predeal.get(seat), "cards", lambda: [])
                   for seat in SEATS}
        predealt = reduce(list.__add__, (predeal[seat]() for seat in SEATS), [])
        predealt_set = set(predealt)
        if len(predealt_set) < len(predealt):
            raise Exception("Same card dealt twice.")
        if smartstacks:
            try:
                (seat, smartstack), = smartstacks
            except ValueError:
                raise Exception("Only one SmartStack allowed.")
            predealt_by_suit = {
                suit: {card.rank for card in predealt_set if card.suit == suit}
                for suit in range(N_SUITS)}
            predeal[seat] = _SmartStack.from_predealt(smartstack,
                                                      predealt_by_suit)
        predeal["_remaining"] = [card for card in FULL_DECK
                                 if card not in predealt_set]
        return predeal

    def __new__(cls, dealer):
        """Randomly deal a hand from a prepared dealer."""
        cards = dealer["_remaining"]
        random.shuffle(cards)
        hands = []
        for seat in SEATS:
            pre = dealer[seat]()
            to_deal = PER_SUIT - len(pre)
            hand, cards = pre + cards[:to_deal], cards[to_deal:]
            hands.append(Hand(hand))
        return tuple.__new__(cls, hands)

    def __str__(self):
        return " ".join(map(str, self))

    def __unicode__(self):
        return " ".join(map(unicode, self))

    @property
    def _long_str(self):
        """A pretty-printed version of the deal."""
        s = ""
        for line in self.north._long_str.split("\n"):
            s += " " * 7 + line + "\n"
        for line_w, line_e in zip(self.west._long_str.split("\n"),
                                  self.east._long_str.split("\n")):
            s += line_w.ljust(14) + line_e + "\n"
        for line in self.south._long_str.split("\n"):
            s += " " * 7 + line + "\n"
        return s

    _N = SEATS.index("N")
    @property
    def north(self):
        return self[self._N]

    _E = SEATS.index("E")
    @property
    def east(self):
        return self[self._E]

    _S = SEATS.index("S")
    @property
    def south(self):
        return self[self._S]

    _W = SEATS.index("W")
    @property
    def west(self):
        return self[self._W]

    @property
    def _bits(self):
        return [hand._bits for hand in self]


class Hand(tuple, object):
    """A hand, represented as a tuple of holdings."""

    def __new__(cls, cards):
        """Initialize with a list of cards, or with another hand."""
        return tuple.__new__(
            cls,
            (Holding(card for card in cards if card.suit == suit)
             for suit in range(N_SUITS)))

    @classmethod
    def from_str(cls, init):
        """Initialize with a string, e.g. "AK432 K87 QJT54 -"."""
        suits = [holding if holding != "-" else "" for holding in init.split()]
        if (len(suits) != N_SUITS or
            not all(rank in RANKS for holding in suits for rank in holding)):
            raise Exception("Invalid initializer for Hand.")
        cards = [Card(suit=suit, rank=RANKS.index(rank.upper()))
                 for suit, holding in enumerate(suits) for rank in holding]
        return cls(cards)

    def __str__(self):
        return "".join(suit_symbol + str(holding)
                       for suit_symbol, holding in zip(SUITS_SYM, self))

    @property
    def _long_str(self):
        """Return a pretty-printed version of the hand."""
        return "\n" + "\n".join(suit_symbol + str(holding)
            for suit_symbol, holding in zip(SUITS_SYM, self))

    def cards(self):
        """Return self as a list of card objects."""
        return [Card(suit, rank)
                for suit in range(N_SUITS) for rank in self[suit]]

    _S = SUITS.index("S")
    @reify
    def spades(self):
        return self[self._S]

    _H = SUITS.index("H")
    @reify
    def hearts(self):
        return self[self._H]

    _D = SUITS.index("D")
    @reify
    def diamonds(self):
        return self[self._D]

    _C = SUITS.index("C")
    @reify
    def clubs(self):
        return self[self._C]

    @reify
    def shape(self):
        return list(map(len, self))

    @reify
    def hcp(self):
        return sum(holding.hcp for holding in self)

    @reify
    def losers(self):
        return sum(holding.losers for holding in self)

    @reify
    def _bits(self):
        return [holding._bits for holding in self]


class Holding(frozenset, object):
    """A one-suit holding, represented as a frozenset of card ranks."""

    def __new__(cls, cards):
        return frozenset.__new__(cls, (card.rank for card in cards))

    def __str__(self):
        return "".join(RANKS[rank] for rank in sorted(self))

    @reify
    def hcp(self):
        return sum(HCP[rank] for rank in self)

    _A, _K, _Q, _J, _T = [RANKS.index(rank) for rank in "AKQJT"]
    @reify
    def losers(self):
        if len(self) == 0:
            return 0
        losers = 0
        if not any(rank == self._A for rank in self):
            losers += 1
        if len(self) >= 2 and not any(rank == self._K for rank in self):
            losers += 1
        if len(self) >= 3:
            if not any(rank == self._Q for rank in self):
                losers += 1
            elif (losers == 2 and
                  not any(rank in [self._J, self._T] for rank in self)):
                losers += 0.5
        return losers

    @reify
    def _bits(self):
        """Used for DDS interop."""
        # bit #i (0 ≤ i ≤ 12) is set if card of rank i+2 (A = 14) is held
        return sum(1 << (PER_SUIT - 1 - rank) for rank in self)


class Contract(object):
    def __init__(self, level, strain, doubled=0, vul=False):
        self.level = level
        self.strain = strain
        self.doubled = doubled
        self.vul = vul

    @classmethod
    def from_str(cls, s, vul=False):
        """Initialize with a string, e.g. "7NXX".  Vulnerability still a kwarg.
        """
        doubled = len(s) - len(s.lstrip("xX"))
        return cls(int(s[0]), s[1].upper(), doubled=doubled, vul=vul)

    def score(self, tricks):
        """Score for a contract for a given number of tricks taken."""
        target = self.level + 6
        overtricks = tricks - target
        if overtricks >= 0:
            per_trick = 20 if self.strain in ["C", "D"] else 30
            base_score = per_trick * self.level
            bonus = 0
            if self.strain == "N":
                base_score += 10
            if self.doubled == 1:
                base_score *= 2
                bonus += 50
            if self.doubled == 2:
                base_score *= 4
                bonus += 100
            bonus += [300, 500][self.vul] if base_score >= 100 else 50
            if self.level == 6:
                bonus += [500, 750][self.vul]
            elif self.level == 7:
                bonus += [1000, 1500][self.vul]
            if not self.doubled:
                per_overtrick = per_trick
            else:
                per_overtrick = [100, 200][self.vul] * self.doubled
            overtricks_score = overtricks * per_overtrick
            return base_score + overtricks_score + bonus
        else:
            if not self.doubled:
                per_undertrick = [50, 100][self.vul]
                return overtricks * per_undertrick
            else:
                if overtricks == -1:
                    score = [-100, -200][self.vul]
                elif overtricks == -2:
                    score = [-300, -500][self.vul]
                else:
                    score = -300 * overtricks + [400, 100][self.vul]
            if self.doubled == 2:
                score *= 2
            return score


H = Hand.from_str
C = Contract.from_str


def defvector(*vals):
    """Additive holding evaluator.
    
    For example, `defvector(4, 3, 2, 1)(holding)` returns the HCPs of
    `holding`.
    """
    return lambda holding: sum(val for rank, val in enumerate(vals)
                               if any(rank_ == rank for rank_ in holding))


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


def matchpoints(my, other):
    return (1 + (my > other) - (my < other)) / 2


def imps(my, other):
    imp_table = [15, 45, 85, 125, 165, 215, 265, 315, 365, 425, 495, 595,
        745, 895, 1095, 1295, 1495, 1745, 1995, 2245, 2495, 2995, 3495, 3995]
    return bisect(imp_table, abs(my - other)) * (1 if my > other else -1)


if __name__ == "__main__":
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
