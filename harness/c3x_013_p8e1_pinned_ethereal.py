#!/usr/bin/env python3
"""P8-E1: descriptive independent-engine signs on all frozen P7 tactic-matched pairs.

Ethereal classical at exact pinned Git commit; NOT causal concept transport.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

PINNED_ETHEREAL_COMMIT="0e47e9b67f345c75eb965d9fb3e2493b6a11d09a"
DEPTHS=(8,12,16)

def sign(x):
    return (x>0)-(x<0)

def observe(exe,board,pair,depth):
    roots=[chess.Move.from_uci(pair[k]) for k in ("a","b")]
    if any(m not in board.legal_moves for m in roots):
        return {"status":"HOLD_ILLEGAL_ROOT"}
    with chess.engine.SimpleEngine.popen_uci(exe,timeout=65) as engine:
        if not {"Hash","Threads","MultiPV"}.issubset(set(engine.options)):
            return {"status":"HOLD_UCI_OPTIONS_UNSUPPORTED","options":list(engine.options)}
        engine.configure({"Threads":1,"Hash":16})
        identity=dict(engine.id)
        info=engine.analyse(board,chess.engine.Limit(depth=depth),
                            root_moves=roots,multipv=2)
    observations={}
    for row in (info if isinstance(info,list) else [info]):
        pv=row.get("pv",[])
        score=row.get("score")
        if not pv or score is None:
            continue
        cp=score.pov(board.turn).score(mate_score=None)
        if cp is None:
            continue
        observations[pv[0].uci()]={"cp":cp,"depth":row.get("depth"),
                                   "nodes":row.get("nodes"),
                                   "pv":[move.uci() for move in pv[:8]]}
    left,right=(observations.get(pair[k]) for k in ("a","b"))
    if not left or not right:
        return {"status":"HOLD_MISSING_ROOT_OR_MATE","raw":observations,"engine_id":identity}
    if left["depth"]!=depth or right["depth"]!=depth:
        return {"status":"HOLD_INCOMPLETE_ROOT_DEPTH","raw":observations,"engine_id":identity}
    return {"status":"CP_DIRECTION_ONLY","gap_cp":left["cp"]-right["cp"],
            "sign":sign(left["cp"]-right["cp"]),
            "engine_id":identity,"raw":observations}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--p7-source",required=True)
    p.add_argument("--p7-outcome",required=True)
    p.add_argument("--engine",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    source_bytes=Path(args.p7_source).read_bytes()
    outcome_bytes=Path(args.p7_outcome).read_bytes()
    source=json.loads(source_bytes)
    outcome=json.loads(outcome_bytes)
    assert source["schema"]=="c3x-013-p7-r1-disjoint-tactical-support-census-v1"
    assert outcome["schema"]=="c3x-013-p7-r2-tactical-cold-near-equal-v1"
    assert outcome["source_groups_frozen"]==32
    assert outcome["source_r1_exact_sha256"]==hashlib.sha256(source_bytes).hexdigest()
    assert outcome["nested_support_counts"]["P7_tactically_filtered"]==8
    sources={(x["broadcast"],x["game_url"]):x for x in source["records"]}
    rows=[]
    for inherited in outcome["records"]:
        key=inherited["broadcast"],inherited["game_url"]
        original=sources.get(key)
        if not original:
            raise ValueError("P7_SOURCE_KEY_MISMATCH")
        out={"broadcast":key[0],"game_url":key[1],"original_P7_status":inherited["status"]}
        frozen_pair=inherited.get("qualification",{}).get("tactically_filtered_pair")
        if not frozen_pair:
            out["status"]="P7_SOURCE_OR_TACTICAL_SUPPORT_HOLD"
            rows.append(out)
            continue
        if original["status"]!="TACTICAL_RULE_SUPPORT_MEASURED":
            raise ValueError("P7_PAIRED_ROOT_SOURCE_NOT_CHESS_LEGAL")
        board=chess.Board(original["fen"])
        if not board.is_valid() or board.is_game_over():
            raise ValueError("P7_SOURCE_FEN_INVALID")
        out["frozen_pair"]=frozen_pair
        out["source_fen_sha256"]=hashlib.sha256(original["fen"].encode()).hexdigest()
        out["stockfish_p7_status"]=inherited["status"]
        out["panels"]={}
        for depth in DEPTHS:
            trials=[observe(args.engine,board,frozen_pair,depth) for _ in (1,2)]
            comparable=all(x["status"]=="CP_DIRECTION_ONLY" for x in trials)
            identical=comparable and trials[0]["gap_cp"]==trials[1]["gap_cp"]
            stockfish=inherited["complete_depth_measurements"][str(depth)]
            sf_rep=stockfish["exact_repeat"]
            sf_gap=stockfish["trials"][0].get("gap_cp") if sf_rep else None
            eth_sign=trials[0].get("sign") if identical else None
            sf_sign=sign(sf_gap) if sf_gap is not None else None
            out["panels"][str(depth)]={
                "ethereal_trials":trials,"ethereal_repeat_exact":identical,
                "stockfish_inherited_gap_cp":sf_gap,
                "stockfish_inherited_repeat_exact":sf_rep,
                "directional_agreement":(
                    eth_sign==sf_sign if eth_sign not in (None,0) and
                    sf_sign not in (None,0) else None)}
        valid=all(row["ethereal_repeat_exact"] for row in out["panels"].values())
        agreements=[row["directional_agreement"] for row in out["panels"].values()]
        eth_signs=[row["ethereal_trials"][0]["sign"] for row in out["panels"].values()
                   if row["ethereal_repeat_exact"]]
        out["across_all_three_depth_signs_stable"]=valid and len(set(eth_signs))==1 and eth_signs[0]!=0
        out["all_depth_direction_concordance"]=valid and all(x is True for x in agreements)
        out["status"]="ENGINE_DIRECTION_OBSERVED_ONLY" if valid else "HOLD_ENGINE_REPEAT_OR_DEPTH"
        rows.append(out)
    counts={s:sum(x["status"]==s for x in rows) for s in sorted(set(x["status"] for x in rows))}
    measured=[x for x in rows if x["status"]=="ENGINE_DIRECTION_OBSERVED_ONLY"]
    result={"schema":"c3x-013-p8-e1-pinned-ethereal-classical-v1",
            "stage":"C3X 0.13 P8-E1",
            "authority":"TWO_ARCHITECTURE_DIRECTIONAL_DIAGNOSTIC_NOT_CONCEPT_CAUSALITY",
            "p7_source_sha256":hashlib.sha256(source_bytes).hexdigest(),
            "p7_outcome_sha256":hashlib.sha256(outcome_bytes).hexdigest(),
            "engine_source_commit":PINNED_ETHEREAL_COMMIT,
            "engine_is_classical_no_nnue":True,
            "engine_binary_sha256":hashlib.sha256(Path(args.engine).read_bytes()).hexdigest(),
            "source_cohort":32,"inherited_tactical_pairs":8,
            "counts":counts,
            "both_engines_all_depth_sign_agreements":sum(x["all_depth_direction_concordance"] for x in measured),
            "ethereal_all_depth_stable_signs":sum(x["across_all_three_depth_signs_stable"] for x in measured),
            "rows":rows,"chess_concept_causal_certificates":[],
            "source_or_engine_independent_confirmation":False,
            "human_utility_measured":False,
            "C3X_014":"CANDIDATE_ONLY_UNOPENED"}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(result,indent=2)+"\n")
    print("P8_E1_TWO_ENGINE_RESULTS",counts,
          "ethereal_sign_stable",result["ethereal_all_depth_stable_signs"],
          "all_depth_concordant",result["both_engines_all_depth_sign_agreements"])
    assert len(rows)==32 and sum(counts.values())==32
    assert not result["chess_concept_causal_certificates"]
if __name__=="__main__":
    main()
