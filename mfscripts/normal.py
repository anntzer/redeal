"""No strange hands for lesson final tourney."""
from pathlib import Path

from redeal import Deal, hcp

dealvul = (
    ("N", "None"),
    ("E", "NS"),
    ("S", "EW"),
    ("W", "All"),
    ("N", "NS"),
    ("E", "EW"),
    ("S", "All"),
    ("W", "None"),
    ("N", "EW"),
    ("E", "All"),
    ("S", "None"),
    ("W", "NS"),
    ("N", "All"),
    ("E", "None"),
    ("S", "NS"),
    ("W", "EW"),
)


def accept(deal: Deal) -> bool:
    """Boring hands.  No 30+ in one partnership, no 7+ card suits."""

    if hcp(deal.north) + hcp(deal.south) not in range(10, 30, 1):
        return False

    max_length = 0
    for hand in deal:
        hand_length = max(hand.shape)
        max_length = max(max_length, hand_length)
    if max_length > 6:
        return False

    return True


Deal.set_str_style("pbn")
dealer = Deal.prepare()

with Path(Path.cwd() / "normal.pbn").open("w", newline="\r\n", encoding="utf-8") as f:
    for i in range(18):
        dv = i % 16
        print(f'\n[Board "{i + 1}"]', file=f)
        print(f'[Dealer "{dealvul[dv][0]}"]', file=f)
        print(f'[Vulnerable "{dealvul[dv][1]}"]', file=f)
        print(dealer(accept), file=f)
