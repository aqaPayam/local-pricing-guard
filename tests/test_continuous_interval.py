"""Prospective synthetic arithmetic/model tests; no inherited study cases run."""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
import importlib.util
import copy
import random
import sys
import unittest

RESEARCH = Path(__file__).resolve().parents[1] / 'research'
sys.dont_write_bytecode = True
sys.path.insert(0, str(RESEARCH))
from continuous_interval import (Interval as I, Unresolved, PRECISION,
    fraction_decimal, exact_binary64, bisect_increasing,
    lambert_w_positive, classify_floor)
spec = importlib.util.spec_from_file_location('continuous_study', RESEARCH / 'continuous-study.py')
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


class DirectedIntervalTests(unittest.TestCase):
    def test_binary64_and_exact_real_allowance_are_not_short_decimals(self):
        record = exact_binary64(0.1)
        self.assertNotEqual(record['exactDecimal'], '0.1')
        self.assertEqual(Fraction(Decimal(record['exactDecimal'])), Fraction(0.1))
        total = Fraction(0.1) + Fraction(1e-12)
        self.assertEqual(Fraction(fraction_decimal(total)), total)
        self.assertNotEqual(total, Fraction(0.1 + 1e-12))

    def test_fraction_conversion_never_uses_default_context_precision(self):
        value = Fraction(1, 2 ** 180)
        self.assertEqual(Fraction(fraction_decimal(value)), value)
        with self.assertRaises(ValueError):
            fraction_decimal(Fraction(1, 3))

    def test_outward_rational_arithmetic_against_exact_fractions(self):
        rng = random.Random(20261026)
        for _ in range(50):
            a = Fraction(rng.randint(-1000, 1000), 128)
            b = Fraction(rng.choice([v for v in range(-1000, 1001) if v]), 256)
            ia, ib = I(fraction_decimal(a)), I(fraction_decimal(b))
            for result, exact in [(ia + ib, a + b), (ia - ib, a - b),
                                  (ia * ib, a * b), (ia / ib, a / b)]:
                self.assertLessEqual(Fraction(result.lo), exact)
                self.assertGreaterEqual(Fraction(result.hi), exact)

    def test_mixed_sign_interval_products_and_reciprocals(self):
        result = I('-3', '2') * I('-7', '5')
        self.assertTrue(result.contains(-15))
        self.assertTrue(result.contains(21))
        self.assertTrue((1 / I('-4', '-2')).contains(Decimal('-0.25')))
        with self.assertRaises(ValueError):
            I(1) / I(-1, 1)

    def test_exp_and_log_against_independent_220_digit_reference(self):
        for text in ['-30', '-0.00001', '0', '0.1', '1', '30']:
            x = Decimal(text)
            with localcontext() as context:
                context.prec = 220
                expected = x.exp()
            enclosure = I(x).exp()
            self.assertLess(enclosure.lo, expected)
            self.assertGreater(enclosure.hi, expected)
        for text in ['0.00001', '0.7', '1', '2', '100000']:
            x = Decimal(text)
            with localcontext() as context:
                context.prec = 220
                expected = x.ln()
            enclosure = I(x).ln()
            self.assertLess(enclosure.lo, expected)
            self.assertGreater(enclosure.hi, expected)
        self.assertGreaterEqual(PRECISION, 80)

    def test_monotone_transcendental_endpoint_coverage(self):
        with localcontext() as context:
            context.prec = 200
            for point in ['0.1', '0.25', '0.5', '0.75', '1.5']:
                x = Decimal(point)
                self.assertTrue(I('0.1', '1.5').exp().contains(x.exp()))
                self.assertTrue(I('0.1', '1.5').ln().contains(x.ln()))

    def test_sign_certified_root_handles_exact_midpoint_root(self):
        root, evidence = bisect_increasing(lambda x: x * x - 4, 0, 4, '1e-28')
        self.assertTrue(root.contains(2))
        self.assertLessEqual(root.width, Decimal('1e-28'))
        self.assertLess(Decimal(evidence['lowerEvaluation']['upper']), 0)
        self.assertGreater(Decimal(evidence['upperEvaluation']['lower']), 0)

    def test_root_rejects_bad_or_uncertified_bracket(self):
        with self.assertRaises(Unresolved):
            bisect_increasing(lambda x: x * x + 1, 0, 4)
        with self.assertRaises(Unresolved):
            bisect_increasing(lambda x: I('-1e-8', '1e-8'), 0, 1)

    def test_lambert_w_has_independently_known_root_and_signed_bounds(self):
        z = 2 * I(2).exp()
        value, proofs = lambert_w_positive(z)
        self.assertTrue(value.contains(2))
        self.assertLess(value.width, Decimal('1e-38'))
        for proof in proofs:
            self.assertLess(Decimal(proof['lowerEvaluation']['upper']), 0)
            self.assertGreater(Decimal(proof['upperEvaluation']['lower']), 0)

    def test_floor_classification_uses_strict_failure_and_non_strict_guarantee(self):
        self.assertEqual(classify_floor(I(1, 2), 3), 'all-start failing continuation')
        self.assertEqual(classify_floor(I(1, 2), 1), 'already guaranteed')
        self.assertEqual(classify_floor(I(1, 2), 2), 'unresolved')


