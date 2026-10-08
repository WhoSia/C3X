"""P8-EP4 chess-law source-lock tests for TCEC heldout pawn genesis confluence."""
import unittest
import chess
from harness.c3x_013_p7r1_tactical_support import hazard
from harness.c3x_013_p6r1_birth_rival_support import births

TCEC_FEN="r5k1/6p1/p5qn/4p2p/2ppP3/3Q3P/1P1B1PP1/R5K1 w - - 0 25"
EXPECTED_COMMON="r5k1/6p1/p5qn/4p2p/3pP3/1p1Q3P/3B1PP1/R5K1 w - - 0 26"
def cases():
    root=chess.Board(TCEC_FEN)
    d={}
    for label,uci in (("single","b2b3"),("double","b2b4")):
        move=chess.Move.from_uci(uci)
        assert root.is_valid() and move in root.legal_moves
        b=root.copy(stack=False);b.push(move)
        rep=chess.Move.from_uci("c4b3")
        assert rep in b.legal_moves
        typ=b.is_en_passant(rep)
        b.push(rep)
        d[label]=(typ,b)
    return root,d

class HeldoutTCECConfluence(unittest.TestCase):
    def test_exact_original_source_fen_and_legality(self):
        root,_=cases()
        self.assertTrue(root.is_valid())
        self.assertEqual(root.fullmove_number,25)
        self.assertEqual(root.turn,chess.WHITE)
    def test_normal_vs_en_passant_shared_legal_black_response(self):
        _,d=cases()
        self.assertEqual(d["single"][0],False)
        self.assertEqual(d["double"][0],True)
    def test_exact_full_fen_confluence_including_turn_clocks_and_rights(self):
        _,d=cases()
        self.assertEqual(d["single"][1].fen(en_passant="fen"),EXPECTED_COMMON)
        self.assertEqual(d["double"][1].fen(en_passant="fen"),EXPECTED_COMMON)
    def test_black_c4_pawn_newly_passes_only_on_double(self):
        root,_=cases()
        single=births(root,chess.Move.from_uci("b2b3"))
        double=births(root,chess.Move.from_uci("b2b4"))
        self.assertEqual(single,[])
        self.assertTrue(any(x["color"]=="black" and x["pawn_after"]=="c4" for x in double))
    def test_corrected_immediate_legal_capture_hazards_match(self):
        root,_=cases()
        h1=hazard(root,chess.Move.from_uci("b2b3"))
        h2=hazard(root,chess.Move.from_uci("b2b4"))
        self.assertEqual(h1,h2)
        self.assertIn("pawn",h1["recapture_types"])
    def test_repeated_pawn_root_one_step_two_step_same_origin(self):
        a,b=chess.Move.from_uci("b2b3"),chess.Move.from_uci("b2b4")
        self.assertEqual(a.from_square,b.from_square)
        self.assertNotEqual(a.to_square,b.to_square)
if __name__=="__main__":
    unittest.main()
