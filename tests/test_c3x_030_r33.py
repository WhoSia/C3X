"""Guard the frozen event selection and the intervention entry signature."""
import unittest

from c3x_030_r33_gate_panel import select
from c3x_030_r33_replay import focus


def event(seq, group, slack, *, root="e2e4"):
    beta = 10
    return {"open": {"event":str(seq), "attempt":"3", "candidate":"6", "root":root,
                     "excluded":"g1f3", "tested":"d2d4", "parent_stage":"reduced",
                     "key":"42", "ply":"3", "depth":"3", "alpha":"9", "beta":str(beta),
                     "floor":str(beta+slack), "eval":"50", "static":"25",
                     "null_eligible":str(group)}, "close":{"event":str(seq),"value":"50"}}


class R33EventTests(unittest.TestCase):
    def test_select_minimum_slack_by_stratum_and_first_occurrence(self):
        rows = [event(1,1,5),event(2,0,0),event(3,1,2),event(4,1,2),event(5,0,4)]
        chosen = select(rows)
        self.assertEqual(chosen["1"]["open"]["event"],"3")
        self.assertEqual(chosen["0"]["open"]["event"],"2")

    def test_reject_outside_depth_or_ineligible_slack(self):
        row=event(1,1,0)
        row["open"]["depth"]="6"
        with self.assertRaisesRegex(ValueError,"registered range"):
            select([row])
        row["open"]["depth"]="3"
        row["open"]["floor"]="9"
        with self.assertRaisesRegex(ValueError,"ineligible"):
            select([row])

    def test_focus_matches_all_pretreatment_fields(self):
        selected=event(3,1,0)
        self.assertEqual(focus([event(1,0,1),selected],selected["open"]), selected)
        changed=event(3,1,0,root="d2d4")
        with self.assertRaisesRegex(ValueError,"identity"):
            focus([changed],selected["open"])
        with self.assertRaisesRegex(ValueError,"identity"):
            focus([selected,selected],selected["open"])


if __name__=="__main__":
    unittest.main()
