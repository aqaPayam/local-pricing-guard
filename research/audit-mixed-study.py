"""Authoritative independent mixed-timing audit driver.

Computes continuous checks freshly in this Python process, then invokes the
independent JS BigInt/control component. A JS-only/cached bridge result is not
a full acceptance certificate. Imports read source code, not market evidence.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
from datetime import datetime, timezone
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mixed_independent_fresh_continuous', ROOT/'research/audit-mixed-continuous.py')
continuous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(continuous)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def local(file):
    file = (ROOT/file).resolve()
    require(file == ROOT or ROOT in file.parents, 'Evidence path stays in workspace')
    return file


def digest(file):
    h = hashlib.sha256()
    with local(file).open('rb') as f:
        for block in iter(lambda: f.read(2*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read(file):
    return json.loads(local(file).read_text(encoding='utf-8-sig'))


def run_node_component(script, args, payload, node=None):
    """Python->Node works in the sandbox; no Node->Python child is needed."""
    node = node or shutil.which('node')
    require(node is not None, 'Node runtime is required for independent BigInt checks')
    result = subprocess.run([node, str(local(script)), *args],
                            input=json.dumps(payload, separators=(',', ':')),
                            text=True, capture_output=True, cwd=ROOT, check=False)
    require(result.returncode == 0, 'Independent Node component failed: '+result.stderr)
    return json.loads(result.stdout)


def finalize_component(component, bridge):
    require(component['passed'] is False and component['componentPassed'] is True and
            component['requiresOrchestrator'] is True,
            'A component-only result cannot masquerade as full independent acceptance')
    for field in ['studyManifestHash', 'resultsSha256', 'continuousAuditorSourceHash', 'arithmeticBackendHash']:
        require(component[field] == bridge[field], 'Component/fresh continuous identity mismatch '+field)
    require(component['auditorSourceHash'] == bridge['controlAuditorSourceHash'], 'Exact independent JS source')
    require(component['scalarRootCertificates'] == sum(e['result']['scalarRootCertificates'] for e in bridge['records'].values()),
            'All freshly calculated scalar certificates included')
    require(sorted(bridge['records']) == sorted(e['id'] for e in component['details'] if e['scalarRootCertificates'] > 0),
            'Complete fresh continuous/model coverage')
    return {**component, 'passed': True, 'requiresOrchestrator': False,
            'auditorSourceHash': bridge['orchestratorSourceHash'],
            'controlAuditorSourceHash': bridge['controlAuditorSourceHash'],
            'orchestratorSourceHash': bridge['orchestratorSourceHash'],
            'auditorEntryPoint': 'research/audit-mixed-study.py',
            'continuousChecksComputedInProcess': True,
            'continuousBridgeScope': 'Fresh recomputation in authoritative Python process; no saved/unvalidated bridge cache accepted as full audit'}


def audit(directory='research/mixed-timing-results', node=None):
    began = perf_counter()
    directory = local(directory)
    prefix = directory.relative_to(ROOT).as_posix()+'/'
    manifest, results = read(prefix+'manifest.json'), read(prefix+'results.json')
    mh = digest(prefix+'manifest.json')
    require(results['manifestSha256'] == mh, 'New aggregate/manifest binding before continuous computation')
    files = ['research/audit-mixed-study.py', 'research/audit-mixed-continuous.py',
             'research/audit-mixed-timing.js', 'tests/test_mixed_audit_driver.py']
    for file in files:
        require(manifest['sourceHashes'].get(file) == digest(file), 'Frozen independent source '+file)
    inherited = read('research/continuous-results/results.json')['records']
    plans = manifest['plan']['models']
    require(len(plans) == len(results['records']) == 24, 'All planned model containers')
    bridge = {'schemaVersion': 1, 'studyManifestHash': mh,
              'resultsSha256': digest(prefix+'results.json'),
              'inheritedResultsSha256': digest('research/continuous-results/results.json'),
              'orchestratorSourceHash': digest('research/audit-mixed-study.py'),
              'controlAuditorSourceHash': digest('research/audit-mixed-timing.js'),
              'continuousAuditorSourceHash': digest('research/audit-mixed-continuous.py'),
              'arithmeticBackendHash': digest('research/audit-continuous-study.py'), 'records': {}}
    for plan, record in zip(plans, results['records']):
        require(record['id'] == plan['id'], 'Continuous driver model order')
        if plan['kind'] == 'finite' or record['envelope'] is None:
            continue
        require(plan['kind'] in ['effective', 'nominal'], 'Declared continuous interpretation')
        closed_file = plan['continuousFile']
        guard_file = 'research/cycle-results/cases/'+plan['scenario']+'-guard.json'
        raw = read(plan['finiteFile'])
        matches = [r for r in inherited if r['scenario'] == plan['scenario'] and r['continuum'] == plan['kind']]
        require(len(matches) == 1, 'Unique accepted global continuum identity')
        periods = [r['period'] for r in record['queriedSums'] if r['sumBounds'] is not None]
        payload = {'record': read(closed_file), 'guard': read(guard_file),
                   'inherited': matches[0], 'physicalCap': raw['cap']['price'], 'periods': periods}
        bindings = {'closedFile': closed_file, 'closedSha256': digest(closed_file),
                    'guardFile': guard_file, 'guardSha256': digest(guard_file), 'periods': periods}
        computed = continuous.verify_payload(payload)
        bridge['records'][plan['id']] = {**bindings, 'result': computed}
        print('Independently checked continuous orbit and queried sums: '+plan['id'], file=sys.stderr, flush=True)
    component = run_node_component('research/audit-mixed-timing.js',
                                   ['--internal-continuous-bridge', prefix.rstrip('/')], bridge, node)
    result = finalize_component(component, bridge)
    # The Node component checked the full frozen source/input closure and
    # journals after our continuous computation. Recheck the exact bridge's
    # scientific/source bindings once more before emitting acceptance.
    require(digest(prefix+'manifest.json') == mh and digest(prefix+'results.json') == bridge['resultsSha256'],
            'Primary identities unchanged after both components')
    for field, file in [('orchestratorSourceHash', 'research/audit-mixed-study.py'),
                        ('controlAuditorSourceHash', 'research/audit-mixed-timing.js'),
                        ('continuousAuditorSourceHash', 'research/audit-mixed-continuous.py'),
                        ('arithmeticBackendHash', 'research/audit-continuous-study.py')]:
        require(digest(file) == bridge[field], 'Independent source unchanged after full audit')
    result['completedAt'] = datetime.now(timezone.utc).isoformat()
    result['seconds'] = perf_counter()-began
    return result


def write_receipt(file, result):
    """Exclusive output: re-verification cannot alter a closed receipt."""
    with local(file).open('x', encoding='utf-8') as f:
        f.write(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', default='research/mixed-timing-results')
    parser.add_argument('--output')
    parser.add_argument('--node')
    args = parser.parse_args()
    if args.output:
        require(not local(args.output).exists(), 'Existing independent receipt preserved; choose a new output path')
    result = audit(args.directory, args.node)
    if args.output:
        write_receipt(args.output, result)
    print(json.dumps(result, separators=(',', ':')))
