#!/usr/bin/env python3
"""C3X P11/S4C1 actual Stockfish native single-encounter TT-hit experiment.

S4B frozen source key, but only ONE physical matching hit flag per OS process
is changed in S4C1. Same modified binary in irrelevant-key sham and active arms.
No coercion of root switch success: zero change is publishable negative result.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

from c3x_030_p11s4a_native_trace_court import play_session,compare_records

SCHEMA="c3x030-p11s4c1-once-only-hit-sham-native-v1"
SOURCE_SHA="081ee839f883d538081f1d2d15c43db1aa31cb12e4e713e1cda81815d5e59300"
SHAM="18446744073709551615"
IDS=("queens_gambit_ply4","sicilian_najdorf_ply4","english_ply4")
MARKER="C3X_S4C_SINGLE_HIT "

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run_keyed(binary,fen,key):
    before=os.environ.get("C3X_S4C_FIRST_HIT_KEY")
    os.environ["C3X_S4C_FIRST_HIT_KEY"]=key
    try:return play_session(binary,fen)
    finally:
        if before is None:os.environ.pop("C3X_S4C_FIRST_HIT_KEY",None)
        else:os.environ["C3X_S4C_FIRST_HIT_KEY"]=before

def events(record):
    original=record["stderr_other"]
    lines=[s for s in original if s.startswith(MARKER)]
    if any(" ply=1 " not in x or " old_hit=1 new_hit=0" not in x
           or " parent_move_raw=" not in x for x in lines):
        raise ValueError("S4C_HOLD_BAD_PHYSICAL_EVENT_RECEIPT")
    return lines

def main_run(previous,baseline,patched):
    if sha(previous)!=SOURCE_SHA:
        raise ValueError("S4C_HOLD_FROZEN_S4B_RAW_SHA")
    r=json.loads(Path(previous).read_bytes())
    if r.get("schema")!="c3x030-p11s4b-exact-s4a-first-hit-pl1-target-sham-source-mask-v1" or r.get("status")!="PASS_EXACT_NATIVE_SOURCE_HIT_MASK_WITH_CONTROLS":
        raise ValueError("S4C_HOLD_SOURCE_S4B_PASS")
    if r["unmodified_original_binary_sha256"]!=sha(baseline) or sha(patched)==sha(baseline):
        raise ValueError("S4C_HOLD_SOURCE_BINARIES")
    out={"schema":SCHEMA,"frozen_original_S4B_json_sha256":SOURCE_SHA,
         "baseline_native_binary_sha256":sha(baseline),
         "same_sham_and_target_native_binary_sha256":sha(patched),
         "selected_position_keys_before_S4C_outcomes":True,
         "exactly_one_claim_shared_across_search_templates":True,
         "independent_holdout_cohort":False,
         "ancestral_return_value_transmission_proven":False,
         "single_event_first_hit_claim_global_per_engine_process":True,
         "position_data":{}}
    for id in IDS:
        old=r["positions"][id]
        fen=old["fen"];key=old["target_original_TT_key"]
        original=play_session(baseline,fen)
        sham=run_keyed(patched,fen,SHAM)
        active=run_keyed(patched,fen,key)
        mask_events=events(active);sham_events=events(sham)
        sham_compare=compare_records(original,dict(sham,events=[]))
        target_compare=compare_records(sham,dict(active,events=[]))
        if len(mask_events)>1:
            raise ValueError("S4C_HOLD_MORE_THAN_ONE_EVENT_RECORDED")
        if len(sham_events):
            raise ValueError("S4C_HOLD_SHAM_HIT")
        out["position_data"][id]={
            "fen":fen,"original_history_uci":old["history_uci"],
            "S4A_preselected_exact_key":key,
            "source_single_encounter_receipt":mask_events,
            "sham_source_events":sham_events,
            "original_trials":original["trials"],
            "sham_trials":sham["trials"],
            "single_hit_trials":active["trials"],
            "sham_equal_to_original":sham_compare["noninterference_pass"],
            "single_hit_vs_sham_changed_fields":target_compare["mismatches"],
            "root_bestmove_changes":sum(a["bestmove"]!=b["bestmove"]
                for a,b in zip(sham["trials"],active["trials"])),
            "score_changes":sum(a["score"]!=b["score"]
                for a,b in zip(sham["trials"],active["trials"])),
        }
        print("S4C_SINGLE_NATIVE",id,"physical_contacts",len(mask_events),
              "root_changes",out["position_data"][id]["root_bestmove_changes"],
              "sham_ok",sham_compare["noninterference_pass"],flush=True)
    out["native_searches"]=len(IDS)*3*2
    out["native_nodes_total"]=sum(t["nodes"] for p in out["position_data"].values()
        for arm in ("original_trials","sham_trials","single_hit_trials") for t in p[arm])
    out["one_and_only_one_hit_each"]=all(
        len(x["source_single_encounter_receipt"])==1 for x in out["position_data"].values())
    out["all_shams_noninterfering"]=all(
        x["sham_equal_to_original"] for x in out["position_data"].values())
    out["number_of_target_root_changes"]=sum(
        x["root_bestmove_changes"] for x in out["position_data"].values())
    out["status"]=("PASS_ONE_SOURCE_TT_HIT_NATIVE_GATE" if
        out["one_and_only_one_hit_each"] and out["all_shams_noninterfering"] else
        "HOLD_SINGLE_HIT_NOT_PROVEN_OR_SHAM_DRIFT")
    return out

def main():
    p=argparse.ArgumentParser()
    for name in ("s4b-original","baseline","single-hit-binary","out"):
        p.add_argument("--"+name,required=True)
    a=vars(p.parse_args())
    d=main_run(a["s4b_original"],a["baseline"],a["single_hit_binary"])
    out=Path(a["out"]);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("S4C_NATIVE_ONE_HIT",d["status"],"root_changes",
        d["number_of_target_root_changes"],"searches",d["native_searches"],
        "nodes",d["native_nodes_total"],"JSON_SHA256",sha(out),flush=True)
    if not d["status"].startswith("PASS_"):raise SystemExit(2)

if __name__=="__main__":main()
