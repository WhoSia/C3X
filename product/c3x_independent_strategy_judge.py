#!/usr/bin/env python3
"""P4-B: independent Berserk judge of SHA-frozen source-Cui strategy leaves.

FIRST freeze P4-A source native Stockfish-only tree JSON SHA from an already
COMPLETED workflow. THEN accept that exact source hash and use a *different*
pinned Berserk14 family to evaluate all eight legal 5-ply histories at two
depths. The independent judge NEVER selects/changes the source opponent
tree. No literal 'worst case' over untested replies; only sampled k2^2.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

from c3x_recursive_strategy import SCHEMA as SOURCE_SCHEMA

SCHEMA="c3x030-p4b-frozen-source-cui-independent-berserk-leaf-judge-v1"
FAMILY_COMMIT="8ae895a6151695be4a50d4fb65b0c131659c513a"
NET_SHA="9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084"
DEPTHS=(10,12)


def digest(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()


def reconstruct(data):
    if (data.get("schema")!=SOURCE_SCHEMA
        or data.get("same_engine_not_independent_judge") is not True
        or data.get("not_source_chess_root_causal_intervention") is not True
        or len(data.get("roots",[]))!=2
        or data.get("total_leaf_paths")!=8):
        raise ValueError("P4B_HOLD_SOURCE_FROZEN_CUSTODY")
    root_board=chess.Board(data["fen"])
    if not root_board.is_valid() or root_board.is_game_over(claim_draw=False):
        raise ValueError("P4B_HOLD_FEN_BAD")
    observed=[]
    for root in data["roots"]:
        uc=root.get("root_uci")
        if (root.get("opponent_layers")!=2 or root.get("source_opponent_k")!=2
            or root.get("source_depth")!=8 or root.get("leaf_count")!=4
            or len(root.get("leaf_paths",[]))!=4):
            raise ValueError("P4B_HOLD_SOURCE_DEPTH_BRANCH_STRUCTURE")
        if chess.Move.from_uci(uc) not in root_board.legal_moves:
            raise ValueError("P4B_HOLD_ROOT_ILLEGAL")
        first=root.get("tree")
        if len(first)!=2 or {r.get("opponent_rank_1based") for r in first}!={1,2}:
            raise ValueError("P4B_HOLD_FIRST_OPPONENT_RANK")
        tree_paths=[]
        for branch in first:
            if len(branch.get("next_opponent_replies",[]))!=2:
                raise ValueError("P4B_HOLD_SECOND_OPPONENT_COUNT")
            for second in branch["next_opponent_replies"]:
                if second.get("opponent_rank_1based") not in (1,2):
                    raise ValueError("P4B_HOLD_SECOND_RANK")
                trace=[uc,branch["opponent_move"]["action_uci"],
                       branch["own_best_move_or_null"]["action_uci"],
                       second["opponent_move"]["action_uci"],
                       second["own_best_move_or_null"]["action_uci"]]
                if trace!=second.get("trace_uci"):
                    raise ValueError("P4B_HOLD_BRANCH_PATH_DISAGREEMENT")
                tree_paths.append(tuple(trace))
        if len(set(tree_paths))!=4 or set(tree_paths)!={
                tuple(x["trace_uci"]) for x in root["leaf_paths"]}:
            raise ValueError("P4B_HOLD_TREE_LEAF_FABRICATION")
        leaves=[]
        for path in tree_paths:
            board=root_board.copy(stack=True)
            for u in path:
                mv=chess.Move.from_uci(u)
                if mv not in board.legal_moves:
                    raise ValueError("P4B_HOLD_SOURCE_PATH_ILLEGAL")
                board.push(mv)
            if board.is_game_over(claim_draw=False):
                raise ValueError("P4B_HOLD_UNEXPECTED_TERMINAL_LEAF")
            leaves.append({"path_uci":list(path),"board":board})
        observed.append({"root_uci":uc,"root_mover":root_board.turn,"leaves":leaves})
    if len({r["root_uci"] for r in observed})!=2:
        raise ValueError("P4B_HOLD_TWO_DIFFERENT_ROOTS")
    return observed


def judge(verified,engine):
    judged=[]
    for root in verified:
        rows=[]
        for leaf in root["leaves"]:
            depths={}
            for depth in DEPTHS:
                info=engine.analyse(leaf["board"],chess.engine.Limit(depth=depth),
                                    game=object(),info=chess.engine.INFO_ALL)
                if (type(info.get("depth")) is not int or info["depth"]<depth
                    or type(info.get("nodes")) is not int or info["nodes"]<=0
                    or not info.get("pv") or info.get("score") is None):
                    raise ValueError("P4B_HOLD_INDEPENDENT_JUDGE_DEPTH_NODES")
                if info["pv"][0] not in leaf["board"].legal_moves:
                    raise ValueError("P4B_HOLD_JUDGE_ILLEGAL_PV")
                cp=info["score"].pov(root["root_mover"]).score()
                if cp is None:
                    raise ValueError("P4B_HOLD_MATE_NOT_CP_COMPARABLE")
                depths[str(depth)]={"root_mover_cp":cp,
                                   "actual_nodes":info["nodes"],
                                   "pv_first_uci":info["pv"][0].uci()}
            rows.append({"path_uci":leaf["path_uci"],"scores":depths})
        summary={}
        for depth in DEPTHS:
            key=str(depth)
            vals=[r["scores"][key]["root_mover_cp"] for r in rows]
            summary[key]={
                "min_over_only_four_source_selected_paths_cp":min(vals),
                "max_over_only_four_source_selected_paths_cp":max(vals),
                "span_across_only_four_paths_cp":max(vals)-min(vals),
                "actual_independent_nodes":sum(r["scores"][key]["actual_nodes"] for r in rows),
            }
        judged.append({"root_uci":root["root_uci"],
                       "independent_leaf_scores":rows,"depth_summaries":summary})
    return {"schema":SCHEMA,"status":"SOURCE_SHA_LOCKED_INDEPENDENT_BERSERK_JUDGE",
            "independent_engine_family":"Berserk14",
            "berserk_commit":FAMILY_COMMIT,"nnue_sha256":NET_SHA,
            "depths":list(DEPTHS),
            "independent_search_count":sum(len(x["independent_leaf_scores"])*len(DEPTHS)
                                           for x in judged),
            "source_selected_replies_unchanged_by_referee":True,
            "full_opponent_universe_judged":False,
            "source_engine_actual_causal_decision_proven":False,
            "roots":judged}


def main():
    p=argparse.ArgumentParser()
    for x in ("source-tree","source-sha","berserk","nnue","out"):
        p.add_argument("--"+x,required=True)
    a=p.parse_args()
    if len(a.source_sha)!=64 or any(x not in "0123456789abcdef" for x in a.source_sha):
        raise ValueError("P4B_HOLD_SOURCE_SHA_FORMAT")
    if digest(a.source_tree)!=a.source_sha or digest(a.nnue)!=NET_SHA:
        raise ValueError("P4B_HOLD_SOURCE_OR_NNUE_RAW_SHA")
    src=json.loads(Path(a.source_tree).read_text(encoding="utf-8"))
    leaves=reconstruct(src)
    with chess.engine.SimpleEngine.popen_uci(a.berserk,timeout=120) as eng:
        if "berserk" not in eng.id.get("name","").lower() or not {"Threads","Hash"}.issubset(eng.options):
            raise ValueError("P4B_HOLD_NOT_BERSERK")
        eng.configure({"Threads":1,"Hash":16})
        data=judge(leaves,eng)
    if data["independent_search_count"]!=16:
        raise ValueError("P4B_HOLD_EXPECTED_SIXTEEN_SEARCHES")
    data["source_tree_sha256"]=a.source_sha
    data["berserk_binary_sha256"]=digest(a.berserk)
    path=Path(a.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    for row in data["roots"]:
        print("C3X_P4B_ACTUAL_BERSERK_SOURCE_CONDITIONAL_RANGE",
              row["root_uci"],row["depth_summaries"],flush=True)
    print("C3X_P4B_SOURCE_LOCKED_REAL_JUDGE_SHA",digest(path))


if __name__=="__main__":
    main()
