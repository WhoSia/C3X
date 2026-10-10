#!/usr/bin/env python3
"""Strict SEE operator witness regression against pinned SF16 static callsite code."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_022_P2_R2_native_SEE_source_witness_overlay import patch,ANCHORS
class SEEFourSites(unittest.TestCase):
    def test_all_four_native_SEE_sites_replaced_exactly_once(self):
        minimal="namespace Stockfish {\n"+'\n'.join(x for x,y in ANCHORS)+"\n"
        p=patch(minimal)
        for a,b in ANCHORS:
            self.assertNotIn(a,p)
            self.assertEqual(p.count(b),1)
        self.assertIn('c3x022_r2_see_matches',p)
    def test_no_unrecognised_source_replacement(self):
        with self.assertRaises(ValueError):
            patch("namespace Stockfish {\nif (!pos.see_ge(x))")
        with self.assertRaises(ValueError):
            patch(patch("namespace Stockfish {\n"+'\n'.join(x for x,y in ANCHORS)))
    def test_first_contact_operator_only(self):
        p=Path(__file__).resolve().parents[1]/"tools"/"c3x_022_P2_R2_native_SEE_source_witness_overlay.py"
        s=p.read_text()
        self.assertIn("requested_flip && n==1",s)
        self.assertIn("pos.see_ge(move",s)
        self.assertIn("c3x018_root_context_call!=call",s)
        self.assertIn("uint64_t(pos.key())!=target",s)
        self.assertIn('" site=" << site',s)
        self.assertEqual(len(ANCHORS),4)
    def test_native_play_default_not_flipped(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/"c3x_018_native_TT_lineage_factorial_6_8.py").read_text()
        self.assertIn("see_watch=None",s)
        self.assertIn('"native_see_events":native_see_events',s)
        self.assertIn('"OBS","FLIP"',s)
if __name__=="__main__":unittest.main()
