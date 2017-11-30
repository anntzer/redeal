"""Deal's gambling 3NT example, with smartstacking:

Find deals where south is AK K52 98765 962 and north has a gambling 3NT
hand.

To test the implementation, run ::

    redeal -n10000 examples/deal_gambling.py

and compare to the output of deal's ::

    deal -i ex/3nt-stack.tcl 10000 | sort | uniq -c | sort -nr
"""

from collections import Counter
from redeal import *

GamblingShape = Shape.from_cond(lambda s, h, d, c:
    s <= 3 and h <= 3 and (d >= 7 and c <= 4 or d <= 4 and c >= 7))

# All suits must satisfy "gambling", so the total "gambling" should equal 4.
def gambling(holding):
    return (
        len(holding) >= 7 and A in holding and K in holding and Q in holding
        or len(holding) <= 4 and A not in holding and K not in holding)

predeal = {"S": H("AK K52 98765 962"),
           "N": SmartStack(GamblingShape, gambling, [4])}

_shapes = Counter()

def do(deal):
    _shapes[deal.north.shape] += 1

def final(deal):
    for k, v in _shapes.most_common():
        print(" ".join(map(str, k)), ":", v)
