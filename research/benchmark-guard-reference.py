"""Prospective source-bound maximal artificial engineering benchmark.

Creates no inherited-market case, source freeze or actual evidence export.
Never retries a failed arm. Primary and independently authored replay run serially.
"""
from pathlib import Path
import argparse,types,json,shutil,subprocess,time,traceback,uuid
ROOT=Path(__file__).resolve().parent.parent
path=ROOT/'research/run-guard-reference.py';parent=types.ModuleType('reference_benchmark_parent');parent.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),parent.__dict__)
def run_json(arguments,timeout=30):return json.loads(subprocess.check_output(arguments,cwd=ROOT,timeout=timeout))
def validate_independent_result(value):
 checkpoints=value.get('checkpointResults',[])
 parent.require(not value.get('operationalFailure') and value.get('fullHorizonReplayed') is True and type(value.get('replayedRounds')) is int and value['replayedRounds']==2_000_000 and value.get('allPlannedCheckpointsMatched') is True and value.get('allEligibleCheckpointsMatched') is True and value.get('finalConsumedIntegrityCheck') is True and value.get('transcriptBlocksMatched')==200 and len(checkpoints)==2 and all(c.get('matched') is True and type(c.get('step')) is int and c.get('worldStatesChecked')==5*62**2 and c.get('canonicalDenseCellsPerFirm')==5*62**3 for c in checkpoints) and [c['step'] for c in checkpoints]==[1_000_000,2_000_000] and [c.get('transcriptBlocksMatched') for c in checkpoints]==[100,200],'Independent maximal checkpoint replay did not fully pass')
 return value
def parse_independent_messages(out):
 parent.require(isinstance(out,bytes) and out.endswith(b'\n'),'Independent replay NDJSON is incomplete');messages=[json.loads(line) for line in out.splitlines()]
 parent.require(len(messages)==3 and [m.get('type') for m in messages]==['checkpoint audited','checkpoint audited','replay finished'],'Independent complete checkpoint/final message order differs')
 value=validate_independent_result(messages[-1]['result']);parent.require([m['result'] for m in messages[:-1]]==value['checkpointResults'],'Independent checkpoint/final duplication differs')
 return value
def load_independent_parent():
 return parent.load_local_module(ROOT,'research/audit-guard-reference-study.py')
def independent_case(node,task_file,record_file,directory):
 # Exercise the independently authored PRODUCTION Python supervisor too; do not
 # substitute a benchmark-only Popen/timeout/NDJSON transport implementation.
 independent=load_independent_parent()
 value=independent.run_replay(node,ROOT,directory,task_file,record_file,600);ref=parent.save(directory,'independent-production-replay.json',value)
 validate_independent_result(value)
 parent.require(value.get('supervisedSeconds',601)<600 and isinstance(value.get('rssSamples'),list) and len(value['rssSamples'])>0,'Production replay supervision/resource receipt incomplete')
 return {'passed':True,'seconds':value['supervisedSeconds'],'receipt':ref,'rssSamples':value['rssSamples'],'result':value,'scope':'Actual independent production Python supervisor and Node numerical replay, same pinned V8/SHA backend; artificial workload only'}
