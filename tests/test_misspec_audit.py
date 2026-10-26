"""Independent synthetic arithmetic/claim checks, not alternative-demand cases."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, localcontext
import importlib.util,sys,unittest
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('misspec_audit',Path(__file__).resolve().parents[1]/'research/audit-misspec-study.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
primary_spec=importlib.util.spec_from_file_location('toy_misspec_primary',Path(__file__).resolve().parents[1]/'research/misspec-study.py')
primary=importlib.util.module_from_spec(primary_spec)
primary_spec.loader.exec_module(primary)


class ToyModel:
    scale=audit.B(1)
    k=audit.B(1)


def toy_curve():
    prices=[audit.B.rational(Fraction(2)*(1-Fraction(1,2**j))) for j in range(64)]
    a64=audit.B.rational(Fraction(2)*(1-Fraction(1,2**64)))
    return audit.IndependentDemandCurve(ToyModel(),prices,a64,audit.B(2),audit.B('.5'))


class MisspecAuditTests(unittest.TestCase):
    def test_actual_surplus_decreases_in_quality_drop_and_price(self):
        model=ToyModel()
        previous=None
        for d in ['0','.001','.01','.05','1']:
            result=audit.shifted_surplus(model,audit.B('1.4'),audit.B(d))
            with localcontext() as ctx:
                ctx.prec=220
                reference=(1+2/((Decimal('1.4')+Decimal(d)).exp())).ln()
            self.assertLess(result.low,reference)
            self.assertGreater(result.high,reference)
            if previous is not None:
                self.assertLess(result.high,previous.low)
            previous=result
        self.assertLess(audit.shifted_surplus(model,audit.B('1.5'),audit.B('.05')).high,
                        audit.shifted_surplus(model,audit.B('1.4'),audit.B('.05')).low)
        with self.assertRaises(ValueError):
            audit.shifted_surplus(model,audit.B(1),audit.B('-.01'))

    def test_stationary_closed_form_and_independent_signed_crossing(self):
        with localcontext() as ctx:
            ctx.prec=220
            threshold=Fraction((1+2/Decimal('1.6').exp()).ln())
        radius=audit.stationary_crossing(ToyModel(),audit.B('1.4'),threshold)
        self.assertLess(radius.low,Decimal('.2'))
        self.assertGreater(radius.high,Decimal('.2'))
        curve=toy_curve()
        with localcontext() as ctx:
            ctx.prec=220
            first_threshold=Fraction((1+2/Decimal('.2').exp()).ln())
        lo='0.1999999999999999999999';hi='0.2000000000000000000001'
        audit.check_signed_radius(curve,1,first_threshold,lo,hi)
        with self.assertRaises(ValueError):
            audit.check_signed_radius(curve,1,first_threshold,'.1999999999999999999997',lo)
        with self.assertRaises(ValueError):
            audit.check_signed_radius(curve,1,first_threshold,lo,'.20000000001')

    def test_tail_encloses_direct_synthetic_orbit_and_preserves_period_boundary(self):
        curve=toy_curve();d=audit.B('.05')
        for K in [1,4,64,65,128]:
            direct=sum((audit.shifted_surplus(ToyModel(),audit.B.rational(Fraction(2)*(1-Fraction(1,2**j))),d) for j in range(K)),audit.B(0))/K
            bound=curve.value(K,d)
            self.assertLessEqual(bound.low,direct.low)
            self.assertGreaterEqual(bound.high,direct.high)
        two,three=curve.value(2,d),curve.value(3,d)
        threshold=Fraction((two.low+three.high)/2)
        audit.check_fixed_period_boundaries(curve,threshold,d,2,3)
        with self.assertRaises(ValueError):
            audit.check_fixed_period_boundaries(curve,threshold,d,3,4)
        with self.assertRaises(ValueError):
            curve.value(65537,d)

    def test_synthetic_primary_policy_certificates_and_corruptions_are_independently_checked(self):
        prices=[primary.I(primary.fraction_decimal(Fraction(2)*(1-Fraction(1,2**j)))) for j in range(64)]
        a64=primary.I(primary.fraction_decimal(Fraction(2)*(1-Fraction(1,2**64))))
        bounds=primary.ShiftedBounds(primary.ActualDemand(primary.I(1),primary.I(1)),prices,a64,primary.I(2),primary.I('.5'))
        closed={'label':'synthetic',**primary.period_selection(bounds,Decimal('.5'),Decimal(0))}
        original={'label':'synthetic','requestedTarget':.5,'actualGuaranteedThreshold':.5}
        row=primary.policy_rows(bounds,original,closed)
        curve=toy_curve()
        result=audit.check_target(row,original,closed,curve)
        self.assertTrue(result['zeroReproduces'])
        import copy
        def inflate_radius(r):
            p=next(p for p in r['policies'] if p['radius']['status']=='certified crossing enclosure')
            p['radius']['radiusEnclosure']['upper']='8'
        changes=[lambda r:r.update(actualThresholdExact='.1'),
                 lambda r:r['policies'][0]['sensitivity'][1]['dbar'].update(exactDecimal='.01'),
                 inflate_radius,
                 lambda r:r['robustPeriods'][0].update(largestPeriod=100)]
        for mutate in changes:
            changed=copy.deepcopy(row)
            mutate(changed)
            with self.assertRaises(ValueError):
                audit.check_target(changed,original,closed,curve)


if __name__=='__main__':
    unittest.main()
