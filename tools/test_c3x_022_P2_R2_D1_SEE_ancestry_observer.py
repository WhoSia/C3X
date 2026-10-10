#!/usr/bin/env python3
"""D1 read-only descendant site census and no broadened-scope mutation."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_022_P2_R2_native_SEE_source_witness_overlay import patch as strict
from c3x_022_P2_R2_D1_rootcall_only_SEE_observer import patch as widen
from c3x_022_P2_R2_native_SEE_source_witness_overlay import ANCHORS
class AncestorReadOnly(unittest.TestCase):
    def test_ancestry_scope_works_only_for_observation(self):
        s=strict("namespace Stockfish {\n"+'\n'.join(a for a,b in ANCHORS)+"\n")
        t=widen(s)
        self.assertIn("observe_descendant",t)
        self.assertIn("!observe_descendant && policy",t)
        self.assertIn("c3x018_root_context_call!=call",t)
        with self.assertRaises(ValueError):
            widen(t)
    def test_no_widened_FLIP_in_harness(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_018_native_TT_lineage_factorial_6_8.py").read_text()
        self.assertIn('see_watch["policy"]=="OBS"',s)
        self.assertIn('C3X022_R2_SEE_PASSIVE_ANCESTRY',s)
    def test_zero_intervention_diagnostic(self):
        p=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_022_P2_R2_D1_passive_root_descendant_SEE_census.py").read_text()
        self.assertIn("D1_READ_ONLY_SEE_OPERATOR_MUTATED",p)
        self.assertIn('"SEE_return_value_interventions":0',p)
        self.assertIn('"TT_interventions":0',p)
if __name__=="__main__":unittest.main()
