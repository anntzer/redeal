from redeal import *

predeal = {"W": "QT T32 JT8732 32"}

def accept(deal):
    north, south = deal.north, deal.south
    return (south.shape in Shape("33(43)") + Shape("(32)(53)") and
            4 in (len(north.spades), len(north.hearts)) and
            15 <= south.hcp <= 17 and 9 <= north.hcp <= 11)

simulation = OpeningLeadSim(accept, "3NS", imps)
