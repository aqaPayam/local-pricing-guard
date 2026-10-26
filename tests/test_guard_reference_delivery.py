"""Delivery CLI regression only: real report parser, stop before evidence IO."""
from pathlib import Path
import argparse,runpy,sys,types,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
class ReportCommand(unittest.TestCase):
 def test_actual_report_parser_receives_distinct_old_and_reference_audit_bindings(self):
  source=ROOT/'research/package-guard-reference.py';delivery=types.ModuleType('reference_delivery_command');delivery.__file__=str(source);exec(compile(source.read_bytes(),str(source),'exec'),delivery.__dict__)
  command=delivery.report_command(sys.executable);real_parse=argparse.ArgumentParser.parse_args;seen=[]
  class StopBeforeEvidence(Exception):pass
  def parse(parser,args=None,namespace=None):
   parsed=real_parse(parser,args,namespace)
   self.assertEqual(parsed.audit_sha,'a19425072110d514f7a0630383eaf2973f465204aa87d2edc3bb6350ae9864f6')
   self.assertEqual(parsed.reference_audit_sha,'2443c1f0874aac903c2125b68b47d6c7a7401d801969829b433d79a47e14bc7b')
   seen.append(True);raise StopBeforeEvidence()
  with patch.object(sys,'argv',command[2:]),patch.object(argparse.ArgumentParser,'parse_args',parse):
   with self.assertRaises(StopBeforeEvidence):runpy.run_path(str(ROOT/delivery.REPORT_BUILDER),run_name='__main__')
  self.assertEqual(seen,[True])
if __name__=='__main__':unittest.main()
