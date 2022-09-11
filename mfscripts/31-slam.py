from redeal import hand, deal, semibalanced


predeal = {"S": "KJ8 K5 A9753 K73"}
table = {"D": 0, "NT": 0}


def one_c_two_nt(hand):
    """Will open 1C, will rebid 2NT over 1D response"""
    if (semibalanced(hand) and len(hand.diamonds) <= 4
        and len(hand.clubs) >= len(hand.diamonds)
        and len(hand.clubs) >= 3
            and not (len(hand.hearts) == 5 or len(hand.spades) == 5)):
        return 18 <= hand.hcp <= 19


def accept(deal):
    return one_c_two_nt(deal.north)


def do(deal):
    table['D'] += deal.dd_tricks("6DS") >= 12
    table['NT'] += deal.dd_tricks("6NN") >= 12


def final(n_hands):
    print(f"total; {n_hands}, 6D makes on: {table['D']}, 6NT on {table['NT']}")
