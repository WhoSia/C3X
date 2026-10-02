from __future__ import annotations
import argparse,json,itertools
from pathlib import Path
from c3x_g10.mechanism_identity import development_adjudication,classify_pair

def load(p):return json.loads(Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    for x in ["development","holdout","out"]:ap.add_argument("--"+x,required=True)
    a=ap.parse_args();dev=load(a.development);hold=load(a.holdout)
    dres=development_adjudication(dev)
    dc=dev["certificates"];hc=hold["certificates"]
    comparisons=[]
    composition=[]
    for x,y in itertools.combinations(dc+hc,2):
        cls=classify_pair(x,y)
        rec={"a":x["id"],"b":y["id"],**cls}
        comparisons.append(rec)
        if cls["class"]=="COMPOSITION_CORE_MATCH":
            # At least one member must be holdout; development-only pairs cannot earn P6 composition authority.
            if x["id"].startswith("HOLDOUT_") or y["id"].startswith("HOLDOUT_"):
                composition.append({"a":x["id"],"b":y["id"],"core_match":True})
    support=bool(hold.get("support",{}).get("pass"))
    if dres["verdict"]!="PASS_CONJUNCTIVE_CONSTITUTIVE_CORE_PRESEALED":
        verdict="FAIL_CONSTITUTIVE_IDENTITY_COUNTEREXAMPLE"
    elif not support:
        verdict="HOLD_HOLDOUT_CERTIFICATE_SUPPORT_INSUFFICIENT"
    elif composition:
        verdict="PASS_LAWFUL_CAUSAL_COMPOSITION_CANDIDATE"
    else:
        verdict="PASS_CONSTITUTIVE_MECHANISM_IDENTITY_NO_COMPOSITION"
    result={
      "schema":"c3x-g10-p6-court-v1","verdict":verdict,
      "development":dres,
      "holdout_support":hold.get("support"),
      "holdout_instrument_verdict":hold.get("fresh_instrument_verdict"),
      "holdout_certificate_count":len(hc),
      "pairwise_geometry":comparisons,
      "empirical_composition_candidates":composition,
      "constitutive_core":["relation_delta","response_topology"],
      "authority_obligations":["falsifier_pattern","chain_relative_minimality","independent_source_and_position_provenance"],
      "transportable_pattern_instantiated":False,
      "authority_ceiling":["At most COMPOSITION_CANDIDATE","No transportable causal pattern","No objective chess truth or human cognition claim"]
    }
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("G10_P6_VERDICT",verdict,"holdout_certs",len(hc),"composition",len(composition))
if __name__=="__main__":main()
