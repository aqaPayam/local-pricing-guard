"""Independent synthetic controller-certificate tests; no real scenario runs."""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
import importlib.util, sys, unittest, copy
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('sparse_audit',Path(__file__).resolve().parents[1]/'research/audit-sparse-reset.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class SparseAuditTests(unittest.TestCase):
    def test_exact_saved_weight_prefix_floor_both_orbit_directions(self):
        prices = [1,2,3]
        rewards = [float(20-i-j) for i in range(3) for j in range(3)]
        for upper,cap,expected_floor,expected_mean in [([1,2,2],0,18,18),([0,0,1],2,16,18)]:
            result = audit.exact_finite_prefix(prices,upper,cap,rewards,3)
            self.assertEqual(result['floor'],Fraction(expected_floor))
            self.assertEqual(result['average'],Fraction(expected_mean))
            sequence = [Fraction(rewards[i*3+i]) for i in result['indices']]
            for horizon in range(1,31):
                average = sum(sequence[j%3] for j in range(horizon))/horizon
                self.assertGreaterEqual(average,result['floor'])
        self.assertFalse(result['descending'])
        self.assertEqual(result['horizon'],1)
        with self.assertRaises(ValueError):
            audit.exact_finite_prefix(prices,[2,0,1],0,rewards,3)

    def test_power_encloses_exact_fraction_and_zero_exponent(self):
        value = audit.B.rational(Fraction(2,3))
        for n in [0,1,2,17,65536]:
            result = audit.power(value,n)
            expected = Fraction(2,3)**n
            self.assertLessEqual(Fraction(result.low),expected)
            self.assertGreaterEqual(Fraction(result.high),expected)

    def test_rational_certificate_rejects_a_forged_prefix_floor(self):
        game = {'prices':[1,2,3],'upper':[0,0,1],'capIndex':2,
                'rewards':{'consumerSurplus':[float(20-i-j) for i in range(3) for j in range(3)]}}
        certificate = {'period':3,'cycleIndices':[2,1,0],
                       'cycleAverageExact':{'numerator':'18','denominator':'1'},
                       'cycleAverageLower':18.,'activationFloorExact':{'numerator':'16','denominator':'1'},
                       'activationFloorLower':16.,'minimizingPrefix':1,'descending':False,'capFirst':True}
        audit.check_finite_certificate(game,certificate)
        certificate['activationFloorExact']['numerator'] = '18'
        with self.assertRaises(ValueError):
            audit.check_finite_certificate(game,certificate)

    def test_independent_signed_upper_root_accepts_reference_and_rejects_corruptions(self):
        case = {'scenario':{'economy':{'id':'synthetic','quality':0,'cost':0,'mu':1,'buyers':1,'outsideQuality':0},'epsilon':.001},'game':{'prices':[0,3]}}
        model = audit.backend.AuditEconomy(case,'nominal')
        with localcontext() as ctx:
            ctx.prec = 200
            y = Decimal('.5')
            z = 1/(Decimal(1).exp()*(1+(-y).exp()))
            w = z
            for _ in range(40):
                w -= (w*w.exp()-z)/(w.exp()*(1+w))
            lo,hi = 1+w,Decimal(3)
            t = Decimal.from_float(.001)
            for _ in range(400):
                x = (lo+hi)/2
                f = x/(1+(1+(-y).exp())*x.exp())
                if f > w-t:
                    lo = x
                else:
                    hi = x
            x = (lo+hi)/2
            wb = audit.B(w-Decimal('1e-60'),w+Decimal('1e-60'))
            root = audit.B(x-Decimal('1e-45'),x+Decimal('1e-45'))
        record = {'rivalExact':'.5','bestProfitW':wb.strings(),
                  'bestResponse':(1+wb).strings(),'normalizedTargetProfit':(wb-model.t).strings(),
                  'normalizedPrice':root.strings(),'proof':{'kind':'interior upper root'}}
        observed = audit.check_scalar_upper(model,record,y)
        self.assertEqual(observed.low,root.low)
        for mutate in [lambda r:r['bestProfitW'].update(lower='0',upper='0'),
                       lambda r:r['normalizedPrice'].update(lower='2.9',upper='2.9'),
                       lambda r:r.update(rivalExact='.6')]:
            changed = copy.deepcopy(record)
            mutate(changed)
            with self.assertRaises(ValueError):
                audit.check_scalar_upper(model,changed,y)


if __name__ == '__main__':
    unittest.main()
