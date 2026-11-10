"""C3X 0.30/R4 ACT-Eval-inspired deterministic claim routing regression.

No original ACT-Eval free-text or 325-position benchmark is claimed.
"""
import unittest
import chess

from c3x_030_r4_acteval_symbolic_claim_verifier import evaluate_atom, demonstration


class AtomicChessFactContracts(unittest.TestCase):
    def setUp(self):
        self.b=chess.Board()

    def test_legal_root_move_true_and_false_foil(self):
        for expected,truth in ((True,True),(False,False)):
            r=evaluate_atom(self.b,{"kind":"legal_move","move_uci":"e2e4","expected":expected})
            self.assertEqual(r["atom_factually_correct"],truth)
    
    def test_illegal_move_may_be_reported_false(self):
        r=evaluate_atom(self.b,{"kind":"legal_move","move_uci":"e2e5","expected":False})
        self.assertTrue(r["atom_factually_correct"])

    def test_illegal_tactical_claim_is_not_assigned_false_silently(self):
        with self.assertRaisesRegex(ValueError,"NONLEGAL_MOVE"):
            evaluate_atom(self.b,{"kind":"move_is_capture","move_uci":"e2e5","expected":False})

    def test_factual_piece_and_empty_square(self):
        self.assertTrue(evaluate_atom(self.b,{"kind":"piece_on_square","square":"e1","expected":"K"})["atom_factually_correct"])
        self.assertTrue(evaluate_atom(self.b,{"kind":"piece_on_square","square":"e4","expected":None})["atom_factually_correct"])
        self.assertFalse(evaluate_atom(self.b,{"kind":"piece_on_square","square":"e1","expected":"k"})["atom_factually_correct"])

    def test_attack_owner_and_square(self):
        self.assertTrue(evaluate_atom(self.b,{"kind":"square_attacked_by","square":"e3","color":"white","expected":True})["atom_factually_correct"])
        self.assertTrue(evaluate_atom(self.b,{"kind":"square_attacked_by","square":"e3","color":"black","expected":False})["atom_factually_correct"])

    def test_white_material_balance(self):
        self.assertTrue(evaluate_atom(self.b,{"kind":"white_material_minus_black","expected":0})["atom_factually_correct"])
        self.b.remove_piece_at(chess.D8)
        self.assertTrue(evaluate_atom(self.b,{"kind":"white_material_minus_black","expected":9})["atom_factually_correct"])

    def test_true_check_and_capture_from_legal_sequence(self):
        b=chess.Board()
        for m in ("f2f3","e7e5","g2g4"):
            b.push_uci(m)
        self.assertTrue(evaluate_atom(b,{"kind":"move_gives_check","move_uci":"d8h4","expected":True})["atom_factually_correct"])
        b=chess.Board()
        for m in ("e2e4","d7d5"):
            b.push_uci(m)
        self.assertTrue(evaluate_atom(b,{"kind":"move_is_capture","move_uci":"e4d5","expected":True})["atom_factually_correct"])

    def test_reject_invalid_claim_category_and_extra_fields(self):
        with self.assertRaisesRegex(ValueError,"ATOM_SCHEMA"):
            evaluate_atom(self.b,{"kind":"best_strategy","expected":True})
        with self.assertRaisesRegex(ValueError,"MOVE_ATOM_FIELDS"):
            evaluate_atom(self.b,{"kind":"legal_move","move_uci":"e2e4","expected":True,"hint":"leak"})

    def test_reject_invalid_uci_and_square(self):
        with self.assertRaisesRegex(ValueError,"INVALID_UCI"):
            evaluate_atom(self.b,{"kind":"legal_move","move_uci":"????????","expected":False})
        with self.assertRaisesRegex(ValueError,"INVALID_PIECE_SQUARE"):
            evaluate_atom(self.b,{"kind":"piece_on_square","square":"z9","expected":None})

    def test_real_history_demo_requires_two_real_roots(self):
        z={"case_id":"fixture","event_family":"fixture"}
        with self.assertRaisesRegex(ValueError,"TWO_ORIGINAL_ROOTS"):
            demonstration([(z,self.b,[{"root":"e2e4"}])])

    def test_real_history_demo_24_atoms_with_false_controls(self):
        cases=[]
        for i in (1,2):
            cases.append(({"case_id":f"synthetic:{i}","event_family":f"synthetic:{i}"},
                          chess.Board(),[{"root":"e2e4"},{"root":"d2d4"}]))
        r=demonstration(cases)
        self.assertEqual(r["n_tool_checked_atoms"],24)
        self.assertEqual(r["true_source_derived_claims"],12)
        self.assertEqual(r["intentionally_false_foils"],12)
        self.assertTrue(r["no_llm_commentary_or_original_gold_dataset"])


if __name__=="__main__":
    unittest.main()
