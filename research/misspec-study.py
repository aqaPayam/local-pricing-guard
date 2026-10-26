"""Fixed nominal enforcement, alternative actual logit demand. No default case run.

Only the frozen interval kernel and hash-bound saved nominal price enclosures
are reused. New welfare, tail, radius and period-selection logic lives here.
Synthetic tests may call functions; inherited cases require reviewed freeze/run.
"""
from pathlib import Path
from decimal import Decimal
from fractions import Fraction
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, platform, sys, time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'research'))
from continuous_interval import Interval as I, Unresolved, PRECISION, decimal, fraction_decimal, exact_binary64, midpoint

OUT = ROOT / 'research/misspec-results'
KINDS = ['effective', 'nominal']
LABELS = ['cap-90pct', 'cap-95pct', 'cap-99pct', 'cap-100pct', 'near-Nash-anchor-floor']
LEVELS = [Fraction(0), Fraction(1, 1000), Fraction(1, 100), Fraction(1, 20)]
MAX_PERIOD = 65536
MAX_D = Decimal(8)
RADIUS_WIDTH = Decimal('1e-20')
STATIONARY_PADDING = Decimal('1e-24')
SOURCES = ['research/misspec-study.py', 'tests/test_misspec.py',
           'research/MODEL_MISSPEC_PROTOCOL.md', 'research/MODEL_MISSPEC_THEORY.md',
           'research/continuous_interval.py']


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def box(r): return I(r['lower'], r['upper'])
def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(value, separators=(',', ':'), ensure_ascii=False) + '\n')


def level_record(value):
    value = Fraction(value)
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator),
            'exactDecimal': str(fraction_decimal(value)),
            'units': 'dimensionless downward inside-quality shift divided by unchanged mu'}


def nonnegative_power(value, exponent):
    value = I.cast(value)
    if value.lo < 0 or type(exponent) is not int or exponent < 0:
        raise ValueError('Nonnegative base and integer exponent required')
    result = I(1)
    while exponent:
        if exponent & 1: result = result * value
        value = value * value
        exponent //= 2
    return result


class ActualDemand:
    """Only demand quality changes. k is the certified NOMINAL constant."""
    def __init__(self, nominal_k, mass_scale):
        self.k, self.mass_scale = I.cast(nominal_k), I.cast(mass_scale)
        if self.k.lo <= 0 or self.mass_scale.lo <= 0:
            raise ValueError('Positive nominal k and unchanged B*mu required')

    def signal(self, price):
        price = I.cast(price)
        return 2 * (-price).exp() / self.k

    def from_signal(self, signal, displacement):
        d = decimal(displacement)
        if not Decimal(0) <= d <= MAX_D:
            raise ValueError('Displacement outside declared [0,8] domain')
        factor = I(1) if d == 0 else (-I(d)).exp()
        return self.mass_scale * (1 + factor * signal).ln()

    def surplus(self, price, displacement):
        return self.from_signal(self.signal(price), displacement)

    def stationary_crossing(self, price, target):
        f = decimal(target)
        if f <= 0: raise ValueError('Positive fixed absolute target required')
        return self.signal(price).ln() - ((I(f) / self.mass_scale).exp() - 1).ln()


