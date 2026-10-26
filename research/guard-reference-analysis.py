"""Prospective pure exact anchors and paired aggregation; no IO or execution."""
from fractions import Fraction
import math
import re

SEEDS = tuple(range(907001, 907013))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def packed(v):
    return dict(numerator=str(v.numerator), denominator=str(v.denominator))


def ratio(v):
    need(isinstance(v, dict) and set(v) == {'numerator', 'denominator'}, 'Canonical exact fraction required')
    n, d = v['numerator'], v['denominator']
    need(isinstance(n, str) and re.fullmatch(r'0|-?[1-9][0-9]*', n), 'Canonical numerator required')
    need(isinstance(d, str) and re.fullmatch(r'[1-9][0-9]*', d), 'Positive canonical denominator required')
    x = Fraction(int(n), int(d))
    need(packed(x) == v, 'Reduced fraction required')
    return x


def binary64(v):
    need(type(v) in (int, float), 'Saved numerical weight required')
    try:
        x = float(v)
    except OverflowError as e:
        raise ValueError('Saved numerical weight must be finite binary64') from e
    need(math.isfinite(x), 'Saved numerical weight must be finite binary64')
    return Fraction.from_float(x)


def stage_anchors(finite):
    """All pure Nash pairs and exact joint maxima of the full simultaneous grid.

    Imported saved numbers are interpreted as binary64 first. In particular,
    summing A and B happens as fractions, never as a newly rounded float sum.
    These are static stage-game anchors, not learned-policy equilibria.
    """
    need(isinstance(finite, dict), 'Finite table required')
    raw_prices = finite.get('prices')
    need(isinstance(raw_prices, list) and 2 <= len(raw_prices) <= 62, 'Expected 2..62 original price indices')
    n = len(raw_prices)
    prices = [binary64(v) for v in raw_prices]
    need(all(prices[i] < prices[i+1] for i in range(n-1)), 'Prices must strictly increase')
    rewards = finite.get('rewards', {})
    values = {}
    for name in ('profitA', 'profitB', 'consumerSurplus'):
        raw = rewards.get(name)
        need(isinstance(raw, list) and len(raw) == n*n, 'Complete WORLD payoff table required: '+name)
        values[name] = [binary64(x) for x in raw]
    a_pay, b_pay, cs = (values[k] for k in ('profitA', 'profitB', 'consumerSurplus'))
    best_a = []
    for b in range(n):
        maximum = max(a_pay[a*n+b] for a in range(n))
        best_a.append([a for a in range(n) if a_pay[a*n+b] == maximum])
    best_b = []
    for a in range(n):
        maximum = max(b_pay[a*n+b] for b in range(n))
        best_b.append([b for b in range(n) if b_pay[a*n+b] == maximum])
    joint = [a_pay[k]+b_pay[k] for k in range(n*n)]
    maximum_joint = max(joint)

    def pair(a, b):
        k = a*n+b
        return dict(indices=[a,b], prices=[packed(prices[a]),packed(prices[b])],
                    profits=dict(A=packed(a_pay[k]),B=packed(b_pay[k]),joint=packed(joint[k])),
                    consumerSurplus=packed(cs[k]))

    equilibria = [pair(a,b) for a in range(n) for b in range(n) if a in best_a[b] and b in best_b[a]]
    maxima = [pair(a,b) for a in range(n) for b in range(n) if joint[a*n+b] == maximum_joint]
    return dict(n=n, coordinateOrder='WORLD row-major (currentA,currentB)',
                scope='All static pure Nash and exact joint-profit maxima on the unchanged full original price grid; no dynamic-policy equilibrium or collusion index',
                bestResponses=dict(AByRivalB=best_a,BByRivalA=best_b),
                pureNash=dict(count=len(equilibria),pairs=equilibria,
                              reason=None if equilibria else 'No pure Nash pair exists in this saved simultaneous full-grid game'),
                jointProfitMaximum=dict(value=packed(maximum_joint),count=len(maxima),pairs=maxima))


