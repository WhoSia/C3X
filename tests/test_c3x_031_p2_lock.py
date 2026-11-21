"""P2 locked-model tests: full P1 training, exact source parity, no labels at score time."""
import json
from copy import deepcopy
from pathlib import Path
import unittest

from c3x_031_p1_forecast import PUBLIC, SOURCE, fit_predict, load_rows
from c3x_031_p2_lock import infer, predict, seal

ROOT=Path(__file__).resolve().parents[1]
TABLE=ROOT/"frozen/C3X_031_P1_R33_128_PRETREATMENT_ROWS_20261121.tsv"


class P2ModelSealTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=load_rows(TABLE)
        cls.seal=seal(TABLE)

    def test_full_original_training_only(self):
        self.assertEqual(self.seal["training_event_families"],16)
        self.assertEqual(self.seal["training_games"],64)
        self.assertEqual(self.seal["training_positives"],11)
        self.assertEqual(self.seal["training_physical_events"],128)
        self.assertIs(self.seal["training_new_p2_outcomes_seen"],False)
        self.assertEqual(self.seal["source_native_p2_searches_seen"],0)

    def test_no_unexpected_model_features(self):
        self.assertEqual(self.seal["m1"]["features"],list(PUBLIC))
        self.assertEqual(self.seal["m2"]["features"],list(PUBLIC+SOURCE))
        for mode in ("m1","m2"):
            self.assertNotIn("family",self.seal[mode]["features"])
            self.assertNotIn("y",self.seal[mode]["features"])
            self.assertEqual(len(self.seal[mode]["weights"]),
                             len(self.seal[mode]["features"])+1)

    def test_m1_exact_parity_with_p1_fit(self):
        observed=[predict(self.seal["m1"],{k:r[k] for k in PUBLIC})
                  for r in self.rows]
        reference=fit_predict(self.rows,self.rows,PUBLIC)
        self.assertEqual(len(observed),128)
        self.assertTrue(all(abs(a-b)<1e-12
                            for a,b in zip(observed,reference)))

    def test_m2_exact_parity_with_p1_fit(self):
        observed=[predict(self.seal["m2"],{k:r[k] for k in PUBLIC+SOURCE})
                  for r in self.rows]
        reference=fit_predict(self.rows,self.rows,PUBLIC+SOURCE)
        self.assertTrue(all(abs(a-b)<1e-12
                            for a,b in zip(observed,reference)))

    def test_inference_requires_no_result(self):
        first={k:self.rows[0][k] for k in PUBLIC+SOURCE}
        result=infer(self.seal,first)
        self.assertEqual(set(result),{"m0","m1","m2"})
        self.assertAlmostEqual(result["m0"],11.5/129,places=14)
        self.assertTrue(all(0<r<1 for r in result.values()))

    def test_refuse_post_intervention_label_leak(self):
        first={k:self.rows[0][k] for k in PUBLIC+SOURCE}
        first["y"]=1
        with self.assertRaises(ValueError):
            infer(self.seal,first)

    def test_refuse_original_family_leak(self):
        first={k:self.rows[0][k] for k in PUBLIC+SOURCE}
        first["family"]=99
        with self.assertRaises(ValueError):
            infer(self.seal,first)

    def test_refuse_nonfinite_public_score(self):
        first={k:self.rows[0][k] for k in PUBLIC+SOURCE}
        first["public_score_cp"]=float("nan")
        with self.assertRaises(ValueError):
            infer(self.seal,first)

    def test_refuse_contradictory_score_bounds(self):
        first={k:self.rows[0][k] for k in PUBLIC+SOURCE}
        first["public_upper_bound"]=first["public_lower_bound"]=1
        with self.assertRaises(ValueError):
            infer(self.seal,first)

    def test_deterministic_serialization(self):
        self.assertEqual(json.dumps(self.seal,sort_keys=True),
                         json.dumps(seal(TABLE),sort_keys=True))


if __name__=="__main__":
    unittest.main()
