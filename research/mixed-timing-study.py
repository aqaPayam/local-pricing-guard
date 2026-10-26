"""Prospective mixed-gap certificates. Importing performs no evidence reads.

Exact saved-weight finite arithmetic and exact rational interval-endpoint
control arithmetic; accepted directed80-digit kernel only for continuous sums.
No inherited cases may execute until the distinct-goal/review/freeze gates.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal, Context, localcontext, ROUND_FLOOR, ROUND_CEILING
from dataclasses import dataclass
import argparse, hashlib, importlib.util, json, math, platform, shutil, sys, time
from datetime import datetime, timezone

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'research/mixed-timing-results'
MAX_K = 65536
DISPLAY_PRECISION = 30
SCENARIOS = ['base-g15-t1', 'scale0.5-g15-t1', 'lower-quality-g15-t1',
             'lowcost-g15-t1', 'base-g11-t1', 'base-g31-t1',
             'base-g15-t0.5', 'base-g15-t2']
LABELS = ['cap-90pct', 'cap-95pct', 'cap-99pct', 'cap-100pct', 'near-Nash-anchor-floor']
KINDS = ['finite', 'effective', 'nominal']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_float(value):
    require(isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value), 'Finite binary64 number required')
    return Q(float(value))


def exact(value):
    if isinstance(value, dict):
        return Q(int(value['numerator']), int(value['denominator']))
    return Q(value)


def ratio(value):
    value = Q(value)
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def sign(value):
    return 'negative' if value < 0 else 'positive' if value > 0 else 'zero'


def display(value):
    value = Q(value)
    out = {}
    for name, rounding in [('lower', ROUND_FLOOR), ('upper', ROUND_CEILING)]:
        with localcontext(Context(prec=DISPLAY_PRECISION, rounding=rounding,
                                  Emin=-999999, Emax=999999)):
            out[name] = str(Decimal(value.numerator) / Decimal(value.denominator))
    return {**out, 'significantDigits': DISPLAY_PRECISION}


@dataclass(frozen=True)
class Bounds:
    lo: Q
    hi: Q
    provenance: object = None

    def __post_init__(self):
        object.__setattr__(self, 'lo', Q(self.lo))
        object.__setattr__(self, 'hi', Q(self.hi))
        require(self.lo <= self.hi, 'Reversed rational enclosure')

    @classmethod
    def point(cls, value):
        return cls(Q(value), Q(value))

    @classmethod
    def inherited(cls, value, source=None):
        return cls(Q(value['lower']), Q(value['upper']),
                   {'source': source, 'originalInterval': value})

    def subtract(self, value):
        return Bounds(self.lo-value, self.hi-value,
                      {'operation': 'subtract exact threshold times length',
                       'input': self.provenance, 'subtracted': ratio(value)})

    def json(self):
        return {'lowerExact': ratio(self.lo), 'upperExact': ratio(self.hi),
                'outwardDisplay': {'lower': display(self.lo)['lower'],
                                   'upper': display(self.hi)['upper'],
                                   'significantDigits': DISPLAY_PRECISION},
                'provenance': self.provenance}


class Envelope:
    """All period queries, including inherited-cache hits, obey one ceiling."""
    def __init__(self):
        self.query_lengths = []
        self.query_failures = []
        self.cache = {}

    def get(self, length):
        require(type(length) is int and 1 <= length <= MAX_K,
                'Period query outside prospectively declared1..65536')
        self.query_lengths.append(length)
        if length not in self.cache:
            try:self.cache[length] = self._sum(length)
            except Exception as error:
                self.query_failures.append({'period':length,'error':str(error),'errorType':type(error).__name__})
                raise
        return self.cache[length]


class FiniteEnvelope(Envelope):
    def __init__(self, raw):
        super().__init__()
        self.raw = raw
        f = raw['finite']; self.finite = f
        prices = f['prices']; n = len(prices); cap = f['capIndex']
        require(0 < n <= 62 and type(cap) is int and 0 <= cap < n, 'Finite quote/cap identity')
        require(all(isinstance(p, (int, float)) and math.isfinite(p)
                    and (not i or p > prices[i-1]) for i,p in enumerate(prices)), 'Increasing prices required')
        sets = f['sets']
        require(len(sets) == n and all(s and all(type(a) is int and 0 <= a < n
                and (not j or a > s[j-1]) for j,a in enumerate(s)) for s in sets), 'Sorted nonempty masks')
        self.upper = [s[-1] for s in sets]
        require(f.get('upper', self.upper) == self.upper, 'Recorded upper map differs')
        require(all(not i or u >= self.upper[i-1] for i,u in enumerate(self.upper)), 'Upper map not monotone')
        require(self.upper[cap] >= cap, 'Cap-start upper orbit is not nondecreasing')
        values = [exact_float(v) for v in f['rewards']['consumerSurplus']]
        require(len(values) == n*n, 'CS table dimensions')
        for i in range(n):
            for j in range(n):
                require((i+1 == n or values[i*n+j] >= values[(i+1)*n+j]) and
                        (j+1 == n or values[i*n+j] >= values[i*n+j+1]), 'Coordinate CS monotonicity')
        self.n = n; self.cap_index = cap; self.orbit = [cap]
        while self.upper[self.orbit[-1]] != self.orbit[-1]:
            following = self.upper[self.orbit[-1]]
            require(following > self.orbit[-1] and len(self.orbit) < n, 'Finite cap orbit failed fixed-point proof')
            self.orbit.append(following)
        self.rewards = [values[i*n+i] for i in self.orbit]
        self.r0 = Bounds.point(self.rewards[0]); self.cstar = Bounds.point(self.rewards[-1])
        self.kind = 'finite'

    def _sum(self, length):
        count = len(self.rewards)
        total = sum(self.rewards[:length], Q(0)) if length <= count else (
            sum(self.rewards, Q(0)) + (length-count)*self.rewards[-1])
        return Bounds(total, total, {'method': 'Exact cap-start orbit plus constant fixed-point tail',
                                    'length': length})

    def reward(self, age):
        return Bounds.point(self.rewards[min(age, len(self.rewards)-1)])

    def price(self, age):
        at = self.orbit[min(age, len(self.orbit)-1)]
        return {'index': at, 'priceExact': ratio(exact_float(self.finite['prices'][at]))}

    def summary(self):
        return {'kind': self.kind, 'capIndex': self.cap_index,
                'capPriceExact': ratio(exact_float(self.finite['prices'][self.cap_index])),
                'upperOrbitIndices': self.orbit, 'limitIndex': self.orbit[-1],
                'r0': self.r0.json(), 'Cstar': self.cstar.json(),
                'scope': 'Cap-start upper-orbit limit; not arbitrary old guard cycles'}


_BACKEND = None
def interval_backend():
    global _BACKEND
    if _BACKEND is None:
        spec = importlib.util.spec_from_file_location('mixed_frozen_interval', ROOT/'research/continuous_interval.py')
        module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
        spec.loader.exec_module(module); _BACKEND = module
    return _BACKEND


class ContinuousEnvelope(Envelope):
    def __init__(self, record, source):
        super().__init__(); self.record = record; self.source = source
        require(record['status'] == 'certified recurring-cap enclosures', 'Closed continuous record not certified')
        require(record['conditions']['ellAtMostCap'] is True and
                record['conditions']['capStrictlyBelowQStar'] is True, 'Closed cap conditions not certified')
        self.steps = record['orbit']; require(len(self.steps) == 64 and record['prefixTerms'] == 64, 'Closed64-term orbit required')
        require([s['j'] for s in self.steps] == list(range(64)), 'Orbit age identities differ')
        self.r0 = Bounds.inherited(self.steps[0]['consumerSurplus'], source+'#orbit/0')
        self.cstar = Bounds.inherited(record['inheritedContinuum']['consumerSurplus'], source+'#inheritedContinuum')
        self.kind = record['continuum']; require(self.kind in ['effective','nominal'], 'Continuous model kind')
        for value in record['periodEvaluations']:
            length = value['period']; require(type(length) is int and 1 <= length <= MAX_K, 'Inherited period outside ceiling')
            require(length not in self.cache, 'Duplicate inherited period')
            self.cache[length] = Bounds.inherited(value['cycleSumConsumerSurplus'], source+f'#period/{length}')

    def _sum(self, length):
        # Only missing bounded sums use the unchanged accepted80-digit tail
        # formula. No new upper-price root or changed economic model is solved.
        kernel = interval_backend(); I = kernel.Interval
        total = I(0)
        for step in self.steps[:min(length,64)]:
            v = step['consumerSurplus']; total = total + I(v['lower'],v['upper'])
        if length > 64:
            count = length-64; rho = I(self.record['inheritedContinuum']['rho']['upper'])
            require(rho.lo >= 0 and rho.hi < 1, 'Inherited contraction domain')
            power = I(1); factor = rho; exponent = count
            while exponent:
                if exponent & 1: power = power*factor
                factor = factor*factor; exponent //= 2
            geometric = (1-power)/(1-rho)
            imported = self.record['importedBinary64']
            mass = exact(imported['buyers'])*exact(imported['mu'])
            distance = self.record['qStarMinusAJ']
            require(mass>0 and Q(distance['lower'])>=0,'Positive mass/nonnegative contraction-tail distance required')
            excess = I(kernel.fraction_decimal(mass))*I(distance['lower'],distance['upper'])*geometric
            star = self.record['inheritedContinuum']['consumerSurplus']
            total = total + count*I(star['lower'],star['upper']) + I(0,excess.hi)
        return Bounds(Q(total.lo),Q(total.hi),{'method':'Accepted80-digit64-prefix contraction tail',
                                              'source':self.source,'length':length,'originalInterval':total.json()})

    def reward(self, age):
        require(0 <= age < 64, 'Continuous preview exceeds accepted orbit rows')
        return Bounds.inherited(self.steps[age]['consumerSurplus'], self.source+f'#orbit/{age}')

    def price(self, age):
        require(0 <= age < 64, 'Continuous preview exceeds accepted orbit rows')
        return {'priceEnclosure': self.steps[age]['executedPrice']}

    def summary(self):
        return {'kind':self.kind,'source':self.source,'physicalCap':self.record['physicalCap'],
                'r0':self.r0.json(),'Cstar':self.cstar.json(),
                'scope':'Accepted continuous cap-start attained envelope; prices/rewards remain enclosures'}


def mixing(a,b):
    a,b = Q(a),Q(b)
    require(a >= 0 and b < 0, 'Safe/strict-failing adjacent credits required')
    return a/(a-b)


def calendar_blocks(K,a,b=None,count=64):
    a = Q(a); b = Q(b) if b is not None else None
    require(type(K) is int and 1 <= K <= MAX_K and a >= 0, 'Calendar safe gap/credit')
    require(b is None or b < 0 and K+1 <= MAX_K, 'Calendar next gap/credit')
    credit = Q(0); start = 1; rows = []
    for block in range(1,count+1):
        longer = b is not None and a > 0 and credit >= -b
        length = K+int(longer); endpoint = b if longer else a
        after = credit+endpoint; require(after >= 0, 'Unfunded calendar block')
        if b is not None: require(after < a-b, 'Bounded credit invariant failed')
        rows.append({'block':block,'startExecution':start,'length':length,
                     'long':longer,
                     'boundaryCreditBeforeExact':ratio(credit),'blockEndpointCreditExact':ratio(endpoint),
                     'boundaryCreditAfterExact':ratio(after)})
        credit = after; start += length
    return rows


def preview(envelope,F,calendar):
    if calendar['kind'] == 'unavailable': return []
    limit = 256 if envelope.kind == 'finite' else 64
    startup = calendar['kind'] == 'startup-only'; K = calendar.get('K')
    a = exact(calendar['creditAExact']) if calendar.get('creditAExact') else None
    b = exact(calendar['creditBExact']) if calendar.get('creditBExact') else None
    credit = Q(0); age = 0; length = None; endpoint = None; total_lo = Q(0); total_hi = Q(0); rows = []; previous = None
    for execution in range(1,limit+1):
        if not startup and age == 0:
            longer = b is not None and a > 0 and credit >= -b
            length = K+int(longer); endpoint = b if longer else a
        reward = envelope.reward(age); total_lo += reward.lo; total_hi += reward.hi
        prefix = Bounds(total_lo-execution*F,total_hi-execution*F)
        lower = execution*(envelope.cstar.lo-F) if startup else credit+min(Q(0),endpoint)
        require(lower >= 0, 'Prefix proof lower bound negative')
        require(prefix.hi >= lower, 'Raw cumulative enclosure contradicts certified prefix lower bound')
        before = credit; completed = not startup and age+1 == length
        if completed: credit += endpoint
        if envelope.kind == 'finite': require(prefix.lo >= 0, 'Exact finite activation prefix failed')
        price=envelope.price(age)
        rows.append({'execution':execution,'mode':'cap' if age == 0 else 'guard','age':age,
                     'plannedGapLength':None if startup else length,
                     'previousExecutedPrice':previous,
                     'previousIndices':[previous['index']]*2 if previous is not None and 'index' in previous else None,
                     'executedIndices':[price['index']]*2 if 'index' in price else None,
                     'executedPrice':price,'rewardBounds':reward.json(),
                     'boundaryCreditBeforeExact':ratio(before),'boundaryCreditAfterExact':ratio(credit),
                     'completedBlock':completed,'cumulativePrefixExcessBounds':prefix.json(),
                     'certifiedPrefixLowerBoundExact':ratio(lower),
                     'scope':'Bounded upper-envelope illustration; not learned/human behavior or limiting-rate estimate'})
        previous=price
        age = 0 if completed else age+1
    return rows


def frontier(envelope,F):
    started=len(envelope.query_lengths)
    safe = 0; failed = None
    first = envelope.get(1)
    if first.lo < F: return {'safeK':0,'failingK':1 if first.hi < F else None,'adjacent':False}
    safe = 1; length = 2
    while length <= MAX_K:
        value = envelope.get(length)
        if value.hi < length*F: failed = length; break
        if value.lo >= length*F: safe = length
        if length == MAX_K: break
        length = min(MAX_K,2*length)
    if failed is None: return {'safeK':safe,'failingK':None,'adjacent':False}
    low,high = safe,failed
    while high-low > 1:
        middle = (low+high)//2
        if envelope.get(middle).lo >= middle*F: low = middle
        else: high = middle
    safe = low; low,high = safe,failed
    while high-low > 1:
        middle = (low+high)//2
        if envelope.get(middle).hi < middle*F: high = middle
        else: low = middle
    # Preserve the strongest witnesses actually encountered, without claiming
    # that ambiguous enclosures were globally resolved or querying new lengths.
    queried=set(envelope.query_lengths[started:])
    safe=max((k for k in queried if envelope.cache[k].lo >= k*F),default=0)
    high=min((k for k in queried if envelope.cache[k].hi < k*F),default=None)
    require(not safe or high is None or safe < high,'Contradictory monotone frontier witnesses')
    return {'safeK':safe,'failingK':high,'adjacent':high == safe+1 if high is not None else False}


def rate_fields(lower,upper,constructed,bestK=None,pbounds=None):
    fixed = Q(1,bestK) if bestK is not None else None
    def box(lo,hi): return {'lower':ratio(lo),'upper':ratio(hi)}
    out = {'bestFixedK':bestK,'fixedRateExact':ratio(fixed) if fixed is not None else None,
           'optimumRateBoundsExact':box(lower,upper),
           'optimumRateDisplay':{'lower':display(lower)['lower'],'upper':display(upper)['upper'],
                                 'significantDigits':DISPLAY_PRECISION},
           'constructedRateExact':ratio(constructed),'constructedRateDisplay':display(constructed),
           'optimalityGapUpperExact':ratio(constructed-lower),
           'mixFractionBoundsExact':box(*pbounds) if pbounds is not None else None,
           'absoluteSavingBoundsExact':box(fixed-upper,fixed-lower) if fixed is not None else None,
           'relativeSavingBoundsExact':box((fixed-upper)/fixed,(fixed-lower)/fixed) if fixed is not None else None,
           'constructedSavingExact':ratio(fixed-constructed) if fixed is not None else None,
           'exactOptimum':lower == upper}
    if fixed is not None:
        out['absoluteSavingSigns']={'lower':sign(fixed-upper),'upper':sign(fixed-lower)}
        out['relativeSavingSigns']={'lower':sign((fixed-upper)/fixed),'upper':sign((fixed-lower)/fixed)}
        out['constructedSavingSign']=sign(fixed-constructed)
    if pbounds is not None:out['mixFractionSigns']={'lower':sign(pbounds[0]),'upper':sign(pbounds[1])}
    return out


def solve_target(envelope,F,label,identity=None):
    F = Q(F); start_query = len(envelope.query_lengths)
    out = {'label':label,'actualThresholdExact':ratio(F),'identity':identity,'status':'unresolved',
           'frontier':{'maxK':MAX_K,'bestFixedK':None,'certifiedSafeK':None,'safe':None,'failing':None},
           'rates':None,'calendar':{'kind':'unavailable','K':None,'creditAExact':None,'creditBExact':None,
                                   'startupCaps':None,'creditUpperExclusiveExact':None,'blockPreview64':[]},'executionPreview':[]}
    if F <= envelope.cstar.lo:
        out['status'] = 'certified startup-only zero limiting rate'
        out['rates'] = rate_fields(Q(0),Q(0),Q(0))
        out['rates']['fixedFamilyInfimumRateExact'] = ratio(0)
        out['calendar'].update(kind='startup-only',startupCaps=1)
    elif F > envelope.r0.hi:
        out['status'] = 'infeasible cap-first two-mode family'
        out['reason'] = 'Feasible upper response fails the first actual cap atT1'
    else:
        f = frontier(envelope,F); safe,failed = f['safeK'],f['failingK']
        out['frontier']['certifiedSafeK'] = safe or None
        if safe:
            s = envelope.get(safe); a = s.subtract(safe*F)
            out['frontier']['safe'] = {'period':safe,'sumBounds':s.json(),'excessBounds':a.json()}
        if failed is not None:
            s = envelope.get(failed); b = s.subtract(failed*F)
            out['frontier']['failing'] = {'period':failed,'sumBounds':s.json(),'excessBounds':b.json()}
        if f['adjacent']:
            require(a.lo >= 0 and b.hi < 0,'Adjacent frontier sign certificate failed')
            pL,pU = mixing(a.lo,b.lo),mixing(a.hi,b.hi)
            rateL,rateU = 1/(safe+pU),1/(safe+pL)
            out['frontier']['bestFixedK'] = safe
            out['rates'] = rate_fields(rateL,rateU,rateU,safe,(pL,pU))
            out['status'] = ('certified exact mixed optimum' if rateL == rateU else
                             'certified continuous optimum enclosure')
            if envelope.kind == 'finite' and a.lo == 0:
                out['status'] = 'certified exact equality frontier; zero mixed saving'
            out['calendar'].update(kind='funded-mixed',K=safe,creditAExact=ratio(a.lo),
                                   creditBExact=ratio(b.lo),startupCaps=1,
                                   creditUpperExclusiveExact=ratio(a.lo-b.lo),
                                   blockPreview64=calendar_blocks(safe,a.lo,b.lo))
        elif safe:
            out['status'] = ('censored safe ceiling' if safe == MAX_K else
                             'unresolved certified frontier bracket')
            rateL = Q(1,failed) if failed is not None else Q(0)
            out['rates'] = rate_fields(rateL,Q(1,safe),Q(1,safe))
            out['rates']['exactOptimum'] = False
            out['calendar'].update(kind='fixed-safe',K=safe,creditAExact=ratio(a.lo),startupCaps=1,
                                   blockPreview64=calendar_blocks(safe,a.lo))
        else:
            out['status'] = 'unresolved cap/target boundary; no certified schedule'
            out['reason'] = 'No certified safe bounded period; overlap is not equality or zero'
    out['frontier']['queryLengths'] = envelope.query_lengths[start_query:]
    out['executionPreview'] = preview(envelope,F,out['calendar'])
    out['prefixCertificateScope'] = 'Every prefix from the first actual cap; not sliding windows or arbitrary old guard histories'
    return out


def planned_models():
    return [{'id':sid+'--'+kind,'scenario':sid,'kind':kind,'labels':LABELS.copy(),
             'finiteFile':f'research/sparse-display-results/cases/{sid}.json',
             'continuousFile':None if kind=='finite' else f'research/recurring-results/records/{sid}-{kind}.json'}
            for sid in SCENARIOS for kind in KINDS]


def failed_slot(plan,label,error,F=None,identity=None):
    return {'id':plan['id']+'--'+label,'label':label,'scenario':plan['scenario'],
            'kind':plan['kind'],'status':'unresolved calculation or identity',
            'actualThresholdExact':ratio(F) if F is not None else None,'identity':identity,
            'duplicateOf':None,'frontier':{'maxK':MAX_K,'bestFixedK':None,'certifiedSafeK':None,
                                        'safe':None,'failing':None,'queryLengths':[]},
            'rates':None,'calendar':{'kind':'unavailable','K':None,'creditAExact':None,
                                   'creditBExact':None,'startupCaps':None,'creditUpperExclusiveExact':None,'blockPreview64':[]},
            'executionPreview':[],'error':str(error),'errorType':type(error).__name__}


def prepare_model(plan,raw,closed=None):
    require(raw['scenario']['id']==plan['scenario'],'Finite scenario differs from plan')
    require(raw['cap']['index']==raw['finite']['capIndex'],'Physical cap index differs from saved quote')
    require(exact_float(raw['cap']['price'])==exact_float(raw['finite']['prices'][raw['finite']['capIndex']]),
            'Physical cap differs from saved quote')
    rows=raw['originalTargets'];require(len(rows)==5 and {r['label'] for r in rows}==set(LABELS),'Five target identities required')
    targets=[]
    if plan['kind']=='finite':
        envelope=FiniteEnvelope(raw)
    else:
        require(closed is not None and closed['scenario']==plan['scenario'] and
                closed['continuum']==plan['kind'],'Continuous scenario/kind differs')
        require(exact(closed['physicalCap']['physicalPriceImported'])==exact_float(raw['cap']['price']),
                'Continuous/finite physical cap price differs')
        for key,value in raw['scenario']['economy'].items():
            if key!='id':require(exact(closed['importedBinary64'][key])==exact_float(value),'Imported economy differs '+key)
        envelope=ContinuousEnvelope(closed,plan['continuousFile'])
    for label in LABELS:
        row=next(r for r in rows if r['label']==label);F=exact_float(row['actualGuaranteedThreshold'])
        identity={'finiteSource':plan['finiteFile'],'requestedExact':ratio(exact_float(row['requestedTarget'])),
                  'actualThresholdExact':ratio(F),'numericalMarginImportedExact':ratio(exact_float(row['numericalMargin']))}
        if closed is not None:
            matches=[r for r in closed['comparisons'] if r['label']==label]
            require(len(matches)==1,'Unique closed continuous target required');old=matches[0]
            require(exact(old['actualThresholdImported'])==F and
                    exact(old['requestedImported'])==exact_float(row['requestedTarget']),'Closed target identity differs')
            identity.update(continuousSource=plan['continuousFile'],closedTarget=old)
        targets.append({'label':label,'F':F,'identity':identity})
    return envelope,targets


def execute_model(plan,loader):
    """The loader is injected for artificial failure tests; no I/O on import."""
    began=time.perf_counter();result={**plan,'status':'unresolved model identity','envelope':None,
                                   'targets':[],'calculationFailures':0,'queriedSums':[],'queryFailures':[]}
    try:
        envelope,targets=loader(plan)
        require(len(targets)==5 and [r['label'] for r in targets]==LABELS,'Planned five target slots differ')
        result['envelope']=envelope.summary();seen={}
        for row in targets:
            label,F,identity=row['label'],row['F'],row['identity']
            before_query=len(envelope.query_lengths)
            try:
                target=solve_target(envelope,F,label,identity)
            except Exception as error:
                target=failed_slot(plan,label,error,F,identity);result['calculationFailures']+=1
                target['frontier']['queryLengths']=envelope.query_lengths[before_query:]
            target.update(id=plan['id']+'--'+label,scenario=plan['scenario'],kind=plan['kind'],
                          duplicateOf=seen.get(F));seen.setdefault(F,target['id'])
            result['targets'].append(target)
        result['status']='completed timing certificate calculations' if not result['calculationFailures'] else 'retained target calculation failures'
        result['queriedSums']=[{'period':length,'sumBounds':envelope.cache[length].json() if length in envelope.cache else None}
                               for length in sorted(set(envelope.query_lengths))]
        result['queryFailures']=envelope.query_failures.copy()
    except Exception as error:
        result['error']=str(error);result['errorType']=type(error).__name__
        result['targets']=[failed_slot(plan,label,error) for label in LABELS]
        result['calculationFailures']=5
    result['seconds']=time.perf_counter()-began
    return result


SOURCES=['research/mixed-timing-study.py','tests/test_mixed_timing.py',
         'research/MIXED_TIMING_PROTOCOL.md','research/MIXED_TIMING_THEORY.md',
         'research/MIXED_TIMING_NOVELTY.md','research/MIXED_TIMING_CONCEPT_REVIEW.md',
         'research/MIXED_TIMING_PROSPECTIVE_REVIEW.md','research/MIXED_TIMING_ANALYSIS_CONTRACT.md',
         'research/audit-mixed-timing.js','research/audit-mixed-continuous.py',
         'research/audit-mixed-study.py','tests/test_mixed_audit_driver.py',
         'tests/mixed-timing-audit.test.js','tests/test_mixed_continuous_audit.py',
         'tests/test_mixed_timing_cross_audit.py']


def digest(file):
    file=contained(file)
    h=hashlib.sha256()
    with Path(file).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def read(file):
    return json.loads(contained(file).read_text(encoding='utf-8-sig'))


def save(file,value):
    file=contained(file);file.parent.mkdir(parents=True,exist_ok=True)
    with file.open('x',encoding='utf-8') as f:
        f.write(json.dumps(value,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n')


def contained(file):
    file=Path(file).resolve()
    require(file==ROOT or ROOT in file.parents,'Evidence path escapes this workspace')
    return file


def manifest_closure(seeds,files=None,load=read,hash_file=digest):
    """Validate nested manifest maps, including conflicts/cycles; injectable synthetic I/O."""
    files={} if files is None else files
    visited=set()
    def bind(name,expected=None):
        name=contained(ROOT/name).relative_to(ROOT).as_posix()
        actual=hash_file(ROOT/name)
        require(expected is None or actual==expected,'Frozen inherited dependency changed '+name)
        require(name not in files or files[name]==actual,'Conflicting inherited hash '+name)
        files[name]=actual
        return name
    def visit(name,expected=None):
        name=bind(name,expected)
        if name in visited:return
        visited.add(name)
        manifest=load(ROOT/name)
        require('sourceHashes' in manifest or 'inputHashes' in manifest,
                'Inherited manifest has no declared source/input hash maps '+name)
        for group in ['sourceHashes','inputHashes']:
            mapping=manifest.get(group,{})
            require(isinstance(mapping,dict),'Inherited manifest map malformed '+name+' '+group)
            for dep,h in mapping.items():
                dep=bind(dep,h)
                if Path(dep).name=='manifest.json':visit(dep,h)
    for name in seeds:visit(name)
    return files


def inventory():
    """Read-only inherited identity gate. Call only after future execution GO."""
    files=manifest_closure(['research/sparse-display-results/manifest.json',
                            'research/recurring-results/manifest.json',
                            'research/continuous-results/manifest.json',
                            'research/handover-init-results/manifest.json'])
    def use(name):
        h=digest(ROOT/name);require(name not in files or files[name]==h,'Conflicting inherited hash')
        files[name]=h;return read(ROOT/name)
    for folder,audits in [('sparse-display-results',['independent-audit.json','rational-audit.json']),
                          ('recurring-results',['independent-audit.json'])]:
        prefix='research/'+folder+'/'
        manifest=use(prefix+'manifest.json')
        for filename in audits:
            audit=use(prefix+filename)
            require(audit['passed'] is True and audit['studyManifestHash']==digest(ROOT/(prefix+'manifest.json')),
                    'Inherited audit/manifest binding differs')
            controls=audit.get('corruptionNegativeControls',{})
            require(bool(controls) and all(v is True for v in controls.values()),'Inherited corruption controls failed')
            auditor='research/audit-sparse-display.js' if folder=='sparse-display-results' and filename=='independent-audit.json' else 'research/audit-sparse-reset.py'
            require(audit['auditorSourceHash']==digest(ROOT/auditor),'Inherited independent source differs');files[auditor]=digest(ROOT/auditor)
            for field,name in [('indexSha256','index.json'),('resultsSha256','results.json')]:
                if field in audit:require(audit[field]==digest(ROOT/(prefix+name)),'Inherited output binding differs')
        for name in ['completion.json']:
            done=use(prefix+name);require(done.get('passed',done.get('finalFrozenDependencyCheck',{}).get('passed')) is True,
                                         'Inherited completion did not pass')
            if folder=='recurring-results':
                require(done['records']==16 and done['resolved']==16 and done['unresolved']==0 and
                        done['targetLabels']==80 and done['resultsSha256']==digest(ROOT/(prefix+'results.json')),
                        'Closed continuous completion counts/binding differ')
            else:require(done['cases']==8 and done['failures']==0 and done['finalHashCheck'] is True,
                         'Closed finite completion counts differ')
    for folder,auditor in [('continuous-results','audit-continuous-study.py'),
                           ('handover-init-results','audit-handover-init.js')]:
        prefix='research/'+folder+'/'
        audit=use(prefix+'independent-audit.json');source='research/'+auditor
        require(audit['passed'] is True and audit['studyManifestHash']==digest(ROOT/(prefix+'manifest.json')),
                'Accepted global premise audit/manifest binding differs')
        require(audit['auditorSourceHash']==digest(ROOT/source),'Accepted global premise auditor changed')
        files[source]=digest(ROOT/source)
        controls=audit.get('corruptionNegativeControls',{})
        require(bool(controls) and all(v is True for v in controls.values()),'Accepted premise corruption controls failed')
        if folder=='continuous-results':
            require(audit['resultsSha256']==digest(ROOT/(prefix+'results.json')),
                    'Accepted global continuum results binding differs')
        use(prefix+'results.json')
    index=use('research/sparse-display-results/index.json')
    require(index['manifestSha256']==digest(ROOT/'research/sparse-display-results/manifest.json') and len(index['cases'])==8,
            'Finite case index differs')
    for sid in SCENARIOS:
        entries=[r for r in index['cases'] if r['scenario']==sid]
        require(len(entries)==1 and entries[0]['status']=='completed','Missing closed finite case')
        name='research/sparse-display-results/'+entries[0]['file'];use(name)
        require(digest(ROOT/name)==entries[0]['sha256'],'Closed finite file differs')
    aggregate=use('research/recurring-results/results.json')
    require(aggregate['manifestSha256']==digest(ROOT/'research/recurring-results/manifest.json') and len(aggregate['records'])==16,
            'Closed continuous aggregate differs')
    for plan in planned_models():
        if plan['kind']=='finite':continue
        record=use(plan['continuousFile'])
        matches=[r for r in aggregate['records'] if r['scenario']==plan['scenario'] and r['continuum']==plan['kind']]
        require(len(matches)==1 and matches[0]==record,'Closed continuous record/aggregate differs')
    receipt_name='output/adaptive-package-verification.json';delivery=use(receipt_name)
    require(delivery['verification']['passed'] is True and delivery['verification']['payloadHashesAndCRC'] is True,
            'Accepted V9 delivery receipt required')
    require(len(delivery['sha256'])==64 and all(c in '0123456789abcdef' for c in delivery['sha256']),'V9 archive identity malformed')
    archive=ROOT/delivery['archive'];present=archive.exists()
    if present:require(digest(archive)==delivery['sha256'],'Available V9 archive differs from receipt')
    return files,{'receipt':receipt_name,'receiptSha256':digest(ROOT/receipt_name),
                  'archive':delivery['archive'],'archiveSha256':delivery['sha256'],
                  'archivePresentAtVerification':present}


def plan_specification():
    return {'models':planned_models(),'modelCount':24,'targetLabels':120,
            'maxK':MAX_K,'displayPrecision':DISPLAY_PRECISION,
            'blockPreviewLimit':64,'finiteExecutionPreviewLimit':256,
            'continuousExecutionPreviewLimit':64,
            'softResourceTargets':{'seconds':1800,'observedRSSBytes':250000000,'newOutputBytes':50000000},
            'scope':'Same physical cap/full guard; pathwise every activation prefix; worst-path limiting cap-rule frequency'}


def freeze(directory=OUT):
    directory=contained(directory);require(not directory.exists() or not any(directory.iterdir()),'Evidence directory nonempty; no overwrite')
    files,delivery=inventory()
    manifest={'schemaVersion':1,'frozenAt':datetime.now(timezone.utc).isoformat(),
              'sourceHashes':{name:digest(ROOT/name) for name in SOURCES},'inputHashes':files,
              'v9Delivery':delivery,'plan':plan_specification()}
    for name in SOURCES:
        target=directory/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
        require(not target.exists(),'Source snapshot already exists');shutil.copyfile(ROOT/name,target)
    save(directory/'manifest.json',manifest)
    return {'manifestSha256':digest(directory/'manifest.json'),'plannedModels':24,'plannedLabels':120}


def verify(directory=OUT):
    directory=Path(directory).resolve();manifest=read(directory/'manifest.json')
    require(manifest['plan']==plan_specification(),'Frozen plan differs')
    require(set(manifest['sourceHashes'])==set(SOURCES),'Frozen source inventory differs')
    for group in ['sourceHashes','inputHashes']:
        for name,h in manifest[group].items():
            require(digest(ROOT/name)==h,'Frozen mixed dependency changed '+name)
            if group=='sourceHashes':require(digest(directory/'sources'/name)==h,'Frozen source snapshot differs')
    _,delivery=inventory()
    require(delivery['receiptSha256']==manifest['v9Delivery']['receiptSha256'] and
            delivery['archiveSha256']==manifest['v9Delivery']['archiveSha256'],'Accepted V9 identity changed')
    return manifest


def assert_fresh(directory):
    for name in ['execution-start.json','journal.jsonl','records','results.json','index.json','completion.json']:
        require(not (Path(directory)/name).exists(),'Partial/closed evidence preserved; refusing rerun: '+name)


def rss_bytes():
    if sys.platform!='win32':return None
    try:
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in
                ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
                 'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
        c=Counters();c.cb=ctypes.sizeof(c)
        ctypes.windll.kernel32.GetCurrentProcess.restype=wintypes.HANDLE
        ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
        ctypes.windll.psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
        process=ctypes.windll.kernel32.GetCurrentProcess()
        if ctypes.windll.psapi.GetProcessMemoryInfo(process,ctypes.byref(c),c.cb):return c.WorkingSetSize
    except Exception:return None
    return None


def run(directory=OUT):
    directory=Path(directory).resolve();manifest=verify(directory);assert_fresh(directory)
    began=time.perf_counter();mh=digest(directory/'manifest.json')
    save(directory/'execution-start.json',{'startedAt':datetime.now(timezone.utc).isoformat(),'manifestSha256':mh})
    def journal(value):
        with (directory/'journal.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),**value},separators=(',',':'))+'\n')
    def loader(plan):
        for field in ['finiteFile','continuousFile']:
            name=plan[field]
            if name is not None:require(digest(ROOT/name)==manifest['inputHashes'][name],'Model input changed after verification')
        return prepare_model(plan,read(ROOT/plan['finiteFile']),
                             read(ROOT/plan['continuousFile']) if plan['continuousFile'] else None)
    records=[];indexed=[];samples=[]
    for plan in manifest['plan']['models']:
        journal({'id':plan['id'],'status':'started'})
        result=execute_model(plan,loader);name='records/'+plan['id']+'.json';save(directory/name,result)
        records.append(result);indexed.append({'id':plan['id'],'file':name,'sha256':digest(directory/name),
                                              'status':result['status'],'targetLabels':len(result['targets'])})
        samples.append({'id':plan['id'],'rssBytes':rss_bytes()})
        journal({'id':plan['id'],'status':result['status'],'calculationFailures':result['calculationFailures']})
        print(json.dumps({'id':plan['id'],'status':result['status'],'seconds':result['seconds']}),flush=True)
    save(directory/'results.json',{'manifestSha256':mh,'records':records})
    save(directory/'index.json',{'manifestSha256':mh,'records':indexed})
    try:verify(directory);final={'passed':True}
    except Exception as error:final={'passed':False,'error':str(error)}
    failures=sum(r['calculationFailures'] for r in records);count=sum(len(r['targets']) for r in records)
    measured=[s['rssBytes'] for s in samples if s['rssBytes'] is not None]
    elapsed=time.perf_counter()-began;size=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())
    completion={'passed':final['passed'] and len(records)==24 and count==120 and failures==0,
                'manifestSha256':mh,'models':len(records),'targetLabels':count,'calculationFailures':failures,
                'resultsSha256':digest(directory/'results.json'),'indexSha256':digest(directory/'index.json'),
                'finalFrozenDependencyCheck':final,'resources':{'seconds':elapsed,'rssSamples':samples,
                 'largestObservedRSSBytes':max(measured) if measured else None,'sampling':'Current Windows working set after each model, not continuous peak; unavailable on other systems',
                 'newOutputBytesBeforeCompletion':size,'experimentalModelApiCalls':0,'newTrainingRounds':0,
                 'python':platform.python_version(),'softTargetExceeded':{'seconds':elapsed>1800,
                 'observedRSS':max(measured)>250000000 if measured else None,'outputBytes':size>50000000}}}
    save(directory/'completion.json',completion);require(final['passed'],'Final dependency recheck failed')
    return completion


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['freeze','verify','run'])
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args();print(json.dumps(globals()[args.mode](args.output)))

