from bisect import bisect
from collections import Counter
from functools import reduce
from itertools import combinations, product
import operator
import random

from .global_defs import Card, Rank, Suit


class SmartStack:
    def __init__(self, shape, evaluator, values, predealt=None):
        self._shape = shape
        self._evaluator = evaluator
        self._values = values
        self._predealt = predealt
        self._prepared = False

    def _prepare(self):
        # holdings[i][l, v]:
        #     OK holdings for suit #i such that len(h) = l, eval_holding(h) = v
        self._prepared = True
        by_suit = {suit: {card.rank for card in (self._predealt or {})
                          if card.suit == suit}
                   for suit in Suit}
        holdings = [{} for _ in Suit]
        for l in range(len(Rank)):
            for holding in map(frozenset, combinations(Rank, l)):
                v = self._evaluator(holding)
                for suit in Suit:
                    if (self._shape.min_ls[suit] <= len(holding)
                            <= self._shape.max_ls[suit]
                            and not holding & by_suit[suit]):
                        holdings[suit].setdefault((l, v), []).append(holding)
        counter = Counter()
        for lvs_hs in product(*[holdings[suit].items() for suit in Suit]):
            lvs, hs = zip(*lvs_hs)
            ls, vs = zip(*lvs)
            if ls in self._shape and sum(vs) in self._values:
                counter[ls, vs] += reduce(operator.mul, map(len, hs))
        patterns, cumsum = zip(*counter.items())
        cumsum = list(cumsum)
        for i in range(1, len(cumsum)):
            cumsum[i] += cumsum[i - 1]
        self.holdings = holdings
        self.patterns = patterns
        self.cumsum = cumsum
        self.total = cumsum[-1]

    def __call__(self):
        if not self._prepared:
            self._prepare()
        lvs = zip(*self.patterns[bisect(self.cumsum,
                                        random.randint(0, self.total - 1))])
        hand = [random.choice(holdings[ls, vs])
                for holdings, (ls, vs) in zip(self.holdings, lvs)]
        return [Card(suit, rank) for suit in Suit for rank in hand[suit]]
