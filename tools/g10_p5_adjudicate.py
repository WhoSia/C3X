from __future__ import annotations
import argparse,json
from pathlib import Path
from c3x_g10.authority_dynamics import classify_certificate_conflict,Claim,apply_evidence,propagate_revision,rendered_language_allowed
from c3x_g10.promotion_calculus import compose_local_certificates

def load(p):return json.loads(Path(p).read_text())
def norm_old(p16):
    c=p16["representative_minimal_bridge"]
    return {
      "certificate_id":"P16::"+c["pair_uci"],"authority":"LOCAL_CAUSAL_EXPLANATION","scope":"LOCAL_ONLY",
      "world_id":c["position_id"],"provenance_id":"LICHESS_2026_07_08",
      "intervention_grammar":"P16_EXACT_EVENT_FULL_BRIDGE","consequence_schema":"ROOT_CHOICE_TRANSITION",
      "correspondence_id":"P16_FULL_BRIDGE_CONTRACT_V1","context_signature":c["engine"]+"|"+c["bound"],
      "mechanism_signature":c["structural_signature"],"falsifier_contradiction":False
    }
def norm_fresh(c):
    source=str(c.get("source_id",""))
    provenance="TWIC1663" if source.endswith("1663") else "TWIC1664" if source.endswith("1664") else source
    return {
      "certificate_id":c["certificate_id"],"authority":"LOCAL_CAUSAL_EXPLANATION","scope":"LOCAL_ONLY",
      "world_id":c["position_id"],"provenance_id":provenance,
      "intervention_grammar":"P16_EXACT_EVENT_FULL_BRIDGE","consequence_schema":"ROOT_CHOICE_TRANSITION",
      "correspondence_id":"P16_FULL_BRIDGE_CONTRACT_V1","context_signature":c["engine"]+"|"+c["bound"],
      "mechanism_signature":c["structural_signature"],"falsifier_contradiction":False,
      "source_id":c["source_id"]
    }

def main():
    ap=argparse.ArgumentParser()
    for x in ["fresh","p16","p18","p4","out"]:ap.add_argument("--"+x,required=True)
    a=ap.parse_args();fresh=load(a.fresh);p16=load(a.p16);p18=load(a.p18);p4=load(a.p4)
    old=norm_old(p16);news=[norm_fresh(c) for c in fresh.get("causal_explanation_certificates",[])]
    pair_results=[];composition=[]
    for n in news:
        cls=classify_certificate_conflict(old,n)
        comp=compose_local_certificates([old,n])
        eligible=cls["class"]=="COMPATIBLE_COMPOSABLE" and comp["allowed"]
        pair_results.append({"old":old["certificate_id"],"fresh":n["certificate_id"],"conflict":cls,"composition_allowed":eligible,"raw_composition":comp})
        if eligible:composition.append([old["certificate_id"],n["certificate_id"]])
    # Dependency revision stress: retract certificate -> explanation + composition suspend and language withdraws.
    cert=Claim("cert","LOCAL_CAUSAL_EXPLANATION")
    expl=Claim("explanation","LOCAL_CAUSAL_EXPLANATION",dependencies={"cert"})
    compc=Claim("composition","COMPOSITION_CANDIDATE",dependencies={"cert"})
    claims={"cert":cert,"explanation":expl,"composition":compc}
    apply_evidence(cert,{"PROVENANCE_INVALID"},"stress-retract")
    prop=propagate_revision(claims)
    stress_pass=(prop["claims"]["explanation"]["status"]=="SUSPENDED" and prop["claims"]["composition"]["status"]=="SUSPENDED" and not rendered_language_allowed(expl)["causal"])
    support=bool(fresh.get("support",{}).get("pass"))
    if not stress_pass:
        verdict="FAIL_DEPENDENCY_PROPAGATION_LEAK"
    elif not support:
        verdict="HOLD_FRESH_CERTIFICATE_ECOLOGY_SUPPORT_INSUFFICIENT"
    elif composition:
        verdict="PASS_MULTI_CERTIFICATE_COMPOSITION_CANDIDATE"
    else:
        verdict="PASS_AUTHORITY_DYNAMICS_FRESH_ECOLOGY_NO_COMPOSITION"
    out={
      "schema":"c3x-g10-p5-court-v1","verdict":verdict,
      "authority_dynamics_verdict":"PASS_SELF_CORRECTING_AUTHORITY_DYNAMICS" if stress_pass else "FAIL_DEPENDENCY_PROPAGATION_LEAK",
      "fresh_instrument_verdict":fresh.get("verdict"),"fresh_support":fresh.get("support"),
      "fresh_local_certificate_count":len(news),"fresh_certificates":news,
      "existing_p16_certificate":old,"certificate_pair_adjudications":pair_results,
      "empirical_composition_candidates":composition,
      "dependency_revision_stress":{"pass":stress_pass,"result":prop},
      "p18_transport_status":p18["result"]["transport_support_status"],
      "p4_parent_verdict":p4["verdict"],
      "transportable_pattern_instantiated":False,
      "authority_ceiling":["Fresh certificates remain LOCAL_ONLY unless later authority is separately earned","Composition candidate is not transport","P18 transport failure unchanged"]
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P5_VERDICT",verdict,"fresh_certs",len(news),"composition",len(composition),"stress",stress_pass)
if __name__=="__main__":main()
