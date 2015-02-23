# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
from array import array
from bisect import bisect
from itertools import count, permutations, product
from math import sqrt
import random
import sys
if sys.version_info.major < 3:
    from itertools import ifilter as filter

try:
    from colorama import Fore, Style
    BRIGHT_GREEN = Style.BRIGHT + Fore.GREEN
    BRIGHT_RED = Style.BRIGHT + Fore.RED
    RESET_ALL = Style.RESET_ALL
except ImportError:
    BRIGHT_GREEN = BRIGHT_RED = RESET_ALL = ""

from . import global_defs, dds, util
from .global_defs import *
from .smartstack import SmartStack, _SmartStack


__all__ = ["Shape", "balanced", "semibalanced",
           "Evaluator", "hcp", "qp", "controls",
           "RANKS", "A", "K", "Q", "J", "T",
           "Card", "Holding", "Hand", "H", "Deal", "SmartStack",
           "Contract", "C", "matchpoints", "imps", "Payoff",
           "Simulation", "OpeningLeadSim",]


for i, suit in enumerate(SUITS):
    for j, rank in enumerate(RANKS):
        globals()[suit + rank] = Card(i, j)
del i, j, suit, rank


class Shape(object):
    """A shape specification, as a 0-1 table, intended as immutable.

    :attr:`min_ls` and :attr:`max_ls` are hints for smartstacking,
    guaranteed to be correct but not necessarily optimal. :attr:`_cls_cache`
    and :attr:`_op_cache` cache :class:`Shape` instantiations and
    additions/substractions -- this avoids repetitive instantations in the
    ``accept`` function of a simulation, for example..
    """

    JOKER = "x"
    TABLE = {JOKER: -1, "t": 10, "j": 11, "q": 12, "k": 13, "(": "(", ")": ")"}
    TABLE.update({str(n): n for n in range(10)})
    _cls_cache = {}

    def __new__(cls, init=None):
        """Initialize with a string.
        """
        try:
            return cls._cls_cache[init]
        except KeyError:
            self = object.__new__(cls)
            self.table = array(str("b"))
            self.table.fromlist([0] * (PER_SUIT + 1) ** N_SUITS)
            self.min_ls = [PER_SUIT for _ in range(N_SUITS)]
            self.max_ls = [0 for _ in range(N_SUITS)]
            self._op_cache = {}
            if init:
                self.insert([self.TABLE[char.lower()] for char in init])
                cls._cls_cache[init] = self
            return self

    @classmethod
    def from_table(cls, table, min_max_hint=None):
        """Initialize from a table.
        """
        self = cls()
        self.table = array(str("b"))
        self.table.fromlist(list(table))
        if min_max_hint is not None:
            self.min_ls, self.max_ls = min_max_hint
        else:
            self.min_ls = [PER_SUIT for _ in range(N_SUITS)]
            self.max_ls = [0 for _ in range(N_SUITS)]
            for nonflat in product(*[range(PER_SUIT + 1)
                                     for _ in range(N_SUITS)]):
                if self.table[self._flatten(nonflat)]:
                    for dim, coord in enumerate(nonflat):
                        self.min_ls[dim] = min(self.min_ls[dim], coord)
                        self.max_ls[dim] = max(self.max_ls[dim], coord)
        return self

    @classmethod
    def from_cond(cls, func):
        """Initialize from a shape-accepting function.
        """
        self = cls()
        for nonflat in product(*[range(PER_SUIT + 1)
                                 for _ in range(N_SUITS)]):
            if sum(nonflat) == PER_SUIT and func(*nonflat):
                self.table[self._flatten(nonflat)] = True
                for dim, coord in enumerate(nonflat):
                    self.min_ls[dim] = min(self.min_ls[dim], coord)
                    self.max_ls[dim] = max(self.max_ls[dim], coord)
        return self

    @staticmethod
    def _flatten(index):
        """Transform a 4D index into a 1D index.
        """
        s, h, d, c = index
        mul = PER_SUIT + 1
        return ((((s * mul + h) * mul) + d) * mul) + c

    def _insert1(self, shape, safe=True):
        """Insert an element, possibly with "x" but no "()" terms.
        """
        jokers = any(l == -1 for l in shape)
        pre_set = sum(l for l in shape if l >= 0)
        if not jokers:
            if pre_set == PER_SUIT:
                self.table[self._flatten(shape)] = 1
                for suit in range(N_SUITS):
                    self.min_ls[suit] = min(self.min_ls[suit], shape[suit])
                    self.max_ls[suit] = max(self.max_ls[suit], shape[suit])
            elif safe:
                raise Exception("Wrong number of cards in shape.")
        else:
            if pre_set > PER_SUIT:
                raise Exception("Invalid ambiguous shape.")
            for i, l in enumerate(shape):
                if l == -1:
                    for ll in range(PER_SUIT - pre_set + 1):
                        self._insert1(shape[:i] + (ll,) + shape[i+1:],
                                     safe=False)

    def insert(self, it, acc=()):
        """Insert an element, possibly with "()" or "x" terms.
        """
        if not it:
            self._insert1(acc, safe=False)
            return
        if it[0] == "(":
            try:
                closing = it.index(")")
            except ValueError:
                raise Exception("Unbalanced parentheses.")
            head, it = it[1:closing], it[closing+1:]
        else:
            head, it = it[0:1], it[1:]
        for perm in permutations(head):
            self.insert(it, acc + perm)

    def __contains__(self, int_shape):
        """Check if the given shape is included.
        """
        return self.table[self._flatten(int_shape)]

    def __call__(self, hand):
        """Check if the shape of the given hand is included.
        """
        return hand.shape in self

    def __add__(self, other):
        """Return the union of two ``Shapes``.
        """
        try:
            return self._op_cache["+", other]
        except KeyError:
            table = array(str("b"))
            table.fromlist([x or y for x, y in zip(self.table, other.table)])
            min_ls = [min(self.min_ls[suit], other.min_ls[suit])
                      for suit in range(N_SUITS)]
            max_ls = [max(self.max_ls[suit], other.max_ls[suit])
                      for suit in range(N_SUITS)]
            result = Shape.from_table(table, (min_ls, max_ls))
            self._op_cache["+", other] = result
            return result

    def __sub__(self, other):
        """Remove one ``Shape`` from another.
        """
        try:
            return self._op_cache["-", other]
        except KeyError:
            table = array("b")
            table.fromlist(
                [x and not y for x, y in zip(self.table, other.table)])
            result = Shape.from_table(table, (self.min_ls, self.max_ls))
            self._op_cache["-", other] = result
            return result


