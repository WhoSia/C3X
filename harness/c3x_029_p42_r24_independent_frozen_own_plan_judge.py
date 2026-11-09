#!/usr/bin/env python3
"""C3X P42/R24-B2: INDEPENDENT Berserk judging of frozen source plans.

R24-B1 actions are SHA-locked before judging; no reference-favored response
selection. Evaluates all 147 legal opponent replies twice at each depth:
(1) unrestricted Berserk search and (2) Berserk search with root_moves
restricted to frozen Stockfish own action, with actual nodes logged.
This is finite-depth exploratory cross-engine tactical policy assessment,
not exact minimax, true strategic explanation or Cui/BinProp superiority.
"""
import argparse,hashlib,json
from pathlib import Path
import chess,chess.engine
from c3x_029_p38_r1_ethereal_independent_referee import (
 authentic_archive,authentic_cases,SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA,
 PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA
)
from c3x_029_p42_r23_independent_all_opponent_reply_value_court import (
 FROZEN_EXPLORATORY_CASES,source_positions
)
from c3x_029_p42_r22_berserk_fixed_depth_value_pilot import (
 quality,DEPTHS,NET_SHA,FAMILY_COMMIT
)

FROZEN_PLAN_SHA="3c8f2a57cefe19fcb7a00925f4434f5008195bce5adeba1e67dc84f18f084f34"
PLAN_SCHEMA="c3x042-r24-prejudge-source-conditioned-own-policy-v1"
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def source_policy(worlds,frozen):
    if (frozen.get("schema")!=PLAN_SCHEMA
        or frozen.get("status")!="FROZEN_BEFORE_INDEPENDENT_REFERENCE_OWN_ACTION_JUDGING"
        or frozen.get("reference_score_used_to_generate_plan") is not False
        or frozen.get("selection_is_post_R22_exploratory") is not True
        or frozen.get("reply_conditioned_own_moves")!=147):
        raise ValueError("R24_HOLD_PREJUDGE_POLICY_PROVENANCE")
    if len(frozen.get("cases",[]))!=len(worlds):
        raise ValueError("R24_HOLD_PREJUDGE_GAME_COUNT")
    cases=[]
    for (source,board,pairs),f_case in zip(worlds,frozen["cases"]):
        if f_case.get("case_id")!=source["case_id"] or len(f_case["root_candidates"])!=len(pairs):
            raise ValueError("R24_HOLD_SOURCE_GAME_OR_ROOT_IDENTITY")
        roots=[]
        for p,f_root in zip(pairs,f_case["root_candidates"]):
            if p["root"]!=f_root.get("root_uci"):
                raise ValueError("R24_HOLD_SOURCE_ROOT_ORDER")
            rows=f_root.get("conditional_own_plan",[])
            if [x.get("opponent_reply") for x in rows]!=p["replies"]:
                raise ValueError("R24_HOLD_ALL_SOURCE_LEGAL_REPLY_FREEZE_DRIFT")
            child=board.copy(stack=True);child.push_uci(p["root"])
            for row in rows:
                after=child.copy(stack=True);after.push_uci(row["opponent_reply"])
                own=chess.Move.from_uci(row["own_uci"])
                if own not in after.legal_moves or row.get("source_depth",0)<12:
                    raise ValueError("R24_HOLD_FROZEN_SOURCE_OWN_MOVE_ILLEGAL")
            roots.append((p,rows))
        cases.append((source,board,roots))
    return cases

def signed_gap(best,forced):
    if any(x.get("status")!="DEPTH_CONTROLLED_FINITE_SEARCH_ONLY" for x in (best,forced)):
        return None
    return best["root_mover_cp"]-forced["root_mover_cp"]

