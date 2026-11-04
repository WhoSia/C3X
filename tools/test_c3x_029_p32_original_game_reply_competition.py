import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p32_original_game_reply_competition import row_views, compare, SOURCE_SHA


def sample():
    source={"id":1,"source_game_sha256":"a"*64,
            "full_original_mainline_uci":["e2e4","e7e5","g1f3"],
            "source_ply_before_original_move":1}
    candidate={"root_uci":"e7e5","is_source_played":True,
               "forced_root_pv_uci":["e7e5","g1f3"],
               "forced_root_value_cp_or_mate_scaled":12,
               "immediate_material_delta_cp":0,
               "best_opponent_reply":"g1f3",
               "best_opponent_reply_value_cp_or_mate_scaled":4,
               "opponent_reply_top3":[
                 {"reply_uci":x,"root_pov_cp_or_mate_scaled":i+2,
                  "mover_followup_uci":"b8c6",
                  "material_after_opponent_reply_cp":0,
                  "material_after_mover_followup_cp":0}
                 for i,x in enumerate(["g1f3","f1c4","b1c3"])]}
    experiment={"id":1,"game_sha256":"a"*64,"original_move_uci":"e7e5",
                "candidates":[candidate]}
    return source,experiment


class P32CompareMethods(unittest.TestCase):
    def test_a_b_c_positive(self):
        a,b=sample()
        o=row_views(a,b)
        m=o["historical_response_metrics"]
        self.assertTrue(m["A_forced_pv_exact_next"])
        self.assertTrue(m["B_simple_plan_best_reply_exact"])
        self.assertEqual(m["C_top3_rank_of_actual_reply"],1)

    def test_actual_reply_outside_three_fail(self):
        a,b=sample()
        a["full_original_mainline_uci"][2]="d2d4"
        m=row_views(a,b)["historical_response_metrics"]
        self.assertIsNone(m["C_top3_rank_of_actual_reply"])
        self.assertFalse(m["C_top3_covers_actual_reply"])

    def test_16_are_required_and_matching(self):
        a,b=sample()
        with self.assertRaisesRegex(ValueError,"DENOMINATOR"):
            compare({"selected":[a]},{"source_sha256":SOURCE_SHA,"cases":[b]})

    def test_source_id_mismatch_rejected(self):
        a,b=sample()
        b["game_sha256"]="b"*64
        with self.assertRaisesRegex(ValueError,"SOURCE_IDENTITY"):
            row_views(a,b)

    def test_different_predictions_are_not_equal_metrics(self):
        a,b=sample()
        b["candidates"][0]["forced_root_pv_uci"]=["e7e5","f1c4"]
        m=row_views(a,b)["historical_response_metrics"]
        self.assertFalse(m["A_forced_pv_exact_next"])
        self.assertTrue(m["B_simple_plan_best_reply_exact"])

if __name__=="__main__":
    unittest.main()
