"""Full48 artificial processes and wrapper; no inherited numerical evidence.

Only the accepted-old-study premise gate is mocked. All NEW task/process,
checkpoint, Q, transition, path, Bellman, summary and retention checks execute.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT/file)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value
F = module('learned_inventory_artificial_fixtures', 'tests/test_learned_opponent_audit.py')
A = F.A
P = module('learned_inventory_primary_runner', 'research/run-learned-opponent.py')


class FullArtificialInventoryTests(unittest.TestCase):
    def setUp(self):
        self.local = (ROOT/'.local').resolve()
        self.local.mkdir(exist_ok=True)
        self.temporary = self.local/('learned-full-wrapper-'+uuid.uuid4().hex)
        self.temporary.mkdir()
        self.assertTrue(self.temporary.resolve().is_relative_to(self.local))

    def tearDown(self):
        target = self.temporary.resolve()
        self.assertTrue(target.is_relative_to(self.local))
        shutil.rmtree(target)

    def test_all48_actual_artificial_processes_and_full_audit_with_final_recheck(self):
        project, output = self.temporary/'project', self.temporary/'output'
        project.mkdir(); output.mkdir()
        inputs, hashes, old_index = {}, {}, {'records': []}
        for seed in range(907001, 907013):
            for controller in ('startup-only', 'selected95'):
                supplied, expected, declared, index = F.checkpoint_fixture(
                    project, seed=seed, controller=controller)
                inputs[supplied['oldRunID']] = supplied
                hashes.update(declared)
                old_index['records'].extend(index['records'])
        manifest = {'plan': {'cases': A.planned_cases()}, 'inputs': inputs, 'inputHashes': hashes}
        (output/'manifest.json').write_text(json.dumps(manifest)+'\n', encoding='utf8')
        context = {'manifest': manifest, 'manifestHash': A.file_digest(output/'manifest.json'),
                   'adaptiveIndex': old_index, 'priorArchivePresent': False}
        # This is not a reproduction of any old audit or its training. The
        # fixture directly supplies its artificial input premise, then runs all
        #48 new process/math/output checks without numerical mocking.
        with patch.object(P, 'verify', return_value=manifest), contextlib.redirect_stdout(io.StringIO()):
            primary = P.run(output, project)
        self.assertTrue(primary['primaryPassed'])
        self.assertEqual(primary['scientificallyAvailable'], 48)
        with patch.object(A, 'verify_study_dependencies', return_value=context):
            receipt = A.audit_study(output, project)
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['labels'], 48)
        self.assertEqual(receipt['certifiedRecords'], 48)
        self.assertEqual(receipt['checkpointNumericalReconstructions'], 24)
        self.assertEqual(receipt['worldStatesChecked'], 576)
        self.assertEqual(receipt['legalStateActionEdgesChecked'], 960)
        self.assertEqual(len(receipt['independentSummaries']['seedMeans']), 24)
        self.assertEqual(len(receipt['independentSummaries']['pairedDifferences']), 12)
        self.assertEqual(len(receipt['corruptionNegativeControls']), 19)
        self.assertTrue(all(receipt['corruptionNegativeControls'].values()))
        original = {name: (output/name).read_bytes() for name in
                    ('index.json', 'completion.json', 'journal.jsonl', 'results.json')}
        # Semantic completion corruption, with all independent wrapper checks.
        bad_completion = json.loads(original['completion.json'])
        bad_completion['primaryPassed'] = False
        (output/'completion.json').write_text(json.dumps(bad_completion)+'\n', encoding='utf8')
        with patch.object(A, 'verify_study_dependencies', return_value=context), self.assertRaises(ValueError):
            A.audit_study(output, project)
        (output/'completion.json').write_bytes(original['completion.json'])
        # A same-semantics output edit AFTER initial hash capture must be caught
        # by the final recheck, even though new scientific calculations agree.
        controls = A.scientific_negative_controls
        def edit_after_check(*args, **kwargs):
            result = controls(*args, **kwargs)
            with (output/'index.json').open('ab') as stream:
                stream.write(b' ')
            return result
        with patch.object(A, 'verify_study_dependencies', return_value=context), \
             patch.object(A, 'scientific_negative_controls', side_effect=edit_after_check), \
             self.assertRaisesRegex(ValueError, 'Output changed during audit'):
            A.audit_study(output, project)
        (output/'index.json').write_bytes(original['index.json'])

    def test_all48_unavailable_inventory_is_honest_and_existing_receipt_is_preserved(self):
        project, output = self.temporary/'project', self.temporary/'failed'
        project.mkdir(); output.mkdir()
        plans = A.planned_cases()
        manifest = {'plan': {'cases': plans}, 'inputs': {
            row['oldRunID']: {'inputRoot': 'artificial missing premise', 'oldRunID': row['oldRunID']}
            for row in plans}, 'inputHashes': {}}
        (output/'manifest.json').write_text(json.dumps(manifest)+'\n', encoding='utf8')
        def retained(plan, *args, **kwargs):
            return {**plan, 'status': 'retained worker failure', 'executionSucceeded': False,
                    'scientificAvailable': False, 'scientificUnavailableReason': 'Artificial runner failure',
                    'input': manifest['inputs'][plan['oldRunID']], 'mdp': None, 'optimizer': None,
                    'baseline': None, 'response': None, 'certificate': None, 'performance': None,
                    'runtime': {'events': [], 'caseSeconds': 0},
                    'failure': {'stage': 'runner', 'message': 'Artificial retained startup failure'}}
        with patch.object(P, 'verify', return_value=manifest), patch.object(P, 'execute_case', side_effect=retained), \
             contextlib.redirect_stdout(io.StringIO()):
            primary = P.run(output, project)
        self.assertFalse(primary['primaryPassed'])
        context = {'manifest': manifest, 'manifestHash': A.file_digest(output/'manifest.json'),
                   'adaptiveIndex': {'records': []}, 'priorArchivePresent': False}
        with patch.object(A, 'verify_study_dependencies', return_value=context):
            receipt = A.audit_study(output, project)
        self.assertTrue(receipt['passed'])
        self.assertFalse(receipt['primaryExecutionPassed'])
        self.assertEqual(receipt['certifiedRecords'], 0)
        self.assertEqual(receipt['unavailableRecords'], 48)
        self.assertFalse(receipt['actualScientificNegativeControlsAvailable'])
        self.assertEqual(len(receipt['corruptionNegativeControls']), 3)
        self.assertTrue(all(row['status'] == 'unavailable' for row in
                            receipt['independentSummaries']['pairedDifferences']))
        accepted = self.temporary/'accepted-receipt.json'
        accepted.write_bytes(b'prior accepted receipt\n')
        with patch.object(A, 'audit_study', side_effect=AssertionError('Must refuse before reading cases')), \
             contextlib.redirect_stdout(io.StringIO()):
            code = A.main(['--output', str(accepted)])
        self.assertEqual(code, 1)
        self.assertEqual(accepted.read_bytes(), b'prior accepted receipt\n')


if __name__ == '__main__':
    unittest.main()
