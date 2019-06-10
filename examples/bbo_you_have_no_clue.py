from collections import Counter
from redeal import *


predeal = {"S": "T8 8762 KT4 KQ52"}


def initial():
    global TABLE
    TABLE = [[Counter() for _ in range(3)] for _ in range(3)]


def accept(deal):
    return 15 <= deal.north.hcp <= 17 and balanced(deal.north)


def do(deal):
    pass1N = deal.dd_score("1NN", vul=True)
    if len(deal.north.hearts) < 4:
        if deal.north.hcp >= 17:
            s17 = deal.dd_score("3NN", vul=True)
        else:
            s17 = deal.dd_score("2NN", vul=True)
    else:
        if deal.north.hcp >= 17:
            s17 = deal.dd_score("4HN", vul=True)
        else:
            s17 = deal.dd_score("3HN", vul=True)
    if len(deal.north.hearts) < 4:
        if deal.north.hcp >= 16:
            s16 = deal.dd_score("3NN", vul=True)
        else:
            s16 = deal.dd_score("2NN", vul=True)
    else:
        if deal.north.hcp >= 16:
            s16 = deal.dd_score("4HN", vul=True)
        else:
            s16 = deal.dd_score("3HN", vul=True)
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
    print(f"Tries: {n_tries}")
