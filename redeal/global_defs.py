from collections import namedtuple
import enum
from enum import Enum, Flag
import functools
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
        self._sym = (
            unicode_sym if sys.stdout.encoding.lower() == "utf-8" else sym)
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


Rank = Flag("Rank", list("23456789TJQKA"))
Rank.__str__ = functools.lru_cache()(
    lambda self: "".join(rank.name for rank in reversed(Rank) if self & rank))
Rank.__index__ = lambda self: self.value.bit_length() - 1
Rank.__lt__ = lambda self, other: self.value < other.value
Rank.__le__ = lambda self, other: self.value <= other.value
Rank.__gt__ = lambda self, other: self.value > other.value
Rank.__ge__ = lambda self, other: self.value >= other.value
Rank.__len__ = lambda self: sum(c == 1 for c in bin(self.value))


Card = namedtuple("Card", ["suit", "rank"])
Card.from_str = lambda s: Card(Suit[s[0]], Rank[s[1]])
Card.__str__ = lambda self: "{0.suit}{0.rank}".format(self)
Card.__format__ = lambda self, fmt: format(str(self), fmt)
FULL_DECK = {Card(suit=suit, rank=rank)
             for suit, rank in itertools.product(Suit, Rank)}


if sys.version_info < (3, 9):

    def _decompose(flag, value):  # bpo-38045, minus IntFlag handling.
        """Extract all members from the value."""
        # _decompose is only called if the value is not named
        not_covered = value
        members = []
        for member in flag:
            member_value = member.value
            if member_value and member_value & value == member_value:
                members.append(member)
                not_covered &= ~member_value
        if not members and value in flag._value2member_map_:
            members.append(flag._value2member_map_[value])
        members.sort(key=lambda m: m._value_, reverse=True)
        if len(members) > 1 and members[0].value == value:
            # we have the breakdown, don't need the value member itself
            members.pop(0)
        return members, not_covered

    enum._decompose = _decompose
