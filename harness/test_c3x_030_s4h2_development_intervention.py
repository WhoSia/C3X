import hashlib
import unittest
from unittest.mock import patch
from c3x_030_s4h2_development_intervention import execute

def fixture():
    cases=[]
    observations=[]
    for i in range(8):
        case={"case_id":f"dev_{i}","game_id":f"game_{i//2}",
              "split":"development","fen":f"fen_{i}"}
        cases.append(case)
        observations.append({"case_id":case["case_id"],"game_id":case["game_id"],
          "split":"development","eligible":True,"frozen_key":"123"})
    p={"schema":"c3x030-s4h2-preoutcome-native-execution-protocol-v1",
       "arm_order":["original","sham","zero","one","two","many"],
       "mask_hit_caps":{"original":None,"sham":10000,"zero":0,"one":1,"two":2,"many":10000},
       "cases":cases}
    e={"schema":"c3x030-s4h2-source-only-eligibility-receipts-v1",
       "split":"development","source_probes_only":True,
       "engine_scores_read":False,"engine_bestmove_read":False,
       "engine_pv_read":False,"treatment_searches":0,
       "cases":observations,"binary_sha256":"unused"}
    return p,e

class TestDevelopment(unittest.TestCase):
    def test_holdout_disallowed(self):
        p,e=fixture();e["split"]="holdout"
        with self.assertRaisesRegex(ValueError,"NOT_DEVELOPMENT"):
            execute(p,e,"baseline","modified")
    def test_outcome_leak_disallowed(self):
        p,e=fixture();e["engine_scores_read"]=True
        with self.assertRaisesRegex(ValueError,"PRETREATMENT_LEAK"):
            execute(p,e,"baseline","modified")
    def test_missing_registered_case_disallowed(self):
        p,e=fixture();e["cases"].pop()
        with self.assertRaisesRegex(ValueError,"MISSING_OR_EXTRA"):
            execute(p,e,"baseline","modified")
    def test_treatment_cannot_change_dose_caps(self):
        p,e=fixture();p["mask_hit_caps"]["one"]=7
        with self.assertRaisesRegex(ValueError,"DOSE_CHANGED"):
            execute(p,e,"baseline","modified")
    def test_discovery_mode_must_not_continue_into_treatment(self):
        p,e=fixture()
        with patch.dict("os.environ",{"C3X_S4H2_ELIGIBILITY_MODE":"1"}):
            with self.assertRaisesRegex(ValueError,"MODE_MUST_BE_DISABLED"):
                execute(p,e,"baseline","modified")
if __name__=="__main__":unittest.main()
