#!/usr/bin/env python3
"""C3X S4-K/R1: independent archived evidence audit of true-go epochs.

Recomputes each bounded per-go trace summary and cross-arm state matching
from the first S4-K native CI artifact. Validates original raw bytes against
the SHA published before this auditor was written. ZERO engine searches.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_030_s4k_epoch_court import compare_by_go

ORIGINAL_SHA256="0beb46fa6188563cc8259933af70fa091154732ecda3f3d6a1bbc0cab281449c"
ORIGINAL_SCHEMA="c3x030-s4k-epoch-tagged-cutoff-development-v1"
ARMS=("sham","two")

def sha(raw):return hashlib.sha256(raw).hexdigest()

def validate_trial(t,key):
    events=t["events"]
    total=t["actual_source_cutoffs_at_this_return_site"]
    if not isinstance(total,int) or total<0 or len(events)!=min(total,8):
        raise ValueError("S4KR1_SOURCE_TOTAL_CONTRACT")
    if t["observed"]!=len(events) or t["right_censored"]!=(total>8) or t["coverage_complete"]!=(total<=8):
        raise ValueError("S4KR1_CENSOR_OR_COVERAGE")
    for index,e in enumerate(events):
        st=e["state"]
        if (e["ordinal"]!=index or len(st)!=7 or
            st[0]!=int(key) or st[4]!=1 or st[5] not in (0,1)
            or st[6] not in (0,1) or st[2]>=st[3]
            or not isinstance(e["return_value"],int)):
            raise ValueError("S4KR1_EVENT_IDENTITY")
    return len(events),total

def audit(raw):
    if sha(raw)!=ORIGINAL_SHA256:
        raise ValueError("S4KR1_ARCHIVED_RAW_SHA_MISMATCH")
    d=json.loads(raw)
    if (d.get("schema")!=ORIGINAL_SCHEMA
        or d.get("verdict")!="PASS_TRIAL_AWARE_SITE_SCOPE_ONLY"
        or d.get("native_searches")!=48 or d.get("native_nodes",0)<=0
        or d.get("control_noninterference") is not True
        or d.get("untouched_holdout") is not True
        or d.get("causal_mediation_proven") is not False):
        raise ValueError("S4KR1_ORIGINAL_SCOPE")
    cases=d.get("cases",{})
    if len(cases)!=8 or len(set(x["game_id"] for x in cases.values()))!=4:
        raise ValueError("S4KR1_INDEPENDENT_GAME_UNIT")
    summaries={name:{"logged":0,"total":0} for name in ARMS}
    shared=unique=ambiguous=changed_values=root_changes=0
    by_case={}
    for case_id,c in sorted(cases.items()):
        if not c["original_sham_noninterference"] or len(c["native_trials"]["two"])!=2:
            raise ValueError("S4KR1_CONTROL_OR_TRIAL")
        traces=c["cutoff_return_trace"]
        k=c["frozen_key"]
        for name in ARMS:
            t=traces[name]
            if set(t["trials"])!={"1","2"}:
                raise ValueError("S4KR1_MISSING_GO_EPOCH")
            logged=total=0
            for epoch in ("1","2"):
                n,m=validate_trial(t["trials"][epoch],k)
                logged+=n;total+=m
            if t["logged_cutoff_events_total"]!=logged or t["all_cutoff_events_total"]!=total:
                raise ValueError("S4KR1_ARM_TOTAL_FALSE")
            summaries[name]["logged"]+=logged
            summaries[name]["total"]+=total
        recomputed=compare_by_go(traces["sham"],traces["two"])
        if recomputed != c["candidate_cross_arm_state_alignment"]:
            raise ValueError("S4KR1_RECOMPUTED_ALIGNMENT_DIFFERS")
        actual=sum(x["bestmove"]!=y["bestmove"] for x,y in zip(c["native_trials"]["sham"],c["native_trials"]["two"]))
        if actual!=c["root_move_changes"] or any(c["per_trial_root_changed"][str(j+1)] !=
            (c["native_trials"]["sham"][j]["bestmove"]!=c["native_trials"]["two"][j]["bestmove"])
            for j in range(2)):
            raise ValueError("S4KR1_ROOT_OUTCOME_FALSE")
        shared+=recomputed["shared_states_total"]
        unique+=recomputed["unambiguous_candidates_total"]
        ambiguous+=recomputed["ambiguous_candidates_total"]
        changed_values+=recomputed["unambiguous_changed_values_total"]
        root_changes+=actual
        by_case[case_id]={"game_id":c["game_id"],"root_changes":actual,
            "sham_total":traces["sham"]["all_cutoff_events_total"],
            "two_total":traces["two"]["all_cutoff_events_total"],
            "unique_state_candidates":recomputed["unambiguous_candidates_total"],
            "changed_values_in_unique_candidates":recomputed["unambiguous_changed_values_total"]}
    if (summaries["sham"]["logged"]!=d["total_tt_cutoff_observations"]["sham"]
        or summaries["two"]["logged"]!=d["total_tt_cutoff_observations"]["two"]
        or summaries["sham"]["total"]!=d["actual_cutoff_events_by_arm"]["sham"]
        or summaries["two"]["total"]!=d["actual_cutoff_events_by_arm"]["two"]
        or shared!=d["candidate_shared_state_total"]
        or unique!=d["candidate_unique_state_total"]
        or ambiguous!=d["candidate_repeated_state_ambiguity_total"]
        or root_changes!=d["root_change_total"]):
        raise ValueError("S4KR1_AGGREGATE_DRIFT")
    return {"schema":"c3x030-s4k-r1-archived-go-epoch-audit-v1",
      "original_sha256":sha(raw),"development_games":4,"development_fens":8,
      "inherited_native_searches":48,"new_native_searches":0,"holdout_searches":0,
      "source_site_logged_events":summaries,
      "common_candidate_states":shared,"unique_candidate_states":unique,
      "ambiguous_candidates":ambiguous,
      "changed_unique_candidate_values":changed_values,
      "root_changes":root_changes,"per_case":by_case,
      "full_search_tree_covered":False,"complete_causal_mediation_proven":False,
      "prior_method_superiority":"HOLD",
      "verdict":"PASS_SOURCE_SITE_AND_TRIAL_REAUDIT_ONLY"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True)
    p.add_argument("--out",required=True)
    x=p.parse_args()
    result=audit(Path(x.original).read_bytes())
    dest=Path(x.out);dest.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,indent=2,sort_keys=True)+"\n").encode()
    dest.write_bytes(raw)
    print("C3X_S4K_R1_ARCHIVED_AUDIT",result["verdict"],
          result["source_site_logged_events"],
          result["unique_candidate_states"],
          result["root_changes"],sha(raw))
if __name__=="__main__":main()
