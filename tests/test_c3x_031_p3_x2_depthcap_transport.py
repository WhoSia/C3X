"""P3-X2 frozen depth-cap schedule and physical source negative regressions."""
import copy
import unittest

from c3x_030_r33_replay import PRETREATMENT
from c3x_031_p3_x2_depthcap_transport import (
    FROZEN_THREE, NODES, DEPTH_OFFSETS, ARMS,
    TOTAL_NEW_NATIVE_SEARCHES, reported_uci, extract_arm,
)


def fixture():
    target={field:str(i+1) for i,field in enumerate(PRETREATMENT)}
    target.update({"event":"27","root":"a2a3","null_eligible":"1"})
    row={"original_target":target}
    close={"event":"27","stopped":"0","skip_f":"1","skip_n":"1",
           "value":"42","null_cut":"0"}
    best={"move":"a2a3"}
    uci=["info depth 11 score cp 12 nodes 1899 pv a2a3",
         "bestmove a2a3"]
    proof={"best":best,"best_source":{"move":"a2a3"}}
    run={"events":[{"open":target,"close":close}],
         "proof":proof,"uci":uci,"trace":"1"*64}
    return row,run


class P3DepthCapTests(unittest.TestCase):
    def test_exposed_case_roots_are_not_reselected(self):
        self.assertEqual(FROZEN_THREE,(
            ("P2-005-0",12,"g8f8","g7g6"),
            ("P2-052-1",11,"a7c7","e5d6"),
            ("P2-056-1",13,"b8d8","h5e2")
        ))

    def test_full_matrix_exact_60_real_runs(self):
        self.assertEqual(NODES,(32000,64000))
        self.assertEqual(DEPTH_OFFSETS,(0,1))
        self.assertEqual(TOTAL_NEW_NATIVE_SEARCHES,60)
        self.assertEqual(len(ARMS),5)
        self.assertEqual(ARMS,(
            ("sham0",False,False),("sham1",False,False),
            ("futility_only",True,False),
            ("both_off0",True,True),("both_off1",True,True),
        ))

    def test_actual_reported_nodes_and_depth_fields(self):
        self.assertEqual(reported_uci([
            "info depth 10 score cp 22 nodes 849 pv b2b3",
            "info depth 11 score cp 12 nodes 1899 pv a2a3",
            "bestmove a2a3"
        ])["last_reported_uci_nodes"],1899)

    def test_exact_observed_source_under_depth_cap(self):
        row,run=fixture()
        ans=extract_arm(row,run,11,32000,True,True)
        self.assertEqual(ans["native_root_best"]["move"],"a2a3")
        self.assertEqual(ans["max_reported_uci_depth"],11)
        self.assertEqual(ans["public_budget_cap_nodes"],32000)

    def test_refuse_earlier_depth_cap_drift(self):
        row,run=fixture()
        with self.assertRaises(ValueError):
            extract_arm(row,run,10,32000,True,True)

    def test_refuse_broken_native_best_uci_link(self):
        row,run=fixture()
        run["uci"][-1]="bestmove b2b3"
        with self.assertRaises(ValueError):
            extract_arm(row,run,11,32000,True,True)

    def test_refuse_mismatched_source_flags(self):
        row,run=fixture()
        run["events"][0]["close"]["skip_n"]="0"
        with self.assertRaises(ValueError):
            extract_arm(row,run,11,32000,True,True)

    def test_refuse_event_not_contacted_without_retarg(self):
        row,run=fixture()
        run["events"][0]["open"]=copy.deepcopy(row["original_target"])
        run["events"][0]["open"]["attempt"]="101"
        with self.assertRaises(ValueError):
            extract_arm(row,run,11,32000,True,True)


if __name__=="__main__":
    unittest.main()
