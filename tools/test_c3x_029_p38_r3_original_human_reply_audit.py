"""P38/R3 adversarial unit tests for observed-human-reply admission."""
import hashlib
import sys
import unittest
from pathlib import Path
import chess

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_029_p38_r3_original_human_reply_audit import inspect_observed_case, sha

KNIGHT_CYCLE = ["g1f3","g8f6","f3g1","f6g8"]


def source_fixture(root_is_observed=True):
    moves = KNIGHT_CYCLE * 15
    board = chess.Board()
    for u in moves[:30]:
        board.push_uci(u)
    frozen = board.fen(en_passant="fen")
    identity = sha(" ".join(moves).encode("ascii"))
    key = "case-smoke-1234"
    roots = ["f3g1", "e2e4"] if root_is_observed else ["e2e4","d2d4"]
    observed_reply = moves[31]
    pair = []
    for i, r in enumerate(roots):
        pair.append({"root_uci": r, "predictions":{
            "stockfish_pv": {"reply": observed_reply if i==0 else "a7a6"},
            "simple_json": {"reply": "e7e5"},
            "c3x_legal_plan": {"reply": observed_reply if i==0 else "a7a6"},
        }})
    prediction = {
        "case_id":key,"source_id":"synthetic-event",
        "event_family":"synthetic-law-test","fixed_ply":30,
        "original_game_sha256":identity,
        "original_prefix_uci":moves[:30],"frozen_fen":frozen,
        "candidate_pairs":pair,
    }
    game = {
        "case_id":key,"source_id":"synthetic-event","fixed_ply":30,
        "full_game_uci_sha256":identity,"full_game_uci":moves,
        "frozen_fen":frozen,
    }
    prefix={k:prediction[k] for k in
            ("case_id","source_id","fixed_ply","original_game_sha256",
             "original_prefix_uci","frozen_fen")}
    return prediction,game,prefix


class ActualHumanOutcomeAuditorTest(unittest.TestCase):
    def test_observed_root_and_reply_are_legal(self):
        row=inspect_observed_case(*source_fixture(True))
        self.assertEqual(row["status"],"OBSERVED_OWN_CANDIDATE")
        self.assertEqual(row["historical_opponent_reply_uci"],"f6g8")
        self.assertTrue(row["hits"]["stockfish_pv"])
        self.assertFalse(row["hits"]["simple_json"])
        self.assertTrue(row["hits"]["c3x_legal_plan"])

    def test_unplayed_foils_never_get_hallucinated_human_labels(self):
        row=inspect_observed_case(*source_fixture(False))
        self.assertEqual(row["status"],"NO_ACTUAL_COUNTERFACTUAL_FOR_FROZEN_CANDIDATES")
        self.assertEqual(row["predictions"],{})
        self.assertEqual(row["hits"],{})

    def test_forecaster_prefix_drift_fatal(self):
        p,g,pre=source_fixture()
        p["original_prefix_uci"][-1]="a7a6"
        with self.assertRaisesRegex(ValueError,"FORECAST_PREFIX_LEAKAGE"):
            inspect_observed_case(p,g,pre)

    def test_historical_illegal_opponent_reply_fatal(self):
        p,g,pre=source_fixture()
        g["full_game_uci"][31]="f6g1"
        digest=sha(" ".join(g["full_game_uci"]).encode("ascii"))
        g["full_game_uci_sha256"]=p["original_game_sha256"]=pre["original_game_sha256"]=digest
        with self.assertRaisesRegex(ValueError,"ACTUAL_OPPONENT_REPLY_ILLEGAL"):
            inspect_observed_case(p,g,pre)

if __name__=="__main__":
    unittest.main()