class SyntheticContinuumTests(unittest.TestCase):
    economy = {'id': 'synthetic-zero-value', 'quality': 0, 'cost': 0,
               'mu': 1, 'buyers': 1, 'outsideQuality': 0}
    targets = [{'label': label, 'requestedTarget': 0.1,
                'actualGuaranteedThreshold': 0.1 - 1e-8} for label in study.TARGET_LABELS]

    def test_interior_continuum_root_and_stationary_regret(self):
        model = study.Model(self.economy, 0, 3, 0.001)
        result = study.solve_model(model, self.targets)
        self.assertEqual(result['status'], 'certified theorem and enclosures')
        self.assertEqual(result['worst']['rootProof']['kind'], 'interior upper-root fixed point')
        self.assertGreater(Decimal(result['nashToWorstSurplusGap']['lower']), 0)
        regret = result['worst']['stationaryUnilateralDeviationGain']
        self.assertLessEqual(Decimal(regret['lower']), Decimal.from_float(0.001))
        self.assertGreaterEqual(Decimal(regret['upper']), Decimal.from_float(0.001))

    def test_clipped_upper_fixed_point_is_detected_separately(self):
        model = study.Model(self.economy, 0, 1.25, 0.001)
        result = study.solve_model(model, self.targets)
        self.assertEqual(result['status'], 'certified theorem and enclosures')
        self.assertEqual(result['worst']['rootProof']['kind'], 'ceiling-clipped')
        self.assertEqual(result['worst']['normalizedPrice']['lower'], '1.25')
        self.assertGreater(Decimal(result['worst']['upperBranchMargin']['lower']), 0)

    def test_failed_assumptions_are_retained_without_outcome_substitution(self):
        model = study.Model(self.economy, 0, 3, 1)
        result = study.solve_model(model, self.targets)
        self.assertEqual(result['status'], 'unresolved assumptions')
        self.assertEqual(result['comparisons'][0]['classification'], 'unresolved')
        self.assertNotIn('worst', result)
        self.assertEqual(len(result['comparisons']), 5)
        self.assertIn('requestedImported', result['comparisons'][0])
        self.assertIn('thresholdImported', result['comparisons'][0])

    def test_malformed_parameters_rejected(self):
        with self.assertRaises(ValueError):
            study.Model({**self.economy, 'mu': 0}, 0, 3, 0.001)
        with self.assertRaises(ValueError):
            study.Model(self.economy, 3, 0, 0.001)
        with self.assertRaises(ValueError):
            study.Model(self.economy, 0, 3, -1)

    def test_raw_target_identity_uses_scenario_object_and_rejects_mismatch(self):
        scenario = {'id': 'synthetic-g3', 'economy': self.economy, 'gridSize': 3,
                    'toleranceFactor': 1, 'epsilon': 0.001}
        case = {'id': 'synthetic-g3-guard', 'scenario': scenario, 'controller': 'guard',
                'game': {'n': 3, 'prices': [0, 1.5, 3],
                         'treatment': {'type': 'guard', 'epsilon': 0.001}}}
        records = [{'scenario': scenario, 'guardCaseId': case['id'],
                    'capCaseId': 'synthetic-g3-cap', 'results': self.targets}]
        self.assertEqual(study.validate_case_targets(case, records, scenario), self.targets)
        changed = copy.deepcopy(records)
        changed[0]['scenario']['economy']['cost'] = 0.25
        with self.assertRaises(ValueError):
            study.validate_case_targets(case, changed, scenario)
        changed = copy.deepcopy(records)
        changed[0]['results'][0]['label'] = 'unplanned'
        with self.assertRaises(ValueError):
            study.validate_case_targets(case, changed, scenario)

    def test_unresolved_evidence_keeps_all_five_labels_and_does_not_guess_targets(self):
        records = study.comparisons_for([self.targets[0]])
        self.assertEqual([r['label'] for r in records], study.TARGET_LABELS)
        self.assertIn('requestedImported', records[0])
        self.assertEqual(records[1]['classification'], 'unresolved')
        self.assertIn('targetEvidenceFailure', records[1])


if __name__ == '__main__':
    unittest.main()
