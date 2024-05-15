"""Should 5M332s transfer over 1NT?"""

from collections import defaultdict

from redeal import hcp, Shape, Simulation, SmartStack

# play with these values if desired
NT_MIN = 15
NT_MAX = 17
RESP_MIN = 7
RESP_MAX = 8
INCLUDE_5M332 = True
INCLUDE_6m322 = False  # pylint: disable=invalid-name
PRINT_EACH_HAND = False
# You shouldn't have to change anything after this.

# Give N a strong NT opener
nt_shape = Shape("(4333)") + Shape("(4432)")
if INCLUDE_5M332:
    nt_shape += Shape("(5332)")
else:
    nt_shape += Shape("33(52)") + Shape("(32)(53)")
if INCLUDE_6m322:
    nt_shape += Shape("(32)(62)") + Shape("22(63)")
predeal = {"N": SmartStack(nt_shape, hcp, range(NT_MIN, NT_MAX + 1))}


class MySim(Simulation):
    """Should max pass 5M332s transfer or try to take the same tricks in 1NT?

    Question on the BB Forums about "do you transfer or pass with 5332 at
    matchpoints?"  The only thing not reaching consensus was "if you're 22-23,
    so you're a max for not-an-invite, is it better to pass and try to take
    the same number of tricks in NT as in the suit?"

    This simulation attempts to answer this question.

    """

    def __init__(self):
        self.stats = {
            "accepted": {
                "count": 0,
                "display": "{item} hands processed of {n_tries} attempted:\n",
            },
            "nt_best": {"count": 0, "display": "NT scores better on {item} deals"},
            "nt_not_worse": {
                "count": 0,
                "display": "NT scores equal or better on {item} deals",
            },
            "nt_minus_1": {"count": 0, "display": "NT one trick less on {item} deals"},
            "nt_down": {"count": 0, "display": "1NT goes down on {item} deals"},
            "suit_down": {"count": 0, "display": "2M goes down on {item} deals"},
            "fit": {"count": 0, "display": "8-card M fit on {item} deals"},
        }
        self.points = defaultdict(int)

    def accept(self, deal):
        """Accept the deal if South is 5M332 and within requested range."""

        return deal.south.shape in Shape("(53)(32)") + Shape(
            "(52)33"
        ) and deal.south.hcp in range(RESP_MIN, RESP_MAX + 1)

    def do(self, deal):
        """Process the accepted deal.  Increment the relevant counters."""

        def _increment_if(stat, test):
            # relies on int(bool) being 1 or 0.
            self.stats[stat]["count"] += test

        # increment total points counter
        points = deal.north.hcp + deal.south.hcp
        self.points[points] += 1

        # get tricks in NT and the major.  Transfers, so NTer always plays.
        nt = deal.dd_tricks("1NN")
        if len(deal.south.spades) == 5:
            s_contract = "2SN"
            fit = len(deal.south.spades) + len(deal.north.spades) >= 8
        else:
            s_contract = "2HN"
            fit = len(deal.south.hearts) + len(deal.north.hearts) >= 8
        suit = deal.dd_tricks(s_contract)

        # increment relevant counters for table.
        _increment_if("accepted", True)
        _increment_if("nt_best", deal.dd_score("1NN") > deal.dd_score(s_contract))
        _increment_if("nt_not_worse", deal.dd_score("1NN") >= deal.dd_score(s_contract))
        _increment_if("nt_minus_1", suit - nt == 1)
        _increment_if("nt_down", deal.dd_score("1NN") < 0)
        _increment_if("suit_down", deal.dd_score(s_contract) < 0)
        _increment_if("fit", fit)

        if PRINT_EACH_HAND:
            print(f"NT: {nt}, suit: {suit}, HCP: {points}{' FIT' if fit else ''}")

    def final(self, n_tries):
        """After all processing, print out the results"""

        print(
            f"{NT_MIN}-{NT_MAX} opposite {RESP_MIN}-{RESP_MAX},"
            f"{' 5M332' if INCLUDE_5M332 else ''}",
            f"{' 6m322' if INCLUDE_6m322 else ''}",
        )
        for stat in self.stats.values():
            print(stat["display"].format(item=stat["count"], n_tries=n_tries))
        print(f"frequencies of HCP totals: {sorted(self.points.items())}")


simulation = MySim()
