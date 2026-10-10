#!/usr/bin/env python3
"""Precommitted C3X0.23-P1 native exact-descendant SEE identity matcher.

Input: cold repeated, same original game AND root order, first physical TT
block verified elsewhere. Compare observed source-passive SEE events from
OBS baseline and V FIRST with key64, ancestry hash, parent_key64, path length,
rootcall, root native move, SEE native move, site and threshold. Log prefix
censoring prevents global negative claims. A shared node is only identity
eligible: NOT proof SEE naturally mediates TT by itself.
"""
from collections import Counter
FIELDS=("root_call","root_move","key64","parent_key64","path_hash",
        "path_length","move","site","threshold")
QUALIFY_KINDS=("witness",)

def identity(event):
    if event.get("kind") not in QUALIFY_KINDS:return None
    if any(f not in event for f in FIELDS):
        raise ValueError("C3X023_SHARED_NATIVE_SEE_INCOMPLETE_OR_NOT_PATH_TAGGED")
    if event["path_length"]<=0:
        raise ValueError("C3X023_SHARED_NATIVE_SEE_INVALID_ANCESTRY_LENGTH")
    if event["key64"]==0:
        raise ValueError("C3X023_SHARED_NATIVE_SEE_INVALID_NODE_KEY")
    return tuple(event[f] for f in FIELDS)

def candidates(source_original,source_first,physical_source_witness):
    """physical_source_witness: actual exact entry+call blocked and writer
    source checked by earlier C3X018/019 physical full64 proof.
    NEVER use numeric root-call alone across path-divergent worlds.
    """
    if not physical_source_witness:
        return {"status":"HOLD_MISSING_ACTUAL_PHYSICAL_TT_FIRST_READER_BLOCK",
                "matched":[],"first_shared":None}
    obs=[(i,identity(x),x) for i,x in enumerate(source_original)
         if x.get("kind") in QUALIFY_KINDS]
    treated=[(i,identity(x),x) for i,x in enumerate(source_first)
             if x.get("kind") in QUALIFY_KINDS]
    obs_count=Counter(z[1] for z in obs);treated_count=Counter(z[1] for z in treated)
    shared=set(obs_count)&set(treated_count)
    matches=[]
    for key in sorted(shared):
        if obs_count[key]!=1 or treated_count[key]!=1:
            # Repeated identical path fingerprints within the same rootcall
            # cannot identify a unique *event occurrence*; fail closed.
            continue
        oi,_,o=next(x for x in obs if x[1]==key)
        ti,_,t=next(x for x in treated if x[1]==key)
        if o.get("original")!=o.get("delivered") or t.get("original")!=t.get("delivered"):
            raise ValueError("C3X023_SEE_SOURCE_TRACE_NOT_PASSIVE")
        if o["original"]!=t["original"]:
            raise ValueError("C3X023_SAME_SOURCE_NODE_DIFFERS_NATIVE_SEE_BOOLEAN")
        matches.append({"exact_source_identity":dict(zip(FIELDS,key)),
                        "untreated_prefix_event_index":oi,
                        "TT_FIRST_prefix_event_index":ti,
                        "observed_native_see_original_Boolean":o["original"],
                        "position_key_and_ordered_ancestor_64bit_path_equal":True,
                        "source_parent_key_equal":True,
                        "full_raw_chess_path_bytes_proved":False})
    matches.sort(key=lambda m:(m["untreated_prefix_event_index"],
                               m["TT_FIRST_prefix_event_index"]))
    censored=any(x.get("kind")=="censored" for x in source_original+source_first)
    return {"status":"SOURCE_PATH_FINGERPRINT_COMMON_NODE_IDENTIFIED" if matches
                   else "NO_SHARED_SEE_NODE_IN_OBSERVED_PREFIX__CENSORED_HOLD" if censored
                   else "NO_SHARED_SEE_NODE_IN_FULL_LOGGED_SCOPE",
            "matched":matches,"first_shared":matches[0] if matches else None,
            "observed_prefix_censored":censored,
            "dropped_nonunique_repeated_source_identities":len(
                [k for k in shared if obs_count[k]!=1 or treated_count[k]!=1]),
            "no_natural_mediation_conclusion_without_exact_actuator_AND_aligned_paths":True}
