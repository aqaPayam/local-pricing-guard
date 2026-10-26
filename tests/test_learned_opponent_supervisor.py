"""Artificial process-isolation/retention tests; no inherited evidence read."""
from pathlib import Path
import contextlib,importlib.util,io,json,shutil,struct,sys,time,uuid,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prospective_learned_runner',ROOT/'research/run-learned-opponent.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

class ProcessTests(unittest.TestCase):
 def setUp(self):
  self.parent=(ROOT/'.local').resolve();self.directory=self.parent/('learned-process-synthetic-'+uuid.uuid4().hex);self.directory.mkdir();self.plan={**runner.planned_cases()[0],'id':'artificial','control':{'id':'selected95','period':1,'phases':1}}
  f={'prices':[0,1],'sets':[[0,1],[0,1]],'capIndex':1,'rewards':{'profitA':[1,3,4,2],'profitB':[2,5,7,1],'consumerSurplus':[10,8,8,6]}}
  self.payload={'record':f,'control':self.plan['control'],'worldPolicies':[[0]*4,[0]*4],'focal':'A','start':0,'input':{'scope':'artificial retained reference'}}
 def tearDown(self):
  p=self.directory.resolve();self.assertTrue(p.is_relative_to(self.parent) and p.name.startswith('learned-process-synthetic-'));shutil.rmtree(p)
 def case(self,name,body):
  p=self.directory/(name+'.mjs');p.write_text(body,encoding='utf-8');return p
 def generated(self,tail):
  url=(ROOT/'research/learned-opponent-study.js').as_uri()
  return "import fs from 'node:fs';import path from 'node:path';import {prepareMDP,solveLoadedCase} from "+json.dumps(url)+";const task=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),p=task.payload,directory=path.resolve(path.dirname(process.argv[2]),'..'),m=prepareMDP(p.record,p.control,p.worldPolicies.map(x=>Uint8Array.from(x)),p.focal),r=solveLoadedCase(task.plan,{mdp:m,start:p.start,input:{inputRoot:'artificial'}},directory);fs.writeSync(1,JSON.stringify({type:'certificate',complete:r.complete})+'\\n');"+tail
 def execute(self,**kwargs):return runner.execute_case(self.plan,self.directory,ROOT,mode='artificial',payload=self.payload,**kwargs)
 def test_owned_busy_process_is_killed_then_next_case_completes(self):
  stall=self.case('busy',"process.stdout.write(JSON.stringify({type:'stage',stage:'proposal'})+'\\n');while(true){}")
  r=self.execute(case_source=stall,budget_seconds=.3);self.assertEqual(r['status'],runner.STATUS['timeout']);self.assertFalse(r['executionSucceeded']);self.assertFalse(r['scientificAvailable']);self.assertIsNone(r['performance']);self.assertEqual(r['input'],self.payload['input']);self.assertLess(r['runtime']['caseSeconds'],5)
  self.plan={**self.plan,'id':'artificial-next'};n=self.execute(budget_seconds=10);self.assertTrue(n['executionSucceeded']);self.assertTrue(n['scientificAvailable']);self.assertTrue(n['certificate']['passed']);self.assertEqual(n['runtime']['workerExitCode'],0)
 def test_complete_before_timeout_remains_available_execution_failed(self):
  source=self.case('after',self.generated('while(true){}'));r=self.execute(case_source=source,budget_seconds=1)
  self.assertEqual(r['status'],runner.STATUS['timeout']);self.assertFalse(r['executionSucceeded']);self.assertTrue(r['scientificAvailable']);self.assertLess(r['runtime']['receivedCompleteMilliseconds'],r['runtime']['terminationRequestedMilliseconds']);self.assertIsNotNone(r['performance']);runner.readref(self.directory,r['runtime']['completeCertificate'])
  events=r['runtime']['events'];receipt=next(e for e in events if e['type']=='complete certificate received');self.assertLessEqual(receipt['lineReceivedMilliseconds'],receipt['elapsedMilliseconds'])
 def test_nonzero_before_certificate_is_unavailable_then_continues(self):
  source=self.case('crash','process.stderr.write("artificial native-like failure\\n");process.exit(23);');r=self.execute(case_source=source,budget_seconds=5);self.assertFalse(r['scientificAvailable']);self.assertFalse(r['executionSucceeded']);self.assertEqual(r['runtime']['workerExitCode'],23);self.assertIn('artificial',r['runtime']['stderr'])
  self.plan={**self.plan,'id':'after-nonzero'};self.assertTrue(self.execute(budget_seconds=10)['executionSucceeded'])
 def test_nonzero_after_complete_is_available_but_never_an_optimized_success(self):
  source=self.case('late-crash',self.generated("fs.writeSync(1,JSON.stringify({type:'done'})+'\\n');process.exit(29);"));r=self.execute(case_source=source,budget_seconds=5)
  self.assertTrue(r['scientificAvailable']);self.assertFalse(r['executionSucceeded']);self.assertEqual(r['status'],runner.STATUS['worker']);self.assertEqual(r['runtime']['workerExitCode'],29)
 def test_done_then_busy_is_still_a_hard_timeout(self):
  source=self.case('done-busy',self.generated("fs.writeSync(1,JSON.stringify({type:'done'})+'\\n');while(true){}"));r=self.execute(case_source=source,budget_seconds=1)
  self.assertEqual(r['status'],runner.STATUS['timeout']);self.assertFalse(r['executionSucceeded']);self.assertTrue(r['scientificAvailable'])
 def test_closed_stdout_then_busy_is_still_a_hard_timeout(self):
  source=self.case('closed-stdout',self.generated("fs.writeSync(1,JSON.stringify({type:'done'})+'\\n');fs.closeSync(1);while(true){}"));r=self.execute(case_source=source,budget_seconds=1)
  self.assertEqual(r['status'],runner.STATUS['timeout']);self.assertFalse(r['executionSucceeded']);self.assertTrue(r['scientificAvailable'])
 def test_duplicate_or_corrupt_complete_message_cannot_replace_received_bundle(self):
  source=self.case('duplicate',self.generated("fs.writeSync(1,JSON.stringify({type:'certificate',complete:r.complete})+'\\n');process.exit(0);"));r=self.execute(case_source=source,budget_seconds=5)
  self.assertFalse(r['executionSucceeded']);self.assertTrue(r['scientificAvailable']);self.assertIn('Second complete',r['failure']['message']);self.assertEqual(sum(e['type']=='complete certificate received' for e in r['runtime']['events']),1)
 def test_only_last_received_proposal_is_preserved_without_post_timeout_salvage(self):
  url=(ROOT/'research/learned-opponent-study.js').as_uri()
  code="import fs from 'node:fs';import path from 'node:path';import {writeArtifact,float64Bytes} from "+json.dumps(url)+";const directory=path.resolve(path.dirname(process.argv[2]),'..'),file='progress.bin',ref=writeArtifact(directory,file,float64Bytes(new Float64Array([.5,.5,.5,.5])));fs.writeSync(1,JSON.stringify({type:'iteration',completedSweeps:1,difference:1,proposal:ref})+'\\n');fs.readSync(0,Buffer.alloc(1),0,1,null);fs.writeFileSync(path.join(directory,file),float64Bytes(new Float64Array([9,9,9,9])));while(true){}"
  source=self.case('partial-proposal',code);r=self.execute(case_source=source,budget_seconds=.5)
  self.assertFalse(r['scientificAvailable']);self.assertIsNone(r['performance']);self.assertEqual(r['optimizer']['completedSweeps'],1);b=runner.readref(self.directory,r['optimizer']['finalFloat64']);self.assertEqual(struct.unpack('<4d',b),(.5,)*4);self.assertEqual(struct.unpack('<4d',(self.directory/'progress.bin').read_bytes()),(9,)*4)
 def test_validation_crossing_deadline_never_grants_scientific_availability(self):
  original=runner.validate_complete
  def delayed(*args):
   r=original(*args);time.sleep(.6);return r
  with patch.object(runner,'validate_complete',side_effect=delayed):r=self.execute(budget_seconds=.5)
  self.assertEqual(r['status'],runner.STATUS['timeout']);self.assertFalse(r['scientificAvailable']);self.assertIsNone(r['performance']);self.assertIsNone(r['runtime']['receivedCompleteAt'])
 def test_no_overwrite_path_escape_or_false_closed_receipt(self):
  ref=runner.save(self.directory,'retained/data.bin',b'original');self.assertEqual(runner.readref(self.directory,ref),b'original')
  with self.assertRaises(FileExistsError):runner.save(self.directory,ref['file'],b'replacement')
  with self.assertRaises(ValueError):runner.local(self.directory,'../escape')
  for name in ['execution-start.json','journal.jsonl','records','artifacts','tasks','results.json','index.json','completion.json']:
   p=self.directory/name;p.write_text('old',encoding='utf-8')
   with self.assertRaises(ValueError):runner.assert_fresh(self.directory)
   self.assertEqual(p.read_text(),'old');p.unlink()
 def test_all48_bookkeeping_labels_survive_mocked_input_and_budget_failures(self):
  plans=runner.planned_cases();manifest={'plan':{'cases':plans},'inputs':{p['oldRunID']:{'scope':'artificial administrative identity'} for p in plans}};(self.directory/'manifest.json').write_text(json.dumps(manifest))
  def failed(plan,*args,**kwargs):return {**plan,'status':runner.STATUS['timeout'] if plan==plans[0] else runner.STATUS['input'],'executionSucceeded':False,'scientificAvailable':False,'input':manifest['inputs'][plan['oldRunID']],'mdp':None,'optimizer':None,'baseline':None,'response':None,'certificate':None,'performance':None,'runtime':{'events':[],'caseSeconds':0},'failure':{'stage':'input','message':'Artificial declared failure'}}
  with patch.object(runner,'verify',return_value=manifest),patch.object(runner,'execute_case',side_effect=failed),contextlib.redirect_stdout(io.StringIO()):c=runner.run(self.directory,ROOT)
  self.assertTrue(c['inventoryComplete']);self.assertFalse(c['primaryPassed']);self.assertEqual(c['retainedRecords'],48);self.assertEqual(c['executionFailures'],48);self.assertEqual(c['budgetFailures'],1);self.assertEqual(c['scientificallyAvailable'],0)
  self.assertIsNone(c['resources']['largestSampledNodeProcessRSSBytes']);self.assertIsNotNone(c['resources']['nodeRSSUnavailableReason']);self.assertIsNone(c['resources']['largestApproximatelyPairedRSSBytes'])
  rows=json.loads((self.directory/'results.json').read_text())['records'];self.assertEqual([r['id'] for r in rows],[p['id'] for p in plans]);self.assertEqual(len(list((self.directory/'records').glob('*.json'))),48)
  with patch.object(runner,'verify',return_value=manifest),self.assertRaises(ValueError):runner.run(self.directory,ROOT)

if __name__=='__main__':unittest.main()
