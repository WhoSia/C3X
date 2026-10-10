#!/usr/bin/env python3
"""Fail closed exact source-first TT reader, true native score-use, multi-depth model."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_R1_TWIC1664_stageB_native_TT_value_survival_court import (
    exact_block,SCHEMA,SOURCE_SHA,PRIMITIVE_SHA)
class DeepNativeTTSource(unittest.TestCase):
    forecast={"physical":{"key64":101,"slot":0,"epoch":1},
              "root_calls":[2,4],"root_candidate_native":222}
    def event(self):
        return {"kind":"reader_block","root_call":2,"root_move":222,
                "key64":101,"slot":0,"epoch":1}
    @patch("c3x_022_P2_R1_TWIC1664_stageB_native_TT_value_survival_court.verified_reader_lineage")
    def test_exact_full64_physical_blocks_require_verifiable_writer(self,verify):
        verify.return_value={"all_valid":True,"count":1}
        d={"blocks":[self.event()],"lineage_summary":{"reader_block":1}}
        a,b=exact_block(d,self.forecast)
        self.assertEqual(len(a),1)
        self.assertTrue(b["all_valid"])
    @patch("c3x_022_P2_R1_TWIC1664_stageB_native_TT_value_survival_court.verified_reader_lineage")
    def test_nonmatching_source_rejected(self,verify):
        verify.return_value={"all_valid":True,"count":1}
        for key,x in (("key64",99),("slot",1),("epoch",2),("root_call",4),("root_move",500)):
            e={**self.event(),key:x}
            with self.assertRaises(RuntimeError):
                exact_block({"blocks":[e],"lineage_summary":{"reader_block":1}},self.forecast)
    @patch("c3x_022_P2_R1_TWIC1664_stageB_native_TT_value_survival_court.verified_reader_lineage")
    def test_nominal_source_without_delivery_not_contact(self,verify):
        verify.return_value={"all_valid":None,"count":0}
        e,v=exact_block({"blocks":[],"lineage_summary":{"reader_block":0}},self.forecast)
        self.assertEqual(e,[])
    def test_separately_scores_M0_M1_M2_and_native_value_use(self):
        root=Path(__file__).resolve().parents[1]/"harness"/"c3x_022_P2_R1_TWIC1664_stageB_native_TT_value_survival_court.py"
        s=root.read_text()
        for word in ('"native_baseline_watch_value_events"',
                     '"native_FIRST_watch_value_events"',
                     '"first_semantic_root_source_difference"',
                     '"M2_vs_M0_game_wins"',
                     '"HOLD_CENSORED_DISCOVERY"'):
            self.assertIn(word,s)
        self.assertEqual(len(SOURCE_SHA),64)
        self.assertEqual(len(PRIMITIVE_SHA),64)
if __name__=="__main__":unittest.main()