balanced = Shape("(4333)") + Shape("(4432)") + Shape("(5332)")
semibalanced = balanced + Shape("(5422)") + Shape("(6322)")


class Evaluator(object):
    """Additive holding evaluator.

    For example, ``Evaluator(4, 3, 2, 1)(holding)`` returns the HCPs of
    ``holding``.
    """

    def __init__(self, *vals, **kwargs):
        self._vals = vals + (0,) * (PER_SUIT - len(vals))
        self._le = kwargs.pop("le", None)
        self._ge = kwargs.pop("ge", None)

    def __call__(self, arg):
        if isinstance(arg, frozenset): # Holding
            return sum(self._vals[rank] for rank in arg)
        elif isinstance(arg, tuple): # Hand
            return sum(self(holding) for holding in arg)
        else:
            raise TypeError("Cannot evaluate {}".format(arg))

    def __eq__(self, value):
        if self._le is not None or self._ge is not None:
            raise Exception("Already bound")
        return type(self)(*self._vals, le=value, ge=value)

    def __le__(self, value):
        if self._le is not None:
            raise Exception("Already bound by {}".format(self._le))
        return type(self)(*self._vals, le=value, ge=self._ge)

    def __ge__(self, value):
        if self._ge is not None:
            raise Exception("Already bound by {}".format(self._ge))
        return type(self)(*self._vals, le=self._le, ge=value)

    def contains(self, value):
        return ((self._le is None or value <= self._le) and
                (self._ge is None or value >= self._ge))


hcp = Evaluator(4, 3, 2, 1)
hcp.__name__ = "hcp"
qp = Evaluator(3, 2, 1)
qp.__name__ = "qp"
controls = Evaluator(2, 1)
controls.__name__ = "controls"


