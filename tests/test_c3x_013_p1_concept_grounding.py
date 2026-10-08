"""C3X 0.13 P1 archival calibration and adversarial concept-wording controls."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/"harness"/"c3x_013_p1_concept_grounding.py"
spec=importlib.util.spec_from_file_location("c3x013_concept",source)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cert=json.loads((ROOT/"c3x"/"certificates"/"g95-p16-local-minimal-full-bridge.json").read_text())

class ConceptGroundingTest(unittest.TestCase):
    def test_archival_relations(self):
        out=module.evaluate(copy.deepcopy(cert))
        self.assertTrue(out["all_archived_attack_vectors_reproduced"])
        self.assertTrue(out["all_three_legal"])
    def test_own_king_is_not_hostile_pressure(self):
        out=module.evaluate(copy.deepcopy(cert))
        fact=out["attack_relation_results"]["B0"][2]
        self.assertEqual((fact["square"],fact["occupancy"],fact["attacked"]),
                         ("e8","OWN_OCCUPIED",True))
        self.assertEqual(out["semantic_counterexample"]["verdict"],"FALSIFIED")
    def test_no_unsupported_science_promotion(self):
        out=module.evaluate(copy.deepcopy(cert))
        self.assertFalse(out["named_chess_concept_certified"])
        self.assertFalse(out["causal_mechanism_certified"])
        self.assertFalse(out["human_understanding_improved"])
        self.assertFalse(out["cross_engine_transport_certified"])
    def test_sham_and_subset_share_exact_world(self):
        out=module.evaluate(copy.deepcopy(cert))
        self.assertTrue(out["sham_is_exact_subset_world"])
    def test_forged_target_relation_rejected(self):
        x=copy.deepcopy(cert)
        x["chain"]["target_edit"]["relation_after"][2]=True
        with self.assertRaisesRegex(ValueError,"ARCHIVE_VECTOR_NOT_REPRODUCED_TARGET"):
            module.evaluate(x)
    def test_swapped_target_and_sham_rejected(self):
        x=copy.deepcopy(cert)
        x["counterfactual_boards"]["TARGET"],x["counterfactual_boards"]["SHAM"]=(
            x["counterfactual_boards"]["SHAM"],x["counterfactual_boards"]["TARGET"])
        with self.assertRaisesRegex(ValueError,"SHAM_SUBSET_NOT_IDENTICAL"):
            module.evaluate(x)
    def test_wrong_historical_stage_rejected(self):
        x=copy.deepcopy(cert)
        x["scientific_stage"]="C3X 0.13"
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_HISTORICAL_SOURCE"):
            module.evaluate(x)
    def test_missing_queen_rejected(self):
        import chess
        x=copy.deepcopy(cert)
        b=chess.Board(x["counterfactual_boards"]["B0"]["fen"])
        b.remove_piece_at(chess.D8)
        x["counterfactual_boards"]["B0"]["fen"]=b.fen()
        with self.assertRaisesRegex(ValueError,"INVALID_BOARD_B0|PIECE_IDENTITY_MISMATCH"):
            module.evaluate(x)

if __name__=="__main__":
    unittest.main()
