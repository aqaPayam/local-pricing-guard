"""Complete artificial primary-kernel -> saved-file -> independent cross-audit."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid
from fractions import Fraction

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('learned_audit_fixtures',
                                            ROOT/'tests/test_learned_opponent_audit.py')
F = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = F
SPEC.loader.exec_module(F)
A = F.A


NODE_GENERATOR = r"""
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
const p=await import(process.argv[1]);
const project=process.argv[2],out=process.argv[3],focal=process.argv[4];
const supplied=JSON.parse(fs.readFileSync(path.join(project,'fixture-input.json'),'utf8'));
const read=ref=>fs.readFileSync(path.join(project,ref.file));
const meta=JSON.parse(read(supplied.metadata)),raw=JSON.parse(read(supplied.finiteGame));
const q=supplied.q.map(ref=>{const b=read(ref);return Array.from({length:b.length/8},(_,i)=>b.readDoubleLE(i*8));});
const counts=supplied.counts.map(ref=>{const b=read(ref);return Array.from({length:b.length/2},(_,i)=>b.readUInt16LE(i*2));});
const prepared=p.reconstructGreedy(raw.finite,meta.control,q,counts,meta.countOverflow,{expectedRounds:2000000});
const mdp=p.prepareMDP(raw,meta.control,prepared.worldPolicies,focal,prepared.supportCount);
const initial=meta.phase*mdp.n*mdp.n+meta.previousIndices[0]*mdp.n+meta.previousIndices[1];
const plan={id:supplied.oldRunID+'--focal'+focal,scenario:'base-g15-t1',seed:meta.seed,initialization:'zero',control:meta.control,focal,checkpointStep:2000000};
const solved=p.solveLoadedCase(plan,{mdp,start:initial,input:supplied},out);
const result={...solved.report,scientificAvailable:true,executionSucceeded:true};
process.stdout.write(JSON.stringify(result));
"""


class CompletePrimaryCrossAudit(unittest.TestCase):
    def test_actual_outer_process_and_pretermination_scientific_bundle(self):
        spec = importlib.util.spec_from_file_location('artificial_primary_process_runner',
                                                     ROOT/'research/run-learned-opponent.py')
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        local = ROOT/'.local'; local.mkdir(exist_ok=True)
        temporary = (local/('learned-process-cross-'+uuid.uuid4().hex)).resolve()
        temporary.mkdir()
        self.assertTrue(temporary.is_relative_to(local.resolve()))
        try:
            project, output = temporary/'project', temporary/'output'
            project.mkdir(); output.mkdir()
            supplied, expected, hashes, index = F.checkpoint_fixture(project)
            (output/'manifest.json').write_text(json.dumps({'inputHashes': hashes}), encoding='utf8')
            loaded = A.load_checkpoint_inputs(project, supplied, expected, hashes, index)
            for focal in ('A', 'B'):
                plan = next(row for row in A.planned_cases() if row['seed'] == 907001
                            and row['control']['id'] == 'selected95' and row['focal'] == focal)
                record = runner.execute_case(plan, output, project, mode='evidence',
                                             payload={'input': supplied}, budget_seconds=10)
                self.assertTrue(record['executionSucceeded'], record['failure'])
                A.audit_runtime(record, plan, supplied, output, expected_budget_seconds=10)
                self.assertTrue(A.audit_scientific_record(record, loaded, output)['scientificAvailable'])
                corrupt = copy.deepcopy(record)
                corrupt['runtime']['receivedCompleteMilliseconds'] = (
                    corrupt['runtime']['terminationRequestedMilliseconds']+1)
                with self.assertRaises(ValueError):
                    A.audit_runtime(corrupt, plan, supplied, output, expected_budget_seconds=10)
            # Actual case module writes all real-format progress and scientific
            # artifacts; only its enclosing artificial process then stalls.
            stalled = temporary/'after-complete.mjs'
            source = (ROOT/'research/learned-opponent-case.js').read_text(encoding='utf8')
            source = source.replace("'./learned-opponent-study.js'",
                                    json.dumps((ROOT/'research/learned-opponent-study.js').as_uri()))
            stalled.write_text(source+'\nwhile(true){}\n', encoding='utf8')
            late_output = temporary/'late'; late_output.mkdir()
            (late_output/'manifest.json').write_text(json.dumps({'inputHashes': hashes}), encoding='utf8')
            plan = next(row for row in A.planned_cases() if row['seed'] == 907001
                        and row['control']['id'] == 'selected95' and row['focal'] == 'A')
            late = runner.execute_case(plan, late_output, project, mode='evidence',
                                       payload={'input': supplied}, budget_seconds=2, case_source=stalled)
            self.assertFalse(late['executionSucceeded'])
            self.assertEqual(late['status'], 'retained hard-budget timeout')
            self.assertTrue(late['scientificAvailable'], json.dumps({
                'failure': late['failure'], 'runtime': late['runtime']}))
            A.audit_runtime(late, plan, supplied, late_output, expected_budget_seconds=2)
            self.assertTrue(A.audit_scientific_record(late, loaded, late_output)['scientificAvailable'])
        finally:
            if temporary.resolve().is_relative_to(local.resolve()):
                shutil.rmtree(temporary)

    def test_both_focals_complete_files_and_scientific_negative_controls(self):
        local = ROOT/'.local'; local.mkdir(exist_ok=True)
        temporary = (local/('learned-cross-'+uuid.uuid4().hex)).resolve()
        temporary.mkdir()
        self.assertTrue(temporary.is_relative_to(local.resolve()))
        try:
            project, output = temporary/'project', temporary/'output'
            project.mkdir(); output.mkdir()
            supplied, expected, hashes, index = F.checkpoint_fixture(project)
            (project/'fixture-input.json').write_text(json.dumps(supplied), encoding='utf8')
            loaded = A.load_checkpoint_inputs(project, supplied, expected, hashes, index)
            results = []
            for focal in ('A', 'B'):
                response = subprocess.run(['node', '--input-type=module', '-e', NODE_GENERATOR,
                                           (ROOT/'research/learned-opponent-study.js').as_uri(),
                                           str(project), str(output), focal],
                                          capture_output=True, check=True, text=True, timeout=60)
                record = json.loads(response.stdout)
                accepted = A.audit_scientific_record(record, loaded, output)
                self.assertTrue(accepted['scientificAvailable'])
                self.assertTrue(accepted['withinRequestedGap'])
                results.append(record)
            original = results[0]
            self.assertNotEqual(results[0]['baseline']['value'], results[1]['baseline']['value'])
            checks = []
            def changed(field, mutation):
                value = copy.deepcopy(original)
                mutation(value)
                checks.append((field, value))
            changed('residual', lambda r: r['certificate'].__setitem__('maximumResidualNumeratorHex', '0x12345'))
            changed('wrong upper factor', lambda r: r['certificate'].__setitem__(
                'upperValue', A.exact_hex(A.parse_hex(r['certificate']['upperValue'])*Fraction(19,20))))
            changed('witness ancillary', lambda r: r['certificate']['maximumWitness'].__setitem__(
                'payoffIndex', r['certificate']['maximumWitness']['payoffIndex'] ^ 1))
            changed('bool edge count', lambda r: r['certificate'].__setitem__('allEdgesChecked', True))
            changed('raw gain', lambda r: r['performance'].__setitem__('rawGain', A.exact_hex(Fraction(-3))))
            changed('gain sign', lambda r: r['performance'].__setitem__('rawGainSign', 'negative'))
            changed('possible baseline bound', lambda r: r['performance']['possibleGain'].__setitem__(
                'lower', A.exact_hex(Fraction(987))))
            changed('secondary CS', lambda r: r['performance'].__setitem__(
                'cycleCustomerBenefitDifference', A.exact_hex(Fraction(999))))
            changed('coverage exposure', lambda r: r['response']['coverage']['A']['discounted'].__setitem__(
                'unvisitedStateExposure', A.exact_hex(Fraction(1,2))))
            changed('terminal reset', lambda r: r['mdp']['terminal'].__setitem__('node', 0))
            for label, record in checks:
                with self.subTest(control=label), self.assertRaises(ValueError):
                    A.audit_scientific_record(record, loaded, output)
            # Artifact edits get fresh refs: failures must be semantic, not stale hashes.
            for label in ('path clock', 'path cycle', 'path support count', 'proposal quantization',
                          'candidate newline', 'off-path policy'):
                record = copy.deepcopy(original)
                if label.startswith('path'):
                    claim = record['response']; ref = claim['path']
                    value = json.loads((output/ref['file']).read_bytes())
                    if label == 'path clock': value['nextStates'][0] ^= 4
                    elif label == 'path cycle': value['closingState'] ^= 1
                    else: value['coverage']['B']['stateVisits'][0] += 1
                    data = (json.dumps(value)+'\n').encode()
                    target = claim; key = 'path'
                else:
                    target = record['optimizer']
                    key = {'proposal quantization': 'finalFloat64', 'candidate newline': 'dyadicValues',
                           'off-path policy': 'responsePolicy'}[label]
                    data = (output/target[key]['file']).read_bytes()
                    if label == 'proposal quantization':
                        import struct
                        data = struct.pack('<d', 1000.)+data[8:]
                    elif label == 'candidate newline': data = data[:-1]
                    else: data = data[:-1]+bytes([255])
                file = 'corrupt-'+str(label.replace(' ', '-'))+'.bin'
                (output/file).write_bytes(data)
                target[key] = {'file': file, 'bytes': len(data), 'sha256': A.digest(data)}
                with self.subTest(control=label), self.assertRaises(ValueError):
                    A.audit_scientific_record(record, loaded, output)
        finally:
            if temporary.resolve().is_relative_to(local.resolve()):
                shutil.rmtree(temporary)


if __name__ == '__main__':
    unittest.main()
