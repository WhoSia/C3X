"""P3-X3 simulated source PRE snapshot and original-source observer invariants."""
import copy
import unittest

from c3x_030_r33_replay import PRETREATMENT
from c3x_031_p3_x3_nonmutating_tt_observer import (
    STATE_KEYS,FROZEN_CASES,ARMS,MODES,NEW_SOURCE_SEARCHES,
    parse_state,verified_source_arm
)


def signed():
    data={key:str(i+1) for i,key in enumerate(PRETREATMENT)}
    data.update({"event":"12","key":"47241","nodes":"3159"})
    close={"event":"12","skip_f":"0","skip_n":"0","value":"17"}
    source={"original_target":data}
    prior={"target_event":{"open":data,"close":close},
           "proof":{"move":"a2a3"},"root_producer":{"move":"a2a3","id":"10"},
           "source_uci":["info depth 6 score cp 14 nodes 1150 pv a2a3","bestmove a2a3"]}
    r={"source_events":[{"open":data,"close":close}],
       "uci":prior["source_uci"],
       "proof":{"best":prior["proof"],"best_source":prior["root_producer"]},
       "R39":[dict(event="12",key="47241",tt_hit="0",tt_move="0000",
                   tt_depth="-99",tt_bound="0",tt_raw_value="32002",
                   tt_value="32002",tt_eval="32002",tt_pv="0",
                   parent_stat="4",rule50="2",source_nodes="3159")]}
    return source,prior,r


class P3SafeTTObserverTests(unittest.TestCase):
    def test_fixed_7_x_3_x_3_real_search_census(self):
        self.assertEqual(NEW_SOURCE_SEARCHES,63)
        self.assertEqual(len(FROZEN_CASES),7)
        self.assertEqual(len(ARMS),3)
        self.assertEqual(MODES,("observer_off","observer_on0","observer_on1"))

    def test_original_R39_scope_can_only_be_pre_event(self):
        self.assertEqual(len(STATE_KEYS),13)
        self.assertIn("tt_hit",STATE_KEYS)
        self.assertIn("tt_raw_value",STATE_KEYS)
        self.assertNotIn("TT_probe_again",STATE_KEYS)

    def test_physical_pre_event_source_parity(self):
        x,p,r=signed()
        a=verified_source_arm(x,r,p,True)
        self.assertEqual(a["key"],"47241")
        self.assertEqual(a["tt_hit"],"0")

    def test_observer_disabled_must_have_no_R39_line(self):
        x,p,r=signed()
        r["R39"]=[]
        self.assertIsNone(verified_source_arm(x,r,p,False))

    def test_wrong_observer_count_rejected(self):
        x,p,r=signed()
        r["R39"].append(copy.deepcopy(r["R39"][0]))
        with self.assertRaises(ValueError):
            verified_source_arm(x,r,p,True)

    def test_original_native_move_disagreement_rejected(self):
        x,p,r=signed()
        r["proof"]["best"]=copy.deepcopy(r["proof"]["best"])
        r["proof"]["best"]["move"]="b2b3"
        with self.assertRaises(ValueError):
            verified_source_arm(x,r,p,True)

    def test_source_pre_event_tt_key_mismatch_rejected(self):
        x,p,r=signed()
        r["R39"][0]["key"]="5000"
        with self.assertRaises(ValueError):
            verified_source_arm(x,r,p,True)

    def test_source_pre_event_tt_miss_cannot_claim_entry(self):
        x,p,r=signed()
        r["R39"][0]["tt_depth"]="10"
        with self.assertRaises(ValueError):
            verified_source_arm(x,r,p,True)

    def test_missing_source_target_rejected(self):
        x,p,r=signed()
        r["source_events"][0]["open"]=copy.deepcopy(x["original_target"])
        r["source_events"][0]["open"]["attempt"]="4242"
        with self.assertRaises(ValueError):
            verified_source_arm(x,r,p,True)

    def test_state_parser_refuse_duplicate_fields(self):
        msg="C3X_R39_PRE event=1 event=2"
        with self.assertRaises(ValueError):
            parse_state([msg])

    def test_state_parser_refuse_unexpected_source_schema(self):
        msg="C3X_R39_PRE event=1 key=2 tt_hit=1"
        with self.assertRaises(ValueError):
            parse_state([msg])


if __name__=="__main__":
    unittest.main()
