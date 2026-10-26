"""Prospective synthetic checks only; no inherited incentive case execution."""
from fractions import Fraction
from pathlib import Path
import functools
import hashlib
import importlib.util
import copy
import json
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('independent_incentive', Path(__file__).resolve().parents[1]/'research/audit-incentive-study.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def toy():
    return {'prices': [1., 2., 3.], 'sets': [[0, 1], [0, 1, 2], [1, 2]], 'capIndex': 1,
            'rewards': {'profitA': [1., 3., 2., 2., -1., 4., 0., 2., 3.],
                        'profitB': [5., 1., -3., 2., 4., 1., 7., 0., 2.],
                        'consumerSurplus': [10., 9., 8., 9., 8., 7., 8., 7., 6.]}}


def exhaustive(game, period, seller, gamma, phase=0, previous=None):
    """Enumerate every action sequence with Fraction rewards; no scaled Bellman arrays."""
    n, cap = len(game['prices']), game['capIndex']
    upper = [max(s) for s in game['sets']]
    def payoff(a, b):
        key, at = ('profitA', a*n+b) if seller == 0 else ('profitB', b*n+a)
        return Fraction(game['rewards'][key][at])
    def paths(at, own, rival):
        if at == period:
            return [(Fraction(0), ())]
        support = range(cap+1) if at == 0 else game['sets'][rival]
        other = cap if at == 0 else upper[own]
        return [(payoff(action, other)+gamma*tail, (action,)+acts)
                for action in support for tail, acts in paths(at+1, action, other)]
    outcomes = paths(phase, *(previous or (None, None)))
    maximum = max(v for v, _ in outcomes)
    return maximum, min(actions for value, actions in outcomes if value == maximum)


class IncentiveAuditTests(unittest.TestCase):
    def test_complete_integer_layers_match_exhaustive_asymmetric_negative_games(self):
        game = toy()
        for period in [1, 2, 3, 4]:
            for seller in [0, 1]:
                for gamma in [Fraction(19, 20), Fraction(0)]:
                    result = audit.calculate(game, period, seller, gamma)
                    value, actions = exhaustive(game, period, seller, gamma)
                    self.assertEqual(result['phases'][0]['optimalBlockValue'], value)
                    self.assertEqual(result['capOptimalAction'], actions[0])
                    for phase in range(1, period):
                        previous = result['phases'][phase]['previous']
                        expected, _ = exhaustive(game, period, seller, gamma, phase, previous)
                        self.assertEqual(result['phases'][phase]['optimalBlockValue'], expected)
                    self.assertTrue(all(row['infiniteGain'] >= 0 for row in result['phases']))

    def test_discount_zero_at_cap_misses_profitable_last_guard(self):
        game = {'prices': [1., 2.], 'sets': [[0, 1], [0, 1]], 'capIndex': 0,
                'rewards': {'profitA': [1., 3., 0., 2.], 'profitB': [1., 0., 3., 2.],
                            'consumerSurplus': [4., 3., 3., 2.]}}
        zero = audit.calculate(game, 2, 0, Fraction(0))
        positive = audit.calculate(game, 2, 0, Fraction(19, 20))
        self.assertEqual(zero['phases'][0]['infiniteGain'], 0)
        self.assertEqual(zero['oneShotScreen']['gain'], 1)
        self.assertGreater(positive['phases'][0]['infiniteGain'], 0)
        phase = positive['phases'][1]
        # Removing the next-cycle difference produces the wrong infinite gain.
        self.assertNotEqual(phase['infiniteGain'], phase['optimalBlockValue']-phase['baselineBlockValue'])

    def test_exact_conversion_tie_policy_and_signed_hash_encoding(self):
        self.assertEqual(audit.binary_fraction(.1), Fraction(*(.1).as_integer_ratio()))
        self.assertEqual(audit.value_hash([-2, 0, 3]), hashlib.sha256(b'-2\n0\n3\n').hexdigest())
        with self.assertRaises(ValueError):
            audit.binary_fraction(float('inf'))
        game = toy()
        game['rewards']['profitA'] = [-1.]*9
        result = audit.calculate(game, 3, 0, Fraction(19, 20))
        self.assertEqual(result['capOptimalAction'], 0)
        for layer in result['layers'].values():
            for i in range(3):
                for j in range(3):
                    self.assertEqual(layer['policy'][i*3+j], min(game['sets'][j]))

    def test_exact_minimum_prefix_not_assumed_equal_cycle_mean(self):
        game = toy()
        # Explicitly allow a cap above its guard upper image: reward rises after
        # the first execution, so the first prefix sets the finite floor.
        game['capIndex'] = 2
        game['sets'] = [[0], [1], [1]]
        result = audit.finite_welfare(game, 3)
        self.assertEqual(result['cycleIndices'], [2, 1, 1])
        self.assertEqual(result['activationFloor'], 6)
        self.assertEqual(result['cycleAverage'], Fraction(22, 3))
        self.assertEqual(result['minimizingPrefix'], 1)
        game['rewards']['consumerSurplus'][1] = 11.
        with self.assertRaises(ValueError):
            audit.finite_welfare(game, 3)

    def test_primary_toy_record_is_checked_without_primary_audit_imports(self):
        # Primary code constructs a synthetic certificate only. All checking is
        # independent Python code; no inherited study cases are evaluated.
        raw = {'finite': toy()}
        raw['finite']['upper'] = [max(s) for s in raw['finite']['sets']]
        module = (Path(__file__).resolve().parents[1]/'research/incentive-study.js').as_uri()
        script = ('import {solveBlock} from '+json.dumps(module)+';'
                  'const raw='+json.dumps(raw)+';const r=solveBlock(raw,3,"B",{p:19,q:20});'
                  'const files={};for(const l of r.layers){l.argmaxFile="toy/"+l.phase;'
                  'files[l.argmaxFile]=Buffer.from(r.policies.get(l.phase)).toString("base64");}'
                  'delete r.policies;r.status="completed exact unilateral audit";'
                  'console.log(JSON.stringify({r,files}));')
        import base64
        fixture = json.loads(subprocess.run(['node', '--input-type=module', '-e', script],
                                           check=True, capture_output=True, text=True).stdout)
        loader = lambda path: base64.b64decode(fixture['files'][path])
        audit.check_record(fixture['r'], raw['finite'], loader)
        alterations = [lambda r: r['layers'][0].update(optimalValueSha256='0'*64),
                       lambda r: r['cap'].update(action=255),
                       lambda r: r['phaseDiagnostics'][1]['nextCycleOptimalContribution'].update(numerator='-1'),
                       lambda r: r.update(rewardOrientation='original profitA[own*n+rival]'),
                       lambda r: r['oneShotScreen']['gain'].update(numerator='-1')]
        for mutate in alterations:
            altered = copy.deepcopy(fixture['r'])
            mutate(altered)
            with self.assertRaises(ValueError):
                audit.check_record(altered, raw['finite'], loader)
        with self.assertRaises(ValueError):
            audit.check_record(fixture['r'], raw['finite'], lambda path: bytes([255])*9)


if __name__ == '__main__':
    unittest.main()