class Deal(tuple, object):
    """A deal, represented as a tuple of hands.
    """

    LONG, SHORT = range(2)

    @staticmethod
    def prepare(predeal):
        """Contruct a dealer from a ``seat -> [Hand | SmartStack]`` dict.

        There can be at most one ``SmartStack`` entry.
        """
        predeal = predeal or {}
        dealer = {}
        seat_smartstack = None
        for seat in SEATS:
            pre = predeal.get(seat, Hand(()))
            if isinstance(pre, SmartStack):
                if seat_smartstack:
                    raise Exception("Only one Smartstack allowed.")
                seat_smartstack = seat, pre
            else:
                dealer[seat] = pre.cards
        predealt = [card for hand_cards in dealer.values()
                    for card in hand_cards()]
        predealt_set = set(predealt)
        if len(predealt_set) < len(predealt):
            raise Exception("Same card dealt twice.")
        if seat_smartstack:
            seat, smartstack = seat_smartstack
            dealer[seat] = _SmartStack.from_predealt(smartstack, predealt)
            dealer["_smartstack"] = seat
        dealer["_remaining"] = [card for card in FULL_DECK
                                if card not in predealt_set]
        return lambda: Deal(dealer)

    def __new__(cls, dealer):
        """Randomly deal a hand from a prepared dealer.
        """
        hands = [None] * N_SEATS
        cards = dealer["_remaining"]
        try:
            seat = dealer["_smartstack"]
        except KeyError:
            pass
        else:
            hands[SEATS.index(seat)] = hand = Hand(dealer[seat]())
            cards = list(set(cards).difference(hand.cards()))
        random.shuffle(cards)
        for seat in SEATS:
            if hands[SEATS.index(seat)]:
                continue
            pre = dealer[seat]()
            to_deal = PER_SUIT - len(pre)
            hand, cards = pre + cards[:to_deal], cards[to_deal:]
            hands[SEATS.index(seat)] = Hand(hand)
        self = tuple.__new__(cls, hands)
        self._dd_cache = {}
        return self

    def _short_str(self):
        """Return a one-line version of the deal.
        """
        return " ".join(self[SEATS.index(hand)]._short_str()
                        for hand in self._print_only)

    def _long_str(self):
        """Return pretty-printed version of the deal.
        """
        s = ""
        if "N" in self._print_only:
            for line in self.north._long_str().split("\n"):
                s += " " * 7 + line + "\n"
        for line_w, line_e in zip(self.west._long_str().split("\n"),
                                  self.east._long_str().split("\n")):
            s += ((line_w if "W" in self._print_only else "").ljust(14) +
                  (line_e if "E" in self._print_only else "") + "\n")
        if "S" in self._print_only:
            for line in self.south._long_str().split("\n"):
                s += " " * 7 + line + "\n"
        return s

    def _pbn(self):
        """Return the deal in PBN format.
        """
        return "{}:{}".format(
            SEATS[0], " ".join(".".join(str(holding) for holding in hand)
                               for hand in self))

    __str__ = _short_str

    @classmethod
    def set_str_style(cls, style):
        """Set output style (:attr:`Deal.SHORT` or :attr:`Deal.LONG`).
        """
        cls.__str__ = {cls.SHORT: cls._short_str,
                       cls.LONG: cls._long_str}[style]

    @classmethod
    def set_print_only(cls, hands):
        assert all(hand in SEATS for hand in hands)
        cls._print_only = hands

    _N = SEATS.index("N")
    _E = SEATS.index("E")
    _S = SEATS.index("S")
    _W = SEATS.index("W")
    north = property(lambda self: self[self._N])
    east = property(lambda self: self[self._E])
    south = property(lambda self: self[self._S])
    west = property(lambda self: self[self._W])

    def dd_tricks(self, contract_declarer):
        """Compute declarer's number of double-dummy tricks in a contract.
        """
        strain = Contract.from_str(contract_declarer[:-1]).strain
        declarer = contract_declarer[-1]
        if (strain, declarer) not in self._dd_cache:
            self._dd_cache[strain, declarer] = dds.solve(self, strain, declarer)
        return self._dd_cache[strain, declarer]

    def dd_score(self, contract_declarer, vul=False):
        """Compute declarer's double-dummy score in a contract.
        """
        return Contract.from_str(contract_declarer[:-1], vul=vul).score(
            self.dd_tricks(contract_declarer))

    def dd_all_tricks(self, strain, leader):
        """Compute declarer's number of double dummy tricks for all leads.
        """
        return dds.solve_all(self, strain, leader)


