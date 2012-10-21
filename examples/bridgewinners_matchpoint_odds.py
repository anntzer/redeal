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
`initial`, `accept` `do` and `final`.
"""

from redeal import *


# The predealt cards (a dict with keys N, E, S, W).  `H` is a hand constructor
# (if less than 13 cards are predealt, use "-" for the empty suits).
predeal = {"S": H("652 K752 53 9862")}


# `initial` is called at the beginning of the sim.  Here it initializes a
# global matchpoint payoff table (yes, globals are bad, but well).
def initial():
    global TABLE
    TABLE = Payoff(("pass2N", "bid3N", "stayman", "pstayman", "majorgame"),
                   matchpoints)


# `accept` is called for each hand with the currently dealt hand as argument.
# It must return True if the hand is accepted, or False if not.
def accept(deal):
    # Deals have four properties: north, south, east, west.  Each of them is a
    # hand object, with properties spades, hearts, diamonds, clubs (that are
    # themselves hand objects, with fewer cards), shape (a list of lengths),
    # hcp.
    # Shape can also be tested by an expression such as `shape in
    # Shape("(4333)")+Shape("22(54)")` which behaves as expected. The
    # `balanced` and `semibalanced` shapes are predefined.
    return 22 <= deal.north.hcp <= 24 and balanced(deal.north)


# `do` is called for each accepted hand.
def do(deal):
    # `deal.dd_score` returns the double dummy score for a contract, assumed
    # non-vulnerable -- vulnerability can be specified as a second (boolean)
    # argument.
    pass2N = deal.dd_score("2NN")
    bid3N = deal.dd_score("3NN")
    stayman = deal.dd_score("4HN") if len(deal.north.hearts) >= 4 else bid3N
    pstayman = deal.dd_score("4SN") if len(deal.north.spades) == 5 else stayman
    majorgame = (deal.dd_score("4SN") if len(deal.north.spades) == 5 else
                 (deal.dd_score("4HN") if len(deal.north.hearts) >= 4 else
                  (deal.dd_score("4SN") if len(deal.north.spades) == 4 else
                   bid3N)))
    # Respectively: pass 2N, bid 3N directly, go through Stayman, go through
    # puppet Stayman, and go through Stayman but prefer a 4-3 S fit to 3N.
    scores = dict(pass2N=pass2N, bid3N=bid3N, stayman=stayman,
                  pstayman=pstayman, majorgame=majorgame)
    print("{} {}".format(deal, " ".join(str(scores[k]) for k in TABLE.entries)))
    # Update the cross-matchpoint table.
    TABLE.add_data(scores)


# `final` is called at the end of the sim with the number of tries as an
# argument.  Here it outputs the cross-matchpoint table.
def final(n_tries):
    TABLE.report()
    print("Tries: {}".format(n_tries))


# An alternative simulation, where we only want to compute how often there is a
# making game, regardless of whether it is reasonably easy to find (for
# example, we will have to choose between a 4-3 S fit -- 7% of the hands! --
# and a more normal contract -- which is more frequently the best choice).
def initial2():
    global TABLE
    TABLE = [0, 0]


# `deal.dd_tricks` returns the double-dummy number of tricks for a contract.
def do2(found, deal):
    if (deal.dd_overtricks("4HN") >= 10 or deal.dd_overtricks("4SN") >= 10 or
        deal.dd_overtricks("3NN") >= 9):
        TABLE[True] += 1
    else:
        TABLE[False] += 1
    print("{}: {}".format(found + 1, deal))


def final2(n_tries):
    print(TABLE)
