import copy,gzip,hashlib,importlib.util,json,shutil,struct,subprocess,time,unittest,uuid
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent.parent
import types
p=ROOT/'research/run-guard-reference.py';parent=types.ModuleType('reference_primary_parent');parent.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),parent.__dict__)

class Transport(unittest.TestCase):
 def setUp(self):
  self.root=ROOT/'.local'/('reference-parent-test-'+uuid.uuid4().hex);self.root.mkdir(parents=True)
  self.finite={'prices':[1,2],'capIndex':0,'sets':[[0],[1]],'rewards':{'profitA':[0]*4,'profitB':[0]*4,'consumerSurplus':[1]*4}}
  self.task={'plan':{'id':'artificial-startup','arm':'startup','seed':907001,'actors':[[1,2,3,4],[5,6,7,8]]},'finite':self.finite,'finiteGameRef':{'file':'artificial.json','sha256':'a'*64,'bytes':1},'software':{'artificial':True},'T':20,'checkpoints':[10,20]}
  self.task['scientificTreatment']=parent.SCIENTIFIC_TREATMENT.copy();self.task['plan'].update(treatment=parent.TREATMENT,scientificTreatment=parent.SCIENTIFIC_TREATMENT.copy());self.task['record']={'finite':self.finite}
 def tearDown(self):shutil.rmtree(self.root)
 def dense(self,name,raw,encoding,n=2):
  ref=parent.save(self.root,name,gzip.compress(raw,mtime=0));return {**ref,'encoding':encoding,'compression':'gzip-single-member','rawBytes':len(raw),'rawSha256':hashlib.sha256(raw).hexdigest()}
 def fixture(self,step=10):
  counts=[0]*40;transitions={};previous=1
  for t in range(step):
   phase=0 if t==0 else 1+(t-1)%4;row=(phase*2+previous)*2+previous;counts[row*2]+=1;key=row*4;transitions[key]=transitions.get(key,0)+1;previous=0
  artifacts={'q':[self.dense(f'q{f}.gz',bytes(320),'f64le') for f in range(2)],'counts':[self.dense(f'c{f}.gz',struct.pack('<40I',*counts),'u32le') for f in range(2)]}
  windows=[{'startStep':0,'endStep':end,'rounds':step,'transitions':sorted([k,v] for k,v in transitions.items()),'maxAllowed':[1,1],'explorations':[0,0],'priceChanges':[1,1],'capExecutions':1} for end in (10,20)]
  m={'schemaVersion':1,**{k:self.task['plan'][k] for k in ('id','arm','seed')},'step':step,'n':2,'phases':5,'layout':parent.LAYOUT,'finiteGameRef':self.task['finiteGameRef'],'learning':{'T':20,'alpha':.1,'gamma':19/20,'initialization':'positive-zero'},'software':self.task['software'],'allocation':{'cellsPerFirm':40,'qBytesPerFirm':320,'countBytesPerFirm':160},'terminal':{'phase':1+(step-1)%4,'previousIndices':[0,0]},'caps':1,'actors':[parent.advanced_actor(a,2*step) for a in self.task['plan']['actors']],'artifacts':artifacts,'windows':windows,'transcriptBlocks':[],'transcriptPartial':{'rounds':step,'bytes':step*120,'sha256':'b'*64},'graph':parent.save(self.root,'graph.json',{'scientificTreatment':parent.SCIENTIFIC_TREATMENT,'floor':None,'cycles':[{'floorApplies':None,'floorGap':None}],'actualTerminal':{'floorApplies':None,'floorGap':None},'freshCapCounterfactual':{'floorApplies':None,'floorGap':None}})}
  compact=lambda v:hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
  declaration={'schemaVersion':1,'treatment':parent.TREATMENT,'clock':'startup-only-five-phase','initialCap':'original physical cap; phase0 only','laterPhases':[1,2,3,4],'laterSupport':'all original price indices, independent of previous rival','originalIndexRange':[0,1],'originalCapIndex':0,'originalGuardMasksSha256':compact(self.finite['sets']),'physicalRecordUnchanged':True,'floorTransferred':False,'scope':'Initial cap, unrestricted thereafter over the original price grid; no inherited guard floor','effectiveSupportsSha256':compact([[[0],[0]]]+[[[0,1],[0,1]]]*4)}
  m.update(treatment=parent.TREATMENT,scientificTreatment=parent.SCIENTIFIC_TREATMENT.copy(),supportTreatment=declaration)
  g=json.loads((self.root/m['graph']['file']).read_bytes());g['supportTreatment']=declaration;name='graph-complete-'+uuid.uuid4().hex+'.json';m['graph']=parent.save(self.root,name,g)
  m['policies']={key:[parent.save(self.root,f'{key}-{f}.u8',bytes(20)) for f in range(2)] for key in ('own','world')};m['cacheIdentity']={'best':[hashlib.sha256(bytes(20)).hexdigest()]*2,'maximum':[hashlib.sha256(bytes(160)).hexdigest()]*2}
  def ratio(n=0,d=1):
   import fractions
   r=fractions.Fraction(n,d);return {'numerator':str(r.numerator),'denominator':str(r.denominator),'approximate':float(r)}
  metrics={'consumerSurplus':ratio(1),'capRuleFrequency':ratio(1,step),'profits':[ratio(),ratio()],'prices':[ratio(1),ratio(1)],'maskCount':[ratio(2*step-1,step)]*2,'maskFraction':[ratio(2*step-1,step*2)]*2,'maskSpan':[ratio(step-1,step)]*2,'maxAllowedUsage':[ratio(1,step)]*2,'explorationFrequency':[ratio(),ratio()],'priceChangeFrequency':[ratio(1,step)]*2}
  metrics={key:({'A':value[0],'B':value[1]} if isinstance(value,list) else value) for key,value in metrics.items()}
  m['windowMetrics']=[{'startStep':0,'endStep':end,'rounds':step,'metrics':copy.deepcopy(metrics),'reason':None} for end in (10,20)]
  return m,parent.save(self.root,'metadata.json',m)
 def test_scientific_support_types_and_transferred_floors_are_rejected(self):
  original,_=self.fixture()
  for mutate in [lambda m:m['scientificTreatment'].__setitem__('initialCap',1),lambda m:m['supportTreatment'].__setitem__('floorTransferred',True),lambda m:m.__setitem__('treatment','startup-guard')]:
   bad=copy.deepcopy(original);mutate(bad);ref=parent.save(self.root,'wrong-treatment-'+uuid.uuid4().hex+'.json',bad)
   with self.assertRaises(ValueError):parent.validate_checkpoint(self.root,ref,self.task)
  for change in [{'floor':{'guardApplies':True}},{'cycles':[{'floorApplies':False,'floorGap':None}]}]:
   bad=copy.deepcopy(original);graph=json.loads((self.root/bad['graph']['file']).read_bytes());graph.update(change);bad['graph']=parent.save(self.root,'wrong-floor-'+uuid.uuid4().hex+'.json',graph);ref=parent.save(self.root,'wrong-floor-meta-'+uuid.uuid4().hex+'.json',bad)
   with self.assertRaises(ValueError):parent.validate_checkpoint(self.root,ref,self.task)
 def test_strict_gzip_full_dimensions_and_single_member(self):
  m,ref=self.fixture();self.assertEqual(parent.validate_checkpoint(self.root,ref,self.task)['step'],10)
  q=m['artifacts']['q'][0];raw=parent.strict_dense(self.root,q,2,'f64le');self.assertEqual(len(raw),320)
  for suffix in [b'x',(self.root/q['file']).read_bytes()]:
   bad=(self.root/q['file']).read_bytes()+suffix;r=parent.save(self.root,'bad-'+uuid.uuid4().hex+'.gz',bad);r.update({k:q[k] for k in ('encoding','compression','rawBytes','rawSha256')})
   with self.assertRaises(ValueError):parent.strict_dense(self.root,r,2,'f64le')
  for patch in [{'rawBytes':312},{'rawSha256':'0'*64}]:
   with self.assertRaises(ValueError):parent.strict_dense(self.root,{**q,**patch},2,'f64le')
 def test_checkpoint_actor_clock_counter_and_forbidden_corruptions(self):
  m,_=self.fixture()
  for patch in [{'step':10.0},{'actors':[[0,0,0,0]]*2},{'terminal':{'phase':2.0,'previousIndices':[0,0]}},{'caps':True},{'caps':2},{'learning':{'T':20,'alpha':.2,'gamma':.95,'initialization':'positive-zero'}}]:
   bad={**m,**patch};ref=parent.save(self.root,'bad-'+uuid.uuid4().hex+'.json',bad)
   with self.assertRaises(ValueError):parent.validate_checkpoint(self.root,ref,self.task)
  raw=bytearray(320);struct.pack_into('<d',raw,8,-0.0);bad=copy.deepcopy(m);bad['artifacts']['q'][0]=self.dense('minuszero.gz',raw,'f64le')
  with self.assertRaises(ValueError):parent.validate_checkpoint(self.root,parent.save(self.root,'minuszero.json',bad),self.task)
  bad=copy.deepcopy(m);bad['windows'][0]['maxAllowed']=[0,0]
  with self.assertRaises(ValueError):parent.validate_checkpoint(self.root,parent.save(self.root,'bad-geometry.json',bad),self.task)
 def test_actor_linear_skip_matches_literal_unsigned_transition(self):
  state=[1,2,3,4];v=sum(x<<(32*i) for i,x in enumerate(state))
  for _ in range(113):v=parent.rng_transition(v)
  self.assertEqual(parent.advanced_actor(state,113),[(v>>(32*i))&0xffffffff for i in range(4)])
 def child(self,text):
  p=self.root/('child-'+uuid.uuid4().hex+'.cjs');p.write_text(text,encoding='utf-8');return p
 def supervise(self,text,budget=2,validator=lambda *args:{}):
  return parent.supervise(self.task,self.root,ROOT,budget_seconds=budget,case_source=self.child(text),validator=validator)
 def test_success_requires_both_validated_checkpoints_ack_and_natural_exit(self):
  text="let s=10;const send=()=>console.log(JSON.stringify({type:'checkpoint',step:s,metadata:{file:'fake',bytes:1,sha256:'a'.repeat(64)}}));process.stdin.on('data',()=>{if(s===10){s=20;send()}else{console.log(JSON.stringify({type:'done'}));process.exit(0)}});send();"
  r=self.supervise(text);self.assertTrue(r['executionSucceeded']);self.assertEqual([c['parentEligible'] for c in r['checkpoints']],[True,True]);self.assertTrue(all(not c['scientificAvailable'] for c in r['checkpoints']))
 def test_watchdog_kills_during_blocking_validation_and_never_salvages(self):
  def slow(*args):time.sleep(.5);return {}
  text="console.log(JSON.stringify({type:'checkpoint',step:10,metadata:{}}));setInterval(()=>{},1000);"
  r=self.supervise(text,.3,slow);self.assertEqual(r['status'],'timeout');self.assertFalse(any(c['parentEligible'] for c in r['checkpoints']));self.assertTrue(any(e['type']=='deadline termination requested' for e in r['events']))
 def test_valid_checkpoint_survives_later_failure_but_remains_replay_pending(self):
  text="console.log(JSON.stringify({type:'checkpoint',step:10,metadata:{}}));process.stdin.once('data',()=>process.exit(7));"
  r=self.supervise(text);self.assertFalse(r['executionSucceeded']);self.assertTrue(r['checkpoints'][0]['parentEligible']);self.assertFalse(r['checkpoints'][1]['parentEligible']);self.assertFalse(r['checkpoints'][0]['scientificAvailable'])
 def test_done_or_exit_alone_cannot_create_a_checkpoint(self):
  r=self.supervise("console.log(JSON.stringify({type:'done'}));process.exit(0)");self.assertFalse(r['executionSucceeded']);self.assertFalse(any(c['parentEligible'] for c in r['checkpoints']))
 def test_rejected_secondary_checkpoint_does_not_suppress_later_final(self):
  text="let s=10;const send=()=>console.log(JSON.stringify({type:'checkpoint',step:s,metadata:{}}));process.stdin.on('data',()=>{if(s===10){s=20;send()}else{console.log(JSON.stringify({type:'done'}));process.exit(0)}});send();"
  counter=[0]
  def validator(*args):
   counter[0]+=1
   if counter[0]==1:raise ValueError('artificial secondary rejection')
   return {}
  r=self.supervise(text,validator=validator);self.assertFalse(r['executionSucceeded']);self.assertFalse(r['checkpoints'][0]['parentEligible']);self.assertTrue(r['checkpoints'][1]['parentEligible'])
 def test_real_primary_adapter_interoperability_on_wholly_artificial_game(self):
  self.task['software']=json.loads(subprocess.check_output([shutil.which('node'),'research/matched-clock-study.js','runtime'],cwd=ROOT))
  self.task['executionMode']='artificial'
  r=parent.supervise(self.task,self.root,ROOT,budget_seconds=10)
  self.assertTrue(r['executionSucceeded'],r);self.assertTrue(all(c['parentEligible'] for c in r['checkpoints']))
 def wrapper_fixture(self):
  project=self.root/'project';project.mkdir();directory=project/'study';directory.mkdir();(directory/'sources').mkdir()
  raw={'scenario':{'id':'base-g15-t1'},'finite':{'prices':list(range(62))}}
  ref=parent.save(project,'artificial.json',raw)
  plans=[{'id':f'artificial-{arm}-{seed}','arm':arm,'seed':seed,'treatment':parent.TREATMENT,'scientificTreatment':parent.SCIENTIFIC_TREATMENT.copy()} for seed in range(907001,907013) for arm in ('startup',)]
  checker_hashes={'research/audit-guard-reference-study.py':'c'*64,'research/replay-guard-reference.js':'d'*64,'research/audit-guard-reference.js':'e'*64}
  manifest={'sourceHashes':checker_hashes,'parentRuntime':parent.parent_runtime(),'runtime':{'artificial':True},'inputs':{'finiteGame':ref},'plan':{'runs':plans,'T':2000000,'checkpoints':[1000000,2000000],'hardCaseSeconds':600,'scientificTreatment':parent.SCIENTIFIC_TREATMENT.copy()}}
  parent.save(directory,'manifest.json',manifest);gate=project/'admin.json';gate.write_bytes(parent.encode({'passed':True,'studyManifestHash':parent.digest(directory/'manifest.json'),'sourcesVerified':True,'inputsVerified':True,'auditorSourceHash':'c'*64,'controlAuditorSourceHash':'d'*64,'replayCoreSourceHash':'e'*64}));return project,directory,gate
 def fake_failed_case(self,task,*args,**kwargs):
  p=task['plan'];return {'id':p['id'],'arm':p['arm'],'seed':p['seed'],'status':'failure','executionSucceeded':False,'events':[],'rssSamples':[],'failure':{'message':'Artificial retained failure'},'checkpoints':[{'step':s,'metadata':None,'parentEligible':False,'scientificAvailable':False,'reason':'Artificial unavailable'} for s in task['checkpoints']]}
 def test_full12_failed_inventory_retains24_slots_and_refuses_rerun(self):
  project,directory,gate=self.wrapper_fixture();ok=subprocess.CompletedProcess([],0,'{"passed":true}','')
  with patch.object(parent.subprocess,'run',return_value=ok),patch.object(parent,'supervise',side_effect=self.fake_failed_case):r=parent.run_inventory(directory,gate,project)
  self.assertTrue(r['inventoryComplete']);self.assertFalse(r['primaryPassed']);self.assertEqual((r['retainedRuns'],r['retainedCheckpointSlots'],r['executionFailures']),(12,24,12));self.assertFalse(r['fullTrainingReplay']);self.assertEqual(len(json.loads((directory/'results.json').read_text())['records']),12)
  with self.assertRaises(ValueError):parent.run_inventory(directory,gate,project)
 def test_final_dependency_failure_is_retained_after_all12_rows(self):
  project,directory,gate=self.wrapper_fixture();responses=[subprocess.CompletedProcess([],0,'{"passed":true}',''),subprocess.CompletedProcess([],1,'','Artificial source drift')]
  with patch.object(parent.subprocess,'run',side_effect=responses),patch.object(parent,'supervise',side_effect=self.fake_failed_case):r=parent.run_inventory(directory,gate,project)
  self.assertTrue(r['inventoryComplete']);self.assertFalse(r['finalFrozenDependencyCheck']['passed']);self.assertEqual(r['retainedRuns'],12)
 def test_absent_or_false_administrative_gate_cannot_start_execution(self):
  project,directory,gate=self.wrapper_fixture();value=json.loads(gate.read_text());value['inputsVerified']=False;gate.write_bytes(parent.encode(value))
  with self.assertRaises(ValueError):parent.run_inventory(directory,gate,project)
  self.assertFalse((directory/'execution-start.json').exists())
 def test_stray_study_files_and_inside_administrative_receipts_reject_before_execution(self):
  project,directory,gate=self.wrapper_fixture();extra=directory/'auxiliary.txt';extra.write_text('artificial stray')
  with self.assertRaisesRegex(ValueError,'only manifest'):parent.run_inventory(directory,gate,project)
  extra.unlink();inside=directory/'sources'/'admin.json';inside.write_bytes(gate.read_bytes())
  with self.assertRaisesRegex(ValueError,'outside the evidence'):parent.run_inventory(directory,inside,project)
  self.assertFalse((directory/'execution-start.json').exists())

if __name__=='__main__':unittest.main()
