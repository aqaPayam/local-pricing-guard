"""Small directed Decimal interval kernel for the prospective continuous study.

No binary floating economic calculation is used. Decimal exp/ln are correctly
rounded HALF_EVEN, so their endpoint values receive one outward nextafter pad.
This module is an implementation, not a claim of a formally verified library.
"""
from dataclasses import dataclass
from decimal import Decimal, Context, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
import math
import json

PRECISION = 80
DOWN = Context(prec=PRECISION, rounding=ROUND_FLOOR, Emin=-999999, Emax=999999)
UP = Context(prec=PRECISION, rounding=ROUND_CEILING, Emin=-999999, Emax=999999)
NEAR = Context(prec=PRECISION, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999)


def decimal(value):
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('Nonfinite imported binary64')
        return Decimal.from_float(value)
    return Decimal(value)


def fraction_decimal(value):
    """Exact terminating Fraction -> Decimal, without context rounding."""
    value = Fraction(value)
    numerator, denominator = value.numerator, value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        raise ValueError('Fraction does not have a terminating Decimal expansion')
    places = max(twos, fives)
    numerator *= 2 ** (places - twos) * 5 ** (places - fives)
    return Decimal((int(numerator < 0), tuple(map(int, str(abs(numerator)))), -places))


def exact_binary64(value):
    """Record the imported JSON number's binary64 value and exact ratio."""
    serialized = json.dumps(value, separators=(',', ':'), allow_nan=False)
    value = float(value)
    d = decimal(value)
    numerator, denominator = value.as_integer_ratio()
    return {'serialized': serialized, 'binary64Serialization': repr(value), 'exactDecimal': str(d),
            'numerator': str(numerator), 'denominator': str(denominator)}


@dataclass(frozen=True)
class Interval:
    lo: Decimal
    hi: Decimal

    def __init__(self, lo, hi=None):
        lo, hi = decimal(lo), decimal(lo if hi is None else hi)
        if not lo.is_finite() or not hi.is_finite() or lo > hi:
            raise ValueError('Invalid finite interval')
        object.__setattr__(self, 'lo', lo)
        object.__setattr__(self, 'hi', hi)

    @staticmethod
    def cast(other):
        return other if isinstance(other, Interval) else Interval(other)

    def __add__(self, other):
        other = self.cast(other)
        return Interval(DOWN.add(self.lo, other.lo), UP.add(self.hi, other.hi))

    __radd__ = __add__

    def __neg__(self):
        return Interval(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + (-self.cast(other))

    def __rsub__(self, other):
        return self.cast(other) - self

    def __mul__(self, other):
        other = self.cast(other)
        low = [DOWN.multiply(a, b) for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        high = [UP.multiply(a, b) for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return Interval(min(low), max(high))

    __rmul__ = __mul__

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ValueError('Division interval contains zero')
        return Interval(DOWN.divide(Decimal(1), self.hi), UP.divide(Decimal(1), self.lo))

    def __truediv__(self, other):
        return self * self.cast(other).reciprocal()

    def __rtruediv__(self, other):
        return self.cast(other) / self

    def exp(self):
        lower = NEAR.exp(self.lo)
        upper = NEAR.exp(self.hi)
        return Interval(NEAR.next_minus(lower), NEAR.next_plus(upper))

    def ln(self):
        if self.lo <= 0:
            raise ValueError('Logarithm requires a positive interval')
        lower = NEAR.ln(self.lo)
        upper = NEAR.ln(self.hi)
        return Interval(NEAR.next_minus(lower), NEAR.next_plus(upper))

    @property
    def width(self):
        return UP.subtract(self.hi, self.lo)

    @property
    def sign(self):
        return -1 if self.hi < 0 else 1 if self.lo > 0 else 0

    def contains(self, value):
        value = decimal(value)
        return self.lo <= value <= self.hi

    def hull(self, other):
        other = self.cast(other)
        return Interval(min(self.lo, other.lo), max(self.hi, other.hi))

    def json(self):
        return {'lower': str(self.lo), 'upper': str(self.hi), 'width': str(self.width)}


class Unresolved(ValueError):
    pass


def midpoint(a, b):
    return NEAR.divide(NEAR.add(a, b), Decimal(2))


def bisect_increasing(function, lower, upper, tolerance='1e-38', max_steps=600):
    """Enclose a unique continuous root with negative/positive signed endpoints.

    The historical function name denotes sign orientation, not a numerical
    derivative assertion. Existence/uniqueness and the negative-to-positive
    orientation must be supplied mathematically by the caller.
    Evidence retains independently recheckable endpoint evaluations. If a
    midpoint straddles zero, quarter-point evaluations avoid choosing its sign.
    """
    lower, upper, tolerance = decimal(lower), decimal(upper), decimal(tolerance)
    if not lower < upper or tolerance <= 0:
        raise ValueError('Invalid root bracket/tolerance')
    fl, fu = function(Interval(lower)), function(Interval(upper))
    if fl.sign != -1 or fu.sign != 1:
        raise Unresolved('Root bracket endpoints are not strictly sign-certified')
    steps = 0
    while UP.subtract(upper, lower) > tolerance:
        if steps >= max_steps:
            raise Unresolved('Root bisection budget exhausted')
        mid = midpoint(lower, upper)
        if not lower < mid < upper:
            raise Unresolved('Root bisection exhausted arithmetic resolution')
        fm = function(Interval(mid))
        if fm.sign < 0:
            lower, fl = mid, fm
        elif fm.sign > 0:
            upper, fu = mid, fm
        else:
            left, right = midpoint(lower, mid), midpoint(mid, upper)
            fleft, fright = function(Interval(left)), function(Interval(right))
            progress = False
            if fleft.sign == -1:
                lower, fl, progress = left, fleft, True
            if fright.sign == 1:
                upper, fu, progress = right, fright, True
            if not progress:
                raise Unresolved('Root sign ambiguity cannot be reduced safely')
        steps += 1
    return Interval(lower, upper), {'lowerEvaluation': fl.json(), 'upperEvaluation': fu.json(),
                                    'iterations': steps, 'orientation': 'negative below unique root; positive above'}


def lambert_w_positive(z, tolerance='1e-40'):
    """Positive principal W enclosure; monotone w exp(w), without special libs."""
    z = Interval.cast(z)
    if z.lo <= 0:
        raise ValueError('Positive Lambert-W input required')
    evidence = []
    bounds = []
    for endpoint in (z.lo, z.hi):
        hi = Decimal(1)
        while (Interval(hi) * Interval(hi).exp() - endpoint).sign != 1:
            hi = NEAR.multiply(hi, Decimal(2))
            if hi > 100000:
                raise Unresolved('Lambert-W expansion budget exhausted')
        root, proof = bisect_increasing(lambda w: w * w.exp() - endpoint, 0, hi, tolerance)
        bounds.append(root)
        evidence.append(proof)
    return Interval(bounds[0].lo, bounds[1].hi), evidence


def classify_floor(enclosure, threshold):
    enclosure, threshold = Interval.cast(enclosure), decimal(threshold)
    if enclosure.hi < threshold:
        return 'all-start failing continuation'
    if enclosure.lo >= threshold:
        return 'already guaranteed'
    return 'unresolved'
