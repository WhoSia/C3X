"""P3-X1 native source gate negative control: source event unit regressions.

These synthetic records test the court, not claim new real Stockfish trials.
"""
import copy
import unittest

from c3x_030_r33_replay import PRETREATMENT
from c3x_031_p3_x1_gate_factorial import evaluate_negative_cell, N_ONLY_REPEATS


def fixture():
    sign={key:str(i+1) for i,key in enumerate(PRETREATMENT)}
    sign.update({"event":"7","root":"a2a3","null_eligible":"1"})
    close={"event":"7","value":"341","nodes":"317",
           "skip_f":"0","skip_n":"1","stopped":"0",
           "futility":"1","null_tried":"0","null_cut":"0","replies":"0"}
    original=copy.deepcopy(close)
    original["skip_n"]="0"
    root_best={"move":"a2a3","update":"1"}
    root_producer={"move":"a2a3","attempt":"17"}
    pub=["info depth 6 score cp 12 nodes 100 pv a2a3","bestmove a2a3"]
    b2={"original_target":sign,"arms":{"sham0":{
        "source_uci":pub,"bestmove":"a2a3","proof":root_best,
        "root_producer":root_producer,
        "target_event":{"open":sign,"close":original}
    }}}
    observed={"events":[{"open":sign,"close":close}],
              "proof":{"best":root_best,"best_source":root_producer},
              "uci":pub,"trace":"0"*64}
    return b2,observed


class P3FactorialTests(unittest.TestCase):
    def test_exact_two_cold_processes_locked(self):
        self.assertEqual(N_ONLY_REPEATS,2)

    def test_expected_unreachable_null_only_source_return(self):
        old,run=fixture()
        found=evaluate_negative_cell(old,run)
        self.assertEqual(found["bestmove"],"a2a3")
        self.assertEqual(found["source_event"]["close"]["null_tried"],"0")

    def test_wrong_preintervention_event_rejected(self):
        old,run=fixture()
        run["events"][0]["open"]=copy.deepcopy(old["original_target"])
        run["events"][0]["open"]["attempt"]="99"
        with self.assertRaises(ValueError):
            evaluate_negative_cell(old,run)

    def test_null_gate_reached_is_negative_control_failure(self):
        old,run=fixture()
        run["events"][0]["close"]["null_tried"]="1"
        with self.assertRaises(ValueError):
            evaluate_negative_cell(old,run)

    def test_futility_accidentally_disabled_is_invalid(self):
        old,run=fixture()
        run["events"][0]["close"]["skip_f"]="1"
        with self.assertRaises(ValueError):
            evaluate_negative_cell(old,run)

    def test_targeted_native_child_return_changed_is_invalid(self):
        old,run=fixture()
        run["events"][0]["close"]["value"]="17"
        with self.assertRaises(ValueError):
            evaluate_negative_cell(old,run)

    def test_root_candidate_producer_changed_is_invalid(self):
        old,run=fixture()
        run["proof"]["best_source"]={"move":"b2b3","attempt":"99"}
        with self.assertRaises(ValueError):
            evaluate_negative_cell(old,run)

    def test_uci_choice_changed_is_invalid(self):
        old,run=fixture()
        run["uci"]=["info depth 6 score cp 12 nodes 100 pv a2a3","bestmove b2b3"]
        with self.assertRaises(ValueError):
            evaluate_negative_cell(old,run)

    def test_excess_native_source_events_do_not_retarget(self):
        old,run=fixture()
        # Duplicate event_id must not make this source audit silently select one.
        run["events"].append(copy.deepcopy(run["events"][0]))
        with self.assertRaises(ValueError):
            evaluate_negative_cell(old,run)


if __name__=="__main__":
    unittest.main()
