# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from ctypes import *
from globals import *


dll = CDLL("dds-1.1.9/libdds.so.1.1.9")
dll.DDSInitStart()


holding_t = c_ushort


class _Deal(Structure):
    """The diagram struct."""

    # cards[hand][suit] is a bit-array (2->2^0, ..., A->2^12)
    # the mapping seems to have been modified in later versions of dds.
    _fields_ = [("cards", holding_t * 4 * 4)]

    @classmethod
    def from_deal(cls, deal):
        self = cls()
        for i, hand in enumerate(deal._deal):
            for j, holding in enumerate(hand):
                self.cards[i][j] = holding
        return self


class _Board(Structure):
    """The deal struct."""

    STRAINS = list("SHDCN")
    SEATS = list("NESW")

    _fields_ = [("trump", c_int), # 0=S, 1=H, 2=D, 3=C, 4=NT
                ("first", c_int), # leader: 0=N, 1=E, 2=S, 3=W
                ("currentTrickSuit", c_int * 3),
                ("currentTrickRank", c_int * 3), # 2-14, up to 3 cards; 0=unplayed
                ("remaining", _Deal)]

    @classmethod
    def from_deal(cls, deal, strain, leader):
        self = cls(STRAINS.index(strain.upper()), SEATS.index(leader.upper()),
                   (c_int * 3)(0, 0, 0), (c_int * 3)(0, 0, 0),
                   _Deal.from_deal(deal))
        return self


class _FutureTricks(Structure):
    """The futureTricks struct."""

    _fields_ = [("nodes", c_int),
                ("cards", c_int),
                ("suit", c_int * 13),
                ("rank", c_int * 13),
                ("equals", c_int * 13),
                ("score", c_int * 13)]


SolveBoardStatus = {
    1: "No fault",
    -1: "Unknown fault",
    -2: "Zero cards",
    -3: "Target > tricks left",
    -4: "Duplicated cards",
    -5: "Target < -1",
    -7: "Target > 13",
    -8: "Solutions < 1",
    -9: "Solutions > 3",
    -10: "> 52 cards",
    -12: "Invalid deal.currentTrick{Suit,Rank}",
    -13: "Card played in current trick is also remaining",
    -14: "Wrong number of remaining cards in a hand.",
    -15: "threadIndex < 0 or > 15"}


def solve_board(deal, strain, declarer):
    """Wrapper for SolveBoard.  Return the number of tricks for declarer."""
    leader = SEATS[(SEATS.index(declarer) + 1) % N_SUITS]
    _board = _Board.from_deal(deal, strain, leader)
    _futp = _FutureTricks()
    # find one optimal card with its score, even if only one card
    status = dll.SolveBoard(_board, -1, 1, 1, byref(_futp))
    if status != 1:
        raise Exception("SolveBoard failed with status {} ({}).".
                        format(status, SolveBoardStatus[status]))
    best_score = PER_SUIT - _futp.score[0]
    return best_score

