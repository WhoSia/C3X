#!/usr/bin/env python3
"""No July2025 archive/Stockfish: frozen M4 decision rule legal exact-UCI checks."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_024_P4_M4_preFIRST_survivor_corroboration_rule import m4_survivor_corroboration as rule
LEGAL={"d6c5","d6c7","e2e4","d2d4","g1f3","c2c4"}
def ask(depth=None,**kw):
    opts={"role":"STRICT","eligible":True,"source_reader_native":12,
          "baseline_native":12,"baseline_UCI":"e2e4","opposite_UCI":"d2d4",
          "depth8to11":{8:"e2e4",9:"e2e4",10:"e2e4",11:"e2e4"},
          "legal_uci":LEGAL}
    if depth is not None:opts["depth8to11"]=depth
    opts.update(kw)
    return rule(**opts)
class M4PreFirstSurvivor(unittest.TestCase):
    def test_exposed_sept107_opposite_only_false_positive_vetoed(self):
        r=ask(role="STRICT",baseline_UCI="d6c5",opposite_UCI="d6c7",
              depth8to11={8:"d6c5",9:"d6c5",10:"d6c5",11:"d6c5"})
        self.assertEqual((r["M4"],r["predict_flip"]),("d6c5",False))
    def test_cross_order_alternative_seen_earlier_and_at_depth11(self):
        self.assertEqual(ask(depth={8:"d2d4",9:"e2e4",10:"e2e4",11:"d2d4"})["M4"],"d2d4")
    def test_same_order_depth11_with_two_earlier_leaders(self):
        self.assertEqual(ask(depth={8:"g1f3",9:"g1f3",10:"e2e4",11:"g1f3"},
                             opposite_UCI="e2e4")["M4"],"g1f3")
    def test_single_historical_depth_witness_not_enough(self):
        self.assertFalse(ask(depth={8:"g1f3",9:"e2e4",10:"e2e4",11:"g1f3"},
                             opposite_UCI="e2e4")["predict_flip"])
    def test_wrong_reader_target_keeps_original(self):
        self.assertEqual(ask(depth={8:"d2d4",9:"d2d4",10:"d2d4",11:"d2d4"},
                             source_reader_native=66)["M4"],"e2e4")
    def test_broad_never_overrides(self):
        self.assertFalse(ask(role="BROAD",depth={8:"d2d4",9:"d2d4",10:"d2d4",11:"d2d4"})["predict_flip"])
    def test_censored_ladder_null(self):
        self.assertEqual(ask(depth={8:"d2d4",9:None,10:"d2d4",11:"d2d4"})["reason"],"DEPTH_SOURCE_CENSORED_OR_ILLEGAL")
    def test_ineligible_never_guesses(self):
        self.assertIsNone(ask(eligible=False)["M4"])
    def test_illegal_current_root_is_error(self):
        with self.assertRaises(ValueError):ask(baseline_UCI="a1a9")
if __name__=="__main__":unittest.main()
