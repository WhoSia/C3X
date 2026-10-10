#!/usr/bin/env python3
"""Test fail-closed source-only C3X 0.24 P0 selector and rights semantics."""
import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_024_P0_aug2025_engineblind_source16 import (
    URL,CHARTER,SCAN_MAX,FIRST_ELIGIBLE,PICK,SCHEMA,game_digest,
    selected_ply,fens_in_material,historic_sources)

class BeforeEngineSourceCase(unittest.TestCase):
    def test_exact_month_and_limits_are_frozen(self):
        self.assertEqual(URL,"https://database.lichess.org/broadcast/lichess_db_broadcast_2025-08.pgn.zst")
        self.assertTrue(CHARTER.endswith("20261011.md"))
        self.assertEqual((SCAN_MAX,FIRST_ELIGIBLE,PICK),(20000,512,16))
        self.assertIn("before-any-native-treatment",SCHEMA)

    def test_hash_and_ply_are_deterministic(self):
        game={"Event":"source-only-test"}
        self.assertEqual(game_digest(game,["e2e4","e7e5"]),
                         game_digest(dict(game),["e2e4","e7e5"]))
        h=game_digest(game,["e2e4","e7e5"])
        self.assertGreaterEqual(selected_ply(h),30)
        self.assertLessEqual(selected_ply(h),44)
        with self.assertRaises(ValueError):selected_ply("foo")

    def test_history_only_literal_valid_fen4(self):
        x={"selected":[{"fen4":"8/8/8/8/8/8/8/K6k w - -",
                        "full_original_mainline_uci":["e2e4"]}],
           "per_ecology":{"may":{"selected":[{"fen4":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"}]}},
           "other":{"fen4":"not a fen"}}
        self.assertEqual(len(fens_in_material(x)),2)

    def test_no_silent_coverage_downgrade(self):
        with self.assertRaises(ValueError):
            historic_sources(["p0=/nonexistent.json"])
        with self.assertRaises(ValueError):
            historic_sources([])

    def test_no_twic_full_raw_or_bot_authored_workflow(self):
        code=(Path(__file__).resolve().parents[1]/"harness"/
              "c3x_024_P0_aug2025_engineblind_source16.py").read_text()
        self.assertNotIn("Stockfish",code.split("def produce")[0])
        self.assertIn('"TT_FIRST_interventions":0',code)
        self.assertIn('"SEE_forced_interventions":0',code)
        self.assertIn('"treatment_outcomes_seen":False',code)
        self.assertIn('"source_halfmove_clock":board.halfmove_clock',code)
        self.assertNotIn('"source_headers":',code)
        self.assertNotIn('"full_original_mainline_uci":',code)

if __name__=="__main__":unittest.main()