def expected_id(seed, treatment):
    if treatment == 'full-grid-after-cap':
        return f'base-g15-t1--full-grid-after-cap--zero--s{seed}'
    need(treatment == 'startup-guard', 'Unknown comparison treatment')
    return f'base-g15-t1--matched5-startup--zero--s{seed}'


def normalized(entries, treatment):
    need(isinstance(entries, list) and len(entries) == 12, 'All twelve endpoint slots required')
    by_seed = {}
    for e in entries:
        need(isinstance(e, dict) and type(e.get('seed')) is int and e['seed'] in SEEDS, 'Planned seed required')
        seed = e['seed']
        need(seed not in by_seed and e.get('runId') == expected_id(seed,treatment), 'Endpoint identity differs or is duplicated')
        for name in ('available', 'replayMatched', 'executionSucceeded'):
            need(type(e.get(name)) is bool, 'Explicit endpoint status required')
        if e['available']:
            need(e['replayMatched'] and e.get('unavailableReason') is None, 'Available endpoint must be independently accepted')
            need(type(e.get('step')) is int and e['step'] == 2_000_000 and type(e.get('nextPhase')) is int and e['nextPhase'] == 4, 'Actual final endpoint/clock required')
            history = e.get('previousIndices')
            need(isinstance(history,list) and len(history)==2 and all(type(v) is int and 0<=v<62 for v in history), 'Actual final history required')
            length = e.get('cycleLength')
            need(type(length) is int and 1<=length<=4*62*62 and length%4==0, 'Complete recurrent-clock cycle required')
            for key in ('checkpointSha256','graphSha256'):
                need(isinstance(e.get(key),str) and re.fullmatch('[a-f0-9]{64}',e[key]), 'Bound endpoint hashes required')
            ratio(e.get('cycleCustomerBenefit'))
        else:
            need(e.get('cycleCustomerBenefit') is None and isinstance(e.get('unavailableReason'),str) and e['unavailableReason'].strip(), 'Unavailable outcome must be null with reason')
        by_seed[seed] = e
    need(set(by_seed)==set(SEEDS), 'Planned endpoint seeds differ')
    return by_seed


def aggregate(reference_endpoints, startup_guard_endpoints):
    """Pure normalization is not evidence acceptance; authoritative adapters bind it."""
    reference = normalized(reference_endpoints,'full-grid-after-cap')
    guard = normalized(startup_guard_endpoints,'startup-guard')
    rows, differences, seeds = [], [], []
    for seed in SEEDS:
        a,b = guard[seed],reference[seed]
        available = a['available'] and b['available']
        delta = ratio(b['cycleCustomerBenefit'])-ratio(a['cycleCustomerBenefit']) if available else None
        reasons = [f'{label}: {e["unavailableReason"]}' for label,e in [('startup-guard',a),('full-grid-after-cap',b)] if not e['available']]
        rows.append(dict(seed=seed,runIds=[a['runId'],b['runId']],available=available,
                         executionSucceeded=[a['executionSucceeded'],b['executionSucceeded']],
                         replayMatched=[a['replayMatched'],b['replayMatched']],
                         cycleCustomerBenefits=[a['cycleCustomerBenefit'],b['cycleCustomerBenefit']],
                         difference=packed(delta) if available else None,
                         unavailableReason='; '.join(reasons) if reasons else None))
        if available:
            differences.append(delta)
            seeds.append(seed)
    complete = len(differences)==12
    signs = dict(positive=sum(x>0 for x in differences),zero=sum(x==0 for x in differences),negative=sum(x<0 for x in differences))
    return dict(pairedRows=rows,
                primarySummary=dict(plannedDenominator=12,availablePairs=len(differences),available=complete,
                                    meanDifference=packed(sum(differences,Fraction())/12) if complete else None,
                                    unavailableReason=None if complete else 'At least one required final pair lacks two accepted endpoints'),
                completePairDescription=dict(scope='Secondary available-pair description; never substitutes for the planned all-twelve mean',
                                             denominator=len(differences),seedIds=seeds,signCounts=signs,
                                             meanDifference=packed(sum(differences,Fraction())/len(differences)) if differences else None))
