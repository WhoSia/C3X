import unittest
from c3x_030_p11s1_search_state_ablation import summarize, ARMS, engine_configuration, REPEATS
class Contract(unittest.TestCase):
    def test_full_strength(self):
        c=engine_configuration()
        self.assertEqual(c["Skill Level"],20)
        self.assertEqual(c["Threads"],1)
        self.assertFalse(c["UCI_LimitStrength"])
        self.assertFalse(c["Use NNUE"])
    def test_four_unique_arms(self):
        self.assertEqual(len(ARMS),4)
        self.assertEqual(len(set(ARMS)),4)
    def test_no_switch(self):
        r=summarize([dict(move_uci="e2e4",nodes_actual=12000)]*REPEATS)
        self.assertFalse(r["observed_switch"])
        self.assertEqual(r["entropy_bits"],0)
    def test_switch_entropy(self):
        r=summarize([dict(move_uci=s,nodes_actual=12000)
                     for s in ("e2e4","d2d4","e2e4","d2d4","e2e4","d2d4")])
        self.assertTrue(r["observed_switch"])
        self.assertAlmostEqual(r["entropy_bits"],1)
    def test_repetition_guard(self):
        with self.assertRaisesRegex(ValueError,"REPETITION_COUNT"):
            summarize([dict(move_uci="e2e4",nodes_actual=12000)])
if __name__=="__main__":unittest.main()
