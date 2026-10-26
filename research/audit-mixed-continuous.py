"""Independent continuous ingredients for the prospective mixed-timing audit.

Imports only the closed independent130-digit model/interval implementation.
New primary timing/search/calendar functions are never imported. Merely
importing this module reads no inherited numerical evidence. Shared Decimal
transcendentals remain an explicit limitation, not formal verification.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('closed_mixed_interval_backend', ROOT/'research/audit-continuous-study.py')
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)
B = backend.Box
MAX_K, PREFIX_TERMS = 65536, 64


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fraction(value):
    if isinstance(value, dict):
        return Fraction(int(value['numerator']), int(value['denominator']))
    if isinstance(value, float):
        return Fraction.from_float(value)
    return Fraction(value)


def exact_bounds(box):
    def pair(value):
        value = Fraction(value)
        return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}
    return {'lower': pair(box.low), 'upper': pair(box.high)}


def enclosure_contains(saved, independent, label):
    candidate = B(saved['lower'], saved['upper'])
    require(candidate.low <= independent.low and candidate.high >= independent.high,
            label+' independently enclosed')
    return candidate


def nonnegative_power(value, exponent):
    require(isinstance(exponent, int) and exponent >= 0 and value.low >= 0,
            'Nonnegative interval power')
    result = B(1)
    while exponent:
        if exponent & 1:
            result = result*value
        value = value*value
        exponent >>= 1
    return result


def scalar_root_signs(model, proof, rival):
    """Validate a supplied upper root by independent log-W/profit signs."""
    require(fraction(proof['rivalExact']) == Fraction(rival), 'Exact rival endpoint for scalar root')
    y = B(rival)
    w = backend.enclosure(proof['bestProfitW'])
    require(w.low > 0, 'Positive best-profit bracket')
    target_log = -(B(1)+(model.k+(-y).exp()).log())
    residual = lambda z: B(z)+B(z).log()-target_log
    require(residual(w.low).sign == -1 and residual(w.high).sign == 1,
            'Independent best-profit log-W endpoint signs')
    enclosure_contains(proof['bestResponse'], 1+w, 'Best response')
    threshold = w-model.t
    require(threshold.low > 0, 'Positive guarded target profit')
    enclosure_contains(proof['normalizedTargetProfit'], threshold, 'Guard target')
    root = backend.enclosure(proof['normalizedPrice'])
    require(Fraction(root.high)-Fraction(root.low) <= Fraction('1e-25'), 'Upper root width')
    require(root.low > 1+w.high and Fraction(root.high) <= model.high,
            'Upper branch and original price ceiling')
    actual_profit = lambda z: B(z)/(1+(model.k+(-y).exp())*B(z).exp())
    r = lambda z: threshold-actual_profit(z)
    kind = proof['proof']['kind']
    if kind == 'interior upper root':
        require(r(root.low).sign == -1 and r(root.high).sign == 1,
                'Independent upper-root profit endpoint signs')
    elif kind == 'ceiling-clipped':
        require(Fraction(root.low) == model.high == Fraction(root.high), 'Exact ceiling clipping')
        require(r(root.high).sign == -1, 'Guard feasible at clipping ceiling')
    else:
        raise ValueError('Unknown scalar upper-root proof')
    return root


def validate_orbit(record, guard, inherited_continuum, physical_cap):
    """Check64 propagation/reward rows and128 scalar-root sign certificates.

    Global monotonicity/contraction premises and q_star/C_star/rho certificates
    are REUSED from the accepted hash-bound old continuum audit, not recomputed
    by this helper. The real-data adapter must verify that inherited binding
    and disclose it. The root signs, orbit propagation and used new sums below
    are independently recalculated with the closed130-digit model code.
    """
    require(record['continuum'] in ('effective', 'nominal'), 'Declared continuum interpretation')
    require(record['scenario'] == guard['scenario']['id'] == inherited_continuum['scenario'],
            'Same continuous economic identity')
    model = backend.AuditEconomy(guard, record['continuum'])
    cap = (fraction(physical_cap)-model.values['cost'])/model.values['mu']
    require(fraction(record['normalizedCapExact']) == cap, 'Same physical normalized cap')
    current = B.rational(cap)
    fixed = backend.enclosure(inherited_continuum['worst']['normalizedPrice'])
    cstar = backend.enclosure(inherited_continuum['worst']['consumerSurplus'])
    rho = backend.enclosure(inherited_continuum['assumptions']['rho'])
    require(model.ell <= cap and current.high < fixed.low and rho.low >= 0 and rho.high < 1,
            'Cap below fixed point and declared contraction')
    require(record['prefixTerms'] == PREFIX_TERMS and len(record['orbit']) == PREFIX_TERMS,
            'Exactly the closed64 orbit terms')
    rewards = []
    for index, step in enumerate(record['orbit']):
        require(step['j'] == index, 'Consecutive executed orbit indices')
        enclosure_contains(step['executedNormalizedPrice'], current, 'Current normalized price')
        enclosure_contains(step['executedPrice'], model.cost+model.mu*current, 'Current physical price')
        reward = model.diagonal_cs(current)
        enclosure_contains(step['consumerSurplus'], reward, 'Executed reward')
        left = scalar_root_signs(model, step['upperMapProof']['lowerEndpoint'], current.low)
        right = scalar_root_signs(model, step['upperMapProof']['upperEndpoint'], current.high)
        following = B(left.low, right.high)
        enclosure_contains(step['nextNormalizedPrice'], following, 'Next orbit price')
        require(following.high >= current.low, 'Nondecreasing orbit enclosure consistency')
        if index == 0:
            require(following.low > current.high, 'Strict first upward orbit step')
        rewards.append(reward)
        current = following
    enclosure_contains(record['aJ'], current, 'Closed a64')
    gap = fixed-current
    require(gap.high >= 0, 'Orbit remains consistent with upper fixed point')
    distance = B(max(Decimal(0), gap.low), gap.high)
    enclosure_contains(record['qStarMinusAJ'], distance, 'Orbit-to-fixed-point distance')
    return {'model': model, 'rewards': rewards, 'cstar': cstar, 'rho': rho,
            'distance': distance, 'lastPrice': current, 'fixed': fixed}


def bounded_sum(orbit, length):
    """Independent prefix plus contraction tail; never queries length65537."""
    require(isinstance(length, int) and 1 <= length <= MAX_K, 'Bounded mixed-gap sum length')
    terms = orbit['rewards']
    require(len(terms) == PREFIX_TERMS, 'Closed prefix length')
    total = sum(terms[:min(length, PREFIX_TERMS)], B(0))
    if length > PREFIX_TERMS:
        count = length-PREFIX_TERMS
        rho = B(orbit['rho'].high)
        geometric = (1-nonnegative_power(rho, count))/(1-rho)
        excess = orbit['model'].scale*orbit['distance']*geometric
        total += count*orbit['cstar']+B(0, excess.high)
    return total


def validate_sum_bounds(saved, independent, label):
    lo, hi = fraction(saved['lower']), fraction(saved['upper'])
    require(lo <= Fraction(independent.low) and hi >= Fraction(independent.high),
            label+' includes independently calculated sum')
    return lo, hi


def verify_payload(payload):
    """Read-only helper entry; all input objects are supplied by the JS audit."""
    orbit = validate_orbit(payload['record'], payload['guard'], payload['inherited'],
                           payload['physicalCap'])
    periods = payload['periods']
    require(periods == sorted(set(periods)), 'Unique sorted queried lengths')
    return {'passed': True, 'scalarRootCertificates': 128, 'orbitTerms': 64,
            'inheritedPremiseRevalidation': False,
            'inheritedPremiseScope': 'Global monotonicity/contraction and q_star/C_star/rho certificates reused from accepted hash-bound old continuum audit; not recomputed here',
            'sumBounds': [{'period': k, 'bounds': exact_bounds(bounded_sum(orbit, k))} for k in periods],
            'newCheckScope': 'Independent128 scalar root signs,64 executed price/reward propagation rows and every used64-prefix/contraction-tail sum; common Decimal backend'}


if __name__ == '__main__':
    require(sys.argv[1:] == ['--verify-input'], 'Use --verify-input with a JSON object on stdin')
    print(json.dumps(verify_payload(json.load(sys.stdin)), separators=(',', ':')))
