"""Actual independent process supervision on invented serialized evidence only."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import unittest
import uuid
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('reference_process_auditor',ROOT/'research/audit-guard-reference-study.py')
A=importlib.util.module_from_spec(SPEC)
exec(compile(Path(SPEC.origin).read_bytes(),str(SPEC.origin),'exec'),A.__dict__)


class ReplayProcessTests(unittest.TestCase):
    def setUp(self):
        self.directory=ROOT/'.local'/('guard-replay-process-invented-'+uuid.uuid4().hex)
        self.directory.mkdir(parents=True)

    def tearDown(self):
        self.assertEqual(self.directory.resolve().parent,(ROOT/'.local').resolve())
        self.assertTrue(self.directory.name.startswith('guard-replay-process-invented-'))
        shutil.rmtree(self.directory)

    def test_real_serialized_child_reexecution_and_every_field(self):
        generator="""
import fs from 'node:fs';import path from 'node:path';
import {createGuardReferenceLearners,evaluateGuardReference,summarizeGuardReferenceWindows,scientificTreatment} from './research/guard-reference-learning.js';
import {advanceTo} from './research/matched-clock-learning.js';
import {writeReferenceCheckpoint} from './research/guard-reference-io.js';
import {runtimeIdentity} from './research/matched-clock-study.js';
const directory=process.argv[1],record={finite:{prices:[1,2,3],capIndex:1,sets:[[0],[1],[1]],rewards:{profitA:[-2,0,1,3,-1,2,0,1,0],profitB:[1,-3,0,0,2,-1,4,0,1],consumerSurplus:[9,8,7,8,6,5,7,5,3]}}};
const m=createGuardReferenceLearners(record,{T:20000,seed:907001}),software=runtimeIdentity(),id='invented-independent-process';
const plan={id,arm:'startup',seed:907001,treatment:'full-grid-after-cap',scientificTreatment:scientificTreatment(),actors:m.actors.map(a=>a.slice())};
const finiteGameRef={file:'invented-original.json',bytes:0,sha256:'0'.repeat(64)};
const task={plan,record,finite:record.finite,originalTargets:[],scientificTreatment:scientificTreatment(),software,finiteGameRef,T:20000,checkpoints:[10000,20000]};
const run={...plan,checkpoints:[]};
for(const step of task.checkpoints){advanceTo(m,step);const metadata=writeReferenceCheckpoint(directory,m,{id,software,finiteGameRef,graph:evaluateGuardReference(m),windowMetrics:summarizeGuardReferenceWindows(m)});run.checkpoints.push({step,parentEligible:true,metadata});}
fs.writeFileSync(path.join(directory,'task.json'),JSON.stringify(task));fs.writeFileSync(path.join(directory,'record.json'),JSON.stringify(run));
"""
        node=shutil.which('node');self.assertIsNotNone(node)
        made=subprocess.run([node,'--input-type=module','-e',generator,str(self.directory)],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(made.returncode,0,made.stdout+made.stderr)
        task=self.directory/'task.json';record=self.directory/'record.json'
        before={p.relative_to(self.directory).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in self.directory.rglob('*') if p.is_file()}
        result=A.run_replay(node,ROOT,self.directory,task,record,30)
        self.assertTrue(result['fullHorizonReplayed']);self.assertTrue(result['allPlannedCheckpointsMatched'])
        self.assertEqual(result['replayedRounds'],20000);self.assertEqual(result['transcriptBlocksMatched'],2)
        self.assertTrue(result['finalConsumedIntegrityCheck']);self.assertTrue(result['rssSamples'])
        self.assertTrue(all(r['matched'] and len(r['corruptionNegativeControls'])==14 for r in result['checkpointResults']))
        after={p.relative_to(self.directory).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in self.directory.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_actual_owned_process_timeout_and_typed_integrity_failure(self):
        project=self.directory/'project';(project/'research').mkdir(parents=True)
        task=self.directory/'task.json';task.write_text(json.dumps(dict(checkpoints=[10000,20000])))
        record=self.directory/'record.json';record.write_text('{}')
        worker=project/'research/invented-process.js'
        with patch.object(A,'WORKER','research/invented-process.js'):
            worker.write_text('setInterval(()=>{},1000);')
            result=A.run_replay(shutil.which('node'),project,self.directory,task,record,.2)
            self.assertIn('deadline',result['operationalFailure'])
            self.assertFalse(result['fullHorizonReplayed']);self.assertEqual(result['replayedRounds'],0)
            worker.write_text("process.stdout.write(JSON.stringify({type:'replay failure',failureKind:'integrity',reason:'invented consumed drift'})+'\\n');process.exitCode=1;")
            with self.assertRaisesRegex(ValueError,'integrity failure'):
                A.run_replay(shutil.which('node'),project,self.directory,task,record,5)


if __name__=='__main__':unittest.main()
