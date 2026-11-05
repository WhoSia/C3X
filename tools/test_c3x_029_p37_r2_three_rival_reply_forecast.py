import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
import chess

from c3x_029_p37_r2_three_rival_reply_forecast import (
    material, predict_json_reply, predict_c3x_plan_reply,
    next_reply_pv, signed_margin, reconstruct,
)


class ForecastLawTests(unittest.TestCase):
    def test_material_perspective_and_capture(self):
        b=chess.Board()
        self.assertEqual(material(b,chess.WHITE),0)
        self.assertEqual(material(b,chess.BLACK),0)
        b.remove_piece_at(chess.A7)
        self.assertEqual(material(b,chess.WHITE),100)
        self.assertEqual(material(b,chess.BLACK),-100)

    def test_legal_conditional_forecasters_do_not_mutate_board(self):
        b=chess.Board()
        b.push_uci("e2e4")
        fen=b.fen()
        a=predict_json_reply(b,chess.WHITE)
        c=predict_c3x_plan_reply(b,chess.WHITE)
        self.assertEqual(b.fen(),fen)
        self.assertIn(chess.Move.from_uci(a["reply"]),b.legal_moves)
        self.assertIn(chess.Move.from_uci(c["reply"]),b.legal_moves)
        self.assertEqual(a["legal_opponent_replies_considered"],c["legal_opponent_replies_considered"])
        self.assertGreater(c["own_continuations_enumerated"],0)

    def test_pv_reply_requires_root_identity_and_legality(self):
        b=chess.Board()
        root=chess.Move.from_uci("e2e4")
        self.assertEqual(next_reply_pv(b,root,[root,chess.Move.from_uci("c7c5")]),"c7c5")
        self.assertIsNone(next_reply_pv(b,root,[chess.Move.from_uci("d2d4")]))

    def test_negative_multipv_rank_is_not_sorted_away(self):
        x=signed_margin([{"root_side_cp":-25},{"root_side_cp":13}])
        self.assertEqual(x["signed_cp"],-38)
        self.assertEqual(x["stratum"],"rank_unresolved")

    def test_near_boundary_and_mate(self):
        self.assertEqual(signed_margin([{"root_side_cp":12},{"root_side_cp":-7}])["stratum"],"near")
        self.assertEqual(signed_margin([{"root_side_cp":12},{"root_side_cp":-8}])["stratum"],"intermediate")
        self.assertEqual(signed_margin([{"root_side_cp":None},{"root_side_cp":0}])["stratum"],"mate_or_unscored")

    def test_illegal_prefix_rejected(self):
        d={"fixed_ply":30,"original_prefix_uci":["a1a8"]*30,"frozen_fen":chess.STARTING_FEN}
        with self.assertRaisesRegex(ValueError,"ILLEGAL_PREFIX"):
            reconstruct(d)


if __name__ == "__main__":
    unittest.main()