def benchmark(output,directory):
 output=Path(output).resolve();directory=Path(directory).resolve();parent.require(directory.is_relative_to(ROOT/'.local') and not directory.exists(),'New workspace-local benchmark directory required');parent.require(not output.exists(),'Existing artificial benchmark receipt preserved')
 parent.require((ROOT/'research/replay-guard-reference.js').exists(),'Independent production replay source not ready; benchmark not started')
 node=shutil.which('node');parent.require(node,'Node24 executable required');source_command=[node,'research/guard-reference-study.js','sources'];before=run_json(source_command);directory.mkdir(parents=True)
 for name,h in before.items():
  source=parent.local(ROOT,name);parent.require(parent.digest(source)==h,'Initial source drift');parent.save(directory,'sources/'+name,source.read_bytes())
 software=run_json([node,'research/guard-reference-study.js','runtime']);python_runtime=parent.parent_runtime();runtime_ref=parent.save(directory,'parent-runtime.json',python_runtime)
 record=run_json([node,'--input-type=module','-e',"import {syntheticMatchedRecord} from './research/matched-clock-learning.js';process.stdout.write(JSON.stringify(syntheticMatchedRecord(62))); "])
 finite_ref=parent.save(directory,'artificial-record.json',record);finite_project_ref={**finite_ref,'file':(directory/finite_ref['file']).relative_to(ROOT).as_posix()};plan=run_json([node,'research/guard-reference-study.js','plan']);rows=[];began=time.perf_counter();failures=[]
 for arm in ('startup',):
  arm_dir=directory/arm;arm_dir.mkdir();chosen=next(p for p in plan if p['seed']==907001 and p['arm']==arm);chosen={**chosen,'id':'artificial--'+chosen['id']}
  task={'plan':chosen,'scientificTreatment':parent.SCIENTIFIC_TREATMENT.copy(),'record':record,'finite':record['finite'],'originalTargets':[],'finiteGameRef':finite_project_ref,'software':software,'T':2_000_000,'checkpoints':[1_000_000,2_000_000],'executionMode':'artificial','projectRoot':'.'}
  try:
   anchors=parent.load_local_module(ROOT,'research/guard-reference-analysis.py').stage_anchors(record['finite']);anchor_ref=parent.save(directory,'artificial-stage-anchors.json',anchors);independent_anchors=load_independent_parent().check_anchors(node,ROOT,record,anchors);parent.save(directory,'independent-artificial-stage-anchors.json',independent_anchors)
   primary=parent.supervise(task,arm_dir,ROOT,budget_seconds=600,node=node);primary_ref=parent.save(arm_dir,'primary-run.json',primary);parent.require(primary['executionSucceeded'] and all(c['parentEligible'] for c in primary['checkpoints']),'Artificial primary transport/case failed')
   raw_equivalent=0
   for cp in primary['checkpoints']:
    meta=json.loads(parent.readref(arm_dir,cp['metadata']));raw_equivalent+=sum(r['rawBytes'] for refs in meta['artifacts'].values() for r in refs)
   replay=independent_case(node,arm_dir/primary['task']['file'],arm_dir/primary_ref['file'],arm_dir);rows.append({'arm':arm,'passed':True,'primary':primary_ref,'primarySeconds':primary['seconds'],'primaryRSS':primary['rssSamples'],'canonicalDenseCheckpointBytes':raw_equivalent,'replay':replay})
  except Exception as exc:
   failures.append({'arm':arm,'message':str(exc),'traceback':traceback.format_exc()});rows.append({'arm':arm,'passed':False,'reason':str(exc)})
 after=run_json(source_command);sources_unchanged=before==after;artifacts=[]
 for p in sorted(directory.rglob('*')):
  if p.is_file():artifacts.append({'file':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':parent.digest(p)})
 value={'passed':len(rows)==1 and all(r['passed'] for r in rows) and sources_unchanged,'artificial':True,'scientificTreatment':parent.SCIENTIFIC_TREATMENT.copy(),'n':62,'rounds':2_000_000,'arms':rows,'fullIndependentReplay':len(rows)==1 and all(r['passed'] for r in rows),'sourceHashes':before,'finalSourceHashes':after,'sourcesUnchanged':sources_unchanged,'parentRuntime':python_runtime,'parentRuntimeReceipt':{**runtime_ref,'file':(directory/runtime_ref['file']).relative_to(ROOT).as_posix()},'directory':directory.relative_to(ROOT).as_posix(),'artifacts':artifacts,'failures':failures,'seconds':time.perf_counter()-began,'scope':'Wholly invented62-quote signed/zero-profit model; dense primary, transcript encoding/hashing, two full-support checkpoints, graph/gzip/strict parent validation and independent full replay. Engineering feasibility only; no inherited market outcomes, freeze or real training.'}
 output.parent.mkdir(parents=True,exist_ok=True)
 with output.open('xb') as f:f.write(parent.encode(value))
 return {'passed':value['passed'],'receipt':output.relative_to(ROOT).as_posix(),'sha256':parent.digest(output),'directory':value['directory'],'seconds':value['seconds'],'sourceFiles':len(before),'artifacts':len(artifacts)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default=str(ROOT/'.local/guard-reference-benchmark.json'));p.add_argument('--directory',default=str(ROOT/'.local'/('guard-reference-final-benchmark-'+uuid.uuid4().hex)));a=p.parse_args();print(json.dumps(benchmark(a.output,a.directory)))