class Hand(tuple, object):
    """A hand, represented as a tuple of holdings.
    """

    LONG, SHORT = range(2)

    def __new__(cls, cards):
        """Initialize with a sequence of :class:`Cards <Card>`.
        """
        if len(cards) > PER_SUIT:
            raise ValueError("More than {} cards in a hand".format(PER_SUIT))
        return tuple.__new__(
            cls,
            (Holding(card for card in cards if card.suit == suit)
             for suit in range(N_SUITS)))

    @classmethod
    def from_str(cls, init):
        """Initialize with a string, e.g. "AK432 K87 QJT54 -".
        """
        suits = [holding if holding != "-" else "" for holding in init.split()]
        if (len(suits) != N_SUITS or
            not all(rank in RANKS for holding in suits for rank in holding)):
            raise Exception("Invalid initializer for Hand.")
        cards = [Card(suit=suit, rank=RANKS.index(rank.upper()))
                 for suit, holding in enumerate(suits) for rank in holding]
        return cls(cards)

    def to_str(self):
        """Inverse of :meth:`from_str`.
        """
        return " ".join(str(holding) if holding else "-" for holding in self)

    def _short_str(self):
        """Return a one-line version of the hand.
        """
        return "".join(suit_symbol + str(holding)
                       for suit_symbol, holding
                       in zip(global_defs.SUITS_SYM, self))

    def _long_str(self):
        """Return a pretty-printed version of the hand.
        """
        return "\n" + "\n".join(suit_symbol + str(holding)
            for suit_symbol, holding in zip(global_defs.SUITS_SYM, self))

    __str__ = _short_str

    @classmethod
    def set_str_style(cls, style):
        """Set output style (:attr:`Hand.SHORT` or :attr:`Hand.LONG`).
        """
        cls.__str__ = {cls.SHORT: cls._short_str,
                       cls.LONG: cls._long_str}[style]

    def cards(self):
        """Return ``self`` as a list of card objects.
        """
        return [Card(suit, rank)
                for suit in range(N_SUITS) for rank in self[suit]]

    def __contains__(self, other):
        """Specialize the case of checking for containing a :class:`Card`.
        """
        if isinstance(other, Card):
            return other.rank in self[other.suit]
        else:
            return tuple.__contains__(self, other)

    _S = SUITS.index("S")
    _H = SUITS.index("H")
    _D = SUITS.index("D")
    _C = SUITS.index("C")
    spades = util.reify(lambda self: self[self._S], "The hand's spades.")
    hearts = util.reify(lambda self: self[self._H], "The hand's hearts.")
    diamonds = util.reify(lambda self: self[self._D], "The hand's diamonds.")
    clubs = util.reify(lambda self: self[self._C], "The hand's clubs.")

    shape = util.reify(lambda self: [len(holding) for holding in self],
                       "The hand's shape.")
    hcp = util.reify(lambda self: sum(holding.hcp for holding in self),
                     "The hand's HCP count.")
    qp = util.reify(lambda self: sum(holding.qp for holding in self),
                    "The hand's QP count.")
    losers = util.reify(lambda self: sum(holding.losers for holding in self),
                        "The hand's loser count.")


A, K, Q, J, T = [RANKS.index(rank) for rank in "AKQJT"]
class Holding(frozenset, object):
    """A one-suit holding, represented as a frozenset of card ranks.
    """

    def __new__(cls, cards):
        """Initialize with a sequence of :class:`Cards <Card>`.
        """
        return frozenset.__new__(cls, (card.rank for card in cards))

    def __str__(self):
        return "".join(RANKS[rank] for rank in sorted(self))

    hcp = util.reify(hcp, "The holding's HCP.")
    qp = util.reify(qp, "The holding's QP.")

    @util.reify
    def losers(self):
        """The holding's loser count.
        """
        if len(self) == 0:
            return 0
        losers = 0
        if not any(rank == A for rank in self):
            losers += 1
        if len(self) >= 2 and not any(rank == K for rank in self):
            losers += 1
        if len(self) >= 3:
            if not any(rank == Q for rank in self):
                losers += 1
            elif (losers == 2 and
                  not any(rank in [J, T] for rank in self)):
                losers += 0.5
        return losers


