from __future__ import annotations
import argparse,json,itertools
from pathlib import Path
from c3x_g10.morphism_grammar import development_adjudication,morphism_witness

def load(p):return json.loads(Path(p).read_text())

def independent(a,b):
    return a["source_id"]!=b["source_id"] and a["position_id"]!=b["position_id"]

def main():
    ap=argparse.ArgumentParser()
    for x in ["development","holdout","out"]:ap.add_argument("--"+x,required=True)
    a=ap.parse_args()
    dev=load(a.development);hold=load(a.holdout)
    dres=development_adjudication(dev)
    dc=dev["certificates"];hc=hold.get("certificates",[])
    pairs=[];families=[]
    for x,y in itertools.combinations(dc+hc,2):
        w=morphism_witness(x,y)
        rec={"a":x["id"],"b":y["id"],"witness":w,"independent_provenance":independent(x,y)}
        pairs.append(rec)
        if w["isomorphic"] and independent(x,y) and (x["id"].startswith("HOLDOUT_") or y["id"].startswith("HOLDOUT_")):
            gens=set(w["minimal_generators"] or [])
            substantive=bool(gens & {"S","E"})
            if substantive:
                families.append({"a":x["id"],"b":y["id"],"minimal_generators":w["minimal_generators"],"substantive":True})
    support=bool(hold.get("support",{}).get("pass"))
    if dres["verdict"]!="PASS_MORPHISM_GRAMMAR_PRESEALED":
        verdict="FAIL_DEGENERATE_ISOMORPHISM_GRAMMAR"
    elif not support:
        verdict="HOLD_HOLDOUT_CERTIFICATE_SUPPORT_INSUFFICIENT"
    elif families:
        verdict="PASS_NONTRIVIAL_MECHANISM_FAMILY_ISOMORPHISM"
    else:
        verdict="PASS_ADMISSIBLE_MORPHISM_GRAMMAR_NO_HOLDOUT_FAMILY"
    out={
      "schema":"c3x-g10-p7-court-v1","verdict":verdict,
      "development":dres,
      "holdout_support":hold.get("support"),
      "holdout_instrument_verdict":hold.get("fresh_instrument_verdict"),
      "holdout_certificate_count":len(hc),
      "pairwise_morphism_geometry":pairs,
      "mechanism_family_candidates":families,
      "frozen_grammar":["C","S","E"],
      "unlicensed_generators":["G","U"],
      "gauge_generator":"C",
      "substantive_generators":["S","E"],
      "transportable_pattern_instantiated":False,
      "authority_ceiling":["At most MECHANISM_FAMILY_CANDIDATE","No transportable causal pattern","No objective chess truth or human cognition claim"]
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P7_VERDICT",verdict,"holdout_certs",len(hc),"families",len(families))
if __name__=="__main__":main()
