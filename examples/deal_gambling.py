"""Deal's gambling 3NT example, with smartstacking:

Find deals where south is AK K52 98765 962 and north has a gambling 3NT
hand.

To test the implementation, run

    ./redeal.py -n10000 examples/deal_gambling.py | sort | uniq -c | sort -nr

and compare to the output of deal's

    deal -i ex/3nt-stack.tcl 10000 | sort | uniq -c | sort -nr
"""

from redeal import *

GamblingShape = Shape.from_cond(lambda s, h, d, c:
    s <= 3 and h <= 3 and (d >= 7 and c <= 4 or d <= 4 and c >= 7))

# all suits must satisfy "gambling", hence the total of 4
def gambling(holding):
    return (len(holding) >= 7 and A in holding and
            K in holding and Q in holding or
            len(holding) <= 4 and A not in holding and K not in holding)
gambling.contains = lambda v: v == 4

predeal = {"S": H("AK K52 98765 962"),
           "N": SmartStack(GamblingShape, gambling)}

def do(deal):
    print("-- " + " ".join(map(str, deal.north.shape)))
