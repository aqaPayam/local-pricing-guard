"""Artificial-only Python->Node full-record orchestration and trust gates."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import importlib.util
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import json
import unittest
import uuid
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT/file)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result

driver = module('mixed_driver_object', 'research/audit-mixed-study.py')
cross = module('mixed_cross_fixtures', 'tests/test_mixed_timing_cross_audit.py')
B = driver.continuous.B


def artificial_continuous_payload():
    # A wholly artificial ceiling-clipped map U(y)=1.25, cap1, k=1.
    # This is not an inherited economic calibration or an experimental outcome.
    guard = {'scenario': {'id': 'artificial-ceiling', 'economy': {'quality': 0,
             'cost': 0, 'mu': 1, 'buyers': 1, 'outsideQuality': 0}, 'epsilon': .01},
             'game': {'prices': [0, 1.25]}}
    model = driver.continuous.backend.AuditEconomy(guard, 'nominal')
    proofs = {}
    for rival in ['1', '1.25']:
        with localcontext() as ctx:
            ctx.prec = 200
            y = Decimal(rival)
            z = 1/(Decimal(1).exp()*(1+(-y).exp()))
            lo, hi = Decimal(0), Decimal(1)
            for _ in range(600):
                mid = (lo+hi)/2
                if mid*mid.exp() < z: lo = mid
                else: hi = mid
            w = (lo+hi)/2
            wl, wh = w-Decimal('1e-70'), w+Decimal('1e-70')
            pad = Decimal('1e-120')
            tlo, thi = model.t.low, model.t.high
            proofs[rival] = {'rivalExact': rival, 'bestProfitW': {'lower': str(wl), 'upper': str(wh)},
                'bestResponse': {'lower': str(1+wl-pad), 'upper': str(1+wh+pad)},
                'normalizedTargetProfit': {'lower': str(wl-thi-pad), 'upper': str(wh-tlo+pad)},
                'normalizedPrice': B('1.25').strings(), 'proof': {'kind': 'ceiling-clipped'}}
    orbit = []
    for j in range(64):
        x = '1' if j == 0 else '1.25'
        orbit.append({'j': j, 'executedNormalizedPrice': B(x).strings(),
                      'executedPrice': B(x).strings(), 'consumerSurplus': model.diagonal_cs(B(x)).strings(),
                      'nextNormalizedPrice': B('1.25').strings(),
                      'upperMapProof': {'lowerEndpoint': proofs[x], 'upperEndpoint': proofs[x]}})
    inherited = {'scenario': 'artificial-ceiling',
                 'worst': {'normalizedPrice': B('1.25').strings(),
                           'consumerSurplus': model.diagonal_cs(B('1.25')).strings()},
                 'assumptions': {'rho': B('.5').strings()}}
    record = {'scenario': 'artificial-ceiling', 'continuum': 'nominal', 'normalizedCapExact': '1',
              'prefixTerms': 64, 'orbit': orbit, 'aJ': B('1.25').strings(), 'qStarMinusAJ': B(0).strings()}
    return {'guard': guard, 'record': record, 'inherited': inherited, 'physicalCap': 1,
            'periods': [1, 2, 64, 65, 65536]}


NODE_FIXTURE = r"""
import fs from 'node:fs';
const a=await import(process.argv[2]);
const bundle=JSON.parse(fs.readFileSync(0,'utf8'));
for(const item of bundle.targets){
 const env=a.tailEnvelope(item.terms),F=a.rat(item.F),e=a.rat(item.error),kind=item.kind;
 a.verifyPrimaryTarget(item.row,{F,r0:{lo:env.r0.sub(e),hi:env.r0.add(e)},cstar:{lo:env.cstar.sub(e),hi:env.cstar.add(e)},kind,finite:kind==='finite'?env:null});
 a.verifyPrimaryPreview(item.row,{F,kind,cstarLower:env.cstar.sub(e),reward:age=>({lo:env.reward(age).sub(e),hi:env.reward(age).add(e)}),price:age=>({syntheticAge:age})});
}
if(!bundle.bridge.records.synthetic.result.passed||bundle.bridge.records.synthetic.result.scalarRootCertificates!==128)throw Error('Fresh continuous component missing');
console.log(JSON.stringify({...bundle.component,syntheticCompleteRecordsChecked:bundle.targets.length}));
"""


class DriverTests(unittest.TestCase):
    def test_existing_receipt_is_preserved_on_reverification_output(self):
        relative = '.local/mixed-receipt-artificial-'+uuid.uuid4().hex+'.json'
        file = ROOT/relative
        file.parent.mkdir(parents=True, exist_ok=True)
        try:
            driver.write_receipt(relative, {'passed': True, 'synthetic': True, 'stamp': 'closed'})
            before = file.read_bytes()
            with self.assertRaises(FileExistsError):
                driver.write_receipt(relative, {'passed': False, 'stamp': 'overwritten'})
            self.assertEqual(file.read_bytes(), before)
        finally:
            self.assertEqual(file.parent, ROOT/'.local')
            file.unlink(missing_ok=True)

    def test_fresh_continuous_then_actual_python_node_full_record_bridge(self):
        computed = driver.continuous.verify_payload(artificial_continuous_payload())
        self.assertTrue(computed['passed'])
        bridge = {'studyManifestHash': 'artificial-manifest', 'resultsSha256': 'artificial-results',
                  'orchestratorSourceHash': driver.digest('research/audit-mixed-study.py'),
                  'controlAuditorSourceHash': driver.digest('research/audit-mixed-timing.js'),
                  'continuousAuditorSourceHash': driver.digest('research/audit-mixed-continuous.py'),
                  'arithmeticBackendHash': driver.digest('research/audit-continuous-study.py'),
                  'records': {'synthetic': {'result': computed}}}
        component = {k: bridge[k] for k in ['studyManifestHash', 'resultsSha256', 'continuousAuditorSourceHash', 'arithmeticBackendHash']}
        component.update(passed=False, componentPassed=True, requiresOrchestrator=True,
                         auditorSourceHash=bridge['controlAuditorSourceHash'], scalarRootCertificates=128,
                         details=[{'id': 'synthetic', 'scalarRootCertificates': 128}])
        targets = [cross.CrossAudit.item([3,1,0], Q(3,2)), cross.CrossAudit.item([5], Q(5)),
                   cross.CrossAudit.item([1,0], Q(1,131072)),
                   cross.CrossAudit.item([3,1,0], Q(3,2), Q(1,10**40))]
        relative = '.local/mixed-driver-artificial-'+uuid.uuid4().hex+'.mjs'
        file = ROOT/relative
        file.parent.mkdir(parents=True, exist_ok=True)
        try:
            file.write_text(NODE_FIXTURE, encoding='utf-8')
            result = driver.run_node_component(relative, [(ROOT/'research/audit-mixed-timing.js').as_uri()],
                                                {'bridge': bridge, 'component': component, 'targets': targets})
            final = driver.finalize_component(result, bridge)
            self.assertEqual(final['syntheticCompleteRecordsChecked'], 4)
            self.assertTrue(final['passed'])
            self.assertFalse(final['requiresOrchestrator'])
            self.assertTrue(final['continuousChecksComputedInProcess'])
            self.assertEqual(final['auditorSourceHash'], bridge['orchestratorSourceHash'])
        finally:
            self.assertEqual(file.parent, ROOT/'.local')
            file.unlink(missing_ok=True)

    def test_component_or_cache_cannot_be_mistaken_for_full_acceptance(self):
        bridge = {'studyManifestHash': 'm', 'resultsSha256': 'r', 'continuousAuditorSourceHash': 'h',
                  'arithmeticBackendHash': 'b', 'controlAuditorSourceHash': 'c', 'orchestratorSourceHash': 'o',
                  'records': {}}
        component = {k: bridge[k] for k in ['studyManifestHash','resultsSha256','continuousAuditorSourceHash','arithmeticBackendHash']}
        component.update(passed=False, componentPassed=True, requiresOrchestrator=True,
                         auditorSourceHash='c', scalarRootCertificates=0, details=[])
        self.assertTrue(driver.finalize_component(component, bridge)['passed'])
        for field,value in [('passed',True), ('requiresOrchestrator',False),
                            ('resultsSha256','stale'), ('auditorSourceHash','wrong-source'),
                            ('scalarRootCertificates',128)]:
            changed = deepcopy(component);changed[field] = value
            with self.assertRaises(ValueError): driver.finalize_component(changed, bridge)


if __name__ == '__main__':
    unittest.main()
