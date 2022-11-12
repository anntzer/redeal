"""Given control-rich 14 count, does slam make after 1C-1D; 2NT?"""

from collections import Counter

from redeal import Hand, Deal, semibalanced


predeal = {"S": "KJ8 K5 A9753 K73"}
table = Counter()


def one_c_two_nt(hand: Hand) -> bool:
    """Will open 1C, will rebid 2NT over 1D response"""
    if (semibalanced(hand) and len(hand.diamonds) <= 4
        and len(hand.clubs) >= len(hand.diamonds)
        and len(hand.clubs) >= 3
            and not (len(hand.hearts) == 5 or len(hand.spades) == 5)):
        return 18 <= hand.hcp <= 19


def accept(deal: Deal) -> bool:
    return one_c_two_nt(deal.north)


def do(deal: Deal) -> None:
    table['D'] += deal.dd_tricks("6DS") >= 12
    table['NT'] += deal.dd_tricks("6NN") >= 12
    table['count'] += 1


def final(n_hands: int) -> None:
    print(f"hands dealt: {n_hands}, matches: {table['count']}, "
          f"6D makes on: {table['D']}, 6NT on {table['NT']}")
