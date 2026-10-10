#!/usr/bin/env python3
"""T1 exact Stockfish16 four-site call invariance and source state contract."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_023_P1_R2_T1_source_search_state_overlay import patch,SIG,LOG,SITES
class NativeSEEStateSource(unittest.TestCase):
    def test_four_source_calls_and_exact_state_are_each_once(self):
        baseline=SIG+"\n"+LOG+"\n"+"\n".join(x for x,_ in SITES)
        altered=patch(baseline)
        self.assertEqual(altered.count('state_ply='),1)
        self.assertEqual(altered.count('state_occupied64='),1)
        self.assertEqual(altered.count('state_alpha='),1)
        self.assertEqual(altered.count('state_beta='),1)
        for a,b in SITES:
            self.assertEqual(altered.count(b),1)
            self.assertNotIn(a,altered)
        with self.assertRaises(ValueError):patch(altered)
    def test_omitted_source_site_must_fail_closed(self):
        with self.assertRaises(ValueError):
            patch(SIG+"\n"+LOG+"\n"+"\n".join(x for x,_ in SITES[:3]))
    def test_no_chess_SEE_value_or_position_mutation(self):
        s=(Path(__file__).resolve().parents[1]/"tools"/
           "c3x_023_P1_R2_T1_source_search_state_overlay.py").read_text()
        self.assertIn('"read_only_native_SEE_operator":True',s)
        self.assertIn('"does_not_instrument_PV_or_cutnode_or_explicit_branch_decision":True',s)
if __name__=="__main__":unittest.main()
