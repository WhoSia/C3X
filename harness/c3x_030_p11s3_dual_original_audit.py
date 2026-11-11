#!/usr/bin/env python3
"""C3X P11/S3 — zero-search SHA-gated cross-experiment receipt verifier.

Audits actual P11S1 (480 native searches) and P11S2 (140 native searches)
for exact same-FEN comparison, move restoration and original summary integrity.
No chess or engine dependency. No new source causal mediation claims.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

SCHEMA="c3x030-p11s3-verified-state-reset-cross-experiment-audit-v1"
A1="c3x030-p11s1-fullstrength-search-state-factorial-v1"
A2="c3x030-p11s2-reversible-clear-hash-washout-v1"
COMMIT="68e1e9b3811e16cad014b590d7443b9063b3eb52"
ARMS=("cold_fresh_process","same_game_retained","same_game_clear_hash","same_process_new_game")
PHASES=("baseline","warm1","warm2","clear1","postclear_warm1","clear2","postclear_warm2")

def audit(a,b):
    if (a.get("schema")!=A1 or b.get("schema")!=A2
        or a.get("source_commit")!=COMMIT or b.get("source_commit")!=COMMIT
        or a.get("native_searches")!=480 or b.get("total_native_searches")!=140
        or a.get("independent_confirmatory_cohort") is not False
        or b.get("new_holdout_position_cohort") is not False
        or a.get("no_intentional_strength_prng") is not True
        or b.get("chess_engine_skill_level")!=20
        or a.get("binary_sha256")!=b.get("stockfish_binary_sha256")):
        raise ValueError("P11S3_HOLD_SCOPE_OR_BINARY_IDENTITY")
    positions_a=a.get("cohort",{})
    positions_b=b.get("cohort",{})
    if len(positions_a)!=20 or set(positions_a)!=set(positions_b):
        raise ValueError("P11S3_HOLD_20_MATCHED_POSITION_IDS")
    totals={arm:{"within_arm_switch_positions":0,"trials_differing_from_cold":0,
                 "native_nodes":0} for arm in ARMS}
    phases={key:0 for key in ("clear1_restores","clear2_restores",
                              "warm1_differs","warm2_differs",
                              "postclear_warm1_differs","postclear_warm2_differs")}
    phase_nodes_total=0
    baseline_identity_nodes=0
    for key in positions_a:
        s,t=positions_a[key],positions_b[key]
        if s.get("fen")!=t.get("fen") or s.get("history_uci")!=t.get("history_uci"):
            raise ValueError("P11S3_HOLD_MISMATCHED_CHESS_WORLD")
        if set(s.get("arms",{}))!=set(ARMS) or set(t.get("phase_rows",{}))!=set(PHASES):
            raise ValueError("P11S3_HOLD_ARMS_OR_PHASES")
        cold=s["arms"]["cold_fresh_process"]["trials"]
        if len(cold)!=6 or len({r["move_uci"] for r in cold})!=1:
            raise ValueError("P11S3_HOLD_COLD_REFERENCE_UNSTABLE")
        reference=cold[0]["move_uci"]
        if t["phase_rows"]["baseline"]["move_uci"]!=reference:
            raise ValueError("P11S3_HOLD_BASELINE_MOVE_MISMATCH")
        baseline_identity_nodes+=int(t["phase_rows"]["baseline"]["nodes_actual"]==cold[0]["nodes_actual"])
        for arm in ARMS:
            trials=s["arms"][arm].get("trials")
            if not isinstance(trials,list) or len(trials)!=6:
                raise ValueError("P11S3_HOLD_S1_TRIALS")
            c=Counter(row["move_uci"] for row in trials)
            nodes=sum(row["nodes_actual"] for row in trials)
            summary=s["arms"][arm].get("summary",{})
            if (summary.get("counts")!=dict(c) or
                summary.get("actual_nodes_total")!=nodes or
                summary.get("observed_switch") is not (len(c)>1) or
                nodes<=0):
                raise ValueError("P11S3_HOLD_S1_SUMMARY_MISMATCH")
            totals[arm]["native_nodes"]+=nodes
            totals[arm]["within_arm_switch_positions"]+=int(len(c)>1)
            totals[arm]["trials_differing_from_cold"]+=sum(r["move_uci"]!=reference for r in trials)
        orig=t["phase_rows"]
        phase_nodes_total+=sum(row["nodes_actual"] for row in orig.values())
        if any(type(row.get("nodes_actual")) is not int or row["nodes_actual"]<1 for row in orig.values()):
            raise ValueError("P11S3_HOLD_S2_NATIVE_NODES")
        expected={
            "clear1_restores":orig["clear1"]["move_uci"]==reference,
            "clear2_restores":orig["clear2"]["move_uci"]==reference,
            "warm1_differs":orig["warm1"]["move_uci"]!=reference,
            "warm2_differs":orig["warm2"]["move_uci"]!=reference,
            "postclear_warm1_differs":orig["postclear_warm1"]["move_uci"]!=reference,
            "postclear_warm2_differs":orig["postclear_warm2"]["move_uci"]!=reference,
        }
        summary=t.get("summary",{})
        source_key={"postclear_warm1_differs":"after_clear1_warm_differs",
                    "postclear_warm2_differs":"after_clear2_warm_differs"}
        for target,v in expected.items():
            phases[target]+=int(v)
            raw_name=source_key.get(target,target)
            if summary.get(raw_name)!=v:
                raise ValueError("P11S3_HOLD_S2_SUMMARY_MISMATCH:"+raw_name)
    if sum(x["native_nodes"] for x in totals.values())!=a["native_nodes_total"]:
        raise ValueError("P11S3_HOLD_S1_NODE_TOTAL")
    if phase_nodes_total!=b["total_actual_nodes"]:
        raise ValueError("P11S3_HOLD_S2_NODE_TOTAL")
    if (any(totals[arm]["within_arm_switch_positions"]!=a["within_arm_switch_position_counts"][arm] for arm in ARMS)
        or any(totals[arm]["trials_differing_from_cold"]!=a["cross_arm_disagreements_with_cold_reference"][arm] for arm in ARMS)):
        raise ValueError("P11S3_HOLD_S1_AGGREGATE")
    phase_raw_key={"postclear_warm1_differs":"after_clear1_warm_differs",
                   "postclear_warm2_differs":"after_clear2_warm_differs"}
    if any(phases[p]!=b["position_summary_counts"][phase_raw_key.get(p,p)] for p in phases):
        raise ValueError("P11S3_HOLD_S2_AGGREGATE")
    return {"schema":SCHEMA,"record_type":"cross_verified_original_native_search_reanalysis",
            "inherited_S1_real_native_searches":480,"inherited_S2_real_native_searches":140,
            "new_native_searches_performed":0,"source_chess_positions":20,
            "opening_lineage_groups":4,"independent_confirmation":False,
            "actual_original_binary_equal":True,
            "same_FEN_and_source_history_in_both_experiments":True,
            "S1":totals,"S2":phases,
            "S2_baseline_nodes_match_S1_cold_first_trial_count":baseline_identity_nodes,
            "source_event_to_root_causal_mediation_proven":False,
            "TT_only_mediation_proven":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--s1",required=True);ap.add_argument("--s1-sha",required=True)
    ap.add_argument("--s2",required=True);ap.add_argument("--s2-sha",required=True)
    ap.add_argument("--out",required=True)
    p=ap.parse_args()
    raw=[]
    for filename,sha in ((p.s1,p.s1_sha),(p.s2,p.s2_sha)):
        data=Path(filename).read_bytes()
        if len(sha)!=64 or hashlib.sha256(data).hexdigest()!=sha:
            raise ValueError("P11S3_HOLD_SOURCE_RAW_BYTE_SHA")
        raw.append(data)
    report=audit(json.loads(raw[0]),json.loads(raw[1]))
    report["s1_source_sha256"]=p.s1_sha
    report["s2_source_sha256"]=p.s2_sha
    dest=Path(p.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("C3X_P11S3_BOTH_ORIGINALS_CROSS_VERIFIED",json.dumps(report["S1"],sort_keys=True),
          json.dumps(report["S2"],sort_keys=True),"SHA256",hashlib.sha256(dest.read_bytes()).hexdigest())
if __name__=="__main__":main()
