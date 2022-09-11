import collections
from functools import cmp_to_key

from redeal import Evaluator, hcp, Shape, Simulation
from redeal.global_defs import Suit

DEBUG = {'hand': True,
         'hcp': True,
         'is_clubs': False,
         'suits': True,}

IS_CLUBS = True
RANGE_MIN = 6
RANGE_MAX = 12

twobidshape = Shape.from_cond(
    lambda s, h, d, c: s >= 5 or h >= 5 or d >= 5 or (c >= 5 and IS_CLUBS)
)
full_suit_eval = Evaluator(*range(14, 1, -1))


def holding_cmp(x, y):
    """stronger holding.  Length, then cards from sum."""
    return (
        len(x) - len(y)
        if len(x) != len(y)
        else full_suit_eval(x) - full_suit_eval(y)
    )


def ehaa_nt(hand):
    is_nt_shape = (Shape('(4333)') + Shape('(4432)')
                   + Shape('(33)(25)') + Shape('(32)(35)'))
    return is_nt_shape(hand) and hcp(hand) in (10, 11, 12)


class EHAA2length(Simulation):

    def initial(self):
        self.maxlength = collections.defaultdict(int)
        self.points = collections.defaultdict(int)
        self.bidsuit = []

    def accept(self, deal):

        return (
                deal.south.shape in twobidshape
                and hcp(deal.south) in range(RANGE_MIN, RANGE_MAX + 1)
                and not ehaa_nt(deal.south)
        )

    def do(self, deal):

        if DEBUG['hand']:
            print(deal.south)

        if DEBUG['is_clubs'] and len(deal.south.clubs) >= 5:
            other_suit = (len(deal.south.diamonds) >= 5
                          or len(deal.south.hearts) >= 5
                          or len(deal.south.spades) >= 5)
            print(f'{deal.south}   {other_suit}')

        ml = max(deal.south.shape)
        self.maxlength[ml] = self.maxlength[ml] + 1
        self.points[deal.south.hcp] = self.points[deal.south.hcp] + 1
        for suit in Suit:
            if len(deal.south[suit]) == ml:
                self.bidsuit.append(deal.south[suit])

    def final(self, n_tries):

        print('Lengths:')
        for k in sorted(self.maxlength):
            print(f'{k}\t{self.maxlength[k]}')

        if DEBUG['hcp']:
            print('\nHCP:')
            for k in sorted(self.points):
                print(f'{k}\t{self.points[k]}')

        if DEBUG['suits']:
            print(self.bidsuit)
            print([full_suit_eval(x) for x in self.bidsuit])

        print('\nMedian hand: '
              f'{sorted(self.bidsuit, key=cmp_to_key(holding_cmp))[len(self.bidsuit) // 2]}')


simulation = EHAA2length()
