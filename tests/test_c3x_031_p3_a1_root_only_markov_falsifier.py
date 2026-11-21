"""P3-A1 original-root-only Markov-state counterexample and negative checks.

Original source: P2-D1 156 log files, 78 native searches, P2-028-0.
Mutations are NOT chess outcomes and the rooted model explicitly omits nodes.
"""
import os
from pathlib import Path
import tempfile
import unittest
import zipfile

from c3x_031_p3_a1_root_only_markov_falsifier import audit, lines_for, public_projection, sha

LOG = Path(os.environ.get("C3X_P3_A0_NATIVE_ZIP",
                          "/tmp/c3x-p3-a0/native-original.zip"))
SCIENCE = Path(os.environ.get("C3X_P3_A0_SCIENCE_ZIP",
                              "/tmp/c3x-p3-a0/science-original.zip"))


class RootOnlyFalsifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = audit(LOG, SCIENCE)
        with zipfile.ZipFile(LOG) as z:
            cls.stderr = z.read("P2-028-0/depth-16/untouched-0/stderr.txt")
            cls.stdout = z.read("P2-028-0/depth-16/untouched-0/stdout.txt")

    def test_original_exact_same_full_root_candidate_ledger(self):
        for depth in ("15","16"):
            cell=self.data["depth_cells"][depth]
            self.assertEqual(cell["root_ledger_full_candidate_count"], 45)
            self.assertTrue(cell["same_root_candidate_projection"])
            self.assertTrue(cell["same_depth13_public_score_pv_projection"])

    def test_original_same_root_projection_across_fixed_depths(self):
        a,b=self.data["depth_cells"]["15"],self.data["depth_cells"]["16"]
        self.assertEqual(a["root_projection_sha256"],b["root_projection_sha256"])
        self.assertEqual(a["public_projection_sha256"],b["public_projection_sha256"])

    def test_original_node_count_is_an_explicitly_excluded_feature(self):
        a=self.data["depth_cells"]["16"]
        self.assertEqual(a["nodes_at_end16"],[7699,7717])
        self.assertIn("cumulative node/time/nps",self.data["projection_excludes"])
        self.assertFalse("node count" in self.data["projection_includes"])

    def test_identical_snapshot_does_not_predict_next_iterative_choice(self):
        for d in ("15","16"):
            a=self.data["depth_cells"][d]
            self.assertEqual(a["future_root_bestmoves"],["d4e5","f4e5"])
            self.assertEqual(a["first_future_candidate_value_drift_attempt"],17)
            self.assertEqual(a["first_future_leader_update_drift_attempt"],18)
        self.assertEqual(self.data["scope_of_falsification"],
                         "ROOT_CANDIDATE_LEDGER_ONLY_NOT_SUFFICIENT")

    def test_limit_not_a_full_engine_state_causality_proof(self):
        self.assertTrue(self.data["full_engine_state_sufficiency_not_falsified"])
        self.assertTrue(self.data["source_TT_history_node_mediator_not_identified"])
        self.assertTrue(self.data["original_R26_macro_family_exposure"])
        self.assertEqual(self.data["native_searches_new_this_unit"],0)

    def test_exact_source_candidate_45_original_records_included(self):
        row=lines_for(self.stderr)
        self.assertEqual(row["candidate_count"],45)
        self.assertEqual(len(row["projection_lines"]),47)
        self.assertTrue(any("move=f4e5" in line
                            for line in row["projection_lines"]))

    def test_source_public_projection_includes_score_pv_but_not_nodes(self):
        view=public_projection(self.stdout)
        self.assertIn("score cp 746",view)
        self.assertIn("pv d4e5",view)
        self.assertNotIn(" nodes ",view)
        self.assertNotIn(" nps ",view)
        self.assertNotIn(" time ",view)

    def test_injection_of_source_candidate_changes_projection(self):
        clean=lines_for(self.stderr)["projection_lines"]
        changed=self.stderr.replace(b"move=f4e5 value=", b"move=f4e5 value=900000",1)
        # Altering even one candidate makes its exact normalized ledger distinct.
        bad=lines_for(changed)["projection_lines"]
        self.assertNotEqual(clean,bad)

    def test_missing_root_candidate_fails_closed(self):
        parts=self.stderr.splitlines(keepends=True)
        parts=[x for x in parts if b"C3X_R23_CANDIDATE attempt=16" not in x or
               b"move=g7h7" not in x]
        with self.assertRaisesRegex(ValueError,"root boundary incomplete"):
            lines_for(b"".join(parts))

    def test_missing_public_depth13_fails_closed(self):
        lines=[r for r in self.stdout.splitlines(keepends=True)
               if not r.startswith(b"info depth 13 ")]
        with self.assertRaisesRegex(ValueError,"public output incomplete"):
            public_projection(b"".join(lines))

    def test_original_zip_byte_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            damaged=Path(tmp)/"bad_source.zip"
            damaged.write_bytes(LOG.read_bytes()+b"corrupted")
            with self.assertRaisesRegex(ValueError,"ZIP SHA"):
                audit(damaged,SCIENCE)


if __name__ == "__main__":
    unittest.main()
