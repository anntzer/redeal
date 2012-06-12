"""Deal's example 1:

North is 44 in the majors, short in a minor, and has 11-15HCP.
"""

from __future__ import division, print_function, unicode_literals

def accept(deal):
    if (len(deal.north.spades) == 4 and len(deal.north.hearts) == 4 and
        len(deal.north.diamonds) not in [2, 3] and 11 <= deal.north.hcp <= 15):
        print("{}".format(deal)) # dirty trick to work both in Python 2 and 3
        return True
