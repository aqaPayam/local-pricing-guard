import copy,importlib.util,json,shutil,types,unittest,uuid
from pathlib import Path
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'research/benchmark-guard-reference.py';benchmark=types.ModuleType('reference_benchmark_fixture');benchmark.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),benchmark.__dict__)
class BenchmarkGate(unittest.TestCase):
 def messages(self):
  cps=[{'step':step,'matched':True,'worldStatesChecked':5*62**2,'canonicalDenseCellsPerFirm':5*62**3,'transcriptBlocksMatched':step//10000} for step in (1000000,2000000)]
  return [{'type':'checkpoint audited','result':cp} for cp in cps]+[{'type':'replay finished','result':{'fullHorizonReplayed':True,'replayedRounds':2000000,'allPlannedCheckpointsMatched':True,'allEligibleCheckpointsMatched':True,'finalConsumedIntegrityCheck':True,'transcriptBlocksMatched':200,'checkpointResults':cps}}]
 def encode(self,value):return ('\n'.join(json.dumps(v) for v in value)+'\n').encode()
 def test_complete_ndjson_requires_both_checkpoints_and_final_integrity(self):
  messages=self.messages();self.assertEqual(benchmark.parse_independent_messages(self.encode(messages))['replayedRounds'],2000000)
  for field in ('fullHorizonReplayed','allPlannedCheckpointsMatched','allEligibleCheckpointsMatched','finalConsumedIntegrityCheck'):
   bad=copy.deepcopy(messages);bad[-1]['result'][field]=False
   with self.assertRaises(ValueError):benchmark.parse_independent_messages(self.encode(bad))
 def test_missing_duplicate_partial_or_reordered_messages_are_rejected(self):
  messages=self.messages()
  for bad in [messages[:-1],messages+[messages[-1]],[messages[-1],*messages[:-1]],[messages[0],messages[-1]]]:
   with self.assertRaises(ValueError):benchmark.parse_independent_messages(self.encode(bad))
  with self.assertRaises(ValueError):benchmark.parse_independent_messages(self.encode(messages)[:-1])
 def test_single_json_legacy_schema_and_float_clock_cannot_pass(self):
  with self.assertRaises(ValueError):benchmark.parse_independent_messages(json.dumps({'fullHorizon':True,'replayedRounds':2000000}).encode()+b'\n')
  messages=self.messages();messages[0]['result']['step']=1000000.0
  with self.assertRaises(ValueError):benchmark.parse_independent_messages(self.encode(messages))
 def test_actual_production_supervisor_api_is_used_and_complete_or_failed_receipts_are_preserved(self):
  for fail in (False,True):
   directory=ROOT/'.local'/('reference-benchmark-api-test-'+uuid.uuid4().hex);directory.mkdir(parents=True)
   try:
    result={**self.messages()[-1]['result'],'supervisedSeconds':.25,'rssSamples':[{'approximatelyPairedRSSBytes':100}]}
    if fail:result['operationalFailure']='Artificial deadline failure'
    run=Mock(return_value=result);module=types.SimpleNamespace(run_replay=run)
    with patch.object(benchmark,'load_independent_parent',return_value=module):
     if fail:
      with self.assertRaises(ValueError):benchmark.independent_case('node',Path('artificial-task'),Path('artificial-record'),directory)
     else:self.assertTrue(benchmark.independent_case('node',Path('artificial-task'),Path('artificial-record'),directory)['passed'])
    run.assert_called_once_with('node',ROOT,directory,Path('artificial-task'),Path('artificial-record'),600)
    self.assertEqual(json.loads((directory/'independent-production-replay.json').read_bytes()),result)
   finally:shutil.rmtree(directory)
if __name__=='__main__':unittest.main()
