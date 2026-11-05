import sys
import unittest
from pathlib import Path
import chess
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_029_p38_r1_ethereal_independent_referee import stable_label, extract_child_reply, authentic_cases

class P38EthicalCrossEngineCourt(unittest.TestCase):
    def test_stable_exact_reply(self):
        a=stable_label({"reply":"e7e5"},{"reply":"e7e5"})
        self.assertEqual(a["status"],"REFERENCE_STABLE")
        self.assertEqual(a["label"],"e7e5")

    def test_unstable_cannot_be_wrong_label(self):
        a=stable_label({"reply":"e7e5"},{"reply":"c7c5"})
        self.assertEqual(a["status"],"REFERENCE_UNSTABLE")
        self.assertIsNone(a["label"])

    def test_missing_reference_is_undefined(self):
        self.assertEqual(stable_label({"reply":None},{"reply":"e7e5"})["status"],
                         "REFERENCE_UNDEFINED")

    def test_reply_is_first_move_from_post_candidate_child(self):
        board=chess.Board()
        board.push_uci("e2e4")
        result=extract_child_reply(board,{"pv":[chess.Move.from_uci("e7e5"),
                                                    chess.Move.from_uci("g1f3")],
                                           "nodes":96012,"depth":10},96000)
        self.assertEqual((result["reply"],result["status"]),("e7e5","VALID_NATIVE_REF_REPLY"))

    def test_one_move_pv_is_genuine_opponent_reply(self):
        board=chess.Board()
        board.push_uci("e2e4")
        result=extract_child_reply(board,{"pv":[chess.Move.from_uci("e7e5")],
                                           "nodes":96010,"depth":9},96000)
        self.assertEqual(result["reply"],"e7e5")

    def test_actual_two_node_shallow_engine_is_fatal(self):
        board=chess.Board()
        board.push_uci("e2e4")
        with self.assertRaisesRegex(ValueError,"INSUFFICIENT_NATIVE_SEARCH_NODES"):
            extract_child_reply(board,{"pv":[chess.Move.from_uci("e7e5")],
                                             "nodes":2,"depth":1},96000)

    def test_invalid_opponent_reply_refused(self):
        board=chess.Board()
        board.push_uci("e2e4")
        with self.assertRaisesRegex(ValueError,"REF_PV_ILLEGAL"):
            extract_child_reply(board,{"pv":[chess.Move.from_uci("e2e3")],
                                             "nodes":96010,"depth":10},96000)

    def test_depth_one_even_with_enough_nodes_is_fatal(self):
        board=chess.Board()
        board.push_uci("e2e4")
        with self.assertRaisesRegex(ValueError,"SHALLOW_NATIVE_REFEREE_DEPTH"):
            extract_child_reply(board,{"pv":[chess.Move.from_uci("e7e5")],
                                             "nodes":96001,"depth":1},96000)

    def test_changed_manifest_identity_refused(self):
        with self.assertRaisesRegex(ValueError,"EIGHT_SOURCE_EVENTS"):
            authentic_cases({"status":"PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS",
                             "cases":[]},{"sources":[]})

if __name__=="__main__":
    unittest.main()
