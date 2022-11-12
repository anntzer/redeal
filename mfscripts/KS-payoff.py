"""Does it hurt KS to pass borderline openers? from BBO"""

from redeal import hcp, Hand, Deal
from collections import Counter


predeal = {"S": "8 A94 AT843 K942", "N": "A93 5 K752 AT853"}
tricks_ns = Counter()
tricks_ew = Counter()
open_hand = Counter()


def preempt(hand: Hand) -> bool:
    return (max(len(hand.spades), len(hand.hearts)) >= 6
            and 6 <= hcp(hand) <= 10)


def major_opener(hand: Hand) -> bool:
    return (max(len(hand.spades), len(hand.hearts)) >= 5
            and hcp(hand) >= 11)


def do(deal: Deal) -> None:
    tricks_ns[max(deal.dd_tricks('5CN'), deal.dd_tricks('5DS'))] += 1
    tricks_ew[max(deal.dd_tricks('4SE'), deal.dd_tricks('4HW'))] += 1
    open_hand['pre'] += preempt(deal.west)
    open_hand['1M'] += (
            major_opener(deal.west)
            or (major_opener(deal.east) and not preempt(deal.west))
    )


def final(n_tries: int) -> None:
    print(f"N-S in minor: {sorted(tricks_ns.items())}")
    print(f"E-W in major: {sorted(tricks_ew.items())}")
    print(f"West preempt in major: {open_hand['pre']}")
    print(f"E-W open 1 Major: {open_hand['1M']}")
    print(f"hands dealt: {n_tries}")
