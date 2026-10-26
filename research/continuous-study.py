"""Prospective validated continuum study. Real inputs execute only after freeze.

CLI: freeze (after independent GO), run, verify. Synthetic unit tests may call
the arithmetic/model functions without generating any scientific case results.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import argparse
import ctypes
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone

sys.dont_write_bytecode = True
from continuous_interval import (Interval as I, Unresolved, PRECISION,
    decimal, fraction_decimal, exact_binary64, bisect_increasing,
    lambert_w_positive, classify_floor)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'research/continuous-results'
SOURCES = ['research/continuous-study.py', 'research/continuous_interval.py',
           'tests/test_continuous_interval.py',
           'research/CONTINUOUS_NUMERIC_ADDENDUM.md',
           'research/CONTINUOUS_REFINEMENT_PROTOCOL.md',
           'research/CONTINUOUS_REFINEMENT_THEORY.md']
ALLOWANCE = 1e-12
ROOT_TOLERANCE = '1e-28'
TARGET_LABELS = ['cap-90pct', 'cap-95pct', 'cap-99pct', 'cap-100pct', 'near-Nash-anchor-floor']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(value, separators=(',', ':'), ensure_ascii=False) + '\n')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def rss_bytes():
    """Current resident bytes, sampled after records; not continuous peak RSS."""
    if os.name == 'nt':
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD),
                        ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
                        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t), ('QuotaPagedPoolUsage', ctypes.c_size_t),
                        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t), ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                        ('PagefileUsage', ctypes.c_size_t), ('PeakPagefileUsage', ctypes.c_size_t)]
        c = Counters(); c.cb = ctypes.sizeof(c)
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        fn = ctypes.WinDLL('psapi', use_last_error=True).GetProcessMemoryInfo
        fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        if not fn(kernel.GetCurrentProcess(), ctypes.byref(c), c.cb):
            raise OSError(ctypes.get_last_error(), 'GetProcessMemoryInfo')
        return c.WorkingSetSize
    statm = Path('/proc/self/statm')
    if statm.exists():
        return int(statm.read_text().split()[1]) * os.sysconf('SC_PAGE_SIZE')
    return None


def exact(value):
    return Fraction(float(value))


class Model:
    def __init__(self, economy, lower_price, upper_price, epsilon, effective=False):
        self.imported = {key: exact_binary64(value) for key, value in economy.items()
                         if key != 'id'}
        self.imported.update({'lowerPrice': exact_binary64(lower_price),
                              'upperPrice': exact_binary64(upper_price),
                              'epsilon': exact_binary64(epsilon),
                              'comparisonAllowance': exact_binary64(ALLOWANCE)})
        required = {'quality', 'cost', 'mu', 'buyers', 'outsideQuality'}
        if not required <= set(economy):
            raise ValueError('Economic parameter missing')
        f = {key: exact(economy[key]) for key in required}
        if f['mu'] <= 0 or f['buyers'] <= 0:
            raise ValueError('Scale and buyer mass must be positive')
        self.c = I(fraction_decimal(f['cost']))
        self.mu = I(fraction_decimal(f['mu']))
        self.mass_scale = I(fraction_decimal(f['buyers'] * f['mu']))
        self.ell = fraction_decimal((exact(lower_price) - f['cost']) / f['mu'])
        self.high = fraction_decimal((exact(upper_price) - f['cost']) / f['mu'])
        if self.ell >= self.high:
            raise ValueError('Ordered continuous domain required')
        tolerance = exact(epsilon) + (exact(ALLOWANCE) if effective else 0)
        if tolerance <= 0:
            raise ValueError('Positive payoff tolerance required')
        self.t = I(fraction_decimal(tolerance / (f['buyers'] * f['mu'])))
        self.k = I(fraction_decimal((f['cost'] - f['quality'] + f['outsideQuality']) / f['mu'])).exp()
        self.rounding = {'kind': 'effective' if effective else 'nominal',
                         'epsilonExact': str(decimal(float(epsilon))),
                         'allowanceExact': str(decimal(ALLOWANCE)),
                         'effectiveToleranceExactRealSum': str(fraction_decimal(exact(epsilon) + exact(ALLOWANCE))),
                         'effectiveToleranceJavaScriptRoundedBinary64': exact_binary64(float(epsilon) + ALLOWANCE),
                         'appliedPayoffToleranceExact': str(fraction_decimal(tolerance)),
                         'normalizedToleranceExact': str(self.t.lo)}

    def w(self, y):
        y = I.cast(y)
        z = 1 / (I(1).exp() * (self.k + (-y).exp()))
        return lambert_w_positive(z)[0]

    def profit(self, x, y):
        x, y = I.cast(x), I.cast(y)
        return x / (1 + (self.k + (-y).exp()) * x.exp())

    def surplus(self, x, y):
        x, y = I.cast(x), I.cast(y)
        return self.mass_scale * (1 + ((-x).exp() + (-y).exp()) / self.k).ln()

    def original_price(self, x):
        return self.c + self.mu * x


def certify_assumptions(model):
    m = model.w(I(model.ell))
    w_high = model.w(I(model.high))
    b_low, b_high = 1 + m, 1 + w_high
    w_bar = lambert_w_positive(1 / (I(1).exp() * model.k))[0]
    rho = w_bar / (1 + w_bar)
    first = m * m / (2 * (1 + m))
    second = m * m * m * (1 + m) / 2
    tests = {
        'lowerBestResponseStrictlyInterior': b_low.lo > model.ell,
        'upperBestResponseStrictlyInterior': b_high.hi < model.high,
        'positiveTolerance': model.t.lo > 0,
        'positiveProfitThreshold': model.t.hi < m.lo,
        'smallToleranceFirstBound': model.t.hi < first.lo,
        'smallToleranceSecondBound': model.t.hi < second.lo,
        'contractionUpperBelowOne': rho.hi < 1,
    }
    return {'eligible': all(tests.values()), 'certifiedChecks': tests,
            'minimumW': m.json(), 'lowerEndpointBestResponse': b_low.json(),
            'upperEndpointBestResponse': b_high.json(), 'wBar': w_bar.json(),
            'rho': rho.json(), 'smallToleranceBounds': [first.json(), second.json()],
            'statusOfFailedChecks': 'Not certified by the sufficient theorem; no sampled replacement or claim that the condition is necessary.'}


def comparisons_for(targets, enclosure=None):
    records = []
    for label in TARGET_LABELS:
        matching = [r for r in targets if r.get('label') == label]
        row = matching[0] if len(matching) == 1 else None
        record = {'label': label, 'classification': 'unresolved'}
        if row is not None:
            for field, output in [('requestedTarget', 'requestedImported'),
                                  ('actualGuaranteedThreshold', 'thresholdImported')]:
                if field in row:
                    try:
                        record[output] = exact_binary64(row[field])
                    except (ValueError, TypeError, OverflowError) as error:
                        record['targetEvidenceFailure'] = 'Invalid imported target: ' + str(error)
            if 'thresholdImported' in record:
                threshold = decimal(float(row['actualGuaranteedThreshold']))
                record['thresholdExact'] = str(threshold)
                if enclosure is not None:
                    record['classification'] = classify_floor(enclosure, threshold)
        else:
            record['targetEvidenceFailure'] = 'Missing or duplicate retained target label'
        records.append(record)
    return records


def validate_case_targets(case, raw_records, expected_scenario):
    scenario_id = expected_scenario['id']
    if case.get('id') != scenario_id + '-guard' or case.get('scenario') != expected_scenario or case.get('controller') != 'guard':
        raise ValueError('Malformed inherited guard identity/economy/configuration')
    if case['game']['n'] != expected_scenario['gridSize'] or len(case['game']['prices']) != expected_scenario['gridSize']:
        raise ValueError('Inherited price-grid identity mismatch')
    if case['game']['treatment'] != {'type': 'guard', 'epsilon': expected_scenario['epsilon']}:
        raise ValueError('Inherited guard-treatment mismatch')
    selected = [r for r in raw_records if isinstance(r.get('scenario'), dict)
                and r['scenario'].get('id') == scenario_id]
    if len(selected) != 1 or selected[0].get('scenario') != expected_scenario or selected[0].get('guardCaseId') != case['id'] or selected[0].get('capCaseId') != scenario_id + '-cap':
        raise ValueError('Audited target scenario/economy/case identity mismatch')
    rows = selected[0]['results']
    if len(rows) != 5 or {r['label'] for r in rows} != set(TARGET_LABELS):
        raise ValueError('Expected exactly the five predeclared retained target labels')
    for row in rows:
        exact_binary64(row['requestedTarget'])
        exact_binary64(row['actualGuaranteedThreshold'])
    return rows


def solve_model(model, targets):
    record = {'importedBinary64': model.imported, 'rounding': model.rounding,
              'domainNormalized': {'lowerExact': str(model.ell), 'upperExact': str(model.high)},
              'k': model.k.json(), 'assumptions': certify_assumptions(model)}
    if not record['assumptions']['eligible']:
        record.update({'status': 'unresolved assumptions', 'comparisons': comparisons_for(targets)})
        return record
    nash, nash_proof = bisect_increasing(lambda x: x - 1 - model.w(x),
                                        model.ell, model.high, ROOT_TOLERANCE)
    # Fixed-point upper-root residual w(q)-t-f(q,q) is negative at Nash and
    # positive above the unique upper-map fixed point, under the theorem.
    residual = lambda x: model.w(x) - model.t - model.profit(x, x)
    high_residual = residual(I(model.high))
    if high_residual.sign == -1:
        qstar = I(model.high)
        q_proof = {'kind': 'ceiling-clipped', 'ceilingAllowedStrictly': True,
                   'ceilingResidual': high_residual.json(),
                   'upperBranchMargin': (I(model.high) - 1 - model.w(I(model.high))).json()}
    elif high_residual.sign == 1:
        qstar, proof = bisect_increasing(residual, nash.hi, model.high, ROOT_TOLERANCE)
        q_proof = {'kind': 'interior upper-root fixed point', **proof,
                   'lowerEndpoint': str(qstar.lo), 'upperEndpoint': str(qstar.hi)}
    else:
        raise Unresolved('Ceiling residual sign is unresolved; boundary equality not assumed')
    branch = qstar - 1 - model.w(qstar)
    if branch.lo <= 0:
        raise Unresolved('Upper best-response branch not certified')
    if qstar.width > Decimal('1e-25') or nash.width > Decimal('1e-25'):
        raise Unresolved('Required normalized root width not met')
    cs = model.surplus(qstar, qstar)
    nash_cs = model.surplus(nash, nash)
    own = model.mass_scale * model.profit(qstar, qstar)
    deviation = model.mass_scale * model.w(qstar)
    comparisons = comparisons_for(targets, cs)
    record.update({'status': 'certified theorem and enclosures',
                   'nash': {'normalizedPrice': nash.json(), 'price': model.original_price(nash).json(),
                            'consumerSurplus': nash_cs.json(), 'rootProof': nash_proof},
                   'worst': {'normalizedPrice': qstar.json(), 'price': model.original_price(qstar).json(),
                             'consumerSurplus': cs.json(), 'rootProof': q_proof,
                             'upperBranchMargin': branch.json(),
                             'profitA': own.json(), 'profitB': own.json(), 'jointProfit': (2 * own).json(),
                             'unilateralBestResponseProfit': deviation.json(),
                             'stationaryUnilateralDeviationGain': (deviation - own).json()},
                   'nashToWorstSurplusGap': (nash_cs - cs).json(), 'comparisons': comparisons,
                   'scope': 'All-start infimum of liminf infinite average surplus under the stated exact-real comparison continuum. No finite-time jump, equilibrium, learned behavior or literal floating-operation replay.'})
    return record


def input_inventory():
    manifest = read(ROOT / 'research/cycle-results/manifest.json')
    paths = ['research/cycle-results/manifest.json', 'research/cycle-results/independent-audit.json',
             'research/handover-init-results/manifest.json', 'research/handover-init-results/results.json',
             'research/handover-init-results/independent-audit.json']
    scenarios = manifest['plan']['scenarios']
    for scenario in scenarios:
        paths.append(f"research/cycle-results/cases/{scenario['id']}-guard.json")
    return scenarios, {p: digest(ROOT / p) for p in paths}


def freeze():
    if OUT.exists() and any(OUT.iterdir()):
        raise ValueError('Continuous evidence directory is not empty; refusing overwrite')
    scenarios, inputs = input_inventory()
    value = {'frozenAt': datetime.now(timezone.utc).isoformat(),
             'plan': {'scenarioIds': [s['id'] for s in scenarios], 'scenarios': scenarios,
                      'targetLabels': TARGET_LABELS, 'continuums': ['effective', 'nominal'],
                      'records': 16, 'precision': PRECISION, 'rootTolerance': ROOT_TOLERANCE,
                      'payoffAllowanceExact': str(decimal(ALLOWANCE)), 'runtimeTargetSeconds': 600,
                      'sampledRSSTargetBytes': 250_000_000, 'apiCalls': 0, 'trainingRounds': 0},
             'sourceHashes': {p: digest(ROOT / p) for p in SOURCES}, 'inputHashes': inputs}
    for p in SOURCES:
        dest = OUT / 'sources' / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / p).read_bytes())
    save(OUT / 'manifest.json', value)
    print(json.dumps({'frozenAt': value['frozenAt'], 'manifestSha256': digest(OUT / 'manifest.json')}))


def verify():
    manifest = read(OUT / 'manifest.json')
    for group in ('sourceHashes', 'inputHashes'):
        for name, expected in manifest[group].items():
            if digest(ROOT / name) != expected:
                raise ValueError('Frozen dependency changed: ' + name)
            if group == 'sourceHashes' and digest(OUT / 'sources' / name) != expected:
                raise ValueError('Frozen source snapshot changed: ' + name)
    return manifest


def run():
    manifest = verify()
    if (OUT / 'execution-start.json').exists() or (OUT / 'results.json').exists():
        raise ValueError('Continuous execution evidence already exists; refusing partial or complete overwrite')
    started = time.perf_counter()
    raw_targets = read(ROOT / 'research/handover-init-results/results.json')['records']
    save(OUT / 'execution-start.json', {'startedAt': datetime.now(timezone.utc).isoformat(),
                                      'manifestSha256': digest(OUT / 'manifest.json')})
    records = []
    samples = []
    for expected_scenario in manifest['plan']['scenarios']:
        scenario_id = expected_scenario['id']
        rows = []
        identity_error = None
        try:
            case = read(ROOT / f'research/cycle-results/cases/{scenario_id}-guard.json')
            selected = [r for r in raw_targets if isinstance(r.get('scenario'), dict)
                        and r['scenario'].get('id') == scenario_id]
            if len(selected) == 1 and isinstance(selected[0].get('results'), list):
                rows = selected[0]['results']
            rows = validate_case_targets(case, raw_targets, expected_scenario)
        except Exception as error:
            identity_error = error
        for kind in manifest['plan']['continuums']:
            began = time.perf_counter()
            model = None
            try:
                if identity_error is not None:
                    raise ValueError('Pre-case validation failed: ' + str(identity_error))
                model = Model(case['scenario']['economy'], case['game']['prices'][0],
                              case['game']['prices'][-1], case['scenario']['epsilon'], kind == 'effective')
                result = solve_model(model, rows)
            except Exception as error:
                result = {'status': 'unresolved calculation', 'failure': str(error),
                          'failureType': type(error).__name__,
                          'comparisons': comparisons_for(rows)}
                if model is not None:
                    result.update({'importedBinary64': model.imported, 'rounding': model.rounding,
                                   'domainNormalized': {'lowerExact': str(model.ell), 'upperExact': str(model.high)}})
            result.update({'scenario': scenario_id, 'continuum': kind,
                           'seconds': time.perf_counter() - began})
            records.append(result)
            save(OUT / 'records' / f'{scenario_id}-{kind}.json', result)
            samples.append({'scenario': scenario_id, 'continuum': kind, 'rssBytes': rss_bytes()})
            print(json.dumps({'scenario': scenario_id, 'continuum': kind, 'status': result['status'],
                              'seconds': result['seconds']}), flush=True)
    resources = {'seconds': time.perf_counter() - started, 'rssSamples': samples,
                 'largestObservedRSSBytes': max((s['rssBytes'] for s in samples if s['rssBytes'] is not None), default=None),
                 'sampling': 'After each retained record; not a continuously measured peak.',
                 'python': platform.python_version(), 'platform': platform.platform(),
                 'apiCalls': 0, 'newTrainingRounds': 0}
    save(OUT / 'results.json', {'manifestSha256': digest(OUT / 'manifest.json'), 'records': records})
    try:
        verify()
        final_dependencies = {'passed': True}
    except Exception as error:
        final_dependencies = {'passed': False, 'failure': str(error)}
    save(OUT / 'completion.json', {'records': len(records), 'resolved': sum(r['status'] == 'certified theorem and enclosures' for r in records),
                                 'unresolved': sum(r['status'] != 'certified theorem and enclosures' for r in records),
                                 'resultsSha256': digest(OUT / 'results.json'), 'resources': resources,
                                 'finalFrozenDependencyCheck': final_dependencies})
    if not final_dependencies['passed']:
        raise ValueError('Final frozen dependency check failed; retained outputs are invalidated')
    print(json.dumps({'complete': True, 'records': len(records), 'seconds': resources['seconds']}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['freeze', 'run', 'verify'])
    args = parser.parse_args()
    if args.mode == 'freeze':
        freeze()
    elif args.mode == 'run':
        run()
    else:
        verify()
        print(json.dumps({'passed': True, 'frozenDependencies': True}))


if __name__ == '__main__':
    main()
