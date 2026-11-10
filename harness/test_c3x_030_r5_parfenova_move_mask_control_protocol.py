"""R5 Parfenova-inspired leakage protocol tests: purely synthetic text only."""
import unittest

import chess

from c3x_030_r5_parfenova_move_mask_control_protocol import (
    mask_explicit_hints, packet, demonstrate, MOVE_HINT, CONTROL_NAMES)


class ExplicitMoveLeakageContracts(unittest.TestCase):
    def test_explicit_uci_san_coordinates_and_castling_removed(self):
        src = "14. Nf3 improves e2-e4 and e2 to e4; e2e4, O-O, 0-0-0, e8=Q."
        masked = mask_explicit_hints(src)
        self.assertNotIn("e2e4", masked)
        self.assertNotIn("Nf3", masked)
        self.assertNotIn("O-O",masked)
        self.assertNotIn("0-0-0",masked)
        self.assertFalse(MOVE_HINT.search(masked))

    def test_normal_strategy_terms_not_removed(self):
        text = "This continuation improves coordination and restricts opponent replies."
        self.assertEqual(mask_explicit_hints(text),text)

    def test_empty_commentary_rejected(self):
        with self.assertRaisesRegex(ValueError,"EMPTY"):
            mask_explicit_hints("   ")

    def test_legal_source_move_and_five_conditions(self):
        x=packet(chess.Board(),"e2e4","Unrelated plan e7e5 is plausible.")
        self.assertEqual(tuple(x["conditions"]),CONTROL_NAMES)
        self.assertTrue(x["explicit_uci_present_before_mask"])
        self.assertTrue(x["explicit_uci_absent_after_mask"])
        self.assertTrue(x["explicit_san_absent_after_mask"])
        self.assertIsNone(x["conditions"]["fen_only"]["explanation"])
        self.assertIsNone(x["conditions"]["explanation_only"]["fen"])
        self.assertEqual(x["conditions"]["fen_only"]["fen"],chess.Board().fen())
        self.assertIsNotNone(x["conditions"]["fen_plus_unrelated_foil"]["explanation"])

    def test_invalid_chess_action_rejected(self):
        with self.assertRaisesRegex(ValueError,"CANDIDATE_NOT_LEGAL"):
            packet(chess.Board(),"e2e5","An unrelated comment.")

    def test_malformed_uci_rejected(self):
        with self.assertRaisesRegex(ValueError,"BAD_CANDIDATE"):
            packet(chess.Board(),"nonsense","A generic comment.")

    def test_checking_candidate_is_ACT_eval_grounded(self):
        b=chess.Board()
        for u in ("f2f3","e7e5","g2g4"):
            b.push_uci(u)
        x=packet(b,"d8h4","Opponent plans d2d4.")
        self.assertTrue(x["act_eval_check_truth"])
        self.assertTrue(x["explicit_san_absent_after_mask"])

    def test_capturing_candidate_is_ACT_eval_grounded(self):
        b=chess.Board()
        for u in ("e2e4","d7d5"):
            b.push_uci(u)
        x=packet(b,"e4d5","A different line a2a4.")
        self.assertTrue(x["act_eval_capture_truth"])
        self.assertTrue(x["explicit_uci_absent_after_mask"])

    def test_five_conditions_on_two_old_worlds(self):
        worlds=[]
        for k in range(2):
            worlds.append(({"case_id":f"mock:{k}","event_family":f"mock:{k}"},
                           chess.Board(),[{"root":"e2e4"},{"root":"d2d4"}]))
        result=demonstrate(worlds)
        self.assertEqual(result["n_condition_packets"],20)
        self.assertEqual(result["n_candidate_moves"],4)
        self.assertTrue(result["no_decoder_or_token_probability_model_called"])
        self.assertTrue(result["strict_mask_is_regex_approximation_not_original_maximal_semantic_mask"])

    def test_foils_must_be_distinct_worlds(self):
        b=chess.Board()
        with self.assertRaisesRegex(ValueError,"TWO_EXPOSED_GAMES"):
            demonstrate([({"case_id":"mock","event_family":"mock"},b,
                          [{"root":"e2e4"},{"root":"d2d4"}])])

    def test_null_unrelated_foil_is_allowed_for_single_template(self):
        result=packet(chess.Board(),"d2d4")
        self.assertIsNone(result["conditions"]["fen_plus_unrelated_foil"]["explanation"])


if __name__=="__main__":
    unittest.main()
