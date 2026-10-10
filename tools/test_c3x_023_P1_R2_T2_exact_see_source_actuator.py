#!/usr/bin/env python3
"""T2 never switches target to a different chess search node after source divergence."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_023_P1_R2_T2_exact_native_SEE_single_operator_actuator import (
    patch,ANCHOR,END)
from c3x_023_P1_R2_T2_exact_SEE_site_factorial_development import (
    select,T1_SHA,FIELDS,SELECTED)
class SourceExactT2(unittest.TestCase):
    def event(self,site):
        return {"source_key":{"key64":88,"parent_key64":77,"root_call":3,
                "root_move":2,"move":192,"site":site,"threshold":-95},
                "state":{"path_exact":"4d,58","source_ply":1,"source_depth":3,
                 "source_alpha":-10,"source_beta":20,"source_pv":0,
                 "source_rule50":8,"source_occupancy64":123},
                "SEE_original_boolean":0}
    def test_source_first_two_excludes_capture_without_fallback(self):
        source={"SEE_native_search_state_comparison":{
            "status":"POST_TT_COMPUTATIONAL_SEE_INPUT_WINDOW_MATCH",
            "first_two_full_computational_match_candidates":[self.event("capture_prune"),
                                                               self.event("quiet_prune")]}}
        x=select(source)
        self.assertEqual(x["status"],"T1_FIRST_TWO_SOURCE_SEE_ELIGIBLE")
        self.assertEqual(x["target"]["site"],"quiet_prune")
        source["SEE_native_search_state_comparison"]["first_two_full_computational_match_candidates"]=[
          self.event("capture_prune"),self.event("capture_prune")]
        self.assertIsNone(select(source)["target"])
    def test_HOLD_NEVER_forced(self):
        x=select({"SEE_native_search_state_comparison":{
          "status":"HOLD_CENSORED_NO_COMPUTATIONAL_EVENT",
          "first_two_full_computational_match_candidates":[]}})
        self.assertIsNone(x["target"])
    def test_native_cpp_t2_requires_identical_FULL_chess_path_window(self):
        text=patch(ANCHOR+"\n"+END)
        for field in ("root_call","root_move","key64","parent_key64",
                      "path_exact","move","site","threshold","source_ply","source_depth",
                      "source_alpha","source_beta","source_pv","source_rule50",
                      "source_occupancy64"):
            self.assertIn("C3X023_T2_"+field,text)
        self.assertIn("c3x023_T2_delivered_count",text)
        self.assertIn("kind=forced",text)
        with self.assertRaises(ValueError):patch(text)
    def test_preexisting_native_T1_SHA_does_not_depend_on_T2_outcomes(self):
        self.assertEqual(T1_SHA,
          "1975a515755e31a4c9445239750bde88211a13c328f667d86cabba2ce58effeb")
        self.assertEqual(len(SELECTED),6)
        self.assertEqual(len(FIELDS),15)
    def test_play_subprocess_clears_all_T2_sources_when_off(self):
        source=(Path(__file__).resolve().parents[1]/"harness"/
            "c3x_018_native_TT_lineage_factorial_6_8.py").read_text()
        self.assertIn('env.pop("C3X023_T2_ENABLE",None)',source)
        self.assertIn('"P1_T2_SOURCE_EXACT_TARGET_REQUIRED"',source)
if __name__=="__main__":unittest.main()
