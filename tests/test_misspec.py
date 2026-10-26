"""Synthetic alternative-demand tests only; no inherited shifted-demand cases."""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
import importlib.util, sys, unittest, json, uuid, contextlib, io
from unittest.mock import patch
from types import SimpleNamespace

sys.dont_write_bytecode = True
RESEARCH = Path(__file__).resolve().parents[1]/'research'
sys.path.insert(0, str(RESEARCH))
from continuous_interval import Interval as I
spec = importlib.util.spec_from_file_location('misspec_primary', RESEARCH/'misspec-study.py')
study = importlib.util.module_from_spec(spec); spec.loader.exec_module(study)


def synthetic_bounds(j=8):
    # Synthetic fixed nominal price orbit a_j=1-2^-j, qstar=1, rho=1/2.
    # It is not an inherited market or a newly solved enforcement model.
    prices = [I(0)]
    for _ in range(j): prices.append((1+prices[-1])/2)
    return study.ShiftedBounds(study.ActualDemand(I(1), I(1)), prices[:-1], prices[-1], I(1), I('.5'))


def reference_cs(z, d, k=Decimal(1), scale=Decimal(1)):
    with localcontext() as ctx:
        ctx.prec = 200
        return scale*(1+2*(-Decimal(z)-Decimal(d)).exp()/k).ln()


@contextlib.contextmanager
def synthetic_directory():
    # Sandbox-friendly disposable synthetic evidence, always inside this project.
    parent=RESEARCH.parent/'.local'/'misspec-synthetic-tests'
    parent.mkdir(parents=True,exist_ok=True)
    # Python 3.13's Windows mode-0700 tempfile directories exclude the sandbox
    # identity. Ordinary inherited directory permissions work in both runtimes.
    temporary=parent/('synthetic-'+uuid.uuid4().hex)
    temporary.mkdir()
    if temporary.resolve().parent != parent.resolve():
        raise AssertionError('Synthetic cleanup directory escaped its project parent')
    try:
        yield str(temporary)
    finally:
        for path in sorted(temporary.rglob('*'),key=lambda p:len(p.parts),reverse=True):
            if not path.resolve().is_relative_to(temporary.resolve()):
                raise AssertionError('Synthetic cleanup target escaped its verified directory')
            if path.is_dir(): path.rmdir()
            else: path.unlink()
        temporary.rmdir()


class ToyPeriodBounds:
    def __init__(self, overlap=False): self.called=[]; self.overlap=overlap
    def guard(self,d): return I(8)-d
    def get(self,k,d):
        self.called.append(k)
        if k>65536: raise AssertionError('Undeclared next period evaluated')
        value = I(8)+I(4)/k-d
        if self.overlap and k==4: value=I('8.99','9.01')-d
        return {'period':k,'averageConsumerSurplus':value.json()}


