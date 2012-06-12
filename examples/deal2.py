"""Deal's example 2:

I held the south hand given below, and east opened 2C. I overcalled 2S
red-on-red.  This procedure deals hands where east will open 2C in front of the
south hand.
"""

from __future__ import division, print_function, unicode_literals
from redeal import *

predeal = {"S": H("Q86432 T2 932 83")}

def accept(deal):
    if deal.east.hcp > 18 and (deal.east.hcp > 22 or deal.east.losers < 2):
        print("{}".format(deal)) # dirty trick to work both in Python 2 and 3
        return True
