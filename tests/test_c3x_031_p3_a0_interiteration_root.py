"""P3-A0 authentic P2-D1 root-iteration lineage and fail-closed synthetic controls.

The one original game was previously exposed to R26 at tournament-macro level.
No new Stockfish run and no causal TT/history mediator claim is tested here.
"""
from copy import deepcopy
import os
from pathlib import Path
import zipfile
import json
import tempfile
import unittest

from c3x_031_p3_a0_interiteration_root import audit, parse, trace, sha, LOG_SHA, RESULT_ZIP_SHA

ORIGINAL_LOG = Path(os.environ.get("C3X_P3_A0_NATIVE_ZIP",
                                   "/tmp/c3x-p3-a0/native-original.zip"))
ORIGINAL_SCIENCE = Path(os.environ.get("C3X_P3_A0_SCIENCE_ZIP",
                                       "/tmp/c3x-p3-a0/science-original.zip"))


class P3A0SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = audit(ORIGINAL_LOG, ORIGINAL_SCIENCE)
        with zipfile.ZipFile(ORIGINAL_SCIENCE) as source:
            j = json.loads(source.read("C3X_031_P2_D1_ALL_NATIVE_EQUAL_DEPTH_EVENTS.json"))
        cls.case = next(x for x in j["results"] if x["source_event_id"] == "P2-028-0")
        cls.cell = next(x for x in cls.case["fixed_depth_cells"] if x["depth"] == 16)
        with zipfile.ZipFile(ORIGINAL_LOG) as z:
            cls.base = parse(z.read("P2-028-0/depth-16/untouched-0/stderr.txt"))
            cls.treated = parse(z.read("P2-028-0/depth-16/both_off-0/stderr.txt"))

    def test_original_signed_archives_and_provenance(self):
        self.assertEqual(sha(ORIGINAL_LOG.read_bytes()), LOG_SHA)
        self.assertEqual(sha(ORIGINAL_SCIENCE.read_bytes()), RESULT_ZIP_SHA)
        self.assertEqual(self.original["new_native_searches"], 0)
        self.assertEqual(self.original["original_D1_native_searches"], 78)
        self.assertTrue(self.original["R26_prior_exposed_macro_family"])
        self.assertFalse(self.original["TT_history_or_budget_causal_mediator_identified"])

    def test_source_event_actual_contact_and_new_child_work(self):
        a = self.original["root_trajectories"]["16"]
        self.assertEqual(a["physical_child_return"], [-2429, -2500])
        self.assertEqual(a["actual_treated_child_replies"], 2)
        self.assertEqual(self.original["original_physical_target"]["event"], "19")

    def test_same_contact_attempt_no_visible_root_change_but_more_nodes(self):
        a = self.original["root_trajectories"]["16"]["root_attempts"][15]
        self.assertEqual(a["attempt"], 16)
        self.assertEqual(a["iteration"], 13)
        self.assertEqual(a["same_move_value_changes"], 0)
        self.assertEqual(a["same_move_update_changes"], 0)
        self.assertEqual(a["different_candidate_at_same_index"], 0)
        self.assertEqual((a["control_end"]["nodes"], a["treated_end"]["nodes"]), (7699, 7717))
        self.assertEqual((a["control_end"]["move"], a["treated_end"]["move"]), ("d4e5", "d4e5"))

    def test_first_root_value_drift_at_next_iteration(self):
        a = self.original["root_trajectories"]["16"]["first_root_same_move_value_change"]
        self.assertEqual((a["attempt"], a["iteration"], a["index"], a["move"]),
                         (17, 14, 2, "f4e5"))
        self.assertEqual((a["control"], a["treated"]), (2265, 2280))
        self.assertEqual((a["update_control"], a["update_treated"]), (0, 0))
        self.assertEqual((a["alpha_control"], a["alpha_treated"]), (2289, 2289))

    def test_first_leader_changed_later_at_same_root_window(self):
        a = self.original["root_trajectories"]["16"]["first_root_leader_update_change"]
        self.assertEqual((a["attempt"], a["iteration"], a["move"]), (18, 15, "f4e5"))
        self.assertEqual((a["control_value"], a["treated_value"]), (2238, 2256))
        self.assertEqual((a["control_update"], a["treated_update"]), (0, 1))
        r = self.original["root_trajectories"]["16"]["root_attempts"][17]
        self.assertEqual(r["control_start_alpha_beta"], r["treated_start_alpha_beta"])
        self.assertEqual((r["control_end"]["move"], r["treated_end"]["move"]), ("d4e5","f4e5"))

    def test_first_root_window_divergence_only_at_final_depth16(self):
        x = self.original["root_trajectories"]["16"]["first_root_start_window_change"]
        self.assertEqual(x["attempt"], 19)
        self.assertEqual(x["control_alpha_beta"], [1932, 2602])
        self.assertEqual(x["treated_alpha_beta"], [1911, 2563])
        self.assertIsNone(self.original["root_trajectories"]["15"]["first_root_start_window_change"])

    def test_same_first_two_transition_events_at_fixed_depth_15_and_16(self):
        a, b = (self.original["root_trajectories"][str(d)] for d in (15,16))
        self.assertEqual(a["first_root_same_move_value_change"],
                         b["first_root_same_move_value_change"])
        self.assertEqual(a["first_root_leader_update_change"],
                         b["first_root_leader_update_change"])
        self.assertEqual(a["final_fixed_depth_root_choice"], ["d4e5","f4e5"])
        self.assertEqual(b["final_fixed_depth_root_choice"], ["d4e5","f4e5"])

    def test_reject_fabricated_root_leader_change(self):
        poisoned = deepcopy(self.treated)
        row = next(x for x in poisoned["C3X_R23_CANDIDATE"]
                   if x["attempt"]=="18" and x["move"]=="f4e5")
        row["update"]="0"
        with self.assertRaisesRegex(ValueError, "first observed downstream root"):
            trace(self.base, poisoned, self.case["target"], 16, self.cell)

    def test_reject_fake_physical_target_return(self):
        poisoned = deepcopy(self.treated)
        row = next(x for x in poisoned["C3X_R33_CLOSE"] if x["event"]=="19")
        row["value"]="−2500"
        with self.assertRaisesRegex(ValueError, "treated physical return"):
            trace(self.base, poisoned, self.case["target"], 16, self.cell)

    def test_reject_changed_source_target_prefix(self):
        poisoned = deepcopy(self.treated)
        row = next(x for x in poisoned["C3X_R33_OPEN"] if x["event"]=="19")
        row["key"]="000000000000000000"
        with self.assertRaisesRegex(ValueError, "physical contact identity"):
            trace(self.base, poisoned, self.case["target"], 16, self.cell)

    def test_reject_bad_zip_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"changed.zip"
            p.write_bytes(ORIGINAL_LOG.read_bytes()+b"x")
            with self.assertRaisesRegex(ValueError, "ZIP SHA"):
                audit(p,ORIGINAL_SCIENCE)


if __name__ == "__main__":
    unittest.main()