class ShiftedBounds:
    """Saved fixed prices; recompute actual rewards, retain geometric price tail."""
    def __init__(self, demand, prices, a_j, qstar, rho):
        self.demand = demand
        self.prices = [I.cast(p) for p in prices]
        self.a_j, self.qstar, self.rho = map(I.cast, (a_j, qstar, rho))
        if not self.prices or self.rho.lo < 0 or self.rho.hi >= 1:
            raise ValueError('Certified finite nominal prefix and contraction required')
        if self.prices[0].hi >= self.qstar.lo:
            raise Unresolved('Inherited cap strictly below qstar not certified')
        gap = self.qstar - self.a_j
        if gap.hi < 0: raise Unresolved('Saved nominal prefix exceeds qstar')
        self.gap = I(max(Decimal(0), gap.lo), gap.hi)
        self.signals = [demand.signal(p) for p in self.prices]
        self.qsignal = demand.signal(self.qstar)
        self.cache, self.displacements = {}, {}

    def at_displacement(self, d):
        d = decimal(d)
        if not 0 <= d <= MAX_D: raise ValueError('No evaluation above d=8')
        key = str(d)
        if key not in self.displacements:
            rewards = [self.demand.from_signal(s, d) for s in self.signals]
            prefix = [I(0)]
            for reward in rewards: prefix.append(prefix[-1] + reward)
            self.displacements[key] = {'rewards': rewards, 'prefix': prefix,
                'cstar': self.demand.from_signal(self.qsignal, d)}
        return self.displacements[key]

    def guard(self, d): return self.at_displacement(d)['cstar']

    def get(self, k, d):
        if type(k) is not int or not 1 <= k <= MAX_PERIOD:
            raise ValueError('Period outside declared [1,65536] domain')
        d = decimal(d); key = (k, str(d))
        if key in self.cache: return self.cache[key]
        values = self.at_displacement(d); j = len(self.prices); tail = None
        if k <= j:
            total = values['prefix'][k]
            last = values['rewards'][k-1]
        else:
            length = k-j
            # The uniform price Lipschitz constant remains B*mu, even though
            # actual demand has changed. a_J is the FIRST omitted reward price.
            r = I(self.rho.hi)
            geometric = (1 - nonnegative_power(r, length)) / (1-r)
            excess = self.demand.mass_scale * self.gap * geometric
            total = values['prefix'][j] + length*values['cstar'] + I(0, excess.hi)
            last_excess = self.demand.mass_scale*self.gap*nonnegative_power(r, k-1-j)
            last = values['cstar'] + I(0, last_excess.hi)
            tail = {'firstOmittedIndex': j, 'terms': length,
                    'constantFloor': values['cstar'].json(),
                    'geometricSum': geometric.json(), 'excessSumUpper': str(excess.hi),
                    'lastRoundExcessUpper': str(last_excess.hi),
                    'scope': 'Uniform nominal-price contraction bound; no shrinking-in-d excess asserted'}
        value = {'period': k, 'displacementExact': str(d),
                 'averageConsumerSurplus': (total/k).json(),
                 'cycleSumConsumerSurplus': total.json(), 'lastRoundConsumerSurplus': last.json(),
                 'capRuleActivationFrequency': (I(1)/k).json(), 'startupCapCount': 1,
                 'finiteActivationAverageLowerBound': str((total/k).lo), 'tail': tail}
        self.cache[key] = value
        return value


def status_at(value, target):
    value, target = I.cast(value), decimal(target)
    if value.hi < target: return 'already failing'
    if value.lo == value.hi == target: return 'exact zero reserve'
    if value.lo >= target: return 'certified safe'
    return 'unresolved overlap'


def signed_evaluation(evaluate, d, f):
    value = evaluate(decimal(d))
    return {'displacementExact': str(d), 'surplus': value.json(),
            'reserve': (value-f).json(), 'status': status_at(value, f)}


