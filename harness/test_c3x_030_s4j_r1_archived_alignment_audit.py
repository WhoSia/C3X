import hashlib,json,unittest
from unittest.mock import patch
import c3x_030_s4j_r1_archived_alignment_audit as a
from c3x_030_s4j_state_alignment import compare

def sample():
    cases={}
    for i in range(8):
        name=f"dev_{i//2}_ply{8 if i%2==0 else 10}"
        state=[123,3,-20,40,1,0,1]
        event={"ordinal":0,"invocation_id":"9","parent_id":"1","state":state,"return_value":42}
        sham={"events":[event],"observed":1,"observed_cutoffs":1,"right_censored":False}
        two={"events":[dict(event,return_value=42)],"observed":1,"observed_cutoffs":1,"right_censored":False}
        cases[name]={"game_id":f"dev_{i//2}","frozen_key":"123",
          "original_sham_noninterference":True,
          "cutoff_return_trace":{"sham":sham,"two":two},
          "candidate_cross_arm_state_alignment":compare(sham,two),
          "root_move_changes":0}
    return {"schema":a.SCHEMA,"verdict":"PASS_BOUNDED_CANDIDATE_STATE_ALIGNMENT_ONLY",
      "native_searches":48,"native_nodes":5000,"control_noninterference":True,
      "untouched_holdout":True,"causal_mediation_proven":False,
      "cases":cases,"total_tt_cutoff_observations":{"sham":8,"two":8},
      "candidate_shared_state_total":8,"candidate_unique_state_total":8,
      "candidate_repeated_state_ambiguity_total":0,"root_change_total":0}

def verify(d):
    raw=(json.dumps(d,sort_keys=True)+"\n").encode()
    with patch.object(a,"ORIGINAL_SHA",hashlib.sha256(raw).hexdigest()):
        return a.audit(raw)

class ArchivedAuditTests(unittest.TestCase):
    def test_source_is_not_self_certifying(self):
        with self.assertRaisesRegex(ValueError,"ARCHIVED_RAW"):a.audit(b'{}')
    def test_synthetic_identity_contract(self):
        r=verify(sample())
        self.assertEqual(r["totals"]["unique"],8)
        self.assertFalse(r["complete_tt_to_root_mediation_proven"])
    def test_forged_summary_rejected(self):
        d=sample();d["candidate_unique_state_total"]=9
        with self.assertRaisesRegex(ValueError,"SUMMARY_NOT_REPRODUCIBLE"):verify(d)
    def test_forged_value_alignment_rejected(self):
        d=sample();next(iter(d["cases"].values()))["cutoff_return_trace"]["two"]["events"][0]["return_value"]=23
        with self.assertRaisesRegex(ValueError,"ALIGNMENT_RECOMPUTE"):verify(d)
    def test_wrong_game_count_rejected(self):
        d=sample();d["cases"].pop(next(iter(d["cases"])))
        with self.assertRaisesRegex(ValueError,"CASES_CORRELATED"):verify(d)
    def test_fake_censor_rejected(self):
        d=sample();next(iter(d["cases"].values()))["cutoff_return_trace"]["sham"]["right_censored"]=True
        with self.assertRaisesRegex(ValueError,"FALSE_CENSOR"):verify(d)
if __name__=="__main__":unittest.main()
