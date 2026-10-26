"""Independent shifted-demand audit; imports no new primary study functions.

The frozen independent 130-digit Box/model backend is reused with explicit
hashing. Standard Decimal is shared with the primary arithmetic implementation.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import importlib.util, hashlib, json, argparse, copy
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('frozen_independent_demand_backend',ROOT/'research/audit-continuous-study.py')
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)
B = backend.Box
LEVELS = [Fraction(0),Fraction(1,1000),Fraction(1,100),Fraction(1,20)]
checks = 0


def require(ok, message):
    global checks
    checks += 1
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def enclosed(saved, actual, label):
    result = backend.enclosure(saved)
    require(result.low <= actual.low and result.high >= actual.high,label+' independently enclosed')
    if 'width' in saved:
        require(Fraction(Decimal(saved['width'])) >= Fraction(result.high)-Fraction(result.low),label+' honest width')
    return result


def nonnegative_power(value, exponent):
    require(isinstance(exponent,int) and exponent >= 0 and value.low >= 0,'Nonnegative power domain')
    answer = B(1)
    while exponent:
        if exponent % 2:
            answer = answer*value
        value = value*value
        exponent //= 2
    return answer


def shifted_surplus(model, normalized_price, displacement):
    """Separate algebra: absorb d into exp(x+d), not nominal reward rescaling."""
    x,d = B.cast(normalized_price),B.cast(displacement)
    require(d.low >= 0,'Downward quality displacement must be nonnegative')
    return model.scale*(1+2/(model.k*(x+d).exp())).log()


def stationary_crossing(model, normalized_price, threshold):
    """Exact real crossing enclosure; may be negative if already failing at0."""
    require(Fraction(threshold)>0,'Positive fixed absolute target')
    x = B.cast(normalized_price)
    f = B.rational(threshold)
    return B(2).log()-model.k.log()-x-((f/model.scale).exp()-1).log()


class IndependentDemandCurve:
    def __init__(self,model,prices,a64,qstar,rho):
        self.model = model
        self.prices = [B.cast(p) for p in prices]
        self.a64,self.qstar,self.rho = map(B.cast,[a64,qstar,rho])
        require(len(self.prices)==64,'Closed 64-term nominal price prefix')
        require(self.rho.low >= 0 and self.rho.high < 1,'Closed contraction factor')
        gap = self.qstar-self.a64
        require(gap.high >= 0,'Nominal source orbit bounded by fixed point')
        self.distance = B(max(Decimal(0),gap.low),gap.high)
        self.cache = {}

    def value(self,period,displacement):
        d = B.cast(displacement)
        require(0 <= d.low <= d.high <= 8,'No actual-demand audit evaluation outside declared displacement domain')
        key = period,d.low,d.high
        if key in self.cache:
            return self.cache[key]
        if period is None:
            result = shifted_surplus(self.model,self.qstar,d)
        else:
            require(isinstance(period,int) and 1<=period<=65536,'Same declared fixed-period family')
            result = sum((shifted_surplus(self.model,p,d) for p in self.prices[:min(64,period)]),B(0))
            if period > 64:
                count = period-64
                rho = B(self.rho.high)
                geometric = (1-nonnegative_power(rho,count))/(1-rho)
                excess = self.model.scale*self.distance*geometric
                result += count*shifted_surplus(self.model,self.qstar,d)+B(0,excess.high)
            result = result/period
        self.cache[key] = result
        return result


def fixed_threshold(value):
    return Fraction(float(value))


def check_signed_radius(curve,period,threshold,lower,upper):
    """Certifies one crossing bracket without implementing primary root search."""
    lower,upper = Decimal(lower),Decimal(upper)
    require(Decimal(0)<=lower<upper<=Decimal(8),'Radius sign bracket within declared ceiling')
    require(Fraction(upper)-Fraction(lower)<=Fraction(1,10**20),'Declared radius width in exact arithmetic')
    f = B.rational(threshold)
    low_value,high_value = curve.value(period,B(lower)),curve.value(period,B(upper))
    require(low_value.low>=f.high,'Independently safe downward-error endpoint')
    require(high_value.high<f.low,'Independently failing downward-error endpoint')
    return low_value,high_value


def check_fixed_period_boundaries(curve,threshold,displacement,safe,failed):
    require(isinstance(safe,int) and isinstance(failed,int) and 1<=safe<failed<=65536,'Robust period bracket domain')
    f = B.rational(threshold)
    low_value = curve.value(safe,B.cast(displacement))
    high_value = curve.value(failed,B.cast(displacement))
    require(low_value.low>=f.high and high_value.high<f.low,'Independent robust safe/failing period inequalities')
    return low_value,high_value


def status_of(value,threshold):
    f = B.rational(threshold)
    if value.high < f.low:
        return 'already failing'
    if value.low == value.high == f.low == f.high:
        return 'exact zero reserve'
    if value.low >= f.high:
        return 'certified safe'
    return 'unresolved overlap'


def check_level(record,expected):
    require(Fraction(int(record['numerator']),int(record['denominator'])) == expected,'Exact rational uncertainty bound')
    require(Fraction(Decimal(record['exactDecimal'])) == expected,'Exact decimal uncertainty bound')
    require(record['units'] == 'dimensionless downward inside-quality shift divided by unchanged mu','Displacement units and direction')


def check_evaluation(record,curve,period,threshold,expected=None):
    d = Decimal(record['displacementExact'])
    if expected is not None:
        require(Fraction(d) == Fraction(expected),'Evaluation displacement identity')
    value = curve.value(period,B(d))
    saved = enclosed(record['surplus'],value,'Shifted actual surplus')
    enclosed(record['reserve'],value-B.rational(threshold),'Fixed absolute-target reserve')
    require(record['status'] == status_of(saved,threshold),'Saved interval classification at actual demand')
    return saved


def check_radius(record,curve,period,threshold):
    zero = check_evaluation(record['zero'],curve,period,threshold,0)
    require(Decimal(record['searchCeilingExact']) == 8 and Decimal(record['requiredBracketWidth']) == Decimal('1e-20'),'Prospective radius limits')
    simple = enclosed(record['simpleNominalReserveRatio'],(curve.value(period,B(0))-B.rational(threshold))/curve.model.scale,'Simple nominal reserve ratio')
    lower = record['certifiedSimpleSufficientRadiusLower']
    if lower is not None:
        require(Decimal(lower) == simple.low and simple.low > 0,'Certified conservative sufficient radius uses outward positive lower endpoint')
    stationary = period is None or period == 1
    if stationary:
        price = curve.qstar if period is None else curve.prices[0]
        analytic = stationary_crossing(curve.model,price,threshold)
        enclosed(record['stationaryClosedForm'],analytic,'Independent stationary radius closed form')
        require(Decimal(record['stationarySignPaddingExact']) == Decimal('1e-24'),'Predeclared stationary sign padding')
    else:
        require('stationaryClosedForm' not in record,'No false stationary formula for a multi-price cycle')
    status = record['status']
    if status == 'already failing at zero; empty safe nonnegative set':
        require(status_of(zero,threshold) == 'already failing' and record['safeNonnegativeSet'] == 'empty','Empty safe set distinct from radius zero')
        require(record['radiusEnclosure'] is None and lower is None,'No radius or positive reserve for already-failing target')
        return status
    if status == 'unresolved zero-displacement overlap':
        require(status_of(zero,threshold) == 'unresolved overlap' and record['radiusEnclosure'] is None,'Honest overlap at zero')
        return status
    if status == 'certified exact zero radius':
        require(status_of(zero,threshold) == 'exact zero reserve' and backend.enclosure(record['radiusEnclosure']).low == backend.enclosure(record['radiusEnclosure']).high == 0,'Certified equality at zero')
        require(record['safeNonnegativeSet'] == '[0,0]','Zero safe interval includes its endpoint only')
        return status
    require(status_of(zero,threshold) == 'certified safe','Radius search begins at a certified-safe zero')
    ceiling = check_evaluation(record['ceiling'],curve,period,threshold,8)
    if status == 'censored safe lower bound':
        require(status_of(ceiling,threshold) in ['certified safe','exact zero reserve'] and Decimal(record['certifiedRadiusLowerBound']) == 8 and record['radiusEnclosure'] is None,'Displacement ceiling censoring')
        return status
    if status == 'unresolved at displacement ceiling':
        require(status_of(ceiling,threshold) == 'unresolved overlap' and record['radiusEnclosure'] is None,'Unresolved ceiling overlap')
        return status
    require(status_of(ceiling,threshold) == 'already failing','Radius has a certified failing displacement ceiling')
    if 'stationarySignedCrossCheck' in record:
        check_evaluation(record['stationarySignedCrossCheck']['lower'],curve,period,threshold)
        check_evaluation(record['stationarySignedCrossCheck']['upper'],curve,period,threshold)
    left = check_evaluation(record['safeLower'],curve,period,threshold)
    right = check_evaluation(record['failingUpper'],curve,period,threshold)
    lo,hi = Decimal(record['safeLower']['displacementExact']),Decimal(record['failingUpper']['displacementExact'])
    require(left.low >= B.rational(threshold).high and right.high < B.rational(threshold).low,'Explicit radius endpoint surplus signs')
    if status == 'certified crossing enclosure':
        check_signed_radius(curve,period,threshold,lo,hi)
        bracket = backend.enclosure(record['radiusEnclosure'])
        require(bracket.low == lo and bracket.high == hi,'Radius interval equals its independently signed endpoints')
    else:
        require(status in ['unresolved crossing budget','unresolved crossing width'] and record['radiusEnclosure'] is None,'Only declared unresolved radius statuses')
        bracket = backend.enclosure(record['signedBracket'])
        require(bracket.low == lo and bracket.high == hi and 0 <= lo < hi <= 8,'Retained conservative signed unresolved interval')
        if status == 'unresolved crossing width':
            require(Fraction(hi)-Fraction(lo) > Fraction(1,10**20),'Honest unresolved radius-width limitation')
    return status


def check_period_record(record,curve,displacement):
    k = record['period']
    d = B.cast(displacement)
    require(Fraction(Decimal(record['displacementExact'])) == Fraction(d.low) and d.low == d.high,'Period demand displacement identity')
    value = curve.value(k,d)
    saved = enclosed(record['averageConsumerSurplus'],value,'Independent actual-demand period average')
    enclosed(record['cycleSumConsumerSurplus'],value*k,'Independent actual-demand cycle sum')
    if k <= 64:
        last = shifted_surplus(curve.model,curve.prices[k-1],d)
        require(record['tail'] is None,'No fabricated tail inside stored price prefix')
    else:
        rho = B(curve.rho.high)
        count = k-64
        geometric = (1-nonnegative_power(rho,count))/(1-rho)
        excess = curve.model.scale*curve.distance*geometric
        last_excess = curve.model.scale*curve.distance*nonnegative_power(rho,k-65)
        cstar = curve.value(None,d)
        last = cstar+B(0,last_excess.high)
        tail = record['tail']
        require(tail['firstOmittedIndex'] == 64 and tail['terms'] == count,'Actual-demand tail first omitted reward and length')
        enclosed(tail['constantFloor'],cstar,'Actual-demand tail floor')
        enclosed(tail['geometricSum'],geometric,'Unchanged nominal geometric multiplier')
        require(Decimal(tail['excessSumUpper']) >= excess.high and Decimal(tail['lastRoundExcessUpper']) >= last_excess.high,'Outward uniform price-tail bounds')
    enclosed(record['lastRoundConsumerSurplus'],last,'Separate actual individual-round floor')
    enclosed(record['capRuleActivationFrequency'],B(1)/k,'Rule activation rate')
    require(record['startupCapCount'] == 1 and Decimal(record['finiteActivationAverageLowerBound']) == saved.low,'Actual first cap and outward finite-average floor')
    return saved


def check_period_selection(record,curve,threshold,level):
    check_level(record['dbar'],level)
    d = B.rational(level)
    require(Fraction(Decimal(record['displacementExact'])) == level and Fraction(Decimal(record['thresholdExact'])) == threshold,'Robust period fixed threshold/displacement')
    require(record['searchCeiling'] == 65536,'No undeclared period ceiling')
    guard = enclosed(record['guardFloor'],curve.value(None,d),'Alternative-demand guard floor')
    f = B.rational(threshold)
    status = record['status']
    def period(field):
        return check_period_record(record[field],curve,d)
    if status == 'no recurring cap needed for the long-run target':
        require(guard.low >= f.high,'Robust guard-only long-run target')
        a,b = record['withoutIntervention'],record['oneImmediateCapThenOriginalGuard']
        require(a['startupCaps'] == 0 and b['startupCaps'] == 1 and a['recurringFrequency'] == b['recurringFrequency'] == 0,'Distinct zero-frequency startup policies')
        require(a['finiteActivationAverageGuaranteedFromArbitraryOldPrices'] is False and Decimal(b['finiteActivationAverageLowerBound']) == guard.low,'Finite-startup claim scoped to actual cap')
    elif status == 'infeasible for this fixed-cap family':
        require(record['strongestPeriod']['period'] == 1 and period('strongestPeriod').high < f.low,'Strongest inherited family member already fails')
    elif status == 'unresolved period-one boundary':
        one = period('strongestPeriod')
        require(record['strongestPeriod']['period'] == 1 and one.low < f.high <= one.high,'Honest robust period-one overlap')
    elif status in ['largest certified fixed period','certified integer bracket']:
        safe,failed = record['certifiedSafePeriodLowerBound'],record['certifiedFailingPeriodUpperBound']
        check_fixed_period_boundaries(curve,threshold,d,safe,failed)
        require(record['safePeriod']['period'] == safe and record['nextFailingPeriod']['period'] == failed,'Robust period boundary metadata')
        require(period('safePeriod').low >= f.high and period('nextFailingPeriod').high < f.low,'Saved robust period boundary signs')
        require(record['possibleLargestPeriodBracket'] == [safe,failed-1],'Possible robust maximum bracket')
        if status == 'largest certified fixed period':
            require(failed == safe+1 and record['largestPeriod'] == safe,'Adjacent robust boundaries establish same-family maximality')
        else:
            require(failed > safe+1 and record['largestPeriod'] is None,'Unresolved robust period bracket is not an optimum')
    elif status in ['censored safe lower bound','unresolved censored bracket']:
        safe = record['certifiedSafePeriodLowerBound']
        require(record['safePeriod']['period'] == safe and period('safePeriod').low >= f.high,'Certified robust lower period under censoring')
        require(record['certifiedFailingPeriodUpperBound'] is None and record['ceilingPeriod']['period'] == 65536 and record['largestPeriod'] is None,'Censoring does not invent period65537 or optimum')
        period('ceilingPeriod')
        require((safe == 65536) == (status == 'censored safe lower bound'),'Censored status matches certified period')
    else:
        raise ValueError('Unknown robust-period classification')
    require(all(2 <= k <= 65536 and k & (k-1) == 0 for k in record.get('doublingPeriods',[])),'Declared robust-period probes')
    return status


def check_policy(record,slot,expected,duplicate,curve,threshold):
    require(record['slot'] == slot and record['available'] == (expected[0] != 'unavailable'),'Retained policy slot/availability')
    policy = record['policy']
    require((policy['kind'],policy['period']) == expected,'Policy fixed before alternative-demand results')
    require(record['duplicateOf'] == duplicate,'Repeated policies retained as explicit duplicates')
    require(len(record['sensitivity']) == 4,'Four uncertainty assumptions for every policy')
    if expected[0] == 'unavailable':
        require(record['radius']['status'] == 'unavailable inherited policy','No invented selection from unresolved old result')
        return 'unavailable inherited policy'
    guard = expected[0] == 'guard'
    period = None if guard else expected[1]
    radius_status = check_radius(record['radius'],curve,period,threshold)
    rate = B(0) if guard else B(1)/period
    require(record['startupCapCount'] == (0 if guard else 1),'Policy startup execution count')
    enclosed(record['capRuleActivationFrequency'],rate,'Fixed policy recurring rate')
    if guard:
        variant = record['singleStartupCapVariant']
        require(variant['startupCapCount'] == 1 and variant['recurringFrequency'] == 0,'Single immediate cap distinguished from no intervention')
    else:
        require(record['singleStartupCapVariant'] is None,'Periodic policy not mislabeled a single finite initializer')
    for level,row in zip(LEVELS,record['sensitivity']):
        check_level(row['dbar'],level)
        d = B.rational(level)
        value = curve.value(period,d)
        saved = enclosed(row['surplus'],value,'Fixed-policy actual surplus at declared uncertainty')
        enclosed(row['reserve'],value-B.rational(threshold),'Fixed-policy true reserve against old absolute target')
        require(row['status'] == status_of(saved,threshold),'Policy target status from its own enclosure')
        require([Fraction(Decimal(v)) for v in row['uniformForFixedUnknownDIn']] == [0,level],'Uniform interval concerns unknown fixed displacement only')
        require(row['startupCapCount'] == (0 if guard else 1) and row['finiteActivationAverageGuaranteedFromArbitraryOldPrices'] == (not guard),'Guard-only finite-prefix scope distinct from cap-first policy')
        enclosed(row['capRuleActivationFrequency'],rate,'Sensitivity policy activation rate')
    return radius_status


def check_target(record,original,closed,curve):
    require(record['label'] == original['label'] == closed['label'],'Old target label identity')
    backend.validate_import(record['requestedImported'],original['requestedTarget'],'Misspec requested old target')
    backend.validate_import(record['actualThresholdImported'],original['actualGuaranteedThreshold'],'Misspec actual old threshold')
    threshold = fixed_threshold(original['actualGuaranteedThreshold'])
    require(Fraction(Decimal(record['actualThresholdExact'])) == threshold,'No target renormalization to weaker actual demand')
    require(record['closedSelectionStatus'] == closed['status'],'Closed zero-error selection origin')
    selected = ('guard',None) if closed['status'] == 'no recurring cap needed for the long-run target' else ('periodic',closed['largestPeriod']) if closed['status'] == 'largest certified fixed period' else ('unavailable',None)
    expected = [('guard-only',('guard',None)),('closed-selected',selected),('permanent-cap',('periodic',1))]
    require([r['slot'] for r in record['policies']] == [r[0] for r in expected],'All three policy slots retained in order')
    first,counts = {},{}
    for row,(slot,policy) in zip(record['policies'],expected):
        duplicate = first.get(policy) if policy[0] != 'unavailable' else None
        if policy[0] != 'unavailable':
            first.setdefault(policy,slot)
        if slot == 'closed-selected':
            require(row['policy']['originatingStatus'] == closed['status'],'Selected policy originating status not refit')
        status = check_policy(row,slot,policy,duplicate,curve,threshold)
        counts[status] = counts.get(status,0)+1
    require(len(record['robustPeriods']) == 4,'Every robust uncertainty-level row retained')
    statuses = [check_period_selection(row,curve,threshold,d) for row,d in zip(record['robustPeriods'],LEVELS)]
    keys = ['status','largestPeriod','certifiedSafePeriodLowerBound','certifiedFailingPeriodUpperBound','possibleLargestPeriodBracket']
    reproduces = all(record['robustPeriods'][0].get(k) == closed.get(k) for k in keys)
    require(record['d0ReproducesClosedSelection'] == reproduces,'Honest zero-shift closed-selection reproduction flag')
    # If two levels have exact finite optima, monotonicity forbids a rise.
    maxima = [r.get('largestPeriod') for r in record['robustPeriods']]
    require(all(a >= b for a,b in zip(maxima,maxima[1:]) if a is not None and b is not None),'Exact robust periods cannot increase with worse actual demand')
    return {'radiusStatuses':counts,'robustPeriodStatuses':statuses,'zeroReproduces':reproduces}


def check_record(record,scenario,guard,old_recurring,old_continuous,old_targets):
    require(record['scenario'] == scenario['id'] == guard['scenario']['id'] and record['continuum'] == old_recurring['continuum'] == old_continuous['continuum'],'Actual/nominal model labels')
    require(scenario == guard['scenario'],'Nominal enforcement economy unchanged')
    require(record['actualDemand'] == 'Inside quality = inherited quality - d*unchanged mu; outside quality/enforcement unchanged','Actual versus enforced demand identity')
    require([r['label'] for r in record['targets']] == backend.LABELS,'All five target/model rows retained')
    if record['status'] != 'completed alternative-demand comparisons':
        require(record['status'] == 'unresolved calculation or inherited condition' and bool(record['failure']),'Retained whole-model failure')
        require(all(len(t['policies']) == 3 and len(t['robustPeriods']) == 4 for t in record['targets']),'Failure retains every planned policy/period slot')
        return {'scenario':record['scenario'],'continuum':record['continuum'],'status':record['status'],'policySlots':15,'robustPeriodRows':20,'unresolved':True}
    enforcement = record['nominalEnforcement']
    for key,value in [('scenario',scenario),('physicalCap',old_recurring['physicalCap']),('normalizedCapExact',old_recurring['normalizedCapExact']),('conditions',old_recurring['conditions']),('rounding',old_continuous['rounding']),('qstar',old_recurring['inheritedContinuum']['qstar']),('rho',old_recurring['inheritedContinuum']['rho']),('aJ',old_recurring['aJ']),('nominalK',old_continuous['k'])]:
        require(enforcement[key] == value,'Frozen nominal enforcement/orbit identity '+key)
    model = backend.AuditEconomy(guard,record['continuum'])
    enclosed(enforcement['unchangedMassScale'],model.scale,'Unchanged actual buyers times taste scale')
    prices = [backend.enclosure(s['executedNormalizedPrice']) for s in old_recurring['orbit']]
    curve = IndependentDemandCurve(model,prices,backend.enclosure(old_recurring['aJ']),backend.enclosure(enforcement['qstar']),backend.enclosure(enforcement['rho']))
    old_by_label = {r['label']:r for r in old_targets}
    selected = {r['label']:r for r in old_recurring['comparisons']}
    targets = [check_target(t,old_by_label[t['label']],selected[t['label']],curve) for t in record['targets']]
    require(record['d0AllClosedSelectionsReproduced'] is True and all(t['zeroReproduces'] for t in targets),'Every completed model reproduces old zero-shift selection')
    radius_counts,period_counts = {},{}
    for target in targets:
        for name,count in target['radiusStatuses'].items():
            radius_counts[name] = radius_counts.get(name,0)+count
        for name in target['robustPeriodStatuses']:
            period_counts[name] = period_counts.get(name,0)+1
    return {'scenario':record['scenario'],'continuum':record['continuum'],'status':record['status'],'policySlots':15,'robustPeriodRows':20,'unresolved':False,'radiusStatuses':radius_counts,'robustPeriodStatuses':period_counts,'zeroReproductions':5}


def check_inherited_hashes():
    for folder,auditor in [('recurring-results','audit-sparse-reset.py'),('continuous-results','audit-continuous-study.py'),('handover-init-results','audit-handover-init.js')]:
        directory = ROOT/'research'/folder
        manifest,audit = read(directory/'manifest.json'),read(directory/'independent-audit.json')
        require(audit['passed'] and audit['studyManifestHash'] == digest(directory/'manifest.json'),'Closed audit/manifest link '+folder)
        require(audit['auditorSourceHash'] == digest(ROOT/'research'/auditor),'Closed independent auditor source '+folder)
        if 'resultsSha256' in audit:
            require(audit['resultsSha256'] == digest(directory/'results.json'),'Closed audit/results link '+folder)
        for field in ['sourceHashes','inputHashes']:
            for name,sha in manifest[field].items():
                require(digest(ROOT/name) == sha,'Closed source/input '+name)


def audit(directory=None):
    global checks
    checks = 0
    directory = Path(directory or ROOT/'research/misspec-results')
    manifest,results,completion = (read(directory/name) for name in ['manifest.json','results.json','completion.json'])
    for field in ['sourceHashes','inputHashes']:
        for name,sha in manifest[field].items():
            require(digest(ROOT/name) == sha,'New frozen dependency '+name)
            if field == 'sourceHashes':
                require(digest(directory/'sources'/name) == sha,'New frozen source snapshot '+name)
    check_inherited_hashes()
    require(results['manifestSha256'] == digest(directory/'manifest.json'),'Alternative-demand result/manifest identity')
    plan = manifest['plan']
    require(plan['records'] == 16 and plan['radiusPolicySlots'] == 240 and plan['robustPeriodRows'] == 320,'Prospective model/policy/period inventory')
    require(plan['continuums'] == ['effective','nominal'] and plan['targetLabels'] == backend.LABELS and plan['policySlots'] == ['guard-only','closed-selected','permanent-cap'],'Prospective semantic/target/policy families')
    require(Decimal(plan['maximumDisplacementExact']) == 8 and plan['maximumPeriod'] == 65536 and Decimal(plan['requiredRadiusWidth']) == Decimal('1e-20') and Decimal(plan['stationarySignPaddingExact']) == Decimal('1e-24'),'Prospective numerical gates')
    require(len(plan['uncertaintyBounds']) == 4,'Four declared uncertainty bounds')
    for level,saved in zip(LEVELS,plan['uncertaintyBounds']):
        check_level(saved,level)
    old_targets = read(ROOT/'research/handover-init-results/results.json')['records']
    old_cont = read(ROOT/'research/continuous-results/results.json')['records']
    old_rec = read(ROOT/'research/recurring-results/results.json')['records']
    records = results['records']
    require(len(records) == 16 and len({(r['scenario'],r['continuum']) for r in records}) == 16,'All sixteen model records once')
    details,fixture = [],None
    for scenario in plan['scenarios']:
        sid = scenario['id']
        guard = read(ROOT/f'research/cycle-results/cases/{sid}-guard.json')
        original = next(r['results'] for r in old_targets if r['scenario'] == scenario)
        for kind in ['effective','nominal']:
            record = next(r for r in records if r['scenario'] == sid and r['continuum'] == kind)
            require(read(directory/'records'/f'{sid}-{kind}.json') == record,'Alternative-demand per-model journal matches result')
            old = next(r for r in old_rec if r['scenario'] == sid and r['continuum'] == kind)
            continuous = next(r for r in old_cont if r['scenario'] == sid and r['continuum'] == kind)
            arguments = scenario,guard,old,continuous,original
            details.append(check_record(record,*arguments))
            if fixture is None and record['status'] == 'completed alternative-demand comparisons':
                fixture = record,arguments
    journal = [json.loads(line) for line in (directory/'journal.jsonl').read_text(encoding='utf-8').splitlines() if line]
    for record in records:
        entries = [e for e in journal if e['scenario'] == record['scenario'] and e['continuum'] == record['continuum']]
        require([e['status'] for e in entries] == ['started',record['status']],'Started and retained final model journal receipts')
    unresolved = sum(d['unresolved'] for d in details)
    require(completion['records'] == 16 and completion['policySlots'] == 240 and completion['robustPeriodRows'] == 320 and completion['unresolvedModels'] == unresolved,'Completion retained-label/status inventory')
    require(completion['resultsSha256'] == digest(directory/'results.json') and completion['finalFrozenDependencyCheck']['passed'],'Final alternative-demand output/dependency check')
    require(completion['resources']['apiCalls'] == completion['resources']['newTrainingRounds'] == 0,'No seller model calls or training')
    require(fixture is not None,'Actual completed fixture for corruption controls')
    def wrong_selection(r):
        row = next(t for t in r['targets'] if t['robustPeriods'][0]['status'] == 'largest certified fixed period')
        row['robustPeriods'][0]['largestPeriod'] += 1
    def wrong_radius(r):
        row = next(p for t in r['targets'] for p in t['policies'] if p['radius']['status'] == 'certified crossing enclosure')
        row['radius']['radiusEnclosure']['upper'] = '8'
    mutations = {
        'enforcementModel':lambda r:r['nominalEnforcement']['nominalK'].update(lower='1',upper='1'),
        'shiftUnits':lambda r:r['targets'][0]['policies'][0]['sensitivity'][1]['dbar'].update(exactDecimal='0.01'),
        'targetScaling':lambda r:r['targets'][0].update(actualThresholdExact='1'),
        'radiusBracket':wrong_radius,'periodFrequencyClaim':wrong_selection}
    controls = {}
    for name,mutate in mutations.items():
        changed = copy.deepcopy(fixture[0]);mutate(changed)
        rejected = False
        try:
            check_record(changed,*fixture[1])
        except (ValueError,KeyError):
            rejected = True
        require(rejected,'Rejected actual-evidence '+name+' corruption')
        controls[name] = True
    radii,periods = {},{}
    for detail in details:
        for name,count in detail.get('radiusStatuses',{}).items():
            radii[name] = radii.get(name,0)+count
        for name,count in detail.get('robustPeriodStatuses',{}).items():
            periods[name] = periods.get(name,0)+count
    policies = [p for r in records for t in r['targets'] for p in t['policies']]
    available = sum(p.get('available',False) for p in policies)
    return {'passed':True,'completedAt':datetime.now(timezone.utc).isoformat(),'studyManifestHash':digest(directory/'manifest.json'),'resultsSha256':digest(directory/'results.json'),'auditorSourceHash':digest(Path(__file__)),'arithmeticBackendHash':digest(ROOT/'research/audit-continuous-study.py'),'checks':checks,'records':16,'targetLabels':80,'policySlots':240,'robustPeriodRows':320,'unresolvedModels':unresolved,'availablePolicySlots':available,'unavailablePolicySlots':240-available,'reserveLevelRows':sum(len(p['sensitivity']) for p in policies),'duplicatePolicySlots':sum(p.get('duplicateOf') is not None for p in policies),'unresolvedRadiusRows':sum(count for status,count in radii.items() if status.startswith('unresolved')),'radiusStatuses':radii,'robustPeriodStatuses':periods,'corruptionNegativeControls':controls,'details':details,'scope':'Independent alternative-demand algebra, signed robustness radii/stationary closed forms, fixed nominal enforcement and original absolute thresholds, all reserve assumptions and robust-period boundaries. Hash-bound certified old price enclosures reused; separate130-digit calculation logic with shared standard Decimal backend, not formal verification or empirical misspecification validation.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory',type=Path)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = audit(args.directory)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
