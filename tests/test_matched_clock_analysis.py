import importlib.util
from pathlib import Path
import unittest
from copy import deepcopy
from fractions import Fraction

spec = importlib.util.spec_from_file_location('matched_clock_analysis', Path(__file__).parents[1] / 'research/matched-clock-analysis.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture():
    rows = []
    for i, seed in enumerate(mod.SEEDS):
        for arm in mod.ARMS:
            value = Fraction(70) + (Fraction(i - 6, 7) if arm == 'recurring4' else 0)
            rows.append(dict(seed=seed, arm=arm, runId=mod.normalized_run_id(seed, arm),
                             executionSucceeded=True, available=True, replayMatched=True,
                             cycleCustomerBenefit=mod.packed(value), unavailableReason=None,
                             step=2_000_000, nextPhase=4, previousIndices=[0, 61], cycleLength=4,
                             checkpointSha256='a' * 64, graphSha256='b' * 64))
    return rows


class ExactMatchedSummary(unittest.TestCase):
    def test_all_signed_pairs_and_exact_planned_mean(self):
        result = mod.aggregate(reversed(fixture()))
        self.assertEqual([r['seed'] for r in result['pairedRows']], list(mod.SEEDS))
        self.assertEqual(mod.exact(result['primarySummary']['meanDifference']), Fraction(-1, 14))
        self.assertEqual(result['completePairDescription']['signCounts'], dict(positive=5, zero=1, negative=6))

    def test_one_missing_endpoint_nulls_planned_mean_without_dropping_pair(self):
        rows = fixture()
        rows[1].update(available=False, replayMatched=False, cycleCustomerBenefit=None,
                       unavailableReason='Final artifact incomplete', executionSucceeded=False)
        result = mod.aggregate(rows)
        self.assertEqual(len(result['pairedRows']), 12)
        self.assertIsNone(result['primarySummary']['meanDifference'])
        self.assertEqual(result['primarySummary']['plannedDenominator'], 12)
        self.assertEqual(result['completePairDescription']['denominator'], 11)
        self.assertNotIn(907001, result['completePairDescription']['seedIds'])
        self.assertIsNone(result['pairedRows'][0]['difference'])

    def test_validated_predeadline_endpoint_can_survive_later_execution_failure(self):
        rows = fixture()
        rows[0]['executionSucceeded'] = False
        result = mod.aggregate(rows)
        self.assertTrue(result['primarySummary']['available'])
        self.assertEqual(result['pairedRows'][0]['executionSucceeded'], [False, True])

    def test_all_missing_keeps_every_identity_and_no_zero_imputation(self):
        rows = fixture()
        for row in rows:
            row.update(available=False, replayMatched=False, executionSucceeded=False,
                       cycleCustomerBenefit=None, unavailableReason='No eligible checkpoint')
        result = mod.aggregate(rows)
        self.assertEqual(len(result['pairedRows']), 12)
        self.assertIsNone(result['primarySummary']['meanDifference'])
        self.assertIsNone(result['completePairDescription']['meanDifference'])
        self.assertEqual(result['completePairDescription']['denominator'], 0)

    def test_corrupt_inventory_status_terminal_and_fraction_are_rejected(self):
        base = fixture()
        mutations = [lambda x: x.pop(), lambda x: x.__setitem__(1, deepcopy(x[0])),
                     lambda x: x[0].update(runId='old-compact-run'),
                     lambda x: x[0].update(available=1),
                     lambda x: x[0].update(replayMatched=False),
                     lambda x: x[0].update(step=1_000_000),
                     lambda x: x[0].update(nextPhase=0),
                     lambda x: x[0].update(previousIndices=[-1, 2]),
                     lambda x: x[0].update(cycleLength=3),
                     lambda x: x[0].update(checkpointSha256='none'),
                     lambda x: x[0].update(cycleCustomerBenefit={'numerator': '140', 'denominator': '2'}),
                     lambda x: x[0].update(cycleCustomerBenefit={'numerator': '-0', 'denominator': '1'}),
                     lambda x: x[0].update(available=False, unavailableReason='failed')]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                rows = deepcopy(base)
                mutate(rows)
                with self.assertRaises(ValueError):
                    mod.aggregate(rows)


if __name__ == '__main__':
    unittest.main()
