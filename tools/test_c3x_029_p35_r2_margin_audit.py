import unittest
from c3x_029_p35_r2_margin_audit import margin_bin, misranking_probability, validate_registry

class P35MarginAuditTest(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual([margin_bin(x) for x in (0,19.999,20,99.999,100)],
                         ["near","near","intermediate","intermediate","wide"])
    def test_bad_gap(self):
        for x in (-1,float("nan"),float("inf")):
            with self.assertRaises(ValueError): margin_bin(x)
    def test_misrank_math(self):
        self.assertAlmostEqual(misranking_probability(0,20),0.5)
        self.assertAlmostEqual(misranking_probability(20,20),0.23975006109347674)
        self.assertLess(misranking_probability(100,20),misranking_probability(10,20))
        self.assertAlmostEqual(misranking_probability(10,20),misranking_probability(-10,20))
    def test_disjoint(self):
        res=validate_registry([{"game_id":"g1","split":"dev","abs_gap_cp":5},
                               {"game_id":"g2","split":"heldout","abs_gap_cp":180}])
        self.assertEqual(res["counts"]["dev:near"],1)
        self.assertEqual(res["games"],2)
    def test_leakage(self):
        with self.assertRaisesRegex(ValueError,"contamination"):
            validate_registry([{"game_id":"g1","split":"dev","abs_gap_cp":5},
                               {"game_id":"g1","split":"heldout","abs_gap_cp":180}])

if __name__=="__main__":unittest.main()
