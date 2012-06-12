# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from collections import Counter
from redeal import *


predeal = {"S": H("T8 8762 KT4 KQ52")}


def accept(found, deal):
    global TABLE
    if not (15 <= deal.north.hcp <= 17 and deal.north.shape in Balanced):
        return False
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
    print("{}: {} {}".format(found + 1, deal, " ".join(map(str, scores))))
    global TABLE
    try:
        TABLE
    except NameError:
        TABLE = [[Counter() for _ in scores] for _ in scores]
    for i, scorei in enumerate(scores):
        for j, scorej in enumerate(scores):
            TABLE[i][j][imps(scorei, scorej)] += 1
    return True


def final(n_tries):
    global TABLE
    for line in TABLE:
        print("\t".join(str(sum(list(counter.elements())) /
                            len(list(counter.elements())))
                        for counter in line))
    print("Tries: {}".format(n_tries))

