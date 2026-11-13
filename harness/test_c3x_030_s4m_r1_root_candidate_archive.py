import unittest
from c3x_030_s4m_r1_root_candidate_archive import pair_epoch,audit

def rec(i=0,move=42,value=30,old=5,depth=3,alpha=-50,beta=50,count=1):
    return {"ordinal":i,"epoch":1,"root_move_raw":move,"depth":depth,
       "move_count":count,"alpha":alpha,"beta":beta,"value":value,
       "old_best":old,"will_update_best":value>old,
       "will_update_root_pv":count==1 or value>alpha}

def trial(rows,total=None):
    if total is None:total=len(rows)
    return {"root_score_receipts":rows,"root_score_total_at_this_site":total,
            "root_score_right_censored":total>512}

class RootCandidateAlignment(unittest.TestCase):
    def test_single_candidate_value_difference(self):
        x=pair_epoch(trial([rec(value=30)]),trial([rec(value=31)]))
        self.assertEqual(x["unique_singleton_candidate_pairs"],1)
        self.assertEqual(x["different_value_candidates"],1)
        self.assertFalse(x["causal_mediator_identity_proven"])
    def test_same_state_value_invariant(self):
        x=pair_epoch(trial([rec(value=30)]),trial([rec(value=30)]))
        self.assertEqual(x["different_value_candidates"],0)
    def test_repeated_signature_is_ambiguous(self):
        a=trial([rec(i=0),rec(i=1)])
        b=trial([rec(i=0,value=35)])
        x=pair_epoch(a,b)
        self.assertEqual(x["ambiguous_state_signatures"],1)
        self.assertEqual(x["unique_singleton_candidate_pairs"],0)
    def test_unmatched_not_implicitly_null_value(self):
        x=pair_epoch(trial([rec(move=42)]),trial([rec(move=43)]))
        self.assertEqual(x["unique_singleton_candidate_pairs"],0)
        self.assertEqual(x["sham_only_signatures"],1)
        self.assertEqual(x["two_only_signatures"],1)
    def test_cap_reports_unknowns(self):
        xs=[rec(i=i,move=42+i) for i in range(512)]
        result=pair_epoch(trial(xs,total=550),trial(xs,total=520))
        self.assertTrue(result["any_detail_log_censored"])
        self.assertFalse(result["complete_root_search_coverage"])
    def test_forged_root_decision_rejected(self):
        a=rec();a["will_update_best"]=False
        with self.assertRaisesRegex(ValueError,"BAD_SOURCE_PREDICATE"):
            pair_epoch(trial([a]),trial([]))
    def test_forged_ordinal_rejected(self):
        with self.assertRaisesRegex(ValueError,"BROKEN_SOURCE_LOG_ORDINAL"):
            pair_epoch(trial([rec(i=1)]),trial([]))
    def test_archive_sha_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"NOT_THE_ORIGINAL"):
            audit(b'{}')
    def test_missing_events_not_counted_as_matching(self):
        x=pair_epoch(trial([]),trial([]))
        self.assertEqual(x["shared_state_signatures"],0)

if __name__=="__main__": unittest.main()
