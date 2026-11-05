"""P37 source-only selection contracts; synthetic chess histories, no engine."""
import json
import unittest
from pathlib import Path

import chess
import chess.pgn
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3x_029_p37_r1_oct_eight_event_source_freeze import (
    SOURCES, sha256, parse_game, freeze_round, freeze, PLY
)

# Deterministic 70-ply legal PGN fixture from prior C3X source-parser test.
UCI = """c2c4 c7c5 g1f3 g8f6 b1c3 b8c6 e2e3 e7e6 d2d4 d7d5
c4d5 e6d5 f1b5 a7a6 b5c6 b7c6 e1g1 f8d6 d4c5 d6c5
c3a4 c5d6 d1c2 d8c7 h2h3 e8g8 b2b3 f6e4 c1b2 c8f5
c2e2 f8c8 a1c1 c7b7 f1d1 a8b8 f3h4 f5e6 h4f3 e6f5
b2e5 d6a3 e5b8 a3c1 d1c1 c8b8 f3d4 f5d7 f2f3 e4g3
e2d3 b7a8 g1f2 g3h5 d3c3 g8h8 c3a5 a8a7 a4c5 d7e8
g2g4 h5f6 a5a6 b8a8 a6a7 a8a7 c5a4 c6c5 c1c5 e8a4""".split()

def game_for(source_id, date="2026.10.30", result="1-0"):
    g = chess.pgn.Game()
    for k, v in {"Event":source_id, "Date":date, "White":"W",
                 "Black":"B", "Result":result, "Site":"fixture.invalid"}.items():
        g.headers[k] = v
    b=g.board()
    node=g
    for u in UCI:
        m=chess.Move.from_uci(u)
        assert m in b.legal_moves, u
        node=node.add_variation(m)
        b.push(m)
    return g

class P37SourcePreOutcomeTests(unittest.TestCase):
    def test_eight_independent_source_labels_and_rounds(self):
        self.assertEqual(len(SOURCES),8)
        self.assertEqual(len({x[0] for x in SOURCES}),8)
        self.assertEqual(len({x[1] for x in SOURCES}),8)

    def test_deterministic_full_history_and_fen(self):
        g=game_for("one")
        a,status=parse_game(g,"one",10)
        b,status_b=parse_game(g,"one",20)
        self.assertEqual(status,status_b)
        self.assertEqual(status,"ELIGIBLE")
        self.assertEqual(a["selection_sha256"],b["selection_sha256"])
        self.assertEqual(a["fixed_ply"],30)
        self.assertEqual(a["full_game_uci_sha256"],sha256(" ".join(UCI).encode()))
        board=chess.Board()
        for move in UCI[:PLY]:
            board.push_uci(move)
        self.assertEqual(a["frozen_fen"],board.fen(en_passant="fen"))

    def test_out_of_window_or_invalid_result_hold(self):
        self.assertEqual(parse_game(game_for("x",date="2026.08.01"),"x",1)[1],"WRONG_DATE")
        self.assertEqual(parse_game(game_for("x",result="*"),"x",1)[1],"MISSING_HEADER")

    def test_html_does_not_become_pgn(self):
        with self.assertRaisesRegex(ValueError,"NON_PGN"):
            freeze_round("evt","example","event","2026-10-30",b"<html>page not a PGN</html>")

    def test_single_event_freeze_preserves_identifiers(self):
        g=game_for("one")
        res=freeze_round("evt","abc","event","2026-10-30",
                         (str(g)+"\n").encode("utf-8"))
        self.assertEqual(res["selected"]["total_plies"],len(UCI))
        self.assertEqual(res["eligible_games"],1)
        self.assertFalse(res["upstream_sha256_published"])

    def test_no_posthoc_source_replacement(self):
        self.assertEqual([x[1] for x in SOURCES],
                         ["MR4eFoUH","tZQNFMoC","ZvY3jr6Q","LVWRdrsl",
                          "lEQStSIp","TGKbOvjn","3veI3mSx","GcyAs4TL"])

if __name__ == "__main__":
    unittest.main()
