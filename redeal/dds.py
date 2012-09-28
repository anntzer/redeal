# vim: set fileencoding=utf-8
from __future__ import division, print_function
# for pypy compatibility we do not use unicode_literals in this module
from ctypes import *
from os import path

from .globals import *


class _Board(Structure):
    """The deal struct."""

    STRAINS = list("SHDCN")
    SEATS = list("NESW")

    _fields_ = [("trump", c_int), # 0=S, 1=H, 2=D, 3=C, 4=NT
                ("first", c_int), # leader: 0=N, 1=E, 2=S, 3=W
                ("currentTrickSuit", c_int * 3),
                ("currentTrickRank", c_int * 3), # 2-14, up to 3 cards; 0=unplayed
                # remaincards[hand][suit] is a bit-array (2->2^2, ..., A->2^14)
                ("remaincards", c_uint * 4 * 4)]

    @classmethod
    def from_deal(cls, deal, strain, leader):
        self = cls(trump=STRAINS.index(strain.upper()),
                   first=SEATS.index(leader.upper()),
                   currentTrickSuit=(c_int * 3)(0, 0, 0),
                   currentTrickRank=(c_int * 3)(0, 0, 0))
        # bit #i (2 ≤ i ≤ 14) is set if card of rank i (A = 14) is held
        for seat, hand in enumerate(deal):
            for suit, holding in enumerate(hand):
                self.remaincards[seat][suit] = sum(1 << (PER_SUIT + 1 - rank)
                                                   for rank in holding)
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
    -14: "Wrong number of remaining cards in a hand."}


def solve_board(deal, strain, declarer):
    """Wrapper for SolveBoard.  Return the number of tricks for declarer."""
    leader = SEATS[(SEATS.index(declarer.upper()) + 1) % N_SUITS]
    _board = _Board.from_deal(deal, strain, leader)
    _futp = _FutureTricks()
    # find one optimal card with its score, even if only one card
    status = dll.SolveBoard(_board, -1, 1, 1, byref(_futp))
    if status != 1:
        raise Exception("SolveBoard failed with status {} ({}).".
                        format(status, SolveBoardStatus[status]))
    best_score = PER_SUIT - _futp.score[0]
    return best_score


dll = CDLL(path.join(path.dirname(__file__), "dds-1.1.15/libdds.so.1.1.15"))
dll.InitStart.argtypes = [c_int, c_int]
dll.SolveBoard.argtypes = [_Board, c_int, c_int, c_int, POINTER(_FutureTricks)]
dll.InitStart(0, 0)
