import hashlib
import json
import unittest
from unittest.mock import patch
import c3x_030_s4h2_preoutcome_protocol as p

def fixture():
    def row(i, split):
        gid=split+str(i//2)
        ply=8 if i%2==0 else 10
        return {"case_id":gid+"_ply"+str(ply),"game_id":gid,
                "fen":"synthetic-fen-"+str(i)+split,"history_uci":["a"]*ply}
    d={"schema":"c3x030-f2-blind-holdout-manifest-v1",
       "entries":[row(i,"hold") for i in range(16)],
       "development_entries":[row(i,"dev") for i in range(8)]}
    raw=(json.dumps(d,sort_keys=True)+"\n").encode()
    return raw

class ProtocolTests(unittest.TestCase):
    def locked(self, raw):
        with patch.object(p,"H0_SHA",hashlib.sha256(raw).hexdigest()):
            return p.make(raw)
    def test_valid_identity_only_plan(self):
        r=self.locked(fixture())
        self.assertEqual((r["number_of_positions"],r["planned_native_searches"]), (24,288))
        self.assertEqual(r["planned_holdout_native_searches"],192)
        self.assertIs(r["holdout_effects_observed"],False)
        self.assertEqual(r["method_superiority"],"HOLD")
        self.assertEqual(r["split_order"],["development","holdout"])
    def test_unpinned_raw_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError,"NOT_ORIGINAL"):
            p.make(fixture())
    def test_extra_prediction_field_rejected(self):
        d=json.loads(fixture())
        d["entries"][0]["label"]=1
        with self.assertRaisesRegex(ValueError,"OUTCOME_LEAK"):
            self.locked(json.dumps(d).encode())
    def test_missing_holdout_rejected(self):
        d=json.loads(fixture());d["entries"].pop()
        with self.assertRaisesRegex(ValueError,"CASE_COUNTS"):
            self.locked(json.dumps(d).encode())
    def test_no_implicit_key_reselection(self):
        r=self.locked(fixture())
        self.assertTrue(r["key_eligibility_policy"]["do_not_reselect_after_treatment"])
        self.assertEqual(r["key_eligibility_policy"]["no_source_hit"],
                         "record ineligible, retain in denominator, do not substitute another case")
    def test_native_workload_is_fixed(self):
        r=self.locked(fixture())
        self.assertEqual(r["engine_protocol"]["go_nodes"],12000)
        self.assertEqual(r["engine_protocol"]["threads"],1)
        self.assertEqual(r["arm_order"],["original","sham","zero","one","two","many"])
if __name__=="__main__":unittest.main()
