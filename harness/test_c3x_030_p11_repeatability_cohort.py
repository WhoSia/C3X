import unittest
from c3x_030_p11_repeatability_cohort import positions, arm_summary, CHECKPOINTS, ARMS, engine_options

class TestP11(unittest.TestCase):
    def test_twenty_precommitted_unique_legal_positions(self):
        p=positions()
        self.assertEqual(len(p),20)
        self.assertEqual(len({v["fen"] for v in p.values()}),20)
    def test_all_four_openings_five_checkpoints(self):
        p=positions()
        self.assertEqual(sorted(len(v["history_uci"]) for v in p.values()),
                         sorted(list(CHECKPOINTS)*4))
    def test_all_full_strength_and_no_skill_sampling(self):
        self.assertEqual(len(ARMS),3)
        for _,threads,_ in ARMS:
            x=engine_options(threads)
            self.assertEqual(x["Skill Level"],20)
            self.assertFalse(x["UCI_LimitStrength"])
            self.assertFalse(x["Use NNUE"])
    def test_entropy_zero_for_identical_move(self):
        x=arm_summary([dict(move_uci="e2e4",nodes_actual=1200,depth=5)]*4)
        self.assertEqual(x["empirical_move_entropy_bits"],0)
        self.assertFalse(x["switch_observed"])
    def test_entropy_one_bit_for_two_equally_common_moves(self):
        x=arm_summary([dict(move_uci=m,nodes_actual=1000,depth=5)
                       for m in ("e2e4","d2d4","e2e4","d2d4")])
        self.assertAlmostEqual(x["empirical_move_entropy_bits"],1)
        self.assertTrue(x["switch_observed"])
    def test_empty_arm_rejected(self):
        with self.assertRaisesRegex(ValueError,"EMPTY_ARM"): arm_summary([])
if __name__=="__main__":unittest.main()
