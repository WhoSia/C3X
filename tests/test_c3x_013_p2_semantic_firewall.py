"""Adversarial source-bound claims for C3X 0.13 P2. No human participants."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import c3x_013_p2_semantic_firewall as firewall

CERT=json.loads((ROOT/"c3x"/"certificates"/"g95-p16-local-minimal-full-bridge.json").read_text())

class SemanticFireWallTest(unittest.TestCase):
    def setUp(self):
        self.report=firewall.produce(copy.deepcopy(CERT))
        self.king=self.report["worlds"]["B0"][2]
    def test_all_negative_controls(self):
        self.assertTrue(all(self.report["negative_control_results"].values()))
    def test_friendly_king_coverage_not_hostile(self):
        self.assertEqual(self.king["square"],"e8")
        self.assertEqual(self.king["predicate"],"OWN_OCCUPIED_COVERAGE")
    def test_target_removed_coverage(self):
        self.assertEqual(self.report["worlds"]["TARGET"][2]["predicate"],"NO_ATTACK_MAP_CONTACT")
    def test_observable_board_fact_is_allowed(self):
        self.assertTrue(firewall.admit_claim(
            {"claim_kind":"BOARD_FACT","predicate":"OWN_OCCUPIED_COVERAGE"},
            self.king)["admitted"])
    def test_fake_board_fact_fails(self):
        with self.assertRaisesRegex(ValueError,"BOARD_FACT_MISMATCH"):
            firewall.admit_claim(
                {"claim_kind":"BOARD_FACT","predicate":"ENEMY_OCCUPIED_CONTACT"},
                self.king)
    def test_hostile_pressure_label_fails(self):
        with self.assertRaisesRegex(ValueError,"UNLICENSED_SEMANTIC_OR_CAUSAL_PROMOTION"):
            firewall.admit_claim({"claim_kind":"HOSTILE_PRESSURE"},self.king)
    def test_other_unsupported_claims_fail(self):
        for kind in ("STRATEGIC_CONCEPT","CAUSAL_MECHANISM",
                     "CROSS_ENGINE_TRANSPORT","HUMAN_LEARNING_BENEFIT"):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(ValueError,"UNLICENSED_SEMANTIC_OR_CAUSAL_PROMOTION"):
                    firewall.admit_claim({"claim_kind":kind},self.king)
    def test_sham_subset_independence_illusion_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATED_SAME_FEN_NOT_INDEPENDENT"):
            firewall.admit_claim({"claim_kind":"INDEPENDENT_REPLICATION"},self.king,1)
    def test_historical_concept_label_unassigned(self):
        self.assertIsNone(CERT["concept_label"])
        self.assertFalse(self.report["concept_label_authorized"])
    def test_mutated_archived_attack_vector_rejected(self):
        x=copy.deepcopy(CERT)
        x["chain"]["sham_edit"]["relation_after"][2]=False
        with self.assertRaisesRegex(ValueError,"ARCHIVE_VECTOR_NOT_REPRODUCED_SHAM"):
            firewall.produce(x)

if __name__=="__main__":
    unittest.main()
