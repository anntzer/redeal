from redeal import *

# Give N a strong NT opener ("balanced" includes 5M332)
predeal = {'N': SmartStack(balanced, hcp, range(15, 18))}


class MySim(Simulation):

    def __init__(self):
        self.counters = {
            'accepted': 0,
            'nt_best': 0,
            'nt_minus_1': 0,
            'nt_down': 0,
            'suit_down': 0,
            'fit': 0
        }

    def accept(self, deal):
        """Accept the deal if South is 5M332 and "maximum" for pass

        Specifically 6-8.  I assume we invite with 9.

        """

        return (deal.south.shape in Shape('(53)(32)') + Shape('(52)33')
                and deal.south.hcp in range(6, 9))

    def do(self, deal):
        """Process the accepted deal.  Increment the relevant counters."""
        nt = deal.dd_tricks('1NN')
        if len(deal.south.spades) == 5:
            s_contract = '2SN'
            fit = len(deal.south.spades) + len(deal.north.spades) >= 8
        else:
            s_contract = '2HN'
            fit = len(deal.south.hearts) + len(deal.north.hearts) >= 8
        suit = deal.dd_tricks(s_contract)

        self.counters['accepted'] += 1
        self.counters['nt_best'] += 1 if deal.dd_score('1NN') > deal.dd_score(s_contract) else 0
        self.counters['nt_minus_1'] += 1 if nt - suit == 1 else 0
        self.counters['nt_down'] += 1 if deal.dd_score('1NN') < 0 else 0
        self.counters['suit_down'] += 1 if deal.dd_score(s_contract) < 0 else 0
        self.counters['fit'] += 1 if fit else 0

#        print('NT: {nt}, suit: {suit}, HCP: {hcp} {fit}'
#              .format(nt=nt,
#                      suit=suit,
#                      hcp=deal.north.hcp + deal.south.hcp,
#                      fit='FIT' if fit else ''))

    def final(self, n_tries):
        print('{} hands processed of {} attempted:'.format(self.counters['accepted'], n_tries))
        print('NT scores better on {} deals'.format(self.counters['nt_best']))
        print('NT one trick less on {} deals'.format(self.counters['nt_minus_1']))
        print('1NT goes down on {} deals'.format(self.counters['nt_down']))
        print('2M goes down on {} deals'.format(self.counters['suit_down']))
        print('8-card M fit on {} deals'.format(self.counters['fit']))


simulation = MySim()