# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from collections import namedtuple as _namedtuple
from itertools import product as _product
import sys as _sys


__author__ = "Antony Lee"
__version__ = "0.2"
__fullname__ = "redeal v. {}".format(__version__)
__copyright__ = "{}, (c) {}".format(__fullname__, __author__)

SEATS = list("NESW")
LONG_SEATS = ["North", "South", "East", "West"]
SUITS = list("SHDC")
STRAINS = SUITS + ["N"]
SUITS_SYM_UNICODE = list("♠♡♢♣")
SUITS_SYM = (list("♠♡♢♣") if _sys.getdefaultencoding() == "utf-8"
             else [" S", " H", " D", " C"])
N_SUITS = len(SUITS)
RANKS = list("AKQJT98765432")
HCP = list(map(int, "4321000000000"))
PER_SUIT = 13
Card = _namedtuple("Card", ["suit", "rank"])
Card.from_str = lambda s: Card(SUITS.index(s[0].upper()),
                               RANKS.index(s[1].upper()))
Card.__str__ = lambda self: SUITS_SYM[self.suit] + RANKS[self.rank]
FULL_DECK = {Card(suit=suit, rank=rank)
             for suit, rank in _product(range(N_SUITS), range(PER_SUIT))}