def radius(evaluate, target, mass_scale, stationary=None):
    """Every returned safe/failing endpoint has its own welfare/reserve evidence."""
    f = decimal(target)
    if f <= 0: raise ValueError('Positive fixed target required')
    zero = signed_evaluation(evaluate, Decimal(0), f)
    z = box(zero['surplus']); reserve = z-f
    out = {'zero': zero, 'searchCeilingExact': str(MAX_D),
           'requiredBracketWidth': str(RADIUS_WIDTH), 'safeNonnegativeSet': None,
           'simpleNominalReserveRatio': (reserve/I.cast(mass_scale)).json(),
           'certifiedSimpleSufficientRadiusLower': None}
    if stationary is not None:
        out['stationaryClosedForm'] = stationary.json()
        out['stationarySignPaddingExact'] = str(STATIONARY_PADDING)
    if zero['status'] == 'already failing':
        return {**out, 'status': 'already failing at zero; empty safe nonnegative set',
                'safeNonnegativeSet': 'empty', 'radiusEnclosure': None}
    if zero['status'] == 'unresolved overlap':
        return {**out, 'status': 'unresolved zero-displacement overlap', 'radiusEnclosure': None}
    if zero['status'] == 'exact zero reserve':
        return {**out, 'status': 'certified exact zero radius', 'safeNonnegativeSet': '[0,0]',
                'radiusEnclosure': I(0).json(),
                'reason': 'Exact equality plus strict decrease for positive displacement'}
    if reserve.lo > 0:
        out['certifiedSimpleSufficientRadiusLower'] = str((reserve/I.cast(mass_scale)).lo)
    ceiling = signed_evaluation(evaluate, MAX_D, f)
    out['ceiling'] = ceiling
    if box(ceiling['surplus']).lo >= f:
        return {**out, 'status': 'censored safe lower bound',
                'certifiedRadiusLowerBound': str(MAX_D), 'radiusEnclosure': None,
                'safeNonnegativeSet': 'contains [0,8]; crossing not identified within declared domain'}
    if box(ceiling['surplus']).hi >= f:
        return {**out, 'status': 'unresolved at displacement ceiling', 'radiusEnclosure': None}
    low, high = Decimal(0), MAX_D
    left, right = zero, ceiling
    # Separate closed-form expression and direct welfare signs. The fixed pad
    # prevents treating an uncertain analytic boundary as an exact signed point.
    if stationary is not None:
        a = max(Decimal(0), (I(stationary.lo)-STATIONARY_PADDING).lo)
        b = min(MAX_D, (I(stationary.hi)+STATIONARY_PADDING).hi)
        if a < b:
            ea, eb = signed_evaluation(evaluate, a, f), signed_evaluation(evaluate, b, f)
            out['stationarySignedCrossCheck'] = {'lower': ea, 'upper': eb}
            if box(ea['surplus']).lo >= f and box(eb['surplus']).hi < f:
                low, high, left, right = a, b, ea, eb
    iterations = 0
    while I(low, high).width > RADIUS_WIDTH:
        if iterations >= 600:
            return {**out, 'status': 'unresolved crossing budget', 'signedBracket': I(low, high).json(),
                    'safeLower': left, 'failingUpper': right, 'radiusEnclosure': None}
        middle = midpoint(low, high)
        if not low < middle < high:
            break
        value = signed_evaluation(evaluate, middle, f)
        v = box(value['surplus'])
        if v.lo >= f: low, left = middle, value
        elif v.hi < f: high, right = middle, value
        else:
            progress = False
            for point in [midpoint(low, middle), midpoint(middle, high)]:
                e = signed_evaluation(evaluate, point, f); v = box(e['surplus'])
                if v.lo >= f and point > low: low, left, progress = point, e, True
                elif v.hi < f and point < high: high, right, progress = point, e, True
            if not progress: break
        iterations += 1
    bracket = I(low, high)
    if bracket.width > RADIUS_WIDTH:
        return {**out, 'status': 'unresolved crossing width', 'signedBracket': bracket.json(),
                'safeLower': left, 'failingUpper': right, 'iterations': iterations, 'radiusEnclosure': None}
    return {**out, 'status': 'certified crossing enclosure', 'radiusEnclosure': bracket.json(),
            'safeNonnegativeSet': 'true break-even crossing enclosed; endpoints independently signed',
            'positiveReserveCertified': reserve.lo > 0, 'safeLower': left,
            'failingUpper': right, 'iterations': iterations}


