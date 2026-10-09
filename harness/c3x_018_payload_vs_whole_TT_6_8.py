#!/usr/bin/env python3
"""C3X018 #6/#8 TT payload-only vs whole-save source-ablation native court.

Frozen 0.18 TT shadow and source writer targets; distinguish source fields
while retaining physical input/singlethread/outcome controls. P generates
possibly hybrid TT entries and must not be called a natural intervention.
"""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play, need
from c3x_018_TT_writer_dose_6_8 import TARGETS

BUDGETS={6:(1,2,21,22,23),8:(1,2,74)}
SCHEMA="c3x018-tt-payload-only-vs-whole-save-source-ablation-v1"

def main():
    parser=argparse.ArgumentParser()
    for opt in ("cohort","prior","patched","out"):
        parser.add_argument("--"+opt,required=True)
    args=parser.parse_args()
    cohort=json.loads(Path(args.cohort).read_text())
    prior=json.loads(Path(args.prior).read_text())
    results={"schema":SCHEMA,
             "cohort_sha256":hashlib.sha256(Path(args.cohort).read_bytes()).hexdigest(),
             "prior_sha256":hashlib.sha256(Path(args.prior).read_bytes()).hexdigest(),
             "case_dose_grid":{str(k):list(v) for k,v in BUDGETS.items()},
             "P_mechanism":"Suppress accepted payload fields only, allow original move16 update",
             "W_mechanism":"Suppress entire accepted TTEntry::save call",
             "cases":[]}
    for case_id,budgets in BUDGETS.items():
        w=cohort["selected"][case_id-1]
        need(w["id"]==case_id,"FROZEN_ID")
        prior_cells=prior["worlds"][case_id-1]["cells"]
        controls={}
        for arm in ("O","F","Z"):
            a=play(args.patched,w,arm,"OBS")
            need(a["UCI"]==prior_cells[arm]["UCI"],"P4_NONINTERFERENCE_"+str(case_id))
            controls[arm]=a["UCI"]
        need(controls["O"]==controls["Z"],"O_Z_NEGATIVE_CONTROL")
        row={"id":case_id,"target":TARGETS[case_id],"controls":controls,
             "budget_rows":[]}
        decoy=play(args.patched,w,"F","P",
                   {"key64":18446744073709551615,"slot":0,"epoch":1},
                   writer_budget=74)
        need(decoy["UCI"]==controls["F"] and decoy["lineage_summary"]["writer_block"]==0,
             "PAYLOAD_DECOY_CONTACT_OR_DRIFT")
        row["decoy_P_no_contact_exact"]=True
        for budget in budgets:
            outcome={}
            for mode in ("W","P"):
                first=play(args.patched,w,"F",mode,TARGETS[case_id],writer_budget=budget)
                second=play(args.patched,w,"F",mode,TARGETS[case_id],writer_budget=budget)
                need(first==second,f"COLD_REPLAY_{case_id}_{budget}_{mode}")
                contacts=first["lineage_summary"]["writer_block"]
                need(0<contacts<=budget,f"CONTACT_{case_id}_{budget}_{mode}")
                needed_site="save" if mode=="W" else "payload"
                need(all(b["site"]==needed_site for b in first["blocks"]),
                     f"EVENT_SITE_MISMATCH_{case_id}_{budget}_{mode}")
                outcome[mode]={
                    "UCI":first["UCI"],"write_blocks":contacts,
                    "matches_F_core":first["UCI"]==controls["F"],
                    "matches_O_bestmove":first["UCI"]["bestmove"]==controls["O"]["bestmove"]
                }
                print("C3X018_ABLATION",case_id,budget,mode,contacts,
                      first["UCI"]["bestmove"],first["UCI"]["score_value"],
                      first["UCI"]["nodes"],flush=True)
            row["budget_rows"].append({
                "budget":budget,**outcome,
                "categorical_W_P_disagree":
                    outcome["W"]["UCI"]["bestmove"]!=outcome["P"]["UCI"]["bestmove"],
                "full_core_W_P_disagree":outcome["W"]["UCI"]!=outcome["P"]["UCI"]
            })
        results["cases"].append(row)
    results["limitations"]=[
       "P permits move16 source update but retains old payload fields: hybrid TT state possible",
       "W skips full save, so operator contrast is not a natural biological/chess mechanism",
       "Only previously selected same-case F-exposed TT key/slot/epoch; independent target transport not established",
       "Source exact slot write epochs evolve after interventions",
       "Full O/F/Z final output check, source cold replay and decoy gate; finite-depth SF16 only",
       "Intervention-dependent scope and other TT uses remain; no proof of exclusive mediation",
       "Selected #6/#8 based on prior root flips; no new independent game sample"
    ]
    Path(args.out).write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
    print("C3X018_PAYLOAD_VS_WHOLE_SAVE_NATIVE_PASS",flush=True)

if __name__=="__main__":main()
