"""Simming Cyberyeti's 1S conundrum.

Question: 1S is 5+ unless 15-19 4333.
    Also, 5S332s 12-14 are opened 1NT.
    What are the probabilities of various hands in 1S?
"""

from collections import Counter

from redeal import Deal, Hand, Shape, Simulation, balanced, hcp

predeal = {"N": "KJ7 J95 KJ5 T864"}


def is_4333_1s(hand: Hand) -> bool:
    """True if 4 spades square and out of NT range."""
    if hand.shape in Shape("4333") and hcp(hand) in range(15, 20):
        return True
    return False


def is_5332_1s(hand: Hand) -> bool:
    """True if 5(332) and out of NT range."""
    if hand.shape in Shape("5(332)") and hcp(hand) in range(15, 20):
        return True
    return False


def is_unbal_1s(hand: Hand) -> bool:
    """True if "normal" 1S opener.  Implies !`is_4333_1s` and !`is_5332_1s`"""
    if not balanced(hand) and len(hand.spades) >= max(map(len, hand[1:])):
        return True
    return False


class Yeti(Simulation):
    """The Simulation functions."""

    def __init__(self):
        super().__init__()
        self.counts = Counter()

    def accept(self, deal: Deal) -> bool:
        """Accept if 1S opener by rules."""
        south = deal.south
        if hcp(south) < 12 or hcp(south) > 21:
            return False  # out of range for 1S
        if is_4333_1s(south):
            return True
        if is_5332_1s(south):
            return True
        if is_unbal_1s(south):
            return True
        return False

    def do(self, deal: Deal) -> None:
        """Collect stats info for each successful deal."""
        south = deal.south
        # print(south)

        self.counts["is_4333"] += is_4333_1s(south)
        self.counts["is_4333_bad"] += is_4333_1s(south) and hcp(south) < 17
        self.counts["is_min5+"] += len(south.spades) > 4 and hcp(south) < 15
        self.counts["is_min5"] += len(south.spades) == 5 and hcp(south) < 15
        self.counts["twoSnv"] += hcp(south) < 17 and deal.dd_score(
            "2SS"
        ) >= deal.dd_score("1NTN")
        self.counts["oneNTnv"] += hcp(south) < 17 and deal.dd_score(
            "1NTN"
        ) >= deal.dd_score("2SS")
        self.counts["equalnv"] += hcp(south) < 17 and deal.dd_score(
            "2SS"
        ) == deal.dd_score("1NTN")

    def final(self, n_tries: int) -> None:
        """Print stats for run."""
        print(
            f"4333 hands: {self.counts['is_4333']}, "
            f"{self.counts['is_4333_bad']} of them 15 or 16 HCP."
        )
        print(
            f"min unbal: {self.counts['is_min5+']}, "
            f"{self.counts['is_min5']} of them exactly 5 spades."
        )
        print("2S+\t1NT+\tsame: Dealer 12-16 HCP")
        print(
            f"{self.counts['twoSnv']}\t"
            f"{self.counts['oneNTnv']}\t"
            f"{self.counts['equalnv']}"
        )


simulation = Yeti()
