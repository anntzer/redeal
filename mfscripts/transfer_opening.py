"""Chance of 'other' hand in N.Houle 1-red openers

Claiming that "1D: 11-14, 4+H unbalanced or 17-19 BAL, 3H2S"
and "1H: 11-14, 4+S unbalanced or 15-16/19-20 BAL, 3S2H"
are Open Legal because they have a "not unlikely hand type" to
make it allowed.  Let's find out.
"""
from collections import defaultdict

from redeal import Deal, Hand, Shape, balanced, Simulation

DEBUG = {
    "hand": False,
}
TABLE = defaultdict(int)


def unbalanced(hand: Hand) -> bool:
    """They seem to agree that 5M233 and 5M2(42) are unbalanced, so"""
    return not balanced(hand) or len(hand.spades) == 5 or len(hand.hearts) == 5


def one_d_hearts(hand: Hand) -> bool:
    """1D opener, with hearts."""
    return unbalanced(hand) and len(hand.hearts) >= 4 and hand.hcp in range(11, 15)


def one_d_bal(hand: Hand) -> bool:
    """1D opener, balanced."""
    bal = Shape("2344") + Shape("23(35)")
    return bal(hand) and hand.hcp in range(17, 20)


def one_h_spades(hand: Hand) -> bool:
    """1H opener, with spades."""
    return unbalanced(hand) and len(hand.spades) >= 4 and hand.hcp in range(11, 15)


def one_h_bal(hand: Hand) -> bool:
    """1H opener, balanced."""
    bal = Shape("3244") + Shape("32(35)")
    return bal(hand) and (hand.hcp in range(15, 17) or hand.hcp in range(19, 21))


class TransferOpeners(Simulation):
    """Simulate 1D/1H openers, count the different styles."""

    def accept(self, deal: Deal) -> bool:
        """True if it's a 1D/1H opener."""
        return (
            one_d_bal(deal.south)
            or one_d_hearts(deal.south)
            or one_h_bal(deal.south)
            or one_h_spades(deal.south)
        )

    def do(self, deal: Deal) -> None:
        """Count 'em up."""
        hand = deal.south
        if DEBUG["hand"]:
            print(f"{'* ' if one_d_bal(hand) or one_h_bal(hand) else ''} {hand}")

        TABLE["1DH"] += one_d_hearts(hand) and (
            len(hand.hearts) > len(hand.spades) or hand.shape in Shape("44xx")
        )
        TABLE["1DB"] += one_d_bal(hand)
        TABLE["1HS"] += one_h_spades(hand) and (
            len(hand.spades) > len(hand.hearts)
            or hand.shape in Shape("55xx") + Shape("66xx")
        )
        TABLE["1HB"] += one_h_bal(hand)

    def final(self, n_tries: int) -> None:
        """Print stats."""
        print(TABLE)
        print(
            f"IsRare: 1D: {round((100 * TABLE['1DB'])/(TABLE['1DH'] + TABLE['1DB']), 2)}%"
        )
        print(
            f"IsRare: 1H: {round((100 * TABLE['1HB'])/(TABLE['1HS'] + TABLE['1HB']), 2)}%"
        )
        print(f"Total: {sum(TABLE.values())}")
        print(n_tries)


simulation = TransferOpeners()
