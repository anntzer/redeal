# vim: set fileencoding=utf-8
"""An example script for redeal.

The following problem was presented on BridgeWinners.  You hold 652 K752 53
9862 and partner opens and shows a 22-24NT in front of you (2C-2D[waiting]-2N).
At matchpoints, do you pass, directly bid 3N, go through normal Stayman or
puppet Stayman?  If you go through Stayman, do you choose to play in a 4-3 S
fit instead of 3N if available?

Here, for each simulated hand, we compute the result of each strategy, and
compute a cross-table of how much each strategy would score against each other
strategy, on average, at BAM scoring.

The following names will be imported from the simulation module: `predeal`,
`initial`, `accept` and `final`.
"""

from collections import Counter
from redeal import *


# The predealt cards (a dict with keys N, E, S, W).  `H` is a hand constructor
# (if less than 13 cards are predealt, use "-" for the empty suits).
predeal = {"S": H("652 K752 53 9862")}


# `initial` is called at the beginning of the sim.  Here it initializes a
# global table (yes, globals are bad, but well).
def initial():
    global TABLE
    TABLE = [[Counter() for _ in range(5)] for _ in range(5)]


# `accept` is called for each hand with the currently dealt hand as argument.
# It must return True if the hand is accepted, or False if not.
def accept(deal):
    global TABLE
    # Deals have four properties: north, south, east, west.  Each of them is a
    # hand object, with properties spades, hearts, diamonds, clubs (that are
    # themselves hand objects, with fewer cards), shape (a list of lengths),
    # hcp.
    # Shape can also be tested by an expression such as `shape in
    # Shape("(4333)")+Shape("22(54)")` which behaves as expected. The
    # `balanced` and `semibalanced` shapes are predefined.
    if not (22 <= deal.north.hcp <= 24 and balanced(deal.north)):
        return False
    # `solve_board(deal, strain, declarer)` returns the DD number of tricks.
    nttricks = solve_board(deal, "N", "N")
    sptricks = solve_board(deal, "S", "N")
    hetricks = solve_board(deal, "H", "N")
    # `C` is the contract constructor.  Non-vulnerable is the default,
    # vulnerability can be specified as a second (boolean) argument.
    # Contracts have a `.score` method.
    pass2N = C("2N").score(nttricks)
    bid3N = C("3N").score(nttricks)
    stayman = C("4H").score(hetricks) if len(deal.north.hearts) >= 4 else bid3N
    pstayman = C("4S").score(sptricks) if len(deal.north.spades) == 5 else stayman
    majorgame = (C("4S").score(sptricks) if len(deal.north.spades) == 5 else 
                 (C("4H").score(hetricks) if len(deal.north.hearts) >= 4 else
                  (C("4S").score(sptricks) if len(deal.north.spades) == 4 else
                   bid3N)))
    # Respectively: pass 2N, bid 3N directly, go through Stayman, go through
    # puppet Stayman, and go through Stayman but prefer a 4-3 S fit to 3N.
    scores = [pass2N, bid3N, stayman, pstayman, majorgame]
    print("{} {}".format(deal, " ".join(map(str, scores))))
    for i, scorei in enumerate(scores):
        for j, scorej in enumerate(scores):
            # Update the cross-matchpoint table.  `imp(my_score, their_score)`
            # is also available for IMP comparisons.
            TABLE[i][j][matchpoints(scorei, scorej)] += 1
    return True


# `final` is called at the end of the sim with the number of tries as an
# argument.  Here it outputs the cross-matchpoint table.
def final(n_tries):
    global TABLE
    for line in TABLE:
        print("\t".join("+{} ={} -{}".format(counter[0], counter[0.5], counter[1])
                        for counter in line))
    print("Tries: {}".format(n_tries))


# An alternative `final` which only outputs the average score for each
# comparison (useful for IMPs, for example).
def final1(n_tries):
    global TABLE
    for line in TABLE:
        print("\t".join(str(np.mean(list(counter.elements())))
                        for counter in line))
    print("Tries: {}".format(n_tries))


# An alternative simulation, where we only want to compute how often there is a
# making game, regardless of whether it is reasonably easy to find (for
# example, we will have to choose between a 4-3 S fit -- 7% of the hands! --
# and a more normal contract -- which is more frequently the best choice).
def initial2():
    global TABLE
    TABLE = [0, 0]


def accept2(found, deal):
    global TABLE
    if not (22 <= deal.north.hcp <= 24 and balanced(deal.north.shape)):
        return False
    if (solve_board(deal, "H", "N") >= 10 or solve_board(deal, "S", "N") >= 10
        or solve_board(deal, "N", "N") >= 9):
        TABLE[True] += 1
    else:
        TABLE[False] += 1
    print("{}: {}".format(found + 1, deal))
    return True


def final2(n_tries):
    print(TABLE)

