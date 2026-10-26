"""Complete wholly invented evidence trees; no inherited market or Q data read.

The baseline authority is a declared artificial stub here; real use compiles
the source frozen by the new independently accepted manifest. Dense payloads
are deliberately opaque hash fixtures, proving the exporter never Q-decodes.
"""
import copy
import csv
import hashlib
import json
import io
from pathlib import Path
import shutil
import types
import unittest
import uuid

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/build-guard-reference-web.py'
M=types.ModuleType('guard_reference_export_tested');M.__file__=str(SOURCE)
exec(compile(SOURCE.read_bytes(),str(SOURCE),'exec'),M.__dict__)
ANALYSIS=types.ModuleType('invented_guard_analysis')
exec(compile((ROOT/'research/guard-reference-analysis.py').read_bytes(),'invented-analysis','exec'),ANALYSIS.__dict__)
SHA=lambda b:hashlib.sha256(b).hexdigest()
ENC=lambda v:(json.dumps(v,indent=2)+'\n').encode()
PACK=lambda i:dict(numerator=str(i),denominator='1')


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.parent=(ROOT/'.local').resolve();self.parent.mkdir(exist_ok=True)
        self.project=self.parent/('guard-export-invented-'+uuid.uuid4().hex);self.project.mkdir()
        self.directory=self.project/'research/guard-reference-results';self.directory.mkdir(parents=True)
        self.sourceHashes={}
        for name in ['research/build-guard-reference-web.py',M.UTILITY,'research/guard-reference-analysis.py']:
            self.write(name,(ROOT/name).read_bytes())
        for name in ['research/guard-reference-analysis.py','research/guard-reference-learning.js','research/guard-reference-io.js','research/guard-reference-case.js',M.IMMUTABLE_SOURCE,*M.SOURCE_KEYS.values()]:
            raw=(ROOT/name).read_bytes() if name in ['research/guard-reference-analysis.py',M.IMMUTABLE_SOURCE] else ('// invented identity '+name).encode()
            self.source(name,raw)
        self.source('research/guard-reference-baseline.py',b"import json\ndef load_baseline(project):\n return json.loads((project/'fixture-baseline.json').read_bytes())\n")
        n=62;rewards={k:[] for k in ['consumerSurplus','profitA','profitB','quantityA','quantityB']}
        for a in range(n):
            for b in range(n):
                for k,v in [('consumerSurplus',200-a-b),('profitA',a),('profitB',b),('quantityA',50),('quantityB',50)]:rewards[k].append(v)
        self.raw=dict(scenario=dict(id='base-g15-t1'),finite=dict(prices=list(range(1,63)),capIndex=0,sets=[[1] for _ in range(n)],rewards=rewards))
        self.finiteRef=self.write('invented/physical.json',ENC(self.raw))
        self.oldRecords=[];self.oldEndpoints=[];self.oldConsumed={}
        for seed in M.SEEDS:
            metadata,graph=self.checkpoint('old-study',seed,'startup-guard',2000000,1)
            self.oldRecords.append(dict(id=M.run_id(seed,'startup-guard'),checkpoints=[dict(step=2000000,parentEligible=True,metadata=metadata)]))
            self.oldEndpoints.append(self.endpoint(seed,'startup-guard',metadata,graph,1))
        oldresults=self.write('old-study/results.json',ENC(dict(records=self.oldRecords)))
        oldsummary=self.write('old-study/analysis.json',ENC(dict(meta=dict(studyDirectory='old-study',coreOutputRefs={'results.json':self.relative(oldresults,'old-study')}))))
        oldmanifest=self.write('old-study/manifest.json',b'{}');oldaudit=self.write('old-study/audit.json',b'{"artificial":true}');oldbuilder=self.write('old-study/builder.py',b'# artificial baseline authority')
        for p in (self.project/'old-study').rglob('*'):
            if p.is_file():self.oldConsumed[p.relative_to(self.project).as_posix()]=dict(bytes=p.stat().st_size,sha256=SHA(p.read_bytes()))
        self.oldConsumed[self.finiteRef['file']]=dict(bytes=self.finiteRef['bytes'],sha256=self.finiteRef['sha256'])
        kernel=self.project/M.IMMUTABLE_SOURCE;self.oldConsumed[M.IMMUTABLE_SOURCE]=dict(bytes=kernel.stat().st_size,sha256=SHA(kernel.read_bytes()))
        self.baseline=dict(manifest=oldmanifest,audit=oldaudit,summary=oldsummary,builder=oldbuilder,finalEndpoints=self.oldEndpoints,finiteGame=self.finiteRef,consumedFiles=self.oldConsumed)
        baselineRef=self.write('fixture-baseline.json',ENC(self.baseline))
        self.plan=[dict(id=M.run_id(seed,'full-grid-after-cap'),arm='startup',seed=seed,treatment='full-grid-after-cap',scientificTreatment=M.SCIENTIFIC) for seed in M.SEEDS]
        self.manifest=dict(sourceHashes=self.sourceHashes,inputHashes={self.finiteRef['file']:self.finiteRef['sha256'],baselineRef['file']:baselineRef['sha256']},inputs=dict(finiteGame=self.finiteRef),baseline={k:self.baseline[k] for k in ['manifest','audit','summary','builder','finalEndpoints']},plan=dict(runs=self.plan,T=2000000,checkpoints=[1000000,2000000],alpha=.1,gamma=19/20,scientificTreatment=M.SCIENTIFIC))
        self.manifest['baseline']['scope']='Artificial administrative prose is allowed'
        self.manifestRef=self.studywrite('manifest.json',self.manifest);self.records=[];self.endpoints=[];self.slots=[]
        for i,seed in enumerate(M.SEEDS):
            chosen=i%3;checkpoints=[]
            for step in M.STEPS:
                meta,graph=self.checkpoint('research/guard-reference-results',seed,'full-grid-after-cap',step,chosen)
                checkpoints.append(dict(step=step,parentEligible=True,scientificAvailable=False,metadata=meta))
                self.slots.append(dict(runId=self.plan[i]['id'],seed=seed,arm='startup',step=step,parentEligible=True,scientificAvailable=True,replayMatched=True,reason=None))
                if step==2000000:self.endpoints.append(self.endpoint(seed,'full-grid-after-cap',meta,graph,chosen))
            task=self.studywrite('tasks/'+self.plan[i]['id']+'.json',dict(plan=self.plan[i],scientificTreatment=M.SCIENTIFIC,record=self.raw,finiteGameRef=self.finiteRef,manifestSha256=self.manifestRef['sha256']))
            self.records.append(dict(self.plan[i],status='completed',executionSucceeded=True,checkpoints=checkpoints,task=task,manifestSha256=self.manifestRef['sha256']))
        anchors=ANALYSIS.stage_anchors(self.raw['finite']);self.anchorRef=self.studywrite('stage-anchors.json',anchors)
        self.audit=dict(passed=True,inventoryAccepted=True,independentAuditPassed=True,finalSourceInputOutputIntegrityCheck=True,studyManifestHash=self.manifestRef['sha256'],runs=12,checkpointSlots=24,
                        scientificallyAvailableCheckpoints=24,finalAvailable=12,replayedRounds=24000000,roundTranscriptBlocksMatched=2400,fullTrainingReplay=True,replayComplete=True,executionPassed=True,executionFailures=0,
                        finalEndpoints=self.endpoints,inheritedFinalEndpoints=self.oldEndpoints,checkpointResults=self.slots,
                        independentSummaries=ANALYSIS.aggregate(self.endpoints,self.oldEndpoints),anchors=dict(available=True,independentAgreement=True,values=copy.deepcopy(anchors),primaryReference=self.anchorRef,reason=None),stageAnchorsSha256=self.anchorRef['sha256'],resources=dict(scope='Invented bounded receipt',seconds=1))
        self.audit['anchors']['values']['scope']='Independent narrative may differ'
        for key,name in M.SOURCE_KEYS.items():self.audit[key]=self.sourceHashes[name]
        self.close_core()
    @staticmethod
    def relative(ref,prefix):return dict(ref,file=ref['file'][len(prefix)+1:])
    def write(self,name,raw):
        p=self.project/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);return dict(file=name,bytes=len(raw),sha256=SHA(raw))
    def studywrite(self,name,value):return self.relative(self.write('research/guard-reference-results/'+name,ENC(value)),'research/guard-reference-results')
    def source(self,name,raw):
        ref=self.write(name,raw);self.sourceHashes[name]=ref['sha256'];self.write('research/guard-reference-results/sources/'+name,raw)
    def checkpoint(self,root,seed,treatment,step,chosen):
        identity=M.run_id(seed,treatment);directory=f'checkpoints/{identity}/{step}';states=5*62*62
        def put(name,raw):return self.relative(self.write(root+'/'+directory+'/'+name,raw),root)
        policy=bytes([0]*(62*62)+[chosen]*(4*62*62));policies={k:[put(f'{k}-{f}.u8',policy) for f in ['A','B']] for k in ['own','world']}
        q=[];counts=[]
        for f in ['A','B']:
            for family,width,encoding,target in [('Q',8,'f64le',q),('counts',4,'u32le',counts)]:
                ref=put(f'{family}-{f}.gz',b'opaque artificial compressed bytes; never decode')
                target.append(dict(ref,rawBytes=5*62**3*width,rawSha256='0'*64,encoding=encoding,compression='gzip-single-member'))
        metrics=dict(consumerSurplus=PACK(200-2*chosen),profits=dict(A=PACK(chosen),B=PACK(chosen)),prices=dict(A=PACK(chosen+1),B=PACK(chosen+1)))
        training={f:dict(neverTriedGreedyActions=0) for f in ['A','B']};nodes=[p*62*62+chosen*62+chosen for p in [4,1,2,3]]
        trajectory=dict(floorApplies=None if treatment=='full-grid-after-cap' else True,floorGap=None if treatment=='full-grid-after-cap' else PACK(0),cycleMetrics=metrics,cycleNodesFromStart=nodes,transientRounds=0,trainingSupport=training)
        graph=dict(step=step,phase=4,arm='startup',scientificTreatment=M.scientific(treatment),floor=None if treatment=='full-grid-after-cap' else dict(scope='Invented old guard floor'),cycles=[dict(floorApplies=trajectory['floorApplies'],floorGap=trajectory['floorGap'])],actualTerminal=trajectory,freshCapCounterfactual=trajectory,policySha256=[r['sha256'] for r in policies['own']],worldPolicySha256=[r['sha256'] for r in policies['world']])
        graphRef=put('graph.json',ENC(graph))
        meta=dict(id=identity,seed=seed,step=step,arm='startup',treatment=treatment,scientificTreatment=M.scientific(treatment),n=62,phases=5,finiteGameRef=self.finiteRef,terminal=dict(phase=4,previousIndices=[chosen,chosen]),artifacts=dict(q=q,counts=counts),policies=policies,graph=graphRef,windowMetrics=[])
        return put('metadata.json',ENC(meta)),graphRef
    def endpoint(self,seed,treatment,meta,graph,chosen):
        return dict(arm='startup',seed=seed,runId=M.run_id(seed,treatment),available=True,replayMatched=True,executionSucceeded=True,step=2000000,nextPhase=4,previousIndices=[chosen,chosen],cycleLength=4,checkpointSha256=meta['sha256'],graphSha256=graph['sha256'],cycleCustomerBenefit=PACK(200-2*chosen),unavailableReason=None)
    def close_core(self):
        ix=[]
        for record in self.records:
            ref=self.studywrite('records/'+record['id']+'.json',record);ix.append(dict(ref,id=record['id'],status=record['status']))
        refs={}
        refs['index.json']=self.studywrite('index.json',dict(manifestSha256=self.manifestRef['sha256'],records=ix))
        refs['results.json']=self.studywrite('results.json',dict(manifestSha256=self.manifestRef['sha256'],records=self.records,stageAnchors=self.anchorRef,stageAnchorsFailure=None))
        refs['execution-start.json']=self.studywrite('execution-start.json',dict(manifestSha256=self.manifestRef['sha256']))
        refs['journal.jsonl']=self.relative(self.write('research/guard-reference-results/journal.jsonl',b''.join(ENC(dict(invented=i)).replace(b'\n',b'')+b'\n' for i in range(26))),'research/guard-reference-results')
        completion=dict(manifestSha256=self.manifestRef['sha256'],inventoryComplete=True,retainedRuns=12,retainedCheckpointSlots=24,finalFrozenDependencyCheck=dict(passed=True),anchorCalculationPassed=True,stageAnchorsSha256=self.anchorRef['sha256'])
        for name,ref in refs.items():completion[M.CORE_KEYS[name]]=ref['sha256'];self.audit[M.CORE_KEYS[name]]=ref['sha256']
        refs['completion.json']=self.studywrite('completion.json',completion);self.audit['completionSha256']=refs['completion.json']['sha256']
        self.auditRef=self.studywrite('independent-audit.json',self.audit)
    def build(self,**kwargs):return M.build(self.project,self.directory,self.directory/'independent-audit.json',self.auditRef['sha256'],**kwargs)
    def tearDown(self):
        self.assertEqual(self.project.resolve().parent,self.parent);self.assertTrue(self.project.name.startswith('guard-export-invented-'));shutil.rmtree(self.project)
    def test_complete_gate_outputs_all_slots_and_exact_anchor_csv_with_independent_text(self):
        bundle=self.build();web=json.loads(bundle['outputs']['web-data.json'])
        self.assertEqual((len(web['finalPolicies']),len(web['pairedRows']),len(web['checkpointStatuses']),len(web['inheritedComparisonStatuses'])),(24,12,24,12))
        self.assertEqual(web['completePairDescription']['signCounts'],dict(positive=4,zero=4,negative=4))
        self.assertEqual(web['primarySummary']['meanDifference'],PACK(0))
        self.assertIn(b'profitA_numerator',bundle['outputs']['stage-anchors.csv'])
        summary=json.loads(bundle['outputs']['analysis.json'])
        self.assertEqual((len(summary['checkpointDetails']),len(summary['inheritedComparisonDetails'])),(24,12))
        self.assertEqual(summary['checkpointDetails'][0]['actualTerminal']['jointProfitExact'],PACK(0))
        rows=list(csv.DictReader(io.StringIO(bundle['outputs']['endpoint-metrics.csv'].decode())))
        self.assertEqual(len(rows),36)
        self.assertEqual(rows[0]['cycle_jointProfit_numerator'],'0')
        self.assertEqual(rows[2]['cycle_jointProfit_numerator'],'2')
        self.assertEqual(web['anchors']['values']['scope'],self.audit['anchors']['values']['scope'].replace('Independent narrative may differ',ANALYSIS.stage_anchors(self.raw['finite'])['scope']))
    def test_rejected_parent_eligible_secondary_retains_hashes_without_graph_policy_adoption(self):
        slot=self.records[0]['checkpoints'][0];meta=json.loads((self.directory/slot['metadata']['file']).read_bytes())
        meta['graph']=self.studywrite(meta['graph']['file'],dict(malformed='Independent rejection; not scientific data'))
        meta['policies']['world'][0]=self.relative(self.write('research/guard-reference-results/'+meta['policies']['world'][0]['file'],b'\xff'*19220),'research/guard-reference-results')
        # Fresh hash binding does not make these independently rejected
        # scientific identities eligible for adoption into the valid finals.
        meta.update(id='wrong-scientific-id',seed=907999,step=7,arm='recurring4',finiteGameRef=dict(file='wrong-physical-record',sha256='f'*64))
        slot['metadata']=self.studywrite(slot['metadata']['file'],meta)
        self.slots[0].update(scientificAvailable=False,replayMatched=False,reason='Invented rejected secondary graph')
        self.audit.update(scientificallyAvailableCheckpoints=23,fullTrainingReplay=False,replayComplete=False)
        self.close_core();bundle=self.build();web=json.loads(bundle['outputs']['web-data.json'])
        self.assertTrue(web['primarySummary']['available']);self.assertFalse(web['checkpointStatuses'][0]['scientificAvailable'])
        details=json.loads(bundle['outputs']['analysis.json'])['checkpointDetails'][0]
        self.assertIsNone(details['actualTerminal']);self.assertIsNone(details['trainingTail']);self.assertIsNone(details['coverage'])
        self.assertTrue(all(p['available'] for p in web['finalPolicies']))
        (self.directory/meta['graph']['file']).write_bytes(b'drift')
        with self.assertRaises(ValueError):self.build()
    def test_unavailable_anchors_preserve_all_twelve_final_mean_and_explicit_csv_row(self):
        reason='Invented independent static-anchor calculation unavailable'
        self.audit['anchors']=dict(available=False,independentAgreement=False,values=None,reason=reason)
        self.close_core()
        bundle=self.build();web=json.loads(bundle['outputs']['web-data.json'])
        self.assertTrue(web['primarySummary']['available'])
        self.assertEqual(web['primarySummary']['plannedDenominator'],12)
        self.assertEqual(web['primarySummary']['availablePairs'],12)
        self.assertEqual(web['primarySummary']['meanDifference'],PACK(0))
        self.assertTrue(all(p['available'] for p in web['finalPolicies']))
        self.assertFalse(web['anchors']['available'])
        self.assertIsNone(web['anchors']['values'])
        self.assertEqual(web['anchors']['reason'],reason)
        rows=list(csv.DictReader(io.StringIO(bundle['outputs']['stage-anchors.csv'].decode())))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['group'],'unavailable')
        self.assertEqual(rows[0]['retainedCount'],'0')
        self.assertEqual(rows[0]['reason'],reason)
        self.assertTrue(all(value=='' for key,value in rows[0].items() if key not in ['group','retainedCount','reason']))
    def test_summary_self_forgery_and_exclusive_outputs_reject(self):
        bundle=self.build();M.write_outputs(bundle,self.directory)
        path=self.directory/'analysis.json';raw=path.read_bytes();summary=json.loads(raw)
        self.assertEqual(M.load_accepted(path,self.auditRef['sha256'],project=self.project),summary)
        changes=[lambda s:s['meta']['consumedFiles'].pop(next(iter(s['meta']['consumedFiles']))),lambda s:s['resources'].__setitem__('seconds',999),lambda s:s['runs'][0].__setitem__('status','forged'),lambda s:s['meta']['inputHashes'].clear()]
        for change in changes:
            forged=copy.deepcopy(summary);change(forged);path.write_bytes(ENC(forged))
            with self.assertRaisesRegex(ValueError,'authoritative deterministic'):M.load_accepted(path,self.auditRef['sha256'],project=self.project)
        path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError,'refusing overwrite'):M.write_outputs(bundle,self.directory)
    def test_bound_input_or_end_of_build_drift_rejects(self):
        with self.assertRaises(ValueError):self.build(before_final_check=lambda:(self.project/self.finiteRef['file']).write_bytes(b'changed input'))

    def test_immutable_kernel_binding_without_optional_receipt_alias(self):
        self.assertNotIn('immutableReplayKernelSourceHash',self.audit)
        self.assertTrue(self.build()['verification']['passed'])
        self.audit['immutableReplayKernelSourceHash']='f'*64;self.close_core()
        with self.assertRaisesRegex(ValueError,'Optional immutable'):self.build()
        del self.audit['immutableReplayKernelSourceHash']
        self.sourceHashes.pop(M.IMMUTABLE_SOURCE)
        self.manifestRef=self.studywrite('manifest.json',self.manifest);self.audit['studyManifestHash']=self.manifestRef['sha256'];self.close_core()
        with self.assertRaisesRegex(ValueError,'immutable replay kernel'):self.build()
        self.source(M.IMMUTABLE_SOURCE,b'// invented hash-rebound incompatible kernel')
        self.manifestRef=self.studywrite('manifest.json',self.manifest);self.audit['studyManifestHash']=self.manifestRef['sha256'];self.close_core()
        with self.assertRaisesRegex(ValueError,'immutable replay kernel'):self.build()


if __name__=='__main__':unittest.main()
