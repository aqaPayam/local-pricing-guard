"""Independent 130-digit enclosure audit; imports no primary calculation code.

Uses a separate interval implementation and log-residual W brackets. Decimal's
correctly rounded transcendental backend is shared and explicitly disclosed.
"""
from decimal import Decimal, Context, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path
import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
P = 130
LOW = Context(prec=P, rounding=ROUND_FLOOR, Emin=-999999, Emax=999999)
HIGH = Context(prec=P, rounding=ROUND_CEILING, Emin=-999999, Emax=999999)
MID = Context(prec=P, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999)
CHECKS = 0
LABELS = ['cap-90pct', 'cap-95pct', 'cap-99pct', 'cap-100pct', 'near-Nash-anchor-floor']


def require(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise ValueError(message)


class Box:
    def __init__(self, low, high=None):
        self.low, self.high = Decimal(low), Decimal(low if high is None else high)
        if not self.low.is_finite() or not self.high.is_finite() or self.low > self.high:
            raise ValueError('Invalid audit interval')

    @staticmethod
    def cast(x):
        return x if isinstance(x, Box) else Box(x)

    @staticmethod
    def rational(x):
        x = Fraction(x)
        return Box(LOW.divide(Decimal(x.numerator), Decimal(x.denominator)),
                   HIGH.divide(Decimal(x.numerator), Decimal(x.denominator)))

    def __add__(self, other):
        b = Box.cast(other)
        return Box(LOW.add(self.low, b.low), HIGH.add(self.high, b.high))

    __radd__ = __add__

    def __neg__(self):
        return Box(self.high.copy_negate(), self.low.copy_negate())

    def __sub__(self, other):
        return self + (-Box.cast(other))

    def __rsub__(self, other):
        return Box.cast(other) - self

    def __mul__(self, other):
        b = Box.cast(other)
        return Box(min(LOW.multiply(a, c) for a in (self.low, self.high) for c in (b.low, b.high)),
                   max(HIGH.multiply(a, c) for a in (self.low, self.high) for c in (b.low, b.high)))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = Box.cast(other)
        if b.low <= 0 <= b.high:
            raise ValueError('Audit division across zero')
        return self * Box(LOW.divide(Decimal(1), b.high), HIGH.divide(Decimal(1), b.low))

    def __rtruediv__(self, other):
        return Box.cast(other) / self

    def exp(self):
        return Box(MID.next_minus(MID.exp(self.low)), MID.next_plus(MID.exp(self.high)))

    def log(self):
        if self.low <= 0:
            raise ValueError('Audit logarithm outside positive domain')
        return Box(MID.next_minus(MID.ln(self.low)), MID.next_plus(MID.ln(self.high)))

    @property
    def sign(self):
        return -1 if self.high < 0 else 1 if self.low > 0 else 0

    def strings(self):
        return {'lower': str(self.low), 'upper': str(self.high)}


def positive_w(z):
    """Independently bracket W using w+log(w)=log(z), not primary w exp(w)-z."""
    z = Box.cast(z)
    require(z.low > 0, 'Positive independent Lambert input')
    answers = []
    for endpoint in (z.low, z.high):
        log_z = Box(endpoint).log()
        residual = lambda x: Box(x) + Box(x).log() - log_z
        a = b = Decimal(1)
        for _ in range(1000):
            if residual(a).sign == -1:
                break
            a = MID.divide(a, Decimal(2))
        else:
            raise ValueError('Independent W lower expansion failed')
        for _ in range(1000):
            if residual(b).sign == 1:
                break
            b = MID.multiply(b, Decimal(2))
        else:
            raise ValueError('Independent W upper expansion failed')
        for _ in range(1000):
            if HIGH.subtract(b, a) <= Decimal('1e-55'):
                break
            m = MID.divide(MID.add(a, b), Decimal(2))
            sign = residual(m).sign
            if sign == -1:
                a = m
            elif sign == 1:
                b = m
            else:
                left = MID.divide(MID.add(a, m), Decimal(2))
                right = MID.divide(MID.add(m, b), Decimal(2))
                changed = False
                if residual(left).sign == -1:
                    a, changed = left, True
                if residual(right).sign == 1:
                    b, changed = right, True
                if not changed:
                    raise ValueError('Independent W sign unresolved')
        else:
            raise ValueError('Independent W bisection budget exhausted')
        require(residual(a).sign == -1 and residual(b).sign == 1, 'Independent log-W signed endpoints')
        answers.append((a, b))
    return Box(answers[0][0], answers[1][1])


def imported_fraction(value):
    return Fraction(float(value))


def validate_import(record, value, label):
    f = imported_fraction(value)
    require(Fraction(Decimal(record['exactDecimal'])) == f, label + ' exact decimal')
    require((int(record['numerator']), int(record['denominator'])) == (f.numerator, f.denominator), label + ' exact ratio')
    require(record['serialized'] == json.dumps(value, separators=(',', ':'), allow_nan=False), label + ' JSON-value serialization')
    require(record['binary64Serialization'] == repr(float(value)), label + ' binary64 serialization')


def enclosure(record):
    return Box(record['lower'], record['upper'])


def contains(record, independent, label):
    original = enclosure(record)
    require(original.low <= independent.low and original.high >= independent.high, label + ' contains independently certified interval')
    if 'width' in record:
        require(Fraction(Decimal(record['width'])) >= Fraction(original.high)-Fraction(original.low), label + ' honest width')
    return original


class AuditEconomy:
    def __init__(self, case, kind):
        e = case['scenario']['economy']
        self.values = {key: imported_fraction(value) for key, value in e.items() if key != 'id'}
        v = self.values
        self.cost, self.mu = Box.rational(v['cost']), Box.rational(v['mu'])
        self.scale = Box.rational(v['buyers']*v['mu'])
        self.ell = (imported_fraction(case['game']['prices'][0])-v['cost'])/v['mu']
        self.high = (imported_fraction(case['game']['prices'][-1])-v['cost'])/v['mu']
        self.epsilon = imported_fraction(case['scenario']['epsilon'])
        self.allowance = imported_fraction(1e-12)
        self.tolerance = self.epsilon + (self.allowance if kind == 'effective' else 0)
        self.t = Box.rational(self.tolerance/(v['buyers']*v['mu']))
        self.k = Box.rational((v['cost']-v['quality']+v['outsideQuality'])/v['mu']).exp()
        self.cache = {}

    def w(self, y):
        y = Box.cast(y)
        key = (y.low, y.high)
        if key not in self.cache:
            self.cache[key] = positive_w(1/(Box(1).exp()*(self.k+(-y).exp())))
        return self.cache[key]

    def diagonal_profit(self, x):
        x = Box.cast(x)
        # Algebraically separate from primary two-price x/(1+lambda exp(x)).
        return x/(2+self.k*x.exp())

    def diagonal_cs(self, x):
        x = Box.cast(x)
        return self.scale*(1+2/(self.k*x.exp())).log()


def check_record(record, case, targets):
    kind = record['continuum']
    require(kind in ['effective', 'nominal'] and record['scenario'] == case['scenario']['id'], 'Scenario and continuum identity')
    require([r['label'] for r in record['comparisons']] == LABELS, 'Five comparison labels retained in order')
    targets = {r['label']: r for r in targets}
    for row in record['comparisons']:
        old = targets[row['label']]
        validate_import(row['requestedImported'], old['requestedTarget'], 'Original requested target')
        validate_import(row['thresholdImported'], old['actualGuaranteedThreshold'], 'Original actual threshold')
        require(Fraction(Decimal(row['thresholdExact'])) == imported_fraction(old['actualGuaranteedThreshold']), 'Fixed threshold exact value')
    if record['status'] == 'unresolved calculation':
        require(bool(record.get('failure')), 'Retained calculation failure reason')
        require(all(r['classification'] == 'unresolved' for r in record['comparisons']), 'No classification after calculation failure')
        return {'scenario': record['scenario'], 'continuum': kind, 'status': record['status']}
    model = AuditEconomy(case, kind)
    for key, value in case['scenario']['economy'].items():
        if key != 'id':
            validate_import(record['importedBinary64'][key], value, 'Economic input '+key)
    for key, value in [('lowerPrice', case['game']['prices'][0]), ('upperPrice', case['game']['prices'][-1]), ('epsilon', case['scenario']['epsilon']), ('comparisonAllowance', 1e-12)]:
        validate_import(record['importedBinary64'][key], value, key)
    rounding = record['rounding']
    require(rounding['kind'] == kind, 'Tolerance model kind')
    for key, value in [('epsilonExact', model.epsilon), ('allowanceExact', model.allowance), ('effectiveToleranceExactRealSum', model.epsilon+model.allowance), ('appliedPayoffToleranceExact', model.tolerance), ('normalizedToleranceExact', model.tolerance/(model.values['buyers']*model.values['mu']))]:
        require(Fraction(Decimal(rounding[key])) == value, 'Exact tolerance '+key)
    validate_import(rounding['effectiveToleranceJavaScriptRoundedBinary64'], float(case['scenario']['epsilon'])+1e-12, 'Separately rounded sum')
    require(Fraction(Decimal(record['domainNormalized']['lowerExact'])) == model.ell and Fraction(Decimal(record['domainNormalized']['upperExact'])) == model.high, 'Exact normalized domain')
    contains(record['k'], model.k, 'Normalized economy constant')
    ell, high = Box.rational(model.ell), Box.rational(model.high)
    m, wh = model.w(ell), model.w(high)
    wb = positive_w(1/(Box(1).exp()*model.k))
    rho, first, second = wb/(1+wb), m*m/(2*(1+m)), m*m*m*(1+m)/2
    a = record['assumptions']
    for key, value in [('minimumW', m), ('lowerEndpointBestResponse', 1+m), ('upperEndpointBestResponse', 1+wh), ('wBar', wb), ('rho', rho)]:
        contains(a[key], value, 'Global theorem enclosure '+key)
    contains(a['smallToleranceBounds'][0], first, 'First sufficient bound')
    contains(a['smallToleranceBounds'][1], second, 'Second sufficient bound')
    independent_flags = {'lowerBestResponseStrictlyInterior': (1+m).low > ell.high,
                         'upperBestResponseStrictlyInterior': (1+wh).high < high.low,
                         'positiveTolerance': model.t.low > 0,
                         'positiveProfitThreshold': model.t.high < m.low,
                         'smallToleranceFirstBound': model.t.high < first.low,
                         'smallToleranceSecondBound': model.t.high < second.low,
                         'contractionUpperBelowOne': rho.high < 1}
    require(set(a['certifiedChecks']) == set(independent_flags), 'Complete sufficient-condition inventory')
    for key, certified in a['certifiedChecks'].items():
        require(isinstance(certified, bool) and (not certified or independent_flags[key]), 'Independently valid theorem condition '+key)
    require(a['eligible'] == all(a['certifiedChecks'].values()), 'Eligibility agrees with all conditions')
    if not a['eligible']:
        require(record['status'] == 'unresolved assumptions' and all(r['classification'] == 'unresolved' for r in record['comparisons']), 'No substituted result after insufficient assumptions')
        return {'scenario': record['scenario'], 'continuum': kind, 'status': record['status']}
    require(record['status'] == 'certified theorem and enclosures' and all(independent_flags.values()), 'Certified result supported globally')
    nash, worst = record['nash'], record['worst']
    nx, qx = enclosure(nash['normalizedPrice']), enclosure(worst['normalizedPrice'])
    for x in (nx, qx):
        require(Fraction(x.high)-Fraction(x.low) <= Fraction(Decimal('1e-25')), 'Required root enclosure width')
    require(nx.low >= ell.low and nx.high <= high.high and qx.low > nx.high and qx.high <= high.high, 'Ordered interior Nash and above-Nash upper tail')
    for endpoint, key, sign in [(nx.low, 'lowerEvaluation', -1), (nx.high, 'upperEvaluation', 1)]:
        value = Box(endpoint)-1-model.w(Box(endpoint))
        require(value.sign == sign, 'Independent signed Nash endpoint')
        saved = contains(nash['rootProof'][key], value, 'Saved Nash sign evaluation')
        require(saved.sign == sign, 'Claimed Nash proof sign')
    residual = lambda x: model.w(x)-model.t-model.diagonal_profit(x)
    if worst['rootProof']['kind'] == 'ceiling-clipped':
        require(qx.low == qx.high and Fraction(qx.low) == model.high, 'Actual clipped ceiling')
        value = residual(high)
        require(value.sign == -1 and worst['rootProof']['ceilingAllowedStrictly'] is True, 'Ceiling strictly guard-allowed')
        contains(worst['rootProof']['ceilingResidual'], value, 'Clipped ceiling residual')
    else:
        require(worst['rootProof']['kind'] == 'interior upper-root fixed point', 'Known fixed-point certificate type')
        require(Decimal(worst['rootProof']['lowerEndpoint']) == qx.low and Decimal(worst['rootProof']['upperEndpoint']) == qx.high, 'Root evidence uses returned endpoints')
        for endpoint, key, sign in [(qx.low, 'lowerEvaluation', -1), (qx.high, 'upperEvaluation', 1)]:
            value = residual(Box(endpoint))
            require(value.sign == sign, 'Independent signed upper-root endpoint')
            saved = contains(worst['rootProof'][key], value, 'Saved upper-root sign evaluation')
            require(saved.sign == sign, 'Claimed upper-root proof sign')
    branch = qx-1-model.w(qx)
    require(branch.low > 0, 'Certified upper best-response branch')
    contains(worst['upperBranchMargin'], branch, 'Upper-branch enclosure')
    ncs, cs = model.diagonal_cs(nx), model.diagonal_cs(qx)
    own, br = model.scale*model.diagonal_profit(qx), model.scale*model.w(qx)
    contains(nash['price'], model.cost+model.mu*nx, 'Physical Nash price')
    contains(worst['price'], model.cost+model.mu*qx, 'Physical worst price')
    contains(nash['consumerSurplus'], ncs, 'Nash customer surplus')
    certified_cs = contains(worst['consumerSurplus'], cs, 'Worst customer surplus')
    for key, value in [('profitA', own), ('profitB', own), ('jointProfit', 2*own), ('unilateralBestResponseProfit', br), ('stationaryUnilateralDeviationGain', br-own)]:
        contains(worst[key], value, 'Stationary economics '+key)
    contains(record['nashToWorstSurplusGap'], ncs-cs, 'Nash-to-worst welfare gap')
    for row in record['comparisons']:
        threshold = Decimal(row['thresholdExact'])
        expected = 'all-start failing continuation' if certified_cs.high < threshold else 'already guaranteed' if certified_cs.low >= threshold else 'unresolved'
        require(row['classification'] == expected, 'Classification follows retained validated interval')
        if expected == 'all-start failing continuation':
            require(cs.high < threshold, 'Independent strict below-target upper bound')
        if expected == 'already guaranteed':
            require(cs.low >= threshold, 'Independent target lower bound')
    return {'scenario': record['scenario'], 'continuum': kind, 'status': record['status'],
            'independentCS': cs.strings(), 'independentRho': rho.strings(),
            'classifications': {r['label']: r['classification'] for r in record['comparisons']}}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def audit(directory=None):
    global CHECKS
    CHECKS = 0
    directory = Path(directory or ROOT/'research/continuous-results')
    manifest, results, completion = [read(directory/name) for name in ['manifest.json', 'results.json', 'completion.json']]
    for group in ['sourceHashes', 'inputHashes']:
        for file, expected in manifest[group].items():
            require(digest(ROOT/file) == expected, 'Frozen dependency '+file)
            if group == 'sourceHashes':
                require(digest(directory/'sources'/file) == expected, 'Frozen source snapshot '+file)
    require(manifest['plan']['records'] == 16 and manifest['plan']['continuums'] == ['effective', 'nominal'] and manifest['plan']['precision'] >= 80, 'Frozen primary matrix and precision')
    require(manifest['plan']['targetLabels'] == LABELS, 'Fixed five labels')
    require(results['manifestSha256'] == digest(directory/'manifest.json') and completion['resultsSha256'] == digest(directory/'results.json'), 'Output identity hashes')
    require(completion['finalFrozenDependencyCheck']['passed'] is True, 'Final frozen dependencies rechecked')
    require(len(results['records']) == 16 and len({(r['scenario'], r['continuum']) for r in results['records']}) == 16, 'All sixteen records exactly once')
    old = read(ROOT/'research/handover-init-results/results.json')['records']
    old_audit = read(ROOT/'research/handover-init-results/independent-audit.json')
    require(old_audit['passed'] and old_audit['studyManifestHash'] == digest(ROOT/'research/handover-init-results/manifest.json'), 'Passed original target audit')
    details, fixture = [], None
    for scenario in manifest['plan']['scenarios']:
        case = read(ROOT/f"research/cycle-results/cases/{scenario['id']}-guard.json")
        require(case['scenario'] == scenario and case['id'] == scenario['id']+'-guard', 'Exact old model identity')
        targets = next(r['results'] for r in old if r['scenario'] == scenario)
        for kind in ['effective', 'nominal']:
            record = next(r for r in results['records'] if r['scenario'] == scenario['id'] and r['continuum'] == kind)
            require(record == read(directory/'records'/f"{scenario['id']}-{kind}.json"), 'Separate retained record receipt')
            details.append(check_record(record, case, targets))
            if fixture is None and record['status'] == 'certified theorem and enclosures':
                fixture = (record, case, targets)
    resolved = sum(r['status'] == 'certified theorem and enclosures' for r in results['records'])
    require(completion['records'] == 16 and completion['resolved'] == resolved and completion['unresolved'] == 16-resolved, 'Resolved/unresolved complete inventory')
    require(completion['resources']['apiCalls'] == 0 and completion['resources']['newTrainingRounds'] == 0, 'No API/training use')
    controls = {}
    require(fixture is not None, 'Actual resolved record for corruption controls')
    def root_mutation(r):
        r['worst']['normalizedPrice']['upper'] = str(HIGH.add(Decimal(r['worst']['normalizedPrice']['upper']), Decimal('0.01')))
    def condition_mutation(r):
        r['assumptions']['rho']['upper'] = '0'
    def classification_mutation(r):
        r['comparisons'][0]['classification'] = 'unresolved' if r['comparisons'][0]['classification'] != 'unresolved' else 'already guaranteed'
    def welfare_mutation(r):
        r['worst']['consumerSurplus']['lower'] = r['worst']['consumerSurplus']['upper'] = '0'
    for name, mutate in [('root', root_mutation), ('globalCondition', condition_mutation), ('classification', classification_mutation), ('welfareEnclosure', welfare_mutation)]:
        changed = copy.deepcopy(fixture[0]); mutate(changed)
        rejected = False
        try:
            check_record(changed, fixture[1], fixture[2])
        except (ValueError, KeyError):
            rejected = True
        require(rejected, 'Rejected actual-output corruption '+name)
        controls[name] = True
    return {'passed': True, 'completedAt': datetime.now(timezone.utc).isoformat(),
            'studyManifestHash': digest(directory/'manifest.json'), 'resultsSha256': digest(directory/'results.json'),
            'auditorSourceHash': digest(Path(__file__)), 'checks': CHECKS, 'records': 16,
            'resolved': resolved, 'comparisonCount': 80, 'corruptionNegativeControls': controls, 'details': details,
            'scope': 'Separate 130-digit directed intervals, log-residual Lambert-W brackets, independent saved-root signs/global hypotheses/economics/80 fixed comparisons. No import of primary interval/model functions. Decimal transcendental backend shared; not a formally verified arithmetic library. Mesh diagnostic has a separate full-enumeration audit.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.directory)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))
