"""SMP 1D hand generators."""

import sys
from pathlib import Path

from redeal import Deal, Hand, balanced, hcp
from smp_definitions import (
    five_card_major,
    four_card_major,
    generate_and_print_hands,
    minor_lengths,
    one_diamond_opener,
)

# TWEAK HERE
# Set this true if the hands should be 1D-2m, False if any response allowed
RESP_2m = False  # pylint: disable=invalid-name
DEBUG = False


def two_m_response(hand: Hand) -> bool:
    """True if responder has a 2m response to 1D.

    Per the book:
        - GF unless:
            - 11-12, 6cm
            - 11-12, 5-4m or better
        - no 4cM unless 4-6+ and GF
        - here we assume that 2NT and 3NT are preferred with balanced hands.
    """
    gf = hcp(hand) >= 13
    inv = hcp(hand) in range(11, 13)

    if inv:
        return not four_card_major(hand) and (
            max(minor_lengths(hand)) >= 6 or sum(minor_lengths(hand)) >= 9
        )
    if gf:
        return (
            not (balanced(hand) and hcp(hand) < 17)
            and not five_card_major(hand)
            and (not four_card_major(hand, plus=False) or max(minor_lengths(hand)) >= 6)
        )
    return False


def accept(deal: Deal) -> bool:
    """Deal accept function."""
    if not one_diamond_opener(deal.south):
        return False
    if not RESP_2m:
        return True

    if two_m_response(deal.north):
        if DEBUG:
            sys.stderr.write(f"Bingo! {deal.north}\n")
        return True
    if DEBUG:
        sys.stderr.write(f"Aw, no 2m response. {deal.north}\n")
    return False


F = f"1D{"-2m" if RESP_2m else ""}.pbn"
with Path(Path.cwd() / F).open(encoding="utf=8", mode="w") as f:
    generate_and_print_hands(f, accept)