class Contract(object):
    def __init__(self, level, strain, doubled=0, vul=False):
        if not (1 <= level <= 7 and strain in STRAINS and 0 <= doubled <= 2):
            raise ValueError("Invalid contract")
        self.level = level
        self.strain = strain
        self.doubled = doubled
        self.vul = vul

    @classmethod
    def from_str(cls, s, vul=False):
        """Initialize with a string, e.g. "7NXX".  Vulnerability still a kwarg.
        """
        doubled = len(s) - len(s.rstrip("xX"))
        return cls(int(s[0]), s[1].upper(), doubled=doubled, vul=vul)

    def score(self, tricks):
        """Score for a contract for a given number of tricks taken.
        """
        target = self.level + 6
        overtricks = tricks - target
        if overtricks >= 0:
            per_trick = 20 if self.strain in ["C", "D"] else 30
            base_score = per_trick * self.level
            bonus = 0
            if self.strain == "N":
                base_score += 10
            if self.doubled == 1:
                base_score *= 2
                bonus += 50
            if self.doubled == 2:
                base_score *= 4
                bonus += 100
            bonus += [300, 500][self.vul] if base_score >= 100 else 50
            if self.level == 6:
                bonus += [500, 750][self.vul]
            elif self.level == 7:
                bonus += [1000, 1500][self.vul]
            if not self.doubled:
                per_overtrick = per_trick
            else:
                per_overtrick = [100, 200][self.vul] * self.doubled
            overtricks_score = overtricks * per_overtrick
            return base_score + overtricks_score + bonus
        else:
            if not self.doubled:
                per_undertrick = [50, 100][self.vul]
                return overtricks * per_undertrick
            else:
                if overtricks == -1:
                    score = [-100, -200][self.vul]
                elif overtricks == -2:
                    score = [-300, -500][self.vul]
                else:
                    score = 300 * overtricks + [400, 100][self.vul]
            if self.doubled == 2:
                score *= 2
            return score


H = Hand.from_str
C = Contract.from_str


def matchpoints(my, other):
    """Return matchpoints scored (-1 to 1) given our and their result.
    """
    return (my > other) - (my < other)


def imps(my, other):
    """Return IMPs scored given our and their results.
    """
    imp_table = [15, 45, 85, 125, 165, 215, 265, 315, 365, 425, 495, 595,
        745, 895, 1095, 1295, 1495, 1745, 1995, 2245, 2495, 2995, 3495, 3995]
    return bisect(imp_table, abs(my - other)) * (1 if my > other else -1)


class Simulation(object):
    """The default simulation.
    """

    def initial(self):
        pass

    def accept(self, deal):
        return True

    def do(self, deal):
        print(format(deal, "")) # Unicode on Python 2.

    def final(self, n_tries):
        print("Tries: {}".format(n_tries))


class OpeningLeadSim(Simulation):
    def __init__(self, accept, contract_declarer, scoring):
        self.accept = accept
        self.leader = SEATS[(SEATS.index(contract_declarer[-1]) + 1) % N_SEATS]
        contract = Contract.from_str(contract_declarer[:-1])
        self.strain = contract.strain
        self.scoring = lambda ti, tj: scoring(contract.score(ti),
                                              contract.score(tj))

    def initial(self, dealer):
        deal = next(filter(self.accept, (dealer() for _ in count())))
        self.payoff = Payoff(
            sorted(dds.valid_cards(deal, self.strain, self.leader)),
            self.scoring)

    def do(self, deal):
        self.payoff.add_data(deal.dd_all_tricks(self.strain, self.leader))

    def final(self, n_tries):
        self.payoff.report()


class Payoff(object):
    """A payoff table for comparing multiple strategies.
    """

    def __init__(self, entries, diff):
        """Initialize with a list of strategy names and a difference function.
        """
        self.entries = entries
        self.diff = diff
        self.table = [[[] for _0 in entries] for _1 in entries]

    def add_data(self, raw_scores):
        """Add a realization of the scores as a strategy -> raw scores dict.
        """
        for i, ei in enumerate(self.entries):
            for j, ej in enumerate(self.entries):
                self.table[i][j].append(
                    self.diff(raw_scores[ei], raw_scores[ej]))

    def report(self):
        """Pretty-print a payoff table.
        """
        means_stderrs = [[(mean(score), stderr(score)) for score in line]
                         for line in self.table]
        print("\t" + "".join("{:.7}\t".format(entry) for entry in self.entries))
        for i, (entry, line) in enumerate(zip(self.entries, means_stderrs)):
            print("{:.7}".format(entry),
                  *("{}{:+.2f}{}".format(
                      BRIGHT_GREEN if mean > stderr
                      else BRIGHT_RED if mean < -stderr
                      else "",
                      mean, RESET_ALL)
                    if i != j else ""
                    for j, (mean, stderr) in enumerate(line)),
                  sep="\t")
            print("",
                  *("({:.2f})".format(stderr) if i != j else ""
                    for j, (mean, stderr) in enumerate(line)),
                  sep="\t")


mean = lambda l: sum(l) / len(l)
stderr = (lambda l:
          sqrt((mean([s ** 2 for s in l]) - mean(l) ** 2) / len(l)))
