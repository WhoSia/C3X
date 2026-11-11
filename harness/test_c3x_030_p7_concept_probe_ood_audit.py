import copy
import hashlib
import unittest
from c3x_030_p7_concept_probe_ood_audit import audit


def rows():
    out = []
    for concept in ("center_control", "knight_outpost"):
        for i, y in enumerate((0, 1, 0, 1)):
            out.append(dict(split="train", domain="standard", concept=concept,
                            game_id="train-"+str(i), position_id="t-"+str(i),
                            position_sha256=hashlib.sha256(("train-"+str(i)).encode()).hexdigest(), label=y))
        for domain in ("standard", "chess960"):
            for i, y in enumerate((0, 1, 0, 1)):
                prob = (.1 if y == 0 else .9) if domain == "standard" else (.9 if y == 0 else .1)
                out.append(dict(split="test", domain=domain, concept=concept,
                                game_id=domain+"-"+str(i), position_id=domain+"-"+str(i),
                                label=y, probe_probability=prob,
                                position_sha256=hashlib.sha256((domain+"-"+str(i)).encode()).hexdigest()))
    return out


class TestP7ConceptProbeCourt(unittest.TestCase):
    def test_ood_gap_and_prevalence_baseline(self):
        x = audit(rows())
        r = x["concepts"]["center_control"]
        self.assertEqual(r["train_positive_prevalence"], .5)
        self.assertEqual(r["accuracy_chess960_minus_standard"], -1.)
        self.assertAlmostEqual(r["test"]["standard"]["probe_brier"], .01)
        self.assertEqual(x["actual_model_executions_performed_by_this_tool"], 0)

    def test_game_leakage_fail_closed(self):
        x = rows()
        x[5]["game_id"] = x[0]["game_id"]
        with self.assertRaisesRegex(ValueError, "GAME_GROUP_LEAKAGE"): audit(x)

    def test_missing_chess960_hold(self):
        x = [r for r in rows() if r["domain"] != "chess960"]
        with self.assertRaisesRegex(ValueError, "SINGLE_CLASS_TEST_OR_EMPTY"): audit(x)

    def test_test_invalid_probability(self):
        x = rows()
        x[4]["probe_probability"] = float("nan")
        with self.assertRaisesRegex(ValueError, "TEST_PROBABILITY"): audit(x)

    def test_duplicate_id(self):
        x = rows()
        x.append(copy.deepcopy(x[4]))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_POSITION_CONCEPT"): audit(x)

    def test_position_fingerprint_cross_split_leakage(self):
        x = rows()
        x[4]["position_sha256"] = x[0]["position_sha256"]
        with self.assertRaisesRegex(ValueError, "POSITION_FINGERPRINT_LEAKAGE"): audit(x)

    def test_bad_fingerprint(self):
        x = rows()
        x[0]["position_sha256"] = "not-a-sha"
        with self.assertRaisesRegex(ValueError, "POSITION_FINGERPRINT_FORMAT"): audit(x)

    def test_no_train_labels(self):
        x = [r for r in rows() if r["split"] == "test"]
        with self.assertRaisesRegex(ValueError, "TRAIN_CLASS_SUPPORT"): audit(x)

    def test_must_not_smuggle_scores_into_training(self):
        x = rows()
        x[0]["probe_probability"] = .1
        with self.assertRaisesRegex(ValueError, "TRAINING_CONTRACT"): audit(x)


if __name__ == "__main__":
    unittest.main()
