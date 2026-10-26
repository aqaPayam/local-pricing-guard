"""Invented exact-payoff and endpoint fixtures only; no project outcomes read."""
from pathlib import Path
import copy
from fractions import Fraction
import types
import unittest

PATH = Path(__file__).resolve().parents[1]/'research/guard-reference-analysis.py'
M = types.ModuleType('guard_reference_analysis')
M.__file__ = str(PATH)
exec(compile(PATH.read_bytes(),str(PATH),'exec'),M.__dict__)


def game(a,b,cs=None):
    return dict(prices=[1,2],rewards=dict(profitA=a,profitB=b,consumerSurplus=cs or [8,7,6,5]))


def endpoints(treatment):
    out=[]
    for index,seed in enumerate(M.SEEDS):
        value=Fraction(10)
        if treatment=='full-grid-after-cap':
            value += Fraction(([-1,0]+[1]*10)[index])
        out.append(dict(seed=seed,runId=M.expected_id(seed,treatment),available=True,replayMatched=True,
                        executionSucceeded=True,step=2_000_000,nextPhase=4,previousIndices=[1,2],cycleLength=4,
                        checkpointSha256='a'*64,graphSha256='b'*64,cycleCustomerBenefit=M.packed(value),unavailableReason=None))
    return out


class AnchorTests(unittest.TestCase):
    def test_all_coordination_equilibria_and_joint_maximum(self):
        x=M.stage_anchors(game([3,0,0,2],[3,0,0,2]))
        self.assertEqual([p['indices'] for p in x['pureNash']['pairs']],[[0,0],[1,1]])
        self.assertEqual([p['indices'] for p in x['jointProfitMaximum']['pairs']],[[0,0]])
        self.assertEqual(x['jointProfitMaximum']['value'],{'numerator':'6','denominator':'1'})

    def test_world_B_orientation_has_asymmetric_equilibrium(self):
        x=M.stage_anchors(game([0,3,1,2],[4,0,5,1]))
        self.assertEqual([p['indices'] for p in x['pureNash']['pairs']],[[1,0]])
        self.assertEqual(x['bestResponses']['BByRivalA'],[[0],[0]])
        self.assertEqual(x['pureNash']['pairs'][0]['profits']['B'],M.packed(Fraction(5)))

    def test_no_pure_nash_and_all_joint_objective_ties(self):
        x=M.stage_anchors(game([1,-1,-1,1],[-1,1,1,-1]))
        self.assertEqual(x['pureNash']['count'],0)
        self.assertIsNotNone(x['pureNash']['reason'])
        self.assertEqual(x['jointProfitMaximum']['count'],4)
        self.assertEqual(x['jointProfitMaximum']['value'],M.packed(Fraction()))

    def test_joint_sum_is_not_rounded_binary64_addition(self):
        huge=float(2**53)
        self.assertEqual(huge+1.,huge)
        x=M.stage_anchors(game([huge,huge,0.,0.],[0.,1.,0.,0.]))
        self.assertEqual([p['indices'] for p in x['jointProfitMaximum']['pairs']],[[0,1]])
        self.assertEqual(x['jointProfitMaximum']['value'],M.packed(Fraction(2**53+1)))

    def test_signed_zero_ties_and_invalid_saved_numbers(self):
        x=M.stage_anchors(game([0.,-0.,0.,-0.],[-0.,0.,-0.,0.]))
        self.assertEqual((x['pureNash']['count'],x['jointProfitMaximum']['count']),(4,4))
        for mutate in [lambda g:g['rewards']['profitA'].__setitem__(0,float('nan')),
                       lambda g:g['rewards']['profitB'].pop(),
                       lambda g:g.__setitem__('prices',[2,1]),
                       lambda g:g['rewards']['consumerSurplus'].__setitem__(1,True)]:
            g=game([1,2,3,4],[4,3,2,1]);mutate(g)
            with self.assertRaises(ValueError):M.stage_anchors(g)


