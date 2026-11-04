import unittest
from c3x_029_p35_r3_evaluator_lineage_gate import (
    VersionGateError, parse_uci_banner, gate_classical_vs_nnue,
    compare_version_experiments,
)

SF16 = "id name Stockfish 16\noption name Use NNUE type check default true\nuciok\n"
SF161 = "id name Stockfish 16.1\noption name Threads type spin default 1 min 1 max 1024\nuciok\n"


class EvaluatorLineageGateTest(unittest.TestCase):
    def test_exact_stockfish16_toggle(self):
        self.assertTrue(parse_uci_banner(SF16).is_stockfish16)
        c = gate_classical_vs_nnue(SF16, requested_arm="classical")
        self.assertIn("value false", c["uci_command"])
        self.assertIn("SOURCE_SHA", c["status"])

    def test_16_1_rejected(self):
        self.assertFalse(parse_uci_banner(SF161).is_stockfish16)
        with self.assertRaisesRegex(VersionGateError, "NOT_STOCKFISH"):
            gate_classical_vs_nnue(SF161, requested_arm="classical")

    def test_no_toggle_rejected_even_with_override(self):
        with self.assertRaisesRegex(VersionGateError, "NO_USE_NNUE"):
            gate_classical_vs_nnue(SF161, requested_arm="classical",
                                   require_pinned_stockfish16=False)

    def test_ambiguous_or_missing_banner_rejected(self):
        for raw in ("", "id name Stockfish 16\n", "id name Stockfish 16\nid name X\nuciok\n"):
            with self.assertRaises(VersionGateError): parse_uci_banner(raw)

    def test_invalid_arm(self):
        with self.assertRaisesRegex(VersionGateError, "INVALID_ARM"):
            gate_classical_vs_nnue(SF16, requested_arm="superhuman")

    def test_version_difference_is_confounder(self):
        a = dict(source_sha256="src16", network_sha256="net16",
                 search_code_sha256="search16", engine_binary_sha256="bin16",
                 position_history_sha256="h", nodes_requested=24000,
                 threads=1, hash_mb=16, evaluator_arm="classical")
        b = dict(a, source_sha256="src161", search_code_sha256="search161",
                 engine_binary_sha256="bin161", evaluator_arm="nnue")
        x = compare_version_experiments([a, b])
        self.assertEqual(x["status"], "VERSION_OR_RUNTIME_CONFOUNDED")
        self.assertFalse(x["effect_identified"])
        self.assertIn("source_sha256", x["changed_fields"])

    def test_missing_provenance_is_hold(self):
        self.assertEqual(compare_version_experiments([{}, {}])["status"],
                         "HOLD_INCOMPLETE_PROVENANCE")

    def test_same_regime_not_caused(self):
        a = dict(source_sha256="s", network_sha256="n",
                 search_code_sha256="s", engine_binary_sha256="b",
                 position_history_sha256="h", nodes_requested=24000,
                 threads=1, hash_mb=16, evaluator_arm="classical")
        self.assertFalse(compare_version_experiments([a, dict(a, evaluator_arm="nnue")])["effect_identified"])
        self.assertEqual(compare_version_experiments([a, dict(a)])["status"], "SAME_EVALUATOR_ARM")


if __name__ == "__main__":
    unittest.main()
