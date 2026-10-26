"""Primary as object under test; only artificial reward sequences are used.

The production independent JS audit never imports primary timing functions.
This cross-language test intentionally generates proposed synthetic records
with the primary, then checks every numeric/clock/credit/preview field through
the independently implemented JavaScript verifier.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import importlib.util
from fractions import Fraction as Q
import json
import subprocess
import shutil
import unittest
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('primary_mixed_object_under_test', ROOT/'research/mixed-timing-study.py')
primary = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = primary
spec.loader.exec_module(primary)


class Sequence(primary.Envelope):
    def __init__(self, terms, error=Q(0)):
        super().__init__()
        self.terms = list(map(Q, terms))
        self.error = error
        self.r0 = primary.Bounds(self.terms[0]-error, self.terms[0]+error)
        self.cstar = primary.Bounds(self.terms[-1]-error, self.terms[-1]+error)
        self.kind = 'finite' if error == 0 else 'effective'

    def _sum(self, n):
        total = sum(self.terms[:n], Q(0))+max(0, n-len(self.terms))*self.terms[-1]
        return primary.Bounds(total-n*self.error, total+n*self.error)

    def reward(self, age):
        r = self.terms[min(age, len(self.terms)-1)]
        return primary.Bounds(r-self.error, r+self.error)

    def price(self, age):
        return {'syntheticAge': age}


NODE_SOURCE = r"""
import fs from 'node:fs';
const a=await import(process.argv[1]);
const data=JSON.parse(fs.readFileSync(0,'utf8'));
for(const item of data){
 const env=a.tailEnvelope(item.terms),F=a.rat(item.F),error=a.rat(item.error),kind=item.kind;
 const r0={lo:env.r0.sub(error),hi:env.r0.add(error)},cstar={lo:env.cstar.sub(error),hi:env.cstar.add(error)};
 a.verifyPrimaryTarget(item.row,{F,r0,cstar,kind,finite:kind==='finite'?env:null});
 a.verifyPrimaryPreview(item.row,{F,kind,cstarLower:cstar.lo,
  reward:age=>({lo:env.reward(age).sub(error),hi:env.reward(age).add(error)}),price:age=>({syntheticAge:age})});
}
console.log(JSON.stringify({passed:true,records:data.length}));
"""


def verify(items):
    node = shutil.which('node')
    if not node:
        raise RuntimeError('Node is required for the independent cross-language audit test')
    return subprocess.run([node, '--input-type=module', '-e', NODE_SOURCE,
                           (ROOT/'research/audit-mixed-timing.js').as_uri()],
                          input=json.dumps(items), text=True, capture_output=True,
                          cwd=ROOT, check=False)


class CrossAudit(unittest.TestCase):
    @staticmethod
    def item(terms, target, error=Q(0)):
        env = Sequence(terms, error)
        return {'terms': [primary.ratio(x) for x in env.terms],
                'error': primary.ratio(error), 'kind': env.kind,
                'F': primary.ratio(target),
                'row': primary.solve_target(env, target, 'artificial-cross-audit')}

    def test_full_primary_synthetic_records_and_scientific_corruptions(self):
        items = [self.item([3,1,0], Q(3,2)), self.item([5,5,2], Q(5)),
                 self.item([5], Q(5)), self.item([3,1,0], Q(4)),
                 self.item([1,0], Q(1,2*primary.MAX_K)),
                 self.item([0,-2,-3], Q(-3,2)),
                 self.item([3,1,0], Q(3,2), Q(1,10**40))]
        result = verify(items)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['records'], len(items))
        mutations = [
            lambda r: r['calendar']['blockPreview64'][0].update(block=2),
            lambda r: r['calendar']['blockPreview64'][1].update(startExecution=4),
            lambda r: r['executionPreview'][0].update(mode='guard'),
            lambda r: r['executionPreview'][0].update(completedBlock=True),
            lambda r: r['executionPreview'][0].update(certifiedPrefixLowerBoundExact=primary.ratio(1)),
            lambda r: r['rates'].update(constructedSavingExact=primary.ratio(0)),
            lambda r: r['rates']['absoluteSavingSigns'].update(lower='zero'),
            lambda r: r['frontier']['queryLengths'].append(primary.MAX_K+1),
        ]
        for mutate in mutations:
            changed = deepcopy(items[0])
            mutate(changed['row'])
            outcome = verify([changed])
            self.assertNotEqual(outcome.returncode, 0, 'Scientific corruption was incorrectly accepted')
        interval = deepcopy(items[-1])
        interval['row']['rates']['exactOptimum'] = True
        self.assertNotEqual(verify([interval]).returncode, 0)
        censored = deepcopy(items[4])
        censored['row']['frontier']['bestFixedK'] = primary.MAX_K
        censored['row']['rates']['bestFixedK'] = primary.MAX_K
        censored['row']['rates']['exactOptimum'] = True
        censored['row']['status'] = 'certified exact mixed optimum'
        self.assertNotEqual(verify([censored]).returncode, 0)


if __name__ == '__main__':
    unittest.main()
