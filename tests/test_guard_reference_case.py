"""Actual production child transport with wholly invented inputs; no old data."""
import json
from pathlib import Path
import shutil
import subprocess
import uuid
import unittest

ROOT=Path(__file__).resolve().parents[1]
NODE=shutil.which('node')


class ChildTests(unittest.TestCase):
    def test_rejected_secondary_ack_still_retains_complete_final_and_treatment(self):
        self.assertIsNotNone(NODE)
        runtime=subprocess.run([NODE,str(ROOT/'research/matched-clock-study.js'),'runtime'],
            cwd=ROOT,capture_output=True,text=True,check=True)
        treatment=dict(capClock='startup',supportMode='full-grid-after-cap',initialCap=True,postInitialOriginalIndices='all')
        record=dict(finite=dict(prices=[1,2,3],capIndex=1,sets=[[0],[0,1],[1]],
                    rewards=dict(profitA=[-2,0,1,3,-1,2,0,1,0],profitB=[1,-3,0,0,2,-1,4,0,1],consumerSurplus=[9,8,7,8,6,5,7,5,3])))
        # Keep the explicitly named artificial directory inside the workspace;
        # restricted Windows runners may not permit descendants of system TEMP.
        scratch=ROOT/'.local';scratch.mkdir(exist_ok=True)
        directory=scratch/('guard-reference-child-artificial-'+uuid.uuid4().hex)
        directory.mkdir()
        try:
            (directory/'tasks').mkdir()
            self.assertEqual(directory.resolve().parent,scratch.resolve())
            task=dict(executionMode='artificial',scientificTreatment=treatment,
                      plan=dict(id='artificial-reference',seed=907001,arm='startup',treatment='full-grid-after-cap',scientificTreatment=treatment,actors=[[11,22,33,44],[55,66,77,88]]),
                      T=20000,checkpoints=[10000,20000],record=record,finite=record['finite'],
                      finiteGameRef=dict(file='artificial-only.json',bytes=0,sha256='0'*64),software=json.loads(runtime.stdout))
            filename=directory/'tasks/task.json';filename.write_text(json.dumps(task),encoding='utf-8')
            child=subprocess.run([NODE,str(ROOT/'research/guard-reference-case.js'),str(filename)],cwd=ROOT,
                input=json.dumps(dict(type='reject',step=10000))+'\n'+json.dumps(dict(type='ack',step=20000))+'\n',
                capture_output=True,text=True,timeout=20)
            self.assertEqual(child.returncode,0,child.stdout+child.stderr)
            messages=[json.loads(line) for line in child.stdout.splitlines()]
            checkpoints=[m for m in messages if m['type']=='checkpoint']
            self.assertEqual([m['step'] for m in checkpoints],[10000,20000])
            self.assertEqual(messages[-1]['type'],'done')
            self.assertFalse(any(m['type'] in ('checkpoint-failure','failure') for m in messages))
            for message in checkpoints:
                meta=json.loads((directory/message['metadata']['file']).read_text())
                self.assertEqual(meta['scientificTreatment'],treatment)
                self.assertEqual(meta['terminal']['phase'],4)
                self.assertEqual(meta['caps'],1)
                self.assertEqual(len(meta['transcriptBlocks']),message['step']//10000)
                graph=json.loads((directory/meta['graph']['file']).read_text())
                self.assertIsNone(graph['floor'])
                self.assertTrue(all(c['floorApplies'] is None and c['floorGap'] is None for c in graph['cycles']))
        finally:
            self.assertEqual(directory.resolve().parent,scratch.resolve())
            self.assertTrue(directory.name.startswith('guard-reference-child-artificial-'))
            shutil.rmtree(directory)


if __name__=='__main__':unittest.main()
