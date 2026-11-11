#!/usr/bin/env python3
"""P11 R1: exact-SHA audit of 20-position native repeatability results.

Separate (a) within-arm switching across six identical requested settings
from (b) alternate-arm disagreement with a deterministic cold single-thread
reference. Four openings (five positions each) share ancestry; these are
NOT 20 independent game clusters. No new native engine searches.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

SCHEMA = "c3x030-p11-precommitted-20-position-full-strength-repetition-v1"
AUDIT_SCHEMA = "c3x030-p11-r1-verified-position-group-comparison-v1"
ARMS = ("cold_single", "warm_single", "cold_parallel4")
FAMILIES = ("ruy_lopez", "queens_gambit", "sicilian_najdorf", "english")

def reanalyze(raw):
    if raw.get("schema") != SCHEMA or raw.get("source_commit") != "68e1e9b3811e16cad014b590d7443b9063b3eb52":
        raise ValueError("P11R_HOLD_ORIGINAL_SOURCE_ID")
    if (raw.get("repeats_per_arm") != 6
            or raw.get("total_native_searches") != 360
            or raw.get("skill_level") != 20
            or raw.get("intentional_handicap_rng_enabled") is not False
            or raw.get("classical_evaluation_nnue_disabled") is not True
            or raw.get("native_source_causal_intervention_performed") is not False):
        raise ValueError("P11R_HOLD_SCOPE")
    positions = raw.get("cohort")
    if not isinstance(positions, dict) or len(positions) != 20:
        raise ValueError("P11R_HOLD_COHORT")
    seen = set()
    results = {}
    totals = {arm:{"within_position_switches":0,
                   "positions_with_any_reference_disagreement":0,
                   "trials_disagreeing_with_cold_reference":0,
                   "native_nodes":0} for arm in ARMS}
    by_family = defaultdict(lambda: {arm:0 for arm in ARMS})
    all_nodes = 0
    for id, item in positions.items():
        matched = [f for f in FAMILIES if id.startswith(f+"_ply")]
        if len(matched)!=1 or not id.endswith(("ply4","ply6","ply8","ply10","ply12")):
            raise ValueError("P11R_HOLD_POSITION_ID")
        family=matched[0]
        fen = item.get("fen")
        if not isinstance(fen,str) or fen in seen:
            raise ValueError("P11R_HOLD_FEN_DUPLICATE")
        seen.add(fen)
        if set(item.get("arms",{}))!=set(ARMS):
            raise ValueError("P11R_HOLD_ARMS")
        measured={}
        for arm in ARMS:
            block=item["arms"][arm]
            trials=block.get("trials")
            if not isinstance(trials,list) or len(trials)!=6:
                raise ValueError("P11R_HOLD_TRIAL_COUNT")
            counts=Counter(t["move_uci"] for t in trials)
            computed_nodes=sum(t["nodes_actual"] for t in trials)
            if any(type(t.get("nodes_actual")) is not int or t["nodes_actual"] <= 0 for t in trials):
                raise ValueError("P11R_HOLD_NATIVE_NODES")
            summary=block.get("summary",{})
            if (summary.get("counts")!=dict(counts)
                or summary.get("actual_nodes_total")!=computed_nodes
                or summary.get("switch_observed") is not (len(counts)>1)):
                raise ValueError("P11R_HOLD_TAMPERED_SUMMARY")
            totals[arm]["native_nodes"]+=computed_nodes
            totals[arm]["within_position_switches"]+=int(len(counts)>1)
            by_family[family][arm]+=int(len(counts)>1)
            all_nodes+=computed_nodes
            measured[arm]=counts
        cold=measured["cold_single"]
        if len(cold)!=1:
            raise ValueError("P11R_HOLD_COLD_REFERENCE_NOT_UNANIMOUS")
        reference=next(iter(cold))
        results[id]={"opening_family":family,"cold_reference_uci":reference,
                     "move_counts":{a:dict(sorted(measured[a].items())) for a in ARMS},
                     "disagreement_counts":{}}
        for arm in ARMS:
            disagreement=6-measured[arm].get(reference,0)
            results[id]["disagreement_counts"][arm]=disagreement
            totals[arm]["trials_disagreeing_with_cold_reference"]+=disagreement
            totals[arm]["positions_with_any_reference_disagreement"]+=int(disagreement>0)
    if len(seen)!=20 or any(sum(id.startswith(f+"_") for id in positions)!=5 for f in FAMILIES):
        raise ValueError("P11R_HOLD_OPENING_GROUPS")
    if all_nodes!=raw["total_actual_native_nodes"]:
        raise ValueError("P11R_HOLD_NODE_SUM")
    return {
        "schema":AUDIT_SCHEMA,
        "status":"REAL_ORIGINAL_P11_FROZEN_RECORD_REANALYSIS",
        "native_searches_performed_during_this_audit":0,
        "inherited_native_searches":360,
        "inherited_native_nodes":all_nodes,
        "source_chess_position_count":20,
        "source_opening_family_count":4,
        "independent_game_count_for_inference":None,
        "six_repeats_per_position_and_arm":True,
        "within_arm_position_variability_NOT_equal_cross_arm_reference_disagreement":True,
        "totals":totals,
        "per_opening_family_within_arm_position_switches":dict(by_family),
        "positions":results,
        "all_position_repeats_independent":False,
        "native_source_causal_intervention_proven":False,
        "hypothesis_that_default_stockfish_samples_RL_policy_proven":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--source-sha256",required=True)
    p.add_argument("--out",required=True)
    x=p.parse_args()
    original=Path(x.input).read_bytes()
    if len(x.source_sha256)!=64 or hashlib.sha256(original).hexdigest()!=x.source_sha256:
        raise ValueError("P11R_HOLD_ORIGINAL_BYTE_SHA")
    report=reanalyze(json.loads(original))
    report["original_P11_raw_json_sha256"]=x.source_sha256
    target=Path(x.out); target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("C3X_P11R_ORIGINAL_AUDIT_SUCCESS",
          json.dumps(report["totals"],sort_keys=True),
          "RAW_OUTPUT_SHA",hashlib.sha256(target.read_bytes()).hexdigest())

if __name__=="__main__":
    main()
