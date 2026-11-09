#!/usr/bin/env python3
"""C3X P42/R23: exhaustive legal-first-reply, independent value *pilot*.

Two exposed event games chosen after R22 independent scores (NOT prospective).
All opponent replies for both previously frozen root candidates, no answer-
driven reply sampling, original full legal game histories, pinned Berserk14.
Per-reply depth12 and depth16 with actual heterogeneous node costs.

If any reply has no admissible finite search value, the 'all replies' claim
is HOLD. A score after one reply does not identify a correct own policy, a
strategic plan, or the source engine's own reasons for choosing the root.
"""
import argparse,hashlib,json
from pathlib import Path
import chess,chess.engine
from c3x_029_p38_r1_ethereal_independent_referee import (
 authentic_archive,authentic_cases,SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA,
 PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA)
from c3x_029_p42_r22_berserk_fixed_depth_value_pilot import (
 quality,DEPTHS,NET_SHA,FAMILY_COMMIT)

R22_JSON_SHA="be4de0811ff7d8b29f9b79a0008757dd6c456f3be0cb87e32940bba0ba23ddaa"
FROZEN_EXPLORATORY_CASES=("1e65fcf3b7a93b9b","04d52e451d89ee05")
METHODS=("stockfish_pv","simple_json","c3x_legal_plan")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def sample_selection(phase):
    if phase.get("schema")!="c3x042-r22-berserk-independent-fixed-depth-feasibility-v1":
        raise ValueError("R23_HOLD_ORIGINAL_R22_SCHEMA")
    ranked=sorted(phase.get("cases",[]),key=lambda c:(
       c["depth16_margin_cp"] if c["both_technically_evaluable"] else float("inf"),
       str(c["case_id"])))
    if len(ranked)!=8 or tuple(c["case_id"] for c in ranked[:2])!=FROZEN_EXPLORATORY_CASES:
        raise ValueError("R23_HOLD_EXPLORATORY_TWO_CASE_SELECTION_DRIFT")
    return FROZEN_EXPLORATORY_CASES

def source_positions(originals, frozen_ids):
    indexed={c["case_id"]:c for c in originals}
    if len(indexed)!=len(originals):
        raise ValueError("R23_HOLD_CASE_DUPLICATE")
    worlds=[]
    for cid in frozen_ids:
        c=indexed[cid]
        board=chess.Board()
        for u in c["original_prefix_uci"]:
            m=chess.Move.from_uci(u)
            if m not in board.legal_moves:raise ValueError("R23_HOLD_SOURCE_HISTORY_ILLEGAL")
            board.push(m)
        pairs=[]
        for candidate in c["candidate_pairs"]:
            root=chess.Move.from_uci(candidate["root_uci"])
            if root not in board.legal_moves:raise ValueError("R23_HOLD_ROOT_ILLEGAL")
            replies=sorted((m.uci() for m in board.copy(stack=True).variation_san([root]) and []),key=str) if False else []
            child=board.copy(stack=True);child.push(root)
            replies=sorted(m.uci() for m in child.legal_moves)
            if not replies:raise ValueError("R23_HOLD_EMPTY_REPLY_UNIVERSE")
            forecasts={method:candidate["predictions"][method]["reply"]
                       for method in METHODS}
            pairs.append({"root":root.uci(),"replies":replies,"frozen_forecasts":forecasts})
        if len(pairs)!=2:raise ValueError("R23_HOLD_TWO_FROZEN_CANDIDATES")
        worlds.append((c,board,pairs))
    return worlds

def judge_reply(eng,board,depth,own):
    if board.is_game_over(claim_draw=False):
        return {"status":"HOLD_TERMINAL_BRANCH_REQUIRES_SEPARATE_RULE_EXACT_VALUE"}
    info=eng.analyse(board,chess.engine.Limit(depth=depth),
                     game=object(),info=chess.engine.INFO_ALL)
    return quality(board,info,depth,own)

