#!/usr/bin/env python3
"""C3X 0.30/P4-A: executable Cui §4.1 opponent-ranked, own-best 2-layer tree.

This is a generic-position PRODUCT ADAPTATION of the previously measured
C3X 0.29/R27 `harness/c3x_029_p42_r27_cui_recursive_k3_tree.py`,
not new prior-art novelty and NOT a full Cui verbalization/TEPP benchmark.

At each node where it is opponent's turn, retain up to k original engine
top-ranked legal actions. At each resulting node where it is the root
player's turn, compute the engine's one best legal response, and recurse
once more. A terminal board is an explicit leaf (no invented moves).

The source Stockfish selects all nodes. A future DIFFERENT independent
engine may value preselected leaves, but must not alter source selection.
No worst-case-of-all-replies claim. No original search decision causality.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

from c3x_explain_two_moves import ENGINE_GIT_COMMIT, verify_board_and_pair
from c3x_concept_contrast import CCC_DRIVE

SCHEMA="c3x030-p4a-cui-inspired-two-opponent-layer-product-tree-v1"
CUI_DRIVE="https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view"
MAX_K=3
MAX_DEPTH=12


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_info(info, board, depth):
    pv=info.get("pv")
    nodes=info.get("nodes")
    if (not isinstance(pv,list) or not pv or pv[0] not in board.legal_moves
        or type(info.get("depth")) is not int or info["depth"] < depth
        or type(nodes) is not int or nodes<=0 or info.get("score") is None):
        raise ValueError("P4_HOLD_SOURCE_NATIVE_DEPTH_NODES_LEGAL_PV")
    return {"action_uci":pv[0].uci(),"action_san":board.san(pv[0]),
            "depth":info["depth"],"nodes":nodes}


def opponent_ranked(board,engine,k,depth):
    if board.is_game_over(claim_draw=False):
        return []
    num=min(k,board.legal_moves.count())
    infos=engine.analyse(board,chess.engine.Limit(depth=depth),
                         multipv=num,game=object(),info=chess.engine.INFO_ALL)
    if isinstance(infos,dict): infos=[infos]
    if len(infos)!=num:
        raise ValueError("P4_HOLD_MULTIPV_INCOMPLETE")
    candidates=[source_info(info,board,depth) for info in infos]
    if len(set(x["action_uci"] for x in candidates))!=num:
        raise ValueError("P4_HOLD_DUPLICATE_OPPONENT_ACTION")
    return candidates


def player_best(board,engine,depth):
    if board.is_game_over(claim_draw=False):
        return None
    info=engine.analyse(board,chess.engine.Limit(depth=depth),
                        game=object(),info=chess.engine.INFO_ALL)
    return source_info(info,board,depth)


def tree_for_root(board,move,engine,k=2,depth=8):
    if type(k) is not int or not 1<=k<=MAX_K:
        raise ValueError("P4_HOLD_K_BOUNDS")
    if type(depth) is not int or not 4<=depth<=MAX_DEPTH:
        raise ValueError("P4_HOLD_DEPTH_BOUNDS")
    if not board.is_valid() or move not in board.legal_moves:
        raise ValueError("P4_HOLD_ILLEGAL_ROOT")
    firstboard=board.copy(stack=True)
    firstboard.push(move)
    root_san=board.san(move)
    ledger={"opponent_queries":0,"player_queries":0,
            "opponent_multipv_nodes_estimate":0,"player_nodes":0}
    def opponent_layer(position,remaining,trace):
        if position.is_game_over(claim_draw=False):
            return [{"terminal":True,"trace_uci":trace,
                     "terminal_result":position.result(claim_draw=False)}]
        ranked=opponent_ranked(position,engine,k,depth)
        ledger["opponent_queries"]+=1
        ledger["opponent_multipv_nodes_estimate"]+=max(x["nodes"] for x in ranked)
        branches=[]
        for rank,move_record in enumerate(ranked,1):
            opponent=chess.Move.from_uci(move_record["action_uci"])
            after_opp=position.copy(stack=True)
            after_opp.push(opponent)
            ours=player_best(after_opp,engine,depth)
            if ours is not None:
                ledger["player_queries"]+=1
                ledger["player_nodes"]+=ours["nodes"]
            after_own=after_opp.copy(stack=True)
            if ours is not None:
                after_own.push_uci(ours["action_uci"])
            next_trace=trace+[move_record["action_uci"]]+(
                [] if ours is None else [ours["action_uci"]])
            branch={
                "terminal":False,
                "opponent_rank_1based":rank,
                "opponent_move":move_record,
                "own_best_move_or_null":ours,
                "trace_uci":next_trace,
                "next_opponent_replies":[],
                "terminal_after_own_move":after_own.is_game_over(claim_draw=False)
            }
            if remaining>1:
                branch["next_opponent_replies"]=opponent_layer(
                    after_own,remaining-1,next_trace)
            branches.append(branch)
        return branches
    branches=opponent_layer(firstboard,2,[move.uci()])
    leaves=[]
    def collect(node):
        if node["terminal"]:
            leaves.append({"trace_uci":node["trace_uci"],
                           "terminal_result":node["terminal_result"]})
        elif node["next_opponent_replies"]:
            for child in node["next_opponent_replies"]:collect(child)
        else:
            leaves.append({"trace_uci":node["trace_uci"],
                "terminal_result":None})
    for b in branches: collect(b)
    if not leaves:
        raise ValueError("P4_HOLD_EMPTY_TREE")
    if len(leaves)>k*k:
        raise ValueError("P4_HOLD_TREE_EXCEEDS_BUDGET")
    return {"root_uci":move.uci(),"root_san":root_san,
            "source_opponent_k":k,"source_depth":depth,
            "opponent_layers":2,"tree":branches,
            "leaf_paths":leaves,"leaf_count":len(leaves),
            "source_work_estimate":ledger,
            "tree_excludes_nonranked_replies":True,
            "same_source_engine_selects_both_player_and_opponent":True,
            "terminal_branches_are_explicit":True}


def produce(fen,ua,ub,engine,k=2,depth=8):
    board,a,b=verify_board_and_pair(fen,ua,ub)
    roots=[tree_for_root(board,x,engine,k,depth) for x in (a,b)]
    if len(roots)!=2 or [x["root_uci"] for x in roots]!=[ua,ub]:
        raise ValueError("P4_HOLD_ROOT_PAIR")
    return {"schema":SCHEMA,"fen":board.fen(en_passant="fen"),
            "root_player":"white" if board.turn else "black",
            "roots":roots,"total_leaf_paths":sum(r["leaf_count"] for r in roots),
            "source_stockfish_commit":ENGINE_GIT_COMMIT,
            "source_family":"Stockfish16 classical",
            "prior_art_original_paper":CUI_DRIVE,
            "related_concept_primary_pdf":CCC_DRIVE,
            "method":"Cui et al 2026 §4.1 opponent top-k ranked; own single best; two opponent layers",
            "same_engine_not_independent_judge":True,
            "complete_opponent_reply_universe":False,
            "not_original_cui_verbalizer_or_human_eval":True,
            "not_source_chess_root_causal_intervention":True}


def main():
    p=argparse.ArgumentParser()
    for x in ("fen","move-a","move-b","stockfish","out"):
        p.add_argument("--"+x,required=True)
    p.add_argument("--depth",type=int,default=8)
    p.add_argument("--k",type=int,default=2)
    args=p.parse_args()
    verify_board_and_pair(args.fen,args.move_a,args.move_b)
    with chess.engine.SimpleEngine.popen_uci(args.stockfish,timeout=120) as engine:
        if ("stockfish" not in engine.id.get("name","").lower()
            or not {"Use NNUE","Threads","Hash"}.issubset(engine.options)):
            raise ValueError("P4_HOLD_NOT_STOCKFISH")
        engine.configure({"Use NNUE":False,"Threads":1,"Hash":16})
        out=produce(args.fen,args.move_a,args.move_b,engine,args.k,args.depth)
    out["native_stockfish_binary_sha256"]=digest(args.stockfish)
    dest=Path(args.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("C3X_P4_ACTUAL_CUI_TWO_LAYER",out["total_leaf_paths"],
          "source_query_counts",[r["source_work_estimate"] for r in out["roots"]],
          "result_sha",digest(dest),flush=True)


if __name__=="__main__":
    main()
