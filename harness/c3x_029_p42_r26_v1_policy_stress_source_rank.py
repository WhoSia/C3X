#!/usr/bin/env python3
"""C3X P42/R26-V1: source-only policy-conditioned opponent vulnerability ranking.

For each already R24 PRE-JUDGE frozen own policy u_S(s,m,r), search after
s,m,r,u_S using pinned original Stockfish16 (NNUE OFF). Rank all legal
opponent first replies by estimated source score from original root-mover POV,
ascending. Never consult independent Berserk, R25-E2 scores, or test outcomes.
This is a cheap exploratory 1-step post-policy stress proxy, NOT a recursive
Cui tree or native causal attribution. Historic cases were postselected.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

from c3x_029_p38_r1_ethereal_independent_referee import (
    authentic_archive, authentic_cases, SOURCE_ZIP_SHA, SOURCE_MEMBER,
    SOURCE_JSON_SHA, PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA)
from c3x_029_p42_r23_independent_all_opponent_reply_value_court import (
    FROZEN_EXPLORATORY_CASES, source_positions)
from c3x_029_p42_r24_independent_frozen_own_plan_judge import (
    FROZEN_PLAN_SHA, source_policy)

SF_COMMIT = "68e1e9b3811e16cad014b590d7443b9063b3eb52"
DEPTH = 12
K = 3
SCHEMA = "c3x042-r26-v1-source-policy-conditioned-stress-top3-v1"


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def score_after_frozen_own(board_after_own, root_mover, eng, depth=DEPTH):
    """Only admit finite, exact UCI search estimates; refuse bounds and mates."""
    if board_after_own.is_game_over(claim_draw=False):
        raise ValueError("R26_HOLD_TERMINAL_AFTER_FROZEN_OWN")
    info = eng.analyse(board_after_own, chess.engine.Limit(depth=depth),
                       game=object(), info=chess.engine.INFO_ALL)
    d, nodes, value = info.get("depth"), info.get("nodes"), info.get("score")
    if (type(d) is not int or d < depth
        or type(nodes) is not int or nodes <= 0
        or value is None or info.get("lowerbound") or info.get("upperbound")):
        raise ValueError("R26_HOLD_SOURCE_SEARCH_OR_BOUND")
    perspective = value.pov(root_mover)
    if perspective.is_mate() or type(perspective.score()) is not int:
        raise ValueError("R26_HOLD_MATE_NOT_COMPARABLE_CP")
    pv = info.get("pv")
    if not isinstance(pv, list) or not pv or pv[0] not in board_after_own.legal_moves:
        raise ValueError("R26_HOLD_SOURCE_PV_ILLEGAL")
    return {"source_policy_stress_cp": perspective.score(),
            "stress_search_nodes": nodes, "stress_search_depth": d}


def source_rank(worlds, frozen, eng):
    verified = source_policy(worlds, frozen)
    cases = []
    for source, board, roots in verified:
        candidate_rows = []
        for pair, own_policy in roots:
            child = board.copy(stack=True)
            child.push_uci(pair["root"])
            ranked = []
            all_reply = set(pair["replies"])
            if len(all_reply) != len(pair["replies"]):
                raise ValueError("R26_HOLD_DUPLICATE_FULL_REPLY")
            if [x["opponent_reply"] for x in own_policy] != pair["replies"]:
                raise ValueError("R26_HOLD_R24_PREJUDGE_OWN_POLICY_DRIFT")
            for row in own_policy:
                reply = row["opponent_reply"]
                after = child.copy(stack=True)
                after.push_uci(reply)
                own = chess.Move.from_uci(row["own_uci"])
                if own not in after.legal_moves:
                    raise ValueError("R26_HOLD_PREJUDGE_OWN_ILLEGAL")
                after.push(own)
                assessment = score_after_frozen_own(after, board.turn, eng)
                ranked.append({"opponent_reply": reply, "frozen_own_move": own.uci(),
                               **assessment})
            if set(x["opponent_reply"] for x in ranked) != all_reply:
                raise ValueError("R26_HOLD_NO_FULL_SOURCE_RANKING")
            ranking = sorted(ranked, key=lambda x: (x["source_policy_stress_cp"],
                                                     x["opponent_reply"]))
            candidate_rows.append({
                "root_uci": pair["root"],
                "legal_first_opponent_replies": len(ranked),
                "stress_searches": len(ranked),
                "stress_search_nodes_total": sum(x["stress_search_nodes"] for x in ranked),
                "ranked_policy_stress_top3": [
                    {"opponent_reply": x["opponent_reply"],
                     "source_policy_stress_cp": x["source_policy_stress_cp"],
                     "frozen_own_move": x["frozen_own_move"],
                     "stress_rank": i + 1}
                    for i, x in enumerate(ranking[:K])],
                # Full 147 ranking stored only in ephemeral private runner memory.
                # No 147 individual scores publicly released.
            })
        cases.append({"case_id": source["case_id"],
                      "event_family": source["event_family"], "roots": candidate_rows})
    return {
        "schema": SCHEMA, "status": "SOURCE_ONLY_V1_BEFORE_ANY_R26_BERSERK",
        "original_R24_prejudge_policy_sha256": FROZEN_PLAN_SHA,
        "source_commit": SF_COMMIT, "use_nnue": False,
        "policy_stress_depth": DEPTH, "top_k": K,
        "ranking_criterion": "ascending original-root-mover source cp after frozen own move",
        "reference_judge_ever_consulted_for_selection": False,
        "R25_outcomes_informed_hypothesis": True,
        "historical_cases_postselected": True,
        "not_full_Cui_or_causal_C3X": True,
        "source_scores_not_reference_chess_truth": True,
        "cases": cases
    }


def main():
    p = argparse.ArgumentParser()
    for a in ("source", "predictions", "frozen-plan", "engine", "out"):
        p.add_argument("--" + a, required=True)
    args = p.parse_args()
    if digest(args.frozen_plan) != FROZEN_PLAN_SHA:
        raise ValueError("R26_HOLD_R24_PREJUDGE_SOURCE_SHA")
    original = authentic_cases(
        authentic_archive(Path(args.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(args.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    worlds = source_positions(original, FROZEN_EXPLORATORY_CASES)
    frozen = json.loads(Path(args.frozen_plan).read_text(encoding="utf-8"))
    with chess.engine.SimpleEngine.popen_uci(args.engine, timeout=180) as eng:
        if ("stockfish" not in eng.id.get("name", "").lower()
            or not {"Threads", "Hash", "Use NNUE"}.issubset(eng.options)):
            raise ValueError("R26_HOLD_SOURCE_ID")
        eng.configure({"Threads": 1, "Hash": 16, "Use NNUE": False})
        result = source_rank(worlds, frozen, eng)
    total = sum(r["stress_searches"] for c in result["cases"] for r in c["roots"])
    selected = sum(len(r["ranked_policy_stress_top3"]) for c in result["cases"]
                   for r in c["roots"])
    if (total, selected) != (147, 12):
        raise ValueError("R26_HOLD_SOURCE_147_OR_TOP12_COVERAGE")
    result["source_stress_search_count"] = total
    result["source_stress_nodes_total"] = sum(
        r["stress_search_nodes_total"] for c in result["cases"] for r in c["roots"])
    result["source_binary_sha256"] = digest(args.engine)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R26_V1_SOURCE_ONLY_STRESS_RANKED_147_ALL_REPLIES_12_SELECTED",
          result["source_stress_nodes_total"], flush=True)


if __name__ == "__main__":
    main()