def period_selection(bounds, f, d):
    """New fixed-target comparison, never evaluates MAX_PERIOD+1."""
    f, d = decimal(f), decimal(d)
    guard = bounds.guard(d); first = bounds.get(1, d)
    result = {'displacementExact': str(d), 'thresholdExact': str(f),
              'searchCeiling': MAX_PERIOD, 'guardFloor': guard.json()}
    if guard.lo >= f:
        return {**result, 'status': 'no recurring cap needed for the long-run target',
                'withoutIntervention': {'startupCaps': 0, 'recurringFrequency': 0,
                    'finiteActivationAverageGuaranteedFromArbitraryOldPrices': False},
                'oneImmediateCapThenOriginalGuard': {'startupCaps': 1, 'recurringFrequency': 0,
                    'finiteActivationAverageLowerBound': str(guard.lo)}}
    one = box(first['averageConsumerSurplus'])
    if one.hi < f:
        return {**result, 'status': 'infeasible for this fixed-cap family', 'strongestPeriod': first,
                'scope': 'Does not rule out a stricter physical cap or another controller'}
    if one.lo < f:
        return {**result, 'status': 'unresolved period-one boundary', 'strongestPeriod': first}
    safe, failed, probes = 1, None, []
    k = 2
    while k <= MAX_PERIOD:
        v = box(bounds.get(k, d)['averageConsumerSurplus']); probes.append(k)
        if v.hi < f: failed = k; break
        if v.lo >= f: safe = k
        if k == MAX_PERIOD: break
        k = min(MAX_PERIOD, 2*k)
    if failed is None:
        return {**result, 'status': 'censored safe lower bound' if safe == MAX_PERIOD else 'unresolved censored bracket',
                'certifiedSafePeriodLowerBound': safe, 'certifiedFailingPeriodUpperBound': None,
                'safePeriod': bounds.get(safe, d), 'ceilingPeriod': bounds.get(MAX_PERIOD, d),
                'doublingPeriods': probes, 'largestPeriod': None}
    # Two conservative searches: an overlap cannot be called either a safe
    # or failing value. Returned endpoints are independently checked below.
    left, right = safe, failed
    while right-left > 1:
        middle = (left+right)//2
        if box(bounds.get(middle, d)['averageConsumerSurplus']).lo >= f: left = middle
        else: right = middle
    safe = left
    left, right = safe, failed
    while right-left > 1:
        middle = (left+right)//2
        if box(bounds.get(middle, d)['averageConsumerSurplus']).hi < f: right = middle
        else: left = middle
    failed = right
    exact = failed == safe+1
    return {**result, 'status': 'largest certified fixed period' if exact else 'certified integer bracket',
            'largestPeriod': safe if exact else None, 'certifiedSafePeriodLowerBound': safe,
            'certifiedFailingPeriodUpperBound': failed, 'possibleLargestPeriodBracket': [safe, failed-1],
            'safePeriod': bounds.get(safe, d), 'nextFailingPeriod': bounds.get(failed, d),
            'doublingPeriods': probes, 'scope': 'Only the same inherited physical cap at fixed integer periods'}


def selected_policy(closed):
    status = closed['status']
    if status == 'no recurring cap needed for the long-run target':
        return {'kind': 'guard', 'period': None, 'originatingStatus': status}
    if status == 'largest certified fixed period':
        k = closed.get('largestPeriod')
        if type(k) is not int or not 1 <= k <= MAX_PERIOD: raise ValueError('Invalid closed selected period')
        return {'kind': 'periodic', 'period': k, 'originatingStatus': status}
    return {'kind': 'unavailable', 'period': None, 'originatingStatus': status,
            'reason': 'No certified closed largest integer policy is invented from a censored, unresolved or infeasible choice'}


