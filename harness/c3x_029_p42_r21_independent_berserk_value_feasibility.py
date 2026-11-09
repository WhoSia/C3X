#!/usr/bin/env python3
"""P42/R21-B: Berserk-14 cross-family root-value referee feasibility.

This is an independent engine-family pilot on already exposed archived P37
events, not objective chess truth, source-causal mediation, independent new
cohort, prospective prediction accuracy, or a full-reply minimax certificate.

All frozen original P37 opponent/candidate forecasts predate this referee.
No forecast modifications or cherry-picked omissions allowed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import chess
import chess.engine

from c3x_029_p38_r1_ethereal_independent_referee import (
    authentic_cases, authentic_archive, SOURCE_JSON_SHA, PRED_JSON_SHA,
    SOURCE_MEMBER, PRED_MEMBER, SOURCE_ZIP_SHA, PRED_ZIP_SHA
)

FAMILY_COMMIT="8ae895a6151695be4a50d4fb65b0c131659c513a"
NET_SHA="9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084"
BUDGETS=(48000,96000)
MIN_DEPTH=3

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def reference_info(board, info, requested, mover_white):
    observed=info.get("nodes")
    depth=info.get("depth")
    pv=info.get("pv",[])
    if type(observed) is not int or observed < (requested*9)//10:
        return {"status":"HOLD_INSUFFICIENT_REAL_NODES","actual_nodes":observed,"depth":depth}
    if type(depth) is not int or depth < MIN_DEPTH:
        return {"status":"HOLD_SHALLOW_REFEREE","actual_nodes":observed,"depth":depth}
    if not isinstance(pv,list) or not pv:
        return {"status":"HOLD_NO_NATIVE_PV","actual_nodes":observed,"depth":depth}
    clone=board.copy(stack=True)
    for m in pv:
        if m not in clone.legal_moves:
            return {"status":"HOLD_ILLEGAL_NATIVE_PV","actual_nodes":observed,"depth":depth}
        clone.push(m)
        if clone.is_game_over(claim_draw=False):break
    score=info.get("score")
    if score is None or score.pov(chess.WHITE if mover_white else chess.BLACK).is_mate():
        return {"status":"HOLD_MATE_OR_MISSING_SCORE","actual_nodes":observed,"depth":depth}
    cp=score.pov(chess.WHITE if mover_white else chess.BLACK).score()
    if type(cp) is not int:
        return {"status":"HOLD_NON_CP_SCORE","actual_nodes":observed,"depth":depth}
    return {"status":"ELIGIBLE_FINITE_INDEPENDENT_ENGINE_SEARCH",
            "actual_nodes":observed,"depth":depth,"root_mover_cp":cp,
            "pv_uci":[m.uci() for m in pv],
            "lowerbound":info.get("lowerbound",False) is True,
            "upperbound":info.get("upperbound",False) is True}

def summarize(one):
    results=[]
    for case in one:
        if len(case["candidate_pairs"])!=2:raise ValueError("R21_HOLD_NOT_FROZEN_PAIR")
        candidates=[]
        for x in case["candidate_pairs"]:
            low=x["budgets"][str(BUDGETS[0])]
            high=x["budgets"][str(BUDGETS[1])]
            good=(low["status"]=="ELIGIBLE_FINITE_INDEPENDENT_ENGINE_SEARCH"
                  and high["status"]=="ELIGIBLE_FINITE_INDEPENDENT_ENGINE_SEARCH"
                  and not (low["lowerbound"] or low["upperbound"]
                           or high["lowerbound"] or high["upperbound"]))
            candidates.append({"root_uci":x["root_uci"],"technical_eligible":good,
                               "low_nodes":low.get("actual_nodes"),"high_nodes":high.get("actual_nodes"),
                               "low_depth":low.get("depth"),"high_depth":high.get("depth"),
                               "low_cp":low.get("root_mover_cp") if good else None,
                               "high_cp":high.get("root_mover_cp") if good else None,
                               "reason":None if good else "HOLD_UNCERTIFIED_FINITE_BUDGET"})
        eligible=all(x["technical_eligible"] for x in candidates)
        margin=abs(candidates[0]["high_cp"]-candidates[1]["high_cp"]) if eligible else None
        first=abs(candidates[0]["low_cp"]-candidates[1]["low_cp"]) if eligible else None
        results.append({"case_id":case["case_id"],"event_family":case["event_family"],
                        "roots":candidates,"pair_technically_eligible":eligible,
                        "cp_margin_96k":margin,"cp_margin_48k":first,
                        "near_tie_30cp_both_budgets":eligible and margin<=30 and first<=30,
                        "winner_stable_48k_96k":eligible and
                          ((candidates[0]["low_cp"]>candidates[1]["low_cp"])==
                           (candidates[0]["high_cp"]>candidates[1]["high_cp"]))})
    return {
     "schema":"c3x042-r21-independent-berserk-native-value-feasibility-v1",
     "status":"SOURCE_AUTHENTIC_INDEPENDENT_FAMILY_PILOT_ONLY",
     "engine_family":"Berserk 14, independent implementation influenced by Stockfish",
     "source_commit":FAMILY_COMMIT,"network_sha256":NET_SHA,
     "judge_is_objective_chess_truth":False,
     "new_game_event_prospective_cohort":False,
     "full_adversarial_reply_value_certificate":False,
     "root_source_causal_mediation_proved":False,
     "fair_full_plan_rival_comparison_proved":False,
     "near_tie_tolerance_cp_exploratory":30,
     "requested_nodes_per_root":list(BUDGETS),
     "cases":results,
     "all_frozen_cases":len(results),
     "technically_eligible_pairs":sum(x["pair_technically_eligible"] for x in results),
     "eligible_exploratory_near_tie_pairs":sum(x["near_tie_30cp_both_budgets"] for x in results)
    }

def main():
    p=argparse.ArgumentParser()
    for k in ("source","predictions","engine","binary","network","out"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    if sha(a.network)!=NET_SHA:raise ValueError("R21_HOLD_NETWORK_SHA")
    if sha(a.engine)!=sha(a.binary):raise ValueError("R21_HOLD_ENGINE_BINARY_ID")
    predictions=authentic_archive(Path(a.predictions),PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA)
    sources=authentic_archive(Path(a.source),SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA)
    cases=authentic_cases(predictions,sources)
    out=[]
    with chess.engine.SimpleEngine.popen_uci(a.engine,timeout=120) as process:
        if "berserk" not in process.id.get("name","").lower():
            raise ValueError("R21_HOLD_ENGINE_NAME_FAMILY")
        required={"Hash","Threads"}
        if not required.issubset(process.options):
            raise ValueError("R21_HOLD_ENGINE_UCI_RESOURCE_OPTIONS")
        process.configure({"Hash":16,"Threads":1})
        for case in cases:
            board=chess.Board()
            for u in case["original_prefix_uci"]:
                m=chess.Move.from_uci(u)
                if m not in board.legal_moves:raise ValueError("R21_HOLD_ORIGINAL_HISTORY_ILLEGAL")
                board.push(m)
            entries=[]
            for candidate in case["candidate_pairs"]:
                m=chess.Move.from_uci(candidate["root_uci"])
                if m not in board.legal_moves:raise ValueError("R21_HOLD_FROZEN_ROOT_ILLEGAL")
                child=board.copy(stack=True);child.push(m)
                data={}
                for n in BUDGETS:
                    if child.is_game_over(claim_draw=False):
                        data[str(n)]={"status":"HOLD_TERMINAL_CHILD"}
                    else:
                        info=process.analyse(child,chess.engine.Limit(nodes=n),
                                             game=object(),info=chess.engine.INFO_ALL)
                        data[str(n)]=reference_info(child,info,n,board.turn==chess.WHITE)
                entries.append({"root_uci":candidate["root_uci"],"budgets":data})
            out.append({"case_id":case["case_id"],"event_family":case["event_family"],
                        "candidate_pairs":entries})
            print("R21_BERSERK_CASE",len(out),out[-1]["event_family"],
                  [(q["root_uci"],q["budgets"]["96000"]["status"]) for q in entries],flush=True)
    report=summarize(out)
    report["binary_sha256"]=sha(a.engine)
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("R21_BERSERK_INDEPENDENT_PILOT",report["technically_eligible_pairs"],
          "of",report["all_frozen_cases"],"near",report["eligible_exploratory_near_tie_pairs"],flush=True)
    if report["technically_eligible_pairs"]==0:
        raise SystemExit("R21_HOLD_ALL_INDEPENDENT_NATIVE_SEARCH_INELIGIBLE")

if __name__=="__main__":
    main()
