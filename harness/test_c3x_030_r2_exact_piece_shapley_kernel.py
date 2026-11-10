"""C3X 0.30/R2 complete-coalition exact Shapley contracts."""
import math
import unittest
from c3x_030_r2_exact_piece_shapley_kernel import shapley_exact


class ExactShapley(unittest.TestCase):
    def test_additive_two_pieces(self):
        r=shapley_exact(["pawn","rook"],{"0":0.5,"1":0.7,"2":0.8,"3":1.0})
        self.assertAlmostEqual(r["piece_feature_shapley_values"]["pawn"],0.2)
        self.assertAlmostEqual(r["piece_feature_shapley_values"]["rook"],0.3)
        self.assertAlmostEqual(r["efficiency_residual"],0.0)

    def test_interaction_split_equally(self):
        r=shapley_exact(["a","b"],{"0":0,"1":0,"2":0,"3":6})
        self.assertAlmostEqual(r["piece_feature_shapley_values"]["a"],3)
        self.assertAlmostEqual(r["piece_feature_shapley_values"]["b"],3)

    def test_negative_piece_contribution(self):
        r=shapley_exact(["x","y"],{"0":0.5,"1":0.3,"2":0.8,"3":0.6})
        self.assertAlmostEqual(r["piece_feature_shapley_values"]["x"],-0.2)
        self.assertAlmostEqual(r["piece_feature_shapley_values"]["y"],0.3)

    def test_three_piece_synergy(self):
        table={str(x): 100.0 if x==7 else 0.0 for x in range(8)}
        r=shapley_exact(["a","b","c"],table)
        for value in r["piece_feature_shapley_values"].values():
            self.assertAlmostEqual(value,100/3)

    def test_reject_incomplete_subset_table(self):
        with self.assertRaisesRegex(ValueError,"COMPLETE_COALITION"):
            shapley_exact(["a","b"],{"0":0,"1":1,"3":4})

    def test_reject_nan(self):
        with self.assertRaisesRegex(ValueError,"NONFINITE"):
            shapley_exact(["a"],{"0":0,"1":math.nan})

    def test_reject_feature_alias_duplicate(self):
        with self.assertRaisesRegex(ValueError,"FEATURE_SUPPORT"):
            shapley_exact(["a","a"],{"0":0,"1":1,"2":2,"3":4})

    def test_methods_not_misrepresented(self):
        r=shapley_exact(["rook"],{"0":0.5,"1":0.6})
        self.assertFalse(r["source_decision_causality_inferred"])
        self.assertFalse(r["full_chess_SHAP_reproduction"])
        self.assertTrue(r["chess_piece_removal_may_be_illegal"])


if __name__=="__main__":
    unittest.main()
