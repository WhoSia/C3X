import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'product'))
from c3x_plan_evidence import audit, required_plan_trial


def row(depth, native, pv, *, cp=89, chooser='black', eligible=True):
    return dict(depth=depth, native=native, pv=pv.split(), move=pv.split()[0],
                cp=cp, bound='none', eligible=eligible, fork_chooser=chooser)


class PlanAuditTest(unittest.TestCase):
    def test_equal_native_different_reply_is_not_plan_proof(self):
        a = row(12, 292, 'd1e2 d6h2 g1h1')
        b = row(18, 292, 'd1e2 d6e7 b2b4')
        result = audit('s28-l2-1.4', [a, b], judge={'d6h2': {'12': -111, '14': -109},
                                                'd6e7': {'12': -95, '14': -98}}, replay_verified=True)
        self.assertEqual(result.first_divergence_ply, 2)
        self.assertEqual(result.native_values, (292, 292))
        self.assertEqual(result.verdict, 'JUDGE_ORDER_STABLE_AT_TESTED_DEPTHS')
        self.assertEqual([x[2] for x in result.judge_order], [16, 11])
        self.assertEqual(result.judge_order[0][1], 'd6e7')
        self.assertIn('CAUSAL_CONTRAST_UNPROVEN', result.provenance)
        self.assertEqual(required_plan_trial(result)['result'], 'NOT_TESTED')

    def test_spanish_depth_reversal(self):
        a = row(8, 128, 'e1g1 f6e4 d2d4', cp=39, chooser='white')
        b = row(10, 131, 'e1g1 f6e4 f1e1 e4c5', cp=39, chooser='white')
        result = audit('spanish', [a, b], judge={'d2d4': {'12': 56, '14': 49},
                                               'f1e1': {'12': 68, '14': -12}})
        self.assertEqual(result.first_divergence_ply, 3)
        self.assertEqual(result.verdict, 'DEPTH_SENSITIVE_FORK_PREFERENCE')
        self.assertEqual(result.shared_prefix, ('e1g1', 'f6e4'))

    def test_reject_bounds_missing_native_and_nonfork(self):
        a = row(12, 292, 'd1e2 d6h2')
        b = row(18, 292, 'd1e2 d6e7')
        for broken in ({**a, 'bound': 'upper'}, {**a, 'eligible': False},
                       {**a, 'native': None}, {**a, 'fork_chooser': 'white'}):
            with self.assertRaises(ValueError): audit('bad', [broken, b])
        with self.assertRaises(ValueError): audit('prefix', [a, row(18, 292, 'd1e2 d6h2 g1h1')])
        with self.assertRaises(ValueError): audit('root', [a, row(18, 292, 'c1d2 d6e7')])
        with self.assertRaises(ValueError): audit('scores', [a, row(18, 293, 'd1e2 d6e7', cp=88)])

    def test_partial_judge_never_implicitly_imputes(self):
        a, b = row(12, 292, 'd1e2 d6h2'), row(18, 292, 'd1e2 d6e7')
        out = audit('partial', [a, b], judge={'d6h2': {'12': -111}, 'd6e7': {'14': -98}})
        self.assertEqual(out.verdict, 'INCONCLUSIVE_JUDGEMENT')
        self.assertTrue(all(p is None for _, p, _ in out.judge_order))

    def test_missing_judge_abstains(self):
        a, b = row(12, 292, 'd1e2 d6h2'), row(18, 292, 'd1e2 d6e7')
        out = audit('none', [a, b])
        self.assertEqual(out.verdict, 'NO_INDEPENDENT_JUDGEMENT')
        self.assertFalse(out.both_continuations_replayed)


if __name__ == '__main__':
    unittest.main()
