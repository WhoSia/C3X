import unittest
from c3x_030_p11f2_risk_coverage_audit import counts,check_manifest,compare,MANIFEST_SCHEMA
from c3x_030_p11f1_evidence_fusion_audit import SCHEMA
def records():
    a=[]
    for i in range(10):
        a.append({"case_id":f"c{i}","game_id":f"g{i}",
          "split":"development" if i<2 else "holdout",
          "fen":f"fen-{i}","history_uci":[f"m{i}"],"label":1 if i%2==0 else 0,
          "sarfa_positive":True,"independent_response_verified":i%2==0,
          "native_event_to_root_certified":None if i%3==0 else i%2==0,
          "original_receipt_sha256":"a"*64})
    data={"schema":SCHEMA,"cases":a,"labels_independent_of_method_generation":True,
          "same_chess_cases_for_all_methods":True,"source_and_judge_engines_distinct":True,
          "holdout_cases_precommitted_before_outcomes":True}
    manifest={"schema":MANIFEST_SCHEMA,"entries":[{"case_id":v["case_id"],"game_id":v["game_id"],
          "fen":v["fen"],"history_uci":v["history_uci"]} for v in a if v["split"]=="holdout"]}
    return data,manifest
class Test(unittest.TestCase):
    def test_case_and_manifest_exact(self):
        data,manifest=records()
        self.assertEqual(len(check_manifest(data,manifest)),8)
    def test_label_in_blind_manifest_refused(self):
        d,m=records();m["entries"][0]["label"]=1
        with self.assertRaisesRegex(ValueError,"OUTCOME_LEAK"):check_manifest(d,m)
    def test_split_game_identity_changes_hold(self):
        d,m=records();m["entries"][0]["game_id"]="changed"
        with self.assertRaisesRegex(ValueError,"MUTATED_FEN_OR_GAME"):check_manifest(d,m)
    def test_history_mutation_hold(self):
        d,m=records();d["cases"][2]["history_uci"]=["other"]
        with self.assertRaisesRegex(ValueError,"MUTATED_HISTORY"):check_manifest(d,m)
    def test_abstentions_not_false_negatives_but_missed_positives(self):
        d,_=records()
        r=counts(d["cases"],"three_gate_fusion")
        self.assertGreater(r["abstain"],0)
        self.assertGreater(r["abstained_true_positives"],0)
        self.assertLess(r["positive_recall_all_cases_including_abstentions_as_missed"],1)
    def test_grouped_pairing_and_superiority_hold(self):
        d,m=records()
        r=compare(d,m,draws=200)
        self.assertEqual(r["n_distinct_holdout_games"],8)
        self.assertTrue(r["no_paper_superiority_claim"])
        self.assertIn("sarfa_only",r["paired_grouped_intervals"])
    def test_missing_cases_hold(self):
        d,m=records();m["entries"].pop()
        with self.assertRaisesRegex(ValueError,"HOLDOUT_CASE_NOT_FROZEN"):compare(d,m)
if __name__=="__main__":unittest.main()
