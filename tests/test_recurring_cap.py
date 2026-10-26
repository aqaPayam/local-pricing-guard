"""Prospective synthetic checks, without inherited recurring-controller cases."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, localcontext
import copy, importlib.util, sys, unittest

sys.dont_write_bytecode=True
RESEARCH=Path(__file__).resolve().parents[1]/'research'
sys.path.insert(0,str(RESEARCH))
from continuous_interval import Interval as I, Unresolved
spec=importlib.util.spec_from_file_location('recurring_primary',RESEARCH/'recurring-cap-study.py')
study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)


class LinearModel:
    mass_scale=I(1)
    def profit(self,x,y):return x+y


def linear_trajectory(j=64):
    # Exact independent toy: U(a)=1+a/2, A=0, q*=2, C(a,a)=10-a.
    prices=[I(0)];rewards=[];profits=[]
    for _ in range(j):
        rewards.append(10-prices[-1]);profits.append(2*prices[-1])
        prices.append(1+prices[-1]/2)
    return {'rewards':rewards,'profits':profits,'prices':prices,'qstar':I(2),'rho':I('0.5'),
            'distanceAfterPrefix':I(2)-prices[-1],'massScale':I(1),'model':LinearModel()}


def exact_average(k):return Fraction(8)+Fraction(4,k)*(1-Fraction(1,2**k))


def target(value):return {'label':'synthetic','requestedTarget':float(value),'actualGuaranteedThreshold':float(value)}


def reference_upper(model,y):
    # Separately coded 200-digit scalar reference, with Newton W and direct
    # upper-root bisection. It imports no primary root/map functions.
    with localcontext() as ctx:
        ctx.prec=200
        y=Decimal(y);k=Decimal(1);one=Decimal(1)
        z=one/(one.exp()*(k+(-y).exp()));w=z
        for _ in range(30):w-=(w*w.exp()-z)/(w.exp()*(1+w))
        t=Decimal.from_float(0.001)
        lo,hi=1+w,Decimal(3)
        for _ in range(500):
            middle=(lo+hi)/2
            profit=middle/(1+(k+(-y).exp())*middle.exp())
            if profit>w-t:lo=middle
            else:hi=middle
        return (lo+hi)/2


class RecurringCapTests(unittest.TestCase):
    economy={'id':'synthetic','quality':0,'cost':0,'mu':1,'buyers':1,'outsideQuality':0}

    def test_scalar_endpoint_roots_contain_separate_high_precision_reference(self):
        model=study.continuous.Model(self.economy,0,3,0.001)
        result,proof=study.map_interval(model,I('0.5','2'))
        for key,value in [('lowerEndpoint','0.5'),('upperEndpoint','2')]:
            endpoint=proof[key];enclosure=study.box(endpoint['normalizedPrice'])
            self.assertTrue(enclosure.contains(reference_upper(model,value)))
            self.assertLessEqual(enclosure.width,Decimal('1e-25'))
            self.assertEqual(endpoint['rivalExact'],value)
        self.assertLessEqual(result.lo,reference_upper(model,'0.5'))
        self.assertGreaterEqual(result.hi,reference_upper(model,'2'))

    def test_scalar_upper_map_clipping_is_explicit(self):
        model=study.continuous.Model(self.economy,0,1.25,0.001)
        result=study.upper_at_point(model,Decimal('1.25'))
        self.assertEqual(result['proof']['kind'],'ceiling-clipped')
        self.assertEqual(result['normalizedPrice']['lower'],'1.25')
        self.assertLess(Decimal(result['proof']['ceilingResidual']['upper']),0)

    def test_exact_prefix_and_analytic_tail_contain_rational_oracle(self):
        bounds=study.PeriodBounds(linear_trajectory(),I(8))
        for k in [1,2,4,8,16,32,64,65,128,1000]:
            interval=study.box(bounds.get(k)['averageConsumerSurplus'])
            expected=exact_average(k)
            self.assertLessEqual(Fraction(interval.lo),expected)
            self.assertGreaterEqual(Fraction(interval.hi),expected)
            if k<=64:self.assertIsNone(bounds.get(k)['tail'])
            else:self.assertEqual(bounds.get(k)['tail']['termsAfterPrefix'],k-64)

    def test_last_round_tail_uses_aJ_with_correct_zero_exponent(self):
        bounds=study.PeriodBounds(linear_trajectory(4),I(8))
        last=study.box(bounds.get(5)['lastRoundConsumerSurplus'])
        actual=Fraction(8)+Fraction(2,2**4)
        self.assertLessEqual(Fraction(last.lo),actual)
        self.assertGreaterEqual(Fraction(last.hi),actual)
        self.assertEqual(bounds.get(5)['tail']['termsAfterPrefix'],1)

    def test_safe_and_next_failing_period_both_required_for_largest(self):
        result=study.target_result(target(9),study.PeriodBounds(linear_trajectory(),I(8)))
        self.assertEqual(result['status'],'largest certified fixed period')
        self.assertEqual(result['largestPeriod'],3)
        self.assertEqual(result['nextFailingPeriod']['period'],4)
        self.assertGreaterEqual(Decimal(result['safePeriod']['averageConsumerSurplus']['lower']),9)
        self.assertLess(Decimal(result['nextFailingPeriod']['averageConsumerSurplus']['upper']),9)

    def test_overlap_retains_integer_bracket_instead_of_guessing_boundary(self):
        class Uncertain:
            cstar=I(0)
            def get(self,k):return {'period':k,'averageConsumerSurplus':(I('6.9','7.1') if k==3 else I(10-k)).json()}
        result=study.target_result(target(7),Uncertain())
        self.assertEqual(result['status'],'certified integer bracket')
        self.assertEqual(result['possibleLargestPeriodBracket'],[2,3])
        self.assertIsNone(result['largestPeriod'])

    def test_search_ceiling_is_censored_not_an_invented_optimum(self):
        result=study.target_result(target(8+1e-10),study.PeriodBounds(linear_trajectory(),I(8)))
        self.assertEqual(result['status'],'censored safe lower bound')
        self.assertEqual(result['certifiedSafePeriodLowerBound'],65536)
        self.assertIsNone(result['certifiedFailingPeriodUpperBound'])

    def test_zero_frequency_policies_keep_different_startup_counts(self):
        result=study.target_result(target(8),study.PeriodBounds(linear_trajectory(),I(8)))
        self.assertEqual(result['status'],'no recurring cap needed for the long-run target')
        self.assertEqual(result['withoutIntervention']['startupCaps'],0)
        self.assertFalse(result['withoutIntervention']['finiteActivationAverageGuaranteedFromArbitraryOldPrices'])
        self.assertEqual(result['oneImmediateCapThenOriginalGuard']['startupCaps'],1)

    def test_infeasibility_only_refers_to_this_fixed_physical_cap_family(self):
        result=study.target_result(target(11),study.PeriodBounds(linear_trajectory(),I(8)))
        self.assertEqual(result['status'],'infeasible for this fixed-cap family')
        self.assertIn('stricter cap',result['scope'])

    def test_cap_price_identity_and_state_independence_are_checked(self):
        scenario={'id':'toy','economy':self.economy,'gridSize':3,'epsilon':0.001}
        guard={'id':'toy-guard','scenario':scenario,'controller':'guard','game':{'prices':[0,1,2]}}
        cap={'id':'toy-cap','scenario':scenario,'controller':'cap','game':{'prices':[0,1,2],'n':3,
            'treatment':{'type':'cap'},'sets':[[0,1],[0,1],[0,1]]}}
        raw={'scenario':scenario,'guardCaseId':'toy-guard','capCaseId':'toy-cap','results':[
            {'label':label,'requestedTarget':1,'actualGuaranteedThreshold':0.99,
             'existingCompetitiveCap':{'index':1,'price':1,'allowedInitialPricesPerSeller':2}} for label in study.LABELS]}
        record,price=study.inherited_cap(guard,cap,raw)
        self.assertEqual(price,1);self.assertEqual(record['oldIndex'],1)
        changed=copy.deepcopy(raw);changed['results'][2]['existingCompetitiveCap']['price']=1.01
        with self.assertRaises(ValueError):study.inherited_cap(guard,cap,changed)
        changed=copy.deepcopy(cap);changed['game']['sets'][2]=[0]
        with self.assertRaises(ValueError):study.inherited_cap(guard,changed,raw)

    def test_failed_A_below_qstar_condition_is_not_repaired_silently(self):
        model=study.continuous.Model(self.economy,0,3,0.001)
        with self.assertRaises(Unresolved):study.orbit(model,I(2),I('1.2','1.4'),I('0.5'),4)
        with self.assertRaises(ValueError):study.power_nonnegative(I(-1),2)
        with self.assertRaises(ValueError):study.PeriodBounds(linear_trajectory(),I(8)).get(65537)


if __name__=='__main__':unittest.main()
