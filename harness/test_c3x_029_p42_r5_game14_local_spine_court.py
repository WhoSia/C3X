"""P42/R5 synthetic contract tests; no native engine or legal chess result."""
import unittest
from c3x_029_p42_r5_game14_local_spine_court import adjudicate,parse

FIELDS={"parent64":9876,"child64":12345,"root_call":7,
        "root_move":344,"move":776,"score":0,
        "pre_best":0,"alpha":0,"beta":100}
def line(event,seq,key,*,value=0,best=0,did=0,entered=0,move=776):
    z=dict(FIELDS,event=event,seq=seq,key64=key,score=value,
           pre_best=best,did_move=did,child_entered=entered,move=move)
    return "c3x042_r5 "+" ".join(f"{a}={b}" for a,b in z.items())
def trace(*,adopt=True,score=44,break_score=False,wrong_key=False,
          omit_child=False,wrong_move=False):
    k=12345 if not wrong_key else 66
    a=[line("GUARD_FALLTHROUGH",1,9876)]
    a.append(line("ACTUAL_DO_MOVE",2,12345,did=1))
    if not omit_child:
        a.append(line("MAIN_CHILD_ENTERED",3,k,did=1,entered=1))
    a.append(line("CHILD_RETURNED_TO_PARENT",len(a)+1,12345,
                  value=score,did=1,entered=1))
    a.append(line("PARENT_VALUE_ASSESSED",len(a)+1,9876,
                  value=score+(1 if break_score else 0),best=20,
                  did=1,entered=1,move=99 if wrong_move else 776))
    if adopt:
        a.append(line("PARENT_BESTVALUE_ASSIGNED",len(a)+1,9876,
                      value=score,did=1,entered=1))
    return "\n".join(a)+"\n"

class P42LocalCourt(unittest.TestCase):
    def test_positive_two_cold_replays_local_only(self):
        result=adjudicate(trace()+trace())
        self.assertEqual(result["status"],
                         "LOCAL_EXACT_GUARD_CHILD_PARENT_WITNESS_ONLY")
        self.assertEqual(result["counts"]["parent_assignment"],2)
        self.assertFalse(result["unique_natural_TT_mediation_certified"])
        self.assertFalse(result["full_ancestor_to_unrestricted_root_certified"])
        self.assertFalse(result["source_keys_exposed"])

    def test_bestvalue_adoption_without_alpha_crossing_is_not_a_root_certificate(self):
        # Synthetic: score improves parent bestValue but does not exceed alpha.
        # The original Stockfish source updates bestValue before checking alpha.
        one=trace(score=15).replace("pre_best=20","pre_best=0")
        one=one.replace("alpha=0","alpha=25")
        result=adjudicate(one+one)
        self.assertEqual(result["status"],
                         "LOCAL_EXACT_GUARD_CHILD_PARENT_WITNESS_ONLY")
        self.assertEqual(result["counts"]["parent_assignment"],2)
        self.assertEqual(result["counts"]["bestvalue_only_assignments"],2)
        self.assertEqual(result["counts"]["parent_value_exceeds_alpha"],0)
        self.assertTrue(result["window_relation_is_not_a_certified_exact_score_bound"])
        self.assertFalse(result["full_ancestor_to_unrestricted_root_certified"])

    def test_valid_zero_zobrist_parent_key_is_not_automatically_rejected(self):
        # A 64-bit legal chess position hash has no general nonzero invariant.
        actual=trace().replace("parent64=9876","parent64=0").replace(
            "key64=9876","key64=0")
        result=adjudicate(actual+actual)
        self.assertEqual(result["status"],
                         "LOCAL_EXACT_GUARD_CHILD_PARENT_WITNESS_ONLY")
        self.assertFalse(result["full_ancestor_to_unrestricted_root_certified"])

    def test_valid_zero_zobrist_child_key_is_not_automatically_rejected(self):
        actual=trace().replace("child64=12345","child64=0").replace(
            "key64=12345","key64=0")
        result=adjudicate(actual+actual)
        self.assertEqual(result["status"],
                         "LOCAL_EXACT_GUARD_CHILD_PARENT_WITNESS_ONLY")
        self.assertFalse(result["natural_TT_SEE_mediation_certified"])

    def test_without_real_guard_event_hold(self):
        self.assertIn("HOLD_WRONG_REPLAY_COUNT",adjudicate("")["status"])

    def test_missing_child_entry_hold(self):
        self.assertEqual(adjudicate(trace(omit_child=True)*2)["status"],
                         "HOLD_LOCAL_PATH_INCOMPLETE_OR_REORDERED")

    def test_wrong_child_key_hold(self):
        self.assertEqual(adjudicate(trace(wrong_key=True)*2)["status"],
                         "HOLD_CHILD_KEY_MISMATCH")

    def test_mismatched_returned_score_hold(self):
        self.assertEqual(adjudicate(trace(break_score=True)*2)["status"],
                         "HOLD_RETURNED_SCORE_NOT_ADOPTED_IN_PARENT_CANDIDATE")

    def test_move_identity_drift_hold(self):
        self.assertEqual(adjudicate(trace(wrong_move=True)*2)["status"],
                         "HOLD_EVENT_IDENTITY_DRIFT")

    def test_expected_parent_adoption_missing_hold(self):
        self.assertEqual(adjudicate(trace(adopt=False)*2)["status"],
                         "HOLD_EXPECTED_ADOPTION_EVENT_ABSENT")

    def test_bad_replay_count_hold(self):
        self.assertEqual(adjudicate(trace())["status"],"HOLD_WRONG_REPLAY_COUNT")

    def test_boolean_as_replay_count_invalid(self):
        with self.assertRaises(ValueError):
            adjudicate(trace(),True)

    def test_non_numeric_key_rejected(self):
        with self.assertRaisesRegex(ValueError,"NONNUMERIC"):
            parse(trace().replace("parent64=9876","parent64=garbage"))

    def test_no_ancestor_claim_from_local_witness(self):
        result=adjudicate(trace()*2)
        self.assertNotIn("root_reached",result)
        self.assertFalse(result["actual_chess_value_verified"])

if __name__=="__main__":
    unittest.main()
