"""Pure prospective exact aggregation. No IO, training or evidence acceptance.

The later audit-gated adapter supplies the normalized final endpoints below.
This module cannot establish replay acceptance merely from supplied booleans.
"""
from fractions import Fraction
import re

SEEDS = tuple(range(907001, 907013))
ARMS = ('startup', 'recurring4')


def exact(value):
    if not isinstance(value, dict) or set(value) != {'numerator', 'denominator'}:
        raise ValueError('Exact fraction shape differs')
    n, d = value['numerator'], value['denominator']
    if not isinstance(n, str) or not re.fullmatch(r'0|-?[1-9][0-9]*', n):
        raise ValueError('Noncanonical exact numerator')
    if not isinstance(d, str) or not re.fullmatch(r'[1-9][0-9]*', d):
        raise ValueError('Noncanonical positive denominator')
    out = Fraction(int(n), int(d))
    if str(out.numerator) != n or str(out.denominator) != d:
        raise ValueError('Exact fraction is not reduced')
    return out


def packed(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def normalized_run_id(seed, arm):
    if seed not in SEEDS or arm not in ARMS:
        raise ValueError('Unexpected planned identity')
    return f'base-g15-t1--matched5-{arm}--zero--s{seed}'


def aggregate(final_endpoints):
    """Aggregate exactly24 normalized endpoints; retain all12 planned pairs.

    Endpoint keys: seed, arm, runId, executionSucceeded, available,
    replayMatched, cycleCustomerBenefit, unavailableReason. Available endpoints
    additionally carry step=2M, nextPhase=4, previousIndices[2], cycleLength and
    checkpointSha256/graphSha256. Other source metadata is preserved by callers.
    """
    endpoints = list(final_endpoints)
    if len(endpoints) != 24:
        raise ValueError('All24 planned final endpoint slots must be retained')
    by_identity = {}
    for entry in endpoints:
        if not isinstance(entry, dict):
            raise ValueError('Endpoint must be a mapping')
        seed, arm = entry.get('seed'), entry.get('arm')
        if type(seed) is not int or entry.get('runId') != normalized_run_id(seed, arm):
            raise ValueError('Final run identity differs')
        identity = (seed, arm)
        if identity in by_identity:
            raise ValueError('Duplicated final endpoint')
        for key in ('executionSucceeded', 'available', 'replayMatched'):
            if type(entry.get(key)) is not bool:
                raise ValueError('Availability/execution/replay must be explicit booleans')
        if entry['available']:
            if not entry['replayMatched'] or entry.get('unavailableReason') is not None:
                raise ValueError('Available endpoint lacks replay or has failure reason')
            if type(entry.get('step')) is not int or entry['step'] != 2_000_000 or type(entry.get('nextPhase')) is not int or entry['nextPhase'] != 4:
                raise ValueError('Primary final step/NEXT phase differs')
            previous = entry.get('previousIndices')
            if not isinstance(previous, list) or len(previous) != 2 or any(
                    type(x) is not int or not 0 <= x < 62 for x in previous):
                raise ValueError('Actual terminal history is missing')
            length = entry.get('cycleLength')
            if type(length) is not int or not 1 <= length <= 4 * 62 * 62 or length % 4:
                raise ValueError('Cyclic phase cycle length differs')
            for key in ('checkpointSha256', 'graphSha256'):
                if not isinstance(entry.get(key), str) or not re.fullmatch(r'[a-f0-9]{64}', entry[key]):
                    raise ValueError('Endpoint identity hash is missing')
            exact(entry.get('cycleCustomerBenefit'))
        else:
            if entry.get('cycleCustomerBenefit') is not None or not isinstance(
                    entry.get('unavailableReason'), str) or not entry['unavailableReason'].strip():
                raise ValueError('Unavailable outcome must be null with a reason')
        by_identity[identity] = entry
    if set(by_identity) != {(seed, arm) for seed in SEEDS for arm in ARMS}:
        raise ValueError('Planned identities differ')

    paired, values, available_seeds = [], [], []
    for seed in SEEDS:
        a, b = (by_identity[(seed, arm)] for arm in ARMS)
        available = a['available'] and b['available']
        difference = exact(b['cycleCustomerBenefit']) - exact(a['cycleCustomerBenefit']) if available else None
        reasons = [f"{x['arm']}: {x['unavailableReason']}" for x in (a, b) if not x['available']]
        paired.append(dict(seed=seed, runIds=[a['runId'], b['runId']], available=available,
                           executionSucceeded=[a['executionSucceeded'], b['executionSucceeded']],
                           replayMatched=[a['replayMatched'], b['replayMatched']],
                           cycleCustomerBenefits=[x['cycleCustomerBenefit'] for x in (a, b)],
                           difference=packed(difference) if available else None,
                           differenceApprox=float(difference) if available else None,
                           unavailableReason='; '.join(reasons) if reasons else None))
        if available:
            values.append(difference)
            available_seeds.append(seed)
    complete = len(values) == 12
    sign_counts = {name: sum(predicate(v) for v in values) for name, predicate in (
        ('positive', lambda v: v > 0), ('zero', lambda v: v == 0), ('negative', lambda v: v < 0))}
    return dict(
        pairedRows=paired,
        primarySummary=dict(plannedDenominator=12, availablePairs=len(values),
                            available=complete, meanDifference=packed(sum(values, Fraction()) / 12) if complete else None,
                            unavailableReason=None if complete else 'At least one planned final pair lacks two accepted endpoints'),
        completePairDescription=dict(scope='Secondary description of available whole-market seed pairs; not a replacement primary estimate',
                                     denominator=len(values), seedIds=available_seeds, signCounts=sign_counts,
                                     meanDifference=packed(sum(values, Fraction()) / len(values)) if values else None),
    )
