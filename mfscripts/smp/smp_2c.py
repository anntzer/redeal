"""SMP 2D hand generators."""

import sys
from pathlib import Path

from redeal import Deal, Hand, SmartStack, hcp
from smp_definitions import generate_and_print_hands, two_clubs_shape

# TWEAK HERE
# Set this true if the hands should be 2C-2D, False if any response allowed
RESP_2D = False
DEBUG = True


def two_diamond_response(hand: Hand) -> bool:
    """True if responder has a 2D response to 1C. (INV+ inquiry)"""
    inv_plus = hcp(hand) > 11
    transfer = hand.l1 >= 6
    return inv_plus and not transfer


def accept(deal: Deal) -> bool:
    """Deal accept function."""
    if not RESP_2D:
        return True

    if two_diamond_response(deal.north):
        if DEBUG:
            sys.stderr.write(f"Bingo! {deal.north}\n")
        return True
    if DEBUG:
        sys.stderr.write(f"Aw, no 2D response. {deal.north}\n")
    return False


predeal = {"S": SmartStack(two_clubs_shape, hcp, range(11, 16))}
F = f"2C{"-2D" if RESP_2D else ""}.pbn"
with Path(Path.cwd() / F).open(encoding="utf=8", mode="w") as f:
    generate_and_print_hands(
        f, accept, predeal=predeal, alternate_after=5, num_hands=20
    )
