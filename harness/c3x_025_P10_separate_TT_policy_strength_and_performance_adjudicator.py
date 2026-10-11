#!/usr/bin/env python3
"""C3X0.25 P10: SEPARATE TT optimization performance and paired-chess contract.
Synthetic negative-control smoke test only; never a real Elo or speedup claim.
"""
import argparse,hashlib,json,math,random,statistics
from pathlib import Path
SCHEMA="c3x025-P10-source-blind-paired-color-original-TT-policy-performance-court-v1"
R0="SF16_ORIGINAL_UNCHANGED"
ARMS=("R1_MOVE_HINT_ONLY","R2_NUMERIC_TT_BOUND_ONLY","R3_PROBE_REFRESH_ONLY",
      "R4_AGE_DEPTH_REPLACEMENT_ONLY")
SEED=20261011
MIN_PAIRS=100
B=10000
def bounds(pairs,seed=SEED,reps=B):
    rng=random.Random(seed)
    means=[(p["A_white_points"]+p["A_black_points"])/2 for p in pairs]
    n=len(means)
    if n<1:raise ValueError("P10_NO_ORIGINAL_COMPLETE_COLOR_PAIRS")
    samples=[]
    for _ in range(reps):
        s=sum(means[rng.randrange(n)] for _ in range(n))/n-0.5
        samples.append(s)
    samples.sort()
    return [samples[int(.025*(reps-1))],samples[int(.975*(reps-1))]]
def adjudicate(manifest:dict,pairs:list[dict])->dict:
    """Input final opponent/score labels are independently observed real game data
    or tagged synthetic; no native game playing capability implied here.
    """
    if manifest.get("schema")!="c3x025-P10-separate-engine-optimization-prereg-source-v1":
        raise ValueError("P10_NO_FROZEN_PRE_TREATMENT_OPTIMIZATION_MANIFEST")
    if manifest.get("baseline")!=R0 or manifest.get("candidate") not in ARMS:
        raise ValueError("P10_UNREGISTERED_OR_COMBINED_TT_ARM")
    if manifest.get("source_unseen_and_disjoint") is not True:
        raise ValueError("P10_EXPOSED_TT_M4_POSITIONS_NOT_INDEPENDENT")
    if manifest.get("color_swap_pairing") is not True or manifest.get("stop_after_pairs")!=len(pairs):
        raise ValueError("P10_STOPPING_RULE_OR_COLOR_SWAP_NOT_ORIGINAL")
    if manifest.get("GPL_rights_scope_verified") is not True:
        raise ValueError("P10_MODIFIED_ENGINE_LICENSE_SCOPE_UNCHECKED")
    if manifest.get("source_mode") not in ("SYNTHETIC_TEST_ONLY","NATIVE_ORIGINAL_MATCHES"):
        raise ValueError("P10_UNKNOWN_NATIVE_EVIDENCE_SOURCE")
    seen=set()
    for i,p in enumerate(pairs):
        if p.get("opening_index")!=i+1 or p.get("opening_index") in seen:
            raise ValueError("P10_COMPLETE_ORIGINAL_PAIRED_ORDER_MISSING")
        seen.add(i+1)
        if p.get("same_opening_hash_confirmed") is not True or p.get("opponent_color_swapped") is not True:
            raise ValueError("P10_ORIGINAL_COLOR_PAIRED_GAME_OR_OPENING_DRIFT")
        if p.get("both_legal_and_complete") is not True:
            raise ValueError("P10_ILLEGAL_OR_CENSORED_UNRESOLVED_GAME")
        if p.get("same_engine_build_contract") is not True:
            raise ValueError("P10_HARDWARE_OR_BUILD_CONTRACT_NOT_MAINTAINED")
        for k in ("A_white_points","A_black_points"):
            if p.get(k) not in (0,0.5,1):raise ValueError("P10_BAD_PAIRED_GAME_RESULT")
    low,high=bounds(pairs)
    mean=sum(p["A_white_points"]+p["A_black_points"] for p in pairs)/(2*len(pairs))
    if manifest["source_mode"]=="SYNTHETIC_TEST_ONLY":
        adjudication="SYNTHETIC_SMOKE_TEST__NO_ENGINE_STRENGTH_CLAIM"
    elif len(pairs)<MIN_PAIRS:
        adjudication="HOLD_UNDERPOWERED_PREDECLARED_MINIMUM"
    elif manifest.get("performance_native_nodes_time_verified") is not True:
        adjudication="HOLD_NO_NATIVE_NODE_TIME_AND_MEMORY_EVIDENCE"
    elif low<=0:
        adjudication="NO_SIGNIFICANT_POSITIVE_PAIRED_GAME_STRENGTH_EVIDENCE"
    else:
        adjudication="PAIRED_SCORE_POSITIVE_UNDER_FIXED_PROTOCOL__REPLICATE_INDEPENDENTLY"
    return {"schema":SCHEMA,"candidate":manifest["candidate"],"baseline":R0,
      "game_strength_optimization_status":adjudication,
      "opponent_color_swap_pairs":len(pairs),
      "individual_complete_original_games":2*len(pairs),
      "candidate_mean_game_score":mean,
      "candidate_minus_original_game_points":mean-0.5,
      "paired_10k_bootstrap_95pct_game_point_improvement":[low,high],
      "paired_original_openings_primary_sampling_unit":True,
      "fixed_seed":SEED,"bootstrap_repetitions":B,
      "minimum_color_swap_pairs_for_positive_inference":MIN_PAIRS,
      "no_Elo_claim_when_synthetic_or_unpowered":True,
      "real_native_Stockfish_chess_games_executed_by_this_program":False,
      "actual_native_TT_speedup_proven":False,
      "source_type":manifest["source_mode"]}
def demo()->dict:
    """Tiny reproducible symbolic data with zero net claimed gain."""
    pairs=[{"opening_index":i+1,"same_opening_hash_confirmed":True,
            "opponent_color_swapped":True,"both_legal_and_complete":True,
            "same_engine_build_contract":True,"A_white_points":0.5,"A_black_points":0.5}
           for i in range(8)]
    manifest={"schema":"c3x025-P10-separate-engine-optimization-prereg-source-v1",
              "baseline":R0,"candidate":ARMS[0],
              "source_unseen_and_disjoint":True,"color_swap_pairing":True,
              "stop_after_pairs":8,"GPL_rights_scope_verified":True,
              "source_mode":"SYNTHETIC_TEST_ONLY",
              "performance_native_nodes_time_verified":False}
    result=adjudicate(manifest,pairs)
    if result["game_strength_optimization_status"]!="SYNTHETIC_SMOKE_TEST__NO_ENGINE_STRENGTH_CLAIM":
        raise AssertionError("P10_INVALID_SYNTHETIC_OPTIMIZATION_CLAIM")
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    p.add_argument("--manifest")
    p.add_argument("--pairs")
    a=p.parse_args()
    if bool(a.manifest)!=bool(a.pairs):raise ValueError("P10_BOTH_MANIFEST_AND_RESULTS_REQUIRED")
    result=adjudicate(json.loads(Path(a.manifest).read_text()),
                      json.loads(Path(a.pairs).read_text())) if a.manifest else demo()
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X025_P10_SEPARATE_TT_PERFORMANCE_NEGATIVE_CONTROL",result,flush=True)
    print("C3X025_P10_PROTOCOL_SMOKE_JSON_SHA256",hashlib.sha256(target.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
