import io
import unittest
import chess
import chess.pgn
from c3x_029_p36_r1_july_engine_blind_freeze import (
    candidate_from_game, FROZEN_PLY, sha
)

# A known legal 70-ply source-history fixture; TEST ONLY, not a July source candidate.
UCI = """c2c4 c7c5 g1f3 g8f6 b1c3 b8c6 e2e3 e7e6 d2d4 d7d5
c4d5 e6d5 f1b5 a7a6 b5c6 b7c6 e1g1 f8d6 d4c5 d6c5
c3a4 c5d6 d1c2 d8c7 h2h3 e8g8 b2b3 f6e4 c1b2 c8f5
c2e2 f8c8 a1c1 c7b7 f1d1 a8b8 f3h4 f5e6 h4f3 e6f5
b2e5 d6a3 e5b8 a3c1 d1c1 c8b8 f3d4 f5d7 f2f3 e4g3
e2d3 b7a8 g1f2 g3h5 d3c3 g8h8 c3a5 a8a7 a4c5 d7e8
g2g4 h5f6 a5a6 b8a8 a6a7 a8a7 c5a4 c6c5 c1c5 e8a4""".split()


def test_game():
    game = chess.pgn.Game()
    for key, val in {"Event":"fixture", "Date":"2026.07.03", "White":"W",
                     "Black":"B", "Result":"1-0"}.items():
        game.headers[key] = val
    board = game.board()
    node = game
    for u in UCI:
        m=chess.Move.from_uci(u)
        assert m in board.legal_moves, u
        node=node.add_variation(m)
        board.push(m)
    return game


class FreezeSelectionContract(unittest.TestCase):
    def test_full_history_identity_and_fixed_ply(self):
        row, reason=candidate_from_game(test_game(), 17)
        self.assertEqual(reason,"ELIGIBLE")
        self.assertEqual(row["pgn_index"],17)
        self.assertEqual(row["fixed_ply"],FROZEN_PLY)
        self.assertEqual(row["total_plies"],len(UCI))
        self.assertEqual(row["full_game_uci"],UCI)
        self.assertEqual(row["full_game_uci_sha256"],sha(" ".join(UCI).encode()))
    def test_reproducible_identity(self):
        a,_=candidate_from_game(test_game(), 1)
        b,_=candidate_from_game(test_game(), 2)
        self.assertEqual(a["selection_sha256"],b["selection_sha256"])
        self.assertNotEqual(a["pgn_index"],b["pgn_index"])
    def test_reject_setup_not_original_start(self):
        g=test_game()
        g.headers["SetUp"]="1"
        r, reason=candidate_from_game(g, 1)
        self.assertIsNone(r)
        self.assertEqual(reason, "NONINITIAL_SETUP")
    def test_reject_game_without_result(self):
        g=test_game()
        g.headers["Result"]="*"
        self.assertEqual(candidate_from_game(g,1)[1],"UNFINISHED_RESULT")
    def test_short_mainline_hold(self):
        g=test_game()
        node=g
        for _ in range(15): node=node.variation(0)
        node.variations.clear()
        self.assertEqual(candidate_from_game(g,1)[1],"TOO_SHORT")

if __name__=="__main__":
    unittest.main()
