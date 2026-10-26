"""Artificial-only tests for the independent learned-opponent certificate."""
import importlib.util
import itertools
import math
import json
import struct
import copy
import shutil
import uuid
from pathlib import Path
import sys
import unittest
from fractions import Fraction

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("independent_learned_audit",
                                            ROOT / "research/audit-learned-opponent.py")
A = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = A
SPEC.loader.exec_module(A)


class GraphLayout:
    def __init__(self, states):
        self.states = states

    def decode(self, state):
        A.require(type(state) is int and 0 <= state < self.states, "Invalid state")
        return state


class ArtificialMDP:
    """Arbitrary tiny graph, separate from the pricing-MDP builder under test."""
    def __init__(self, edges, baseline, denominator=1):
        self.layout = GraphLayout(len(edges))
        self.edges = edges
        self.original = baseline
        self.denominator = denominator
        self.counts = None

    def actions(self, state):
        return tuple(range(len(self.edges[state])))

    def edge(self, state, action):
        A.require(action in self.actions(state), "Illegal graph edge")
        nxt, reward = self.edges[state][action]
        return nxt, reward, 0, (action, 0)

    def baseline(self):
        return self.original


def direct_policy_values(mdp, policy, p=19, q=20):
    """Independent dense rational linear system for tiny test graphs."""
    n = mdp.layout.states
    matrix = [[Fraction(int(i == j)) for j in range(n)] + [Fraction(0)]
              for i in range(n)]
    for i in range(n):
        nxt, reward, _, _ = mdp.edge(i, policy[i])
        matrix[i][nxt] -= Fraction(p, q)
        matrix[i][-1] = Fraction(reward, mdp.denominator)
    for column in range(n):
        row = next(r for r in range(column, n) if matrix[r][column])
        matrix[column], matrix[row] = matrix[row], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [x/scale for x in matrix[column]]
        for r in range(n):
            if r != column:
                factor = matrix[r][column]
                matrix[r] = [a-factor*b for a, b in zip(matrix[r], matrix[column])]
    return [row[-1] for row in matrix]


