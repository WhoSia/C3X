import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_029_p34_equal_budget_nnue_plan_court import adjudicate, METHODS, CASES


class P34Adjudication(unittest.TestCase):
    def trial(self):
        return {
          "A_PV":{"actual_nodes":24000,"predicted_replies":["a"]},
          "B_ONE_REPLY_JSON":{"actual_nodes":24100,"predicted_replies":["b"]},
          "C_THREE_REPLY_POLICY":{"actual_nodes":24200,"predicted_replies":["a","b","c"]}
        }
    def reference(self):
        return [{"reply":"a","root_value_cp":30,"nodes":40000},
                {"reply":"b","root_value_cp":-20,"nodes":40000},
                {"reply":"c","root_value_cp":5,"nodes":40000},
                {"reply":"d","root_value_cp":-50,"nodes":40000}]
    def test_all_replies_must_be_compared_to_outside_minimum(self):
        a=adjudicate(self.trial(),self.reference())
        self.assertEqual(a["reference_argmin_replies"],["d"])
        self.assertEqual(a["representations"]["A_PV"]["missed_refutation_gap_cp"],80)
        self.assertEqual(a["representations"]["B_ONE_REPLY_JSON"]["missed_refutation_gap_cp"],30)
        self.assertEqual(a["representations"]["C_THREE_REPLY_POLICY"]["missed_refutation_gap_cp"],30)
    def test_triplet_contains_true_worst(self):
        vals=self.reference()
        vals[2]["root_value_cp"]=-51
        a=adjudicate(self.trial(),vals)
        self.assertTrue(a["representations"]["C_THREE_REPLY_POLICY"]["includes_adjudicator_argmin"])
        self.assertFalse(a["representations"]["B_ONE_REPLY_JSON"]["includes_adjudicator_argmin"])
    def test_invalid_plan_reply_rejected(self):
        t=self.trial()
        t["B_ONE_REPLY_JSON"]["predicted_replies"]=["illegal"]
        with self.assertRaisesRegex(ValueError,"PREDICTED_REPLY_NOT_LEGAL"):
            adjudicate(t,self.reference())
    def test_adaptive_case_ids_preserved(self):
        self.assertEqual(CASES,(10,14))
        self.assertEqual(METHODS,("A_PV","B_ONE_REPLY_JSON","C_THREE_REPLY_POLICY"))

if __name__=="__main__":
    unittest.main()
