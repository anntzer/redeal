from collections import defaultdict

from redeal import *

# play with these values if desired
NT_MIN = 13
NT_MAX = 15
RESP_MIN = 8
RESP_MAX = 10
INCLUDE_5M332 = True
INCLUDE_6m322 = False
PRINT_EACH_HAND = False
# You shouldn't have to change anything after this.

# Give N a strong NT opener
nt_shape = Shape('(4333)') + Shape('(4432)')
if INCLUDE_5M332:
    nt_shape += Shape('(5332)')
else:
    nt_shape += Shape('33(52)') + Shape('(32)(53)')
if INCLUDE_6m322:
    nt_shape += Shape('(32)(62)') + Shape('22(63)')
predeal = {'N': SmartStack(nt_shape, hcp, range(NT_MIN, NT_MAX + 1))}


class MySim(Simulation):
    """Should max pass 5M332s transfer or try to take the same tricks in 1NT?

     Question on the BB Forums about "do you transfer or pass with 5332 at
     matchpoints?"  The only thing not reaching consensus was "if you're 22-23,
     so you're a max for not-an-invite, is it better to pass and try to take
     the same number of tricks in NT as in the suit?"

     This simulation attempts to answer this question.  It goes for "South is
     6-8 HCP" instead of "22-23 HCP", because South can't know that.

    """

    def __init__(self):
        self.counters = {
            'accepted': 0,
            'nt_best': 0,
            'nt_not_worse': 0,
            'nt_minus_1': 0,
            'nt_down': 0,
            'suit_down': 0,
            'fit': 0
        }
        self.points = defaultdict(int)

    def accept(self, deal):
        """Accept the deal if South is 5M332 and "maximum" for pass

        Specifically 6-8.  I assume we invite with 9.

        """

        return (deal.south.shape in Shape('(53)(32)') + Shape('(52)33')
                and deal.south.hcp in range(RESP_MIN, RESP_MAX + 1))

    def do(self, deal):
        """Process the accepted deal.  Increment the relevant counters."""

        # increment total points counter
        points = deal.north.hcp + deal.south.hcp
        self.points[points] += 1

        # get tricks in NT and the major.  Transfers, so NTer always plays.
        nt = deal.dd_tricks('1NN')
        if len(deal.south.spades) == 5:
            s_contract = '2SN'
            fit = len(deal.south.spades) + len(deal.north.spades) >= 8
        else:
            s_contract = '2HN'
            fit = len(deal.south.hearts) + len(deal.north.hearts) >= 8
        suit = deal.dd_tricks(s_contract)

        # increment relevant counters for table.
        # Note that bool() is guaranteed to be 1 or 0.
        self.counters['accepted'] += 1
        self.counters['nt_best'] += bool(deal.dd_score('1NN')
                                         > deal.dd_score(s_contract))
        self.counters['nt_not_worse'] += bool(deal.dd_score('1NN')
                                              >= deal.dd_score(s_contract))
        self.counters['nt_minus_1'] += bool(suit - nt == 1)
        self.counters['nt_down'] += bool(deal.dd_score('1NN') < 0)
        self.counters['suit_down'] += bool(deal.dd_score(s_contract) < 0)
        self.counters['fit'] += fit

        if PRINT_EACH_HAND:
            print('NT: {nt}, suit: {suit}, HCP: {hcp} {fit}'
                  .format(nt=nt,
                          suit=suit,
                          hcp=deal.north.hcp + deal.south.hcp,
                          fit='FIT' if fit else ''))

    def final(self, n_tries):
        """After all processing, print out the results"""

        print('{lo}-{hi} opposite {rm}-{rx},{M5}{m6}'.format(
            lo=NT_MIN, hi=NT_MAX, rm=RESP_MIN, rx=RESP_MAX,
            M5=' 5M332' if INCLUDE_5M332 else '',
            m6=' 6m322' if INCLUDE_6m322 else '',
        ))
        print('{} hands processed of {} attempted:\n'
              .format(self.counters['accepted'], n_tries))
        print(f"NT scores better on {self.counters['nt_best']} deals")
        print(f"NT scores no worse on {self.counters['nt_not_worse']} deals")
        print(f"NT one trick less on {self.counters['nt_minus_1']} deals")
        print(f"1NT goes down on {self.counters['nt_down']} deals")
        print(f"2M goes down on {self.counters['suit_down']} deals")
        print(f"8-card M fit on {self.counters['fit']} deals")
        print(f'frequencies of HCP totals: {sorted(self.points.items())}')


simulation = MySim()
