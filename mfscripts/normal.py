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
    """Boring hands"""

    if hcp(deal.north) + hcp(deal.south) not in range(10, 30, 1):
        return False

    x = [hand.shape for hand in deal]
    # print(x)
    max_length = max(max(shape_) for shape_ in x)
    if max_length > 6:
        return False

    return True


Deal.set_str_style("pbn")
dealer = Deal.prepare()

f = Path(Path.cwd() / "normal.pbn").open("w", newline="\r\n")
for i in range(18):
    dv = i % 16
    print(f'\n[Board "{i+1}"]', file=f)
    print(f'[Dealer "{dealvul[dv][0]}"]', file=f)
    print(f'[Vulnerable "{dealvul[dv][1]}"]', file=f)
    print(dealer(accept), file=f)

f.close()
