#!/usr/bin/env python3
"""P2 negative contracts: physical TT source identity and legal-root subset."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_021_P2_full31_TT_factorial_legal_root_counterfactual import (
    ARMS,FOCI,witness,legal_root_cold,board_court)

class FixedPhysicalTTFactorial(unittest.TestCase):
    physical={"key64":12345678901234,"slot":2,"epoch":4}
    calls=[3,7]
    def event(self,call,**kw):
        return {"kind":"reader_block","root_call":call,
                "key64":self.physical["key64"],"slot":2,"epoch":4,**kw}
    def arm(self,blocks):
        return {"blocks":blocks,"lineage_summary":{"reader_block":len(blocks)}}
    def test_four_binary_arms_and_preselected_cases(self):
        self.assertEqual(ARMS,("ZERO","FIRST","SECOND","BOTH"))
        self.assertEqual(FOCI[(4,"BROAD")],("h8h4","g5h4"))
        self.assertEqual(FOCI[(9,"STRICT")],("a6b7","f6h5"))
        self.assertEqual(len(FOCI),2)
    def test_exact_physical_two_bit_dose(self):
        for mode,blocks,want in (
            ("ZERO",[],"00"),
            ("FIRST",[self.event(3)],"10"),
            ("SECOND",[self.event(7)],"01"),
            ("BOTH",[self.event(3),self.event(7)],"11"),
            ("BOTH",[self.event(3)],"10"),
            ("SECOND",[],"00"),
        ):
            z=witness(self.arm(blocks),self.physical,self.calls,mode)
            self.assertEqual(z["delivered_bits"],want)
    def test_physical_mismatch_refused(self):
        b=self.event(3,key64=999) if False else self.event(3)
        b["key64"]=999
        with self.assertRaises(RuntimeError):
            witness(self.arm([b]),self.physical,self.calls,"FIRST")
    def test_selected_root_call_mismatch_refused(self):
        with self.assertRaises(RuntimeError):
            witness(self.arm([self.event(7)]),self.physical,self.calls,"FIRST")
        with self.assertRaises(RuntimeError):
            witness(self.arm([self.event(3)]),self.physical,self.calls,"SECOND")
    def test_logged_contact_count_mismatch_refused(self):
        a=self.arm([self.event(3)])
        a["lineage_summary"]["reader_block"]=2
        with self.assertRaises(RuntimeError):
            witness(a,self.physical,self.calls,"FIRST")
    def test_root_move_input_validation_is_new_opt_in(self):
        code=(Path(__file__).resolve().parents[1]/"harness"/
              "c3x_018_native_TT_lineage_factorial_6_8.py").read_text()
        self.assertIn("root_searchmoves=None",code)
        self.assertIn('"ROOT_SEARCHMOVES_STRICT_UNIQUE_UCI"',code)
        self.assertIn('go_cmd+=" searchmoves "+" ".join(root_searchmoves)',code)
        self.assertIn("send(\"position fen \"+world[\"fen4\"]",code)
        self.assertEqual(code.count("go_cmd)"),3)

if __name__=="__main__":unittest.main()
