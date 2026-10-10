#!/usr/bin/env python3
"""Preoutcome strict native SEE physical TT source and ancestry match guard."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_023_P1_same_descendant_SEE_node_matcher import identity,candidates,FIELDS
def evt(**kw):
    x={"kind":"witness","root_call":6,"root_move":500,
       "key64":347,"parent_key64":173,"path_hash":9173,
       "path_length":4,"move":99,"site":"quiet_prune",
       "threshold":-95,"original":0,"delivered":0}
    x.update(kw);return x
class NativeSameNodeIdentity(unittest.TestCase):
    def test_same_key_is_not_enough_without_path(self):
        x=candidates([evt()],[evt(path_hash=8714)],True)
        self.assertEqual(x["status"],"NO_SHARED_SEE_NODE_IN_FULL_LOGGED_SCOPE")
        self.assertEqual(x["matched"],[])
    def test_genuine_parent_path_and_site_threshold_match(self):
        x=candidates([evt()],[evt()],True)
        self.assertEqual(x["status"],"SOURCE_PATH_FINGERPRINT_COMMON_NODE_IDENTIFIED")
        self.assertEqual(x["first_shared"]["exact_source_identity"]["parent_key64"],173)
        self.assertFalse(x["first_shared"]["full_raw_chess_path_bytes_proved"])
    def test_different_SEE_threshold_fails_source_identity(self):
        x=candidates([evt()],[evt(threshold=0)],True)
        self.assertFalse(x["matched"])
    def test_raw_same_source_but_no_actual_TT_block_is_HOLD(self):
        x=candidates([evt()],[evt()],False)
        self.assertTrue(x["status"].startswith("HOLD_"))
    def test_duplicate_occurrence_not_unique_identity(self):
        x=candidates([evt(),evt()],[evt()],True)
        self.assertEqual(x["dropped_nonunique_repeated_source_identities"],1)
        self.assertIsNone(x["first_shared"])
    def test_censoring_does_not_claim_absence(self):
        x=candidates([evt(site="quiet_prune"),{"kind":"censored"}],
                     [evt(site="qsearch_prune")],True)
        self.assertEqual(x["status"],"NO_SHARED_SEE_NODE_IN_OBSERVED_PREFIX__CENSORED_HOLD")
    def test_passive_boolean_stability_required(self):
        with self.assertRaises(ValueError):
            candidates([evt()],[evt(original=1,delivered=1)],True)
        with self.assertRaises(ValueError):
            candidates([evt(delivered=1)],[evt()],True)
    def test_all_native_node_fields_included(self):
        self.assertIn("path_hash",FIELDS)
        self.assertIn("root_move",FIELDS)
        self.assertIn("parent_key64",FIELDS)
if __name__=="__main__":unittest.main()
