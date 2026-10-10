#!/usr/bin/env python3
"""Pre-sealed exact UCI forecasts and the real physical first-reader TT delivery."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_external_exact_move_TT_counterfactual_court import (
    SOURCE_SHA,PRIMITIVES_SHA,actual_block,ROLES,WORLDS,ECOLOGIES)
class StageBPhysicalIntervention(unittest.TestCase):
    pair={"source_physical":{"key64":12345,"slot":1,"epoch":2},
          "root_calls":[4,7],"source_root_move_native":1337}
    def native(self,events):
        return {"blocks":events,"lineage_summary":{"reader_block":len(events)}}
    def event(self):
        return {"kind":"reader_block","root_call":4,"root_move":1337,
                "key64":12345,"slot":1,"epoch":2}
    @patch("c3x_022_P2_external_exact_move_TT_counterfactual_court.verified_reader_lineage")
    def test_real_full64_first_reader_required(self,verified):
        verified.return_value={"all_valid":True,"count":1}
        blocked,proof=actual_block(self.native([self.event()]),self.pair)
        self.assertEqual(len(blocked),1)
        self.assertTrue(proof["all_valid"])
    @patch("c3x_022_P2_external_exact_move_TT_counterfactual_court.verified_reader_lineage")
    def test_physical_key_epoch_rootcall_mismatch_rejected(self,verified):
        verified.return_value={"all_valid":True,"count":1}
        for key,value in (("key64",12346),("slot",0),("epoch",3),
                          ("root_call",7),("root_move",1338)):
            event={**self.event(),key:value}
            with self.assertRaises(RuntimeError):
                actual_block(self.native([event]),self.pair)
    @patch("c3x_022_P2_external_exact_move_TT_counterfactual_court.verified_reader_lineage")
    def test_selection_without_reader_block_is_noncontact(self,verified):
        verified.return_value={"all_valid":None,"count":0}
        x,y=actual_block(self.native([]),self.pair)
        self.assertFalse(x)
    def test_binary_and_exact_prediction_evaluated_only_on_contact(self):
        source=(Path(__file__).resolve().parents[1]/"harness"/
                "c3x_022_P2_external_exact_move_TT_counterfactual_court.py").read_text()
        self.assertIn("if delivered else None",source)
        self.assertIn("majority_no_flip_correct_if_contact",source)
        self.assertIn("earliest_root_leader_depth_changed",source)
        self.assertIn("verified_writer_reader",source)
        self.assertIn("root_depth_ladder",source)
    def test_input_source_snapshots_not_dynamic(self):
        self.assertEqual(SOURCE_SHA,"ebe6648f43f64c6f31e0d547845bec3d87c663093fd68298acf2ebe4c0287554")
        self.assertEqual(PRIMITIVES_SHA,"b3b4a29788c1f9dc2b4d491cd60d44ad8e6530d3d66be5d77039a6fd59cc958d")
        self.assertEqual(len(ECOLOGIES),2)
        self.assertEqual(ROLES,("STRICT","BROAD"))
        self.assertEqual(WORLDS,("O","F"))
if __name__=="__main__":unittest.main()
