from __future__ import annotations
import itertools,json
from typing import Any

CONSTITUTIVE_FEATURES=("relation_delta","response_topology","falsifier_pattern")

def _canon(x:Any)->str:
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def relation_delta(c:dict)->str:
    b=c["board_trigger"]
    return _canon({
      "moved_side_role":b["moved_side_role"],
      "target_atom":b["target_atom"],
      "before":b["relation_before"],
      "after":b["relation_after"],
    })

def response_topology(c:dict)->str:
    return _canon(c["response_topology"])

def falsifier_pattern(c:dict)->str:
    return _canon(c["falsifier"])

def feature_key(c:dict,features)->tuple:
    out=[]
    for f in features:
        if f=="relation_delta": out.append(relation_delta(c))
        elif f=="response_topology": out.append(response_topology(c))
        elif f=="falsifier_pattern": out.append(falsifier_pattern(c))
        elif f=="exact_signature": out.append(c["exact_signature"])
        elif f=="surface": out.append(_canon(c["surface"]))
        else: raise KeyError(f)
    return tuple(out)

def constitutive_core(c:dict)->tuple:
    # Frozen P6 identity witness. Falsifier/minimality remains an authority obligation,
    # not a discriminative identity feature.
    return feature_key(c,("relation_delta","response_topology"))

def independent_provenance(a:dict,b:dict)->bool:
    return a["source_id"]!=b["source_id"] and a["position_id"]!=b["position_id"]

def authority_compatible(a:dict,b:dict)->bool:
    return falsifier_pattern(a)==falsifier_pattern(b) and a["falsifier"]["chain_relative_minimality"] is True

def classify_pair(a:dict,b:dict)->dict[str,Any]:
    same_exact=a["exact_signature"]==b["exact_signature"]
    same_rel=relation_delta(a)==relation_delta(b)
    same_resp=response_topology(a)==response_topology(b)
    same_surface=feature_key(a,("surface",))==feature_key(b,("surface",))
    same_core=same_rel and same_resp
    independent=independent_provenance(a,b)
    if same_core and authority_compatible(a,b):
        cls="COMPOSITION_CORE_MATCH" if independent else "SAME_CORE_PROVENANCE_DEPENDENT"
    elif same_rel and not same_resp:
        cls="SAME_BOARD_TRIGGER_DIFFERENT_SEARCH_MANIFESTATION"
    elif same_resp and not same_rel:
        cls="SAME_SEARCH_RESPONSE_DIFFERENT_BOARD_TRIGGER"
    elif same_surface:
        cls="DIFFERENT_CAUSE_SAME_CONSEQUENCE"
    else:
        cls="NONCOMPARABLE"
    return {
      "class":cls,"same_exact_signature":same_exact,"same_relation_delta":same_rel,
      "same_response_topology":same_resp,"same_constitutive_core":same_core,
      "same_surface_consequence":same_surface,"independent_provenance":independent,
      "authority_compatible":authority_compatible(a,b),
    }

def minimal_witness_sets(certs:dict[str,dict],negative_pairs:list[dict])->list[list[str]]:
    feats=list(CONSTITUTIVE_FEATURES)
    valid=[]
    for r in range(1,len(feats)+1):
        for subset in itertools.combinations(feats,r):
            if all(feature_key(certs[p["a"]],subset)!=feature_key(certs[p["b"]],subset) for p in negative_pairs):
                valid.append(list(subset))
        if valid: break
    return valid

def development_adjudication(ecology:dict)->dict[str,Any]:
    certs={c["id"]:c for c in ecology["certificates"]}
    negatives=ecology["mandated_negative_pairs"]
    minimal=minimal_witness_sets(certs,negatives)
    same_exact_counter=classify_pair(certs["P5_1663_BERSERK"],certs["P5_1663_ETHEREAL"])
    same_resp_counter=classify_pair(certs["P5_1664_ETHEREAL"],certs["P5_1663_BERSERK"])
    pass_=(
      same_exact_counter["same_exact_signature"] and not same_exact_counter["same_response_topology"]
      and same_resp_counter["same_response_topology"] and not same_resp_counter["same_relation_delta"]
      and ["relation_delta","response_topology"] in minimal
    )
    return {
      "verdict":"PASS_CONJUNCTIVE_CONSTITUTIVE_CORE_PRESEALED" if pass_ else "FAIL_DEVELOPMENT_IDENTITY_CONSTITUTION",
      "minimal_witness_sets":minimal,
      "exact_signature_counterexample":same_exact_counter,
      "response_only_counterexample":same_resp_counter,
      "constitutive_core_features":["relation_delta","response_topology"],
      "falsifier_role":"AUTHORITY_OBLIGATION_NOT_IDENTITY_SHORTCUT",
    }
