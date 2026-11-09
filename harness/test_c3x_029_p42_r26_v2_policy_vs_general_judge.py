"""R26-V2 source/judge join contracts. Synthetic mocks are not native evidence."""
import unittest
from unittest.mock import patch
import chess

from c3x_029_p42_r26_v2_policy_vs_general_judge import (
    validate, V1_SCHEMA, R25_SCHEMA)
from c3x_029_p42_r24_independent_frozen_own_plan_judge import FROZEN_PLAN_SHA
from c3x_029_p42_r25_e2_k3_full_reply_coverage import B2_SHA


def fixture():
    board = chess.Board()
    child = board.copy(stack=True)
    child.push_uci("e2e4")
    replies = sorted(x.uci() for x in child.legal_moves)
    selected = ["e7e5", "c7c5", "e7e6"]
    own = "g1f3"
    frozen_rows = [
        {"opponent_reply": reply, "own_uci": own}
        for reply in replies]
    worlds = [({"case_id": "synthetic", "event_family": "unit"}, board,
               [{"root": "e2e4", "replies": replies}])]
    prepared = [({"case_id": "synthetic", "event_family": "unit"}, board,
                 [({"root": "e2e4", "replies": replies}, frozen_rows)])]
    v1 = {"schema": V1_SCHEMA,
          "status": "SOURCE_ONLY_V1_BEFORE_ANY_R26_BERSERK",
          "reference_judge_ever_consulted_for_selection": False,
          "original_R24_prejudge_policy_sha256": FROZEN_PLAN_SHA,
          "cases": [{"case_id": "synthetic", "event_family": "unit",
                     "roots": [{"root_uci": "e2e4",
                                "legal_first_opponent_replies": len(replies),
                                "ranked_policy_stress_top3": [
                                    {"opponent_reply": name, "frozen_own_move": own,
                                     "stress_rank": i + 1,
                                     "source_policy_stress_cp": -30 + i}
                                    for i, name in enumerate(selected)]}]}]}
    r25 = {"schema": R25_SCHEMA, "R24_B2_aggregate_sha256": B2_SHA,
           "cases": [{"case_id": "synthetic", "event_family": "unit",
                      "roots": [{"root_uci": "e2e4", "ranked_k3_replies": [
                          {"opponent_reply": reply, "frozen_own_move": own,
                           "depths": {}} for reply in replies[:3]]}]}]}
    b2 = {"prejudge_plan_sha256": FROZEN_PLAN_SHA,
          "cases": [{"case_id": "synthetic", "event_family": "unit",
                     "roots": [{"root_uci": "e2e4",
                                "source_legal_reply_count": len(replies)}]}]}
    return v1, r25, b2, worlds, prepared


class R26JoinContract(unittest.TestCase):
    def test_matching_source_and_native_cache(self):
        a, b, c, w, prepared = fixture()
        with patch("c3x_029_p42_r26_v2_policy_vs_general_judge.source_policy",
                   return_value=prepared):
            self.assertEqual(len(validate(a, b, c, w, {})), 1)

    def test_reject_referee_leakage(self):
        a, b, c, w, prepared = fixture()
        a["reference_judge_ever_consulted_for_selection"] = True
        with self.assertRaisesRegex(ValueError, "CUSTODY"):
            validate(a, b, c, w, {})

    def test_reject_frozen_own_action_drift(self):
        a, b, c, w, prepared = fixture()
        a["cases"][0]["roots"][0]["ranked_policy_stress_top3"][0][
            "frozen_own_move"] = "e7e5"
        with patch("c3x_029_p42_r26_v2_policy_vs_general_judge.source_policy",
                   return_value=prepared):
            with self.assertRaisesRegex(ValueError, "DRIFT_OR_ILLEGAL"):
                validate(a, b, c, w, {})

    def test_reject_incomplete_original_support(self):
        a, b, c, w, prepared = fixture()
        c["cases"][0]["roots"][0]["source_legal_reply_count"] = 2
        with patch("c3x_029_p42_r26_v2_policy_vs_general_judge.source_policy",
                   return_value=prepared):
            with self.assertRaisesRegex(ValueError, "ROOT_IDENTITY"):
                validate(a, b, c, w, {})


if __name__ == "__main__":
    unittest.main()
