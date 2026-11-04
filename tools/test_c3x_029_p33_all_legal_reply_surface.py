import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_029_p33_all_legal_reply_surface_native import summarize_surface,ADAPTIVE_CASE_IDS


class P33AllReply(unittest.TestCase):
    def test_outside_top3_is_discovered(self):
        x=[{"opponent_reply_uci":f"a{i}a{i+1}",
            "value_root_pov_cp_or_mate_scaled":v} for i,v in [(1,40),(2,20),(3,-25),(4,0)]]
        out=summarize_surface(x,["a1a2","a2a3","a4a5"],"a3a4")
        self.assertEqual(out["entire_legal_reply_count"],4)
        self.assertFalse(out["argmin_found_in_prior_top3"])
        self.assertEqual(out["argmin_uci"],"a3a4")
        self.assertEqual(out["actual_reply_value_minus_worst_cp"],0)

    def test_ties_sort_deterministically(self):
        x=[{"opponent_reply_uci":"h2h3","value_root_pov_cp_or_mate_scaled":0},
           {"opponent_reply_uci":"a2a3","value_root_pov_cp_or_mate_scaled":0}]
        out=summarize_surface(x,["h2h3"],"a2a3")
        self.assertEqual(out["argmin_uci"],"a2a3")
        self.assertFalse(out["argmin_found_in_prior_top3"])

    def test_duplicate_uci_rejected(self):
        with self.assertRaisesRegex(ValueError,"BAD_REPLY_UNIVERSE"):
            summarize_surface([{"opponent_reply_uci":"e2e4","value_root_pov_cp_or_mate_scaled":0}]*2,[])

    def test_selected_are_source_exposed_and_fixed(self):
        self.assertEqual(ADAPTIVE_CASE_IDS,(6,10,14))

if __name__=="__main__":
    unittest.main()
