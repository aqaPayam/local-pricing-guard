"""Artificial-only independent mixed-timing interval checks."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import importlib.util
import unittest
from decimal import Decimal, localcontext
from fractions import Fraction
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('new_mixed_continuous_audit', ROOT/'research/audit-mixed-continuous.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
B = audit.B


class MixedContinuousAuditTests(unittest.TestCase):
    def test_contraction_tail_is_not_constant_last_reward(self):
        artificial = {'rewards': [B(2)]*64, 'cstar': B(1), 'rho': B('.5'),
                      'distance': B(2), 'model': SimpleNamespace(scale=B(1))}
        x = audit.bounded_sum(artificial, 64)
        self.assertEqual((x.low, x.high), (Decimal(128), Decimal(128)))
        x = audit.bounded_sum(artificial, 65)
        self.assertEqual((x.low, x.high), (Decimal(129), Decimal(131)))
        x = audit.bounded_sum(artificial, 66)
        self.assertEqual((x.low, x.high), (Decimal(130), Decimal(133)))
        with self.assertRaises(ValueError):
            audit.bounded_sum(artificial, 65537)
        audit.bounded_sum(artificial, 65536)

    def test_exact_rational_sum_bounds_reject_false_inclusion(self):
        result = B('1.25', '1.75')
        enc = {'lower': {'numerator': '1', 'denominator': '1'},
               'upper': {'numerator': '2', 'denominator': '1'}}
        self.assertEqual(audit.validate_sum_bounds(enc, result, 'toy'), (Fraction(1), Fraction(2)))
        enc['lower'] = {'numerator': '3', 'denominator': '2'}
        with self.assertRaises(ValueError):
            audit.validate_sum_bounds(enc, result, 'toy')
        for n in [0, 1, 17]:
            x = audit.nonnegative_power(B('.5'), n)
            self.assertEqual(Fraction(x.low), Fraction(1, 2**n))
            self.assertEqual(Fraction(x.high), Fraction(1, 2**n))

    def test_synthetic_scalar_root_signs_and_corruptions(self):
        # Purely artificial k=1, rival=0 and tolerance=.01. A separate
        # 200-digit point calculation proposes brackets; the audit validates
        # them with130-digit outward log-W/profit interval signs.
        with localcontext() as ctx:
            ctx.prec = 200
            target_z = 1/(2*Decimal(1).exp())
            lo, hi = Decimal(0), Decimal(1)
            for _ in range(600):
                mid = (lo+hi)/2
                if mid*mid.exp() < target_z:
                    lo = mid
                else:
                    hi = mid
            w = (lo+hi)/2
            wl, wh = w-Decimal('1e-70'), w+Decimal('1e-70')
            threshold = w-Decimal('.01')
            lo, hi = 1+w, Decimal(10)
            for _ in range(600):
                mid = (lo+hi)/2
                if mid/(1+2*mid.exp()) > threshold:
                    lo = mid
                else:
                    hi = mid
            root = (lo+hi)/2
            rl, rh = root-Decimal('1e-60'), root+Decimal('1e-60')
            proof = {'rivalExact': '0', 'bestProfitW': {'lower': str(wl), 'upper': str(wh)},
                     'bestResponse': {'lower': str(1+wl-Decimal('1e-120')), 'upper': str(1+wh+Decimal('1e-120'))},
                     'normalizedTargetProfit': {'lower': str(wl-Decimal('.01')-Decimal('1e-120')), 'upper': str(wh-Decimal('.01')+Decimal('1e-120'))},
                     'normalizedPrice': {'lower': str(rl), 'upper': str(rh)},
                     'proof': {'kind': 'interior upper root'}}
        model = SimpleNamespace(k=B(1), t=B('.01'), high=Fraction(10))
        audit.scalar_root_signs(model, proof, Decimal(0))
        from copy import deepcopy
        corrupt = deepcopy(proof)
        corrupt['normalizedPrice']['lower'] = str(rh)
        with self.assertRaises(ValueError):
            audit.scalar_root_signs(model, corrupt, Decimal(0))
        corrupt = deepcopy(proof)
        corrupt['rivalExact'] = '1'
        with self.assertRaises(ValueError):
            audit.scalar_root_signs(model, corrupt, Decimal(0))
        clipped = deepcopy(proof)
        clipped['proof']['kind'] = 'ceiling-clipped'
        clipped['normalizedPrice'] = {'lower': '1.25', 'upper': '1.25'}
        audit.scalar_root_signs(SimpleNamespace(k=B(1), t=B('.01'), high=Fraction(5,4)),
                                clipped, Decimal(0))
        clipped['normalizedPrice'] = {'lower': '2', 'upper': '2'}
        with self.assertRaises(ValueError):
            audit.scalar_root_signs(SimpleNamespace(k=B(1), t=B('.01'), high=Fraction(2)),
                                    clipped, Decimal(0))


if __name__ == '__main__':
    unittest.main()
