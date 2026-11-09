"""Blind official future broadcast source freezer contract tests.

These deliberately use synthetic PGN only; source not yet downloaded, official
round not yet played. Source precommit must not be called a heldout PASS.
"""
import io,unittest
import chess,chess.pgn
from c3x_029_p42_r24_future_broadcast_blind_cohort_freeze import (
 harvest,FROZEN_ROUND,FIXED_PLY
)
def make(moves=("e2e4","e7e5","g1f3","b8c6"),result="1-0"):
    game=chess.pgn.Game()
    game.headers["Result"]=result
    node=game
    for u in moves:node=node.add_variation(chess.Move.from_uci(u))
    return str(game)+"\n\n"
class R24ProspectiveSourcePolicy(unittest.TestCase):
    def test_real_url_frozen_not_reselected(self):
        self.assertEqual(FROZEN_ROUND,"https://lichess.org/broadcast/lag-dm-2026/round-3/sbfCtgNj")
        self.assertEqual(FIXED_PLY,30)
    def test_synthetic_complete_sample_selects_by_hash_without_evals(self):
        text=make()
        _,out=harvest(text.encode(),minimum=4,target=1)
        self.assertEqual(out["selected_game_count"],1)
        self.assertFalse(out["reference_judge_seen"])
        self.assertTrue(out["not_a_prospective_validation_result"])
        self.assertFalse(out["excluded_prior_source_archive_complete_audit"])
    def test_insufficient_complete_games_holds(self):
        _,out=harvest(make().encode(),minimum=4,target=8)
        self.assertTrue(out["status"].startswith("HOLD_"))
    def test_unfinished_result_rejected(self):
        _,out=harvest(make(result="*").encode(),minimum=4,target=1)
        self.assertEqual(out["census"]["incomplete_result"],1)
    def test_duplicate_mainline_rejected(self):
        _,out=harvest((make()+make()).encode(),minimum=4,target=1)
        self.assertEqual(out["census"]["duplicate_full_uci"],1)
    def test_zip_masquerading_as_pgn_rejected(self):
        with self.assertRaisesRegex(ValueError,"RAW_PGN_REQUIRED"):
            harvest(b"PK"+b"0"*100,minimum=4,target=1)
    def test_incomplete_source_placeholder_rejected(self):
        with self.assertRaisesRegex(ValueError,"RAW_PGN_REQUIRED"):
            harvest(b"file not available",minimum=4,target=1)
    def test_future_source_has_no_own_engine_labels(self):
        p,z=harvest(make().encode(),minimum=4,target=1)
        self.assertNotIn("score",str(z).lower())
        self.assertNotIn("selected_source_positions",z)
        self.assertIn("selected_source_positions",p)
    def test_bad_game_syntax_rejected_by_chess_parser(self):
        bad='[Event "Fake"]\n[Result "1-0"]\n\n1. e4 e5 2. Qh5 Qh4 1-0\n\n'
        _,out=harvest(bad.encode(),minimum=4,target=1)
        self.assertEqual(out["census"]["syntax_illegal"],1)
    def test_eligible_source_selection_does_not_require_prior_referee(self):
        _,out=harvest(make().encode(),minimum=4,target=1)
        self.assertFalse(out["model_scores_known_at_source_freeze"])
        self.assertFalse(out["source_engine_candidates_selected"])
if __name__=="__main__":unittest.main()
