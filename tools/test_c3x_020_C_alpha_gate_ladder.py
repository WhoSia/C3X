#!/usr/bin/env python3
"""Pre-native strict tests for C3X020-C forecast and native gate witnesses."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"harness"), str(ROOT/"tools")]
from c3x_020_C_alpha_gate_threshold_ladder_native import (
    TARGETS, ORIGINAL_VALUE, ALPHA, F_MOVE, V_MOVE,
    treatment, observed_gate, classify_ladder, terminal_by_depth
)
from c3x_020_multi_state_root_repair_overlay import patch

class AlphaGateCourtTest(unittest.TestCase):
    def test_full_precommitted_denominator_and_nonretarget(self):
        self.assertEqual([x[1] for x in TARGETS],
                         [-206,-191,-190,-189,-180,-179])
        self.assertEqual(ALPHA,-190)
        self.assertEqual(treatment(-191)["move"],222)
        self.assertEqual(treatment(-179)["expected"],ORIGINAL_VALUE)
        self.assertEqual(treatment(-191,sham=True)["move"],65535)
    def test_gate_equal_alpha_is_closed(self):
        for x,gate in ((-206,0),(-191,0),(-190,0),(-189,1),(-180,1),(-179,1)):
            contact=[{"kind":"repaired","depth":4,"root_call":4,"trial":1,
                      "move":222,"index":5,"alpha":-190,"beta":-166,
                      "before":-179,"after":x,"target":x,
                      "candidate_update_gate":gate,
                      "alpha_improvement_gate":gate,"beta_boundary_gate":0}]
            got=observed_gate(x,contact)
            self.assertEqual(got["candidate_update"],gate)
            self.assertEqual(got["native_value_changed"],x!=-179)
    def test_forged_gate_and_noncontact_fail(self):
        event={"kind":"repaired","depth":4,"root_call":4,"trial":1,
                "move":222,"index":5,"alpha":-190,"beta":-166,
                "before":-179,"after":-190,"target":-190,
                "candidate_update_gate":1,"alpha_improvement_gate":1,"beta_boundary_gate":0}
        with self.assertRaises(RuntimeError):
            observed_gate(-190,[event])
        with self.assertRaises(RuntimeError):
            observed_gate(-190,[])
        event["candidate_update_gate"]=0
        event["alpha_improvement_gate"]=0
        with self.assertRaises(RuntimeError):
            observed_gate(-190,[event,event])
        with self.assertRaises(RuntimeError):
            observed_gate(-190,[{**event,"move":221}])
    def test_classifier_does_not_infer_results_from_gate_alone(self):
        good=[]
        for label,value,pred in TARGETS:
            good.append({"label":label,"bestmove":pred,
                         "predict_bestmove_correct":True,
                         "actual_gate":{"candidate_update":int(value>ALPHA)}})
        self.assertEqual(classify_ladder(good)["sharp_gate_H_G"],"PASS")
        self.assertEqual(classify_ladder(good)["one_unit_discontinuity_H_C"],"PASS")
        altered=[dict(x) for x in good]
        altered[2]["bestmove"]=V_MOVE
        altered[2]["predict_bestmove_correct"]=False
        self.assertEqual(classify_ladder(altered)["sharp_gate_H_G"],"FAIL")
        self.assertEqual(classify_ladder(altered)["one_unit_discontinuity_H_C"],"FAIL")
    def test_depth_evidence_uses_final_trial_each_depth(self):
        events=[{"kind":"after_sort","depth":i,"first_move":1,
                 "first_score":i,"value":i,"trial":1,"alpha":-5,"beta":5}
                for i in range(1,13)]
        events.insert(3,{"kind":"after_sort","depth":3,"first_move":2,
                         "first_score":-999,"value":-999,"trial":2,"alpha":-5,"beta":5})
        d=terminal_by_depth(events)
        self.assertEqual(d["3"]["trial"],2)
        self.assertEqual(d["12"]["leader_native"],1)
        with self.assertRaises(RuntimeError):
            terminal_by_depth(events[:-1])
    def test_actual_source_overlay_contains_native_gate_witness(self):
        source="""namespace Stockfish {
  c3x019_return_repair_contacts = 0;
      // C3X019 one-site synthetic edge intervention, after child subtree search.
      if (!Threads.stop)
          completedDepth = rootDepth;
}"""
        # Contract requires 019 source state to be present, not just name-only event.
        patched=patch(source)
        for label in ("candidate_update_gate=", "alpha_improvement_gate=",
                      "beta_boundary_gate=", "int(moveCount == 1 || int(value) > int(alpha))"):
            self.assertIn(label,patched)
        self.assertLess(patched.index("C3X020 independently selected second root"),
                        patched.index("C3X019 one-site synthetic edge"))
if __name__=="__main__":
    unittest.main()
