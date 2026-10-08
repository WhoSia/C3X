#!/usr/bin/env python3
"""P6-I: refuse chess concept causal claims under competing feature changes."""
import argparse,json
from pathlib import Path

def adjudicate(payload):
    assert payload["schema"]=="c3x-013-p6-legal-pawn-concept-toggles-v1"
    out={"schema":"c3x-013-p6-feature-fiber-adjudication-v1",
         "authority":"ENGINE_COMPARABILITY_AND_CHESS_BOARD_FACTS_ONLY",
         "unique_concept_mediator_certificates":[],"rows":[]}
    for item in payload["results"]:
        facts=item["concept_rule_facts"]
        a=facts["treated"]["full_descriptive_feature_deltas"]
        b=facts["control"]["full_descriptive_feature_deltas"]
        keys=sorted(set(a)|set(b))
        vector={k:a.get(k,0)-b.get(k,0) for k in keys if a.get(k,0)!=b.get(k,0)}
        concept=item["concept"]
        assert vector.get(concept)!=0,"PRECOMMIT_CONCEPT_WAS_NOT_TOGGLED"
        nuisance={k:v for k,v in vector.items() if k!=concept}
        depth=[]
        for d,v in item["measurements"].items():
            trial=v["trials"]
            depth.append({"depth":int(d),"repeats":len(trial),
                          "same_cp":v["same_cp_repeated"],
                          "gap_cp":[t.get("treated_minus_control_cp") for t in trial]})
        verdict="CONFOUNDED_CONCEPT_HOLD" if nuisance else "ONLY_MEASURED_FEATURE_UNIQUE_NOT_FULL_CAUSALITY"
        out["rows"].append({"fixture":item["id"],"concept":concept,
                            "concept_delta":vector[concept],"nuisance_deltas":nuisance,
                            "nonzero_feature_dimension":len(vector),
                            "available_independent_chess_root_contrasts":1,
                            "complete_depth_repeats":depth,"verdict":verdict})
    out["all_holds"]=all(r["verdict"]=="CONFOUNDED_CONCEPT_HOLD" for r in out["rows"])
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    obj=adjudicate(json.loads(Path(a.raw).read_text()))
    Path(a.out).write_text(json.dumps(obj,indent=2)+"\n")
    print("P6_INTERVENTION_IDENTIFIABILITY",[(r["fixture"],r["verdict"],r["nuisance_deltas"])
                                                for r in obj["rows"]])
    assert obj["all_holds"] and not obj["unique_concept_mediator_certificates"]
if __name__=="__main__":main()
