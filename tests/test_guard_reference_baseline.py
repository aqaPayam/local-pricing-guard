"""Invented baseline-binding fixtures; no project outcomes or checkpoints read."""
import hashlib
import json
from pathlib import Path
import shutil
import types
import unittest
from unittest import mock
import uuid

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/guard-reference-baseline.py'
M=types.ModuleType('guard_reference_baseline_tested')
M.__file__=str(SOURCE)
exec(compile(SOURCE.read_bytes(),str(SOURCE),'exec'),M.__dict__)
SHA=lambda b:hashlib.sha256(b).hexdigest()


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.parent=(ROOT/'.local').resolve();self.parent.mkdir(exist_ok=True)
        self.root=self.parent/('guard-baseline-invented-'+uuid.uuid4().hex);self.root.mkdir()
        self.finite=self.write('invented/physical.json',b'{"scope":"invented"}')
        self.other=self.write('invented/other.json',b'{"not":"physical"}')
        self.manifest=dict(inputs=dict(finiteGame=self.finite))
        self.manifestref=self.write(M.MANIFEST,self.bytes(self.manifest))
        self.audit=self.write(M.AUDIT,b'{"passed":true}')
        # This artificial builder stubs the already separately tested authority.
        # The helper's fixed identities, end checks and consumed refs are real.
        self.builder=self.write(M.BUILDER,b"import json\ndef load_accepted(path,sha,project):\n return json.loads(path.read_bytes())\n")
        endpoints=[dict(arm='startup',seed=s,runId=f'base-g15-t1--matched5-startup--zero--s{s}',available=True,replayMatched=True,step=2_000_000,nextPhase=4) for s in range(907001,907013)]
        self.summary=dict(meta=dict(inventoryAccepted=True,independentAuditPassed=True,fullTrainingReplay=True,replayComplete=True,primaryManifestSha256=self.manifestref['sha256'],replayedRounds=48_000_000,consumedFiles={r['file']:dict(bytes=r['bytes'],sha256=r['sha256']) for r in [self.finite,self.other]}),finalEndpoints=endpoints)
        self.summaryref=self.write(M.SUMMARY,self.bytes(self.summary))
        self.constants=mock.patch.multiple(M,BUILDER_SHA=self.builder['sha256'],SUMMARY_SHA=self.summaryref['sha256'],MANIFEST_SHA=self.manifestref['sha256'],AUDIT_SHA=self.audit['sha256'])
        self.constants.start()
    @staticmethod
    def bytes(value):return json.dumps(value,sort_keys=True).encode()
    def write(self,name,raw):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        return dict(file=name,bytes=len(raw),sha256=SHA(raw))
    def tearDown(self):
        self.constants.stop();self.assertEqual(self.root.resolve().parent,self.parent);self.assertTrue(self.root.name.startswith('guard-baseline-invented-'));shutil.rmtree(self.root)
    def test_complete_artificial_closure_keeps_twelve_old_slots(self):
        v=M.load_baseline(self.root)
        self.assertEqual(len(v['finalEndpoints']),12)
        self.assertEqual(v['finiteGame'],self.finite)
        self.assertEqual(len(v['consumedFiles']),6)
        self.assertEqual(v['inputHashes'][M.MANIFEST],self.manifestref['sha256'])
    def test_exact_manifest_parse_bytes_cannot_change_after_digest(self):
        original=Path.read_bytes;forged=self.bytes(dict(inputs=dict(finiteGame=self.other)))
        def reader(path):
            if path.resolve()==(self.root/M.MANIFEST).resolve():return forged
            return original(path)
        with mock.patch.object(Path,'read_bytes',reader):
            with self.assertRaisesRegex(ValueError,'manifest.*changed|manifest.*differ|Manifest.*changed|Manifest.*differ'):M.load_baseline(self.root)
    def test_fixed_hash_and_post_regeneration_consumed_hash_drift_reject(self):
        real=M.digest
        for changed in [M.BUILDER,self.finite['file']]:
            def digest(path):return '0'*64 if path.resolve()==(self.root/changed).resolve() else real(path)
            with mock.patch.object(M,'digest',digest):
                with self.assertRaises(ValueError):M.load_baseline(self.root)
    def test_unsafe_windows_and_noncanonical_paths_reject(self):
        for name in ['../escape','C:/escape','C:relative','invented/a:stream','invented\\a','/absolute','invented//a','invented/./a']:
            with self.assertRaises(ValueError,msg=name):M.local(self.root,name)
        self.assertEqual(M.local(self.root,self.finite['file']),self.root/self.finite['file'])


if __name__=='__main__':unittest.main()
