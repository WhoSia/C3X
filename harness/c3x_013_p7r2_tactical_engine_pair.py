#!/usr/bin/env python3
"""P7-R2: fixed post-tactical cold-pair qualification, development only.

Input is the complete frozen source-only R1 court, including all 32 denominator
groups and their failed/held positions. Root scores are not explanatory causes.
"""
import argparse,hashlib,json
from pathlib import Path
import chess,chess.engine
from harness.c3x_012_six_source_qualify import cold
from harness.c3x_013_p7r1_tactical_support import hazard
from c3x_explain.concepts import candidate_delta

DEPTHS=(8,12,16)

def sign(x):return (x>0)-(x<0)

def root_pair_gate(board,a,b,strict=False):
    """Tactical-hazard equivalence is necessary only, not sufficient."""
    aa=hazard(board,chess.Move.from_uci(a))
    bb=hazard(board,chess.Move.from_uci(b))
    cls=("mover","captured","gives_check","promotion","castling","recapture_types")
    if any(aa[k]!=bb[k] for k in cls):return False
    if strict and a[:2]!=b[:2]:return False
    return True

def qualification(exe,board):
    cold10=[]
    all_moves=sorted(board.legal_moves,key=lambda m:m.uci())
    for move in all_moves:
        result=cold(exe,board,10000,only=move)
        if result and result["uci"]==move.uci():
            cold10.append(result)
    top=sorted(cold10,key=lambda x:(-x["cp"],x["uci"]))[:8]
    checked=[]
    for x in top:
        move=chess.Move.from_uci(x["uci"])
        repeats=[cold(exe,board,30000,only=move) for _ in range(2)]
        if all(q and q["uci"]==move.uci() for q in repeats) and repeats[0]["cp"]==repeats[1]["cp"]:
            checked.append({"uci":move.uci(),"cp":repeats[0]["cp"]})
    context=cold(exe,board,80000)
    best=context["uci"] if context else None
    anch=next((z for z in checked if z["uci"]==best),None)
    options=[]
    if anch:
        for peer in checked:
            if peer["uci"]==best:continue
            gap=abs(peer["cp"]-anch["cp"])
            if gap<=50:
                a,b=sorted((peer["uci"],best))
                options.append((gap,a,b))
    options.sort()
    paired=lambda vals:{"a":vals[1],"b":vals[2],"cold_gap_cp":vals[0]}
    base=next((paired(pair) for pair in options),None)
    filtered=next((paired(pair) for pair in options
                   if root_pair_gate(board,pair[1],pair[2])),None)
    strict=next((paired(pair) for pair in options
                 if root_pair_gate(board,pair[1],pair[2],strict=True)),None)
    return {"legal_moves":len(all_moves),
            "cold_nonmate_roots":len(cold10),
            "candidate_top8":[z["uci"] for z in top],
            "exact_repeated_roots":[z["uci"] for z in checked],
            "contextual_bestmove":best,"base_pair":base,
            "tactically_filtered_pair":filtered,
            "same_origin_strict_pair":strict,
            "pre_depth_eligible_peer_count":len(options)}

