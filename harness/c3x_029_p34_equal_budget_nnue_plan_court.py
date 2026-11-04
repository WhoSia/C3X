#!/usr/bin/env python3
"""P34: equal *requested* UCI node budgets, PV vs 1-reply JSON vs 3-reply policy.

All results developmental and source-exposed. Reference is a separate deep
Stockfish search, not objective chess truth, NNUE concepts or causal mechanism.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine
from c3x_029_p32_original_history_reply_value_native import (
    replay_original, FROZEN_SOURCE_SHA256, ORIGINAL_STOCKFISH16_COMMIT,
    material_cp, perspective, need,
)

BUDGET = 24000
REFERENCE_NODES = 40000
METHODS = ("A_PV", "B_ONE_REPLY_JSON", "C_THREE_REPLY_POLICY")
CASES = (10, 14)

def run(engine, board, nodes, game, mode, multipv=None, root_moves=None):
    engine.configure({"Use NNUE":mode})
    args={"game":game,"info":chess.engine.INFO_ALL}
    if multipv is not None: args["multipv"]=multipv
    if root_moves is not None:args["root_moves"]=root_moves
    result=engine.analyse(board,chess.engine.Limit(nodes=nodes),**args)
    items=result if isinstance(result,list) else [result]
    need(all("nodes" in x and "score" in x for x in items),"MISSING_INFO")
    return items

def pv_legal(board, path):
    cp=board.copy(stack=True)
    for m in path:
        if m not in cp.legal_moves: return False
        cp.push(m)
    return True

def mode_trial(engine, case_id, board, own, root_uci, mode, budget=BUDGET):
    root=chess.Move.from_uci(root_uci)
    need(root in board.legal_moves,"ILLEGAL_ROOT")
    after=board.copy(stack=True);after.push(root)
    first=run(engine,board,budget,f"p34:{case_id}:{root_uci}:{mode}:A",mode,root_moves=[root])[0]
    need(first.get("pv") and first["pv"][0]==root and pv_legal(board,first["pv"]),"A_PV_ILLEGAL")
    a_reply=first["pv"][1].uci() if len(first["pv"])>1 else None
    a_follow=first["pv"][2].uci() if len(first["pv"])>2 else None
    need(a_reply is not None,"A_NO_OPPONENT_PLY")
    a_nodes=int(first["nodes"])
    half=budget//2
    b_first=run(engine,after,half,f"p34:{case_id}:{root_uci}:{mode}:B_select",mode)[0]
    need(b_first.get("pv") and pv_legal(after,b_first["pv"]),"B_PV_ILLEGAL")
    b_reply=b_first["pv"][0]
    withreply=after.copy(stack=True);withreply.push(b_reply)
    b_next=run(engine,withreply,budget-half,f"p34:{case_id}:{root_uci}:{mode}:B_follow",mode)[0]
    need(pv_legal(withreply,b_next.get("pv",[])),"B_REPLY_PV_ILLEGAL")
    b_nodes=int(b_first["nodes"])+int(b_next["nodes"])
    quarter=budget//4
    top=run(engine,after,quarter,f"p34:{case_id}:{root_uci}:{mode}:C_select",mode,multipv=3)
    need(len(top)==3 and len({x["pv"][0] for x in top})==3,"C_THREE_DISTINCT")
    c_branches=[];c_nodes=int(top[0]["nodes"]) # Multipv shared total search nodes; do NOT triple count
    for i,row in enumerate(top):
        need(pv_legal(after,row.get("pv",[])),"C_PV_ILLEGAL")
        reply=row["pv"][0]
        replyboard=after.copy(stack=True);replyboard.push(reply)
        continuation=run(engine,replyboard,quarter,
              f"p34:{case_id}:{root_uci}:{mode}:C_follow:{i}",mode)[0]
        need(pv_legal(replyboard,continuation.get("pv",[])),"C_CONTINUATION_ILLEGAL")
        c_nodes+=int(continuation["nodes"])
        c_branches.append({"reply":reply.uci(),
                           "follow":continuation["pv"][0].uci() if continuation.get("pv") else None,
                           "after_reply_value_root_cp":perspective(continuation,own)[0],
                           "after_reply_material_root_cp":material_cp(replyboard,own)-material_cp(board,own),
                           "pv": [m.uci() for m in continuation.get("pv",[])[:10]]})
    return {
       "case_id":case_id,"root_uci":root_uci,"mode":mode,"requested_budget_nodes":budget,
       "A_PV":{"actual_nodes":a_nodes,"predicted_replies":[a_reply],"follow":a_follow,
               "root_value_cp":perspective(first,own)[0],
               "pv":[m.uci() for m in first["pv"][:12]]},
       "B_ONE_REPLY_JSON":{"actual_nodes":b_nodes,"predicted_replies":[b_reply.uci()],
               "follow":b_next["pv"][0].uci() if b_next.get("pv") else None,
               "after_reply_root_value_cp":perspective(b_next,own)[0],
               "material_after_reply_cp":material_cp(withreply,own)-material_cp(board,own)},
       "C_THREE_REPLY_POLICY":{"actual_nodes":c_nodes,
               "predicted_replies":[x["reply"] for x in c_branches],"branches":c_branches},
       "spend_model":"requested total nodes 24000 per representation; actual MultiPV shared cost counted once",
    }

def reference_world(engine, board, root_uci, own, nodes=REFERENCE_NODES):
    root=chess.Move.from_uci(root_uci)
    after=board.copy(stack=True);after.push(root)
    vals=[]
    for i,reply in enumerate(sorted(after.legal_moves,key=lambda x:x.uci())):
        nxt=after.copy(stack=True);nxt.push(reply)
        row=run(engine,nxt,nodes,f"p34:oracle:{root_uci}:{reply.uci()}:{i}",True)[0]
        need(pv_legal(nxt,row.get("pv",[])),"REFERENCE_PV_ILLEGAL")
        vals.append({"reply":reply.uci(),"root_value_cp":perspective(row,own)[0],
                     "nodes":int(row["nodes"])})
    need(vals,"EMPTY_REPLY_UNIVERSE")
    return vals

def adjudicate(trial,reference):
    values={x["reply"]:x["root_value_cp"] for x in reference}
    minval=min(values.values())
    summary={}
    for name in METHODS:
        unit=trial[name]
        replies=unit["predicted_replies"]
        need(all(x in values for x in replies),"PREDICTED_REPLY_NOT_LEGAL")
        worst_in_pred=min(values[x] for x in replies)
        summary[name]={"num_replies":len(replies),"actual_nodes":unit["actual_nodes"],
                       "adjudicator_worst_cp":worst_in_pred,
                       "missed_refutation_gap_cp":worst_in_pred-minval,
                       "includes_adjudicator_argmin":any(values[x]==minval for x in replies),
                       "reference_mode":"SF16_NNUE_true_unmodified_frozen_nodes_per_reply"}
    return {"reference_min_cp":minval,
            "reference_argmin_replies":sorted(x for x,v in values.items() if v==minval),
            "reference_legal_reply_count":len(reference),"representations":summary}

def main():
    p=argparse.ArgumentParser()
    for name in ("source","engine","out"):p.add_argument("--"+name,required=True)
    p.add_argument("--budget",type=int,default=BUDGET)
    p.add_argument("--reference-nodes",type=int,default=REFERENCE_NODES)
    args=p.parse_args()
    need(args.budget>=4000 and args.budget%4==0 and args.reference_nodes>=args.budget,
         "BUDGET_SCHEMA")
    source_bytes=Path(args.source).read_bytes()
    need(hashlib.sha256(source_bytes).hexdigest()==FROZEN_SOURCE_SHA256,"SOURCE_SHA")
    source=json.loads(source_bytes)
    cases={x["id"]:x for x in source["selected"]}
    need(set(CASES)<=set(cases),"SOURCE_CASES")
    engine=chess.engine.SimpleEngine.popen_uci(args.engine,timeout=180)
    try:
        engine.configure({"Threads":1,"Hash":16,"Use NNUE":False})
        records=[]
        for case_id in CASES:
            original=cases[case_id]
            board=replay_original(original);own=board.turn
            # Candidate roots were frozen BEFORE this P34 experiment from P33.
            roots={10:("e8f7","e5f4"),14:("c2c3","d5d3")}[case_id]
            for root in roots:
                ref=reference_world(engine,board,root,own,args.reference_nodes)
                trials=[]
                for mode in (False,True):
                    trial=mode_trial(engine,case_id,board,own,root,mode,args.budget)
                    trials.append({"trial":trial,"adjudication":adjudicate(trial,ref)})
                    j=trials[-1]["adjudication"]["representations"]
                    print("P34",case_id,root,"NNUE",mode,"N_REF",len(ref),
                          [(k,round(j[k]["missed_refutation_gap_cp"]),j[k]["actual_nodes"])
                           for k in METHODS],flush=True)
                records.append({"case_id":case_id,"root_uci":root,
                                "full_source_history":True,"reference_all_legal":ref,
                                "trials":trials})
    finally:
        engine.quit()
    result={"schema":"c3x029-p34-equal-requested-node-foil-plan-NNUE-classical-v1",
      "source_sha256":FROZEN_SOURCE_SHA256,"engine_commit":ORIGINAL_STOCKFISH16_COMMIT,
      "source_exposed_adaptive_development":True,"requested_budget_per_method":args.budget,
      "reference_nodes_per_legal_reply":args.reference_nodes,
      "separate_reference_uses_nnue_true":True,
      "reference_independence":"different larger-budget run, SAME engine and same source; not human-independent truth",
      "engine_internals":"unmodified executable; NO NNUE activation, feature, accumulator or search-site instrumentation",
      "conclusion_ceiling":"equal requested nodes only, actual nodes differ; top3 unequal output cardinality",
      "records":records}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
