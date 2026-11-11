#!/usr/bin/env python3
"""C3X P11/S4-B: exact-source, preread TT hit-mask vs sham vs original.

The targets are SELECTED FROM THE SEALED S4-A TRACE (not from outcomes in
this trial): first observed hit=1 MAIN search probe with ply=1 per FEN.
Every intervention uses the same source, binary, FEN, two-search UCI protocol.
Target hit bypass changes exactly ss->ttHit for an exact key/ply, but does not
prove a child-parent-root mediation path or a general strategic explanation.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
from c3x_030_p11s4a_native_trace_court import play_session,compare_records,SOURCE_IDS

SCHEMA="c3x030-p11s4b-exact-s4a-first-hit-pl1-target-sham-source-mask-v1"
S4A_SHA="3daa015325a5bd45cc8e63feb9c70bb7a5efb57e6f6f0d73dc9714c14d020c15"
SHAM_KEY="18446744073709551615"

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def first_hit_ply1(events):
    for x in events:
        if x.get("kind")=="probe" and x.get("ply")==1 and " hit=1 " in x.get("raw",""):
            key=x.get("key")
            if not isinstance(key,str) or not key.isdigit():
                raise ValueError("S4B_HOLD_INVALID_PREDECLARED_KEY")
            if key==SHAM_KEY:raise ValueError("S4B_HOLD_SHAM_COLLISION")
            return key
    raise ValueError("S4B_HOLD_NO_SOURCE_PLY1_HIT")

def mask_session(binary,fen,key):
    prior=os.environ.get("C3X_S4B_TARGET_TT_KEY")
    os.environ["C3X_S4B_TARGET_TT_KEY"]=key
    try:return play_session(binary,fen)
    finally:
        if prior is None:os.environ.pop("C3X_S4B_TARGET_TT_KEY",None)
        else:os.environ["C3X_S4B_TARGET_TT_KEY"]=prior

def contacts(receipt):
    lines=[x for x in receipt["stderr_other"] if x.startswith("C3X_S4B_MASKED ")]
    for line in lines:
        if " ply=1 " not in line or " hit_became=0" not in line:
            raise ValueError("S4B_HOLD_BAD_PHYSICAL_MASK_RECEIPT")
    return len(lines)

def evaluate(original,sham,target):
    equal=compare_records(original,dict(sham,events=[]))
    target_compare=compare_records(sham,dict(target,events=[]))
    return {"baseline_matches_sham":equal["noninterference_pass"],
            "baseline_sham_mismatches":equal["mismatches"],
            "target_vs_sham_mismatches":target_compare["mismatches"],
            "target_changed_bestmove_trials":sum(a["bestmove"]!=b["bestmove"]
                    for a,b in zip(sham["trials"],target["trials"])),
            "target_changed_eval_trials":sum(a["score"]!=b["score"]
                    for a,b in zip(sham["trials"],target["trials"])),
            "target_changed_depth_trials":sum(a["depth"]!=b["depth"]
                    for a,b in zip(sham["trials"],target["trials"]))}

def run(source,binary,masked):
    if sha(source)!=S4A_SHA:raise ValueError("S4B_HOLD_SEALED_S4A_SOURCE_SHA")
    d=json.loads(Path(source).read_bytes())
    if d.get("schema")!="c3x030-p11s4a-stockfish16-readonly-TT-tracer-noninterference-v1" or not d.get("noninterference_pass"):
        raise ValueError("S4B_HOLD_S4A_GATE_NOT_PASS")
    if d.get("baseline_binary_sha256")!=sha(binary):
        raise ValueError("S4B_HOLD_SOURCE_BASELINE_BINARY_DRIFT")
    if sha(binary)==sha(masked):raise ValueError("S4B_HOLD_SAME_BINARY")
    out={"schema":SCHEMA,"source_commit":d["source_commit"],
         "S4A_original_json_sha256":S4A_SHA,
         "unmodified_original_binary_sha256":sha(binary),
         "target_and_sham_same_masked_binary_sha256":sha(masked),
         "targets_preselected_by_first_ply1_hit_in_S4A":True,
         "S4A_original_trace_first_hit_rule":"first event with kind probe, ply=1, hit=1",
         "sham_key":SHAM_KEY,"cohort_is_previously_observed_development":True,
         "new_holdout_confirmation":False,"source_child_parent_root_mediation_proven":False,
         "original_TT_entries_physically_overwritten":False,
         "positions":{}}
    for id in SOURCE_IDS:
        packet=d["positions"][id]
        if not packet["audit"]["noninterference_pass"]:
            raise ValueError("S4B_HOLD_NO_PROVEN_S4A_NONINTERFERENCE")
        key=first_hit_ply1(packet["trace_events"])
        baseline=play_session(binary,packet["fen"])
        sham=mask_session(masked,packet["fen"],SHAM_KEY)
        target=mask_session(masked,packet["fen"],key)
        sham_count=contacts(sham)
        target_count=contacts(target)
        result=evaluate(baseline,sham,target)
        out["positions"][id]={"fen":packet["fen"],"history_uci":packet["history_uci"],
            "target_original_TT_key":key,
            "target_s4a_original_probe_event":next(x["raw"] for x in packet["trace_events"]
                if x["kind"]=="probe" and x["ply"]==1 and x["key"]==key and " hit=1 " in x["raw"]),
            "sham_physical_mask_contacts":sham_count,
            "target_physical_mask_contacts_logged":target_count,
            "original_trials":baseline["trials"],
            "sham_trials":sham["trials"],
            "target_trials":target["trials"],
            "comparison":result}
        print("S4B_EXACT_NATIVE_MASK",id,
              "target_key",key,"contacts",target_count,
              "root_switches",result["target_changed_bestmove_trials"],
              "sham_matches_baseline",result["baseline_matches_sham"],flush=True)
    out["native_searches"]=len(SOURCE_IDS)*3*2
    out["total_native_nodes"]=sum(
        sum(t["nodes"] for mode in ("original_trials","sham_trials","target_trials")
            for t in x[mode]) for x in out["positions"].values())
    out["physical_contact_each_target"]=all(
        x["target_physical_mask_contacts_logged"]>0 for x in out["positions"].values())
    out["negative_sham_contact_zero"]=all(
        x["sham_physical_mask_contacts"]==0 for x in out["positions"].values())
    out["sham_noninterference_all"]=all(
        x["comparison"]["baseline_matches_sham"] for x in out["positions"].values())
    out["root_bestmove_changes_after_target_mask_trials"]=sum(
        x["comparison"]["target_changed_bestmove_trials"] for x in out["positions"].values())
    out["status"]=("PASS_EXACT_NATIVE_SOURCE_HIT_MASK_WITH_CONTROLS" if
        out["physical_contact_each_target"] and out["negative_sham_contact_zero"]
        and out["sham_noninterference_all"] else "HOLD_SHAM_OR_TARGET_PHYSICAL_CONTACT")
    return out

def main():
    p=argparse.ArgumentParser()
    for v in ("s4a-original","baseline","masked","out"):
        p.add_argument("--"+v,required=True)
    a=vars(p.parse_args())
    report=run(a["s4a_original"],a["baseline"],a["masked"])
    f=Path(a["out"]);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("S4B_CAUSAL_SOURCE_HIT_PILOT",report["status"],
          "ROOT_CHANGE_TRIALS",report["root_bestmove_changes_after_target_mask_trials"],
          "ACTUAL_NATIVE_SEARCHES",report["native_searches"],
          "ACTUAL_NODES",report["total_native_nodes"],"JSON_SHA256",sha(f),flush=True)
    if not report["status"].startswith("PASS_"):raise SystemExit(2)

if __name__=="__main__":main()
