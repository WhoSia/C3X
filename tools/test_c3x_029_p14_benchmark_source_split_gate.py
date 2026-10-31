import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p14_benchmark_source_split_gate import audit

def sample():
    return [{"case_id":str(i),"game_id":f"g{i}","root_id":f"root{i}",
        "continuation_id":f"cont{i}","split":("support" if i==0 else "heldout"),
        "group":("positive","negative","nearby_negative")[i%3],
        "source_state_verified":True,"engine_label_verified":True} for i in range(4)]
class Admission(unittest.TestCase):
    def test_disjoint_source_admits_metadata(self):
        self.assertEqual(audit(sample())["status"],"METADATA_ADMISSIBLE_NOT_BYTE_VERIFIED")
    def test_same_game_with_different_root_fails(self):
        x=sample();x[1]["game_id"]=x[0]["game_id"]
        self.assertEqual(audit(x)["status"],"FAIL_CROSS_SPLIT_LEAKAGE")
    def test_shared_continuation_fails(self):
        x=sample();x[1]["continuation_id"]=x[0]["continuation_id"]
        self.assertEqual(audit(x)["key"],"continuation_id")
    def test_unverified_label_fails(self):
        x=sample();x[1]["engine_label_verified"]=False
        self.assertEqual(audit(x)["status"],"HOLD_UNVERIFIED_OR_UNTYPED_SOURCE")
    def test_missing_nearby_group_fails(self):
        x=sample();x[-1]["group"]="negative"
        self.assertEqual(audit(x)["status"],"HOLD_INCOMPLETE_HELDOUT_GROUPS")
    def test_no_heldout_is_not_pass(self):
        x=sample()
        for row in x:row["split"]="support"
        self.assertEqual(audit(x)["status"],"HOLD_NO_HELDOUT")
if __name__=="__main__":unittest.main()
