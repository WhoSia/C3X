#!/usr/bin/env python3
"""P5-B: cold chess pair eligibility and held-different-depth feature predictions."""
import argparse,hashlib,json
from pathlib import Path
import chess,chess.engine
from c3x_explain.concepts import candidate_delta
from harness.c3x_012_six_source_qualify import cold

FEATURES={
 "CENTER":("own_center_occupancy_count",1),
 "ISOLATION":("own_isolated_pawn_count",-1),
 "PASSED":("own_passed_pawn_count",1)
}
SIGN=lambda x:(x>0)-(x<0)

def qualify(engine,board):
    initial=[]
    for m in sorted(board.legal_moves,key=lambda m:m.uci()):
        q=cold(engine,board,10000,only=m)
        if q and q["uci"]==m.uci():initial.append(q)
    top=sorted(initial,key=lambda v:(-v["cp"],v["uci"]))[:8]
    stable=[]
    for row in top:
        move=chess.Move.from_uci(row["uci"])
        checks=[cold(engine,board,30000,only=move) for _ in (0,1)]
        if all(x and x["uci"]==move.uci() for x in checks) and checks[0]["cp"]==checks[1]["cp"]:
            stable.append({"uci":move.uci(),"cp":checks[0]["cp"]})
    context=cold(engine,board,80000)
    best=context["uci"] if context else None
    anchor=next((x for x in stable if x["uci"]==best),None)
    pairs=[]
    if anchor:
        for x in stable:
            if x["uci"]==best:continue
            gap=abs(x["cp"]-anchor["cp"])
            if gap<=50:pairs.append((gap,min(best,x["uci"]),max(best,x["uci"])))
    pairs.sort()
    return {"eligible_nonmate_roots":len(initial),"stable_candidates":len(stable),
            "context_best":best,
            "pair":({"a":pairs[0][1],"b":pairs[0][2],"cold_gap":pairs[0][0]} if pairs else None)}

def depth_probe(engine,board,pair):
    roots=[chess.Move.from_uci(pair[k]) for k in ("a","b")]
    with chess.engine.SimpleEngine.popen_uci(engine,timeout=25) as proc:
        proc.configure({"Threads":1,"Hash":16})
        rows=proc.analyse(board,chess.engine.Limit(depth=12),multipv=2,root_moves=roots)
    found={}
    for row in rows:
        if not row.get("pv") or not row.get("score"):continue
        cp=row["score"].pov(board.turn).score(mate_score=None)
        if cp is not None:
            found[row["pv"][0].uci()]={"cp":cp,"depth":row.get("depth")}
    a,b=found.get(pair["a"]),found.get(pair["b"])
    if not a or not b or a["depth"] is None or a["depth"]!=b["depth"]:
        return {"status":"HOLD_MATE_MISSING_OR_DEPTH","raw":found}
    return {"status":"DEPTH12_COMPARABLE","a_cp":a["cp"],"b_cp":b["cp"],
            "depth":a["depth"],"delta_a_minus_b":a["cp"]-b["cp"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--p5a",required=True);p.add_argument("--engine",default="/usr/games/stockfish")
    p.add_argument("--output",required=True);a=p.parse_args()
    raw=Path(a.p5a).read_bytes()
    source=json.loads(raw)
    assert source["schema"]=="c3x-013-p5-semantic-source-court-v1"
    assert source["sampled_events"]==16
    output={"schema":"c3x-013-p5b-source-disjoint-predictive-rival-v1",
            "authority":"DEVELOPMENT_PREDICTION_ONLY_NOT_CAUSAL_CONCEPT",
            "source_p5a_sha256":hashlib.sha256(raw).hexdigest(),
            "engine_sha256":hashlib.sha256(Path(a.engine).read_bytes()).hexdigest(),
            "samples":[]}
    for initial in source["records"]:
        rec={"broadcast":initial["broadcast"],"source_status":initial["status"]}
        if initial["status"]!="BOARD_FACT_ONLY":
            rec["verdict"]="SOURCE_HOLD";output["samples"].append(rec);continue
        b=chess.Board(initial["fen"])
        try:
            eligibility=qualify(a.engine,b)
            rec["qualification"]=eligibility
            pair=eligibility["pair"]
            if not pair:
                rec["verdict"]="HOLD_NO_NEAR_EQUAL_PAIR"
            else:
                delta=candidate_delta(b,chess.Move.from_uci(pair["a"]),
                                      chess.Move.from_uci(pair["b"]))["played_minus_alternative"]
                rec["frozen_concept_deltas"]={k:delta.get(key,0) for k,(key,_) in FEATURES.items()}
                trials=[depth_probe(a.engine,b,pair) for _ in range(2)]
                rec["independent_depth12_repeats"]=trials
                if any(z["status"]!="DEPTH12_COMPARABLE" for z in trials):
                    rec["verdict"]="HOLD_UNCOMPARABLE_DEPTH"
                elif trials[0]["delta_a_minus_b"]!=trials[1]["delta_a_minus_b"]:
                    rec["verdict"]="HOLD_REPEAT_DISAGREEMENT"
                else:
                    observed=SIGN(trials[0]["delta_a_minus_b"])
                    rec["predictions"]={}
                    for name,(_,direction) in FEATURES.items():
                        d=rec["frozen_concept_deltas"][name]
                        rec["predictions"][name]={"feature_sign":SIGN(d),
                            "tested":bool(d and observed),
                            "agreement":SIGN(d)*direction==observed if d and observed else None}
                    rec["verdict"]="DEVELOPMENT_PREDICTION_OBSERVED"
        except Exception as err:
            rec["verdict"]="EXECUTION_HOLD";rec["error"]=str(err)[:200]
        output["samples"].append(rec)
    outcome={}
    for name in FEATURES:
        p=[r["predictions"][name] for r in output["samples"] if r.get("verdict")=="DEVELOPMENT_PREDICTION_OBSERVED"]
        tested=[z for z in p if z["tested"]]
        counts={"tested_groups":len(tested),"agreements":sum(z["agreement"] for z in tested),
                "positive_feature_delta":sum(z["feature_sign"]>0 for z in tested),
                "negative_feature_delta":sum(z["feature_sign"]<0 for z in tested)}
        counts["polarities_supported"]=counts["tested_groups"]>=4 and min(counts["positive_feature_delta"],counts["negative_feature_delta"])>=2
        outcome[name]=counts
    output["predictive_development"]=outcome
    output["status_counts"]={x:sum(r["verdict"]==x for r in output["samples"]) for x in sorted(set(r["verdict"] for r in output["samples"]))}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(output,indent=2)+"\n")
    print("P5B_SOURCE_DENOMINATOR",len(output["samples"]),output["status_counts"])
    print("P5B_CONCEPT_PREDICTION",outcome)
    assert len(output["samples"])==16
    if "EXECUTION_HOLD" in output["status_counts"]:raise SystemExit("P5B_EXECUTION_HOLD")
if __name__=="__main__":main()
