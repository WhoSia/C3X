#!/usr/bin/env python3
"""C3X018 held-out from #6/#8 focal choice: ten frozen independent-source roots.

No root selected by resulting TT effect. First eligible F-only full-key
consumer is chosen by fixed within-world rule, then W1/W2/R tested regardless
of outcome, including null contacts and no-effect outcomes. All 10 retained.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need,select_candidate
COHORT_IDS=(1,2,3,4,5,7,9,10,11,12)

def main():
    p=argparse.ArgumentParser()
    for key in ("cohort","prior","patched","out"):p.add_argument("--"+key,required=True)
    args=p.parse_args()
    cohort=json.loads(Path(args.cohort).read_text())
    prior=json.loads(Path(args.prior).read_text())
    assert len(cohort["selected"])==12 and len(prior["worlds"])==12
    output={"schema":"c3x018-10-heldout-original-game-histories-source-TT-challenge-v1",
            "frozen_cases":list(COHORT_IDS),
            "prior_sha256":hashlib.sha256(Path(args.prior).read_bytes()).hexdigest(),
            "same_selection_dataset_as_focal":True,
            "independent_source_game_histories":"inherited_P2_12_distinct_GameURL_SHA",
            "cases":[]}
    for case_id in COHORT_IDS:
        source=cohort["selected"][case_id-1]
        assert source["id"]==case_id
        historical=prior["worlds"][case_id-1]["cells"]
        row={"id":case_id,"geometry_candidate":source["geometry_candidate"],
             "historical_root_bestmove_changed":prior["worlds"][case_id-1]["contrasts"]["categorical_bestmove_changed"],
             "status":"UNTESTED"}
        try:
            control={}
            for arm in ("O","F","Z"):
                first=play(args.patched,source,arm,"OBS")
                need(first["UCI"]==historical[arm]["UCI"],
                     f"PASSIVE_CORE_DRIFT_{case_id}_{arm}")
                control[arm]=first
            need(control["O"]["UCI"]==control["Z"]["UCI"],f"ZERO_CONTACT_{case_id}")
            target,basis=select_candidate(control["O"]["consumer_records"],
                                          control["F"]["consumer_records"])
            row.update(status="TARGET_IDENTIFIED" if target else "NO_ELIGIBLE_TT_TARGET",
                       target_selection=basis,target=target,
                       controls={k:control[k]["UCI"] for k in control},
                       observation={k:control[k]["lineage_summary"] for k in control})
            if target:
                decoy={"key64":18446744073709551615,"slot":0,"epoch":1}
                no_contact=play(args.patched,source,"F","W",decoy,writer_budget=2)
                need(no_contact["UCI"]==control["F"]["UCI"] and
                     no_contact["lineage_summary"]["writer_block"]==0,
                     f"DECOY_FAIL_{case_id}")
                row["decoy_no_contact_exact"]=True
                treatment={}
                for mode,budget in (("W1",1),("W2",2),("R",None)):
                    real_mode="R" if mode=="R" else "W"
                    a=play(args.patched,source,"F",real_mode,target,writer_budget=budget)
                    b=play(args.patched,source,"F",real_mode,target,writer_budget=budget)
                    need(a==b,f"COLD_REPLAY_{case_id}_{mode}")
                    t=a["lineage_summary"]
                    treatment[mode]={
                        "UCI":a["UCI"],
                        "write_blocks":t["writer_block"],
                        "reader_blocks":t["reader_block"],
                        "root_choice_changed_from_F":a["UCI"]["bestmove"]!=control["F"]["UCI"]["bestmove"],
                        "full_core_changed_from_F":a["UCI"]!=control["F"]["UCI"]
                    }
                    print("C3X018_HOLDOUT",case_id,mode,"W",t["writer_block"],
                          "R",t["reader_block"],"move",a["UCI"]["bestmove"],flush=True)
                row["treatments"]=treatment
                row["status"]="EXPERIMENTED"
        except (RuntimeError,ValueError,KeyError) as ex:
            row["status"]="HOLD_FAIL_CLOSED"
            row["failure"]=type(ex).__name__+":"+str(ex)[:250]
        output["cases"].append(row)
    need([x["id"] for x in output["cases"]]==list(COHORT_IDS),
         "HOLDOUT_DENOMINATOR_INCOMPLETE")
    output["summary"]={
        "total_frozen":10,
        "experimented":sum(x["status"]=="EXPERIMENTED" for x in output["cases"]),
        "no_eligible":sum(x["status"]=="NO_ELIGIBLE_TT_TARGET" for x in output["cases"]),
        "hold":sum(x["status"]=="HOLD_FAIL_CLOSED" for x in output["cases"]),
        "W2_root_choice_changes":sum(x.get("treatments",{}).get("W2",{}).get("root_choice_changed_from_F",False)
                                       for x in output["cases"]),
        "R_root_choice_changes":sum(x.get("treatments",{}).get("R",{}).get("root_choice_changed_from_F",False)
                                       for x in output["cases"])}
    output["limitations"]=[
      "10 other frozen game histories, but from the same preselected cohort; no independently sampled ecosystem",
      "Within-world TT target chosen from F observation; no source contact oracle independent of F",
      "All worlds retained, even if target absent, operator not fired, trace censored or output unchanged",
      "Two-block intervention affects two attempted writes and can alter future paths, not exclusive TT score mediator",
      "Full64 writer shadow and actual early TT cutoff branch do not cover all TT uses",
      "Exploratory replication does not establish root chess motif understanding"]
    Path(args.out).write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("C3X018_TEN_FROZEN_INDEPENDENT_HISTORIES_AUDIT_MATERIALIZED",
          json.dumps(output["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
