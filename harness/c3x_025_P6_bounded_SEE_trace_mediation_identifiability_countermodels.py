#!/usr/bin/env python3
"""Synthetic finite theorem: equal bounded observational traces need not identify
TT->late SEE branch->root mediation. Not an observed chess path or a proof of
physical realizability of these abstract SCMs in Stockfish16.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SCHEMA="c3x025-P6-finite-two-arm-bounded-SEE-observation-nonidentifiability-countermodels-v1"
LABELS=("DIRECT_TT_OTHER_MEDIATOR","TT_THROUGH_UNOBSERVED_LATE_SEE",
        "NO_ROOT_EFFECT","TT_LATE_SEE_COMPENSATED_BY_OTHER_PATH")
def h(label:str,t:int)->int:
    if label not in LABELS or t not in (0,1):raise ValueError("SCM label or treatment invalid")
    return t if label in (LABELS[1],LABELS[3]) else 0
def y(label:str,t:int,do_h:int)->int:
    if label not in LABELS or t not in (0,1) or do_h not in (0,1):
        raise ValueError("SCM argument invalid")
    if label==LABELS[0]:return t
    if label==LABELS[1]:return do_h
    if label==LABELS[2]:return 0
    return t^do_h
def observed(label:str,t:int,see_after_prefix_observed:bool=False)->dict:
    """Uninformative common first32 witness, physical E0, final UCI flip Y."""
    o={"TT_FIRST_policy":t,"physical_TT_contact_certified":True,
       "common_first32_SEE_prefix_source_event_present":True,
       "first32_SEE_prefix_censored":True,
       "binary_root_final_bestmove_flip":y(label,t,h(label,t))}
    if see_after_prefix_observed:
        o["late_SEE_branch_activation"]=h(label,t)
    return o
def controlled(label:str,t:int,mediator_value:int)->dict:
    return {"T":t,"do_late_SEE_activation":mediator_value,
            "final_root_flip":y(label,t,mediator_value)}
def natural_indirect(label:str)->int:
    return y(label,1,h(label,1))-y(label,1,h(label,0))
def constructive_counterexamples()->dict:
    pair_A=LABELS[0:2]
    pair_B=LABELS[2:4]
    pairs={}
    for key,(left,right),y_expected,natural_expected in (
         ("ROOT_FLIP_YES",pair_A,(0,1),(0,1)),
         ("ROOT_FLIP_NO",pair_B,(0,0),(0,-1))):
        left_visible=[observed(left,t) for t in (0,1)]
        right_visible=[observed(right,t) for t in (0,1)]
        if left_visible!=right_visible:raise AssertionError("VISIBLE_MODELS_NOT_IDENTICAL")
        if tuple(x["binary_root_final_bestmove_flip"] for x in left_visible)!=y_expected:
            raise AssertionError("OBSERVED_ROOT_CONTRAST_WRONG")
        indirect=(natural_indirect(left),natural_indirect(right))
        if indirect!=natural_expected or indirect[0]==indirect[1]:
            raise AssertionError("HIDDEN_CAUSAL_CONTRAST_NOT_DISTINCT")
        controlled_l=[controlled(left,t,m) for t in (0,1) for m in (0,1)]
        controlled_r=[controlled(right,t,m) for t in (0,1) for m in (0,1)]
        if controlled_l==controlled_r:raise AssertionError("CAUSAL_MODELS_IDENTICAL_NOT_COUNTEREXAMPLE")
        extended_l=[observed(left,t,True) for t in (0,1)]
        extended_r=[observed(right,t,True) for t in (0,1)]
        if extended_l==extended_r:raise AssertionError("LATE_SEE_OBSERVATION_DID_NOT_SEPARATE_MODELS")
        pairs[key]={"original_structural_models":list((left,right)),
           "same_observed_two_native_TT_policy_arms":left_visible,
           "same_partial_observation":True,
           "mediator_NIE_direct_or_null":indirect[0],
           "mediator_NIE_late_SEE_or_compensated":indirect[1],
           "controlled_two_policy_times_two_mediator_potential_outcomes":{
               left:controlled_l,right:controlled_r},
           "if_late_SEE_activation_is_actually_measured_then_models_diverge":True,
           "real_native_stockfish_physical_validity_established":False}
    return {"schema":SCHEMA,
        "research_phase":"BOUNDED_SYNTHETIC_STRUCTURAL_NONIDENTIFICATION_THEOREM_NOT_NATIVE_STOCKFISH",
        "theorem":"Two observationally indistinguishable causal SCMs under E0+bounded E3+E6 can disagree on natural mediator effect",
        "logical_late_SEE_mediator_kind":"site_activation_or_branch_occurrence_NOT_deterministic_see_ge_boolean_override",
        "two_constructive_counterexample_pairs":pairs,
        "finite_deterministic_observational_comparison_complete":True,
        "coverage_requirement":"E0 physical + E1 semantic use + exact E2 + untruncated E3 + E4 guard + E5 return + E6 root plus appropriate do mediator intervention",
        "natural_TT_SEE_mediation_proven_in_original_July_games":False,
        "no_independent_M5_test_or_new_native_treatment":True,
        "source_license":"Purely synthetic mathematical counterexample. No source PGN, Stockfish binary or engine changes."}
def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    doc=constructive_counterexamples()
    output=Path(a.out)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(doc,sort_keys=True,indent=2)+"\n")
    print("C3X025_P6_CAUSAL_NONIDENTIFICATION_PAIRS",
          {k:{"models":v["original_structural_models"],
              "NIE":(v["mediator_NIE_direct_or_null"],v["mediator_NIE_late_SEE_or_compensated"])}
           for k,v in doc["two_constructive_counterexample_pairs"].items()},flush=True)
    print("C3X025_P6_JSON_SHA256",hashlib.sha256(output.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
