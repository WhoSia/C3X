#!/usr/bin/env python3
"""C3X018 V-vs-W2 within-arm root search genealogy equivalence court.

Case #2/#5: V one TT bound-based eval override suppression reproduces the
entire W2 final UCI tuple. Determine whether recorded aspiration/candidate
event streams and TT cutoff ancestry ALSO match. No cross-arm causal identity
is inferred from equal numeric root call counters.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_root_call_TT_genealogy_native import summarize
from c3x_018_depth_transport_five_source_worlds import TARGETS

def first_different(a,b):
    match=0
    for v,w in zip(a,b):
        if v!=w:break
        match+=1
    return {"exact":a==b,"common_prefix":match,"length_a":len(a),"length_b":len(b),
            "first_a":a[match] if match<len(a) else None,
            "first_b":b[match] if match<len(b) else None,
            "warning":"source event index alignment beyond first mismatch is not a causal pairing"}

def main():
    p=argparse.ArgumentParser()
    for key in ("cohort","prior","engine","out"):p.add_argument("--"+key,required=True)
    args=p.parse_args()
    cohort=json.loads(Path(args.cohort).read_text())
    prior=json.loads(Path(args.prior).read_text())
    output={"schema":"c3x018-V-W2-root-genealogy-equivalence-court-cases2-5-v1",
      "prior_sha256":hashlib.sha256(Path(args.prior).read_bytes()).hexdigest(),
      "cases":[]}
    for case_id in (2,5):
        world=cohort["selected"][case_id-1]
        need(world["id"]==case_id,"FROZEN_SOURCE_ID")
        old=prior["worlds"][case_id-1]["cells"]
        arms={}
        for name,root_mode,tt_mode,target,budget in (
            ("O","O","OBS",None,None),
            ("F","F","OBS",None,None),
            ("Z","Z","OBS",None,None),
            ("W2","F","W",TARGETS[case_id],2),
            ("V","F","V",TARGETS[case_id],None),
            ("R","F","R",TARGETS[case_id],None)):
            one=play(args.engine,world,root_mode,tt_mode,target,budget)
            two=play(args.engine,world,root_mode,tt_mode,target,budget)
            need(one==two,f"COLD_REPLAY_{case_id}_{name}")
            if name in ("O","F","Z"):
                need(one["UCI"]==old[name]["UCI"],f"PRIOR_CORE_{case_id}_{name}")
            need(one["root_events"] and len(one["root_events"])<4096,
                 f"ROOT_TRACE_MISSING_OR_CENSORED_{case_id}_{name}")
            summ=summarize(one)
            arms[name]={"UCI":one["UCI"],
                "lineage":one["lineage_summary"],
                "root_event_sequence":one["root_events"],
                "root_genealogy":summ,
                "active_operator_contacts":one["blocks"]}
            print("C3X018_V_W2_GENEALOGY",case_id,name,
                  one["UCI"]["bestmove"],len(one["root_events"]),
                  one["lineage_summary"]["reader_block"],flush=True)
        need(arms["O"]["UCI"]==arms["Z"]["UCI"],"OZ_NO_CONTACT")
        need(arms["V"]["UCI"]==arms["W2"]["UCI"],f"V_W2_CORE_EQUIVALENCE_BROKEN_{case_id}")
        need(arms["V"]["lineage"]["reader_block"]==1 and
             all(e["site"]=="tt_value_eval_override" for e in arms["V"]["active_operator_contacts"]),
             f"V_REAL_CONTACT_{case_id}")
        need(arms["W2"]["lineage"]["writer_block"]==2,f"W2_CONTACT_{case_id}")
        comparisons={}
        for name in ("W2","V","R"):
            comparisons[name]=first_different(arms["F"]["root_event_sequence"],
                                               arms[name]["root_event_sequence"])
        equivalent=first_different(arms["W2"]["root_event_sequence"],
                                   arms["V"]["root_event_sequence"])
        row={
          "id":case_id,"F_core":arms["F"]["UCI"],
          "W2_V_final_core_exact":True,
          "W2_vs_V_root_event_equivalence":equivalent,
          "F_vs_treatments_first_root_event":comparisons,
          "arms":{
             k:{"UCI":v["UCI"],"lineage":v["lineage"],
                "root_genealogy":v["root_genealogy"],
                "operator_contacts":v["active_operator_contacts"]}
             for k,v in arms.items()}
        }
        output["cases"].append(row)
    output["limits"]=[
      "Root events contain within-arm IDs; after divergence numeric counter equality does not establish same physical call",
      "Equal root event arrays only document equality of measured source-level events, not all recursive TT state",
      "V single TT eval override output equality to W2 is local substitution, not unique natural mediation",
      "TT root-candidate ancestry is approximate for non-root sections outside guarded search; operator sites retained",
      "Case roots selected after writer sensitivity, same frozen FEN; no independent new population"
    ]
    Path(args.out).write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("C3X018_V_W2_MACRO_GENEALOGY_COMPARISON_NATIVE_PASS",flush=True)
if __name__=="__main__":main()