def reduce_reply_court(worlds):
    out=[]
    for w in worlds:
        pairs=[]
        for p in w["pairs"]:
            full={}
            for d in DEPTHS:
                vals=[row["modes"][str(d)] for row in p["source_reply_values"]]
                full[str(d)]=all(x["status"]=="DEPTH_CONTROLLED_FINITE_SEARCH_ONLY"
                                 for x in vals)
            argmin={}
            minvalues={}
            forecast_hits={}
            for d in DEPTHS:
                if full[str(d)]:
                    q={r["reply"]:r["modes"][str(d)]["root_mover_cp"]
                       for r in p["source_reply_values"]}
                    lowest=min(q.values())
                    argmin[str(d)]=sorted(k for k,v in q.items() if v==lowest)
                    minvalues[str(d)]=lowest
                    forecast_hits[str(d)]={m:p["frozen_forecasts"][m] in argmin[str(d)]
                                            for m in METHODS}
                else:
                    argmin[str(d)]=None;minvalues[str(d)]=None
                    forecast_hits[str(d)]=None
            pairs.append({
                "root_uci":p["root"],"all_legal_opponent_replies":len(p["source_reply_values"]),
                "all_reply_depth_coverage":full,
                "independent_min_after_opponent_reply_cp":minvalues,
                "minimizing_reply_uci":argmin,
                "original_frozen_forecast_hits_if_complete":forecast_hits,
                "total_actual_native_nodes_by_depth":{
                   str(d):sum(z["modes"][str(d)].get("actual_nodes") or 0
                              for z in p["source_reply_values"])
                   for d in DEPTHS},
                "unadmitted_reply_count_by_depth":{
                   str(d):sum(z["modes"][str(d)]["status"]!="DEPTH_CONTROLLED_FINITE_SEARCH_ONLY"
                              for z in p["source_reply_values"])
                   for d in DEPTHS}
                })
        out.append({"case_id":w["case_id"],"event_family":w["event_family"],
                    "frozen_candidate_roots":pairs})
    return {"schema":"c3x042-r23-development-adversarial-reply-value-landscape-v1",
      "status":"EXPLORATORY_FULL_LEGAL_REPLY_SOURCE_EVALUATION_NOT_CHESS_TRUTH",
      "source_commit":FAMILY_COMMIT,"network_sha256":NET_SHA,
      "original_R22_provenance_SHA":R22_JSON_SHA,
      "selection_by_R22_postoutcome_margin":True,
      "source_event_games":len(out),
      "total_root_candidates":sum(len(x["frozen_candidate_roots"]) for x in out),
      "complete_depth16_root_reply_sweeps":sum(
         y["all_reply_depth_coverage"]["16"] for x in out for y in x["frozen_candidate_roots"]),
      "cases":out,"global_root_decision_certified":False,
      "root_source_mediation_certified":False,
      "independent_judge_is_objective_truth":False,
      "all_reply_depth_search_has_equal_real_nodes":False,
      "Cui_k3_or_BinProp_strong_baseline_compared":False,
      "prior_C3X_shallow_heuristic_is_full_causal_explainer":False,
      "prospective_new_game_cohort":False,
      "claim_ceiling":"Exhaustive first opponent replies of two post-selected exploratory root-pairs under independent fixed-depth finite engine score. NOT own continuation plan or objective minimax."
    }

def main():
    p=argparse.ArgumentParser()
    for k in ("source","predictions","r22","engine","network","out"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    if sha(a.network)!=NET_SHA or sha(a.r22)!=R22_JSON_SHA:
        raise ValueError("R23_HOLD_R22_OR_NETWORK_SOURCE_BYTES")
    selected=sample_selection(json.loads(Path(a.r22).read_bytes()))
    original=authentic_cases(
      authentic_archive(Path(a.predictions),PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA),
      authentic_archive(Path(a.source),SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA))
    worlds=source_positions(original,selected)
    completed=[]
    with chess.engine.SimpleEngine.popen_uci(a.engine,timeout=120) as eng:
        if "berserk" not in eng.id.get("name","").lower() or not {"Threads","Hash"}.issubset(eng.options):
            raise ValueError("R23_HOLD_ACTUAL_INDEPENDENT_ENGINE_ID")
        eng.configure({"Threads":1,"Hash":16})
        for case,board,pairs in worlds:
            root_entries=[]
            for p in pairs:
                child=board.copy(stack=True);child.push_uci(p["root"])
                reply_rows=[]
                for u in p["replies"]:
                    with_reply=child.copy(stack=True);with_reply.push_uci(u)
                    modes={str(d):judge_reply(eng,with_reply,d,board.turn) for d in DEPTHS}
                    reply_rows.append({"reply":u,"modes":modes})
                root_entries.append({**p,"source_reply_values":reply_rows})
                print("R23_CROSS_FAMILY_ALL_LEGAL_OPPONENT_REPLIES",case["event_family"],
                      p["root"],len(reply_rows),flush=True)
            completed.append({"case_id":case["case_id"],"event_family":case["event_family"],
                              "pairs":root_entries})
    res=reduce_reply_court(completed)
    res["binary_sha256"]=sha(a.engine)
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n")
    print("R23_INDEPENDENT_FULL_REPLY_PILOT",
          res["complete_depth16_root_reply_sweeps"],"/",res["total_root_candidates"],flush=True)
    if res["complete_depth16_root_reply_sweeps"]==0:
        raise SystemExit("R23_HOLD_NO_COMPLETE_INDEPENDENT_REPLY_LANDSCAPES")
if __name__=="__main__":
    main()
