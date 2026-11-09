#!/usr/bin/env python3
"""R20 result interpretation repair from the original immutable public artifact.

This adjudicates 'third candidate' at a particular *depth* separately from
a novel move across all depth/world root leaders. It cannot change the
underlying Stockfish experiment nor infer strategic chess quality.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SHA="8d176b66f1fa92bda13c74cc62939fd9b114912c5d02e29091ec13ad4a820054"
SCHEMA="c3x042-r20-legal-native-root-choice-counterfactual-v1"

def interpret(original):
    if original.get("schema")!=SCHEMA or original.get("status")!="PASS_ACTUAL_NATIVE_LEGAL_ROOT_LEADER_CANDIDATE_TRANSPORT_ONLY":
        raise ValueError("R20_HOLD_ORIGINAL_NATIVE_COURT_NOT_ADMITTED")
    rows=original.get("root_depths",[])
    if len(rows)!=12 or [x.get("depth") for x in rows]!=list(range(1,13)):
        raise ValueError("R20_HOLD_NATIVE_ROOT_DEPTH_ORDER")
    keys=("A","B","C","C_reverse")
    if any(any(not isinstance(x.get(k),str) or len(x[k]) not in (4,5)
               for k in keys) for x in rows):
        raise ValueError("R20_HOLD_SOURCE_MOVE_IDENTITY")
    changed=[x["depth"] for x in rows if x["C"]!=x["C_reverse"]]
    if changed!=original.get("changed_root_leader_depths"):
        raise ValueError("R20_HOLD_R19_ORIGINAL_LEADER_CHANGE_CONTRACT")
    pair_outside=[x["depth"] for x in rows
                  if x["C_reverse"] not in (x["B"],x["C"])]
    if pair_outside!=original.get("third_candidate_emergence_depths"):
        raise ValueError("R20_HOLD_OLD_PAIR_RELATIVE_THIRD_LABEL")
    all_baseline={x[k] for x in rows for k in ("A","B","C")}
    threeway=[x["depth"] for x in rows
              if x["C_reverse"] not in (x["A"],x["B"],x["C"])]
    globally_novel=[x["depth"] for x in rows
                    if x["C_reverse"] not in all_baseline]
    return {
      "schema":"c3x042-r20-source-legal-dynamic-root-support-corrected-semantics-v1",
      "status":"PASS_DETERMINISTIC_ORIGINAL_PUBLIC_RESULT_INTERPRETATION_ONLY",
      "original_artifact_sha256":EXPECTED_SHA,
      "source_original_chess_game_id":14,
      "changed_leader_depths":changed,
      "outside_contemporaneous_B_C_depths":pair_outside,
      "outside_contemporaneous_A_B_C_depths":threeway,
      "new_move_identity_across_all_original_A_B_C_depths":globally_novel,
      "depthwise":[
        {"depth":x["depth"],"A":x["A"],"B":x["B"],"C":x["C"],
         "reverse_C":x["C_reverse"],
         "reverse_matches_A":x["C_reverse"]==x["A"],
         "reverse_matches_B":x["C_reverse"]==x["B"],
         "reverse_matches_C":x["C_reverse"]==x["C"],
         "reverse_outside_A_B_C_this_depth":x["depth"] in threeway,
         "reverse_new_to_global_baseline_support":x["depth"] in globally_novel}
         for x in rows if x["depth"]>=9
      ],
      "causal_claim":"R18 physical single-source return intervention changes transient native legal root leaders; final C move unchanged.",
      "natural_root_mediation_proved":False,
      "independent_chess_strategic_value_proved":False,
      "generalization_proved":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-public-json",required=True)
    p.add_argument("--public-out",required=True)
    a=p.parse_args()
    data=Path(a.source_public_json).read_bytes()
    if hashlib.sha256(data).hexdigest()!=EXPECTED_SHA:
        raise ValueError("R20_HOLD_ORIGINAL_PUBLIC_JSON_SHA_DRIFT")
    out=interpret(json.loads(data))
    p=Path(a.public_out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("R20_ORIGINAL_PUBLIC_SEMANTIC_CORRECTION",out["status"],
          "outside_same_depth",out["outside_contemporaneous_A_B_C_depths"],
          "new_global",out["new_move_identity_across_all_original_A_B_C_depths"])
if __name__=="__main__":
    main()
