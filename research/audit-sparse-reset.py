"""Independent recurring-controller audit; imports no primary controller code.

The frozen independent 130-digit model/arithmetic backend is reused explicitly.
It shares Python Decimal with the primary implementation, not controller logic.
Saved finite numerical-game weights additionally admit exact Fraction checks.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import importlib.util, json, hashlib, argparse, copy, math
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('frozen_independent_continuum', ROOT/'research/audit-continuous-study.py')
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)
B, LOW, HIGH = backend.Box, backend.LOW, backend.HIGH
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
    result = B(saved['lower'], saved['upper'])
    require(result.low <= actual.low and result.high >= actual.high, label+' independently enclosed')
    if 'width' in saved:
        require(Fraction(Decimal(saved['width'])) >= Fraction(result.high)-Fraction(result.low), label+' honest width')
    return result


def power(value, exponent):
    require(isinstance(exponent, int) and exponent >= 0 and value.low >= 0, 'Nonnegative integer power')
    result = B(1)
    for _ in range(exponent.bit_length()):
        if exponent & 1:
            result = result*value
        value = value*value
        exponent >>= 1
    return result


def profit(model, x, y):
    return x/(1+(model.k+(-y).exp())*x.exp())


def check_scalar_upper(model, record, rival):
    """Certify saved brackets by independent endpoint signs; no primary solver."""
    require(Fraction(Decimal(record['rivalExact'])) == Fraction(rival), 'Exact rival endpoint identity')
    y = B(rival)
    w = B(record['bestProfitW']['lower'], record['bestProfitW']['upper'])
    require(w.low > 0, 'Positive saved best-profit bracket')
    log_z = -(B(1)+(model.k+(-y).exp()).log())
    residual = lambda x: B(x)+B(x).log()-log_z
    require(residual(w.low).sign == -1 and residual(w.high).sign == 1,
            'Independent log-W signs certify entire saved best-profit bracket')
    enclosed(record['bestResponse'], 1+w, 'Best response')
    target = w-model.t
    enclosed(record['normalizedTargetProfit'], target, 'Best-profit tolerance target')
    require(target.low > 0, 'Positive target profit')
    root = B(record['normalizedPrice']['lower'], record['normalizedPrice']['upper'])
    require(root.high-root.low <= Decimal('1e-25'), 'Declared scalar root width')
    require(root.low > 1+w.high and root.high <= B.rational(model.high).high,
            'Upper branch and domain')
    f = lambda x: target-profit(model, B(x), y)
    kind = record['proof']['kind']
    if kind == 'interior upper root':
        require(f(root.low).sign == -1 and f(root.high).sign == 1,
                'Independent scalar upper-root endpoint signs')
    elif kind == 'ceiling-clipped':
        require(Fraction(root.low) == model.high == Fraction(root.high), 'Exact clipped ceiling')
        require(f(root.high).sign == -1, 'Independent clipping residual')
    else:
        raise ValueError('Unrecognized upper-root certificate kind')
    return root


def exact_finite_prefix(prices, upper, cap_index, rewards, period):
    """No primary Fraction or cycle code: saved doubles become exact rationals."""
    require(1 <= period <= 65536 and isinstance(period, int), 'Finite period range')
    n = len(prices)
    require(len(upper) == n and all(isinstance(x, int) and 0 <= x < n for x in upper), 'Finite map domain')
    require(all(upper[i] <= upper[i+1] for i in range(n-1)), 'Finite upper map monotone')
    require(0 <= cap_index < n and len(rewards) == n*n, 'Finite cap/reward dimensions')
    at, total, floor, horizon = cap_index, Fraction(0), None, None
    indices, terms = [], []
    for j in range(period):
        indices.append(at)
        term = Fraction(float(rewards[at*n+at]))
        terms.append(term)
        total += term
        prefix = total/(j+1)
        if floor is None or prefix < floor:
            floor, horizon = prefix, j+1
        at = upper[at]
    return {'indices': indices, 'average': total/period, 'floor': floor,
            'horizon': horizon, 'descending': all(a >= b for a,b in zip(terms, terms[1:]))}


def check_finite_certificate(game, certificate):
    computed = exact_finite_prefix(game['prices'],game['upper'],game['capIndex'],
                                   game['rewards']['consumerSurplus'],certificate['period'])
    require(certificate['cycleIndices'] == computed['indices'], 'Exact finite top-choice cycle')
    for label,field in [('cycleAverage','average'),('activationFloor','floor')]:
        saved = certificate[label+'Exact']
        actual = Fraction(int(saved['numerator']),int(saved['denominator']))
        require(actual == computed[field], 'Fraction-independent '+label+' certificate')
        lower = float(certificate[label+'Lower'])
        require(Fraction(lower) <= actual < Fraction(math.nextafter(lower,math.inf)),
                'Greatest outward binary64 lower display of '+label)
    require(certificate['minimizingPrefix'] == computed['horizon'], 'Exact minimizing prefix horizon')
    require(certificate['descending'] == computed['descending'] and certificate['capFirst'] is True,
            'Finite descending and actual first-cap flags')
    return computed


def audit_finite(directory=None):
    global checks
    checks = 0
    directory = Path(directory or ROOT/'research/sparse-display-results')
    manifest,index,completion = (read(directory/name) for name in ['manifest.json','index.json','completion.json'])
    for field in ['sourceHashes','inputHashes']:
        for name,sha in manifest[field].items():
            require(digest(ROOT/name) == sha,'Frozen finite dependency '+name)
    require(index['manifestSha256'] == digest(directory/'manifest.json'),'Finite index/manifest binding')
    require(len(index['cases']) == 8 and all(r['status'] == 'completed' for r in index['cases']), 'All eight finite cases retained')
    require(manifest['plan']['periods'] == [1,2,4,8,16,32,64,128],'Declared finite periods')
    fixture = None
    counts = 0
    for row in index['cases']:
        path = directory/row['file']
        require(digest(path) == row['sha256'],'Finite case/index binding')
        record = read(path)
        game = record['finite']
        require(record['scenario']['id'] == row['scenario'],'Finite scenario identity')
        require([c['period'] for c in game['certificates']] == [1,2,4,8,16,32,64,128],'Every finite certificate retained')
        for certificate in game['certificates']:
            check_finite_certificate(game,certificate)
            counts += 1
        if fixture is None:
            fixture = game
    require(completion['passed'] and completion['cases'] == 8 and completion['failures'] == 0 and completion['finalHashCheck'], 'Finite completion integrity')
    mutations = {'prefixFloor':lambda c:c['activationFloorExact'].update(numerator='0'),
                 'cycleIndex':lambda c:c['cycleIndices'].__setitem__(0,(c['cycleIndices'][0]+1)%len(fixture['prices'])),
                 'prefixHorizon':lambda c:c.update(minimizingPrefix=c['minimizingPrefix']+1)}
    controls = {}
    for name,mutate in mutations.items():
        certificate = copy.deepcopy(fixture['certificates'][1])
        mutate(certificate)
        rejected = False
        try:
            check_finite_certificate(fixture,certificate)
        except ValueError:
            rejected = True
        require(rejected,'Rejected finite rational corruption '+name)
        controls[name] = True
    return {'passed':True,'completedAt':datetime.now(timezone.utc).isoformat(),
            'studyManifestHash':digest(directory/'manifest.json'),'indexSha256':digest(directory/'index.json'),
            'auditorSourceHash':digest(Path(__file__)),'checks':checks,'cases':8,'certificates':counts,
            'corruptionNegativeControls':controls,
            'scope':'Independent exact Fraction verification of saved binary64 reward cycle means and tight finite activation-prefix floors. The separate Node audit verifies economic tables, JS masks, cap identities and execution phases. This is a saved numerical-game certificate, not exact-real logit arithmetic.'}


def check_orbit(record, model, inherited, physical_cap):
    cap = (Fraction(float(physical_cap))-model.values['cost'])/model.values['mu']
    require(Fraction(Decimal(record['normalizedCapExact'])) == cap, 'Exact inherited normalized cap')
    current = B.rational(cap)
    qstar = backend.enclosure(inherited['worst']['normalizedPrice'])
    require(model.ell <= cap and current.high < qstar.low, 'Inherited cap premise')
    require(record['conditions'] == {'ellAtMostCap': True, 'capStrictlyBelowQStar': True}, 'Premise flags')
    require(record['prefixTerms'] == 64 and len(record['orbit']) == 64, 'All 64 declared orbit terms')
    rewards, profits = [], []
    for j, step in enumerate(record['orbit']):
        require(step['j'] == j, 'Orbit index')
        enclosed(step['executedNormalizedPrice'], current, 'Executed orbit price')
        enclosed(step['executedPrice'], model.cost+model.mu*current, 'Physical executed price')
        reward = model.diagonal_cs(current)
        own_profit = model.scale*model.diagonal_profit(current)
        enclosed(step['consumerSurplus'], reward, 'Orbit surplus')
        enclosed(step['profitPerSellerOnWorstCSPath'], own_profit, 'Orbit descriptive seller profit')
        proof = step['upperMapProof']
        left = check_scalar_upper(model, proof['lowerEndpoint'], current.low)
        right = check_scalar_upper(model, proof['upperEndpoint'], current.high)
        following = B(left.low, right.high)
        enclosed(step['nextNormalizedPrice'], following, 'Endpoint propagation')
        require(following.high >= current.low, 'Nondecreasing orbit compatible with intervals')
        if j == 0:
            require(following.low > current.high, 'Strict first upward step')
        rewards.append(reward)
        profits.append(own_profit)
        current = following
    enclosed(record['aJ'], current, 'Retained a64')
    gap = qstar-current
    require(gap.high >= 0, 'Orbit/fixed-point interval consistency')
    distance = B(max(Decimal(0), gap.low), gap.high)
    enclosed(record['qStarMinusAJ'], distance, 'Conservative distance after prefix')
    return {'rewards': rewards, 'profits': profits, 'lastPrice': current, 'qstar': qstar,
            'distance': distance, 'cstar': backend.enclosure(inherited['worst']['consumerSurplus']),
            'rho': backend.enclosure(inherited['assumptions']['rho']), 'model': model}


def check_period(record, orbit):
    k = record['period']
    require(isinstance(k, int) and 1 <= k <= 65536, 'No period outside frozen ceiling')
    j = len(orbit['rewards'])
    total = sum(orbit['rewards'][:min(k,j)], B(0))
    own = sum(orbit['profits'][:min(k,j)], B(0))
    if k <= j:
        last = orbit['rewards'][k-1]
        require(record['tail'] is None, 'No invented analytic tail for stored terms')
    else:
        count = k-j
        rho = B(orbit['rho'].high)
        geometric = (1-power(rho,count))/(1-rho)
        excess = orbit['model'].scale*orbit['distance']*geometric
        total += count*orbit['cstar']+B(0,excess.high)
        tail_profit = orbit['model'].scale*profit(orbit['model'],
            B(orbit['lastPrice'].low,orbit['qstar'].high), B(orbit['lastPrice'].low,orbit['qstar'].high))
        own += count*tail_profit
        last_excess = orbit['model'].scale*orbit['distance']*power(rho,k-1-j)
        last = orbit['cstar']+B(0,last_excess.high)
        tail = record['tail']
        require(tail['termsAfterPrefix'] == count, 'Exact analytic-tail length')
        enclosed(tail['constantFloor'], orbit['cstar'], 'Tail constant floor')
        enclosed(tail['geometricSum'], geometric, 'Geometric tail multiplier')
        require(Decimal(tail['excessSumUpper']) >= excess.high, 'Outward tail excess sum')
        require(Decimal(tail['lastRoundExcessUpper']) >= last_excess.high, 'Outward last-round tail excess')
        enclosed(tail['pathProfitTailPerSeller'], tail_profit, 'Descriptive profit tail enclosure')
    average = enclosed(record['averageConsumerSurplus'], total/k, 'Independent period average')
    enclosed(record['cycleSumConsumerSurplus'], total, 'Independent period sum')
    enclosed(record['lastRoundConsumerSurplus'], last, 'Individual last-round bound')
    enclosed(record['profitAOnWorstCSPath'], own/k, 'A descriptive path profit')
    enclosed(record['profitBOnWorstCSPath'], own/k, 'B descriptive path profit')
    enclosed(record['jointProfitOnWorstCSPath'], 2*own/k, 'Joint descriptive path profit')
    enclosed(record['capRuleActivationFrequency'], B(1)/k, 'Rule activation frequency')
    require(record['startupCapCount'] == 1, 'Actual first cap counted')
    require(Decimal(record['finiteActivationAverageLowerBound']) == average.low, 'Finite-average floor uses outward lower endpoint')
    return average


def check_target(row, original, periods, cstar):
    require(row['label'] == original['label'], 'Preserved target label/order')
    backend.validate_import(row['requestedImported'], original['requestedTarget'], 'Sparse requested target')
    backend.validate_import(row['actualThresholdImported'], original['actualGuaranteedThreshold'], 'Sparse actual threshold')
    f = Decimal.from_float(float(original['actualGuaranteedThreshold']))
    require(Decimal(row['actualThresholdExact']) == f and row['searchCeiling'] == 65536, 'Fixed exact threshold and ceiling')
    status = row['status']
    def reported(name):
        value = row[name]
        require(value == periods[value['period']]['record'], 'Embedded '+name+' matches independently checked period')
        return periods[value['period']]['average']
    if status == 'no recurring cap needed for the long-run target':
        require(cstar.low >= f, 'No-recurring-cap target already below guard floor')
        a,b = row['withoutIntervention'],row['oneImmediateCapThenOriginalGuard']
        require(a['recurringFrequency'] == b['recurringFrequency'] == 0 and a['startupCaps'] == 0 and b['startupCaps'] == 1, 'Distinct zero-frequency startup counts')
        require(a['finiteActivationAverageGuaranteedFromArbitraryOldPrices'] is False, 'No arbitrary-prefix claim for untouched guard')
        enclosed(a['longRunFloor'],cstar,'Untouched guard long-run floor')
        enclosed(b['finiteActivationAverageFloor'],cstar,'One-cap finite activation floor')
    elif status == 'infeasible for this fixed-cap family':
        require(row['strongestPeriod']['period'] == 1 and reported('strongestPeriod').high < f, 'Family infeasibility at strongest period one')
    elif status == 'unresolved period-one boundary':
        first = reported('strongestPeriod')
        require(first.low < f <= first.high and row['strongestPeriod']['period'] == 1, 'Honest unresolved period-one overlap')
    elif status in ['largest certified fixed period','certified integer bracket']:
        low,high = row['certifiedSafePeriodLowerBound'],row['certifiedFailingPeriodUpperBound']
        require(1 <= low < high <= 65536, 'Certified period bracket in range')
        require(row['safePeriod']['period'] == low and row['nextFailingPeriod']['period'] == high, 'Boundary period identities')
        require(reported('safePeriod').low >= f and reported('nextFailingPeriod').high < f, 'Independent safe and failing boundary inequalities')
        require(row['possibleLargestPeriodBracket'] == [low,high-1], 'Conservative largest-period bracket')
        if status == 'largest certified fixed period':
            require(high == low+1 and row['largestPeriod'] == low, 'Adjacent boundaries establish family maximality')
        else:
            require(high > low+1 and row['largestPeriod'] is None, 'Overlap not silently promoted to maximum')
    elif status in ['censored safe lower bound','unresolved censored bracket']:
        low = row['certifiedSafePeriodLowerBound']
        require(reported('safePeriod').low >= f and row['safePeriod']['period'] == low, 'Censored certified safe period')
        require(row['certifiedFailingPeriodUpperBound'] is None and row['ceilingPeriod']['period'] == 65536, 'No fabricated failing point beyond ceiling')
        reported('ceilingPeriod')
        require((low == 65536) == (status == 'censored safe lower bound'), 'Censoring status matches certified lower bound')
    else:
        raise ValueError('Unknown sparse target classification')
    require(all(2 <= k <= 65536 and k & (k-1) == 0 for k in row.get('doublingPeriods',[])), 'Declared doubling periods only')


def check_record(record, guard, cap, raw, inherited):
    sid = guard['scenario']['id']
    require(record['scenario'] == sid == inherited['scenario'] and record['continuum'] == inherited['continuum'], 'Model/scenario identity')
    require(cap['scenario'] == raw['scenario'] == guard['scenario'], 'Independent inherited economic identity')
    require(cap['controller'] == 'cap' and cap['game']['prices'] == guard['game']['prices'], 'Independent inherited cap game identity')
    support = cap['game']['sets'][0]
    require(support == list(range(len(support))) and len(support)>0 and all(s == support for s in cap['game']['sets']), 'All previous states share exact cap prefix')
    index = support[-1]
    physical = guard['game']['prices'][index]
    require(all(r['existingCompetitiveCap']['index'] == index and r['existingCompetitiveCap']['price'] == physical and r['existingCompetitiveCap']['allowedInitialPricesPerSeller'] == index+1 for r in raw['results']), 'Both inherited cap sources agree')
    require([r['label'] for r in raw['results']] == backend.LABELS, 'All five inherited labels in order')
    require(len(record['comparisons']) == 5, 'All target labels retained')
    if record['status'] != 'certified recurring-cap enclosures':
        require(record['status'] == 'unresolved calculation or condition' and bool(record['failure']), 'Retained unresolved failure')
        require(all(r['classification'] == 'unresolved' for r in record['comparisons']), 'No unsupported classification after failure')
        return {'scenario':sid,'continuum':record['continuum'],'status':record['status']}
    physical_record = record['physicalCap']
    require(physical_record['oldIndex'] == index and physical_record['oldGridSize'] == len(guard['game']['prices']), 'Reported inherited cap index/grid')
    backend.validate_import(physical_record['physicalPriceImported'],physical,'Fixed physical cap import')
    backend.validate_import(physical_record['lowerPriceImported'],guard['game']['prices'][0],'Cap lower-price import')
    require(physical_record['sourceGuardCase'] == guard['id'] and physical_record['sourceCapCase'] == cap['id'] and physical_record['rawInitializerLabelsChecked'] == 5, 'Physical cap provenance labels')
    require(record['importedBinary64'] == inherited['importedBinary64'], 'Exact economic input imports unchanged')
    expected_inherited = {'qstar':inherited['worst']['normalizedPrice'], 'consumerSurplus':inherited['worst']['consumerSurplus'], 'rho':inherited['assumptions']['rho'], 'nash':inherited['nash'], 'rounding':inherited['rounding']}
    require(record['inheritedContinuum'] == expected_inherited, 'Inherited continuum certificate copied without drift')
    model = backend.AuditEconomy(guard,record['continuum'])
    orbit = check_orbit(record,model,inherited,physical)
    values = record['periodEvaluations']
    require([r['period'] for r in values] == sorted(set(r['period'] for r in values)), 'Unique sorted saved period evaluations')
    periods = {r['period']:{'record':r,'average':check_period(r,orbit)} for r in values}
    require([r['period'] for r in record['frontier']] == [1,2,4,8,16,32,64,128], 'Entire fixed prospective period frontier')
    require(all(r == periods[r['period']]['record'] for r in record['frontier']), 'Frontier references verified period records')
    for row,original in zip(record['comparisons'],raw['results']):
        check_target(row,original,periods,orbit['cstar'])
    return {'scenario':sid,'continuum':record['continuum'],'status':record['status'],
            'scalarRootCertificates':128,'periodsChecked':len(periods),
            'classifications':[{'label':r['label'],'status':r['status'],'largestPeriod':r.get('largestPeriod')} for r in record['comparisons']]}


def audit(directory=None):
    global checks
    checks = 0
    directory = Path(directory or ROOT/'research/recurring-results')
    manifest,results,completion = (read(directory/name) for name in ['manifest.json','results.json','completion.json'])
    for field in ['sourceHashes','inputHashes']:
        for name,sha in manifest[field].items():
            require(digest(ROOT/name) == sha,'Frozen recurring dependency '+name)
            if field == 'sourceHashes':
                require(digest(directory/'sources'/name) == sha,'Frozen source snapshot '+name)
    # Re-run the closed independent audit read-only, including all global
    # assumptions and fixed-point signs. This never imports primary functions.
    old = backend.audit(ROOT/'research/continuous-results')
    require(old['passed'],'Inherited continuous evidence reverified independently')
    require(results['manifestSha256'] == digest(directory/'manifest.json'),'Results frozen-manifest binding')
    plan = manifest['plan']
    require(plan['records'] == 16 and plan['targetLabelsAcrossModels'] == 80 and plan['prefixTerms'] == 64 and plan['maximumSearchPeriod'] == 65536,'Prospective inventory')
    require(plan['continuums'] == ['effective','nominal'] and plan['fixedPeriodFrontier'] == [1,2,4,8,16,32,64,128],'Prospective model kinds/frontier')
    raw = read(ROOT/'research/handover-init-results/results.json')['records']
    inherited = read(ROOT/'research/continuous-results/results.json')['records']
    records = results['records']
    require(len(records) == 16 and len({(r['scenario'],r['continuum']) for r in records}) == 16,'All sixteen distinct model records')
    details,fixture = [],None
    for scenario in plan['scenarios']:
        sid = scenario['id']
        guard = read(ROOT/f'research/cycle-results/cases/{sid}-guard.json')
        cap = read(ROOT/f'research/cycle-results/cases/{sid}-cap.json')
        require(scenario == guard['scenario'],'Frozen scenario economic identity')
        target = next(r for r in raw if r['scenario']['id'] == sid)
        for kind in ['effective','nominal']:
            record = next(r for r in records if r['scenario'] == sid and r['continuum'] == kind)
            old_record = next(r for r in inherited if r['scenario'] == sid and r['continuum'] == kind)
            require(read(directory/'records'/f'{sid}-{kind}.json') == record,'Per-record journal matches final results')
            details.append(check_record(record,guard,cap,target,old_record))
            if fixture is None and record['status'] == 'certified recurring-cap enclosures':
                fixture = (record,guard,cap,target,old_record)
    require(completion['records'] == 16 and completion['resolved']+completion['unresolved'] == 16 and completion['targetLabels'] == 80,'Completion case/label inventory')
    require(completion['resolved'] == sum(r['status'] == 'certified recurring-cap enclosures' for r in records),'Completion actual resolved count')
    require(completion['resultsSha256'] == digest(directory/'results.json') and completion['finalFrozenDependencyCheck']['passed'],'Completion output/dependency integrity')
    require(completion['resources']['trainingRounds'] == completion['resources']['apiCalls'] == 0,'No experimental model calls/training')
    require(fixture is not None,'Actual resolved fixture for independent corruptions')
    controls = {}
    def inflate_claimed_maximum(r):
        row = next(x for x in r['comparisons'] if x['status'] == 'largest certified fixed period')
        row['largestPeriod'] += 1
    def inflate_prefix_floor(r):
        r['periodEvaluations'][0]['finiteActivationAverageLowerBound'] = '1000000'
        r['frontier'][0]['finiteActivationAverageLowerBound'] = '1000000'
    mutations = {
        'capIdentity':lambda r:r['physicalCap'].update(oldIndex=r['physicalCap']['oldIndex']+1),
        'orbitTerm':lambda r:r['orbit'][0]['consumerSurplus'].update(lower='0',upper='0'),
        'rewardTiming':lambda r:r['orbit'][0].update(j=1),
        'periodBoundary':inflate_claimed_maximum,
        'prefixCertificate':inflate_prefix_floor}
    for name,mutate in mutations.items():
        changed = copy.deepcopy(fixture[0]);mutate(changed)
        rejected = False
        try:
            check_record(changed,*fixture[1:])
        except (ValueError,KeyError):
            rejected = True
        require(rejected,'Rejected deliberate '+name+' corruption')
        controls[name] = rejected
    return {'passed':True,'completedAt':datetime.now(timezone.utc).isoformat(),
            'studyManifestHash':digest(directory/'manifest.json'),'resultsSha256':digest(directory/'results.json'),
            'auditorSourceHash':digest(Path(__file__)),'arithmeticBackendHash':digest(ROOT/'research/audit-continuous-study.py'),
            'checks':checks,'records':16,'targetLabels':80,'scalarRootCertificates':sum(r.get('scalarRootCertificates',0) for r in details),
            'inheritedContinuousAuditChecks':old['checks'],'corruptionNegativeControls':controls,'details':details,
            'scope':'Independent controller logic and signed scalar endpoint certificates, propagated orbit/rewards, analytic tails, fixed-target maximality/censoring and phase-zero semantics. Reuses frozen independent 130-digit model/arithmetic functions; shared standard Decimal backend, not formal verification or arithmetic-library independence.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--finite',action='store_true')
    args = parser.parse_args()
    result = audit_finite(args.directory) if args.finite else audit(args.directory)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
