"""P36/R3 synthetic contract tests; no real engine score or March output used."""
import sys
import unittest
from pathlib import Path

import chess
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))
from c3x_029_p36_r3_march8_native_multipv2 import (
    validate_case, stratum, FROZEN_PLY
)

UCI_30 = """c2c4 c7c5 g1f3 g8f6 b1c3 b8c6 e2e3 e7e6 d2d4 d7d5
c4d5 e6d5 f1b5 a7a6 b5c6 b7c6 e1g1 f8d6 d4c5 d6c5
c3a4 c5d6 d1c2 d8c7 h2h3 e8g8 b2b3 f6e4 c1b2 c8f5""".split()


def example():
    b=chess.Board()
    for move in UCI_30:
        b.push_uci(move)
    return {"fixed_ply":FROZEN_PLY,"full_game_uci":UCI_30,
            "fixed_board_fen":b.fen()}


class NativeScreenContractTest(unittest.TestCase):
    def test_frozen_board_reconstructed_from_full_history(self):
        case=example()
        self.assertEqual(validate_case(case).fen(),case["fixed_board_fen"])

    def test_wrong_fen_refused(self):
        case=example()
        case["fixed_board_fen"]=chess.STARTING_FEN
        with self.assertRaisesRegex(ValueError,"FROZEN_FEN_MISMATCH"):
            validate_case(case)

    def test_wrong_ply_refused(self):
        case=example()
        case["fixed_ply"]=29
        with self.assertRaisesRegex(ValueError,"PLY_MISMATCH"):
            validate_case(case)

    def test_margin_strata_boundaries(self):
        self.assertEqual([stratum(n) for n in (0,19,20,99,100,None)],
                         ["near","near","intermediate","intermediate","wide","mate_or_unscored"])

    def test_negative_margin_refused(self):
        with self.assertRaisesRegex(ValueError,"NEGATIVE_MULTIPV_MARGIN"):
            stratum(-1)


if __name__ == "__main__":
    unittest.main()
