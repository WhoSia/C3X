"""C3X P2 deterministic chess concept comparison contracts, no synthetic engine scores."""
import unittest
import chess

from c3x_concept_contrast import (
    own_passed_pawns,pawn_islands,material_balance_cp,
    attacked_enemy_nonking,unprotected_attacked_own_nonking,
    king_ring_enemy_attacked_squares,concept_facts_after,contrast,
    markdown_append,SCHEMA
)


class ConceptFacts(unittest.TestCase):
    def test_initial_board_symmetry_and_pawn_islands(self):
        b=chess.Board()
        self.assertEqual(material_balance_cp(b,chess.WHITE),0)
        self.assertEqual(material_balance_cp(b,chess.BLACK),0)
        self.assertEqual(pawn_islands(b,chess.WHITE),1)
        self.assertEqual(pawn_islands(b,chess.BLACK),1)
        self.assertEqual(own_passed_pawns(b,chess.WHITE),[])
        self.assertEqual(own_passed_pawns(b,chess.BLACK),[])

    def test_true_passed_white_pawn(self):
        b=chess.Board("4k3/8/8/4P3/8/8/8/4K3 w - - 0 1")
        self.assertEqual(own_passed_pawns(b,chess.WHITE),["e5"])

    def test_enemy_adjacent_pawn_ahead_blocks_passed_pawn(self):
        b=chess.Board("4k3/8/3p4/4P3/8/8/8/4K3 w - - 0 1")
        self.assertEqual(own_passed_pawns(b,chess.WHITE),[])

    def test_original_full_board_concepts_exist(self):
        b=chess.Board()
        d=concept_facts_after(b,chess.Move.from_uci("e2e4"))
        self.assertEqual(d["own_pawn_island_count"],1)
        self.assertEqual(d["own_material_advantage_simple_piece_values_cp"],0)
        self.assertGreater(d["opponent_legal_response_count_after_move"],0)
        self.assertIsInstance(d["own_king_adjacent_squares_attacked_by_enemy"],list)

    def test_contrastive_suppress_shared_material_and_pawn_islands(self):
        b=chess.Board()
        result=contrast(b,"e2e4","d2d4")
        self.assertEqual(result["schema"],SCHEMA)
        self.assertIn("own_material_advantage_simple_piece_values_cp",
                      result["concept_dimensions_shared_suppressed"])
        self.assertTrue(result["no_automatic_engine_score_attribution"])
        self.assertNotIn("source_original_fen",str(result["concept_dimensions_different"]))

    def test_king_zone_is_squares_not_asserted_engine_score(self):
        b=chess.Board()
        self.assertIsInstance(king_ring_enemy_attacked_squares(b,chess.WHITE),list)

    def test_reject_illegal_actions(self):
        with self.assertRaisesRegex(ValueError,"TWO_DISTINCT"):
            contrast(chess.Board(),"e2e5","d2d4")

    def test_reject_same_action(self):
        with self.assertRaisesRegex(ValueError,"TWO_DISTINCT"):
            contrast(chess.Board(),"e2e4","e2e4")

    def test_markdown_explicit_epistemic_scope(self):
        result=contrast(chess.Board(),"e2e4","d2d4")
        md=markdown_append(result)
        self.assertIn("핀 된 기물",md)
        self.assertIn("인과",md)
        self.assertIn("Google Drive",md)
        self.assertIn("## 5.",md)

    def test_attack_graph_does_not_fabricate_nonexistent_targets(self):
        b=chess.Board()
        self.assertEqual(attacked_enemy_nonking(b,chess.WHITE),[])
        self.assertEqual(unprotected_attacked_own_nonking(b,chess.WHITE),[])


if __name__=="__main__":
    unittest.main()
