"""P2 full-fit only-P1 model lock and deliberate tamper tests."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from c3x_031_p2_lockcheck import fit, verify, predict
from c3x_031_p1_forecast import PUBLIC, SOURCE, load_rows

ROOT=Path(__file__).resolve().parents[1]
M=ROOT/"frozen/C3X_031_P2_FINAL_MODELS_PREOUTCOME_20261121.json"
T=ROOT/"frozen/C3X_031_P1_R33_128_PRETREATMENT_ROWS_20261121.tsv"


class P2LockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=json.loads(M.read_text())
        cls.rows=load_rows(T)

    def test_frozen_raw_bytes_recreate_actual_preoutcome_P1_fit(self):
        court=verify(M,T)
        self.assertEqual(court["P1_rows"],128)
        self.assertEqual(court["P2_treatments_seen"],0)
        self.assertTrue(court["P1_label_source_only"])

    def test_m0_train_prevalence_not_heldout_refit(self):
        for r in self.rows:
            self.assertAlmostEqual(predict(self.model,r,"m0"),11.5/129,places=15)

    def test_m1_m2_source_feature_separation(self):
        self.assertEqual(tuple(self.model["m1"]["features"]),PUBLIC)
        self.assertEqual(tuple(self.model["m2"]["features"]),PUBLIC+SOURCE)
        for model in ("m1","m2"):
            self.assertTrue(all(0<predict(self.model,r,model)<1 for r in self.rows))

    def test_reject_missing_source_feature(self):
        bad=deepcopy(self.rows[0])
        del bad["source_progress_nodes"]
        with self.assertRaises(ValueError):
            predict(self.model,bad,"m2")

    def test_original_training_features_are_not_treatment_ret(self):
        for m in ("m1","m2"):
            self.assertNotIn("treated_child_return",self.model[m]["features"])
            self.assertNotIn("y",self.model[m]["features"])

    def test_m2_is_not_a_causal_mediator(self):
        self.assertEqual(self.model["schema"],"C3X_031_P2_FIXED_MODEL_PRE_OUTCOME_V1")
        self.assertFalse(self.model["used_p2_test_outcomes"])


if __name__=="__main__":
    unittest.main()
