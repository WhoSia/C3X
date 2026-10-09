#!/usr/bin/env python3
"""C3X 0.18 frozen #6/#8 physical TT writer dose-response replication.

Fixed source-exact keys/slot epochs transferred from sealed exploratory
C3X018 6/8 receipt; no reselecting after seeing treatment outputs.
N=0,1,2,4,8,16,32,64,128 matching accepted write attempts are blocked.
This is exploratory dose response, not identification of a unique mediator.
"""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play, need

TARGETS={
 6:{"key64":3293258168769270517,"slot":0,"epoch":2},
 8:{"key64":14544738779862901516,"slot":0,"epoch":1},
}
BUDGETS=(0,1,2,4,8,16,32,64,128)
SEAL="c3x018-physical-TT-epoch-sticky-vs-single-write-native-falsification-v1"

def main():
    p=argparse.ArgumentParser()
    for key in ("cohort","prior","preseal","patched","out"):
        p.add_argument("--"+key,required=True)
    args=p.parse_args()
    frozen=json.loads(Path(args.preseal).read_text())
    need(frozen["schema"]==SEAL, "FROZEN_PRESEAL_INVALID")
    for case in frozen["single_write_repair"]["cases"]:
        need(case["W_contacts"]==1 and case["R_contacts"]==1,
             "EARLIER_SINGLE_CONTACT_INVALID")
    data=json.loads(Path(args.cohort).read_text())
    old=json.loads(Path(args.prior).read_text())
    result={
      "schema":"c3x018-physical-TT-suppression-dose-response-6-8-v1",
      "preseal_sha256":hashlib.sha256(Path(args.preseal).read_bytes()).hexdigest(),
      "cohort_sha256":hashlib.sha256(Path(args.cohort).read_bytes()).hexdigest(),
      "prior_original_P4_sha256":hashlib.sha256(Path(args.prior).read_bytes()).hexdigest(),
      "preregistered_budgets":list(BUDGETS),
      "target_rule":"PRESEALED_FULL64_SLOT_EPOCH_FROM_PRIOR_F_ONLY_OBSERVER",
      "cases":[]
    }
    for case_id in (6,8):
        world=data["selected"][case_id-1]
        need(world["id"]==case_id,"FROZEN_ORDER")
        prior=old["worlds"][case_id-1]["cells"]
        controls={}
        for mode in ("O","F","Z"):
            run=play(args.patched,world,mode,"OBS")
            need(run["UCI"]==prior[mode]["UCI"],
                 "PRIOR_NONINTERFERENCE_"+str(case_id)+"_"+mode)
            controls[mode]=run["UCI"]
        need(controls["O"]==controls["Z"],"O_Z_SHAM_DIFF")
        target=TARGETS[case_id]
        row={
           "id":case_id,"target":target,
           "controls":controls,
           "writer_dose_results":[],
           "selection_limit":"Prior candidate selected on F same dataset: not independent"
        }
        decoy={"key64":18446744073709551615,"slot":0,"epoch":1}
        no_contact=play(args.patched,world,"F","W",decoy,writer_budget=128)
        need(no_contact["UCI"]==controls["F"],
             "DECOY_WRITER_BUDGET_CHANGED_CORE_"+str(case_id))
        need(no_contact["lineage_summary"]["writer_block"]==0,
             "DECOY_WRITER_BUDGET_CONTACT_"+str(case_id))
        for budget in BUDGETS:
            a=play(args.patched,world,"F","W",target,writer_budget=budget)
            b=play(args.patched,world,"F","W",target,writer_budget=budget)
            need(a==b,f"DOSE_COLD_REPEAT_{case_id}_{budget}")
            actual=a["lineage_summary"]["writer_block"]
            need(actual<=budget,f"WRITER_DOSE_OVERRUN_{case_id}_{budget}")
            if budget==0:
                need(actual==0 and a["UCI"]==controls["F"],
                     f"ZERO_DOSE_NOT_SHAM_{case_id}")
            row["writer_dose_results"].append({
                "requested_max_blocks":budget,
                "actual_writer_blocks":actual,
                "actual_reader_blocks":a["lineage_summary"]["reader_block"],
                "bestmove":a["UCI"]["bestmove"],
                "score_kind":a["UCI"]["score_kind"],
                "score_value":a["UCI"]["score_value"],
                "nodes":a["UCI"]["nodes"],
                "PV":a["UCI"]["pv"],
                "matches_F_core":a["UCI"]==controls["F"],
                "matches_O_bestmove":a["UCI"]["bestmove"]==controls["O"]["bestmove"],
                "categorical_flip_from_F":a["UCI"]["bestmove"]!=controls["F"]["bestmove"]
            })
            print("C3X018_WRITER_DOSE",case_id,budget,actual,
                  a["UCI"]["bestmove"],a["UCI"]["score_value"],
                  a["UCI"]["nodes"],flush=True)
        flips=[x["requested_max_blocks"] for x in row["writer_dose_results"]
                if x["categorical_flip_from_F"]]
        row["first_tested_flip_budget"]=flips[0] if flips else None
        row["flip_pattern_across_budgets"]=flips
        row["non_monotone_flip_grid"]=any(
           a["categorical_flip_from_F"] and not b["categorical_flip_from_F"]
           for a,b in zip(row["writer_dose_results"],row["writer_dose_results"][1:]))
        row["decoy_no_contact_exact"]=True
        result["cases"].append(row)
    result["interpretation_limits"]=[
      "Dose is number of suppressed attempts matching one key/slot/epoch, not independent writer nodes",
      "Suppression changes TT state and potentially search ordering or future writes; no monotonic assumption",
      "Source only FEN, Stockfish16 single-thread cold processes; sampling from selected #6/#8",
      "Observed dose threshold in finite grid not necessarily true physical or universal threshold",
      "Original F/O is root-order difference; TT dose perturbation is a separate operator",
      "TT key16 storage, shadow full64 identity; other TT uses not directly tied to this qsearch cutoff",
      "Causal natural TT mediation remains unproven even if output bestmove restores",
      "No independent new game cohort or tactical forcing proof"
    ]
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_DOSE_COURT_MATERIALIZED",flush=True)

if __name__=="__main__":
    main()
