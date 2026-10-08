"""P8-EP2 exact legal Chess continuation confluence under normal vs en passant."""
import unittest
import chess
from harness.c3x_013_p7r1_tactical_support import hazard
from harness.c3x_013_p6r1_birth_rival_support import births
from c3x_explain.concepts import snapshot

SOURCE="1r1qk2r/4bppp/QN1pp1b1/2P5/1p2n1P1/4B2P/PPPN1P2/R3K2R w KQk - 1 17"

def branches():
    root=chess.Board(SOURCE)
    assert root.is_valid()
    worlds={}
    for name,uci in (("A","a2a3"),("B","a2a4")):
        b=root.copy(stack=False)
        m=chess.Move.from_uci(uci)
        assert m in b.legal_moves
        b.push(m)
        r=chess.Move.from_uci("b4a3")
        assert r in b.legal_moves
        pre=b.copy(stack=False)
        b.push(r)
        worlds[name]={"post_root":pre,"post_reply":b}
    return root,worlds

class NZLegalConfluence(unittest.TestCase):
    def test_both_roots_legal_same_original_pawn(self):
        root,_=branches()
        m1,m2=chess.Move.from_uci("a2a3"),chess.Move.from_uci("a2a4")
        self.assertIn(m1,root.legal_moves)
        self.assertIn(m2,root.legal_moves)
        self.assertEqual(m1.from_square,m2.from_square)
        self.assertEqual(root.piece_at(m1.from_square),chess.Piece(chess.PAWN,chess.WHITE))
    def test_same_legal_uci_recap_is_normal_or_en_passant(self):
        _,p=branches()
        r=chess.Move.from_uci("b4a3")
        self.assertFalse(p["A"]["post_root"].is_en_passant(r))
        self.assertTrue(p["A"]["post_root"].is_capture(r))
        self.assertTrue(p["B"]["post_root"].is_en_passant(r))
        self.assertTrue(p["B"]["post_root"].is_capture(r))
    def test_exact_full_FEN_converges_after_black_capture(self):
        _,p=branches()
        self.assertEqual(p["A"]["post_reply"].fen(en_passant="fen"),
                         p["B"]["post_reply"].fen(en_passant="fen"))
        self.assertTrue(p["A"]["post_reply"].is_valid())
        self.assertTrue(p["B"]["post_reply"].is_valid())
    def test_typed_born_not_born_before_replies(self):
        root,p=branches()
        a,b=[chess.Move.from_uci(x) for x in ("a2a3","a2a4")]
        self.assertEqual(births(root,a),[])
        self.assertTrue(any(e["color"]=="white" and e["pawn_after"]=="a4"
                            for e in births(root,b)))
        white_a=snapshot(p["A"]["post_root"],chess.WHITE)
        white_b=snapshot(p["B"]["post_root"],chess.WHITE)
        self.assertEqual(white_b["own_passed_pawn_count"]-white_a["own_passed_pawn_count"],1)
    def test_corrected_pawn_capture_hazard_matches(self):
        root,_=branches()
        a=hazard(root,chess.Move.from_uci("a2a3"))
        b=hazard(root,chess.Move.from_uci("a2a4"))
        self.assertEqual(a["recapture_types"],["pawn"])
        self.assertEqual(b["recapture_types"],["pawn"])
        self.assertEqual(a,b)
    def test_all_source_board_facts_equal_after_common_reply(self):
        _,p=branches()
        for side in (chess.WHITE,chess.BLACK):
            self.assertEqual(snapshot(p["A"]["post_reply"],side),
                             snapshot(p["B"]["post_reply"],side))
if __name__=="__main__":
    unittest.main()