def policy_rows(bounds, target, closed):
    f = decimal(float(target['actualGuaranteedThreshold']))
    descriptions = [('guard-only', {'kind': 'guard', 'period': None}),
                    ('closed-selected', selected_policy(closed)),
                    ('permanent-cap', {'kind': 'periodic', 'period': 1})]
    rows, first_slot = [], {}
    for slot, policy in descriptions:
        available = policy['kind'] != 'unavailable'
        key = (policy['kind'], policy['period'])
        duplicate = first_slot.get(key) if available else None
        if available: first_slot.setdefault(key, slot)
        base = {'slot': slot, 'available': available, 'policy': policy, 'duplicateOf': duplicate}
        if not available:
            rows.append({**base, 'radius': {'status': 'unavailable inherited policy', 'reason': policy['reason']},
                         'sensitivity': [{'dbar': level_record(v), 'status': 'unavailable inherited policy'} for v in LEVELS]})
            continue
        guard = policy['kind'] == 'guard'; k = policy['period']
        evaluate = bounds.guard if guard else lambda d, k=k: box(bounds.get(k, d)['averageConsumerSurplus'])
        stationary = bounds.qstar if guard else bounds.prices[0] if k == 1 else None
        analytic = bounds.demand.stationary_crossing(stationary, f) if stationary is not None else None
        radius_row = radius(evaluate, f, bounds.demand.mass_scale, analytic)
        sensitivity = []
        for level in LEVELS:
            d = fraction_decimal(level); value = evaluate(d)
            sensitivity.append({'dbar': level_record(level), 'surplus': value.json(), 'reserve': (value-f).json(),
                'status': status_at(value, f), 'uniformForFixedUnknownDIn': ['0', str(d)],
                'startupCapCount': 0 if guard else 1,
                'capRuleActivationFrequency': I(0).json() if guard else (I(1)/k).json(),
                'finiteActivationAverageGuaranteedFromArbitraryOldPrices': not guard})
        rows.append({**base, 'radius': radius_row, 'sensitivity': sensitivity,
            'startupCapCount': 0 if guard else 1,
            'capRuleActivationFrequency': I(0).json() if guard else (I(1)/k).json(),
            'singleStartupCapVariant': {'startupCapCount': 1, 'recurringFrequency': 0,
                'finiteActivationAverageFloor': 'same guard-floor value; starts with one actual cap'} if guard else None})
    robust = []
    for level in LEVELS:
        robust.append({'dbar': level_record(level), **period_selection(bounds, f, fraction_decimal(level))})
    zero = robust[0]
    keys = ['status', 'largestPeriod', 'certifiedSafePeriodLowerBound', 'certifiedFailingPeriodUpperBound', 'possibleLargestPeriodBracket']
    reproduces = all(zero.get(k) == closed.get(k) for k in keys)
    return {'label': target['label'], 'requestedImported': exact_binary64(target['requestedTarget']),
            'actualThresholdImported': exact_binary64(target['actualGuaranteedThreshold']),
            'actualThresholdExact': str(f), 'policies': rows, 'robustPeriods': robust,
            'd0ReproducesClosedSelection': reproduces,
            'closedSelectionStatus': closed['status']}


def inherited_inventory():
    """Transitive immutable source/input inventory, including independent code."""
    files = {}
    manifests = {}
    for folder, auditor in [('recurring-results', 'audit-sparse-reset.py'),
                            ('continuous-results', 'audit-continuous-study.py'),
                            ('handover-init-results', 'audit-handover-init.js')]:
        prefix = 'research/'+folder+'/'
        manifest = read(ROOT/(prefix+'manifest.json')); audit = read(ROOT/(prefix+'independent-audit.json'))
        if not audit.get('passed') or audit['studyManifestHash'] != digest(ROOT/(prefix+'manifest.json')):
            raise ValueError('Inherited independent audit/manifest mismatch '+folder)
        if audit['auditorSourceHash'] != digest(ROOT/'research'/auditor):
            raise ValueError('Inherited independent auditor changed '+folder)
        if audit.get('resultsSha256') and audit['resultsSha256'] != digest(ROOT/(prefix+'results.json')):
            raise ValueError('Inherited independently audited results changed '+folder)
        for name in ['manifest.json', 'results.json', 'independent-audit.json']:
            files[prefix+name] = digest(ROOT/(prefix+name))
        files['research/'+auditor] = digest(ROOT/'research'/auditor)
        for field in ['sourceHashes', 'inputHashes']:
            for name, value in manifest.get(field, {}).items():
                if digest(ROOT/name) != value: raise ValueError('Frozen inherited dependency changed '+name)
                if name in files and files[name] != value: raise ValueError('Conflicting inherited hash '+name)
                files[name] = value
        manifests[folder] = manifest
    recurring = read(ROOT/'research/recurring-results/results.json')
    if recurring['manifestSha256'] != digest(ROOT/'research/recurring-results/manifest.json'):
        raise ValueError('Closed recurring result manifest mismatch')
    completion = read(ROOT/'research/recurring-results/completion.json')
    if not completion['finalFrozenDependencyCheck']['passed'] or completion['resultsSha256'] != digest(ROOT/'research/recurring-results/results.json'):
        raise ValueError('Closed recurring completion failed')
    files['research/recurring-results/completion.json'] = digest(ROOT/'research/recurring-results/completion.json')
    return manifests['recurring-results']['plan']['scenarios'], files


