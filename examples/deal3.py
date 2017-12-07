"""Deal's example 3:

You hold the south hand: 764 J4 J753 AQJ2 and the auction has gone:
1S(W)-1NT-2NT-3NT by the opponents, who are playing 2/1.  Choose a lead.

In this example, I've assumed west has no side 4-card suit, and that he holds
exactly 5 spades and 16-19 HCP.

I've also assumed that East had some way to show a 5-card heart suit over 2NT,
and hence, that he doesn't hold one, and also that east does not have spade
support.
"""

from redeal import *

predeal = {"S": "764 J4 J753 AQJ2"}

def accept(deal):
    return (16 <= deal.west.hcp <= 19 and deal.west.shape in Shape("5(332)")
            and 6 <= deal.east.hcp <= 11 and deal.east.losers >= 3
            and len(deal.east.hearts) <= 4 and len(deal.east.spades) <= 2)
