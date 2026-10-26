"""Wholly artificial 24-slot orchestration fixtures; no inherited market/Q reads.

The complete inventory tests inject a fake inherited-premise verifier and fake
numerical child responses. They test the real authoritative wrapper, NOT new
training. Real serialization/reexecution is separately exercised by the Node
serialization suite and by the real outer-process test below.
"""
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('independent_matched',ROOT/'research/audit-matched-clock-study.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)


def save(root,name,value):
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
    b=value if isinstance(value,bytes) else (json.dumps(value,indent=2)+'\n').encode()
    path.write_bytes(b)
    return dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


class Fixture:
    def __init__(self,complete=True):
        self.project=ROOT/'.local'/('matched-inventory-'+str(uuid.uuid4()))
        self.project.mkdir(parents=True)
        self.directory=self.project/'study';self.directory.mkdir()
        runtime=A.node_runtime(ROOT,shutil.which('node'))
        self.raw=dict(scenario=dict(id='base-g15-t1'),finite=dict(prices=list(range(62))),originalTargets=[])
        finite=save(self.project,'invented-finite.json',self.raw)
        self.manifest=dict(schemaVersion=1,sourceHashes={},inputHashes={},inputs=dict(finiteGame=finite),
                           runtime=runtime['runtime'],parentRuntime=A.python_runtime(),
                           plan=dict(runs=A.planned_runs(runtime['actors']),T=2_000_000,checkpoints=[1_000_000,2_000_000],hardCaseSeconds=600))
        save(self.directory,'manifest.json',self.manifest)
        for name in (A.SELF,A.WORKER,A.CORE):
            save(self.project,name,('invented wrapper source '+name).encode())
        self.mh=A.digest(self.directory/'manifest.json')
        self.dependency=dict(passed=True,studyManifestHash=self.mh,manifest=self.manifest)
        self.records=[];self.index=[];self.journal=[];self.responses={}
        for p in self.manifest['plan']['runs']:
            checkpoints=[];events=[]
            if complete:
                for step in [1_000_000,2_000_000]:
                    prefix=f"checkpoints/{p['id']}/{step}/"
                    q=save(self.directory,prefix+'invented-q.bin',b'12345678');q['rawBytes']=8
                    counts=save(self.directory,prefix+'invented-count.bin',b'1234');counts['rawBytes']=4
                    policy=save(self.directory,prefix+'invented-policy.bin',b'\x00')
                    graph=save(self.directory,prefix+'invented-graph.json',dict(scope='mock replay fixture, no numerical claim'))
                    meta=save(self.directory,prefix+'metadata.json',dict(artifacts=dict(q=[q],counts=[counts]),policies=dict(own=[policy],world=[policy]),graph=graph))
                    seq=len(events)
                    for kind,fields in [('process line received',{}),('checkpoint received',dict(step=step,metadata=meta)),('checkpoint validated',dict(step=step,metadata=meta))]:
                        events.append(dict(sequence=len(events),type=kind,elapsedMilliseconds=len(events)+1,at='invented',**fields))
                    checkpoints.append(dict(step=step,metadata=meta,parentEligible=True,receivedSequence=seq,validatedSequence=seq+2,scientificAvailable=False,reason='Pending independent replay'))
                for kind,fields in [('done received',{}),('process exited',dict(exitCode=0)),('supervision closed',{})]:
                    events.append(dict(sequence=len(events),type=kind,elapsedMilliseconds=len(events)+1,at='invented',**fields))
                task=dict(plan=p,record=self.raw,finite=self.raw['finite'],originalTargets=[],finiteGameRef=finite,software=self.manifest['runtime'],T=2_000_000,checkpoints=[1_000_000,2_000_000],manifestSha256=self.mh,executionMode='frozen-primary',projectRoot='.')
                taskref=save(self.directory,'tasks/'+p['id']+'.json',task)
                record=dict(id=p['id'],arm=p['arm'],seed=p['seed'],manifestSha256=self.mh,status='completed',executionSucceeded=True,
                            checkpoints=checkpoints,events=events,task=taskref,parentRuntime=A.python_runtime(),failure=None,rssSamples=[],budgetSeconds=600,precaseSeconds=0,wholeCaseSeconds=1,seconds=1)
            else:
                record=dict(id=p['id'],arm=p['arm'],seed=p['seed'],manifestSha256=self.mh,status='input failure',executionSucceeded=False,
                            checkpoints=[dict(step=s,metadata=None,parentEligible=False,scientificAvailable=False,reason='Invented input failure') for s in [1_000_000,2_000_000]],
                            events=[],failure=dict(message='Invented precase failure'),rssSamples=[])
            self.records.append(record)
            self.responses[p['id']]=self.response(p,record)
        self.save_closed()

    def response(self,p,r):
        controls=[dict(test='invented numerical response '+str(i),rejected=True) for i in range(11)]
        out=[]
        for cp in r['checkpoints']:
            if cp['parentEligible']:
                cs=10+(p['seed']-907001)+(2 if p['arm']=='recurring4' else 0)
                out.append(dict(step=cp['step'],parentEligible=True,matched=True,available=True,metadataSha256=cp['metadata']['sha256'],
                                graphSha256='a'*64,reason=None,phase=4,previousIndices=[1,2],cycleLength=4,
                                cycleCustomerBenefit=dict(numerator=str(cs),denominator='1',approximate=cs),corruptionNegativeControls=controls))
        return dict(id=p['id'],replayedRounds=2_000_000 if out else 0,fullHorizonReplayed=bool(out),checkpointResults=out,
                    allPlannedCheckpointsMatched=bool(out),allEligibleCheckpointsMatched=True,finalConsumedIntegrityCheck=True,nodeProcessRSSBytes=1024)

    def save_closed(self):
        self.index=[];self.journal=[]
        for r in self.records:
            ref=save(self.directory,'records/'+r['id']+'.json',r)
            self.index.append(dict(id=r['id'],**ref,status=r['status']))
            self.journal.extend([dict(at='invented',type='run started',id=r['id']),dict(at='invented',type='run retained',id=r['id'],record=ref,status=r['status'])])
        self.journal.append(dict(at='invented',type='inventory completed',retainedRuns=24,finalFrozenDependencyCheck=dict(passed=True,checkedAt='invented',failure=None)))
        save(self.directory,'journal.jsonl',b''.join((json.dumps(x)+'\n').encode() for x in self.journal))
        save(self.directory,'results.json',dict(manifestSha256=self.mh,records=self.records))
        save(self.directory,'index.json',dict(manifestSha256=self.mh,records=self.index))
        gate=save(self.project,'invented-admin.json',dict(passed=True,studyManifestHash=self.mh,sourcesVerified=True,inputsVerified=True,auditorSourceHash=A.digest(self.project/A.SELF),controlAuditorSourceHash=A.digest(self.project/A.WORKER),replayCoreSourceHash=A.digest(self.project/A.CORE)))
        save(self.directory,'execution-start.json',dict(manifestSha256=self.mh,software=self.manifest['runtime'],runIds=[r['id'] for r in self.records],adminGateSha256=gate['sha256'],adminGate=gate))
        eligible=sum(cp['parentEligible'] for r in self.records for cp in r['checkpoints'])
        failed=sum(not r['executionSucceeded'] for r in self.records)
        # Exclude the previous completion on fixture edits, as the real runner does.
        stored=sum(p.stat().st_size for p in self.directory.rglob('*') if p.is_file() and p.name!='completion.json')
        value=dict(manifestSha256=self.mh,parentRuntime=A.python_runtime(),executionStartSha256=A.digest(self.directory/'execution-start.json'),
                   journalSha256=A.digest(self.directory/'journal.jsonl'),resultsSha256=A.digest(self.directory/'results.json'),indexSha256=A.digest(self.directory/'index.json'),
                   inventoryComplete=True,retainedRuns=24,retainedCheckpointSlots=48,fullTrainingReplay=False,finalFrozenDependencyCheck=self.journal[-1]['finalFrozenDependencyCheck'],
                   executionFailures=failed,budgetFailures=sum(r['status']=='timeout' for r in self.records),primaryPassed=failed==0,parentEligibleCheckpoints=eligible,
                   resources=dict(rawEquivalentEligibleCheckpointBytes=eligible*12,storedBytesBeforeCompletion=stored,largestSampledNodeProcessRSSBytes=None,
                                  largestApproximatelyPairedRSSBytes=None,pairedRSSUnavailableReason='Invented no-sample fixture',eligibleCompressedDenseBytes=eligible*12,
                                  rawEquivalentOutputBytesBeforeCompletion=stored if eligible==48 else None,rawEquivalentOutputSoftTargetExceeded=stored>1_750_000_000 if eligible==48 else None,
                                  sampledPairedRSSSoftTargetExceeded=None,seconds=1,primarySecondsSoftTargetExceeded=False))
        save(self.directory,'completion.json',value)

    def run(self,runner=None):
        def replay(node,project,directory,task_file,record_file,budget):
            r=A.parse(Path(record_file).read_bytes())
            return copy.deepcopy(self.responses[r['id']])
        return A.audit_study(self.project,self.directory,dependency_verifier=lambda *_:self.dependency,replay_runner=runner or replay)

    def close(self):
        target=self.project.resolve()
        assert target.parent== (ROOT/'.local').resolve() and target.name.startswith('matched-inventory-')
        shutil.rmtree(target)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture()

    def tearDown(self):
        self.f.close()

    def test_complete24_inventory48_slots_exact_mean_and_root_aggregator(self):
        result=self.f.run()
        self.assertTrue(result['passed']);self.assertTrue(result['fullTrainingReplay'])
        self.assertEqual(result['replayedRounds'],48_000_000)
        self.assertEqual(result['scientificallyAvailableCheckpoints'],48)
        self.assertEqual(result['independentSummaries']['primarySummary']['meanDifference'],dict(numerator='2',denominator='1'))
        spec=importlib.util.spec_from_file_location('matched_root_analysis',ROOT/'research/matched-clock-analysis.py')
        other=importlib.util.module_from_spec(spec);spec.loader.exec_module(other)
        self.assertEqual(result['independentSummaries'],other.aggregate(result['finalEndpoints']))

    def test_bad_secondary_retains_every_final_and_primary_mean_but_not_full_replay(self):
        r=self.f.responses[self.f.records[0]['id']]
        r['checkpointResults'][0]=dict(step=1_000_000,parentEligible=True,matched=False,available=False,reason='Invented secondary bit mismatch')
        r['allPlannedCheckpointsMatched']=False
        result=self.f.run()
        self.assertEqual(result['finalAvailable'],24);self.assertFalse(result['fullTrainingReplay'])
        self.assertTrue(result['independentSummaries']['primarySummary']['available'])

    def test_bad_final_nulls_planned_mean_without_selective_seed_exclusion(self):
        r=self.f.responses[self.f.records[-1]['id']]
        r['checkpointResults'][1]=dict(step=2_000_000,parentEligible=True,matched=False,available=False,reason='Invented final mismatch')
        r['allPlannedCheckpointsMatched']=False
        result=self.f.run()
        self.assertEqual(len(result['independentSummaries']['pairedRows']),12)
        self.assertIsNone(result['independentSummaries']['primarySummary']['meanDifference'])
        self.assertEqual(result['independentSummaries']['completePairDescription']['denominator'],11)

    def test_operational_replay_failure_retains_unavailable_case_and_runs_later23(self):
        seen=[]
        def replay(node,project,directory,task_file,record_file,budget):
            record=A.parse(Path(record_file).read_bytes());seen.append(record['id'])
            if len(seen)==1:
                return dict(operationalFailure='Invented owned process crash',replayedRounds=0,fullHorizonReplayed=False,allPlannedCheckpointsMatched=False,checkpointResults=[])
            return copy.deepcopy(self.f.responses[record['id']])
        result=self.f.run(replay)
        self.assertEqual(len(seen),24);self.assertEqual(result['finalAvailable'],23)
        self.assertIsNone(result['independentSummaries']['primarySummary']['meanDifference'])

    def test_output_drift_after_provisional_good_endpoint_is_global_fatal(self):
        def replay(node,project,directory,task_file,record_file,budget):
            r=A.parse(Path(record_file).read_bytes())
            if r['id']==self.f.records[-1]['id']:
                with (self.f.directory/'records'/ (self.f.records[0]['id']+'.json')).open('ab') as out:out.write(b' ')
            return copy.deepcopy(self.f.responses[r['id']])
        with self.assertRaisesRegex(ValueError,'Global primary output integrity'):
            self.f.run(replay)

    def test_late_clock_boolean_and_receipt_chronology_corruptions(self):
        original=copy.deepcopy(self.f.records[0])
        for mutation in [lambda r:r['events'][2].update(elapsedMilliseconds=600001),
                         lambda r:r['checkpoints'][0].update(step=True),
                         lambda r:r['checkpoints'][0].update(validatedSequence=0),
                         lambda r:r['events'][0].update(type='process exited',exitCode=0),
                         lambda r:r['events'][2].update(metadata=dict(file='wrong',bytes=1,sha256='c'*64))]:
            r=copy.deepcopy(original);mutation(r)
            with self.assertRaises(ValueError):A.audit_events(r,[1_000_000,2_000_000])

    def test_fixed_task_model_override_rejected_despite_fresh_all_record_hashes(self):
        ref=self.f.records[0]['task'];task=A.parse((self.f.directory/ref['file']).read_bytes())
        task['originalTargets']=[dict(invented='hidden target')]
        self.f.records[0]['task']=save(self.f.directory,ref['file'],task)
        self.f.save_closed()
        with self.assertRaisesRegex(ValueError,'fixed-model task'):
            self.f.run()

    def test_existing_receipt_never_overwritten(self):
        p=self.f.project/'closed.json';p.write_bytes(b'closed exact bytes')
        before=A.digest(p)
        with self.assertRaises(ValueError):A.write_exclusive(p,dict(passed=True))
        self.assertEqual(A.digest(p),before)


class UnavailableTests(unittest.TestCase):
    def test_source_dependency_lexer_does_not_execute_fixture_import_text(self):
        text="""// import './comment.js';
/* export * from './block.js'; */
const fake = "import './b.js'; export * from './c.js';";
const script = `import './template.js';`;
import x from './real-a.js';import './real-b.js';
export {x} from './real-c.js';
"""
        self.assertEqual(A.javascript_imports(text),['./real-a.js','./real-b.js','./real-c.js'])

    def test_independent_administrative_closure_all_legacy_maps_and_snapshot_failures(self):
        f=Fixture(False)
        try:
            project,directory=f.project,f.directory
            source_hashes={}
            for name in A.REQUIRED:
                ref=save(project,name,('invented administrative source '+name).encode());source_hashes[name]=ref['sha256']
                save(directory,'sources/'+name,(project/name).read_bytes())
            base='research/sparse-display-results/'
            child=save(project,'legacy/declared-source.txt',b'closed toy legacy dependency')
            legacy4=save(project,'legacy/four/manifest.json',dict(sources={child['file']:child['sha256']}))
            legacy3=save(project,'legacy/three/manifest.json',dict(hashes={legacy4['file']:legacy4['sha256']}))
            legacy2=save(project,'legacy/two/manifest.json',dict(inputHashes={legacy3['file']:legacy3['sha256']}))
            inherited=save(project,base+'manifest.json',dict(sourceHashes={legacy2['file']:legacy2['sha256']}))
            finite=save(project,base+'cases/invented.json',f.raw)
            index=save(project,base+'index.json',dict(manifestSha256=inherited['sha256'],cases=[dict(scenario='base-g15-t1',status='completed',file='cases/invented.json',sha256=finite['sha256'])]))
            refs=[child,legacy4,legacy3,legacy2,inherited,finite,index]
            for receipt,source in [('independent-audit.json','research/audit-sparse-display.js'),('rational-audit.json','research/audit-sparse-reset.py')]:
                sr=save(project,source,b'invented accepted toy premise source');refs.append(sr)
                refs.append(save(project,base+receipt,dict(passed=True,studyManifestHash=inherited['sha256'],indexSha256=index['sha256'],auditorSourceHash=sr['sha256'])))
            benchmark=save(project,'invented-benchmark.json',dict(passed=True,artificial=True,n=62,roundsPerArm=2_000_000,fullIndependentReplay=True,
                             arms=[dict(arm=a,passed=True) for a in A.ARMS],sourcesUnchanged=True,sourceHashes=source_hashes,finalSourceHashes=source_hashes,artifacts=[]))
            refs.append(benchmark)
            # Artificial accepted-old anchor: the production constants themselves
            # stay fixed; only this test substitutes a tiny prior inventory.
            old_plan=save(project,'invented-prior-plan.json',dict(files={r['file']:dict(bytes=r['bytes'],sha256=r['sha256']) for r in refs if r is not benchmark}))
            old_receipt=save(project,'invented-prior-receipt.json',dict(sha256='e'*64,prospectiveInventorySha256=old_plan['sha256'],verification=dict(passed=True)))
            anchor=dict(planFile=old_plan['file'],planSha256=old_plan['sha256'],receiptFile=old_receipt['file'],receiptSha256=old_receipt['sha256'],archiveSha256='e'*64)
            refs.extend([old_plan,old_receipt])
            m=copy.deepcopy(f.manifest);m.update(sourceHashes=source_hashes,inputHashes={r['file']:r['sha256'] for r in refs},inputs=dict(finiteGame=finite),benchmark=dict(file=benchmark['file'],sha256=benchmark['sha256']))
            m['plan'].update(retainedRuns=24,alpha=.1,gamma=19/20,initialization='positive-zero',clock='0->1->2->3->4->1',
                             transcript=dict(bytesPerRound=120,roundsPerBlock=10000,completeBlocksPerRun=200),
                             softResourceTargets=dict(primarySeconds=3600,replaySeconds=3600,sampledRSSBytes=512000000,newRawEquivalentBytes=1750000000))
            save(directory,'manifest.json',m)
            # Only the executable query is substituted; every artifact/closure/
            # snapshot/plan/benchmark check runs through the real admin adapter.
            runtime=A.node_runtime(ROOT,shutil.which('node'))
            with patch.object(A,'node_runtime',return_value=runtime),patch.object(A,'OLD_ANCHOR',anchor):
                report=A.verify_dependencies(project,directory,shutil.which('node'))
                self.assertTrue(report['passed']);self.assertIn('no Q decode',report['scope'])
                old_child=(project/child['file']).read_bytes()
                (project/child['file']).write_bytes(b'self-consistently rehashed invented old input')
                new_bound={**m['sourceHashes'],**m['inputHashes'],child['file']:A.digest(project/child['file'])}
                with self.assertRaisesRegex(ValueError,'fixed accepted V11'):
                    A.verify_old_anchor(project,new_bound,m['sourceHashes'],[child['file']])
                (project/child['file']).write_bytes(old_child)
                old=(directory/'sources'/A.CORE).read_bytes()
                (directory/'sources'/A.CORE).write_bytes(b'fresh corrupted snapshot')
                with self.assertRaisesRegex(ValueError,'snapshot differs'):A.verify_dependencies(project,directory,shutil.which('node'))
                (directory/'sources'/A.CORE).write_bytes(old)
                wrong=copy.deepcopy(m);wrong['inputHashes'].pop(child['file']);save(directory,'manifest.json',wrong)
                with self.assertRaisesRegex(ValueError,'transitive dependency omitted'):A.verify_dependencies(project,directory,shutil.which('node'))
                wrong=copy.deepcopy(m);wrong['sourceHashes'].pop('tests/test_matched_clock_inventory_audit.py');save(directory,'manifest.json',wrong)
                with self.assertRaisesRegex(ValueError,'sources or tests omitted'):A.verify_dependencies(project,directory,shutil.which('node'))
        finally:f.close()

    def test_real_outer_process_complete_primary_serialization_and_full_independent_replay(self):
        directory=ROOT/'.local'/('matched-outer-'+str(uuid.uuid4()));directory.mkdir(parents=True)
        try:
            script=directory/'invented-generator.mjs'
            uri=lambda name:(ROOT/name).as_uri()
            script.write_text(f"""
import fs from 'node:fs';
import {{createLearners,advanceTo,actorNamespaces}} from {json.dumps(uri('research/matched-clock-learning.js'))};
import {{evaluateFrozen,summarizeWindows}} from {json.dumps(uri('research/matched-clock-graph.js'))};
import {{writeCheckpoint}} from {json.dumps(uri('research/matched-clock-io.js'))};
const dir={json.dumps(str(directory))},raw={{finite:{{prices:[1,2,3],capIndex:1,sets:[[0,1],[0,1,2],[1,2]],upper:[1,2,2],rewards:{{profitA:[0,1,4,5,6,9,10,11,12],profitB:[7,2,3,1,4,8,5,6,9],consumerSurplus:[9,8,7,8,7,6,7,6,5]}}}},originalTargets:[]}};
const finiteGameRef={{file:'invented-source',bytes:1,sha256:'a'.repeat(64)}},software={{scope:'invented outer-process fixture'}};
for(const arm of ['startup','recurring4']){{
const plan={{id:'invented-'+arm,arm,seed:907001,actors:actorNamespaces()[0].actors}},task={{plan,finite:raw.finite,originalTargets:[],finiteGameRef,software,T:20000,checkpoints:[10000,20000]}};
const m=createLearners(raw,arm,{{T:20000}}),checkpoints=[];
for(const step of task.checkpoints){{advanceTo(m,step);checkpoints.push({{step,parentEligible:true,metadata:writeCheckpoint(dir,m,{{id:plan.id,software,finiteGameRef,graph:evaluateFrozen(m),windowMetrics:summarizeWindows(m)}})}});}}
fs.writeFileSync(dir+'/'+arm+'-task.json',JSON.stringify(task));fs.writeFileSync(dir+'/'+arm+'-record.json',JSON.stringify({{...plan,checkpoints}}));
}}
""",encoding='utf-8')
            generated=subprocess.run([shutil.which('node'),str(script)],cwd=ROOT,capture_output=True,timeout=30)
            self.assertEqual(generated.returncode,0,generated.stderr.decode())
            for arm in ['startup','recurring4']:
                result=A.run_replay(shutil.which('node'),ROOT,directory,directory/(arm+'-task.json'),directory/(arm+'-record.json'),30)
                self.assertNotIn('operationalFailure',result)
                self.assertTrue(result['allPlannedCheckpointsMatched']);self.assertTrue(result['fullHorizonReplayed'])
                self.assertEqual(result['replayedRounds'],20000)
                self.assertEqual(len(result['checkpointResults'][0]['corruptionNegativeControls']),11)
                self.assertGreater(len(result['rssSamples']),0)
        finally:
            assert directory.parent.resolve()==(ROOT/'.local').resolve() and directory.name.startswith('matched-outer-')
            shutil.rmtree(directory)

    def test_all24_precase_failures_accepted_as_inventory_not_science(self):
        f=Fixture(False)
        try:
            r=f.run();self.assertTrue(r['passed']);self.assertFalse(r['executionPassed'])
            self.assertEqual(r['replayedRounds'],0);self.assertEqual(r['finalAvailable'],0)
            self.assertFalse(r['actualScientificNegativeControlsAvailable'])
            self.assertEqual(len(r['independentSummaries']['pairedRows']),12)
            self.assertIsNone(r['independentSummaries']['primarySummary']['meanDifference'])
        finally:f.close()

    def test_real_independent_process_watchdog_and_continuation(self):
        root=ROOT/'.local'/('matched-watchdog-'+str(uuid.uuid4()));root.mkdir(parents=True)
        try:
            worker=root/'research/replay-matched-clock.js';worker.parent.mkdir()
            worker.write_text('for(;;){}',encoding='utf-8')
            r=A.run_replay(shutil.which('node'),root,root,root/'unused-task',root/'unused-record',.15)
            self.assertIn('deadline',r['operationalFailure']);self.assertFalse(r['fullHorizonReplayed'])
            self.assertIsInstance(r['rssSamples'],list)
            self.assertIn('not a continuous',r['resourceSamplingScope'])
            worker.write_text("process.stdout.write(JSON.stringify({type:'replay failure',failureKind:'integrity',reason:'Consumed artifact changed during replay'})+'\\n');process.exitCode=1;",encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'consumed-artifact integrity'):
                A.run_replay(shutil.which('node'),root,root,root/'unused',root/'unused',2)
            worker.write_text("process.stdout.write('not JSON\\n');process.exitCode=7;",encoding='utf-8')
            malformed=A.run_replay(shutil.which('node'),root,root,root/'unused',root/'unused',2)
            self.assertIn('output failure',malformed['operationalFailure'])
            task=root/'toy-task.json';task.write_text(json.dumps(dict(checkpoints=[10000,20000])),encoding='utf-8')
            worker.write_text("process.stdout.write(JSON.stringify({type:'checkpoint audited',result:{step:10000,parentEligible:true,matched:false,available:false}})+'\\n');for(;;){}",encoding='utf-8')
            partial=A.run_replay(shutil.which('node'),root,root,task,root/'unused',.25)
            self.assertEqual(partial['replayedRounds'],10000)
            self.assertEqual(partial['checkpointResults'],[])
            self.assertIn('lower bound',partial['countScope'])
        finally:
            assert root.parent.resolve()==(ROOT/'.local').resolve() and root.name.startswith('matched-watchdog-')
            shutil.rmtree(root)


if __name__=='__main__':unittest.main()
