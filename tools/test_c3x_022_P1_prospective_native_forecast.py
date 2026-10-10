#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P1_april16_prospective_order_TT_court import (
    SOURCE_SHA,ATOMIC_SHA,ROLES,WORLDS,physical_contact
)
class ProspectiveRootChoiceForecast(unittest.TestCase):
    pair={"physical":{"key64":19,"slot":0,"epoch":2},"root_calls":[4,6],
          "root_candidate_native":222}
    def event(self):
        return {"kind":"reader_block","root_call":4,"root_move":222,
                "key64":19,"slot":0,"epoch":2}
    @patch("c3x_022_P1_april16_prospective_order_TT_court.verified_reader_lineage")
    def test_physical_contact_real_vs_nominal(self,verify):
        verify.return_value={"all_valid":True,"count":1}
        row={"blocks":[self.event()],"lineage_summary":{"reader_block":1}}
        contacts,w=physical_contact(row,self.pair)
        self.assertEqual(len(contacts),1)
        self.assertTrue(w["all_valid"])
    @patch("c3x_022_P1_april16_prospective_order_TT_court.verified_reader_lineage")
    def test_nominal_selected_but_no_contact_is_not_success(self,verify):
        verify.return_value={"all_valid":None,"count":0}
        c,w=physical_contact({"blocks":[],"lineage_summary":{"reader_block":0}},self.pair)
        self.assertEqual(c,[])
    @patch("c3x_022_P1_april16_prospective_order_TT_court.verified_reader_lineage")
    def test_wrong_physical_target_or_root_refused(self,verify):
        verify.return_value={"all_valid":True,"count":1}
        for k,v in (("key64",0),("slot",1),("epoch",3),("root_call",7),
                    ("root_move",333)):
            event={**self.event(),k:v}
            with self.assertRaises(RuntimeError):
                physical_contact({"blocks":[event],
                    "lineage_summary":{"reader_block":1}},self.pair)
    def test_sources_frozen_and_no_cross_order_TT_target(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_022_P1_april16_prospective_order_TT_court.py").read_text()
        self.assertEqual(len(SOURCE_SHA),64)
        self.assertEqual(len(ATOMIC_SHA),64)
        self.assertEqual(ROLES,("STRICT","BROAD"))
        self.assertEqual(WORLDS,("O","F"))
        self.assertIn('pair=first_pair(events,RULES[role])',s)
        self.assertIn('for order in WORLDS:',s)
        self.assertIn('move_micro_comparison(',s)
        self.assertIn('H22_ORDER',s)
        self.assertIn('H22_NATIVE',s)
        self.assertIn('H22_CONTEXT',s)
if __name__=="__main__":unittest.main()
