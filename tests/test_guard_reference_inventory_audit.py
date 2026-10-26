"""Wholly artificial12-run/24-slot orchestration fixtures; no inherited market/Q reads.

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
spec=importlib.util.spec_from_file_location('independent_reference',ROOT/'research/audit-guard-reference-study.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)


def save(root,name,value):
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
    b=value if isinstance(value,bytes) else (json.dumps(value,indent=2)+'\n').encode()
    path.write_bytes(b)
    return dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


class Fixture:
    def __init__(self,complete=True):
        self.anchors_available=True
        self.project=ROOT/'.local'/('guard-inventory-'+str(uuid.uuid4()))
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
        self.dependency=dict(passed=True,studyManifestHash=self.mh,manifest=self.manifest,oldComparisonEndpoints=[dict(seed=seed,arm='startup',runId=f'base-g15-t1--matched5-startup--zero--s{seed}',executionSucceeded=True,available=True,replayMatched=True,cycleCustomerBenefit=dict(numerator=str(10+seed-907001),denominator='1'),step=2000000,nextPhase=4,previousIndices=[1,2],cycleLength=4,checkpointSha256='b'*64,graphSha256='c'*64,unavailableReason=None) for seed in A.SEEDS],acceptedOldComparison=dict(scope='Invented injected accepted-old-premise fixture'))
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
                task=dict(plan=p,scientificTreatment=A.SCIENTIFIC_TREATMENT,record=self.raw,finite=self.raw['finite'],originalTargets=[],finiteGameRef=finite,software=self.manifest['runtime'],T=2_000_000,checkpoints=[1_000_000,2_000_000],manifestSha256=self.mh,executionMode='frozen-primary',projectRoot='.')
                taskref=save(self.directory,'tasks/'+p['id']+'.json',task)
                record=dict(id=p['id'],arm=p['arm'],seed=p['seed'],treatment=p['treatment'],scientificTreatment=p['scientificTreatment'],manifestSha256=self.mh,status='completed',executionSucceeded=True,
                            checkpoints=checkpoints,events=events,task=taskref,parentRuntime=A.python_runtime(),failure=None,rssSamples=[],budgetSeconds=600,precaseSeconds=0,wholeCaseSeconds=1,seconds=1)
            else:
                record=dict(id=p['id'],arm=p['arm'],seed=p['seed'],treatment=p['treatment'],scientificTreatment=p['scientificTreatment'],manifestSha256=self.mh,status='input failure',executionSucceeded=False,
                            checkpoints=[dict(step=s,metadata=None,parentEligible=False,scientificAvailable=False,reason='Invented input failure') for s in [1_000_000,2_000_000]],
                            events=[],failure=dict(message='Invented precase failure'),rssSamples=[])
            self.records.append(record)
            self.responses[p['id']]=self.response(p,record)
        self.save_closed()

    def response(self,p,r):
        controls=[dict(test='invented numerical response '+str(i),rejected=True) for i in range(14)]
        out=[]
        for cp in r['checkpoints']:
            if cp['parentEligible']:
                cs=12+(p['seed']-907001)
                out.append(dict(step=cp['step'],parentEligible=True,matched=True,available=True,metadataSha256=cp['metadata']['sha256'],
                                graphSha256='a'*64,reason=None,phase=4,previousIndices=[1,2],cycleLength=4,
                                cycleCustomerBenefit=dict(numerator=str(cs),denominator='1',approximate=cs),corruptionNegativeControls=controls))
        return dict(id=p['id'],transcriptBlocksMatched=200 if out else 0,replayedRounds=2_000_000 if out else 0,fullHorizonReplayed=bool(out),checkpointResults=out,
                    allPlannedCheckpointsMatched=bool(out),allEligibleCheckpointsMatched=True,finalConsumedIntegrityCheck=True,nodeProcessRSSBytes=1024)

    def save_closed(self):
        self.index=[];self.journal=[]
        for r in self.records:
            ref=save(self.directory,'records/'+r['id']+'.json',r)
            self.index.append(dict(id=r['id'],**ref,status=r['status']))
            self.journal.extend([dict(at='invented',type='run started',id=r['id']),dict(at='invented',type='run retained',id=r['id'],record=ref,status=r['status'])])
        self.journal.append(dict(at='invented',type='inventory completed',retainedRuns=12,finalFrozenDependencyCheck=dict(passed=True,checkedAt='invented',failure=None)))
        save(self.directory,'journal.jsonl',b''.join((json.dumps(x)+'\n').encode() for x in self.journal))
        anchors=save(self.directory,'stage-anchors.json',dict(scope='Invented mocked anchor fixture; numerical anchors independently tested elsewhere')) if self.anchors_available else None
        failure=None if anchors else dict(message='Invented retained anchor calculation failure')
        self.journal.insert(0,dict(at='invented',type='static anchors retained',reference=anchors) if anchors else dict(at='invented',type='static anchors unavailable',failure=failure))
        save(self.directory,'journal.jsonl',b''.join((json.dumps(x)+'\n').encode() for x in self.journal))
        save(self.directory,'results.json',dict(manifestSha256=self.mh,records=self.records,stageAnchors=anchors,stageAnchorsFailure=failure))
        save(self.directory,'index.json',dict(manifestSha256=self.mh,records=self.index))
        gate=save(self.project,'invented-admin.json',dict(passed=True,studyManifestHash=self.mh,sourcesVerified=True,inputsVerified=True,auditorSourceHash=A.digest(self.project/A.SELF),controlAuditorSourceHash=A.digest(self.project/A.WORKER),replayCoreSourceHash=A.digest(self.project/A.CORE)))
        save(self.directory,'execution-start.json',dict(manifestSha256=self.mh,software=self.manifest['runtime'],runIds=[r['id'] for r in self.records],adminGateSha256=gate['sha256'],adminGate=gate))
        eligible=sum(cp['parentEligible'] for r in self.records for cp in r['checkpoints'])
        failed=sum(not r['executionSucceeded'] for r in self.records)
        # Exclude the previous completion on fixture edits, as the real runner does.
        stored=sum(p.stat().st_size for p in self.directory.rglob('*') if p.is_file() and p.name!='completion.json')
        value=dict(manifestSha256=self.mh,parentRuntime=A.python_runtime(),executionStartSha256=A.digest(self.directory/'execution-start.json'),
                   journalSha256=A.digest(self.directory/'journal.jsonl'),resultsSha256=A.digest(self.directory/'results.json'),indexSha256=A.digest(self.directory/'index.json'),
                   stageAnchorsSha256=anchors['sha256'] if anchors else None,stageAnchorsFailure=failure,anchorCalculationPassed=self.anchors_available,inventoryComplete=True,retainedRuns=12,retainedCheckpointSlots=24,fullTrainingReplay=False,finalFrozenDependencyCheck=self.journal[-1]['finalFrozenDependencyCheck'],
                   executionFailures=failed,executionPassed=failed==0,budgetFailures=sum(r['status']=='timeout' for r in self.records),primaryPassed=failed==0 and self.anchors_available,parentEligibleCheckpoints=eligible,
                   resources=dict(rawEquivalentEligibleCheckpointBytes=eligible*12,storedBytesBeforeCompletion=stored,largestSampledNodeProcessRSSBytes=None,
                                  largestApproximatelyPairedRSSBytes=None,pairedRSSUnavailableReason='Invented no-sample fixture',eligibleCompressedDenseBytes=eligible*12,
                                  rawEquivalentOutputBytesBeforeCompletion=stored if eligible==24 else None,rawEquivalentOutputSoftTargetExceeded=stored>1_000_000_000 if eligible==24 else None,
                                  sampledPairedRSSSoftTargetExceeded=None,seconds=1,primarySecondsSoftTargetExceeded=False))
        save(self.directory,'completion.json',value)

    def run(self,runner=None):
        def replay(node,project,directory,task_file,record_file,budget):
            r=A.parse(Path(record_file).read_bytes())
            return copy.deepcopy(self.responses[r['id']])
        with patch.object(A,'check_anchors',side_effect=lambda node,project,raw,primary:primary):
            return A.audit_study(self.project,self.directory,dependency_verifier=lambda *_:self.dependency,replay_runner=runner or replay)

    def close(self):
        target=self.project.resolve()
        assert target.parent== (ROOT/'.local').resolve() and target.name.startswith('guard-inventory-')
        shutil.rmtree(target)


class MetadataPlanCrossSchemaTests(unittest.TestCase):
    def test_entire_independent_plan_matches_actual_primary_metadata_only_cli(self):
        node=shutil.which('node');self.assertIsNotNone(node)
        # These are real source-only metadata entry points. They neither load
        # a numerical game/Q checkpoint nor construct or advance a learner.
        response=subprocess.run([node,str(ROOT/'research/guard-reference-study.js'),'plan'],cwd=ROOT,
                                capture_output=True,text=True,timeout=30,check=True)
        primary=A.parse(response.stdout)
        runtime=A.node_runtime(ROOT,node)
        independent=A.planned_runs(runtime['actors'])
        A.same(primary,independent,'Complete primary/independent plan schema')
        self.assertEqual(len(independent),12)
        for i,p in enumerate(independent):
            self.assertEqual(set(p),{'id','scenario','arm','seed','initialization','actors','segments','treatment','scientificTreatment'})
            self.assertEqual(p['scenario'],'base-g15-t1');self.assertEqual(p['initialization'],'positive-zero')
            self.assertEqual(p['seed'],907001+i);self.assertEqual(p['segments'],[2*i,2*i+1])
        # The formerly omitted three fields and any altered namespace must be
        # rejected by the unchanged strict administrative identity predicate.
        for key in ('scenario','initialization','segments'):
            wrong=copy.deepcopy(primary);wrong[0].pop(key)
            with self.assertRaises(ValueError):A.same(wrong,independent,'Missing full primary plan field')
        wrong=copy.deepcopy(primary);wrong[-1]['segments'][1]+=1
        with self.assertRaises(ValueError):A.same(wrong,independent,'Wrong actor namespace segment')


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture()

    def tearDown(self):
        self.f.close()

    def test_complete12_inventory24_slots_exact_mean_and_root_aggregator(self):
        result=self.f.run()
        self.assertTrue(result['passed']);self.assertTrue(result['fullTrainingReplay'])
        self.assertEqual(result['replayedRounds'],24_000_000)
        self.assertEqual(result['scientificallyAvailableCheckpoints'],24)
        self.assertEqual(result['independentSummaries']['primarySummary']['meanDifference'],dict(numerator='2',denominator='1'))
        spec=importlib.util.spec_from_file_location('guard_root_analysis',ROOT/'research/guard-reference-analysis.py')
        other=importlib.util.module_from_spec(spec);spec.loader.exec_module(other)
        self.assertEqual(result['independentSummaries'],other.aggregate(result['finalEndpoints'],result['inheritedFinalEndpoints']))

    def test_bad_secondary_retains_every_final_and_primary_mean_but_not_full_replay(self):
        r=self.f.responses[self.f.records[0]['id']]
        r['checkpointResults'][0]=dict(step=1_000_000,parentEligible=True,matched=False,available=False,reason='Invented secondary bit mismatch')
        r['allPlannedCheckpointsMatched']=False
        result=self.f.run()
        self.assertEqual(result['finalAvailable'],12);self.assertFalse(result['fullTrainingReplay'])
        self.assertTrue(result['independentSummaries']['primarySummary']['available'])

    def test_bad_final_nulls_planned_mean_without_selective_seed_exclusion(self):
        r=self.f.responses[self.f.records[-1]['id']]
        r['checkpointResults'][1]=dict(step=2_000_000,parentEligible=True,matched=False,available=False,reason='Invented final mismatch')
        r['allPlannedCheckpointsMatched']=False
        result=self.f.run()
        self.assertEqual(len(result['independentSummaries']['pairedRows']),12)
        self.assertIsNone(result['independentSummaries']['primarySummary']['meanDifference'])
        self.assertEqual(result['independentSummaries']['completePairDescription']['denominator'],11)

    def test_operational_replay_failure_retains_unavailable_case_and_runs_later11(self):
        seen=[]
        def replay(node,project,directory,task_file,record_file,budget):
            record=A.parse(Path(record_file).read_bytes());seen.append(record['id'])
            if len(seen)==1:
                return dict(operationalFailure='Invented owned process crash',replayedRounds=0,fullHorizonReplayed=False,allPlannedCheckpointsMatched=False,checkpointResults=[])
            return copy.deepcopy(self.f.responses[record['id']])
        result=self.f.run(replay)
        self.assertEqual(len(seen),12);self.assertEqual(result['finalAvailable'],11)
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

    def test_missing_anchor_failure_retained_without_losing_valid_training_endpoints(self):
        self.f.anchors_available=False
        # A failed anchor before any closed anchor artifact must remain null.
        (self.f.directory/'stage-anchors.json').unlink()
        self.f.save_closed()
        result=self.f.run()
        self.assertTrue(result['inventoryAccepted']);self.assertTrue(result['executionPassed'])
        self.assertFalse(result['primaryPassed']);self.assertFalse(result['anchors']['available'])
        self.assertIsNone(result['anchors']['values']);self.assertIsNone(result['stageAnchorsSha256'])
        self.assertTrue(result['independentSummaries']['primarySummary']['available'])


class AllUnavailableTests(unittest.TestCase):
    def test_all12_pre_execution_failures_preserve_inventory_and_null_primary(self):
        f=Fixture(False)
        try:
            f.anchors_available=False;(f.directory/'stage-anchors.json').unlink();f.save_closed()
            result=f.run()
            self.assertTrue(result['passed']);self.assertFalse(result['executionPassed'])
            self.assertEqual(result['runs'],12);self.assertEqual(result['checkpointSlots'],24)
            self.assertEqual(result['finalAvailable'],0);self.assertEqual(result['replayedRounds'],0)
            self.assertFalse(result['fullTrainingReplay']);self.assertFalse(result['replayComplete'])
            self.assertEqual(len(result['independentSummaries']['pairedRows']),12)
            self.assertIsNone(result['independentSummaries']['primarySummary']['meanDifference'])
            self.assertFalse(result['anchors']['independentAgreement'])
        finally:f.close()


class AdministrativeOldBindingTests(unittest.TestCase):
    def test_independently_authenticated_old_chain_uses_hashes_not_decoding(self):
        project=ROOT/'.local'/('guard-old-binding-invented-'+uuid.uuid4().hex)
        project.mkdir(parents=True)
        base='research/matched-clock-results/'
        bound={};sources={}
        def write(name,value):
            ref=save(project,name,value);bound[name]=ref['sha256'];return ref
        def oldref(name,value):
            ref=write(base+name,value);return dict(ref,file=name)
        try:
            for name in ['research/audit-matched-clock-study.py','research/replay-matched-clock.js','research/audit-matched-clock.js']:
                ref=write(name,b'Wholly invented frozen source; not executed')
                sources[name]=ref['sha256'];write(base+'sources/'+name,b'Wholly invented frozen source; not executed')
            manifest=dict(sourceHashes=sources,inputHashes={})
            manifest_ref=write(base+'manifest.json',manifest)
            records=[];indices=[];endpoints=[];graphs=[]
            for seed in A.SEEDS:
                rid=f'base-g15-t1--matched5-startup--zero--s{seed}'
                # These intentionally NON-GZIP/NON-Q bytes can be hash-bound by
                # old acceptance reuse, and must never be decoded by this gate.
                q=oldref('checkpoints/'+rid+'/fake-q.gz',b'not a Q checkpoint or gzip stream')
                policy=oldref('checkpoints/'+rid+'/fake-policy.u8',b'opaque hash-bound old evidence')
                ratio=dict(numerator=str(seed-907001+10),denominator='1',approximate=seed-907001+10)
                graph=oldref('checkpoints/'+rid+'/graph.json',dict(actualTerminal=dict(cycleMetrics=dict(consumerSurplus=ratio),cycleNodesFromStart=[1,2,3,4])))
                meta=oldref('checkpoints/'+rid+'/metadata.json',dict(terminal=dict(phase=4,previousIndices=[1,2]),graph=graph,artifacts=dict(q=[q],counts=[q]),policies=dict(own=[policy],world=[policy])))
                row=dict(id=rid,seed=seed,arm='startup',checkpoints=[dict(step=2_000_000,parentEligible=True,metadata=meta)])
                ix=oldref('records/'+rid+'.json',row);ix.update(id=rid)
                records.append(row);indices.append(ix);graphs.append(graph)
                endpoints.append(dict(seed=seed,arm='startup',runId=rid,executionSucceeded=True,available=True,replayMatched=True,step=2_000_000,nextPhase=4,previousIndices=[1,2],cycleLength=4,checkpointSha256=meta['sha256'],graphSha256=graph['sha256'],cycleCustomerBenefit=dict(numerator=ratio['numerator'],denominator='1'),unavailableReason=None))
            for i in range(12):
                records.append(dict(id='invented-other-treatment-'+str(i)));indices.append(dict(id='invented-other-treatment-'+str(i)))
            output={}
            for name,value,key in [('results.json',dict(manifestSha256=manifest_ref['sha256'],records=records),'resultsSha256'),('index.json',dict(manifestSha256=manifest_ref['sha256'],records=indices),'indexSha256'),('completion.json',dict(scope='Invented pinned authority'),'completionSha256'),('execution-start.json',{},'executionStartSha256'),('journal.jsonl',b'opaque invented journal\n','journalSha256')]:
                output[key]=write(base+name,value)['sha256']
            audit=dict(passed=True,inventoryAccepted=True,independentAuditPassed=True,finalSourceInputOutputIntegrityCheck=True,
                       fullTrainingReplay=True,replayComplete=True,replayedRounds=48_000_000,studyManifestHash=manifest_ref['sha256'],
                       auditorSourceHash=sources['research/audit-matched-clock-study.py'],controlAuditorSourceHash=sources['research/replay-matched-clock.js'],replayCoreSourceHash=sources['research/audit-matched-clock.js'],finalEndpoints=endpoints,**output)
            audit_ref=write(base+'independent-audit.json',audit)
            with patch.object(A,'OLD_MANIFEST',manifest_ref['sha256']),patch.object(A,'OLD_AUDIT',audit_ref['sha256']):
                result=A.verify_old_comparison(project,bound)
                self.assertEqual(result['endpoints'],endpoints)
                self.assertIn('no old Q decode',result['scope'])
                changed=copy.deepcopy(bound);changed[base+'manifest.json']='0'*64
                with self.assertRaisesRegex(ValueError,'Pinned old'):A.verify_old_comparison(project,changed)
                file=project/(base+graphs[0]['file']);file.write_bytes(file.read_bytes()+b' ')
                with self.assertRaisesRegex(ValueError,'bytes/hash mismatch'):A.verify_old_comparison(project,bound)
        finally:
            self.assertEqual(project.resolve().parent,(ROOT/'.local').resolve());self.assertTrue(project.name.startswith('guard-old-binding-invented-'));shutil.rmtree(project)



if __name__=='__main__':unittest.main()
