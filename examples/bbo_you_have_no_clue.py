# vim: set fileencoding=utf-8
from __future__ import division

from collections import Counter
from redeal import *


predeal = {"S": H("T8 8762 KT4 KQ52")}


def initial():
    global TABLE
    TABLE = [[Counter() for _ in range(3)] for _ in range(3)]


def accept(deal):
    return 15 <= deal.north.hcp <= 17 and balanced(deal.north)


def do(deal):
    nttricks = solve_board(deal, "N", "N")
    pass1N = C("1N", True).score(nttricks)
    if len(deal.north.hearts) < 4:
        if deal.north.hcp >= 17:
            s17 = C("3N", True).score(nttricks)
        else:
            s17 = C("2N", True).score(nttricks)
    else:
        hetricks = solve_board(deal, "H", "N")
        if deal.north.hcp >= 17:
            s17 = C("4H", True).score(hetricks)
        else:
            s17 = C("3H", True).score(hetricks)
    if len(deal.north.hearts) < 4:
        if deal.north.hcp >= 16:
            s16 = C("3N", True).score(nttricks)
        else:
            s16 = C("2N", True).score(nttricks)
    else:
        hetricks = solve_board(deal, "H", "N")
        if deal.north.hcp >= 16:
            s16 = C("4H", True).score(hetricks)
        else:
            s16 = C("3H", True).score(hetricks)
    scores = [pass1N, s16, s17]
    print("{} {}".format(deal, " ".join(map(str, scores))))
    for i, scorei in enumerate(scores):
        for j, scorej in enumerate(scores):
            TABLE[i][j][imps(scorei, scorej)] += 1


def final(n_tries):
    for line in TABLE:
        print("\t".join(str(sum(list(counter.elements())) /
                            len(list(counter.elements())))
                        for counter in line))
    print("Tries: {}".format(n_tries))
