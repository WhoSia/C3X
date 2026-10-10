#!/usr/bin/env python3
"""P2-R2 targeted genuine SEE x physical TT test design (not new prospective claims)."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_R2_TWIC1664_native_SEE_operator_factorial import CASES,STAGEA_SHA,SCHEMA,run
class SiteFactorialGuards(unittest.TestCase):
    def test_known_R1_changed_game_sample_explicitly_development(self):
        self.assertEqual(CASES,((2,"O","STRICT"),(3,"F","STRICT"),(6,"O","STRICT"),
                                 (12,"O","STRICT"),(13,"F","STRICT"),(14,"O","STRICT")))
    def test_frozen_stagea_sha(self):
        self.assertEqual(STAGEA_SHA,"a84a9a2b38bacedb140724c08fc5137b98c8f0077d4754bb5f399a3c30284c35")
    def test_unreported_new_source_cannot_run(self):
        with self.assertRaises((KeyError,AssertionError)):
            run({"selected":[]},{"cases":[]},None)
    def test_actual_singleton_AND_exact_contact_not_environment_only(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/"c3x_022_P2_R2_TWIC1664_native_SEE_operator_factorial.py").read_text()
        self.assertIn('"SEE_first_Boolean_intervention_count"',s)
        self.assertIn("if not tt_flag:",s)
        self.assertIn('"physical_reader_block"',s)
        self.assertIn('"native_SEE_witness_events"',s)
        self.assertIn("EXPLORATORY_DEVELOPMENT_NOT_HELDOUT",s)
if __name__=="__main__":unittest.main()
