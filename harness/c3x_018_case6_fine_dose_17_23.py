#!/usr/bin/env python3
"""C3X 0.18 adaptive secondary experiment: case #6 exact 17..23 writer budgets.

Exploratory follow-up to presealed 9-level court, not preregistered in its
original run. Independent cold replicates and frozen P4 source controls.
"""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play, need
from c3x_018_TT_writer_dose_6_8 import TARGETS

DOSES=tuple(range(17,24))
SEAL="c3x018-source-exact-TT-writer-suppression-nine-dose-native-receipt-v1"

def main():
    p=argparse.ArgumentParser()
    for opt in ("cohort","prior","preseal","patched","out"):
        p.add_argument("--"+opt,required=True)
    a=p.parse_args()
    receipt=json.loads(Path(a.preseal).read_text())
    need(receipt["schema"]==SEAL, "INVALID_NINE_DOSE_PRESEAL")
    # Freeze the coarse grid endpoints before inspecting finer budget outputs.
    old6=receipt["case6"]
    grid=dict((int(d),m) for d,m in old6["budget_to_bestmove"])
    need(grid[16]=="c3a4" and grid[32]=="e4d6", "COARSE_BOUNDARIES_NOT_PRESEALED")
    original=json.loads(Path(a.prior).read_text())
    cohort=json.loads(Path(a.cohort).read_text())
    world=cohort["selected"][5]
    need(world["id"]==6,"WRONG_SOURCE_ROOT")
    expected=original["worlds"][5]["cells"]
    baseline=play(a.patched,world,"F","OBS")
    need(baseline["UCI"]==expected["F"]["UCI"],"PATCHED_BASELINE_NONINTERFERENCE")
    need(baseline["UCI"]["bestmove"]=="e4d6","UNEXPECTED_ROOT_BASELINE")
    results=[]
    for budget in DOSES:
        run=play(a.patched,world,"F","W",TARGETS[6],writer_budget=budget)
        replicate=play(a.patched,world,"F","W",TARGETS[6],writer_budget=budget)
        need(run==replicate,f"COLD_REPLAY_{budget}")
        n=run["lineage_summary"]["writer_block"]
        need(0<n<=budget, f"CONTACT_INVALID_{budget}")
        u=run["UCI"]
        results.append({"max_block_budget":budget,"actual_writer_blocks":n,
                        "bestmove":u["bestmove"],"score_kind":u["score_kind"],
                        "score_value":u["score_value"],"nodes":u["nodes"],
                        "pv":u["pv"],"matches_F_core":u==baseline["UCI"],
                        "matches_original_O_bestmove":u["bestmove"]=="c3a4"})
        print("C3X018_CASE6_FINE_DOSE",budget,n,u["bestmove"],
              u["score_value"],u["nodes"],flush=True)
    decoy=play(a.patched,world,"F","W",
               {"key64":18446744073709551615,"slot":0,"epoch":1},writer_budget=23)
    need(decoy["UCI"]==baseline["UCI"] and
         decoy["lineage_summary"]["writer_block"]==0,"DECOY_CHANGED")
    series=[(16,"c3a4")]+[(r["max_block_budget"],r["bestmove"]) for r in results]+[(32,"e4d6")]
    switches=[{"from_budget":p[0],"to_budget":q[0],"from":p[1],"to":q[1]}
              for p,q in zip(series,series[1:]) if p[1]!=q[1]]
    result={
        "schema":"c3x018-case6-adaptive-fine-writer-dose-17-23-v1",
        "preseal_sha256":hashlib.sha256(Path(a.preseal).read_bytes()).hexdigest(),
        "prior_original_P4_sha256":hashlib.sha256(Path(a.prior).read_bytes()).hexdigest(),
        "source_id":6,
        "target":TARGETS[6],
        "design":"ADAPTIVE_SECONDARY_DISCRIMINATION_AFTER_COARSE_NONMONOTONE_RESULT",
        "precommitted_extension_budgets":list(DOSES),
        "coarse_16_bestmove":"c3a4",
        "coarse_32_bestmove":"e4d6",
        "results":results,
        "observed_switches":switches,
        "decoy_zero_contact_core_identical":True,
        "limits":[
            "Adaptive follow-up: not an independent confirmation of universality",
            "No monotonicity assumed; other untested dose values may also switch",
            "W suppresses entire save call, not just bound/value payload",
            "Native full64 shadow writer ownership only for cutoff consumers",
            "Slot epochs after intervention are path dependent",
            "No unique natural TT writer reader mediator identified"
        ]
    }
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_CASE6_FINE_GRID_NATIVE_PASS",flush=True)

if __name__=="__main__":
    main()
