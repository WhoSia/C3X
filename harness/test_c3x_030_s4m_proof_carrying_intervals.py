import unittest
import chess
from dataclasses import replace
from c3x_030_s4m_proof_carrying_intervals import (
    SCHEMA, ProofInterval, backup, terminal, terminal_child,
    observational_engine_event, unknown,
)

def before_fools_mate():
    b=chess.Board()
    for move in ("f2f3","e7e5","g2g4"):b.push_uci(move)
    assert b.turn==chess.BLACK and b.is_valid()
    return b

class ProofCarryingContract(unittest.TestCase):
    def test_actual_fools_mate_terminal(self):
        b=before_fools_mate()
        mate=terminal_child(b,"d8h4")
        self.assertEqual((mate.lower,mate.upper),(-1,-1))
        self.assertTrue(mate.verified)
        self.assertIn("mate",mate.lower_tags[0])
    def test_single_winning_witness_proves_exact_win_without_all_branches(self):
        b=before_fools_mate()
        result=backup(b,{"d8h4":terminal_child(b,"d8h4")})
        self.assertEqual((result["interval"]["lower"],result["interval"]["upper"]),(1,1))
        self.assertFalse(result["complete_legal_branch_coverage"])
        self.assertTrue(result["unknown_legal_moves"])
        self.assertEqual(result["witness_moves"],["d8h4"])
        self.assertEqual(result["explanation_strength"],"EXACT_WDL_PROVED")
        self.assertFalse(result["stockfish_mediation_proven"])
    def test_missing_branches_do_not_falsely_prove_draw(self):
        b=chess.Board()
        r=backup(b,{})
        self.assertEqual((r["interval"]["lower"],r["interval"]["upper"]),(-1,1))
        self.assertEqual(len(r["unknown_legal_moves"]),20)
        self.assertEqual(r["explanation_strength"],"SOUND_BOUNDS_ONLY")
    def test_stalemate_exact_without_arbitrary_search_values(self):
        b=chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        self.assertTrue(b.is_stalemate())
        r=backup(b,{})
        self.assertEqual((r["interval"]["lower"],r["interval"]["upper"]),(0,0))
        self.assertEqual(r["legal_move_count"],0)
    def test_forged_user_flag_rejected(self):
        b=before_fools_mate()
        real=terminal_child(b,"d8h4")
        forged=replace(real,lower=0,upper=0)
        with self.assertRaisesRegex(ValueError,"FORGED_TERMINAL"):
            backup(b,{"d8h4":forged})
    def test_proof_cannot_be_claimed_from_native_score(self):
        self.assertEqual(observational_engine_event(
            {"source_kind":"native_root_score","value":1000}),unknown())
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_SOURCE"):
            ProofInterval(1,1,certificate="native_root_score",verified=False)
    def test_nonmate_child_claim_rejected_even_with_false_certified_terminal(self):
        b=chess.Board()
        fake=ProofInterval(1,1,("terminal",),("terminal",),"legal_terminal",True)
        with self.assertRaisesRegex(ValueError,"NOT_A_CERTIFIABLE_TERMINAL"):
            backup(b,{"e2e4":fake})
    def test_illegal_child_rejected(self):
        with self.assertRaisesRegex(ValueError,"FORGED_OR_ILLEGAL"):
            backup(chess.Board(),{"e2e5":unknown()})
    def test_broken_board_rejected(self):
        b=chess.Board("8/8/8/8/8/8/8/8 w - - 0 1")
        with self.assertRaisesRegex(ValueError,"INVALID_BOARD"):backup(b,{})
    def test_unknown_event_kind_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_ENGINE"):
            observational_engine_event({"source_kind":"fake_explanation"})
    def test_terminal_not_accepted_as_nonterminal_branch(self):
        b=before_fools_mate();b.push_uci("d8h4")
        with self.assertRaisesRegex(ValueError,"TERMINAL_WITH_CHILDREN"):
            backup(b,{"g2g3":terminal(b)})
    def test_valid_interval_bounds_only(self):
        with self.assertRaisesRegex(ValueError,"BAD_WDL"):
            ProofInterval(2,2)
    def test_source_schema_frozen(self):
        self.assertEqual(SCHEMA,"c3x030-s4m-proof-carrying-interval-v1")

if __name__=="__main__":unittest.main()
