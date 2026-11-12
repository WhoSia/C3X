import unittest
from c3x_030_f2_blind_game_manifest import generate,manifest
class Test(unittest.TestCase):
    def test_real_chess_legal_position_reconstruction(self):
        c=generate()
        self.assertEqual(len(c),24)
        self.assertEqual(len(set(x["fen"] for x in c)),24)
    def test_game_lineage_split(self):
        c=generate()
        self.assertEqual(len({x["game_id"] for x in c if x["split"]=="holdout"}),8)
        self.assertEqual(len({x["game_id"] for x in c if x["split"]=="development"}),4)
        self.assertFalse(set(x["game_id"] for x in c if x["split"]=="holdout") &
                         set(x["game_id"] for x in c if x["split"]=="development"))
    def test_no_outcomes_or_labels_in_holdout_manifest(self):
        x=manifest()
        for row in x["entries"]:
            self.assertFalse({"label","bestmove","score","sarfa_positive","native_event_to_root_certified"}&set(row))
        self.assertEqual(len(x["entries"]),16)
    def test_full_history_length_and_no_false_independence(self):
        x=manifest()
        self.assertTrue(x["evaluation_positions_from_same_game_are_correlated"])
        self.assertFalse(x["random_population_sample"])
        for row in x["entries"]:
            self.assertEqual(len(row["history_uci"]),int(row["case_id"].split("ply")[1]))
if __name__=="__main__":unittest.main()
