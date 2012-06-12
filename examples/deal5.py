"""Deal's example 5:

When I first wrote this I was somewhat surprised.

This deals hands where south opens a strong blue club and north has a 3+
controls (that is, he has a strong positive response.)

I was surprised to find that slam was making 1/2 the time on these hands.  In
other words, for Blue-clubbers, if the auction starts:

	1C	1S/1NT/2C/2D

there is a 50% chance that a slam should be bid...
"""

from __future__ import division, print_function, unicode_literals
from redeal import *

controls = defvector(2, 1)

def accept(deal):
    if (sum(map(controls, deal.north)) >= 3 and deal.south.hcp >= 17 and
        (deal.south.shape not in Balanced or
         deal.south.hcp != 17 and not (22 <= deal.south.hcp <= 24))):
        print("{}".format(deal)) # dirty trick to work both in Python 2 and 3
        return True
