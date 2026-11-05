"""P41/R3 synthetic preflight tests. All PASS mean structural-only readiness."""
import copy
import hashlib
import unittest
from c3x_029_p41_r3_independent_plan_court_preflight import digest, verify_case


def fixture():
    moves=["e2e4"]*60  # deliberately NOT a legal PGN: legality is a separate gate
    sha=hashlib.sha256(" ".join(moves).encode()).hexdigest()
    plan={"scope":"ALL_LEGAL","opponent_total":2,"opponent_replies":{
        "r0":{"legal_own_count":4,"plan_own_count":1},
        "r1":{"legal_own_count":8,"plan_own_count":3}}}
    methods={k:{"native_nodes":24000,"legal_expansions":600,"cpu_ms":300,
                "claim_slots":2}
             for k in ("pv","partial_tree_k3","foil_json","c3x")}
    case={"source":{"full_uci":moves,"original_sha256":sha,
                    "game_sha256":sha,"event_family":"new-event"},
          "freeze":{"source_sha256":sha,"plan_spec":plan,
                    "plan_digest":digest(plan),"phase":"PRE_JUDGE",
                    "candidate_uci":["a2a3","b2b3"]},
          "roots":{"24k":["a2a3","b2b3"],"48k":["a2a3","b2b3"],
                   "96k":["a2a3","b2b3"]},
          "judge":{"family":"separate-model-family","state":"NATIVE_VERIFIED",
                   "source_sha256":"s","binary_sha256":"b",
                   "actual_nodes":98000,"required_nodes":96000},
          "predictor_families":["Stockfish16"],"methods":methods,
          "global_budget":{"native_nodes":24000,"legal_expansions":600,"cpu_ms":300}}
    history={"game_sha256":{"old-game"},"event_family":{"old-event"}}
    return case,history


class SourcePlanJudgePreflight(unittest.TestCase):
    def fails(self,case,historical,reason):
        result=verify_case(case,historical)
        self.assertEqual(result["status"],"HOLD")
        self.assertTrue(any(reason in x for x in result["failures"]),result)

    def test_synthetic_structure_only(self):
        case,historical=fixture()
        self.assertEqual(verify_case(case,historical)["status"],
                         "PASS_STRUCTURAL_PREFLIGHT_ONLY")
        self.assertNotIn("CHESS_LEGALITY_VERIFIED",
                         verify_case(case,historical)["status"])

    def test_event_overlap(self):
        a,h=fixture();h["event_family"].add("new-event")
        self.fails(a,h,"EVENT_LEAK")

    def test_game_overlap(self):
        a,h=fixture();h["game_sha256"].add(a["source"]["game_sha256"])
        self.fails(a,h,"GAME_LEAK")

    def test_forged_duplicate_identity_not_derived_from_game_is_rejected(self):
        a,h=fixture()
        a["source"]["game_sha256"]="fake-unseen"
        self.fails(a,h,"GAME_ID_NOT_FULL_UCI_SHA")

    def test_plan_after_judge(self):
        a,h=fixture();a["freeze"]["phase"]="AFTER_JUDGE"
        self.fails(a,h,"POSTHOC_PLAN")

    def test_plan_digest_tamper(self):
        a,h=fixture();a["freeze"]["plan_spec"]["opponent_replies"]["r0"]["plan_own_count"]=2
        self.fails(a,h,"PLAN_DIGEST")

    def test_partial_scope_cannot_claim_all(self):
        a,h=fixture();a["freeze"]["plan_spec"]["opponent_total"]=3
        a["freeze"]["plan_digest"]=digest(a["freeze"]["plan_spec"])
        self.fails(a,h,"FALSE_UNIVERSAL_COVERAGE")

    def test_all_legal_trivial_plan(self):
        a,h=fixture();a["freeze"]["plan_spec"]["opponent_replies"]["r0"]["plan_own_count"]=4
        a["freeze"]["plan_digest"]=digest(a["freeze"]["plan_spec"])
        self.fails(a,h,"TRIVIAL_ALL_LEGAL")

    def test_slightly_selective_plan_insufficient(self):
        a,h=fixture();a["freeze"]["plan_spec"]["opponent_replies"]["r0"]["plan_own_count"]=3
        a["freeze"]["plan_digest"]=digest(a["freeze"]["plan_spec"])
        self.fails(a,h,"NO_SELECTIVITY")

    def test_judge_same_family(self):
        a,h=fixture();a["judge"]["family"]="Stockfish16"
        self.fails(a,h,"SAME_FAMILY_JUDGE")

    def test_judge_actual_nodes_too_low(self):
        a,h=fixture();a["judge"]["actual_nodes"]=999
        self.fails(a,h,"UNDERBUDGET_JUDGE")

    def test_partial_tree_rival_mandatory(self):
        a,h=fixture();del a["methods"]["partial_tree_k3"]
        self.fails(a,h,"MISSING_BASELINE_partial_tree_k3")

    def test_cost_and_output_cap(self):
        a,h=fixture()
        a["methods"]["c3x"]["legal_expansions"]=900
        a["methods"]["c3x"]["claim_slots"]=5
        self.fails(a,h,"GLOBAL_BUDGET_legal_expansions")
        self.fails(a,h,"OUTPUT_BUDGET")

    def test_drift_in_top_two(self):
        a,h=fixture();a["roots"]["96k"]=["a2a3","c2c3"]
        self.fails(a,h,"CANDIDATE_DRIFT")


if __name__=="__main__":
    unittest.main()
