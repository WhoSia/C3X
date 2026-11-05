import sys
import unittest
from pathlib import Path
import chess
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_029_p38_r1_ethereal_independent_referee import stable_label, extract_reply, authentic_cases

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

    def test_extract_reply_legal(self):
        board=chess.Board()
        result=extract_reply(board,"e2e4",{"pv":[chess.Move.from_uci("e2e4"),
                                                   chess.Move.from_uci("e7e5")],
                                              "nodes":96012,"depth":10})
        self.assertEqual((result["reply"],result["status"]),("e7e5","VALID_NATIVE_REF_REPLY"))

    def test_short_pv_not_automatically_wrong(self):
        board=chess.Board()
        result=extract_reply(board,"e2e4",{"pv":[chess.Move.from_uci("e2e4")]})
        self.assertEqual(result["status"],"UNDEFINED_NO_OPPONENT_REPLY")
        self.assertIsNone(result["reply"])

    def test_changed_root_refused(self):
        with self.assertRaisesRegex(ValueError,"ENGINE_CHANGED_ROOT"):
            extract_reply(chess.Board(),"e2e4",{"pv":[chess.Move.from_uci("d2d4")]})

    def test_illegal_second_reply_refused(self):
        with self.assertRaisesRegex(ValueError,"REF_PV_ILLEGAL"):
            extract_reply(chess.Board(),"e2e4",{"pv":[chess.Move.from_uci("e2e4"),
                                                         chess.Move.from_uci("e2e3")]})

    def test_changed_manifest_identity_refused(self):
        with self.assertRaisesRegex(ValueError,"EIGHT_SOURCE_EVENTS"):
            authentic_cases({"status":"PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS",
                             "cases":[]},{"sources":[]})

if __name__=="__main__":
    unittest.main()
