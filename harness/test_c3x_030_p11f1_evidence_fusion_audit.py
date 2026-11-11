import unittest
from c3x_030_p11f1_evidence_fusion_audit import evaluate,decide,SCHEMA
def sample():
    cases=[]
    vals=[(1,True,True,True),(0,True,False,False),(1,True,True,None),
          (0,False,False,False),(1,True,True,True),(0,True,True,False)]
    for i,(label,a,b,c) in enumerate(vals):
        cases.append({"case_id":"c"+str(i),"game_id":"g"+str(i),
             "split":"development" if i<3 else "holdout",
             "fen":"valid-source-fen-identity-"+str(i),"label":label,
             "sarfa_positive":a,"independent_response_verified":b,
             "native_event_to_root_certified":c,
             "original_receipt_sha256":"a"*64})
    return {"schema":SCHEMA,"cases":cases,
        "labels_independent_of_method_generation":True,
        "same_chess_cases_for_all_methods":True,
        "source_and_judge_engines_distinct":True,
        "holdout_cases_precommitted_before_outcomes":True}
class Cases(unittest.TestCase):
    def test_unknown_triple_abstains(self):
        x=sample()["cases"][2];self.assertIsNone(decide(x,"three_gate_fusion"))
        self.assertTrue(decide(x,"sarfa_only"))
    def test_comparison_does_not_claim_superiority(self):
        x=evaluate(sample());self.assertTrue(x["no_superiority_or_significance_claim"])
        self.assertEqual(x["metrics_by_split"]["holdout"]["three_gate_fusion"]["distinct_games"],3)
    def test_split_leakage_rejected(self):
        x=sample();x["cases"][3]["game_id"]="g1"
        with self.assertRaisesRegex(ValueError,"SAME_GAME"):evaluate(x)
    def test_unfrozen_holdout_rejected(self):
        x=sample();x["holdout_cases_precommitted_before_outcomes"]=False
        with self.assertRaisesRegex(ValueError,"HOLDOUT_NOT_PRECOMMITTED"):evaluate(x)
    def test_missing_sha_rejected(self):
        x=sample();x["cases"][0].pop("original_receipt_sha256")
        with self.assertRaisesRegex(ValueError,"MISSING_RAW_EVIDENCE_SHA"):evaluate(x)
    def test_false_evidence_is_not_unknown(self):
        x=sample()["cases"][1];self.assertFalse(decide(x,"three_gate_fusion"))
    def test_no_independent_judge_rejected(self):
        x=sample();x["source_and_judge_engines_distinct"]=False
        with self.assertRaisesRegex(ValueError,"SOURCE_JUDGE_LEAK"):evaluate(x)
if __name__=="__main__":unittest.main()
