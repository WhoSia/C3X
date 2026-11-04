import unittest
from unittest.mock import patch
import c3x_029_p35_r5_source_dispatch_probe as p

class SourceProbeTest(unittest.TestCase):
    def test_git_blob_calculation(self):
        self.assertEqual(p.git_blob_sha1(b"test content\n"),
                         "d670460b4b4aece5915caf5c68d12f560a9fe3e4")

    def test_invalid_original_rejected(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_BLOB_SHA"):
            p.apply_patch(b"wrong stockfish source")

    def test_instrument_only_actual_evaluate(self):
        original=(b"#include <cstdlib>\n\nValue Eval::evaluate(const Position& pos) {"
                  b"\n  bool useClassical = !useNNUE || abs(psq) > 2048;"
                  b"\n  return v;\n}\n/// trace() is like evaluate()\n")
        with patch.object(p,"SOURCE_BLOB_SHA1",p.git_blob_sha1(original)):
            transformed=p.apply_patch(original).decode()
        self.assertIn("std::fprintf(stderr",transformed)
        self.assertEqual(transformed.count("C3X_P35_ROUTE key="),1)
        self.assertIn("return v;",transformed)

    def test_route_boundary(self):
        rows=p.parse_route_log("C3X_P35_ROUTE key=17 arm=NNUE psq=2048 value=8\n"
                               "C3X_P35_ROUTE key=18 arm=HCE psq=-2049 value=-10\n")
        self.assertEqual([r["arm"] for r in rows],["NNUE","HCE"])

    def test_wrong_routing_rejected(self):
        with self.assertRaisesRegex(ValueError,"CONTRADICTS_SOURCE"):
            p.parse_route_log("C3X_P35_ROUTE key=17 arm=HCE psq=2048 value=0\n")

    def test_malformed_log_rejected(self):
        with self.assertRaisesRegex(ValueError,"MALFORMED"):
            p.parse_route_log("C3X_P35_ROUTE invalid event\n")

    def test_other_stderr_ignored(self):
        self.assertEqual(p.parse_route_log("Stockfish 16 ready\n"),[])

if __name__=="__main__":
    unittest.main()
