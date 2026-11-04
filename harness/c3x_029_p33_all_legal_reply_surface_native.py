#!/usr/bin/env python3
"""P33: evaluate EVERY legal first opponent response in archived complete games.

Development-only adaptive cases 6,10,14 from C3X 0.18/P32, all already exposed.
Depth10 per forced response is NOT an exact solved minimax guarantee.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

from c3x_029_p32_original_history_reply_value_native import (
    FROZEN_SOURCE_SHA256, ORIGINAL_STOCKFISH16_COMMIT, material_cp,
    perspective, replay_original, need,
)

ADAPTIVE_CASE_IDS = (6,10,14)
P32_NATIVE_SHA256 = "8e9ed5104156887221696a79416c69060dc3fa8beb48c02142337591b25efc8b"


def summarize_surface(records, earlier_top3, actual_next=None):
    need(records and len(records)==len({x["opponent_reply_uci"] for x in records}),
         "BAD_REPLY_UNIVERSE")
    ranked=sorted(records,key=lambda x:(x["value_root_pov_cp_or_mate_scaled"],
                                        x["opponent_reply_uci"]))
    worst=ranked[0]
    top_set=set(earlier_top3)
    observed=next((x for x in records if x["opponent_reply_uci"]==actual_next),None)
    if actual_next is not None:
        need(observed is not None,"ACTUAL_REPLY_NOT_LEGAL")
    return {
        "entire_legal_reply_count":len(records),
        "min_forced_reply_value_root_pov_cp_or_mate_scaled":worst["value_root_pov_cp_or_mate_scaled"],
        "argmin_uci":worst["opponent_reply_uci"],
        "argmin_found_in_prior_top3":worst["opponent_reply_uci"] in top_set,
        "prior_top3_uci":list(earlier_top3),
        "source_actual_next_reply_uci":actual_next,
        "actual_reply_was_in_prior_top3":actual_next in top_set if actual_next is not None else None,
        "actual_reply_value_root_pov_cp_or_mate_scaled":observed["value_root_pov_cp_or_mate_scaled"] if observed else None,
        "actual_reply_value_minus_worst_cp":(observed["value_root_pov_cp_or_mate_scaled"]-worst["value_root_pov_cp_or_mate_scaled"]) if observed else None,
        "exact_chess_guarantee":False,
        "restriction":"every legal first opponent reply, each depth-limited followup engine search",
    }


def run_case(engine, original, past_case, depth):
    board=replay_original(original)
    own=board.turn
    start_mat=material_cp(board,own)
    baseline=past_case["baseline_stockfish16_top2"]
    played=original["played_legal_move_uci"]
    choices=[played]
    for b in baseline:
        if b["root_uci"] not in choices:
            choices.append(b["root_uci"])
        if len(choices)==2: break
    need(len(choices)==2,"TWO_DISTINCT_CANDIDATES_NEEDED")
    old_lookup={x["root_uci"]:x for x in past_case["candidates"]}
    actual_sequence=original["full_original_mainline_uci"]
    i=original["source_ply_before_original_move"]
    actual_next=actual_sequence[i+1] if i+1<len(actual_sequence) else None
    result=[]
    for root_uci in choices:
        root=chess.Move.from_uci(root_uci)
        need(root in board.legal_moves,"ROOT_NOT_LEGAL")
        afterroot=board.copy(stack=True)
        afterroot.push(root)
        reply_moves=sorted(afterroot.legal_moves,key=lambda x:x.uci())
        need(len(reply_moves)>0,"TERMINAL_CANDIDATE_HOLD")
        rows=[]
        for reply in reply_moves:
            afterreply=afterroot.copy(stack=True)
            afterreply.push(reply)
            # One independent analysis per exact legal reply, with full move stack.
            info=engine.analyse(afterreply,chess.engine.Limit(depth=depth),
                                game=f"P33:{original['id']}:{root_uci}:{reply.uci()}",
                                info=chess.engine.INFO_ALL)
            value,uciscore=perspective(info,own)
            pv=[m.uci() for m in info.get("pv",[])[:12]]
            rows.append({
                "opponent_reply_uci":reply.uci(),
                "value_root_pov_cp_or_mate_scaled":value,
                "uci_score":uciscore,
                "native_nodes":int(info.get("nodes",0)),
                "best_mover_next_uci":pv[0] if pv else None,
                "best_mover_pv_uci":pv,
                "material_after_reply_from_root_cp":material_cp(afterreply,own)-start_mat,
            })
        original_top3=old_lookup[root_uci]["opponent_reply_top3"]
        earlier=[x["reply_uci"] for x in original_top3]
        summary=summarize_surface(rows,earlier,actual_next if root_uci==played else None)
        result.append({
            "root_uci":root_uci,
            "is_actual_played_root":root_uci==played,
            "original_root_legal_count":board.legal_moves.count(),
            "immediate_material_delta_cp":material_cp(afterroot,own)-start_mat,
            "prior_p32_depth12_top3":earlier,
            "all_legal_first_reply_surface":rows,
            "summary":summary,
        })
        print("P33_SOURCE_CASE",original["id"],"root",root_uci,
              "all_legal_replies",len(rows),"min",summary["argmin_uci"],
              "min_value",summary["min_forced_reply_value_root_pov_cp_or_mate_scaled"],
              "argmin_in_old_top3",summary["argmin_found_in_prior_top3"],flush=True)
    return {
        "id":original["id"],"game_sha256":original["source_game_sha256"],
        "source_ply":original["source_ply_before_original_move"],
        "source_fen4":original["fen4"],
        "played_original_uci":played,"candidate_surfaces":result,
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("source","p32-native","engine","out"):p.add_argument("--"+name,required=True)
    p.add_argument("--depth",type=int,default=10)
    a=p.parse_args()
    need(6<=a.depth<=18,"INVALID_DEPTH")
    source_bytes=Path(a.source).read_bytes()
    prior_bytes=Path(a.p32_native).read_bytes()
    need(hashlib.sha256(source_bytes).hexdigest()==FROZEN_SOURCE_SHA256,"FROZEN_SOURCE_SHA")
    need(hashlib.sha256(prior_bytes).hexdigest()==P32_NATIVE_SHA256,"FROZEN_P32_NATIVE_SHA")
    src=json.loads(source_bytes)
    prior=json.loads(prior_bytes)
    source_map={x["id"]:x for x in src["selected"]}
    prior_map={x["id"]:x for x in prior["cases"]}
    need(set(ADAPTIVE_CASE_IDS)<=set(source_map) and set(ADAPTIVE_CASE_IDS)<=set(prior_map),
         "CASE_MISSING")
    engine=chess.engine.SimpleEngine.popen_uci(a.engine,timeout=120)
    try:
        engine.configure({"Threads":1,"Hash":16,"Use NNUE":False})
        rows=[run_case(engine,source_map[i],prior_map[i],a.depth) for i in ADAPTIVE_CASE_IDS]
    finally:
        engine.quit()
    need(len(rows)==len(ADAPTIVE_CASE_IDS),"DENOMINATOR")
    data={
        "schema":"c3x029-p33-all-legal-opponent-first-reply-forced-SF16-value-v1",
        "source_sha256":FROZEN_SOURCE_SHA256,
        "p32_native_sha256":P32_NATIVE_SHA256,
        "official_stockfish16_commit":ORIGINAL_STOCKFISH16_COMMIT,
        "adaptively_selected_historical_development_cases":list(ADAPTIVE_CASE_IDS),
        "depth_per_response":a.depth,"threads":1,"hash_mb":16,"use_nnue":False,
        "first_ply_exhaustive":True,
        "future_minimax_solved":False,
        "native_search_at_each_response":"UCI position startpos moves [entire original mainline prefix + root + reply]",
        "claim_ceiling":"bounded-depth engine estimates, no optimal chess proof, no heldout, no search-mechanism causal explanation",
        "cases":rows,
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("P33_EXHAUSTIVE_LEGAL_FIRST_REPLY_SURFACE_COMPLETE",flush=True)


if __name__=="__main__":
    main()
