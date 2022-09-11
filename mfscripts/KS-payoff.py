from redeal import *
from collections import defaultdict


predeal = {"S": "8 A94 AT843 K942", "N": "A93 5 K752 AT853"}
tricks_ns = defaultdict(int)
tricks_ew = defaultdict(int)
open = {'pre': 0, '1M': 0}


def preempt(hand):
    return (max(len(hand.spades), len(hand.hearts)) >= 6
            and 6 <= hcp(hand) <= 10)


def major_opener(hand):
    return (max(len(hand.spades), len(hand.hearts)) >= 5
            and hcp(hand) >= 11)


def do(deal):

    tricks_ns[max(deal.dd_tricks('5CN'), deal.dd_tricks('5DS'))] += 1
    tricks_ew[max(deal.dd_tricks('4SE'), deal.dd_tricks('4HW'))] += 1
    open['pre'] += preempt(deal.west)
    open['1M'] += major_opener(deal.west) or major_opener(deal.east)


def final(n_tries):
    print(f"N-S in minor: {[(k, tricks_ns[k]) for k in sorted(tricks_ns.keys())]}")
    print(f"E-W in major: {tricks_ew}")
    print(f"West preempt in major: {open['pre']}")
    print(f"E-W open in major: {open['1M']}")
    print(f"hands dealt: {n_tries}")
