"""SMP 2D hand generators."""

import sys
from pathlib import Path

from redeal import Deal, Hand, Holding, Rank, Shape, SmartStack, hcp
from smp_definitions import generate_and_print_hands, two_diamond_shape

# TWEAK HERE
# Set this true if the hands should be 2D-2NT, False if any response allowed
RESP_2NT = True
DEBUG = True

# convenience definitions
three_nt = Shape.from_cond(lambda s, h, d, c: s <= 3 and h <= 3 and d >= 2 and c >= 2)


def stopper(suit: Holding) -> bool:
    """return "do I have a stopper (opposite nothing)?"

    Decision is very arbitrary.
    """
    return (
        Rank.A in suit
        or (Rank.K in suit and len(suit) > 1)
        or (Rank.Q in suit and (Rank.J in suit or Rank.T in suit) and len(suit) > 2)
        or (Rank.Q in suit or Rank.J in suit and len(suit) > 3)
        or len(suit) > 4
    )


def two_nt_response(hand: Hand) -> bool:
    """True if responder has a 2NT response to 1D."""
    # must be inv+
    if hcp(hand) < 11:
        return False
    # shapes that probably should just bid 3NT with game values
    if hcp(hand) >= 13 and three_nt(hand) and stopper(hand.diamonds):
        return False
    # just bid 4M
    if hcp(hand) >= 13 and (len(hand.spades) >= 5 or len(hand.hearts) >= 5):
        return False
    return True


def accept(deal: Deal) -> bool:
    """Deal accept function."""
    if not RESP_2NT:
        return True

    if two_nt_response(deal.north):
        if DEBUG:
            sys.stderr.write(f"Bingo! {deal.north}\n")
        return True
    if DEBUG:
        sys.stderr.write(f"Aw, no 2NT response. {deal.north}\n")
    return False


predeal = {"S": SmartStack(two_diamond_shape, hcp, range(11, 16))}
F = f"2D{"-2NT" if RESP_2NT else ""}.pbn"
with Path(Path.cwd() / F).open(encoding="utf=8", mode="w") as f:
    generate_and_print_hands(f, accept, predeal=predeal)