def checkpoint_fixture(project, *, seed=907001, controller='selected95',
                       wrong_clock=False, wrong_total=False, wrong_saved_policy=False):
    """Complete artificial old-format files; never reads inherited evidence."""
    control_id = controller
    old_id = f'base-g15-t1--{control_id}--zero--s{seed}'
    prefix = 'research/adaptive-learning-results/'
    relative = f'checkpoints/{old_id}/step-2000000/'
    hashes = {}
    def save(file, data):
        if not isinstance(data, bytes):
            data = (json.dumps(data, separators=(',', ':'))+'\n').encode()
        target = project/file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        ref = {'file': file, 'bytes': len(data), 'sha256': A.digest(data)}
        hashes[file] = ref['sha256']
        return ref
    startup = controller == 'startup-only'
    control = {'id': control_id, 'period': None if startup else 4,
               'phases': 2 if startup else 4}
    layout = A.Layout(2, control['phases'], 0, ((0, 1), (0, 1)), startup)
    offsets = layout.offsets(); cells = offsets[-1]
    values = [0]*cells
    totals = [1, 1999999] if startup else [500000]*4
    for phase_index, total in enumerate(totals):
        values[offsets[phase_index*4]] = total
    values[offsets[0]] -= 1; values[offsets[3]] += 1  # old high history, first actual cap
    last_phase = control['phases']-1
    values[offsets[last_phase*4]] -= 1; values[offsets[last_phase*4]+1] += 1
    if wrong_total:
        values[next(i for i, value in enumerate(values) if value)] -= 1
    saturated = [min(value, 65535) for value in values]
    overflow = [[i, value] for i, value in enumerate(values) if value > 65535]
    finite = {'prices': [1., 2.], 'capIndex': 0, 'sets': [[0, 1], [0, 1]],
              'rewards': {'profitA': [1., 2., 3., 4.], 'profitB': [4., 3., 2., 1.],
                          'consumerSurplus': [10., 8., 7., 4.]}}
    raw = save('research/sparse-display-results/cases/base-g15-t1.json',
               {'scenario': {'id': 'base-g15-t1'}, 'finite': finite})
    files = {'q': [], 'counts': [], 'policies': []}
    supplied = {'q': [], 'counts': [], 'savedPolicies': []}
    for name in ('A', 'B'):
        for kind, key, filename, data in (
            ('q', 'q', 'Q-'+name+'.f64le', bytes(cells*8)),
            ('counts', 'counts', 'counts-'+name+'.u16le',
             struct.pack('<'+'H'*cells, *saturated)),
            ('policies', 'savedPolicies', 'greedy-'+name+'.u8',
             bytes([1 if wrong_saved_policy else 0]+[0]*(layout.states-1)))):
            ref = save(prefix+relative+filename, data)
            files[kind].append({**ref, 'file': relative+filename})
            supplied[key].append(ref)
    phase = (0 if startup else 1) if wrong_clock else (1 if startup else 0)
    terminal = {'phase': phase, 'previousIndices': [1, 1]}
    meta = {'step': 2_000_000, 'T': 2_000_000, 'seed': seed,
            'initialization': 'zero', 'alpha': .1, 'gamma': 19/20,
            'control': control, 'phase': phase, 'previousIndices': [1, 1],
            'capExecutions': 1 if startup else 500000,
            'layout': {'n': 2, 'rows': layout.states, 'cells': cells,
                       'offsetsSha256': A.digest(b''.join(struct.pack('<I', x) for x in offsets))},
            'countOverflow': [copy.deepcopy(overflow) for _ in range(2)],
            'files': files}
    metadata = save(prefix+relative+'metadata.json', meta)
    checkpoint = {'step': 2_000_000, 'file': relative+'metadata.json',
                  'sha256': metadata['sha256'], 'terminal': terminal}
    old = {'id': old_id, 'scenario': 'base-g15-t1', 'initialization': 'zero',
           'seed': seed, 'status': 'completed frozen-policy evaluation',
           'actualMainRounds': 2_000_000, 'rawFile': raw['file'],
           'rawSha256': raw['sha256'], 'control': control, 'checkpoints': [checkpoint]}
    old_ref = save(prefix+f'records/{old_id}.json', old)
    index = {'records': [{'id': old_id, 'file': f'records/{old_id}.json',
                          'sha256': old_ref['sha256'],
                          'checkpoints': [{k: checkpoint[k] for k in ('step', 'file', 'sha256')}]}]}
    supplied.update({'inputRoot': 'project', 'oldRunID': old_id,
                     'checkpointStep': 2000000, 'finiteGame': raw,
                     'oldRecord': old_ref, 'metadata': metadata, 'checkpointEntry': checkpoint})
    return supplied, {'seed': seed, 'control': control_id}, hashes, index


