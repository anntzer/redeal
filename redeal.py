#!/usr/bin/env python
# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from argparse import ArgumentParser
from array import array
from bisect import bisect
from functools import reduce
from importlib import import_module
from itertools import permutations
import random

from dds import solve_board
from globals import *
from util import Immutable, reify


class Shape(object):
    """A shape specification, represented as a 0-1 table."""

    JOKER = "x"
    TABLE = {JOKER: -1, "t": 10, "j": 11, "q": 12, "k": 13, "(": "(", ")": ")"}
    TABLE.update({str(n): n for n in range(2, 10)})

    def __init__(self, init=None):
        """Initialize with a string."""
        self.table = array(str("b"))
        self.table.fromlist([0] * (PER_SUIT + 1) ** N_SUITS)
        if init:
            self.insert([self.TABLE[char.lower()] for char in init])

    @classmethod
    def from_table(cls, table):
        """Initialize from a table."""
        self = cls()
        self.table = array(str("b"))
        self.table.fromlist(list(table))
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

    def __add__(self, other):
        table = array(str("b"))
        table.fromlist([x or y for x, y in zip(self.table, other.table)])
        return Shape.from_table(table)

    def __sub__(self, other):
        table = array("b")
        table.fromlist([x and not y for x, y in zip(self.table, other.table)])
        return Shape.from_table(table)


Balanced = Shape("(4333)") + Shape("(4432)") + Shape("(5332)")
SemiBalanced = Balanced + Shape("(5422)") + Shape("(6322)")


class Deal(object):
    """A deal, represented as a list of cards."""

    def __init__(self, predeal=None):
        """Randomly deal a hand, with map of predealt cards."""
        predeal = predeal or {}
        for seat in SEATS:
            predeal.setdefault(seat, [])
        predeal = {SEATS.index(seat.upper()): list(pre)
                   for seat, pre in predeal.items()}
        predealt_cards = reduce(list.__add__, predeal.values())
        predealt_set = set(predealt_cards)
        if len(predealt_set) < len(predealt_cards):
            raise Exception("Same card dealt twice.")
        cards = [card for card in FULL_DECK if card not in predealt_set]
        random.shuffle(cards)
        self.hands = [None] * N_SUITS
        for seat, pre in predeal.items():
            to_deal = PER_SUIT - len(pre)
            hand, cards = pre + cards[:to_deal], cards[to_deal:]
            self.hands[seat] = Hand(hand)

    def __str__(self):
        return " ".join(map(str, self.hands))

    def __unicode__(self):
        return " ".join(map(unicode, self.hands))

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

    @property
    def north(self):
        return self.hands[SEATS.index("N")]

    @property
    def east(self):
        return self.hands[SEATS.index("E")]

    @property
    def south(self):
        return self.hands[SEATS.index("S")]

    @property
    def west(self):
        return self.hands[SEATS.index("W")]

    @property
    def _deal(self):
        return [hand._bits for hand in self.hands]


class Hand(Immutable):
    """A hand, represented as a list of cards."""

    def __init__(self, cards):
        """Initialize with a list of cards."""
        cards = sorted(cards)
        object.__setattr__(self, "cards", tuple(cards))

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
        return "".join(
            suit_symbol +
            "".join(RANKS[card.rank] for card in self.cards if card.suit == suit)
            for suit, suit_symbol in enumerate(SUITS_SYM))

    @property
    def _long_str(self):
        """A pretty-printed version of the hand."""
        return "\n" + "\n".join(
            suit_symbol +
            "".join(RANKS[card.rank] for card in self.cards if card.suit == suit)
            for suit, suit_symbol in enumerate(SUITS_SYM))

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    @reify
    def spades(self):
        return type(self)([c for c in self.cards if c.suit == 0])

    @reify
    def hearts(self):
        return type(self)([c for c in self.cards if c.suit == 1])

    @reify
    def diamonds(self):
        return type(self)([c for c in self.cards if c.suit == 2])

    @reify
    def clubs(self):
        return type(self)([c for c in self.cards if c.suit == 3])

    @reify
    def shape(self):
        return [len([c for c in self.cards if c.suit == suit])
                for suit in range(N_SUITS)]

    @reify
    def hcp(self):
        return sum(HCP[c.rank] for c in self.cards)

    @reify
    def _bits(self):
        """Used for dds interop."""
        # bit #i (0<=i<=12) set if card i+2 held
        return [sum(1 << (PER_SUIT - 1 - rank) for rank in range(PER_SUIT)
                    if (suit, rank) in self.cards)
                for suit in range(N_SUITS)]


class Contract:
    def __init__(self, level, strain, doubled=0, vul=False):
        self.level = level
        self.strain = strain
        self.doubled = doubled
        self.vul = vul

    @classmethod
    def from_str(cls, s, vul=False):
        """Initialize with a string, e.g. "7NXX".  Vulnerability still a kwarg.
        """
        s = s.upper()
        if s.endswith("XX"):
            doubled = 2
        elif s.endswith("X"):
            doubled = 1
        else:
            doubled = 0
        return cls(int(s[0]), s[1], doubled=doubled, vul=vul)

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


def generate(n_hands, max_tries, predeal, accept):
    """Repeatedly pass hands to an `accept` function until enough are accepted.
    """
    found = 0
    for i in range(max_tries):
        deal = Deal(predeal)
        if accept(found, deal):
            found += 1
        if found >= n_hands:
            break
    return i + 1


def matchpoint(my, other):
    return (1 + (my > other) - (my < other)) / 2


def imp(my, other):
    imp_table = [15, 45, 85, 125, 165, 215, 265, 315, 365, 425, 495, 595,
        745, 895, 1095, 1295, 1495, 1745, 1995, 2245, 2495, 2995, 3495, 3995]
    return bisect(imp_table, abs(my - other)) * (1 if my > other else -1)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="A reimplementation of Thomas Andrews' Deal in Python.",
        epilog="See script.py for an example")
    parser.add_argument("-n", type=int, default=10,
        help="the number of requested hands")
    parser.add_argument("-N", type=int,
        help="the maximum number of tries (defaults to 1000×n)")
    parser.add_argument("script", nargs="?",
        help="module that can be imported as `import module` (without `.py`)")
    parser.add_argument("-l", action="store_true",
        help="long output for diagrams")
    parser.add_argument("-v", action="store_true",
        help="be verbose")
    args = parser.parse_args()
    if args.N is None:
        args.N = 1000 * args.n
    module = import_module(args.script) if args.script else None

    def verbose_getattr(attr, default):
        if hasattr(module, attr):
            return getattr(module, attr)
        else:
            if args.v:
                print("Using default for {}.".format(attr))
            return default
    initial = verbose_getattr("initial", lambda: None)
    predeal = verbose_getattr("predeal", {})
    accept = verbose_getattr("accept",
                             lambda found, deal: print(str(deal)) or True)
    final = verbose_getattr("final", lambda tries: None)
    n_hands = args.n
    max_tries = args.N
    if args.l:
        Deal.__str__ = lambda self: self._long_str
        Deal.__unicode__ = lambda self: self._long_str

    initial()
    tries = generate(n_hands, max_tries, predeal, accept)
    final(tries)

