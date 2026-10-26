"""Synthetic saved-Q / functional-graph checks; no research training cases."""
from fractions import Fraction
from pathlib import Path
import importlib.util
import sys
import unittest
import struct
import json
import copy
import subprocess
import tempfile
import shutil

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('adaptive_audit', Path(__file__).resolve().parents[1]/'research/audit-adaptive-learning.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def game():
    return {'prices': [1., 2., 3.], 'capIndex': 1,
            'sets': [[0, 1], [0, 2], [1, 2]],
            'rewards': {'consumerSurplus': [10., 9., 8., 9., 8., 7., 8., 7., 6.],
                        'profitA': list(map(float, range(9))),
                        'profitB': [9., 8., 7., 6., 5., 4., 3., 2., 1.]}}


class AdaptiveAuditTests(unittest.TestCase):
    def test_actual_checkpoint_phase_specific_invariant_rejects_off_basin_history(self):
        market = game()
        market['sets'] = [[0, 1], [0, 1], [1, 2]]
        startup = {'kind': 'startup-only'}
        self.assertEqual(audit.check_endpoint(market, startup, {'step': 1000000, 'phase': 1, 'previousIndices': [1, 0]}), 1)
        with self.assertRaises(ValueError):
            audit.check_endpoint(market, startup, {'step': 1000000, 'phase': 1, 'previousIndices': [2, 0]})
        with self.assertRaises(ValueError):
            audit.check_endpoint(market, startup, {'step': 1000000, 'phase': 0, 'previousIndices': [1, 0]})
        # A periodic checkpoint immediately after a cap is bounded by A itself.
        market['sets'] = [[0, 1], [0, 2], [1, 2]]
        periodic = {'kind': 'periodic', 'period': 4}
        self.assertEqual(audit.check_endpoint(market, periodic, {'step': 5, 'phase': 1, 'previousIndices': [1, 0]}), 1)
        with self.assertRaises(ValueError):
            audit.check_endpoint(market, periodic, {'step': 5, 'phase': 1, 'previousIndices': [2, 0]})
        self.assertEqual(audit.check_endpoint(market, periodic, {'step': 6, 'phase': 2, 'previousIndices': [2, 0]}), 2)
        for step, phase, ceiling in [(1, 1, 1), (2, 2, 2), (4, 0, 2)]:
            self.assertEqual(audit.check_endpoint(market, periodic, {'step': step, 'phase': phase, 'previousIndices': [ceiling, 0]}), ceiling)

    def test_complete_frozen_graph_rebuild_keeps_unreachable_bad_cycle(self):
        raw = {'finite': game(), 'originalTargets': [{'label': 'toy', 'actualGuaranteedThreshold': 8.}]}
        raw['finite']['sets'] = [[0, 1], [0, 1], [1, 2]]
        module = (Path(__file__).resolve().parents[1]/'research/adaptive-learning.js').as_uri()
        script = ('import {createLearners,controller,rebuildMaxima,evaluateFrozen} from '+json.dumps(module)+';'
                  'const raw='+json.dumps(raw)+';const m=createLearners(raw,controller("startup-only"),{T:2000,actorStates:[[1,2,3,4],[5,6,7,8]]});'
                  'for(let f=0;f<2;f++)m.q[f][m.L.offsets[17]+1]=10;rebuildMaxima(m);'
                  'm.t=100;m.phase=1;m.previous=[1,1];m.capExecutions=1;'
                  'console.log(JSON.stringify({graph:evaluateFrozen(m).graph,q:m.q.map(x=>Array.from(x)),counts:m.counts.map(x=>Array.from(x)),state:{step:m.t,phase:m.phase,previousIndices:m.previous}}));')
        fixture = json.loads(subprocess.run(['node', '--input-type=module', '-e', script], check=True,
                                            text=True, capture_output=True).stdout)
        result = audit.check_frozen_graph(fixture['graph'], raw, {'kind': 'startup-only'},
                                          fixture['q'], fixture['counts'], [{}, {}], fixture['state'])
        self.assertEqual(result['actualCycleBenefit'], 10)
        self.assertTrue(any(not c['floorApplies'] and int(c['floorGap']['numerator']) < 0 for c in fixture['graph']['cycles']))
        changed = copy.deepcopy(fixture)
        changed['graph']['cycles'][0]['metrics']['profits']['B']['numerator'] = '999'
        with self.assertRaises(ValueError):
            audit.check_frozen_graph(changed['graph'], raw, {'kind': 'startup-only'},
                                      changed['q'], changed['counts'], [{}, {}], changed['state'])

    def test_portable_synthetic_checkpoint_full_probe_and_window_audit(self):
        raw = {'finite': game(), 'originalTargets': []}
        raw['finite']['sets'] = [[0, 1], [0, 1], [1, 2]]
        module = (Path(__file__).resolve().parents[1]/'research/adaptive-learning.js').as_uri()
        directory = None
        try:
            script = ('import fs from "node:fs";import {createLearners,controller,advance,checkpoint} from '+json.dumps(module)+';'
                      'const raw='+json.dumps(raw)+';const m=createLearners(raw,controller("startup-only"),{T:2000,actorStates:[[1,2,3,4],[5,6,7,8]]});'
                      'const directory=fs.mkdtempSync(".local/adaptive-audit-toy-");advance(m,1000);console.log(JSON.stringify({directory,entry:checkpoint(directory,"toy",m)}));')
            process = subprocess.run(['node', '--input-type=module', '-e', script], text=True, capture_output=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            fixture = json.loads(process.stdout)
            directory, entry = Path(fixture['directory']), fixture['entry']
            plan = {'control': {'id': 'startup-only', 'period': None, 'phases': 2}, 'seed': 907001, 'initialization': 'zero'}
            result = audit.check_checkpoint(directory, entry, raw, plan, [[1, 2, 3, 4], [5, 6, 7, 8]], horizon=2000)
            self.assertEqual(result['meta']['step'], 1000)
            self.assertEqual(result['probe']['afterClone']['step'], 1032)
        finally:
            if directory is not None:
                self.assertTrue(directory.resolve().is_relative_to(Path(__file__).resolve().parents[1]/'.local'))
                shutil.rmtree(directory)

    def test_all_state_cycles_distinguish_terminal_reachability(self):
        edges = [1, 2, 1, 4, 4, 3]
        result = audit.decompose(edges)
        self.assertEqual(set(result['cycles']), {(1, 2), (4,)})
        self.assertEqual(result['distance'], [1, 0, 0, 1, 0, 2])
        self.assertEqual(result['cycles'][(1, 2)]['basinStates'], 3)
        self.assertEqual(audit.trace(edges, 5), {'transient': [5, 3], 'cycle': [4], 'canonicalCycle': (4,)})
        self.assertNotEqual(result['cycleByState'][0], result['cycleByState'][5])

    def test_compact_q_legality_ties_and_seller_b_public_orientation(self):
        market, controller = game(), {'kind': 'periodic', 'period': 2}
        rows, offsets = audit.compact_rows(market, controller)
        qa, qb = [0.]*offsets[-1], [0.]*offsets[-1]
        # At public guard state(prevA=0,prevB=1), B reads focal own=1,rival=0.
        public = 9+0*3+1
        brow = 9+1*3+0
        qa[offsets[public]+1] = 3.
        qb[offsets[brow]+1] = 5.
        a = audit.masked_greedy(qa, rows, offsets)
        b = audit.masked_greedy(qb, rows, offsets)
        edges, actions = audit.public_graph(market, controller, [a, b])
        self.assertEqual(tuple(actions[2*public:2*public+2]), (2, 1))
        self.assertEqual(edges[public], 2*3+1)
        self.assertEqual(a[0], 0)  # Exact tied lowest original quote.
        qa[0] = float('nan')
        with self.assertRaises(ValueError):
            audit.masked_greedy(qa, rows, offsets)

    def test_startup_cap_is_transient_and_cycle_mean_excludes_old_history(self):
        market, controller = game(), {'kind': 'startup-only'}
        rows, offsets = audit.compact_rows(market, controller)
        policy = audit.masked_greedy([0.]*offsets[-1], rows, offsets)
        edges, actions = audit.public_graph(market, controller, [policy, policy])
        self.assertTrue(all(destination >= 9 for destination in edges))
        path = audit.trace(edges, 8)
        self.assertTrue(all(state >= 9 for state in path['cycle']))
        means = audit.cycle_means(market, path['cycle'], actions)
        self.assertEqual(means['consumerSurplus'], 10)
        self.assertEqual(means['profitA'], 0)
        self.assertEqual(means['profitB'], 9)

    def test_saved_weights_and_type7_known_values(self):
        self.assertEqual(audit.exact_float(.1), Fraction(3602879701896397, 36028797018963968))
        self.assertEqual(audit.type7([0., 10., 20., 30.], .25), 7.5)
        self.assertEqual(audit.type7([30., 0., 20., 10.], .75), 22.5)
        draws = audit.mulberry_indices(repeats=2)
        self.assertEqual(len(draws), 2)
        self.assertTrue(all(0 <= index < 12 for row in draws for index in row))

    def test_official_xoshiro_transition_jump_and_large_distance_are_independent(self):
        output, state = audit.xoshiro_step((1, 2, 3, 4))
        self.assertEqual(output, 11520)
        self.assertEqual(state, (7, 0, 1026, 12288))
        initial = (907001, 907002, 907003, 907004)
        at = initial
        for _ in range(137):
            _, at = audit.xoshiro_step(at)
        self.assertEqual(audit.advance_xoshiro(initial, 137), at)
        self.assertEqual(audit.advance_xoshiro(initial, 2**64), audit.xoshiro_jump(initial))
        streams, at = [], initial
        for _ in range(24):
            streams.append(at)
            at = audit.xoshiro_jump(at)
        self.assertEqual(len(set(streams)), 24)
        self.assertEqual(audit.advance_xoshiro(streams[0], 4_000_064),
                         audit.advance_xoshiro(audit.advance_xoshiro(streams[0], 4_000_000), 64))

    def test_exact_checkpoint_counts_and_unvisited_greedy_actions_are_distinct(self):
        counts = audit.read_le_array(struct.pack('<HHH', 65535, 0, 1), 'u16')
        overflow = audit.exact_counts(counts, [{'cell': 0, 'count': 70000}], 70001)
        states, actions = audit.visit_support(counts, overflow, [[0, 1], [0]], [0, 2, 3], bytes([1, 0]))
        self.assertEqual(states, bytes([1, 1]))
        self.assertEqual(actions, bytes([0, 1]))
        with self.assertRaises(ValueError):
            audit.exact_counts(counts, [{'cell': 1, 'count': 70000}], 70001)
        with self.assertRaises(ValueError):
            audit.exact_counts(counts, [{'cell': 0, 'count': 70000}, {'cell': 0, 'count': 70001}], 70001)
        self.assertEqual(list(audit.read_le_array(struct.pack('<dd', .1, -2.), 'f64')), [.1, -2.])

    def test_separate_python_short_replay_matches_primary_synthetic_updates(self):
        # Primary supplies synthetic witnesses, not research outcomes. The
        # independent checker imports none of its update/PRNG functions.
        module = (Path(__file__).resolve().parents[1]/'research/adaptive-learning.js').as_uri()
        raw = {'finite': game()}
        script = ('import {createLearners,controller,step} from '+json.dumps(module)+';'
                  'const raw='+json.dumps(raw)+';const out=[];'
                  'for(const initialization of ["zero","optimistic"]){'
                  'const m=createLearners(raw,controller("selected95",4),{T:2000,initialization,actorStates:[[1,2,3,4],[5,6,7,8]]});'
                  'const initial={step:m.t,phase:m.phase,previousIndices:m.previous.slice(),actorStates:m.actors.map(a=>a.slice())};'
                  'const values=m.q.map(q=>Array.from(q)),witnesses=[];for(let i=0;i<32;i++)witnesses.push(step(m,{trace:true}));'
                  'out.push({initial,values,witnesses,final:m.q.map(q=>Array.from(q)),actors:m.actors});}'
                  'console.log(JSON.stringify(out));')
        fixtures = json.loads(subprocess.run(['node', '--input-type=module', '-e', script], check=True,
                                            text=True, capture_output=True).stdout)
        controller = {'kind': 'periodic', 'period': 4}
        rows, offsets = audit.compact_rows(raw['finite'], controller)
        for fixture in fixtures:
            replay = audit.replay_updates(raw['finite'], controller, fixture['values'], rows, offsets,
                                          fixture['initial'], fixture['witnesses'], horizon=2000)
            self.assertEqual([list(actor) for actor in replay['q']], fixture['final'])
            self.assertEqual(replay['actorStates'], fixture['actors'])
            changed = copy.deepcopy(fixture['witnesses'])
            changed[3]['nextPhase'] = 1
            with self.assertRaises(ValueError):
                audit.replay_updates(raw['finite'], controller, fixture['values'], rows, offsets,
                                     fixture['initial'], changed, horizon=2000)


if __name__ == '__main__':
    unittest.main()
