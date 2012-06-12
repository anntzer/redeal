# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from collections import namedtuple as _namedtuple
from itertools import product as _product


SEATS = list("NESW")
SUITS = list("SHDC")
STRAINS = SUITS + ["N"]
SUITS_SYM = list("♠♡♢♣")
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