def fixed_depth(exe,board,pair,depth):
    roots=[chess.Move.from_uci(pair["a"]),chess.Move.from_uci(pair["b"])]
    with chess.engine.SimpleEngine.popen_uci(exe,timeout=45) as eng:
        eng.configure({"Threads":1,"Hash":16})
        info=eng.analyse(board,chess.engine.Limit(depth=depth),
                         multipv=2,root_moves=roots)
    found={}
    for item in info:
        if not item.get("pv") or item.get("score") is None:continue
        cp=item["score"].pov(board.turn).score(mate_score=None)
        if cp is None:continue
        found[item["pv"][0].uci()]={"cp":cp,"depth":item.get("depth"),
                                   "pv":[m.uci() for m in item["pv"][:8]],
                                   "nodes":item.get("nodes")}
    a,b=found.get(pair["a"]),found.get(pair["b"])
    if not a or not b:
        return {"status":"HOLD_MISSING_PV_CP_OR_MATE","raw":found}
    if a["depth"]!=depth or b["depth"]!=depth:
        return {"status":"HOLD_INCOMPLETE_DEPTH","raw":found}
    return {"status":"COMPARABLE_CP_ONLY","depth":depth,"cp_a":a["cp"],"cp_b":b["cp"],
            "gap_cp":a["cp"]-b["cp"],"raw":found}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-court",required=True)
    p.add_argument("--engine",default="/usr/games/stockfish")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    raw=Path(a.source_court).read_bytes()
    court=json.loads(raw)
    assert court["schema"]=="c3x-013-p7-r1-disjoint-tactical-support-census-v1"
    assert court["new_frozen_broadcast_groups"]==32
    assert court["frozen_segment_digest"]=="e5ca78464ef6bb2e95271c12428c47e8f9535efca9674d1048aed029ef1584c0"
    results=[]
    for x in court["records"]:
        row={"broadcast":x["broadcast"],"game_url":x["game_url"],
             "selection_rank":x["selection_rank"],"source_status":x["status"]}
        if x["status"]!="TACTICAL_RULE_SUPPORT_MEASURED":
            row["status"]="SOURCE_HOLD";results.append(row);continue
        board=chess.Board(x["fen"])
        try:
            qual=qualification(a.engine,board)
            row["qualification"]=qual
            pair=qual["tactically_filtered_pair"]
            if not pair:
                row["status"]="HOLD_NO_TACTICALLY_MATCHED_PAIR"
            else:
                delta=candidate_delta(board,chess.Move.from_uci(pair["a"]),
                                      chess.Move.from_uci(pair["b"]))
                row["frozen_feature_contrast"]=delta["played_minus_alternative"]
                row["frozen_tactical_signatures"]={k:hazard(board,chess.Move.from_uci(pair[k]))
                                                   for k in ("a","b")}
                row["complete_depth_measurements"]={}
                for depth in DEPTHS:
                    trials=[fixed_depth(a.engine,board,pair,depth) for _ in range(2)]
                    compar=all(v["status"]=="COMPARABLE_CP_ONLY" for v in trials)
                    exact=compar and trials[0]["gap_cp"]==trials[1]["gap_cp"]
                    margin=bool(exact and abs(trials[0]["gap_cp"])<=50)
                    row["complete_depth_measurements"][str(depth)]={
                        "trials":trials,"exact_repeat":exact,
                        "within_50_cp":margin}
                vals=list(row["complete_depth_measurements"].values())
                good=all(v["exact_repeat"] and v["within_50_cp"] for v in vals)
                signs={sign(v["trials"][0]["gap_cp"]) for v in vals if v["exact_repeat"]}
                row["all_depth_marginal"]=good
                row["all_depth_same_nonzero_orientation"]=good and len(signs)==1 and 0 not in signs
                row["status"]=("STABLE_DESCRIPTIVE_NEAR_EQUAL_ONLY"
                               if row["all_depth_same_nonzero_orientation"]
                               else "HOLD_DEPTH_OR_DIRECTION_OR_SUPPORT")
        except Exception as exc:
            row.update({"status":"EXECUTION_HOLD","error_type":type(exc).__name__,
                        "error_excerpt":str(exc)[:240]})
        results.append(row)
    counts={k:sum(row["status"]==k for row in results)
            for k in sorted(set(row["status"] for row in results))}
    base=sum(bool(z.get("qualification",{}).get("base_pair")) for z in results)
    filtered=sum(bool(z.get("qualification",{}).get("tactically_filtered_pair")) for z in results)
    strict=sum(bool(z.get("qualification",{}).get("same_origin_strict_pair")) for z in results)
    out={"schema":"c3x-013-p7-r2-tactical-cold-near-equal-v1",
         "authority":"TYPED_TACTICAL_SUPPORT_YIELD_AND_ENGINE_RANKS_ONLY",
         "source_r1_exact_sha256":hashlib.sha256(raw).hexdigest(),
         "stockfish_binary_sha256":hashlib.sha256(Path(a.engine).read_bytes()).hexdigest(),
         "source_groups_frozen":32,"legal_source_groups":sum(z["status"]=="TACTICAL_RULE_SUPPORT_MEASURED" for z in court["records"]),
         "nested_support_counts":{"P5_style_cold_base":base,"P7_tactically_filtered":filtered,
                                  "same_origin_strict":strict},
         "source_status_counts":counts,"records":results,
         "causal_strategic_certificate":None,
         "cross_engine_transport_tested":False,
         "human_outcome_tested":False,
         "0_14_status":"UNOPENED_CANDIDATE_ONLY"}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("P7R2_BASE_FILTER_STRICT",out["nested_support_counts"])
    print("P7R2_SOURCE_STATUS",counts)
    assert len(results)==32 and base>=filtered>=strict
    if any(z["status"]=="EXECUTION_HOLD" for z in results):
        raise SystemExit("P7R2_INFRA_EXECUTION_HOLD_REQUIRES_REVIEW")
if __name__=="__main__":main()
