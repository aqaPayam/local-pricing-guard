"""Independent auditor arithmetic and synthetic certificate corruption tests."""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
import copy
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True
RESEARCH = Path(__file__).resolve().parents[1]/'research'
sys.path.insert(0, str(RESEARCH))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load('independent_continuous_audit', RESEARCH/'audit-continuous-study.py')
primary = load('synthetic_primary_fixture', RESEARCH/'continuous-study.py')


class IndependentContinuousTests(unittest.TestCase):
    def test_separate_interval_arithmetic_and_log_residual_w(self):
        a, b = audit.Box.rational(Fraction(-3, 7)), audit.Box.rational(Fraction(5, 11))
        for result, exact in [(a+b, Fraction(-3, 7)+Fraction(5, 11)),
                              (a*b, Fraction(-3, 7)*Fraction(5, 11)),
                              (a/b, Fraction(-3, 7)/Fraction(5, 11))]:
            self.assertLessEqual(Fraction(result.low), exact)
            self.assertGreaterEqual(Fraction(result.high), exact)
        w = audit.positive_w(2*audit.Box(2).exp())
        self.assertLess(w.low, 2)
        self.assertGreater(w.high, 2)
        with localcontext() as context:
            context.prec = 240
            reference = Decimal('0.7').ln()
        interval = audit.Box('0.7').log()
        self.assertLess(interval.low, reference)
        self.assertGreater(interval.high, reference)

    @staticmethod
    def fixture(high):
        economy = {'id': 'audit-synthetic', 'quality': 0, 'cost': 0,
                   'mu': 1, 'buyers': 1, 'outsideQuality': 0}
        case = {'scenario': {'id': 'audit-synthetic', 'economy': economy, 'epsilon': .001},
                'game': {'prices': [0, high]}}
        targets = [{'label': label, 'requestedTarget': .1,
                    'actualGuaranteedThreshold': .1-1e-8} for label in audit.LABELS]
        record = primary.solve_model(primary.Model(economy, 0, high, .001), targets)
        record.update({'scenario': 'audit-synthetic', 'continuum': 'nominal'})
        return record, case, targets

    def test_synthetic_primary_certificate_is_independently_checked_and_corruptions_fail(self):
        record, case, targets = self.fixture(3)
        self.assertEqual(audit.check_record(record, case, targets)['status'], 'certified theorem and enclosures')
        mutations = [lambda r: r['assumptions']['rho'].update(upper='0'),
                     lambda r: r['comparisons'][0].update(classification='unresolved'),
                     lambda r: r['worst']['normalizedPrice'].update(upper='3'),
                     lambda r: r['worst']['consumerSurplus'].update(lower='0', upper='0')]
        for mutate in mutations:
            changed = copy.deepcopy(record)
            mutate(changed)
            with self.assertRaises(ValueError):
                audit.check_record(changed, case, targets)

    def test_clipped_certificate_is_independently_checked(self):
        record, case, targets = self.fixture(1.25)
        self.assertEqual(record['worst']['rootProof']['kind'], 'ceiling-clipped')
        self.assertEqual(audit.check_record(record, case, targets)['status'], 'certified theorem and enclosures')


if __name__ == '__main__':
    unittest.main()
