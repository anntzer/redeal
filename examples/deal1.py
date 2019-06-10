"""
Deal's example 1:

North is 44 in the majors, short in a minor, and has 11-15HCP.
"""

def accept(deal):
    return (len(deal.north.spades) == 4 and len(deal.north.hearts) == 4 and
            len(deal.north.diamonds) not in [2, 3] and
            11 <= deal.north.hcp <= 15)
