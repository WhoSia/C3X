import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p9_r17_native_candidate_score_semantics import admit,admit_pair

def row(kind="lower"):
    return {"engine_sha256":"a"*64,"process_id":"cold-1",
        "treatment_arm":"TT1_SEE_FLIP","root_call":3,
        "iteration_depth":12,"aspiration_attempt":1,"candidate_uci":"b1b4",
        "score_pov":"side_to_move","completed":True,"cp":18,"kind":kind,
        "provenance":{"origin":"root_move_store","same_root_window_documented":True,
        "bound_interpretation":"verified_root_candidate_interval",
        "score_pov_verified":True}}
class ScoreEvidence(unittest.TestCase):
    def test_declared_evidence_not_native_pass(self):
        self.assertEqual(admit(row())["status"],"ADMITTED_PROVENANCE_DECLARATION_ONLY")
    def test_no_origin(self):
        x=row();x["provenance"]["origin"]="UCI_terminal_score"
        self.assertEqual(admit(x)["status"],"HOLD_UNKNOWN_SCORE_ORIGIN")
    def test_failsoft_abstention(self):
        x=row();x["provenance"]["bound_interpretation"]="raw_failsoft"
        self.assertEqual(admit(x)["status"],"ABSTAIN_FAILSOFT_BOUND_NOT_CERTIFIED")
    def test_no_window(self):
        x=row();x["provenance"]["same_root_window_documented"]=False
        self.assertEqual(admit(x)["status"],"HOLD_NO_WINDOW_PROVENANCE")
    def test_unfinished(self):
        x=row();x["completed"]=False
        self.assertEqual(admit(x)["status"],"HOLD_UNFINISHED_SEARCH")
    def test_pair_abstains_on_unverified(self):
        x=row();x["provenance"]["score_pov_verified"]=False
        self.assertEqual(admit_pair(x,row())["status"],"ABSTAIN_UNVERIFIED_SCORE_SEMANTICS")
    def test_missing_fields(self):
        x=row();del x["engine_sha256"]
        self.assertEqual(admit(x)["status"],"HOLD_MISSING_FIELDS")
if __name__=="__main__":unittest.main()
