#!/usr/bin/env python3
"""P42/R22: depth-controlled independent Berserk root-value *feasibility*.

Explicit new protocol after R21 node-based native hard failure. Does not
retroactively weaken R21's >=90% node contract, equate heterogeneous actual
nodes, certify chess truth, or select favorite event cases after the result.
"""
from pathlib import Path
import argparse,hashlib,json
import chess,chess.engine
from c3x_029_p38_r1_ethereal_independent_referee import (
 authentic_cases,authentic_archive,PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA,
 SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA
)
from c3x_029_p42_r21_independent_berserk_value_feasibility import FAMILY_COMMIT,NET_SHA

DEPTHS=(12,16)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def quality(board,info,requested_depth,own):
    nodes=info.get("nodes")
    depth=info.get("depth")
    pv=info.get("pv")
    if type(depth)is not int or depth<requested_depth:
        return {"status":"HOLD_DEPTH_UNDERREQUEST","actual_depth":depth,"actual_nodes":nodes}
    if type(nodes)is not int or nodes<1000:
        return {"status":"HOLD_INSUFFICIENT_REAL_SEARCH","actual_depth":depth,"actual_nodes":nodes}
    if not isinstance(pv,list) or not pv:
        return {"status":"HOLD_NO_PV","actual_depth":depth,"actual_nodes":nodes}
    temp=board.copy(stack=True)
    for m in pv:
        if m not in temp.legal_moves:
            return {"status":"HOLD_ILLEGAL_PV","actual_depth":depth,"actual_nodes":nodes}
        temp.push(m)
        if temp.is_game_over(claim_draw=False):break
    score=info.get("score")
    if score is None:
        return {"status":"HOLD_NO_SCORE","actual_depth":depth,"actual_nodes":nodes}
    val=score.pov(own)
    if val.is_mate() or type(val.score()) is not int:
        return {"status":"HOLD_MATE_OR_NONCP","actual_depth":depth,"actual_nodes":nodes}
    if info.get("lowerbound",False) or info.get("upperbound",False):
        return {"status":"HOLD_BOUND_SCORE","actual_depth":depth,"actual_nodes":nodes}
    return {"status":"DEPTH_CONTROLLED_FINITE_SEARCH_ONLY",
            "root_mover_cp":val.score(),"actual_depth":depth,"actual_nodes":nodes}

def finalize(records):
    accepted=[]
    for r in records:
        pair=[]
        for c in r["candidates"]:
            good=all(c["depth_modes"][str(d)]["status"]=="DEPTH_CONTROLLED_FINITE_SEARCH_ONLY"
                     for d in DEPTHS)
            pair.append({"root_uci":c["root_uci"],"depths_reached":good,
                         "actual_nodes":{str(d):c["depth_modes"][str(d)].get("actual_nodes")
                                         for d in DEPTHS},
                         "cp":{str(d):c["depth_modes"][str(d)].get("root_mover_cp")
                               if good else None for d in DEPTHS}})
        accepted.append({"case_id":r["case_id"],"event_family":r["event_family"],
                         "roots":pair,"both_technically_evaluable":all(q["depths_reached"] for q in pair),
                         "depth16_margin_cp":abs(pair[0]["cp"]["16"]-pair[1]["cp"]["16"])
                           if all(q["depths_reached"] for q in pair) else None})
    return {"schema":"c3x042-r22-berserk-independent-fixed-depth-feasibility-v1",
        "status":"EXPLORATORY_INDEPENDENT_ENGINE_FIXED_DEPTH_PILOT_NOT_REFERENCE_TRUTH",
        "source_commit":FAMILY_COMMIT,"network_sha256":NET_SHA,
        "depth_requirements":list(DEPTHS),"minimum_actual_nodes_per_search":1000,
        "all_frozen_cases":len(accepted),
        "eligible_pairs":sum(x["both_technically_evaluable"] for x in accepted),
        "cases":accepted,
        "node_cost_equality_certified":False,
        "objective_chess_value_certified":False,
        "root_causal_source_mediation_certified":False,
        "new_prospective_cohort":False,
        "pre_frozen_strategic_plan_beyond_PV_compared":False,
        "claim_ceiling":"Only feasibility of independently sourced finite-depth chess root-score estimates with unequal actual node cost."}

def main():
    p=argparse.ArgumentParser()
    for x in ("source","predictions","engine","network","out"):p.add_argument("--"+x,required=True)
    a=p.parse_args()
    if sha(a.network)!=NET_SHA:raise ValueError("R22_HOLD_NETWORK_SOURCE_SHA")
    preds=authentic_archive(Path(a.predictions),PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA)
    source=authentic_archive(Path(a.source),SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA)
    originals=authentic_cases(preds,source)
    rows=[]
    with chess.engine.SimpleEngine.popen_uci(a.engine,timeout=120) as eng:
        if "berserk" not in eng.id.get("name","").lower():
            raise ValueError("R22_HOLD_ENGINE_ID")
        if not {"Threads","Hash"}.issubset(eng.options):
            raise ValueError("R22_HOLD_ENGINE_RESOURCE_ID")
        eng.configure({"Threads":1,"Hash":16})
        for case in originals:
            board=chess.Board()
            for u in case["original_prefix_uci"]:
                mv=chess.Move.from_uci(u)
                if mv not in board.legal_moves:raise ValueError("R22_HOLD_SOURCE_HISTORY_ILLEGAL")
                board.push(mv)
            parts=[]
            for candidate in case["candidate_pairs"]:
                root=chess.Move.from_uci(candidate["root_uci"])
                if root not in board.legal_moves:raise ValueError("R22_HOLD_CANDIDATE_ILLEGAL")
                child=board.copy(stack=True);child.push(root)
                results={}
                for d in DEPTHS:
                    if child.is_game_over(claim_draw=False):
                        results[str(d)]={"status":"HOLD_TERMINAL_CHILD"}
                    else:
                        info=eng.analyse(child,chess.engine.Limit(depth=d),game=object(),
                                         info=chess.engine.INFO_ALL)
                        results[str(d)]=quality(child,info,d,board.turn)
                parts.append({"root_uci":candidate["root_uci"],"depth_modes":results})
            rows.append({"case_id":case["case_id"],"event_family":case["event_family"],
                         "candidates":parts})
            print("R22_BERSERK_DEPTH_PAIR",len(rows),
                  [[a["depth_modes"][str(d)]["status"] for d in DEPTHS] for a in parts],flush=True)
    report=finalize(rows);report["binary_sha256"]=sha(a.engine)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("R22_BERSERK_DEPTH_PILOT",report["eligible_pairs"],"/",report["all_frozen_cases"],flush=True)
    if report["eligible_pairs"]==0:raise SystemExit("R22_HOLD_NO_DEPTH_ELIGIBLE_PAIRS")
if __name__=="__main__":
    main()
