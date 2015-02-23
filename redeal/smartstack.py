# vim: set fileencoding=utf-8
from bisect import bisect
from collections import Counter
from functools import reduce
from itertools import combinations, product
import operator
import random

from .global_defs import *


class _SmartStack(object):
    def __init__(self, shape, oks, bound_eval):
        # shape: Shape object
        # oks[i]: holding acceptance function for suit i
        # bound_eval: bound evaluator

        # holdings[i][l, v]:
        #     OK holdings for suit #i such that len(h) = l, eval_holding(h) = v
        holdings = [{} for _ in range(N_SUITS)]
        for l in range(PER_SUIT):
            for holding in map(frozenset, combinations(range(PER_SUIT), l)):
                v = bound_eval(holding)
                for suit in range(N_SUITS):
                    if oks[suit](holding):
                        holdings[suit].setdefault((l, v), []).append(holding)
        counter = Counter()
        for lvs_hs in product(*[holdings[suit].items()
                                for suit in range(N_SUITS)]):
            lvs, hs = zip(*lvs_hs)
            ls, vs = zip(*lvs)
            if ls in shape and bound_eval.contains(sum(vs)):
                counter[ls, vs] += reduce(operator.mul, map(len, hs))
        patterns, cumsum = zip(*counter.items())
        cumsum = list(cumsum)
        for i in range(1, len(cumsum)):
            cumsum[i] += cumsum[i - 1]
        self.holdings = holdings
        self.patterns = patterns
        self.cumsum = cumsum
        self.total = cumsum[-1]

    @classmethod
    def from_predealt(cls, smartstack, predealt):
        by_suit = {suit: {card.rank for card in predealt if card.suit == suit}
                   for suit in range(N_SUITS)}
        oks = [(lambda holding, suit=suit:
                smartstack.shape.min_ls[suit] <= len(holding) <=
                    smartstack.shape.max_ls[suit] and
                not holding & by_suit[suit])
               for suit in range(N_SUITS)]
        return cls(smartstack.shape, oks, smartstack.bound_eval)

    def __call__(self):
        lvs = zip(*self.patterns[bisect(self.cumsum,
                                        random.randint(0, self.total - 1))])
        hand = [random.choice(holdings[ls, vs])
                for holdings, (ls, vs) in zip(self.holdings, lvs)]
        return [Card(suit, rank)
                for suit in range(N_SUITS) for rank in hand[suit]]


class SmartStack(object):
    def __init__(self, shape, bound_eval):
        self.shape = shape
        self.bound_eval = bound_eval
