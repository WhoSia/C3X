"""0.31/P2 B2 original-source-treatment and locked-family-court negative tests.

Synthetic masks, artificial labels and predictions here are only TEST
fixtures, not evidence that a prospective Stockfish move flipped.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from c3x_030_r33_replay import PRETREATMENT
from c3x_031_p2_1669_native_discovery import MODEL_SHA
from c3x_031_p2_1669_native_treatment import (
    ARMS, B1_SHA, NODES, SAMPLE_SHA, require, validate_arm,
)
from c3x_031_p2_1669_outcome_court import audit_and_score, BOOTSTRAPS


def event(open_id="12", group="1"):
    original={k:"0" for k in PRETREATMENT}
    original.update({
        "event":open_id, "null_eligible":group,"depth":"2",
        "ply":"4","attempt":"33","candidate":"99","root":"a2a3",
        "floor":"15","beta":"14","alpha":"13",
        "nodes":"12344","key":"47151660",
    })
    return original


def arm_receipt(ev, skip_f, skip_n):
    close={"event":ev["event"],"skip_f":str(int(skip_f)),
           "skip_n":str(int(skip_n)),"stopped":"0"}
    uci=["info depth 10 score cp 20 pv a2a3",
         "bestmove a2a3"]
    return {"events":[{"open":ev,"close":close}],
            "proof":{"best":{"move":"a2a3"},"best_source":None},
            "uci":uci}


def synthetic_result():
    results=[]
    for i in range(128):
        game=i//2
        group=str(i%2)
        family="series-"+str(game%25)
        predictions=None if i in (52,53) else {
            "m0":.089,"m1":.10,"m2":.08}
        arms={name:{"bestmove":"a2a3"} for name,_,_ in ARMS}
        results.append({
            "id":f"P2-{game+1:03}-{group}",
            "case_id":f"P2-{game+1:03}",
            "family":family,
            "game_sha256":f"game-{game}",
            "original_untreated_bestmove":"a2a3",
            "predictions":predictions,
            "valid_primary":True,"y":0,
            "invalid_reason":None,
            "arms":arms,
        })
    return {
        "stage":"ACTUAL_NEW_SOURCE_INTERVENTIONS_UNSCORED",
        "source_event_results":results,
        "pre_outcome_signed_source_event_sha256":B1_SHA,
        "pre_outcome_model_sha256":MODEL_SHA,
        "original_source_cohort_sha256":SAMPLE_SHA,
        "actual_native_intervention_processes":640,
        "native_treatment_processes_per_event":5,
    }


class NativeB2Tests(unittest.TestCase):
    def test_arm_contract_fixed_sham_and_combined_main(self):
        self.assertEqual(ARMS,(
            ("sham0",False,False),("sham1",False,False),
            ("both_off0",True,True),("both_off1",True,True),
            ("futility_only",True,False)))
        self.assertEqual(NODES,32000)

    def test_matched_native_source_open_and_close(self):
        ev=event()
        with tempfile.TemporaryDirectory() as tmp:
            stderr=Path(tmp)/"stderr.txt"
            stderr.write_text("original signed source trace\n")
            out=validate_arm("a2a3",ev,arm_receipt(ev,True,True),
                             True,True,stderr)
            self.assertTrue(out["original_unchanged_target_signature"])
            self.assertEqual(out["changes_untouched_choice"],0)
            self.assertEqual(out["bestmove"],"a2a3")

    def test_refuse_unreached_source_event(self):
        ev=event()
        changed=event(open_id="13")
        with tempfile.TemporaryDirectory() as tmp:
            stderr=Path(tmp)/"trace"
            stderr.write_text("not a real source match")
            with self.assertRaises(ValueError):
                validate_arm("a2a3",ev,arm_receipt(changed,True,True),
                             True,True,stderr)

    def test_refuse_wrong_futility_null_treatment_flags(self):
        ev=event()
        with tempfile.TemporaryDirectory() as tmp:
            stderr=Path(tmp)/"trace"
            stderr.write_text("not enough gates masked")
            with self.assertRaises(ValueError):
                validate_arm("a2a3",ev,arm_receipt(ev,True,False),
                             True,True,stderr)

    def test_refuse_target_interrupt(self):
        ev=event()
        rec=arm_receipt(ev,True,True)
        rec["events"][0]["close"]["stopped"]="1"
        with tempfile.TemporaryDirectory() as tmp:
            stderr=Path(tmp)/"trace"
            stderr.write_text("budget interrupted")
            with self.assertRaises(ValueError):
                validate_arm("a2a3",ev,rec,True,True,stderr)

    def test_family_bootstrap_uses_25_clusters_and_declared_abstentions(self):
        court=audit_and_score(synthetic_result())
        self.assertEqual(court["games"],64)
        self.assertEqual(court["canonical_tournament_families"],25)
        self.assertEqual(court["actual_scored_forecasts"],126)
        self.assertEqual(court["predeclared_noncpscore_abstentions"],2)
        self.assertEqual(court["valid_physical_event_contacts"],128)
        self.assertEqual(court["verdict"],"NO_CONFIRMED_PROSPECTIVE_SOURCE_STATE_GAIN")

    def test_reject_128_event_denominator_loss(self):
        data=synthetic_result()
        data["source_event_results"].pop()
        with self.assertRaises(ValueError):
            audit_and_score(data)

    def test_reject_frozen_before_outcome_model_change(self):
        data=synthetic_result()
        data["pre_outcome_model_sha256"]="bad"
        with self.assertRaises(ValueError):
            audit_and_score(data)

    def test_reject_retrospective_label_inconsistency(self):
        data=synthetic_result()
        data["source_event_results"][0]["y"]=1
        with self.assertRaises(ValueError):
            audit_and_score(data)

    def test_reject_overstated_native_search_number(self):
        data=synthetic_result()
        data["actual_native_intervention_processes"]=639
        with self.assertRaises(ValueError):
            audit_and_score(data)

    def test_reject_predicted_outcome_removed(self):
        data=synthetic_result()
        data["source_event_results"][13]["predictions"]=None
        with self.assertRaises(ValueError):
            audit_and_score(data)


if __name__=="__main__":
    unittest.main()
