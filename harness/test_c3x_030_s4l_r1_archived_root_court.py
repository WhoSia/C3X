import hashlib,json,unittest
from unittest.mock import patch
import c3x_030_s4l_r1_archived_root_court as a

def fixture():
    cases={}
    for i in range(8):
        case=f"dev_{i//2}_ply{8 if i%2==0 else 10}"
        trials={}
        for arm in ("sham","two"):
            epochs={}
            for n in ("1","2"):
                r={"ordinal":0,"epoch":int(n),"root_move_raw":42,"value":9,
                   "old_best":5,"alpha":1,"beta":20,"move_count":1,
                   "will_update_best":True,"will_update_root_pv":True,"depth":3}
                epochs[n]={"events":[],"observed":0,"right_censored":False,
                    "actual_source_cutoffs_at_this_return_site":0,
                    "root_score_receipts":[r],"root_score_total_at_this_site":1,
                    "root_score_right_censored":False,
                    "root_candidate_update_site_covered":True,
                    "not_tied_to_specific_tt_invocation":True}
            trials[arm]={"trials":epochs,"logged_root_score_events_total":2,
                         "all_root_score_events_total":2}
        cases[case]={"game_id":f"dev_{i//2}","original_sham_noninterference":True,
            "native_trials":{"sham":[{"bestmove":"e2e4"},{"bestmove":"d2d4"}],
                             "two":[{"bestmove":"e2e4"},{"bestmove":"d2d4"}]},
            "root_move_changes":0,"per_trial_root_changed":{"1":False,"2":False},
            "cutoff_return_trace":trials}
    return {"schema":a.ORIGINAL_SCHEMA,"verdict":"PASS_ROOT_SCORE_RECEIPT_SITE_ONLY",
      "native_searches":48,"native_nodes":576619,"control_noninterference":True,
      "untouched_holdout":True,"causal_mediation_proven":False,"cases":cases,
      "root_update_receipts_by_arm":{"sham":16,"two":16},
      "root_update_total_by_arm":{"sham":16,"two":16},
      "actual_cutoff_events_by_arm":{"sham":0,"two":0},"root_change_total":0}

def run(x):
    raw=(json.dumps(x,sort_keys=True)+"\n").encode()
    with patch.object(a,"ORIGINAL_SHA",hashlib.sha256(raw).hexdigest()):
        return a.audit(raw)

class ArchivedRootAuditTests(unittest.TestCase):
    def test_cannot_self_certify_new_bytes(self):
        with self.assertRaisesRegex(ValueError,"IMMUTABLE_ORIGINAL"):
            a.audit(b"{}")
    def test_valid_frozen_contract(self):
        r=run(fixture())
        self.assertEqual(r["arms"]["sham"]["logged"],16)
        self.assertFalse(r["particular_tt_mask_to_root_score_causal_mediation_proven"])
    def test_falsified_root_update_flag(self):
        d=fixture();next(iter(d["cases"].values()))["cutoff_return_trace"]["two"]["trials"]["1"]["root_score_receipts"][0]["will_update_best"]=False
        with self.assertRaisesRegex(ValueError,"FALSE_ROOT_DECISION"):run(d)
    def test_root_receipt_count_forgery(self):
        d=fixture();next(iter(d["cases"].values()))["cutoff_return_trace"]["two"]["trials"]["1"]["root_score_total_at_this_site"]=2
        with self.assertRaisesRegex(ValueError,"ROOT_SITE_COVERAGE"):run(d)
    def test_pretend_source_control_matches(self):
        d=fixture();next(iter(d["cases"].values()))["original_sham_noninterference"]=False
        with self.assertRaisesRegex(ValueError,"CONTROL_INTERFERENCE"):run(d)
    def test_root_decision_fabrication(self):
        d=fixture();next(iter(d["cases"].values()))["root_move_changes"]=1
        with self.assertRaisesRegex(ValueError,"ROOT_OUTCOME"):run(d)
    def test_forged_total(self):
        d=fixture();d["root_update_total_by_arm"]["sham"]=0
        with self.assertRaisesRegex(ValueError,"AGGREGATE_DRIFT"):run(d)
if __name__=="__main__":unittest.main()