def freeze(directory=OUT):
    directory = Path(directory)
    if directory.exists() and any(directory.iterdir()): raise ValueError('Misspecification evidence directory nonempty; no overwrite')
    scenarios, inputs = inherited_inventory()
    plan = {'scenarios': scenarios, 'continuums': KINDS, 'records': 16, 'targetLabels': LABELS,
        'policySlots': ['guard-only', 'closed-selected', 'permanent-cap'], 'radiusPolicySlots': 240,
        'uncertaintyBounds': [level_record(v) for v in LEVELS], 'robustPeriodRows': 320,
        'maximumDisplacementExact': str(MAX_D), 'maximumPeriod': MAX_PERIOD,
        'requiredRadiusWidth': str(RADIUS_WIDTH), 'stationarySignPaddingExact': str(STATIONARY_PADDING),
        'arithmeticPrecision': PRECISION, 'runtimeTargetSeconds': 1800, 'sampledRSSTargetBytes': 250_000_000,
        'apiCalls': 0, 'trainingRounds': 0,
        'actualDemandShift': 'Inside quality = inherited quality - d*unchanged mu; outside quality/enforcement unchanged'}
    manifest = {'frozenAt': datetime.now(timezone.utc).isoformat(), 'plan': plan,
                'sourceHashes': {name: digest(ROOT/name) for name in SOURCES}, 'inputHashes': inputs}
    for name in SOURCES:
        target = directory/'sources'/name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())
    save(directory/'manifest.json', manifest)
    return {'manifestSha256': digest(directory/'manifest.json'), 'frozenAt': manifest['frozenAt']}


def verify(directory=OUT):
    directory = Path(directory); manifest = read(directory/'manifest.json')
    for field in ['sourceHashes', 'inputHashes']:
        for name, value in manifest[field].items():
            if digest(ROOT/name) != value: raise ValueError('Misspecification frozen dependency changed '+name)
            if field == 'sourceHashes' and digest(directory/'sources'/name) != value:
                raise ValueError('Frozen source snapshot changed '+name)
    inherited_inventory()
    return manifest


def model_from_saved(scenario, recurring, continuous):
    if recurring['status'] != 'certified recurring-cap enclosures' or continuous['status'] != 'certified theorem and enclosures':
        raise Unresolved('Inherited condition/calculation is unresolved')
    if recurring['importedBinary64'] != continuous['importedBinary64'] or recurring['inheritedContinuum']['rounding'] != continuous['rounding']:
        raise ValueError('Enforcement semantics/constants changed')
    if not all(recurring['conditions'].values()): raise Unresolved('Inherited cap premise failed')
    economy = scenario['economy']
    scale = fraction_decimal(Fraction(float(economy['buyers'])) * Fraction(float(economy['mu'])))
    demand = ActualDemand(box(continuous['k']), I(scale))
    steps = recurring['orbit']
    if len(steps) != 64 or any(step['j'] != j for j, step in enumerate(steps)):
        raise ValueError('Expected all 64 saved nominal orbit terms')
    qstar, rho = box(recurring['inheritedContinuum']['qstar']), box(recurring['inheritedContinuum']['rho'])
    if qstar.json() != continuous['worst']['normalizedPrice'] or rho.json() != continuous['assumptions']['rho']:
        raise ValueError('Certified nominal envelope identity differs')
    prices = [box(step['executedNormalizedPrice']) for step in steps]
    if prices[0].lo != prices[0].hi or str(prices[0].lo) != recurring['normalizedCapExact']:
        raise ValueError('Physical cap normalized-price identity differs')
    return ShiftedBounds(demand, prices, box(recurring['aJ']), qstar, rho)