class MisspecificationTests(unittest.TestCase):
    def execution_fixture(self, old_matches=True, reproduction=True):
        scenario={'id':'synthetic-only','economy':{}}
        plan={'scenarios':[scenario], 'targetLabels':study.LABELS,
              'policySlots':['guard-only','closed-selected','permanent-cap'],
              'actualDemandShift':'synthetic fixture; no economic execution'}
        targets=[{'label':label,'requestedTarget':1.0,'actualGuaranteedThreshold':1.0}
                 for label in study.LABELS]
        comparisons=[{'label':label,'actualThresholdImported':{'exactDecimal':'1'}} for label in study.LABELS]
        closed=[{'scenario':'synthetic-only','continuum':kind,'comparisons':comparisons,
                 'physicalCap':{},'normalizedCapExact':'0','conditions':{},'inheritedContinuum':{'rounding':{}}}
                for kind in study.KINDS]
        sources={'handover-init-results':[{'scenario':scenario,'results':targets}] if old_matches else [],
                 'recurring-results':closed,
                 'continuous-results':[{'scenario':'synthetic-only','continuum':kind} for kind in study.KINDS]}
        bounds=SimpleNamespace(qstar=I(1),rho=I('.5'),a_j=I('.9'),
                              demand=SimpleNamespace(k=I(1),mass_scale=I(1)))
        def inherited_read(path):
            return {'records':sources[path.parent.name]}
        def synthetic_rows(_bounds,target,_prior):
            return {'label':target['label'],'d0ReproducesClosedSelection':reproduction,
                    'policies':[{'slot':slot} for slot in plan['policySlots']],
                    'robustPeriods':[{'status':'synthetic'} for _ in study.LEVELS]}
        return {'plan':plan}, inherited_read, bounds, synthetic_rows

    def test_partial_execution_evidence_is_never_appended(self):
        manifest,*_=self.execution_fixture()
        for marker in ['execution-start.json','results.json','journal.jsonl','records','completion.json']:
            with self.subTest(marker=marker),synthetic_directory() as temporary:
                directory=Path(temporary); (directory/marker).write_text('retained evidence')
                with patch.object(study,'verify',return_value=manifest):
                    with self.assertRaisesRegex(ValueError,'preserved'): study.run(directory)
                self.assertEqual((directory/marker).read_text(),'retained evidence')
                self.assertEqual(len(list(directory.iterdir())),1)

    def test_missing_target_scenario_retains_every_planned_slot(self):
        manifest,reader,bounds,rows=self.execution_fixture(old_matches=False)
        with synthetic_directory() as temporary:
            directory=Path(temporary); (directory/'manifest.json').write_text('{}')
            with patch.object(study,'verify',return_value=manifest),patch.object(study,'read',side_effect=reader),\
                 patch.object(study,'model_from_saved',return_value=bounds),patch.object(study,'policy_rows',side_effect=rows),\
                 patch.object(study,'rss_bytes',return_value=None),contextlib.redirect_stdout(io.StringIO()):
                completion=study.run(directory)
            result=json.loads((directory/'results.json').read_text())
            self.assertEqual(completion['unresolvedModels'],2)
            self.assertEqual(completion['policySlots'],30)
            self.assertEqual(completion['robustPeriodRows'],40)
            self.assertEqual(len((directory/'journal.jsonl').read_text().splitlines()),4)
            for record in result['records']:
                self.assertEqual(record['failure'],'Missing/duplicate inherited target scenario')
                self.assertEqual([t['label'] for t in record['targets']],study.LABELS)
                self.assertTrue(all(t['requestedImported'] is None for t in record['targets']))

    def test_zero_displacement_mismatch_retains_failure_and_computed_rows(self):
        manifest,reader,bounds,rows=self.execution_fixture(reproduction=False)
        with synthetic_directory() as temporary:
            directory=Path(temporary); (directory/'manifest.json').write_text('{}')
            with patch.object(study,'verify',return_value=manifest),patch.object(study,'read',side_effect=reader),\
                 patch.object(study,'model_from_saved',return_value=bounds),patch.object(study,'policy_rows',side_effect=rows),\
                 patch.object(study,'rss_bytes',return_value=None),contextlib.redirect_stdout(io.StringIO()):
                completion=study.run(directory)
            result=json.loads((directory/'results.json').read_text())
            self.assertEqual(completion['unresolvedModels'],2)
            for record in result['records']:
                self.assertFalse(record['d0AllClosedSelectionsReproduced'])
                self.assertIn('reproduction',record['failure'])
                self.assertEqual(len(record['targets']),5)
                self.assertTrue(all(not t['d0ReproducesClosedSelection'] for t in record['targets']))

    def test_zero_shift_matches_nominal_and_positive_shift_lowers_welfare(self):
        model=study.ActualDemand(I(1),I(3)); z=I('1.2')
        nominal=model.surplus(z,0)
        self.assertTrue(nominal.contains(reference_cs('1.2','0',scale=Decimal(3))))
        changed=model.surplus(z,Decimal('.01'))
        self.assertLess(changed.hi,nominal.lo)
        self.assertTrue(changed.contains(reference_cs('1.2','.01',scale=Decimal(3))))

    def test_quality_displacement_units_and_fixed_outside_baseline(self):
        # Physical reference: v=2, outside=.3, c=1, mu=.5, p=1.5, B=10.
        # Actual v becomes 2-d*.5. The nominal price and k never change.
        model=study.ActualDemand(I('-1.4').exp(),I(5))
        d=study.fraction_decimal(Fraction(1,100)); result=model.surplus(I(1),d)
        with localcontext() as ctx:
            ctx.prec=200
            utility=(Decimal(2)-d*Decimal('.5')-Decimal('1.5')-Decimal('.3'))/Decimal('.5')
            reference=5*(1+2*utility.exp()).ln()
        self.assertTrue(result.contains(reference))
        self.assertEqual(d,Decimal('.01'))

    def test_stationary_closed_form_has_separately_signed_padded_bracket(self):
        model=study.ActualDemand(I(1),I(2)); z=I('.5'); f=Decimal(1)
        analytic=model.stationary_crossing(z,f)
        result=study.radius(lambda d:model.surplus(z,d),f,model.mass_scale,analytic)
        self.assertEqual(result['status'],'certified crossing enclosure')
        bracket=study.box(result['radiusEnclosure'])
        with localcontext() as ctx:
            ctx.prec=200
            reference=Decimal(2).ln()-Decimal('.5')-((f/2).exp()-1).ln()
        self.assertTrue(analytic.contains(reference)); self.assertTrue(bracket.contains(reference))
        self.assertLessEqual(bracket.width,Decimal('1e-20'))
        self.assertGreaterEqual(Decimal(result['safeLower']['reserve']['lower']),0)
        self.assertLess(Decimal(result['failingUpper']['reserve']['upper']),0)
        self.assertLessEqual(Decimal(result['certifiedSimpleSufficientRadiusLower']),reference)
        self.assertEqual(result['stationarySignPaddingExact'],'1E-24')

    def test_empty_safe_set_is_not_an_ordinary_zero_radius(self):
        result=study.radius(lambda d:I(1)-d,Decimal(2),I(1))
        self.assertEqual(result['safeNonnegativeSet'],'empty')
        self.assertIsNone(result['radiusEnclosure'])
        self.assertIsNone(result['certifiedSimpleSufficientRadiusLower'])

    def test_exact_zero_boundary_and_uncertain_zero_are_distinct(self):
        exact=study.radius(lambda d:I(3)-d,Decimal(3),I(1))
        self.assertEqual(exact['status'],'certified exact zero radius')
        uncertain=study.radius(lambda d:I('2.9','3.1')-d,Decimal(3),I(1))
        self.assertEqual(uncertain['status'],'unresolved zero-displacement overlap')
        self.assertIsNone(uncertain['radiusEnclosure'])

    def test_displacement_ceiling_censors_without_evaluating_above_eight(self):
        probes=[]
        def evaluate(d): probes.append(d); return I(100)-d
        result=study.radius(evaluate,Decimal(1),I(1))
        self.assertEqual(result['status'],'censored safe lower bound')
        self.assertEqual(result['certifiedRadiusLowerBound'],'8')
        self.assertLessEqual(max(probes),8)
        with self.assertRaises(ValueError):study.ActualDemand(I(1),I(1)).surplus(I(0),'8.0001')

    def test_input_uncertainty_prevents_false_tight_root(self):
        result=study.radius(lambda d:I('1.9','2.1')-d,Decimal(1),I(1))
        self.assertEqual(result['status'],'unresolved crossing width')
        self.assertIsNone(result['radiusEnclosure'])
        self.assertGreater(Decimal(result['signedBracket']['width']),Decimal('1e-20'))
        self.assertGreaterEqual(Decimal(result['safeLower']['reserve']['lower']),0)
        self.assertLess(Decimal(result['failingUpper']['reserve']['upper']),0)

    def test_fixed_price_orbit_rewards_order_and_cap_first_prefixes(self):
        bounds=synthetic_bounds(8); values=bounds.at_displacement(Decimal('.05'))
        self.assertTrue(all(values['rewards'][j].hi<values['rewards'][j-1].lo for j in range(1,8)))
        cycle=study.box(bounds.get(8,Decimal('.05'))['averageConsumerSurplus'])
        total=I(0)
        for t in range(1,25):
            total+=values['rewards'][(t-1)%8]
            # All finite activation averages enclose values above the cycle's
            # certified lower floor, apart from outward interval roundoff.
            self.assertGreaterEqual((total/t).hi,cycle.lo)
            with localcontext() as ctx:
                ctx.prec=200
                exact=sum((reference_cs(1-Decimal(2)**(-((u-1)%8)),'.05') for u in range(1,t+1)),Decimal(0))/t
            self.assertTrue((total/t).contains(exact))
            self.assertGreaterEqual(exact,cycle.lo)

    def test_tail_first_omitted_index_and_uncertainty_are_retained(self):
        bounds=synthetic_bounds(4)
        for k in [1,4,5,9,16]:
            row=bounds.get(k,Decimal('.01')); interval=study.box(row['averageConsumerSurplus'])
            with localcontext() as ctx:
                ctx.prec=200
                reference=sum((reference_cs(1-Decimal(2)**(-j),'.01') for j in range(k)),Decimal(0))/k
            self.assertTrue(interval.contains(reference))
            if k>4:
                self.assertEqual(row['tail']['firstOmittedIndex'],4)
                self.assertEqual(row['tail']['terms'],k-4)
                self.assertGreater(Decimal(row['tail']['excessSumUpper']),0)
        last=study.box(bounds.get(5,Decimal('.01'))['lastRoundConsumerSurplus'])
        self.assertTrue(last.contains(reference_cs(Decimal(15)/16,'.01')))

    def test_robust_period_decreases_and_boundary_equality_is_safe(self):
        bounds=ToyPeriodBounds()
        nominal=study.period_selection(bounds,Decimal(9),Decimal(0))
        shifted=study.period_selection(bounds,Decimal(9),Decimal('.001'))
        self.assertEqual(nominal['largestPeriod'],4)
        self.assertEqual(shifted['largestPeriod'],3)
        self.assertEqual(nominal['nextFailingPeriod']['period'],5)
        self.assertLessEqual(max(bounds.called),65536)

    def test_period_overlap_is_a_bracket_and_ceiling_does_not_invent_optimum(self):
        overlap=study.period_selection(ToyPeriodBounds(True),Decimal(9),Decimal(0))
        self.assertEqual(overlap['status'],'certified integer bracket')
        self.assertEqual(overlap['possibleLargestPeriodBracket'],[3,4])
        bounds=ToyPeriodBounds()
        censored=study.period_selection(bounds,Decimal('8.0000000001'),Decimal(0))
        self.assertEqual(censored['status'],'censored safe lower bound')
        self.assertIsNone(censored['largestPeriod'])
        self.assertEqual(max(bounds.called),65536)

    def test_zero_recurring_frequency_keeps_startup_variant_and_family_scope(self):
        result=study.period_selection(ToyPeriodBounds(),Decimal(7),Decimal('.05'))
        self.assertEqual(result['withoutIntervention']['startupCaps'],0)
        self.assertFalse(result['withoutIntervention']['finiteActivationAverageGuaranteedFromArbitraryOldPrices'])
        self.assertEqual(result['oneImmediateCapThenOriginalGuard']['startupCaps'],1)
        failed=study.period_selection(ToyPeriodBounds(),Decimal(13),Decimal(0))
        self.assertEqual(failed['status'],'infeasible for this fixed-cap family')
        self.assertIn('stricter',failed['scope'])

    def test_closed_policy_not_reselected_and_duplicate_slots_are_retained(self):
        bounds=synthetic_bounds(8)
        target={'label':'synthetic','requestedTarget':1.0,'actualGuaranteedThreshold':1.0}
        closed={'status':'largest certified fixed period','largestPeriod':1,
                'certifiedSafePeriodLowerBound':1,'certifiedFailingPeriodUpperBound':2,
                'possibleLargestPeriodBracket':[1,1]}
        row=study.policy_rows(bounds,target,closed)
        self.assertEqual(len(row['policies']),3)
        self.assertEqual(row['policies'][1]['policy']['period'],1)
        self.assertEqual(row['policies'][2]['duplicateOf'],'closed-selected')
        self.assertTrue(row['d0ReproducesClosedSelection'])
        self.assertEqual([r['dbar']['exactDecimal'] for r in row['robustPeriods']],['0','0.001','0.01','0.05'])
        self.assertEqual(row['actualThresholdExact'],'1')
        self.assertEqual(study.selected_policy({'status':'censored safe lower bound'})['kind'],'unavailable')

    def test_exact_error_levels_and_arithmetic_domains(self):
        self.assertEqual(study.level_record(Fraction(1,1000))['denominator'],'1000')
        with self.assertRaises(ValueError):study.nonnegative_power(I(-1),2)
        with self.assertRaises(ValueError):synthetic_bounds().get(65537,0)
        with self.assertRaises(ValueError):study.radius(lambda d:I(1),Decimal(0),I(1))


if __name__ == '__main__': unittest.main()
