"""Artificial hash-bound export fixtures only; no inherited game/Q/outcome reads.

The trusted-audit marker is deliberately manufactured for each fixture. Tests
exercise the derivative gate/shape, not numerical replay or audit authenticity.
"""
import copy
import hashlib
import importlib.util
import json
import shutil
import unittest
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('matched_export',ROOT/'research/build-matched-clock-web.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)


class Fixture:
    def __init__(self,missing=()):
        self.project=ROOT/'.local'/('matched-export-artificial-'+str(uuid.uuid4()));self.project.mkdir()
        self.directory=self.project/'research/matched-clock-results';self.directory.mkdir(parents=True)
        self.audit_path=self.project/'accepted-artificial-audit.json'
        self.put('research/build-matched-clock-web.py',(ROOT/'research/build-matched-clock-web.py').read_bytes())
        self.sources={}
        for name in [*E.SOURCE_KEYS.values(),'research/matched-clock-analysis.py']+[f'artificial/source-{i}.txt' for i in range(25)]:
            raw=(ROOT/name).read_bytes() if name=='research/matched-clock-analysis.py' else ('Artificial source identity '+name).encode()
            ref=self.put(name,raw);self.sources[name]=ref['sha256'];self.put('research/matched-clock-results/sources/'+name,raw)
        n=62;self.raw={'scenario':{'id':'base-g15-t1'},'originalTargets':[],'finite':{'prices':list(range(n)),'capIndex':0,'sets':[[0] for _ in range(n)],'upper':[0]*n,'rewards':{k:[1 if k=='consumerSurplus' else 0]*(n*n) for k in ('consumerSurplus','profitA','profitB','quantityA','quantityB')}}}
        finite=self.put('invented-finite.json',self.raw);self.input=self.put('invented-input.txt',b'artificial immutable premise')
        self.manifest={'schemaVersion':1,'sourceHashes':self.sources,'inputHashes':{finite['file']:finite['sha256'],self.input['file']:self.input['sha256']},'inputs':{'finiteGame':finite},'runtime':{'scope':'artificial backend'},'parentRuntime':{'scope':'artificial parent'},'plan':{'runs':E.planned(),'T':2000000,'checkpoints':[1000000,2000000]}}
        m=self.study('manifest.json',self.manifest);self.mh=m['sha256'];self.records=[];self.slots=[];self.endpoints=[]
        for plan in E.planned():
            record={**plan,'status':'completed','executionSucceeded':True,'failure':None,'manifestSha256':self.mh,'events':[],'checkpoints':[]}
            task=self.study('tasks/'+plan['id']+'.json',{'manifestSha256':self.mh,'finiteGameRef':finite,'record':self.raw});record['task']=task
            for step in (1000000,2000000):
                available=(plan['seed'],plan['arm'],step) not in missing
                prefix='checkpoints/'+plan['id']+'/'+str(step)+'/'
                own=[self.study(prefix+f'own-{f}.bin',bytes(5*n*n)) for f in range(2)]
                world=[self.study(prefix+f'world-{f}.bin',bytes(5*n*n)) for f in range(2)]
                graph={'states':5*n*n,'step':step,'phase':4,'arm':plan['arm'],'policySha256':[r['sha256'] for r in own],'worldPolicySha256':[r['sha256'] for r in world],'actualTerminal':{'start':{'phase':4,'previousIndices':[0,0]},'cycleMetrics':{'consumerSurplus':{'numerator':'1','denominator':'1','approximate':1.0}},'transientRounds':0,'cycleNodesFromStart':[n*n,2*n*n,3*n*n,4*n*n],'trainingSupport':{'A':{'neverTriedGreedyActions':0},'B':{'neverTriedGreedyActions':0}}},'terminalPreview128':[],'coverage':{}}
                gr=self.study(prefix+'graph.json',graph);artifacts={}
                for family,width,encoding in [('q',8,'f64le'),('counts',4,'u32le')]:
                    refs=[]
                    for f in range(2):
                        # Opaque compressed binding: the export MUST NOT inflate it.
                        ref=self.study(prefix+family+str(f)+'.gz',b'artificial-opaque-compressed-binding')
                        refs.append(dict(ref,rawBytes=5*n*n*n*width,rawSha256='c'*64,encoding=encoding,compression='gzip-single-member'))
                    artifacts[family]=refs
                meta={'schemaVersion':1,'id':plan['id'],'arm':plan['arm'],'seed':plan['seed'],'step':step,'n':n,'phases':5,'finiteGameRef':finite,'artifacts':artifacts,'policies':{'own':own,'world':world},'graph':gr,'terminal':{'phase':4,'previousIndices':[0,0]},'caps':1 if plan['arm']=='startup' else step//4,'windowMetrics':[{'endStep':s,'metrics':{'consumerSurplus':{'numerator':'1','denominator':'1','approximate':1.0}}} for s in (1000000,2000000)]}
                mr=self.study(prefix+'metadata.json',meta)
                reason=None if available else 'Retained artificial checkpoint failure'
                record['checkpoints'].append({'step':step,'metadata':mr if available else None,'parentEligible':available,'scientificAvailable':False,'reason':reason})
                self.slots.append(dict(runId=plan['id'],seed=plan['seed'],arm=plan['arm'],step=step,parentEligible=available,scientificAvailable=available,replayMatched=available,reason=reason))
                if step==2000000:
                    endpoint=dict(seed=plan['seed'],arm=plan['arm'],runId=plan['id'],executionSucceeded=True,available=available,replayMatched=available,cycleCustomerBenefit={'numerator':'1','denominator':'1'} if available else None,unavailableReason=reason)
                    if available:endpoint.update(step=step,nextPhase=4,previousIndices=[0,0],cycleLength=4,checkpointSha256=mr['sha256'],graphSha256=gr['sha256'])
                    self.endpoints.append(endpoint)
            self.records.append(record)
        self.refresh()

    def put(self,name,value):
        p=self.project/name;p.parent.mkdir(parents=True,exist_ok=True)
        raw=value if isinstance(value,bytes) else E.encoded(value);p.write_bytes(raw)
        return dict(file=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())

    def study(self,name,value):
        ref=self.put('research/matched-clock-results/'+name,value);ref['file']=name;return ref

    def refresh(self):
        index=[]
        for r in self.records:index.append(dict(self.study('records/'+r['id']+'.json',r),id=r['id'],status=r['status']))
        r=self.study('results.json',{'manifestSha256':self.mh,'records':self.records});ix=self.study('index.json',{'manifestSha256':self.mh,'records':index})
        journal=self.study('journal.jsonl',b''.join(E.encoded({'type':'artificial journal slot','i':i}).replace(b'\n',b'')+b'\n' for i in range(49)))
        start=self.study('execution-start.json',{'manifestSha256':self.mh})
        completion=self.study('completion.json',dict(manifestSha256=self.mh,inventoryComplete=True,retainedRuns=24,retainedCheckpointSlots=48,finalFrozenDependencyCheck={'passed':True},resultsSha256=r['sha256'],indexSha256=ix['sha256'],journalSha256=journal['sha256'],executionStartSha256=start['sha256']))
        analysis=E.load_analysis(self.project/'research/matched-clock-analysis.py');aggregated=analysis.aggregate(self.endpoints)
        complete=all(s['scientificAvailable'] for s in self.slots)
        self.audit=dict(passed=True,inventoryAccepted=True,independentAuditPassed=True,finalSourceInputOutputIntegrityCheck=True,studyManifestHash=self.mh,**{key:self.sources[name] for key,name in E.SOURCE_KEYS.items()},resultsSha256=r['sha256'],indexSha256=ix['sha256'],completionSha256=completion['sha256'],journalSha256=journal['sha256'],executionStartSha256=start['sha256'],runs=24,checkpointSlots=48,scientificallyAvailableCheckpoints=sum(s['scientificAvailable'] for s in self.slots),finalAvailable=sum(e['available'] for e in self.endpoints),fullTrainingReplay=complete,replayComplete=complete,replayedRounds=48000000 if any(e['available'] for e in self.endpoints) else 0,finalEndpoints=self.endpoints,checkpointResults=self.slots,independentSummaries=aggregated,executionPassed=True,executionFailures=0,resources={'scope':'artificial test only'},scope='Wholly artificial trusted-receipt fixture; not numerical audit acceptance')
        self.save_audit()

    def save_audit(self):
        self.audit_path.write_bytes(E.encoded(self.audit));self.audit_sha=E.digest(self.audit_path)

    def build(self,**kw):return E.build(self.project,self.directory,self.audit_path,self.audit_sha,**kw)

    def close(self):
        root=self.project.resolve();allowed=(ROOT/'.local').resolve()
        assert root.is_relative_to(allowed) and root.name.startswith('matched-export-artificial-')
        shutil.rmtree(root)


class ExportTests(unittest.TestCase):
    def test_complete_deterministic_bundle_and_reusable_summary_gate(self):
        f=Fixture()
        try:
            a=f.build();b=f.build();self.assertEqual(a['outputs'],b['outputs']);self.assertTrue(a['verification']['passed'])
            web=json.loads(a['outputs']['web-data.json']);self.assertEqual((len(web['runs']),len(web['checkpoints']),len(web['pairedRows']),len(web['finalPolicyPairs'])),(24,48,12,24));self.assertEqual(web['primarySummary']['mean'],{'numerator':'0','denominator':'1'})
            output=f.project/'derived';E.write_outputs(a,output);summary=E.load_accepted(output/'analysis.json',f.audit_sha,project=f.project);self.assertEqual(summary['primarySummary']['meanDifference'],{'numerator':'0','denominator':'1'})
            path=output/'analysis.json';original=path.read_bytes()
            for change in [lambda s:s['meta']['consumedFiles'].pop(next(iter(s['meta']['consumedFiles']))),lambda s:s['resources'].update(forgedCount=999),lambda s:s['meta']['auditSummary'].update(replayedRounds=1),lambda s:s['checkpoints'][0].update(status='forged'),lambda s:s['runs'][0].update(status='forged'),lambda s:s['inputHashes'].clear()]:
                altered=json.loads(original);change(altered);path.write_bytes(E.encoded(altered))
                with self.assertRaisesRegex(ValueError,'authoritative'):E.load_accepted(path,f.audit_sha,project=f.project)
                path.write_bytes(original)
            self.assertEqual(len(a['outputs']['paired-results.csv'].splitlines()),13);self.assertEqual(len(a['outputs']['checkpoint-statuses.csv'].splitlines()),49)
            with self.assertRaisesRegex(ValueError,'overwrite'):E.write_outputs(b,output)
        finally:f.close()

    def test_honest_secondary_failure_keeps_final_mean_but_missing_final_nulls_it(self):
        for missing,mean in [([(907001,'startup',1000000)],True), ([(907001,'startup',2000000)],False)]:
            f=Fixture(missing)
            try:
                web=json.loads(f.build()['outputs']['web-data.json']);self.assertEqual(web['primarySummary']['available'],mean);self.assertFalse(web['meta']['fullTrainingReplay']);self.assertFalse(web['meta']['replayComplete']);self.assertEqual(len(web['checkpoints']),48)
                if not mean:self.assertIsNone(web['primarySummary']['mean']);self.assertIsNone(web['finalPolicyPairs'][0]['policies'])
            finally:f.close()

    def test_parent_eligible_but_scientifically_rejected_secondary_retains_hashes_not_claims(self):
        f=Fixture()
        try:
            slot=f.records[0]['checkpoints'][0]
            self.assertTrue(slot['parentEligible'])
            meta=json.loads((f.directory/slot['metadata']['file']).read_bytes())
            # Freshly bind a malformed graph claim AND an illegal off-path
            # policy to this rejected secondary slot. Final artifacts stay valid.
            meta['graph']=f.study(meta['graph']['file'],{'rejectedMalformedGraphClaim':True})
            bad=bytearray((f.directory/meta['policies']['world'][1]['file']).read_bytes());bad[0]=61
            meta['policies']['world'][1]=f.study(meta['policies']['world'][1]['file'],bytes(bad))
            slot['metadata']=f.study(slot['metadata']['file'],meta)
            checked=f.slots[0];checked.update(scientificAvailable=False,replayMatched=False,reason='Independent rejection of secondary graph/policy claim')
            f.refresh()
            bundle=f.build();web=json.loads(bundle['outputs']['web-data.json']);rejected=web['checkpoints'][0]
            self.assertTrue(web['primarySummary']['available']);self.assertEqual(web['primarySummary']['acceptedPairs'],12)
            self.assertFalse(web['meta']['fullTrainingReplay']);self.assertFalse(web['meta']['replayComplete'])
            self.assertFalse(rejected['scientificAvailable']);self.assertTrue(rejected['replayStatus']['parentEligible'])
            for key in ('frozen','preview128','coverage','terminal','trainingTail'):self.assertIsNone(rejected[key])
            self.assertIn('Independent rejection',rejected['reason'])
            names=web['meta']['consumedFiles']
            for ref in [meta['graph'],meta['policies']['world'][1]]:
                name='research/matched-clock-results/'+ref['file'];self.assertEqual(names[name]['sha256'],ref['sha256'])
            graph_path=f.directory/meta['graph']['file'];raw=graph_path.read_bytes();graph_path.write_bytes(raw+b'!')
            with self.assertRaises(ValueError):f.build()
            graph_path.write_bytes(raw)
        finally:f.close()

    def test_semantic_receipt_corruptions_reject_even_with_new_artificial_accepted_sha(self):
        f=Fixture()
        try:
            original=copy.deepcopy(f.audit)
            changes=[lambda a:a.update(passed=False),lambda a:a.update(auditorSourceHash='0'*64),lambda a:a.update(studyManifestHash='0'*64),lambda a:a['independentSummaries']['pairedRows'][0].update(difference={'numerator':'1','denominator':'1'}),lambda a:a['finalEndpoints'].pop(),lambda a:a['checkpointResults'].pop(),lambda a:a.update(finalAvailable=23),lambda a:a.update(replayComplete=False)]
            for change in changes:
                f.audit=copy.deepcopy(original);change(f.audit);f.save_audit()
                with self.assertRaises(ValueError):f.build()
            f.audit=original;f.save_audit()
        finally:f.close()

    def test_source_input_core_snapshot_dense_policy_and_final_drift_reject(self):
        f=Fixture()
        try:
            first=f.records[0]['checkpoints'][0]['metadata'];meta=json.loads((f.directory/first['file']).read_bytes())
            files=[f.project/'invented-input.txt',f.project/'research/matched-clock-analysis.py',f.directory/'sources/research/matched-clock-analysis.py',f.directory/'completion.json',f.directory/'records'/f"{f.records[0]['id']}.json",f.directory/meta['artifacts']['q'][0]['file'],f.directory/meta['policies']['world'][1]['file'],f.directory/meta['graph']['file']]
            for path in files:
                raw=path.read_bytes();path.write_bytes(raw+b'!')
                try:
                    with self.assertRaises(ValueError):f.build()
                finally:path.write_bytes(raw)
            path=f.project/'invented-input.txt';raw=path.read_bytes()
            with self.assertRaisesRegex(ValueError,'closure'):f.build(before_final_check=lambda:path.write_bytes(raw+b'!'))
            path.write_bytes(raw)
            with self.assertRaises(ValueError):E.local(f.project,'../escape')
        finally:f.close()


if __name__=='__main__':unittest.main()