def rss_bytes():
    if os.name == 'nt':
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [(name, ctypes.c_size_t) for name in
                ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
                 'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
        c = Counters(); c.cb = ctypes.sizeof(c)
        kernel = ctypes.WinDLL('kernel32', use_last_error=True); kernel.GetCurrentProcess.restype = wintypes.HANDLE
        fn = ctypes.WinDLL('psapi', use_last_error=True).GetProcessMemoryInfo
        fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        if not fn(kernel.GetCurrentProcess(), ctypes.byref(c), c.cb): raise OSError(ctypes.get_last_error())
        return c.WorkingSetSize
    path = Path('/proc/self/statm')
    return int(path.read_text().split()[1])*os.sysconf('SC_PAGE_SIZE') if path.exists() else None


def run(directory=OUT):
    directory = Path(directory); manifest = verify(directory)
    if any((directory/name).exists() for name in
           ['execution-start.json', 'results.json', 'journal.jsonl', 'records', 'completion.json']):
        raise ValueError('Partial or closed misspecification outputs preserved')
    started = time.perf_counter()
    save(directory/'execution-start.json', {'startedAt': datetime.now(timezone.utc).isoformat(),
                                         'manifestSha256': digest(directory/'manifest.json')})
    def journal(value):
        with (directory/'journal.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps({'at': datetime.now(timezone.utc).isoformat(), **value})+'\n')
    input_failure = None
    try:
        old = read(ROOT/'research/handover-init-results/results.json')['records']
        recurrent = read(ROOT/'research/recurring-results/results.json')['records']
        continuums = read(ROOT/'research/continuous-results/results.json')['records']
    except Exception as error:
        input_failure = error
    records, samples = [], []
    for scenario in manifest['plan']['scenarios']:
        sid = scenario['id']
        for kind in KINDS:
            began = time.perf_counter(); journal({'scenario': sid, 'continuum': kind, 'status': 'started'})
            result = {'scenario': sid, 'continuum': kind,
                'actualDemand': manifest['plan']['actualDemandShift'], 'targets': []}
            targets = []
            try:
                if input_failure is not None: raise input_failure
                matches = [r for r in old if r['scenario'] == scenario]
                if len(matches) != 1: raise ValueError('Missing/duplicate inherited target scenario')
                targets = matches[0]['results']
                if sorted(t['label'] for t in targets) != sorted(manifest['plan']['targetLabels']):
                    raise ValueError('Missing/duplicate inherited target label')
                targets = [next(t for t in targets if t['label'] == label)
                           for label in manifest['plan']['targetLabels']]
                closed = [r for r in recurrent if r['scenario'] == sid and r['continuum'] == kind]
                certified = [r for r in continuums if r['scenario'] == sid and r['continuum'] == kind]
                if len(closed) != 1 or len(certified) != 1: raise ValueError('Missing inherited model semantic record')
                closed, certified = closed[0], certified[0]
                bounds = model_from_saved(scenario, closed, certified)
                result['nominalEnforcement'] = {'scenario': scenario, 'physicalCap': closed['physicalCap'],
                    'normalizedCapExact': closed['normalizedCapExact'], 'conditions': closed['conditions'],
                    'rounding': closed['inheritedContinuum']['rounding'],
                    'qstar': bounds.qstar.json(), 'rho': bounds.rho.json(), 'aJ': bounds.a_j.json(),
                    'nominalK': bounds.demand.k.json(), 'unchangedMassScale': bounds.demand.mass_scale.json(),
                    'orbitSource': 'Closed recurring-results/results.json, same scenario/continuum; no price recomputation'}
                for target in targets:
                    prior = [r for r in closed['comparisons'] if r['label'] == target['label']]
                    if len(prior) != 1: raise ValueError('Missing closed target label')
                    threshold = prior[0].get('actualThresholdImported', prior[0].get('thresholdImported'))
                    if threshold is None or threshold['exactDecimal'] != str(decimal(float(target['actualGuaranteedThreshold']))):
                        raise ValueError('Fixed absolute target identity differs')
                    result['targets'].append(policy_rows(bounds, target, prior[0]))
                result['d0AllClosedSelectionsReproduced'] = all(t['d0ReproducesClosedSelection'] for t in result['targets'])
                if not result['d0AllClosedSelectionsReproduced']:
                    raise ValueError('Zero-displacement selection failed closed-study reproduction')
                result['status'] = 'completed alternative-demand comparisons'
            except Exception as error:
                result.update({'status': 'unresolved calculation or inherited condition', 'failure': str(error),
                               'failureType': type(error).__name__})
                # Retain all slots even when the whole inherited model fails.
                present = {r['label'] for r in result['targets']}
                for label in manifest['plan']['targetLabels']:
                    if label not in present:
                        matches = [t for t in targets if t.get('label') == label]
                        target = matches[0] if len(matches) == 1 else None
                        result['targets'].append({'label': label,
                            'requestedImported': exact_binary64(target['requestedTarget']) if target is not None else None,
                            'actualThresholdImported': exact_binary64(target['actualGuaranteedThreshold']) if target is not None else None,
                            'targetIdentityAvailable': target is not None,
                            'policies': [{'slot': slot, 'available': False, 'radius': {'status': 'unresolved inherited/model failure'},
                                'sensitivity': [{'dbar': level_record(d), 'status': 'unresolved'} for d in LEVELS]}
                                for slot in manifest['plan']['policySlots']],
                            'robustPeriods': [{'dbar': level_record(d), 'status': 'unresolved'} for d in LEVELS]})
            result['seconds'] = time.perf_counter()-began
            save(directory/'records'/f'{sid}-{kind}.json', result); records.append(result)
            samples.append({'scenario': sid, 'continuum': kind, 'rssBytes': rss_bytes()})
            journal({'scenario': sid, 'continuum': kind, 'status': result['status'], 'seconds': result['seconds']})
            print(json.dumps({'scenario': sid, 'continuum': kind, 'status': result['status'], 'seconds': result['seconds']}), flush=True)
    save(directory/'results.json', {'manifestSha256': digest(directory/'manifest.json'), 'records': records})
    try: verify(directory); final = {'passed': True}
    except Exception as error: final = {'passed': False, 'failure': str(error)}
    completion = {'records': len(records), 'policySlots': sum(len(t['policies']) for r in records for t in r['targets']),
        'robustPeriodRows': sum(len(t['robustPeriods']) for r in records for t in r['targets']),
        'unresolvedModels': sum(r['status'] != 'completed alternative-demand comparisons' for r in records),
        'resultsSha256': digest(directory/'results.json'), 'finalFrozenDependencyCheck': final,
        'resources': {'seconds': time.perf_counter()-started, 'rssSamples': samples,
            'largestObservedRSSBytes': max((s['rssBytes'] for s in samples if s['rssBytes'] is not None), default=None),
            'sampling': 'After each model; not a continuously measured peak', 'python': platform.python_version(),
            'apiCalls': 0, 'newTrainingRounds': 0}}
    save(directory/'completion.json', completion)
    if not final['passed']: raise ValueError('Final frozen dependency check failed')
    return completion


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['freeze', 'verify', 'run'])
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    output = freeze(args.output) if args.mode == 'freeze' else run(args.output) if args.mode == 'run' else verify(args.output)
    print(json.dumps(output))