class AggregationTests(unittest.TestCase):
    def test_all_twelve_exact_rows_and_signed_mean(self):
        r=M.aggregate(endpoints('full-grid-after-cap'),endpoints('startup-guard'))
        self.assertEqual(r['primarySummary']['meanDifference'],M.packed(Fraction(3,4)))
        self.assertEqual([p['seed'] for p in r['pairedRows']],list(M.SEEDS))
        self.assertEqual(r['completePairDescription']['signCounts'],dict(positive=10,zero=1,negative=1))

    def test_missing_final_nulls_planned_mean_and_preserves_reason(self):
        new,old=endpoints('full-grid-after-cap'),endpoints('startup-guard')
        new[0].update(available=False,replayMatched=False,cycleCustomerBenefit=None,unavailableReason='Invented retained final failure')
        r=M.aggregate(new,old)
        self.assertFalse(r['primarySummary']['available'])
        self.assertIsNone(r['primarySummary']['meanDifference'])
        self.assertEqual(r['primarySummary']['plannedDenominator'],12)
        self.assertEqual(r['completePairDescription']['denominator'],11)
        self.assertEqual(len(r['pairedRows']),12)
        self.assertIn('Invented retained final failure',r['pairedRows'][0]['unavailableReason'])

    def test_no_available_pairs_keeps_twelve_rows_and_null_secondary_mean(self):
        new,old=endpoints('full-grid-after-cap'),endpoints('startup-guard')
        for collection in (new,old):
            for row in collection:
                row.update(available=False,replayMatched=False,executionSucceeded=False,
                           cycleCustomerBenefit=None,unavailableReason='Invented unavailable endpoint')
        r=M.aggregate(new,old)
        self.assertEqual(len(r['pairedRows']),12)
        self.assertEqual(r['primarySummary']['plannedDenominator'],12)
        self.assertIsNone(r['primarySummary']['meanDifference'])
        self.assertEqual(r['completePairDescription']['denominator'],0)
        self.assertEqual(r['completePairDescription']['seedIds'],[])
        self.assertIsNone(r['completePairDescription']['meanDifference'])
        self.assertEqual(r['completePairDescription']['signCounts'],dict(positive=0,zero=0,negative=0))

    def test_accepted_checkpoint_after_execution_failure_stays_scientifically_available(self):
        new,old=endpoints('full-grid-after-cap'),endpoints('startup-guard')
        new[0]['executionSucceeded']=False
        old[1]['executionSucceeded']=False
        r=M.aggregate(list(reversed(new)),list(reversed(old)))
        self.assertTrue(r['primarySummary']['available'])
        self.assertEqual(r['primarySummary']['meanDifference'],M.packed(Fraction(3,4)))
        self.assertEqual(r['pairedRows'][0]['executionSucceeded'],[True,False])
        self.assertEqual(r['pairedRows'][1]['executionSucceeded'],[False,True])
        self.assertEqual([row['seed'] for row in r['pairedRows']],list(M.SEEDS))

    def test_tiny_exact_signs_and_cancellation_do_not_underflow_into_zero(self):
        new,old=endpoints('full-grid-after-cap'),endpoints('startup-guard')
        tiny=Fraction(1,2**1100)
        for i,row in enumerate(new):
            row['cycleCustomerBenefit']=M.packed(Fraction(10)+(tiny if i==0 else -tiny if i==1 else 0))
        r=M.aggregate(new,old)
        self.assertEqual(r['completePairDescription']['signCounts'],dict(positive=1,zero=10,negative=1))
        self.assertEqual(r['pairedRows'][0]['difference'],M.packed(tiny))
        self.assertEqual(r['pairedRows'][1]['difference'],M.packed(-tiny))
        self.assertEqual(r['primarySummary']['meanDifference'],M.packed(Fraction()))

    def test_identity_phase_exact_fraction_and_replay_corruptions_reject(self):
        changes=[lambda x:x.__setitem__('runId','wrong'),lambda x:x.__setitem__('nextPhase',0),
                 lambda x:x.__setitem__('replayMatched',False),
                 lambda x:x.__setitem__('cycleCustomerBenefit',{'numerator':'20','denominator':'2'}),
                 lambda x:x.__setitem__('cycleLength',3),lambda x:x.__setitem__('executionSucceeded',1)]
        for mutate in changes:
            new,old=endpoints('full-grid-after-cap'),endpoints('startup-guard');mutate(new[0])
            with self.assertRaises(ValueError):M.aggregate(new,old)
        new=endpoints('full-grid-after-cap');new[-1]=copy.deepcopy(new[0])
        with self.assertRaises(ValueError):M.aggregate(new,endpoints('startup-guard'))


if __name__=='__main__':
    unittest.main()
