"""P2 1669 original-source native method tests; synthetic signatures only."""
import unittest

from c3x_031_p1_forecast import PUBLIC, SOURCE
from c3x_031_p2_1669_native_discovery import (
    MODEL_SHA, SAMPLE_SHA, NODES, native_features, require,
)


class NativeSourceFreezeTests(unittest.TestCase):
    def native(self, **changes):
        event = {"event":"15","null_eligible":"1","depth":"3","ply":"4",
                 "floor":"234","beta":"230","nodes":"12000",
                 "attempt":"19","root":"a2a3"}
        event.update(changes)
        return event

    def test_exact_independently_frozen_hashes(self):
        self.assertEqual(
            SAMPLE_SHA,"8b7f5da799cc9610c7e4cb8347baa8b3b8bd74eb383939eac9fa91b527a8116d")
        self.assertEqual(
            MODEL_SHA,"ae6f7add6838dc3b4cbe679bd728625593c4e3f9817ea1101e4a7fb550da8c53")
        self.assertEqual(NODES,32000)

    def test_preserve_original_public_score_bound(self):
        features=native_features((12,89,3,0,1),self.native(),"a2a3","1")
        self.assertEqual(set(features),set(PUBLIC+SOURCE))
        self.assertEqual(features["public_score_cp"],89)
        self.assertEqual(features["public_upper_bound"],0)
        self.assertEqual(features["public_lower_bound"],1)
        self.assertEqual(features["source_root_is_public_best"],1)
        self.assertEqual(features["futility_slack"],4)
        self.assertEqual(features["source_progress_nodes"],12000)
        self.assertEqual(features["stratum"],1)

    def test_compare_exact_original_root_identifier(self):
        features=native_features((11,-17,5,1,0),self.native(),"b2b3","1")
        self.assertEqual(features["source_root_is_public_best"],0)

    def test_reject_ineligible_null_stratum(self):
        with self.assertRaises(ValueError):
            native_features((12,89,3,0,0),self.native(),"a2a3","0")

    def test_reject_negative_futility_slack(self):
        with self.assertRaises(ValueError):
            native_features((12,89,3,0,0),self.native(floor="210"),"a2a3","1")

    def test_hashes_and_zero_treatment_bounded_scope(self):
        self.assertNotEqual(SAMPLE_SHA,MODEL_SHA)
        self.assertRaises(ValueError,require,False,"frozen sources changed")


if __name__=="__main__":
    unittest.main()
