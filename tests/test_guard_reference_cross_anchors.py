"""Invented-only cross-author exact static-anchor agreement; no inherited IO."""
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('invented_primary_guard_anchors', ROOT/'research/guard-reference-analysis.py')
PRIMARY = importlib.util.module_from_spec(SPEC)
# Source execution is confined to the newly authored pure module; it performs no IO.
exec(compile((ROOT/'research/guard-reference-analysis.py').read_bytes(), str(SPEC.origin), 'exec'), PRIMARY.__dict__)


class AnchorCrossAudit(unittest.TestCase):
    def test_all_exact_scientific_fields_agree_on_invented_games(self):
        rng = random.Random(20261026)
        cases = []
        def game(a, b, n=2):
            return dict(prices=[i/8 for i in range(n)], rewards=dict(profitA=a, profitB=b, consumerSurplus=[-i/16 for i in range(n*n)]))
        cases.append(game([0.0, -0.0, 0.0, 0.0], [0.0]*4))
        cases.append(game([1, -1, -1, 1], [-1, 1, 1, -1]))
        cases.append(game([0, 2, 3, 1], [0, 4, 2, 1]))
        cases.append(game([1, 1, -1, -1], [2**-53, 0, 0, 0]))
        cases.append(game([-5e-324, 0, -1, -1], [5e-324, 0, -1, -1]))
        for n in range(2, 6):
            for _ in range(4):
                cases.append(game([rng.randrange(-8, 9)/8 for _ in range(n*n)], [rng.randrange(-8, 9)/16 for _ in range(n*n)], n))
        source = """import {exactStageAnchors} from './research/audit-guard-reference.js';
let s='';for await(const b of process.stdin)s+=b;
process.stdout.write(JSON.stringify(JSON.parse(s).map(exactStageAnchors)));
"""
        run = subprocess.run(['node', '--input-type=module', '-e', source], input=json.dumps(cases), text=True,
                             capture_output=True, cwd=ROOT, timeout=30, check=True)
        independently = json.loads(run.stdout)
        self.assertEqual(len(independently), len(cases))
        for case, actual in zip(cases, independently):
            expected = PRIMARY.stage_anchors(case)
            # Independently phrased interpretation strings are not numerical proof.
            for row in [actual, expected]:
                row.pop('scope'); row.pop('coordinateOrder')
                self.assertEqual(row['pureNash']['reason'] is None, row['pureNash']['count'] > 0)
                row['pureNash'].pop('reason')
            self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
