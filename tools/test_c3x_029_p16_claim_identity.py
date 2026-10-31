import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p16_claim_identity import fingerprint
def case():
    return dict(source_game="g1",root_state_digest="a"*64,side="w",candidate_set=["b1c3","g1f3"],property_id="no_forced_loss",reply_scope="all_legal",horizon_plies=4,ruleset="chess-full-history")
class Identity(unittest.TestCase):
    def test_candidate_order_invariant(self):
        a=case();b=case();b["candidate_set"].reverse()
        self.assertEqual(fingerprint(a),fingerprint(b))
    def test_horizon_changes_target(self):
        a=case();b=case();b["horizon_plies"]=6
        self.assertNotEqual(fingerprint(a),fingerprint(b))
    def test_scope_changes_target(self):
        a=case();b=case();b["reply_scope"]="capture_only"
        self.assertNotEqual(fingerprint(a),fingerprint(b))
    def test_no_single_candidate(self):
        x=case();x["candidate_set"]=["b1c3"]
        with self.assertRaisesRegex(ValueError,"CANDIDATES"):fingerprint(x)
    def test_no_ambiguous_history(self):
        x=case();x["root_state_digest"]=""
        with self.assertRaisesRegex(ValueError,"SOURCE"):fingerprint(x)
if __name__=="__main__":unittest.main()
