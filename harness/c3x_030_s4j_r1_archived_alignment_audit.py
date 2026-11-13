#!/usr/bin/env python3
"""C3X S4-J/R1: independent re-audit of S4-J source-native archived bytes.

Reject invented uniqueness, repeated event identities and fabricated values.
A matching state tuple is only a candidate; never declare causal mediation.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_030_s4j_state_alignment import compare,parse

ORIGINAL_SHA="cdfa9d7ba18052a8fee19905c864883f68adb4bda30809da0a4719bb6f60c6d8"
SCHEMA="c3x030-s4j-native-candidate-search-state-development-v1"

def digest(x):return hashlib.sha256(x).hexdigest()

def audit(raw):
    if digest(raw)!=ORIGINAL_SHA:raise ValueError("S4JR1_ARCHIVED_RAW_BYTES_MISMATCH")
    x=json.loads(raw)
    if (x.get("schema")!=SCHEMA or x.get("verdict")!="PASS_BOUNDED_CANDIDATE_STATE_ALIGNMENT_ONLY"
        or x.get("native_searches")!=48 or x.get("native_nodes",0)<=0
        or x.get("control_noninterference") is not True or x.get("untouched_holdout") is not True
        or x.get("causal_mediation_proven") is not False):
        raise ValueError("S4JR1_SCOPE_CONTRACT")
    cases=x.get("cases",{})
    if len(cases)!=8 or len({c["game_id"] for c in cases.values()})!=4:
        raise ValueError("S4JR1_CASES_CORRELATED_FEN")
    totals={"sham":0,"two":0,"shared":0,"unique":0,"ambiguous":0,"changed_values":0,"root_changes":0}
    by_case={}
    for name,c in sorted(cases.items()):
        if not c["original_sham_noninterference"]:
            raise ValueError("S4JR1_FALSE_CONTROL_NONINTERFERENCE")
        data=c["cutoff_return_trace"]
        for arm in ("sham","two"):
            d=data[arm]
            raw_events=d["events"]
            if d["observed"]!=len(raw_events) or d["observed_cutoffs"]!=len(raw_events):
                raise ValueError("S4JR1_FALSE_EVENT_COUNT")
            if d["right_censored"]!=(len(raw_events)==8):
                raise ValueError("S4JR1_FALSE_CENSOR")
            for i,e in enumerate(raw_events):
                st=e["state"]
                if (e["ordinal"]!=i or st[0]!=int(c["frozen_key"])
                    or st[4]!=1 or st[5] not in (0,1) or st[6] not in (0,1) or st[2]>=st[3]):
                    raise ValueError("S4JR1_FALSE_EVENT_STATE")
        candidate=compare(data["sham"],data["two"])
        recorded=c["candidate_cross_arm_state_alignment"]
        if candidate!=recorded:
            raise ValueError("S4JR1_CANDIDATE_ALIGNMENT_RECOMPUTE_MISMATCH")
        counts={arm:data[arm]["observed"] for arm in ("sham","two")}
        shared=candidate["shared_candidate_state_count"]
        unique=len(candidate["unique_candidate_states"])
        ambiguous=len(candidate["ambiguous_repeated_states"])
        changed=sum(z["value_diff"]!=0 for z in candidate["unique_candidate_states"])
        for arm in ("sham","two"):totals[arm]+=counts[arm]
        totals["shared"]+=shared;totals["unique"]+=unique
        totals["ambiguous"]+=ambiguous;totals["changed_values"]+=changed
        totals["root_changes"]+=c["root_move_changes"]
        by_case[name]={"game_id":c["game_id"],"root_move_changes":c["root_move_changes"],
            "sham_observed":counts["sham"],"two_observed":counts["two"],
            "shared_candidate_states":shared,"unique_candidate_states":unique,
            "repeated_ambiguous_states":ambiguous,"different_values_in_unique_candidates":changed,
            "censored":candidate["any_right_censoring"]}
    if (totals["sham"]!=x["total_tt_cutoff_observations"]["sham"]
        or totals["two"]!=x["total_tt_cutoff_observations"]["two"]
        or totals["shared"]!=x["candidate_shared_state_total"]
        or totals["unique"]!=x["candidate_unique_state_total"]
        or totals["ambiguous"]!=x["candidate_repeated_state_ambiguity_total"]
        or totals["root_changes"]!=x["root_change_total"]):
        raise ValueError("S4JR1_SUMMARY_NOT_REPRODUCIBLE")
    return {"schema":"c3x030-s4j-r1-archived-candidate-state-audit-v1",
      "source_sha256":digest(raw),"native_searches_inherited":48,"new_native_searches":0,
      "development_games":4,"development_positions":8,"holdout_runs":0,
      "totals":totals,"cases":by_case,
      "cross_arm_invocation_identity_proven":False,
      "complete_tt_to_root_mediation_proven":False,
      "effect_on_human_quality_or_prior_papers":"HOLD",
      "verdict":"PASS_ARCHIVED_CANDIDATE_ALIGNMENT_ONLY"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=audit(Path(a.original).read_bytes())
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,indent=2,sort_keys=True)+"\n").encode()
    target.write_bytes(raw)
    print("S4JR1_ARCHIVED_REAUDIT",result["verdict"],result["totals"],digest(raw))

if __name__=="__main__":main()
