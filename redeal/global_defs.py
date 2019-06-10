# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from collections import namedtuple

from enum import Enum
import itertools
import sys


Seat = Enum("Seat", zip("NESW", range(4)))
Seat.N._s, Seat.E._s, Seat.S._s, Seat.W._s = (
    "North", "East", "South", "West")
Seat.__str__ = lambda self: self._s
Seat.__index__ = lambda self: self.value
Seat.__add__ = lambda self, val: Seat((self.value + val) % len(Seat))


class Suit(Enum):
    S = 0, " S", "♠"
    H = 1, " H", "♡"
    D = 2, " D", "♢"
    C = 3, " C", "♣"

    def __init__(self, value, sym, unicode_sym):
        self._value_ = value
        self._sym = (unicode_sym
                     if (sys.version_info > (3,)
                         and sys.stdout.encoding.lower() == "utf-8")
                     else sym)
        self._unicode_sym = unicode_sym

    def __str__(self):
        return self._unicode_sym if SUITS_FORCE_UNICODE else self._sym

    def __index__(self): return self.value
    # Yes, the order is reversed.
    def __lt__(self, other): return self.value > other.value
    def __le__(self, other): return self.value >= other.value
    def __gt__(self, other): return self.value < other.value
    def __ge__(self, other): return self.value <= other.value


SUITS_FORCE_UNICODE = False


Strain = Enum("Strain", zip("CDHSN", range(5)))
Strain.__str__ = lambda self: self.name
Strain.__lt__ = lambda self, other: self.value < other.value
Strain.__le__ = lambda self, other: self.value <= other.value
Strain.__gt__ = lambda self, other: self.value > other.value
Strain.__ge__ = lambda self, other: self.value >= other.value


Rank = Enum("Rank", zip("23456789TJQKA", range(2, 15)))
Rank.__str__ = lambda self: self.name
Rank.__index__ = lambda self: self.value - 2
Rank.__lt__ = lambda self, other: self.value < other.value
Rank.__le__ = lambda self, other: self.value <= other.value
Rank.__gt__ = lambda self, other: self.value > other.value
Rank.__ge__ = lambda self, other: self.value >= other.value


Card = namedtuple("Card", ["suit", "rank"])
Card.from_str = lambda s: Card(Suit[s[0]], Rank[s[1]])
Card.__str__ = lambda self: "{0.suit}{0.rank}".format(self)
Card.__format__ = lambda self, fmt: format(str(self), fmt)
FULL_DECK = {Card(suit=suit, rank=rank)
             for suit, rank in itertools.product(Suit, Rank)}
