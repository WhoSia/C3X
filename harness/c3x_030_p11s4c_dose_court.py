#!/usr/bin/env python3
"""C3X P11/S4C2 actual native same-binary TT-hit-dose test.

Precommitted selected keys from SHA-frozen S4B before native execution.
Six conditions per identical FEN: upstream, sham (unreachable 64-bit key),
zero matching-hit suppressions, one, two, and unbounded (10,000).
The last FIVE conditions run exactly the SAME compiled modified binary.
Each condition receives TWO consecutive UCI searches in one process.
A no-root-switch outcome is scientifically valid and must not be hidden.
"""
import argparse,hashlib,json,os
from pathlib import Path
from c3x_030_p11s4a_native_trace_court import play_session,compare_records

RAW_S4B_SHA="081ee839f883d538081f1d2d15c43db1aa31cb12e4e713e1cda81815d5e59300"
SCHEMA="c3x030-p11s4c2-same-binary-tt-hit-dose-v1"
KEY_SHAM="18446744073709551615"
ARMS=("upstream","sham","zero","one","two","unbounded")
DOSES={"sham":10000,"zero":0,"one":1,"two":2,"unbounded":10000}
COHORT=("queens_gambit_ply4","sicilian_najdorf_ply4","english_ply4")
MARKER="C3X_S4C2_MASK "

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def patched_search(binary,fen,key,dose):
    old_key=os.environ.get("C3X_S4C2_KEY")
    old_dose=os.environ.get("C3X_S4C2_LIMIT")
    os.environ["C3X_S4C2_KEY"]=key
    os.environ["C3X_S4C2_LIMIT"]=str(dose)
    try:return play_session(binary,fen)
    finally:
        if old_key is None:os.environ.pop("C3X_S4C2_KEY",None)
        else:os.environ["C3X_S4C2_KEY"]=old_key
        if old_dose is None:os.environ.pop("C3X_S4C2_LIMIT",None)
        else:os.environ["C3X_S4C2_LIMIT"]=old_dose

def physical_events(receipt):
    events=[s for s in receipt["stderr_other"] if s.startswith(MARKER)]
    for line in events:
        if " ply=1 " not in line or " new_hit=0" not in line or " parent_move_raw=" not in line:
            raise ValueError("S4C2_HOLD_MALFORMED_SOURCE_EVENT")
    return events

def run(frozen,upstream,patched):
    if sha(frozen)!=RAW_S4B_SHA:raise ValueError("S4C2_HOLD_FROZEN_SOURCE_SHA")
    prior=json.loads(Path(frozen).read_bytes())
    if prior.get("status")!="PASS_EXACT_NATIVE_SOURCE_HIT_MASK_WITH_CONTROLS" or prior.get("schema")!="c3x030-p11s4b-exact-s4a-first-hit-pl1-target-sham-source-mask-v1":
        raise ValueError("S4C2_HOLD_SOURCE_EVIDENCE_STATUS")
    if prior.get("unmodified_original_binary_sha256")!=sha(upstream) or sha(upstream)==sha(patched):
        raise ValueError("S4C2_HOLD_INCONSISTENT_ENGINE_PROVENANCE")
    report={"schema":SCHEMA,"frozen_S4B_raw_sha256":RAW_S4B_SHA,
       "upstream_binary_sha256":sha(upstream),"all_dose_arms_same_binary_sha256":sha(patched),
       "cohort_previously_seen_development_only":True,
       "independent_confirmation":False,"exact_child_parent_root_mediation_proven":False,
       "specified_source_key_policy":"first ply1 hit in original sealed S4A trace",
       "dosage_measures_matching_hit_flag_suppressions_per_process_across_search_templates":True,
       "arm_order":list(ARMS),"positions":{}}
    for posid in COHORT:
        entry=prior["positions"][posid]
        key=entry["target_original_TT_key"]
        fen=entry["fen"]
        runs={"upstream":play_session(upstream,fen)}
        for arm in ARMS[1:]:
            k=KEY_SHAM if arm=="sham" else key
            runs[arm]=patched_search(patched,fen,k,DOSES[arm])
        count={arm:len(physical_events(runs[arm])) for arm in ARMS}
        comparisons={arm:compare_records(runs["sham"],dict(runs[arm],events=[]))
                     for arm in ARMS}
        if count["sham"] or count["zero"]:
            raise ValueError("S4C2_HOLD_CONTACT_IN_NEGATIVE_CONTROL")
        if count["one"]!=1 or count["two"]!=2 or count["unbounded"]<2:
            raise ValueError("S4C2_HOLD_UNEXPECTED_PHYSICAL_DOSE")
        report["positions"][posid]={
            "fen":fen,"history_uci":entry["history_uci"],
            "original_S4A_selected_key":key,
            "physical_logged_mask_contacts":count,
            "native_search_results":{a:runs[a]["trials"] for a in ARMS},
            "raw_mask_event_receipts":{a:physical_events(runs[a]) for a in ARMS[1:]},
            "comparison_vs_sham":{a:{"changed_fields":comparisons[a]["mismatches"],
                "final_bestmove_change_trials":sum(
                     t["bestmove"]!=s["bestmove"]
                     for s,t in zip(runs["sham"]["trials"],runs[a]["trials"]))}
                     for a in ARMS},
            "upstream_equal_sham":comparisons["upstream"]["noninterference_pass"],
            "target_zero_equal_sham":comparisons["zero"]["noninterference_pass"]}
        print("S4C2_REAL_NATIVE_DOSE",posid,"events",count,
              "root_changes",{a:report["positions"][posid]["comparison_vs_sham"][a]["final_bestmove_change_trials"]
                              for a in ARMS},flush=True)
    report["native_searches"]=len(COHORT)*len(ARMS)*2
    report["actual_nodes_total"]=sum(row["nodes"] for p in report["positions"].values()
           for trials in p["native_search_results"].values() for row in trials)
    report["root_bestmove_change_trial_totals"]={a:sum(
        p["comparison_vs_sham"][a]["final_bestmove_change_trials"] for p in report["positions"].values())
        for a in ARMS}
    report["source_mask_contact_totals_logged"]={a:sum(
        p["physical_logged_mask_contacts"][a] for p in report["positions"].values())
        for a in ARMS}
    report["negative_controls_pass"]=all(
        p["upstream_equal_sham"] and p["target_zero_equal_sham"]
        for p in report["positions"].values())
    report["status"]="PASS_PHYSICAL_DOSE_WITH_NEGATIVE_CONTROLS" if report["negative_controls_pass"] else "HOLD_NEGATIVE_CONTROLS"
    return report

def main():
    p=argparse.ArgumentParser()
    for name in ("s4b-original","original-binary","dose-binary","out"):
        p.add_argument("--"+name,required=True)
    a=vars(p.parse_args())
    result=run(a["s4b_original"],a["original_binary"],a["dose_binary"])
    dest=Path(a["out"]);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("S4C2_NATIVE_FINAL",result["status"],"ROOT",result["root_bestmove_change_trial_totals"],
          "ACTUAL_SEARCHES",result["native_searches"],"NODES",result["actual_nodes_total"],
          "JSON_SHA",sha(dest),flush=True)
    if not result["status"].startswith("PASS_"):raise SystemExit(2)

if __name__=="__main__":main()
