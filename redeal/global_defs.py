# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from collections import namedtuple as _namedtuple

from enum import Enum as _Enum
import itertools as _itertools
import sys as _sys


__author__ = "Antony Lee"
__version__ = "0.2"
__fullname__ = "redeal v. {}".format(__version__)
__copyright__ = "{}, (c) {}".format(__fullname__, __author__)


Seat = _Enum("Seat", zip("NESW", range(4)))
Seat.N._s, Seat.E._s, Seat.S._s, Seat.W._s = (
    "North", "East", "South", "West")
Seat.__str__ = lambda self: self._s
Seat.__index__ = lambda self: self.value
Seat.__add__ = lambda self, val: Seat((self.value + val) % len(Seat))


class Suit(_Enum):
    S = 0, " S", "♠"
    H = 1, " H", "♡"
    D = 2, " D", "♢"
    C = 3, " C", "♣"

    def __init__(self, value, sym, unicode_sym):
        self._value_ = value
        self._sym = (unicode_sym
                     if _sys.version_info > (3,) and
                        _sys.stdout.encoding.lower() == "utf-8"
                     else sym)
        self._unicode_sym = unicode_sym

    __str__ = lambda self: (
        self._unicode_sym if SUITS_FORCE_UNICODE else self._sym)
    __index__ = lambda self: self.value
    # Yes, the order is reversed.
    __lt__ = lambda self, other: self.value > other.value
    __le__ = lambda self, other: self.value >= other.value
    __gt__ = lambda self, other: self.value < other.value
    __ge__ = lambda self, other: self.value <= other.value


SUITS_FORCE_UNICODE = False


Strain = _Enum("Strain", zip("CDHSN", range(5)))
Strain.__str__ = lambda self: self.name
Strain.__lt__ = lambda self, other: self.value < other.value
Strain.__le__ = lambda self, other: self.value <= other.value
Strain.__gt__ = lambda self, other: self.value > other.value
Strain.__ge__ = lambda self, other: self.value >= other.value


Rank = _Enum("Rank", zip("23456789TJQKA", range(2, 15)))
Rank.__str__ = lambda self: self.name
Rank.__index__ = lambda self: self.value - 2
Rank.__lt__ = lambda self, other: self.value < other.value
Rank.__le__ = lambda self, other: self.value <= other.value
Rank.__gt__ = lambda self, other: self.value > other.value
Rank.__ge__ = lambda self, other: self.value >= other.value


Card = _namedtuple("Card", ["suit", "rank"])
Card.from_str = lambda s: Card(Suit[s[0]], Rank[s[1]])
Card.__str__ = lambda self: "{0.suit}{0.rank}".format(self)
Card.__format__ = lambda self, fmt: format(str(self), fmt)
FULL_DECK = {Card(suit=suit, rank=rank)
             for suit, rank in _itertools.product(Suit, Rank)}
