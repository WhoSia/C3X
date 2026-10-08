"""P8-EP3: previously proved exact normal/en-passant confluence remains detectable."""
import unittest
import chess
from harness.c3x_013_p8ep3_heldout_confluence_census import proof, candidates

NZ="1r1qk2r/4bppp/QN1pp1b1/2P5/1p2n1P1/4B2P/PPPN1P2/R3K2R w KQk - 1 17"
class HeldOutConfluenceDetector(unittest.TestCase):
    def test_known_nz_witness_detected(self):
        board=chess.Board(NZ)
        found=proof(board)
        candidates0=[x for x in found["witnesses"] if x["single"]=="a2a3" and x["double"]=="a2a4"]
        self.assertEqual(len(candidates0),1)
        witness=candidates0[0]
        self.assertEqual(witness["reply_after_single"]["reply"],"b4a3")
        self.assertEqual(witness["reply_after_double"]["reply"],"b4a3")
        self.assertTrue(witness["same_opponent_reply_uci"])
        self.assertTrue(witness["normal_vs_en_passant"])
        self.assertTrue(witness["root_capture_hazard_equal"])
        self.assertTrue(witness["passed_birth_toggled"])
        self.assertIn("1r1qk2r/4bppp/",witness["exact_common_full_fen"])
    def test_starting_position_has_no_one_vs_two_pawn_same_root_overlap(self):
        board=chess.Board()
        result=proof(board)
        self.assertEqual(result["exact_legal_reply_confluence_count"],0)
    def test_root_pair_catalogue_unmodified(self):
        board=chess.Board(NZ)
        self.assertTrue(any(a.uci()=="a2a3" and b.uci()=="a2a4"
                            for a,b in candidates(board)))
if __name__=="__main__":
    unittest.main()
