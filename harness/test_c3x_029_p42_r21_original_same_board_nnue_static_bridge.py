"""R21 D source-native evaluator transcript safety and non-causal boundaries."""
import unittest
from c3x_029_p42_r21_original_same_board_nnue_static_bridge import summarize

class RealStaticAdapter(unittest.TestCase):
    def test_same_board_static_values_preserved(self):
        original={"records":[{"case_id":10,"root":"e8f7","scope":"after_root",
          "reply":None,"raw_trace_sha256":"1"*64,
          "trace":{"status":"DIRECT_STATIC_TRACE_OK",
                   "classical_white_pawns":0.8,"nnue_white_pawns":-0.2,
                   "final_white_pawns":-0.1,
                   "raw_nnue_minus_classical_white_pawns":-1.0}}]}
        out=summarize(original)
        self.assertEqual(out["white_pawn_score_sign_differences"],1)
        self.assertEqual(out["independently_parsed_static_worlds"],1)
        self.assertFalse(out["actual_nnue_feature_attribution_proved"])
        self.assertFalse(out["root_search_selection_causally_explained"])
        self.assertNotIn("fen",str(out).lower())
    def test_check_is_excluded_not_zero_scored(self):
        out=summarize({"records":[{"case_id":10,"root":"e8f7","scope":"after_root",
                                  "trace":{"status":"IN_CHECK_EVAL_NOT_AVAILABLE"}}]})
        self.assertEqual(out["total_same_board_conditions"],1)
        self.assertEqual(out["independently_parsed_static_worlds"],0)
        self.assertEqual(out["white_pawn_score_sign_differences"],0)
    def test_missing_trace_is_honestly_counted(self):
        out=summarize({"records":[{"case_id":10,"root":"e8f7","scope":"after_root",
                                  "trace":{"status":"HOLD_EVAL_TRACE_MISSING"}}]})
        self.assertEqual(out["trace_status_counts"]["HOLD_EVAL_TRACE_MISSING"],1)
        self.assertFalse(out["independent_chess_truth_proved"])
    def test_no_pgn_or_raw_log_in_published_record(self):
        row={"case_id":14,"root":"c2c3","scope":"after_root","reply":None,
             "raw_trace_sha256":"a"*64,
             "raw_source_eval_trace":"PRIVATE_BOARD_AND_PLAYERS",
             "fen":"SECRET_FEN",
             "trace":{"status":"DIRECT_STATIC_TRACE_OK",
                      "classical_white_pawns":0.0,
                      "nnue_white_pawns":0.1,"final_white_pawns":0.05,
                      "raw_nnue_minus_classical_white_pawns":0.1}}
        result=summarize({"records":[row]})
        self.assertNotIn("SECRET_FEN",str(result))
        self.assertNotIn("PRIVATE_BOARD",str(result))
    def test_positive_same_sign_has_no_false_reversal(self):
        r={"case_id":14,"root":"c2c3","scope":"after_root","reply":None,
            "raw_trace_sha256":"b"*64,
            "trace":{"status":"DIRECT_STATIC_TRACE_OK","classical_white_pawns":0.25,
                     "nnue_white_pawns":0.65,"final_white_pawns":0.4,
                     "raw_nnue_minus_classical_white_pawns":0.4}}
        self.assertEqual(summarize({"records":[r]})["white_pawn_score_sign_differences"],0)
if __name__=="__main__":
    unittest.main()
