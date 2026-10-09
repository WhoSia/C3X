#!/usr/bin/env python3
"""C3X018 matched proposed-write fingerprint W vs P native discrimination.

Same proposed TT save input and previous physical entry payload is a necessary
source fingerprint for cross-arm candidate match; it is not sufficient to prove
identical upstream recursive call lineage. Compare common prefixes fail-closed.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_TT_writer_dose_6_8 import TARGETS

BUDGETS={6:(2,21,22,23),8:(2,74)}
SIGNATURE=("key64","slot","epoch","proposed_move","proposed_depth",
           "proposed_bound","proposed_value","prior_move","prior_depth",
           "prior_bound","prior_value")
def signature(e):return tuple(e[k] for k in SIGNATURE)

def compare(a,b):
    matched=0
    for x,y in zip(a,b):
        if signature(x)!=signature(y):break
        matched+=1
    return {
      "prefix_matched":matched,
      "W_contacts":len(a),"P_contacts":len(b),
      "complete_fingerprint_equivalence":matched==len(a)==len(b),
      "first_W_nonmatching":a[matched] if matched<len(a) else None,
      "first_P_nonmatching":b[matched] if matched<len(b) else None,
      "matching_relation":"SOURCE_PROPOSAL_SAME_FIELDS_ONLY_NOT_SAME_CAUSAL_CALL"
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("cohort","prior","whole-engine","payload-engine","out"):
        p.add_argument("--"+name,required=True)
    args=p.parse_args()
    cohort=json.loads(Path(args.cohort).read_text())
    prior=json.loads(Path(args.prior).read_text())
    output={"schema":"c3x018-matched-source-TT-write-proposal-W-P-v1",
      "source_only":True,"methods":"Same frozen FEN, target and writer-block budget; compare source proposals before blocked save",
      "signature_fields":list(SIGNATURE),"cases":[],"limits":[]}
    for case_id,budgets in BUDGETS.items():
        world=cohort["selected"][case_id-1]
        need(world["id"]==case_id,"SOURCE_CASE")
        F=prior["worlds"][case_id-1]["cells"]["F"]["UCI"]
        baselines={}
        for label,engine in (("W",args.whole_engine),("P",args.payload_engine)):
            x=play(engine,world,"F","OBS")
            need(x["UCI"]==F,f"BASELINE_DRIFT_{case_id}_{label}")
            baselines[label]=x
        row={"id":case_id,"target":TARGETS[case_id],"F":F,"comparisons":[]}
        for budget in budgets:
            outcomes={}
            for label,engine in (("W",args.whole_engine),("P",args.payload_engine)):
                first=play(engine,world,"F",label,TARGETS[case_id],writer_budget=budget)
                second=play(engine,world,"F",label,TARGETS[case_id],writer_budget=budget)
                need(first==second,f"NONDETERMINISTIC_{case_id}_{budget}_{label}")
                fp=first["write_fingerprints"]
                need(len(fp)==first["lineage_summary"]["writer_block"],f"FINGERPRINT_MISSING_{case_id}_{budget}_{label}")
                need(len(fp)>0 and len(fp)<=budget,f"WRONG_CONTACT_{case_id}_{budget}_{label}")
                need([e["contact"] for e in fp]==list(range(1,len(fp)+1)),
                     f"FINGERPRINT_CONTACT_INDEX_{case_id}_{budget}_{label}")
                outcomes[label]={"UCI":first["UCI"],"fingerprints":fp,
                    "contact_count":len(fp)}
            x=compare(outcomes["W"]["fingerprints"],outcomes["P"]["fingerprints"])
            row["comparisons"].append({
               "budget":budget,"alignment":x,
               "W_UCI":outcomes["W"]["UCI"],"P_UCI":outcomes["P"]["UCI"],
               "W_P_bestmove_differs":outcomes["W"]["UCI"]["bestmove"]!=outcomes["P"]["UCI"]["bestmove"],
               "W_P_full_core_differs":outcomes["W"]["UCI"]!=outcomes["P"]["UCI"]
            })
            print("C3X018_MATCHED_PROPOSAL",case_id,budget,
                  "prefix",x["prefix_matched"],"W",x["W_contacts"],"P",x["P_contacts"],
                  "choices",outcomes["W"]["UCI"]["bestmove"],
                  outcomes["P"]["UCI"]["bestmove"],flush=True)
        output["cases"].append(row)
    output["limits"]=[
     "Fingerprint equality necessary but not sufficient for same physical recursive call; root and aspiration genealogy not yet joined in this court",
     "P leaves move16 updated and may create a hybrid physical TTEntry",
     "Intervention changes later write attempts and eligible epochs; mismatch is a mechanistic finding not a fault",
     "A matched prefix does not identify an exclusive natural TT mediator",
     "Selection based on original treated F arm from #6/#8 (prior exploratory court); not independent target preregistration",
     "Writer proposal fields are recorded when suppressed; unblocked descendant write sequence not exhaustively logged"]
    Path(args.out).write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("C3X018_MATCHED_WRITER_SOURCE_FINGERPRINT_NATIVE_COMPLETE",flush=True)
if __name__=="__main__":main()