class IndependentLearnedAuditTests(unittest.TestCase):
    def test_modern_and_legacy_manifest_maps_require_actual_declared_dependencies(self):
        digest = 'a'*64
        self.assertEqual(A.inherited_manifest_dependencies({'hashes': {'old/source.js': digest}}),
                         {'old/source.js': digest})
        self.assertEqual(A.inherited_manifest_dependencies({'sources': {'old/source.js': digest}}),
                         {'old/source.js': digest})
        self.assertEqual(A.inherited_manifest_dependencies({'sourceHashes': {'source.py': digest}}),
                         {'source.py': digest})
        self.assertEqual(A.inherited_manifest_dependencies(
            {'sourceHashes': {'source.py': digest}, 'inputHashes': {},
             'hashes': {'source.py': digest}}), {'source.py': digest})
        for malformed in ({'oldCheckpointHashes': {}}, {'hashes': None}, {'sources': []},
                          {'hashes': {'source': 'invalid'}},
                          {'sources': {'source': {'sha256': digest}}},
                          {'hashes': {'source': digest}, 'sourceHashes': {'source': 'b'*64}}):
            with self.assertRaises(ValueError):
                A.inherited_manifest_dependencies(malformed)

    def test_independent_summaries_keep_seed_pairing_and_budget_availability(self):
        rows = []
        for plan in A.planned_cases():
            value = (plan['seed']-907000)*(1 if plan['focal'] == 'A' else -1)
            value += 2 if plan['control']['id'] == 'selected95' else 0
            rows.append({**plan, 'scientificAvailable': True, 'executionSucceeded': True,
                         'status': 'certified response within gap target',
                         'performance': {'rawGain': A.exact_hex(Fraction(value))}})
        rows[0]['status'] = 'retained hard-budget timeout'
        rows[0]['executionSucceeded'] = False
        rows[7]['scientificAvailable'] = rows[7]['executionSucceeded'] = False
        rows[7]['status'] = 'retained input failure'
        rows[7]['performance'] = None
        result = A.independent_summaries(rows)
        self.assertEqual([x['available'] for x in result['controllerSummaries']], [24, 23])
        self.assertEqual(result['controllerSummaries'][0]['executionSucceeded'], 23)
        self.assertEqual(result['pairedDifferences'][1]['status'], 'unavailable')
        self.assertIsNone(result['pairedDifferences'][1]['difference'])
        for row in result['pairedDifferences']:
            if row['status'] == 'available':
                self.assertEqual(A.parse_hex(row['difference']), 2)
        with self.assertRaises(ValueError):
            A.independent_summaries(rows[:-1])

    def test_full_artificial_checkpoint_loader_and_semantic_corruption(self):
        local = ROOT/'.local'; local.mkdir(exist_ok=True)
        project = (local/('learned-audit-input-'+uuid.uuid4().hex)).resolve()
        project.mkdir()
        try:
            self.assertTrue(project.is_relative_to(local.resolve()))
            for case_index, flags in enumerate(({}, {'wrong_clock': True}, {'wrong_total': True},
                                                {'wrong_saved_policy': True})):
                case = project/str(case_index)
                case.mkdir()
                supplied, expected, hashes, index = checkpoint_fixture(case, **flags)
                if flags:
                    with self.assertRaises(ValueError):
                        A.load_checkpoint_inputs(case, supplied, expected, hashes, index)
                else:
                    loaded = A.load_checkpoint_inputs(case, supplied, expected, hashes, index)
                    self.assertEqual(loaded['initial'], 3)
                    self.assertEqual(loaded['layout'].states, 16)
                    self.assertEqual(sum(loaded['counts'][0]), 2_000_000)
                    corrupted = copy.deepcopy(supplied)
                    corrupted['checkpointEntry']['terminal']['phase'] = 1
                    with self.assertRaises(ValueError):
                        A.load_checkpoint_inputs(case, corrupted, expected, hashes, index)
        finally:
            if project.resolve().is_relative_to(local.resolve()):
                shutil.rmtree(project)

    def test_binary64_quantization_ties_even_signed_and_extreme(self):
        for original, expected in ((2**-33, 0), (3*2**-33, 2),
                                   (-2**-33, 0), (-3*2**-33, -2),
                                   (math.ldexp(1., -1074), 0), (0., 0), (-0., 0)):
            self.assertEqual(A.quantize_binary64(original), expected)
        huge = float.fromhex('0x1.fffffffffffffp+1023')
        self.assertEqual(A.quantize_binary64(huge), int(huge)*2**32)
        with self.assertRaises(ValueError):
            A.quantize_binary64(math.inf)

    def test_saved_quantization_and_vector_encoding_corruptions(self):
        data = b"0x0\n-0x2\n0x2\n"
        candidate = A.parse_candidate_vector(data, 3)
        raw = struct.pack('<ddd', 2**-33, -3*2**-33, 3*2**-33)
        self.assertEqual(len(A.check_quantization(raw, candidate)), 3)
        for bad in (b"0x0\n-0x2\n0x2", b"0x00\n-0x2\n0x2\n",
                    b"0x0\n-0x0\n0x2\n", b"0x0\n0x2\n"):
            with self.assertRaises(ValueError):
                A.parse_candidate_vector(bad, 3)
        with self.assertRaises(ValueError):
            A.check_quantization(raw[:-1], candidate)
        with self.assertRaises(ValueError):
            A.check_quantization(struct.pack('<ddd', 2**-32, -3*2**-33, 3*2**-33), candidate)

    def test_exact_hex_and_binary64_reward_conversion(self):
        for value in (Fraction(0), Fraction(-17, 20), Fraction(2**20000-1, 3**20)):
            self.assertEqual(A.parse_hex(A.exact_hex(value)), value)
        for malformed in ({"numeratorHex": "0x2", "denominatorHex": "0x4"},
                          {"numeratorHex": "0x0", "denominatorHex": "-0x1"},
                          {"numeratorHex": "garbage", "denominatorHex": "0x1"}):
            with self.assertRaises(ValueError):
                A.parse_hex(malformed)
        values = [math.ldexp(1.0, -1074), -0.5, 1.25]
        denominator, integers = A.integer_rewards(values)
        self.assertEqual(denominator, 2**1074)
        self.assertEqual([Fraction(r, denominator) for r in integers],
                         [Fraction.from_float(v) for v in values])

    def test_q_ties_cap_history_and_b_transposition(self):
        layout = A.Layout(2, 2, 1, ((0, 1), (1,)), False)
        offsets = layout.offsets()
        qa = [0.0]*offsets[-1]
        qb = [0.0]*offsets[-1]
        # B at world cap state(previousA=0,previousB=1) uses own=1,rival=0 =>row2.
        qb[offsets[2]+1] = 4.0
        qb[offsets[0]] = 4.0
        policies = (A.masked_greedy(layout, qa), A.masked_greedy(layout, qb))
        self.assertEqual(policies[0][0], 0)  # exact tie -> lowest ORIGINAL index
        mdp_a = A.FrozenMDP(layout, 0, policies, (0, 10, 100, 1000), 1)
        mdp_b = A.FrozenMDP(layout, 1, policies, (1, 2, 4, 8), 1)
        s = 1
        self.assertEqual(mdp_a.rows(s), (1, 2))
        self.assertEqual(mdp_a.edge(s, 0), (5, 10, 1, (0, 1)))
        self.assertEqual(mdp_a.edge(0, 0)[2], 0)  # cap quote depends on old history
        self.assertEqual(mdp_b.edge(s, 1), (5, 2, 0, (0, 1)))
        self.assertNotEqual(mdp_b.edge(s, 1)[1], 4)  # no accidental transpose of WORLD table
        for bad in ([math.nan]*len(qa), qa[:-1]):
            with self.assertRaises(ValueError):
                A.masked_greedy(layout, bad)

    def test_startup_absorption_and_world_clock(self):
        layout = A.Layout(2, 2, 0, ((0, 1), (0, 1)), True)
        q = [0.0]*layout.offsets()[-1]
        policies = (A.masked_greedy(layout, q),)*2
        mdp = A.FrozenMDP(layout, 0, policies, (1, 2, 3, 4), 1)
        # Already-completed cap is not repeated from saved guard state.
        trace = A.trajectory(mdp, mdp.baseline(), 7)
        self.assertEqual(trace["states"], [7, 4])
        self.assertEqual(trace["cycleEntryState"], 4)
        self.assertEqual(trace["transientLength"], 1)
        self.assertTrue(all(s >= 4 for s in trace["states"]))
        self.assertEqual(A.parse_hex(trace["value"]), 20)

    def test_terminal_next_clock_uses_previous_execution_envelope(self):
        layout = A.Layout(4, 4, 0, ((0, 1), (1, 2), (2, 3), (3,)), False)
        self.assertEqual(A.validate_terminal(layout, 1, 1, [0, 0], 1), 0)
        self.assertEqual(A.validate_terminal(layout, 2, 2, [1, 1], 1), 1)
        # Next phase0 after4 executions retains upper quote3, not reset cap0.
        self.assertEqual(A.validate_terminal(layout, 4, 0, [3, 3], 1), 3)
        for args in ((1, 1, [1, 0], 1), (4, 1, [3, 3], 1), (4, 0, [3, 3], 2)):
            with self.assertRaises(ValueError):
                A.validate_terminal(layout, *args)
        startup = A.Layout(4, 2, 0, layout.sets, True)
        self.assertEqual(A.validate_terminal(startup, 2_000_000, 1, [3, 3], 1), 3)
        with self.assertRaises(ValueError):
            A.validate_terminal(startup, 2_000_000, 0, [0, 0], 1)

    def test_transient_cycle_formula_against_dense_linear_solution(self):
        mdp = ArtificialMDP([[(1, -3)], [(2, 7)], [(3, 2)], [(2, 5)]], [0]*4, 8)
        for p, q in ((19, 20), (0, 1), (1, 2)):
            expected = direct_policy_values(mdp, [0]*4, p, q)
            for initial in range(4):
                trace = A.trajectory(mdp, [0]*4, initial, p, q)
                self.assertEqual(A.parse_hex(trace["value"]), expected[initial])
                self.assertLessEqual(len(trace["states"]), mdp.layout.states)
        with self.assertRaises(ValueError):
            A.discounted_path_value([1, 2], 1, 2, 1)

    def test_all_edge_upper_bound_against_all_stationary_policies(self):
        mdp = ArtificialMDP([[(1, 2), (2, -1)], [(0, 4), (2, 6)],
                             [(2, 3), (1, 1)]], [0, 0, 0], 4)
        candidate = [-7, 20, 11]
        cert = A.bellman_certificate(mdp, candidate, 8)
        upper = [Fraction(a, cert["upperDenominator"]) for a in cert["upperNumerators"]]
        for policy in itertools.product(range(2), repeat=3):
            for achieved, ceiling in zip(direct_policy_values(mdp, policy), upper):
                self.assertLessEqual(achieved, ceiling)
        accepted = A.certify(mdp, candidate, cert["greedyPolicy"], 0, 8)
        self.assertGreaterEqual(A.parse_hex(accepted["optimalityGapUpper"]), 0)

    def test_negative_one_sided_residual_is_valid_not_absolute(self):
        mdp = ArtificialMDP([[(0, 1)]], [0])
        cert = A.bellman_certificate(mdp, [30], 1)
        self.assertEqual(cert["maxResidualNumeratorHex"], hex(-10))
        self.assertEqual(Fraction(cert["upperNumerators"][0], cert["upperDenominator"]), 20)
        outcome = A.certify(mdp, [30], [0], 0, 1)
        self.assertEqual(A.parse_hex(outcome["optimalityGapUpper"]), 0)

    def test_nonproposed_edge_residual_and_wrong_bound_factor(self):
        mdp = ArtificialMDP([[(0, 1), (0, 9)]], [0])
        cert = A.bellman_certificate(mdp, [0], 1)
        self.assertEqual(cert["legalEdges"], 2)
        self.assertEqual(cert["maxResidualWitness"], [0, 1, 0])
        self.assertEqual(int(cert["maxResidualNumeratorHex"], 16), 180)
        self.assertEqual(Fraction(cert["upperNumerators"][0], cert["upperDenominator"]), 180)
        # Proposed-only residual9 or a spurious gamma factor gives an invalid upper bound.
        self.assertLess(Fraction(9), direct_policy_values(mdp, [1])[0])
        self.assertLess(Fraction(19, 20)*180, direct_policy_values(mdp, [1])[0])
        with self.assertRaises(ValueError):
            A.certify(mdp, [0], [0], 0, 1)
        off_path = ArtificialMDP([[(0, 1)], [(1, 9)]], [0, 0])
        full = A.bellman_certificate(off_path, [0, 0], 1)
        self.assertEqual(full["maxResidualWitness"], [1, 0, 1])
        self.assertEqual(full["legalEdges"], 2)  # unreachable states are not omitted

    def test_long_cycle_exact_hex_avoids_decimal_digit_limit(self):
        length = 4000
        rewards = [1]*length
        rewards[-1] = 2
        value = A.discounted_path_value(rewards, 0, length, 1)
        expected = Fraction(20) + Fraction(19**(length-1)*20,
                                           20**length-19**length)
        self.assertEqual(value, expected)
        self.assertGreater(value.denominator.bit_length(), 14285)
        self.assertEqual(A.parse_hex(A.exact_hex(value)), value)

    def test_negative_achieved_gain_is_retained(self):
        # Immediate greedy chooses9 then stays0; baseline earns8 forever.
        mdp = ArtificialMDP([[(0, 8), (1, 9)], [(1, 0)]], [0, 0])
        cert = A.bellman_certificate(mdp, [0, 0], 1)
        result = A.certify(mdp, [0, 0], cert["greedyPolicy"], 0, 1)
        self.assertEqual(A.parse_hex(result["achievedGain"]), 9-160)
        self.assertFalse(result["gapTargetMet"])

    def test_count_overflows_and_off_path_coverage(self):
        layout = A.Layout(2, 1, 1, ((0, 1), (0, 1)), False)
        cells = layout.offsets()[-1]
        raw = [0]*cells; raw[0] = 65535
        counts = A.exact_counts(layout, raw, [[0, 100000]])
        self.assertEqual(counts[0], 100000)
        for overflow in ([[0, 65535]], [[0, 100000], [0, 200000]], [[1, 70000]]):
            with self.assertRaises(ValueError):
                A.exact_counts(layout, raw, overflow)
        q = [0.0]*cells
        policies = (A.masked_greedy(layout, q),)*2
        mdp = A.FrozenMDP(layout, 0, policies, (1, 2, 3, 4), 1,
                          (counts, tuple([0]*cells)))
        trace = A.trajectory(mdp, mdp.baseline(), 3)
        self.assertEqual(trace["coverage"][1]["unvisitedStateOccurrences"], 2)
        self.assertEqual(trace["coverage"][1]["neverTriedActionOccurrences"], 2)
        self.assertEqual(A.parse_hex(trace["coverage"][1][
            "normalizedDiscountedUnvisitedExposure"]), 1)
        # Illegal response at an unreachable/off-path state must still fail.
        illegal = list(mdp.baseline()); illegal[2] = 2
        with self.assertRaises(ValueError):
            A.trajectory(mdp, illegal, 0)

    def test_discounted_coverage_distinguishes_transient_cycle_and_far_future(self):
        exposure = A.normalized_discounted_exposure
        # One unsupported transient at t=0 has normalized weight1-gamma.
        self.assertEqual(exposure([1, 0], 1, 1, 1, 2), Fraction(1, 2))
        # An unsupported absorbing cycle first reached after five steps has weight gamma^5.
        self.assertEqual(exposure([0]*5+[1], 5, 1, 1, 2), Fraction(1, 32))
        # Alternating supported/unsupported cycle: gamma/(1+gamma), not1/2.
        self.assertEqual(exposure([0, 1], 0, 2, 1, 2), Fraction(1, 3))
        self.assertEqual(exposure([1, 0], 0, 2, 0, 1), 1)
        self.assertEqual(exposure([0]*3, 1, 2), 0)
        self.assertEqual(exposure([1]*3, 1, 2), 1)
        with self.assertRaises(ValueError):
            exposure([0, 2], 1, 1)

    def test_secondary_cycle_customer_mean_excludes_transient_and_discount(self):
        trace = {"transientLength": 1, "cycleLength": 2,
                 "executedPairs": [[0, 0], [0, 1], [1, 0]]}
        self.assertEqual(A.cycle_pair_reward_mean(trace, [1000.0, 1.5, 4.0, 0.0], 2),
                         Fraction(11, 4))
        with self.assertRaises(ValueError):
            A.cycle_pair_reward_mean({**trace, "cycleLength": 1}, [1000., 1.5, 4., 0.], 2)


if __name__ == "__main__":
    unittest.main()
