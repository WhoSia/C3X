#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_021_P1_R1_full64_second_consumer_watch_native import (
    actual_use_analysis,USE_SITES
)

class NativeSourceValueUse(unittest.TestCase):
    physical={"key64":17,"slot":1,"epoch":2}
    watch={"key64":17,"root_call":6}
    def good_probe(self):
        return {"kind":"probe","key64":17,"root_call":6,
                "tt_hit":1,"shadow_full64_match":1,"tt_slot":1}
    def good_use(self,site):
        return {"kind":"used","site":site,"key64":17,
                "root_call":6,"full64_match":1}
    def test_eval_use_and_cutoff_are_separate(self):
        self.assertEqual(set(USE_SITES),
                         {"main","qsearch","main_cutoff","qsearch_cutoff"})
        row={"watched_tt_probes":[self.good_probe()],
             "native_tt_value_uses":[self.good_use("main"),self.good_use("qsearch_cutoff")]}
        result=actual_use_analysis(row,self.physical,self.watch)
        self.assertEqual(result["native_eval_assignment_events"],1)
        self.assertEqual(result["native_main_or_qsearch_cutoff_events"],1)
        self.assertEqual(result["native_use_count"],2)
    def test_probe_does_not_imply_native_consumption(self):
        row={"watched_tt_probes":[self.good_probe()],"native_tt_value_uses":[]}
        result=actual_use_analysis(row,self.physical,self.watch)
        self.assertEqual(result["class"],"FULL64_PROBE_WITH_NO_ACTUAL_NATIVE_USE")
        self.assertEqual(result["native_use_count"],0)
    def test_use_without_probe_fails(self):
        row={"watched_tt_probes":[],"native_tt_value_uses":[self.good_use("main")]}
        with self.assertRaises(RuntimeError):
            actual_use_analysis(row,self.physical,self.watch)
    def test_mismatched_key_or_source_call_fails(self):
        row={"watched_tt_probes":[self.good_probe()],
             "native_tt_value_uses":[{**self.good_use("main"),"key64":18}]}
        with self.assertRaises(RuntimeError):
            actual_use_analysis(row,self.physical,self.watch)
        row["native_tt_value_uses"]=[self.good_use("main")]
        row["watched_tt_probes"]=[{**self.good_probe(),"root_call":7}]
        with self.assertRaises(RuntimeError):
            actual_use_analysis(row,self.physical,self.watch)
    def test_censor_fails_closed(self):
        with self.assertRaises(RuntimeError):
            actual_use_analysis({"watched_tt_probes":[{"kind":"censored"}],
                                 "native_tt_value_uses":[]},
                                self.physical,self.watch)
if __name__=="__main__":unittest.main()
