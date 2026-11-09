#!/usr/bin/env python3
"""C3X P42/R25-E1: source-ranked first opponent layer, before any referee read.

This is the genuine engine-ranked k=3 *first opponent layer* of a Cui-style
partial strategy tree, not the full multi-ply Cui tree or a validated strategy.
Reuses R24's frozen all-reply source own policy rather than rerunning 147 queries.
Reference adjudication is deliberately absent from imports and CLI.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine
from c3x_029_p38_r1_ethereal_independent_referee import (
    authentic_archive, authentic_cases, SOURCE_ZIP_SHA, SOURCE_MEMBER,
    SOURCE_JSON_SHA, PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA,
)
from c3x_029_p42_r23_independent_all_opponent_reply_value_court import (
    FROZEN_EXPLORATORY_CASES, source_positions,
)
from c3x_029_p42_r24_independent_frozen_own_plan_judge import (
    FROZEN_PLAN_SHA, source_policy,
)

SF_COMMIT = "68e1e9b3811e16cad014b590d7443b9063b3eb52"
K = 3
DEPTH = 12


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rank_opponent(board, eng, k=K, depth=DEPTH):
    """Only engine-ranked legal replies; reject missing/duplicate/short search."""
    legal = {m.uci() for m in board.legal_moves}
    if board.is_game_over(claim_draw=False) or not legal:
        raise ValueError("R25_HOLD_TERMINAL_OPPONENT_POSITION")
    n = min(k, len(legal))
    raw = eng.analyse(board, chess.engine.Limit(depth=depth), multipv=n,
                      game=object(), info=chess.engine.INFO_ALL)
    if not isinstance(raw, list) or len(raw) != n:
        raise ValueError("R25_HOLD_INCOMPLETE_ENGINE_MULTIPV")
    selected = []
    for rank, info in enumerate(raw, 1):
        pv = info.get("pv")
        if (type(info.get("depth")) is not int or info["depth"] < depth
            or type(info.get("nodes")) is not int or info["nodes"] <= 0
            or not isinstance(pv, list) or not pv
            or not isinstance(pv[0], chess.Move) or pv[0].uci() not in legal):
            raise ValueError("R25_HOLD_BAD_ENGINE_RANK_OR_SEARCH")
        move = pv[0].uci()
        if move in {x["opponent_reply"] for x in selected}:
            raise ValueError("R25_HOLD_DUPLICATE_MULTIPV_MOVE")
        selected.append({"opponent_reply": move, "engine_rank": rank,
                         "ranking_nodes": info["nodes"],
                         "ranking_depth": info["depth"]})
    return selected


def freeze_first_layer(worlds, prejudge, eng):
    verified = source_policy(worlds, prejudge)
    out = []
    for source, board, roots in verified:
        output_roots = []
        for pair, frozen_rows in roots:
            opponent_board = board.copy(stack=True)
            opponent_board.push_uci(pair["root"])
            ranking = rank_opponent(opponent_board, eng)
            full_reply_set = set(pair["replies"])
            own_by_reply = {x["opponent_reply"]: x for x in frozen_rows}
            if len(own_by_reply) != len(frozen_rows):
                raise ValueError("R25_HOLD_DUPLICATE_SOURCE_POLICY_REPLY")
            if set(own_by_reply) != full_reply_set:
                raise ValueError("R25_HOLD_SOURCE_FULL_REPLY_UNIVERSE")
            for item in ranking:
                reply = item["opponent_reply"]
                if reply not in own_by_reply:
                    raise ValueError("R25_HOLD_RANK_NOT_IN_FROZEN_UNIVERSE")
                own = own_by_reply[reply]
                item["frozen_source_own_move"] = own["own_uci"]
                item["frozen_source_own_nodes"] = own["source_nodes"]
            output_roots.append({
                "root_uci": pair["root"],
                "legal_first_opponent_replies": len(pair["replies"]),
                "ranked_replies": ranking,
                "engine_rank_query_nodes": sum(x["ranking_nodes"] for x in ranking),
                "nodes_accounting_note": "MultiPV info nodes can be cumulative; sum is NOT physical query cost.",
            })
        out.append({"case_id": source["case_id"], "event_family": source["event_family"],
                    "roots": output_roots})
    return {
        "schema": "c3x042-r25-e1-source-ranked-first-layer-k3-v1",
        "status": "SOURCE_ONLY_BEFORE_ANY_R25_REFEREE_ADJUDICATION",
        "original_R24_frozen_147_policy_sha256": FROZEN_PLAN_SHA,
        "source_commit": SF_COMMIT, "use_nnue": False,
        "opponent_ranking_depth": DEPTH, "k_strat": K,
        "engine_ranking_not_lexicographic": True,
        "first_opponent_layer_only_not_full_Cui_tree": True,
        "R24_historical_cases_postselected": True,
        "independent_referee_consulted_for_ranking": False,
        "full_opponent_reply_coverage_claim": False,
        "cost_equivalence_claim": False,
        "causal_explanation_claim": False,
        "cases": out,
    }


def main():
    parser = argparse.ArgumentParser()
    for arg in ("source", "predictions", "frozen-plan", "engine", "out"):
        parser.add_argument("--" + arg, required=True)
    args = parser.parse_args()
    if digest(args.frozen_plan) != FROZEN_PLAN_SHA:
        raise ValueError("R25_HOLD_R24_PREJUDGE_PLAN_SHA_DRIFT")
    originals = authentic_cases(
        authentic_archive(Path(args.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(args.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    worlds = source_positions(originals, FROZEN_EXPLORATORY_CASES)
    frozen = json.loads(Path(args.frozen_plan).read_text(encoding="utf-8"))
    with chess.engine.SimpleEngine.popen_uci(args.engine, timeout=180) as eng:
        if ("stockfish" not in eng.id.get("name", "").lower()
            or not {"Threads", "Hash", "Use NNUE"}.issubset(eng.options)):
            raise ValueError("R25_HOLD_SOURCE_ENGINE_ID_OR_OPTIONS")
        eng.configure({"Threads": 1, "Hash": 16, "Use NNUE": False})
        result = freeze_first_layer(worlds, frozen, eng)
    if (len(result["cases"]) != 2
        or sum(len(c["roots"]) for c in result["cases"]) != 4
        or sum(len(r["ranked_replies"]) for c in result["cases"]
               for r in c["roots"]) != 12):
        raise ValueError("R25_HOLD_EXPECTED_EXPLORATORY_SUPPORT")
    result["binary_sha256"] = digest(args.engine)
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R25_ENGINE_RANKED_FIRST_OPPONENT_LAYER_FROZEN", 12,
          "NO_REFEREE_NO_FULL_TREE_NO_STRATEGY_CLAIM")


if __name__ == "__main__":
    main()
