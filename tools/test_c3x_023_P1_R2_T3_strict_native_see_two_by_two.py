#!/usr/bin/env python3
"""Source integrity regression: never flip wrong SEE site or wildcard fallback."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_R2_native_SEE_source_witness_overlay import patch as p0,ANCHORS
from c3x_023_P1_native_SEE_parent_path_key_overlay import patch as p1,MAIN,QS
from c3x_023_P1_R2_T1_native_full_search_state_overlay import patch as t1
from c3x_023_P1_R2_T3_precise_native_SEE_boolean_source_actuator import patch as t3
from c3x_023_P1_R2_T3_strict_SEE_TT_two_by_two_source_court import prereg,ELIGIBLE

class StrictSourceActuator(unittest.TestCase):
    def test_original_Stockfish16_layers_scope_tuple_and_singleton(self):
        src='#include <algorithm>\nnamespace Stockfish {\n'+'\n'.join(a for a,b in ANCHORS)+'\n'+MAIN+'\n'+QS
        after=t3(t1(p1(p0(src))))
        for t in ('c3x023_t3_scope_hits','t3int("t1_alpha"',
                  't3int("t1_beta"','t3int("t1_rule50"',
                  't3u64("parent_key64"','t3u64("key64"',
                  't3int("original_SEE_Boolean"','t3site_allowed'):
            self.assertIn(t,after)
        self.assertIn('t3num==1',after)
        self.assertIn('std::strcmp(site,"quiet_prune")==0',after)
        self.assertIn('std::strcmp(site,"qsearch_prune")==0',after)
        self.assertIn('int(applied || t3altered)',after)
        with self.assertRaises(ValueError):t3(after)
    def test_script_must_prove_both_shams_first(self):
        code=(Path(__file__).resolve().parents[1]/"harness"/
              "c3x_023_P1_R2_T3_strict_SEE_TT_two_by_two_source_court.py").read_text()
        self.assertLess(code.index('base=cold('),code.index('see=cold('))
        self.assertLess(code.index('first=cold('),code.index('joint=cold('))
        self.assertIn("T3_SHAM_EXACT_SOURCE_OBSERVER_CHANGED_ORIGINAL_UCI",code)
        self.assertIn("T3_EXACT_TARGET_BECAME_INELIGIBLE",code)
        self.assertIn("T3_TARGET_SOURCE_LITERAL_MISMATCH",code)
        self.assertEqual(ELIGIBLE,((11,"F","STRICT"),(2,"O","STRICT")))
    def test_no_unsealed_manifest_accepted(self):
        with self.assertRaises((RuntimeError,KeyError,AssertionError)):
            prereg({}, {}, {"freeze_status":"NOT_COMMITTED"}, {})
if __name__=="__main__":unittest.main()
