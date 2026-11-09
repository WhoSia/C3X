#!/usr/bin/env python3
"""C3X P42/R24-B1: PRE-JUDGE source-conditioned own-plan freeze.

For every opponent legal reply of two expressly exposed R23 candidate roots,
run unmodified source-family Stockfish16 with classical evaluation and record
the immediate best own reply. No Berserk reference engine is called here.
Full original 30-ply legal history, original P37/P38 source SHA pinned.
This is an exploratory policy baseline, NOT Cui k=3 or causal C3X explanation.
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

SF_COMMIT="68e1e9b3811e16cad014b590d7443b9063b3eb52"
DEPTH=12
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def admit(board,info):
    depth=info.get("depth");nodes=info.get("nodes");pv=info.get("pv")
    if type(depth)is not int or depth<DEPTH:raise ValueError("R24_HOLD_SOURCE_PLAN_DEPTH_UNREACHED")
    if type(nodes)is not int or nodes<=0:raise ValueError("R24_HOLD_SOURCE_PLAN_NODES_MISSING")
    if not isinstance(pv,list) or not pv or pv[0] not in board.legal_moves:
        raise ValueError("R24_HOLD_SOURCE_OWN_MOVE_ILLEGAL_OR_NO_PV")
    return {"own_uci":pv[0].uci(),"source_depth":depth,"source_nodes":nodes}

def freeze(worlds,eng):
    result=[]
    for case,board,pairs in worlds:
        roots=[]
        for pair in pairs:
            child=board.copy(stack=True);child.push_uci(pair["root"])
            responses=[]
            for reply in pair["replies"]:
                after=child.copy(stack=True);after.push_uci(reply)
                if after.is_game_over(claim_draw=False):
                    raise ValueError("R24_HOLD_TERMINAL_OPPONENT_REPLY_NEEDS_RULE_EXACT_OWN_PLAN")
                info=eng.analyse(after,chess.engine.Limit(depth=DEPTH),
                                 game=object(),info=chess.engine.INFO_ALL)
                record=admit(after,info)
                responses.append({"opponent_reply":reply,**record})
            if [r["opponent_reply"] for r in responses]!=pair["replies"]:
                raise ValueError("R24_HOLD_LEGAL_REPLY_FREEZE_COVERAGE")
            roots.append({"root_uci":pair["root"],
                          "legal_reply_count":len(pair["replies"]),
                          "conditional_own_plan":responses,
                          "actual_source_nodes_total":sum(x["source_nodes"] for x in responses)})
        result.append({"case_id":case["case_id"],"event_family":case["event_family"],
                       "root_candidates":roots})
    return {"schema":"c3x042-r24-prejudge-source-conditioned-own-policy-v1",
       "status":"FROZEN_BEFORE_INDEPENDENT_REFERENCE_OWN_ACTION_JUDGING",
       "selection_is_post_R22_exploratory":True,
       "pre_reference_source_engine_commit":SF_COMMIT,
       "pre_reference_source_depth":DEPTH,
       "pre_reference_use_nnue":False,
       "source_cases":len(result),
       "root_count":sum(len(c["root_candidates"]) for c in result),
       "reply_conditioned_own_moves":sum(len(r["conditional_own_plan"])
         for c in result for r in c["root_candidates"]),
       "cases":result,
       "cui_k3_strong_baseline_claim":False,
       "c3x_native_causal_explanation_claim":False,
       "reference_score_used_to_generate_plan":False,
       "prospective_cohort":False,
       "independently_judged_own_plan_value":False}

def main():
    p=argparse.ArgumentParser()
    for k in ("source","predictions","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    original=authentic_cases(
      authentic_archive(Path(a.predictions),PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA),
      authentic_archive(Path(a.source),SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA))
    worlds=source_positions(original,FROZEN_EXPLORATORY_CASES)
    with chess.engine.SimpleEngine.popen_uci(a.engine,timeout=120) as eng:
        if "stockfish" not in eng.id.get("name","").lower():
            raise ValueError("R24_HOLD_WRONG_SOURCE_PLAN_ENGINE")
        if not {"Threads","Hash","Use NNUE"}.issubset(eng.options):
            raise ValueError("R24_HOLD_MISSING_SOURCE_PLAN_OPTIONS")
        eng.configure({"Threads":1,"Hash":16,"Use NNUE":False})
        result=freeze(worlds,eng)
    if result["reply_conditioned_own_moves"]!=147:
        raise ValueError("R24_HOLD_PREJUDGE_LEGAL_REPLY_FREEZE_UNIVERSE")
    result["source_binary_sha256"]=digest(a.engine)
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X042_R24_B_SOURCE_PREJUDGE_OWN_PLAN_FROZEN",
          result["reply_conditioned_own_moves"],"source candidate actions",
          "NO_BERSERK_JUDGE_CALL")
if __name__=="__main__":
    main()
