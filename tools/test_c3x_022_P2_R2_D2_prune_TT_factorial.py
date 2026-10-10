#!/usr/bin/env python3
"""D2 operator toggle site restrictions, first eligible only, rights bounded."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_022_P2_R2_native_SEE_source_witness_overlay import patch as strict,ANCHORS
from c3x_022_P2_R2_D1_rootcall_only_SEE_observer import patch as readonly
from c3x_022_P2_R2_D2_descendant_first_prune_toggle import patch as d2
class D2FirstQuietOnly(unittest.TestCase):
    def test_three_layer_CXX_overlay_and_singleton_pruning(self):
        src=strict("namespace Stockfish {\n"+'\n'.join(a for a,b in ANCHORS)+"\n")
        src=readonly(src)
        src=d2(src)
        self.assertIn('D2_prune_site=std::strcmp(site,"quiet_prune")==0',src)
        self.assertIn('std::strcmp(site,"qsearch_prune")==0',src)
        self.assertIn('++c3x022_r2_D2_eligible_prune_seen==1',src)
        self.assertIn('kind=forced',src)
        with self.assertRaises(ValueError): d2(src)
    def test_ancestry_first_toggle_must_be_explicit(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_018_native_TT_lineage_factorial_6_8.py").read_text()
        self.assertIn('descendant_prune_flip',s)
        self.assertIn('C3X022_R2_SEE_DESCENDANT_FIRST_PRUNE',s)
        self.assertIn('see_watch["policy"]=="FLIP"',s)
    def test_actual_contact_not_noop_assertion(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_022_P2_R2_D2_first_prune_SEE_TT_factorial.py").read_text()
        self.assertIn('R2_D2_SEE_WRONG_PRUNING_SITE',s)
        self.assertIn('SEE_first_Boolean_intervention_count',s)
        self.assertIn('POST_D1_DEVELOPMENT_DESCENDANT_PRUNE_NOT_HELDOUT',s)
if __name__=="__main__":unittest.main()
