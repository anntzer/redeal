# See http://www.rpbridge.net/8z15.htm

from redeal import *


predeal = {"N": "J763 J874 74 AQ5"}
table = {15: 0, 16: 0, 17: 0}


def accept(d):
    return (
        15 <= d.south.hcp <= 17 and d.south.freakness < 3
        and (len(d.south.spades) < 5 and len(d.south.hearts) < 5
             or not any(len(holding) == 2 and holding.hcp == 0
                        for holding in d.south))
        and all(opp.hcp < 15
                and (opp.freakness < 6 and max(map(len, opp)) < 6
                     or opp.pt < 6)
                for opp in [d.west, d.east])
    )


def do(d):
    table[d.south.hcp] += 1


def final(_):
    print(table)