def reduce_native(data):
    aggregate=[]
    for case in data:
        roots=[]
        for candidate in case["roots"]:
            depth_res={}
            for depth in DEPTHS:
                k=str(depth)
                rows=candidate["reply_results"]
                good=all(row[k]["signed_reference_gap_cp"] is not None for row in rows)
                if good:
                    gaps=[row[k]["signed_reference_gap_cp"] for row in rows]
                    frozen_scores=[row[k]["frozen_policy"]["root_mover_cp"] for row in rows]
                    unrestricted_scores=[row[k]["unrestricted"]["root_mover_cp"] for row in rows]
                    detail={
                      "all_legal_reply_plan_scores_finite":True,
                      "reply_count":len(rows),
                      "worst_frozen_plan_reply_uci":sorted(
                          row["opponent_reply"] for row in rows
                          if row[k]["frozen_policy"]["root_mover_cp"]==min(frozen_scores)),
                      "worst_frozen_plan_value_cp":min(frozen_scores),
                      "worst_unrestricted_judge_response_value_cp":min(unrestricted_scores),
                      "judge_source_action_diff_count":sum(
                          row[k]["unrestricted_pv_own_move"]!=row["frozen_own_move"]
                          for row in rows),
                      "largest_signed_regret_cp":max(gaps),
                      "negative_signed_regret_count":sum(g<0 for g in gaps),
                      "sum_absolute_signed_gap_cp":sum(abs(g) for g in gaps),
                      "actual_judge_nodes_unrestricted":sum(row[k]["unrestricted"]["actual_nodes"] for row in rows),
                      "actual_judge_nodes_forced_source_plan":sum(row[k]["frozen_policy"]["actual_nodes"] for row in rows)}
                else:
                    detail={"all_legal_reply_plan_scores_finite":False,
                            "unadmitted_reply_count":sum(row[k]["signed_reference_gap_cp"] is None for row in rows),
                            "no_full_minimum_reported":True}
                depth_res[k]=detail
            roots.append({"root_uci":candidate["root"],"source_legal_reply_count":len(candidate["reply_results"]),
                          "original_source_plan_total_nodes":candidate["source_plan_nodes"],
                          "depth_evaluations":depth_res})
        aggregate.append({"case_id":case["case_id"],"event_family":case["event_family"],"roots":roots})
    return {
      "schema":"c3x042-r24-independently-judged-full-reply-source-own-policy-v1",
      "status":"EXPLORATORY_JUDGED_OR_PARTIAL_REPLY_CONDITIONED_PLAN_ONLY",
      "prejudge_plan_sha256":FROZEN_PLAN_SHA,
      "independent_referee_commit":FAMILY_COMMIT,
      "independent_referee_nnue_sha256":NET_SHA,
      "actual_referee_nodes_explicit":True,
      "equal_node_budget_certified":False,
      "judge_self_pv_is_not_objective_oracle":True,
      "all_legal_first_reply_plan_conditioning":True,
      "selection_is_post_R22_exploratory":True,
      "conditional_plan_is_mechanistic_source_C3X":False,
      "cui_k3_or_binprop_strong_baseline_implemented":False,
      "independent_chess_truth_proven":False,
      "source_native_root_causality_proven":False,
      "prospective_heldout":False,
      "cases":aggregate
    }

def main():
    p=argparse.ArgumentParser()
    for key in ("source","predictions","frozen-plan","engine","network","out"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    if digest(a.frozen_plan)!=FROZEN_PLAN_SHA or digest(a.network)!=NET_SHA:
        raise ValueError("R24_HOLD_FROZEN_PREJUDGE_OR_INDEPENDENT_NETWORK_BYTES")
    original=authentic_cases(
      authentic_archive(Path(a.predictions),PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA),
      authentic_archive(Path(a.source),SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA))
    cases=source_policy(source_positions(original,FROZEN_EXPLORATORY_CASES),
                        json.loads(Path(a.frozen_plan).read_text()))
    data=[]
    with chess.engine.SimpleEngine.popen_uci(a.engine,timeout=180) as eng:
        if "berserk" not in eng.id.get("name","").lower() or not {"Threads","Hash"}.issubset(eng.options):
            raise ValueError("R24_HOLD_INDEPENDENT_BERSERK_SOURCE_ID")
        eng.configure({"Threads":1,"Hash":16})
        for source,board,pairs in cases:
            roots=[]
            for p,frozen in pairs:
                child=board.copy(stack=True);child.push_uci(p["root"])
                outrows=[]
                for original_row in frozen:
                    after=child.copy(stack=True);after.push_uci(original_row["opponent_reply"])
                    source_own=chess.Move.from_uci(original_row["own_uci"])
                    modes={}
                    for d in DEPTHS:
                        unrestricted_info=eng.analyse(
                           after,chess.engine.Limit(depth=d),game=object(),info=chess.engine.INFO_ALL)
                        forced_info=eng.analyse(
                           after,chess.engine.Limit(depth=d),root_moves=[source_own],
                           game=object(),info=chess.engine.INFO_ALL)
                        unrestricted=quality(after,unrestricted_info,d,board.turn)
                        forced=quality(after,forced_info,d,board.turn)
                        best_move=(unrestricted_info.get("pv") or [None])[0]
                        modes[str(d)]={
                           "unrestricted":unrestricted,
                           "frozen_policy":forced,
                           "signed_reference_gap_cp":signed_gap(unrestricted,forced),
                           "unrestricted_pv_own_move":best_move.uci() if isinstance(best_move,chess.Move) else None
                         }
                    outrows.append({"opponent_reply":original_row["opponent_reply"],
                                    "frozen_own_move":original_row["own_uci"],
                                    **modes})
                roots.append({"root":p["root"],"source_plan_nodes":sum(x["source_nodes"] for x in frozen),
                              "reply_results":outrows})
                print("R24_INDEPENDENT_OWN_POLICY_CHESS_JUDGE",source["event_family"],p["root"],
                      "legal_replies",len(outrows),flush=True)
            data.append({"case_id":source["case_id"],"event_family":source["event_family"],
                         "roots":roots})
    result=reduce_native(data)
    result["independent_judge_binary_sha256"]=digest(a.engine)
    output=Path(a.out);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    completed=sum(
      r["depth_evaluations"]["16"].get("all_legal_reply_plan_scores_finite",False)
      for c in result["cases"] for r in c["roots"])
    print("R24_FROZEN_OWN_PLAN_ADJUDICATION_COMPLETE_FINITE_DEPTH16",completed,"/4")
    if completed==0:raise SystemExit("R24_HOLD_NO_COMPLETE_INDEPENDENT_PLAN_JUDGEMENT")
if __name__=="__main__":
    main()
