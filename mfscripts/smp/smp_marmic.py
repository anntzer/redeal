"""SMP: Strong hands and 4441s"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from mfscripts.smp.smp_definitions import (
    combine_and_print_hands,
    generate_pbn_hands,
    ns_hcp,
    one_club_opener,
    two_diamond_shape,
    two_diamonds_opener,
)
from redeal import Deal, Shape, SmartStack, hcp

DEBUG = False
marmic = Shape("(4441)")  # any marmic hand
OUTPUTS = []
MIN_HCP_STRONG = 29


def two_diamond_accept(deal: Deal) -> bool:
    """Accept if slammish and 2D opener"""
    if two_diamonds_opener(deal.south) and ns_hcp(deal) > MIN_HCP_STRONG:
        if DEBUG:
            print(deal)
        return True
    return False


def one_club_marmic(deal: Deal) -> bool:
    """Accept if 1C -> GF and marmic"""
    if one_club_opener(deal.south) and marmic(deal.south) and hcp(deal.north) > 7:
        if DEBUG:
            print(deal)
        return True
    return False


def one_club_strong_resp(deal: Deal) -> bool:
    """Accept if 1C and resp >= 12"""
    if one_club_opener(deal.south) and hcp(deal.north) > 11:
        if DEBUG:
            print(deal)
        return True
    return False


def one_club_strong_marmic(deal: Deal) -> bool:
    if one_club_strong_resp(deal) and marmic(deal.north):
        if DEBUG:
            print(deal)
        return True
    return False


@dataclass
class Pass:
    accept_function: Callable[[Deal], bool]
    predeal: Optional[dict[str, SmartStack]]


passes = (
    Pass(two_diamond_accept, {"S": SmartStack(two_diamond_shape, hcp, range(11, 16))}),
    Pass(one_club_marmic, {"S": SmartStack(marmic, hcp, range(16, 34))}),
    Pass(one_club_strong_resp, None),
    Pass(one_club_strong_marmic, {"N": SmartStack(marmic, hcp, range(12, 25))}),
)


for pass_ in passes:
    OUTPUTS.append(generate_pbn_hands(pass_.accept_function, pass_.predeal, 10))

F = "marmic.pbn"
with (Path.cwd() / F).open(encoding="utf-8", mode="w") as f:
    combine_and_print_hands(f, OUTPUTS, randomize=True, alternate_after=5)
