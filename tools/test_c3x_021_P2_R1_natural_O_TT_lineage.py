#!/usr/bin/env python3
"""Negative tests for independent natural-O physical TT discovery and contact."""
import sys,unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_021_P2_R1_natural_O_independent_TT_lineage import (
    judge,ROLES,MARCH_SHA,F_P1_SHA
)

class IndependentOPhysicalLineage(unittest.TestCase):
    physical={"key64":945,"slot":1,"epoch":3}
    pair={"physical":physical,"root_calls":[11,14],
          "root_candidate_native":4178}
    def block(self,**fields):
        return {"kind":"reader_block","root_call":11,
                "root_move":4178,**self.physical,**fields}
    def v(self,blocks):
        return {"blocks":blocks,"lineage_summary":{"reader_block":len(blocks)},
                "UCI":{"bestmove":"a2a3"},
                "root_events":[{"kind":"after_sort","depth":i,"first_move":1,
                                "value":1,"trial":1} for i in range(1,13)]}
    def o(self):
        return {"UCI":{"bestmove":"a2a4"},
                "root_events":[{"kind":"after_sort","depth":i,"first_move":1,
                                "value":1,"trial":1} for i in range(1,13)]}
    @patch("c3x_021_P2_R1_natural_O_independent_TT_lineage.verified_reader_lineage")
    def test_exact_O_native_block_can_flip(self,verify):
        verify.return_value={"all_valid":True,"count":1}
        r=judge(self.o(),self.v([self.block()]),self.pair,"STRICT")
        self.assertTrue(r["native_contact"])
        self.assertTrue(r["delivered_final_choice_change"])
        self.assertEqual(r["physical"]["key64"],945)
    @patch("c3x_021_P2_R1_natural_O_independent_TT_lineage.verified_reader_lineage")
    def test_selected_pair_without_real_contact_does_not_count(self,verify):
        verify.return_value={"all_valid":True,"count":0}
        r=judge(self.o(),self.v([]),self.pair,"BROAD")
        self.assertFalse(r["native_contact"])
        self.assertFalse(r["delivered_final_choice_change"])
    @patch("c3x_021_P2_R1_natural_O_independent_TT_lineage.verified_reader_lineage")
    def test_wrong_physical_root_call_refused(self,verify):
        verify.return_value={"all_valid":True,"count":1}
        for drift in ({"key64":7},{"slot":0},{"epoch":2},
                      {"root_call":14},{"root_move":4179}):
            e={**self.block(),**drift}
            with self.assertRaises(RuntimeError):
                judge(self.o(),self.v([e]),self.pair,"STRICT")
    @patch("c3x_021_P2_R1_natural_O_independent_TT_lineage.verified_reader_lineage")
    def test_writer_integrity_fails_closed(self,verify):
        verify.return_value={"all_valid":False,"count":1}
        with self.assertRaises(RuntimeError):
            judge(self.o(),self.v([self.block()]),self.pair,"STRICT")
    def test_own_source_selected_independent_from_F(self):
        code=(Path(__file__).resolve().parents[1]/"harness"/
              "c3x_021_P2_R1_natural_O_independent_TT_lineage.py").read_text()
        self.assertIn('discovery=cold(engine,world,clocks,"O","OBS",discovery=True)',code)
        self.assertIn('pair=first_pair(witness,RULES[role])',code)
        self.assertIn('tt_reader_filters=mask_filters(RULES[role],pair,"FIRST")',code)
        self.assertNotIn('pair=parent["roles"]',code)
        self.assertEqual(len(ROLES),2)
        self.assertEqual(len(MARCH_SHA),len(F_P1_SHA))
if __name__=="__main__":unittest.main()
