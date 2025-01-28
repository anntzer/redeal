"""Generate all "weird" hands for SMP."""

from collections import defaultdict
from pathlib import Path
from pprint import pprint

from smp_1d import two_m_response
from smp_definitions import (
    generate_and_print_hands,
    one_club_opener,
    one_diamond_opener,
    one_diamond_response_sc,
    two_clubs_opener,
    two_diamonds_opener,
)

from redeal import Deal, hcp

# TWEAK HERE
ALLOW_STRONG_NON_WEIRD = True  # allow slammish hands not in the weird categories
REQUIRE_STRONG_WEIRD = False  # only accept slammish hands in the weird categories
MIN_HCP_STRONG = 29
DEBUG = True


HAND_TYPE = defaultdict(int)


def slammish(deal: Deal) -> bool:
    """Is slammish if HCP(NS) >= MIN_HCP_STRONG."""
    return hcp(deal.north) + hcp(deal.south) >= MIN_HCP_STRONG


def accept(deal: Deal) -> bool:
    """For the various cases, accept if they're weird (and/or strong)"""
    accepted = False  # assume wrong
    HAND_TYPE["n_hands"] += 1

    n, s = deal.north, deal.south
    if one_club_opener(s) and (one_diamond_response_sc(n) or hcp(n) > 12):
        accepted = True
        HAND_TYPE["1c1d"] += 1
    elif one_diamond_opener(s) and two_m_response(n):
        accepted = True
        HAND_TYPE["1d2m"] += 1
    elif two_clubs_opener(s) or two_diamonds_opener(s):
        accepted = True
        HAND_TYPE["2m"] += 1

    if ALLOW_STRONG_NON_WEIRD:
        if not accepted and slammish(deal):
            accepted = True
            HAND_TYPE["slam"] += 1
        return accepted
    elif REQUIRE_STRONG_WEIRD:
        return accepted and slammish(deal)
    else:
        return accepted


F = "SMP_weird.pbn"
with (Path.cwd() / F).open(encoding="utf=8", mode="w") as f:
    generate_and_print_hands(f, accept, alternate_after=5, num_hands=40)
if DEBUG:
    pprint(HAND_TYPE)
