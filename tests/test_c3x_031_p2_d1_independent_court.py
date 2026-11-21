"""P2-D1 original raw source and fixed-depth claim integrity tests."""
import json,os
from pathlib import Path
from copy import deepcopy
import unittest

from c3x_031_p2_d1_independent_court import verify

SOURCE=Path(os.environ.get("C3X_P2_D1_RESULT",
             "/tmp/p2-d1-source/C3X_031_P2_D1_ALL_NATIVE_EQUAL_DEPTH_EVENTS.json"))
LOGS=Path(os.environ.get("C3X_P2_D1_LOGS","/tmp/p2-d1-logs"))
ORIGINAL_SOURCE=Path(os.environ.get("C3X_P2_SOURCE","/tmp/p2-precontact/C3X_031_P2_PHYSICAL_EVENT_AND_FORECAST_PRETREATMENT.json"))
ORIGINAL_TREATMENT=Path(os.environ.get("C3X_P2_TREATED","/tmp/p2-treated/C3X_031_P2_TWIC1670_TREATED_NATIVE_ALL_EVENTS.json"))


class OriginalD1Court(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(SOURCE.read_text())
        cls.source=json.loads(ORIGINAL_SOURCE.read_text())
        cls.treated=json.loads(ORIGINAL_TREATMENT.read_text())
        cls.court=verify(cls.data,LOGS,cls.source,cls.treated)

    def test_actual_source_logs_and_replays(self):
        self.assertEqual(self.court["original_native_searches"],78)
        self.assertEqual(self.court["original_log_files_rehashed"],156)
        self.assertEqual(self.court["source_depth_cells"],13)
        self.assertEqual(self.court["new_searches_in_this_verifier"],0)

    def test_exact_original_32k_pair_not_inferred_from_depth(self):
        self.assertEqual(self.court["complete_original_depth_root_flips"],5)
        self.assertEqual(self.court["original_32k_exact_move_pair_reproduced"],1)
        self.assertEqual(self.court["complete_original_depth_root_same"],2)

    def test_P2_028_matched_original_pair_and_nodes(self):
        hit=next(x for x in self.court["per_case_original_depth"]
                 if x["source_event"]=="P2-028-0")
        self.assertTrue(hit["exact_original_32k_pair_reproduced"])
        self.assertEqual(hit["original_32k_move_pair"],hit["fixed_depth_move_pair"])
        self.assertEqual([hit["control_nodes"],hit["treated_nodes"]],[35662,36217])

    def test_source_contact_missing_is_explicit_not_zero_effect(self):
        self.assertEqual(self.court["all_cell_statuses"]["HOLD_SOURCE_CONTACT_OR_IDENTITY"],1)
        p=next(x for x in self.data["results"] if x["source_event_id"]=="P2-043-1")
        cell=next(c for c in p["fixed_depth_cells"] if c["depth"]==9)
        self.assertFalse(cell["matched_physical_target"])
        self.assertEqual(cell["status"],"HOLD_SOURCE_CONTACT_OR_IDENTITY")

    def test_mutated_original_game_pair_rejected(self):
        changed=deepcopy(self.data)
        changed["results"][0]["original_32k_bestmove"]="a1a8"
        with self.assertRaises(ValueError):
            verify(changed,LOGS,self.source,self.treated)

    def test_mutated_source_open_signature_rejected(self):
        changed=deepcopy(self.data)
        changed["results"][0]["fixed_depth_cells"][0]["control"]["target_event"]["open"]["root"]="a1a8"
        with self.assertRaises(ValueError):
            verify(changed,LOGS)


if __name__=="__main__":
    unittest.main()
