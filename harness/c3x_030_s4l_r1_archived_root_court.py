#!/usr/bin/env python3
"""C3X 0.30 S4-L/R1: SHA-pinned independent re-audit of actual root score receipts.

It does NOT join root scores to a specific TT intervention. It checks root
update predicates, event ordinals, per-true-UCI-go totals, loss from bounded
logging, unchanged source negative controls and root move choice outcomes.
"""
import argparse,hashlib,json
from pathlib import Path

ORIGINAL_SHA="a27b961985d2ba4475f51916c41be3426d8a32d3130bce0fab04497ca2eac5c9"
ORIGINAL_SCHEMA="c3x030-s4l-root-update-trace-development-v1"

def sha(raw):return hashlib.sha256(raw).hexdigest()
def audit(raw):
    if sha(raw)!=ORIGINAL_SHA:raise ValueError("S4LR1_NOT_IMMUTABLE_ORIGINAL_BYTES")
    d=json.loads(raw)
    if (d.get("schema")!=ORIGINAL_SCHEMA or
        d.get("native_searches")!=48 or d.get("native_nodes",0)<=0 or
        d.get("verdict")!="PASS_ROOT_SCORE_RECEIPT_SITE_ONLY" or
        d.get("control_noninterference") is not True or
        d.get("untouched_holdout") is not True or
        d.get("causal_mediation_proven") is not False):
        raise ValueError("S4LR1_SOURCE_SCOPE_INVALID")
    cases=d["cases"]
    if len(cases)!=8 or len({x["game_id"] for x in cases.values()})!=4:
        raise ValueError("S4LR1_CORRELATED_GAMES")
    arms=("sham","two")
    sums={arm:{"logged":0,"total":0,"censored_go_epochs":0,
               "logged_best_improvements":0,"target_tt_cutoffs":0} for arm in arms}
    changes=0
    per_case={}
    for case_id,c in sorted(cases.items()):
        if not c["original_sham_noninterference"]:
            raise ValueError("S4LR1_CONTROL_INTERFERENCE")
        if len(c["native_trials"]["sham"])!=2 or len(c["native_trials"]["two"])!=2:
            raise ValueError("S4LR1_TWO_TRIALS_REQUIRED")
        true_changes=[]
        for n in range(2):
            true_changes.append(c["native_trials"]["sham"][n]["bestmove"]!=c["native_trials"]["two"][n]["bestmove"])
        if (sum(true_changes)!=c["root_move_changes"] or
            c["per_trial_root_changed"]!={str(n+1):v for n,v in enumerate(true_changes)}):
            raise ValueError("S4LR1_ROOT_OUTCOME_FABRICATED")
        changes+=sum(true_changes)
        row={"game_id":c["game_id"],"root_changes":sum(true_changes)}
        for arm in arms:
            trace=c["cutoff_return_trace"][arm]
            if set(trace["trials"])!={"1","2"}:
                raise ValueError("S4LR1_GO_EPOCH_IDENTITY")
            logged=total=improvements=cutoffs=0
            for epoch in ("1","2"):
                t=trace["trials"][epoch]
                root=t["root_score_receipts"]
                n=t["root_score_total_at_this_site"]
                if (not isinstance(n,int) or n<0 or
                    len(root)!=min(n,512) or
                    t["root_score_right_censored"]!=(n>512) or
                    t["root_candidate_update_site_covered"]!=(n<=512) or
                    t["not_tied_to_specific_tt_invocation"] is not True):
                    raise ValueError("S4LR1_ROOT_SITE_COVERAGE")
                for i,r in enumerate(root):
                    if (r["ordinal"]!=i or str(r["epoch"])!=epoch or
                        r["will_update_best"]!=(r["value"]>r["old_best"]) or
                        r["will_update_root_pv"]!=(r["move_count"]==1 or r["value"]>r["alpha"]) or
                        r["alpha"]>=r["beta"] or r["move_count"]<1):
                        raise ValueError("S4LR1_FALSE_ROOT_DECISION")
                if len(t["events"])!=t["observed"] or t["right_censored"] != (t["actual_source_cutoffs_at_this_return_site"]>8):
                    raise ValueError("S4LR1_TT_SITE_SCOPE")
                logged+=len(root);total+=n
                improvements+=sum(r["will_update_best"] for r in root)
                cutoffs+=t["actual_source_cutoffs_at_this_return_site"]
                sums[arm]["censored_go_epochs"]+=int(n>512)
            if trace["logged_root_score_events_total"]!=logged or trace["all_root_score_events_total"]!=total:
                raise ValueError("S4LR1_ROOT_ARM_TOTAL")
            sums[arm]["logged"]+=logged;sums[arm]["total"]+=total
            sums[arm]["logged_best_improvements"]+=improvements
            sums[arm]["target_tt_cutoffs"]+=cutoffs
            row[arm]={"logged_root_scores":logged,"all_root_scores":total}
        per_case[case_id]=row
    if (changes!=d["root_change_total"] or
        any(sums[arm]["logged"]!=d["root_update_receipts_by_arm"][arm]
            or sums[arm]["total"]!=d["root_update_total_by_arm"][arm]
            or sums[arm]["target_tt_cutoffs"]!=d["actual_cutoff_events_by_arm"][arm]
            for arm in arms)):
        raise ValueError("S4LR1_AGGREGATE_DRIFT")
    return {"schema":"c3x030-s4l-r1-independent-archived-root-update-audit-v1",
      "original_native_sha256":sha(raw),"new_native_searches":0,
      "inherited_native_searches":48,"inherited_nodes":d["native_nodes"],
      "development_games":4,"development_positions":8,"holdout_searches":0,
      "arms":sums,"root_move_changes":changes,"per_case":per_case,
      "target_tt_site_fully_counted":True,
      "root_score_site_has_censoring":any(sums[a]["censored_go_epochs"]>0 for a in arms),
      "cross_arm_root_score_event_identity_proven":False,
      "particular_tt_mask_to_root_score_causal_mediation_proven":False,
      "paper_superiority":"HOLD",
      "verdict":"PASS_ARCHIVED_SOURCE_ROOT_SCORE_SITE_ONLY"}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=audit(Path(a.original).read_bytes())
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    serialized=(json.dumps(result,indent=2,sort_keys=True)+"\n").encode()
    dest.write_bytes(serialized)
    print("C3X_S4L_R1_ARCHIVED_ROOT",result["verdict"],result["arms"],sha(serialized))
if __name__=="__main__":main()
