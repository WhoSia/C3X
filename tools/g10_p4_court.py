from __future__ import annotations
import argparse,json
from pathlib import Path
from c3x_g10.promotion_calculus import Authority,evaluate_promotion,guard_claim,compose_local_certificates,competitor_novelty_adjudication

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def dump(p,x): Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def run(args):
    competitors=load(args.competitors)
    bank=load(args.counterexamples)
    p12=load(args.p12);p16=load(args.p16);p18=load(args.p18);p3=load(args.p3)
    novelty=competitor_novelty_adjudication(competitors["rows"])
    checks=[]

    by={x["id"]:x for x in bank["cases"]}

    c=by["P12_ROOT_CHANGE_COLOCATION"]
    r=evaluate_promotion(Authority.CHESS_NATIVE_SURFACE,"SURFACE_TO_MECHANISM",c["evidence"])
    checks.append({"id":c["id"],"pass":not r["allowed"] and not guard_claim(Authority.CHESS_NATIVE_SURFACE,"causal")["allowed"],"detail":r})

    c=by["P12_RESPONSE_WITHOUT_COMPLETE_FALSIFIERS"]
    r=evaluate_promotion(Authority.MECHANISM_CANDIDATE,"MECHANISM_TO_LOCAL_CAUSAL",c["evidence"])
    checks.append({"id":c["id"],"pass":not r["allowed"] and "CHAIN_RELATIVE_MINIMALITY" in r["promotion_debt"],"detail":r})

    c=by["P16_COMPLETE_LOCAL_BRIDGE"]
    r=evaluate_promotion(Authority.MECHANISM_CANDIDATE,"MECHANISM_TO_LOCAL_CAUSAL",c["evidence"])
    checks.append({"id":c["id"],"pass":r["allowed"] and not guard_claim(Authority.LOCAL_CAUSAL_EXPLANATION,"transported_causal_pattern")["allowed"],"detail":r})

    c=by["P18_LOCAL_ONLY_NO_TRANSPORT"]
    r=evaluate_promotion(Authority.LOCAL_CAUSAL_EXPLANATION,"COMPOSITION_TO_TRANSPORT",c["evidence"])
    checks.append({"id":c["id"],"pass":not r["allowed"],"detail":r})

    one_actual=[{
      "authority":"LOCAL_CAUSAL_EXPLANATION","scope":"LOCAL_ONLY",
      "world_id":"P16::398eca8d6adf00525e6d5bf7","provenance_id":"G9.5-P16",
      "intervention_grammar":"EVENT_TARGETED_TT_CAUSAL_REPLAY",
      "consequence_schema":"ROOT_CHOICE_TRANSITION",
      "correspondence_id":"P16_LOCAL_CORRESPONDENCE","falsifier_contradiction":False
    }]
    empirical_comp=compose_local_certificates(one_actual)

    schema_comp=compose_local_certificates([
      {"authority":"LOCAL_CAUSAL_EXPLANATION","scope":"LOCAL_ONLY","world_id":"schema-w1","provenance_id":"schema-p1","intervention_grammar":"G","consequence_schema":"C","correspondence_id":"R","falsifier_contradiction":False},
      {"authority":"LOCAL_CAUSAL_EXPLANATION","scope":"LOCAL_ONLY","world_id":"schema-w2","provenance_id":"schema-p2","intervention_grammar":"G","consequence_schema":"C","correspondence_id":"R","falsifier_contradiction":False},
    ])

    source_integrity={
      "p12_root_change_targets":p12["science"]["root_change_targets"],
      "p12_mediated_targets":p12["science"]["mediated_targets"],
      "p16_certificate_count":p16["result"]["certificate_count"],
      "p16_replication_status":p16["representative_minimal_bridge"]["replication_status"],
      "p18_certificates":p18["result"]["certificates"],
      "p18_transport_support_status":p18["result"]["transport_support_status"],
      "p3_verdict":p3["verdict"],
    }
    source_pass=(
      source_integrity["p12_root_change_targets"]==42
      and source_integrity["p12_mediated_targets"]==24
      and source_integrity["p16_certificate_count"]==1
      and source_integrity["p16_replication_status"]=="LOCAL_ONLY"
      and source_integrity["p18_certificates"]==0
      and source_integrity["p3_verdict"]=="PASS_TWO_LEVEL_INVARIANT_ARCHITECTURE"
    )

    counterexample_pass=all(x["pass"] for x in checks)
    calculus_pass=counterexample_pass and schema_comp["allowed"] and not schema_comp["transport_authorized"]
    if not novelty["novelty_survives_frozen_public_ecology"]:
        verdict="FAIL_COMPETITOR_ALREADY_SUBSUMES_PROMOTION_CONTRACT"
    elif not (source_pass and calculus_pass):
        verdict="FAIL_PROMOTION_RULES_AUTHORITY_LAUNDERING"
    else:
        verdict="PASS_EXECUTABLE_EVIDENCE_PROMOTION_CALCULUS"

    return {
      "schema":"c3x-g10-p4-court-v1",
      "verdict":verdict,
      "source_integrity":source_integrity,
      "source_integrity_pass":source_pass,
      "counterexample_checks":checks,
      "counterexample_closure_pass":counterexample_pass,
      "competitor_novelty":novelty,
      "composition":{
        "schema_rule_realizable":schema_comp["allowed"],
        "schema_transport_authorized":schema_comp["transport_authorized"],
        "empirical_actual_local_certificate_count":1,
        "empirical_composition_allowed":empirical_comp["allowed"],
        "empirical_composition_debt":empirical_comp["promotion_debt"],
        "empirical_status":"COMPOSITION_NOT_INSTANTIATED_ONE_LOCAL_CERTIFICATE"
      },
      "promotion_architecture":{
        "measurement_to_surface":"typed evidence rule",
        "surface_to_mechanism":"typed intervention response rule",
        "mechanism_to_local_causal":"falsifier-complete minimal local certificate rule",
        "local_to_composition":"independent compatible local certificates only",
        "composition_to_transport":"prospective held-out transport obligations only"
      },
      "fresh_causal_outcomes_opened":False,
      "transportable_pattern_instantiated":False,
      "authority_ceiling":["P16 remains LOCAL_ONLY","P18 transport failure unchanged","No empirical composition candidate created","No universal novelty claim"],
    }

def main():
    ap=argparse.ArgumentParser()
    for x in ["competitors","counterexamples","p12","p16","p18","p3","out"]: ap.add_argument("--"+x,required=True)
    a=ap.parse_args()
    dump(a.out,run(a))

if __name__=="__main__":main()
