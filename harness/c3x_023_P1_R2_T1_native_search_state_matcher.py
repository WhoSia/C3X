#!/usr/bin/env python3
"""Strict T1 read-only native SEE source+computational state equality.

Prior T0 matched observed events by 64-bit ancestor digest. T1 must also
validate full ordered ancestor key VECTOR, live ply/depth/alpha/beta/PV,
rule50, input pos.pieces and branch site. Do not claim proof of all implicit
search state (TT, contHistory, stack, NNUE); label scoped-source-aligned only.
"""
from collections import Counter
from c3x_023_P1_same_descendant_SEE_node_matcher import identity,FIELDS

EXTRA=("path_exact","source_ply","source_depth","source_alpha","source_beta",
       "source_pv","source_rule50","source_occupancy64","occupied_is_output_arg",
       "input_occ_defined","branch_prune_if_no_extra_capture_guard",
       "branch_direct_continuation")
COMPUTE=("path_exact","source_ply","source_depth","source_alpha","source_beta",
         "source_pv","source_rule50","source_occupancy64","occupied_is_output_arg",
         "input_occ_defined")
SITES=("quiet_prune","qsearch_prune","qsearch_futility","capture_prune")

def whole(event):
    key=identity(event)
    if key is None:return None
    missing=[f for f in EXTRA if f not in event]
    if missing:raise ValueError("T1_NATIVE_SEARCH_STATE_FIELD_MISSING_"+",".join(missing))
    path=event["path_exact"]
    if not isinstance(path,str) or not path or any(
            not tok or any(c not in "0123456789abcdef" for c in tok)
            for tok in path.split(",")):
        raise ValueError("T1_RAW_ANCESTOR_KEY_VECTOR_UNPARSABLE")
    if len(path.split(","))!=event["path_length"]:
        raise ValueError("T1_EXACT_ANCESTOR_LENGTH_MISMATCH")
    if int(path.split(",")[-1],16)!=event["key64"]:
        raise ValueError("T1_EXACT_ANCESTOR_LAST_KEY_MISMATCH")
    if event["path_length"]>=2 and int(path.split(",")[-2],16)!=event["parent_key64"]:
        raise ValueError("T1_EXACT_ANCESTOR_PARENT_KEY_MISMATCH")
    if event["site"] not in SITES or event["input_occ_defined"]!=1:
        raise ValueError("T1_NATIVE_SEE_SOURCE_SITE_OR_DEFINED_INPUT_INVALID")
    if event["original"]!=event["delivered"] or event["altered"]!=0:
        raise ValueError("T1_ACTUATED_SEE_NOT_PASSIVE")
    if event["source_alpha"]>=event["source_beta"]:
        raise ValueError("T1_INVALID_SEARCH_ALPHA_BETA")
    return tuple(event[f] for f in FIELDS),tuple(event[f] for f in COMPUTE)

def trace(x):
    ans={}
    for row in x["ordered_source_operator_trace"]:
        if row["source"]!="native_SEE" or row["fields"].get("kind")!="witness":
            continue
        node,computational=whole(row["fields"])
        ans.setdefault(node,[]).append({"line":row["line_ordinal"],
                                        "state":computational,"event":row["fields"]})
    return ans

def compare_original_treated(original,treated,first_use_original,first_block_treated):
    # Both ordinals are actual source witnessed events, not inferred from
    # score difference or bestmove change.
    left,right=trace(original),trace(treated)
    c=Counter();common=0;after_count=0;strict=[];partial=[]
    censored=any(e["kind"]=="censored" for e in
        original["native_see_events"]+treated["native_see_events"])
    for key in set(left)&set(right):
        lo,rt=left[key],right[key]
        if len(lo)!=1 or len(rt)!=1:
            c["DUPLICATE_SOURCE_IDENTITY"]+=1;continue
        common+=1
        a,b=lo[0],rt[0]
        if not (a["line"]>first_use_original and b["line"]>first_block_treated):
            c["BEFORE_TT_SOURCE_EVENT"]+=1;continue
        after_count+=1
        if a["state"]!=b["state"]:
            diffs=[f for f,ai,bi in zip(COMPUTE,a["state"],b["state"])
                   if ai!=bi]
            for diff in diffs:c["DIFFERENT_"+diff]+=1
            partial.append({"source_key":dict(zip(FIELDS,key)),"state_mismatch":diffs,
                            "natural_SEE_original_bool_equal":
                              a["event"]["original"]==b["event"]["original"]})
            continue
        if a["event"]["original"]!=b["event"]["original"]:
            raise ValueError("T1_IDENTICAL_SEE_STATE_DIFFERENT_BOOLEAN_NEEDS_SOURCE_AUDIT")
        strict.append({"source_key":dict(zip(FIELDS,key)),
                       "state":dict(zip(COMPUTE,a["state"])),
                       "SEE_original_boolean":a["event"]["original"],
                       "original_native_line_ordinal":a["line"],
                       "TT_FIRST_native_line_ordinal":b["line"],
                       "source_legal_site_only":a["event"]["site"] in
                         ("quiet_prune","qsearch_prune","qsearch_futility"),
                       "equal_subset_of_search_state_not_all_stack_history":True})
    strict.sort(key=lambda e:(e["original_native_line_ordinal"],
                              e["TT_FIRST_native_line_ordinal"]))
    counts={k:v for k,v in sorted(c.items())}
    return {"status":("POST_TT_COMPUTATIONAL_SEE_INPUT_WINDOW_MATCH" if strict
               else "SAME_POSITION_PATH_DIFFERENT_COMPUTATIONAL_STATE" if partial
               else "HOLD_CENSORED_NO_COMPUTATIONAL_EVENT" if censored
               else "NO_POST_TT_COMPUTATIONAL_EVENT_IN_WATCH_SCOPE"),
            "source_chess_path_matches_any_time":common,
            "source_chess_path_matches_post_TT_use_in_both_arms":after_count,
            "post_TT_full_search_window_state_matches":len(strict),
            "post_TT_same_chess_path_but_different_state":len(partial),
            "site_kinds_with_strict_full_match":dict(sorted(Counter(
                x["source_key"]["site"] for x in strict).items())),
            "differences_by_field":counts,
            "first_two_full_computational_match_candidates":strict[:2],
            "first_two_chess_path_same_but_search_state_diff":partial[:2],
            "first32_prefix_censored":censored,
            "original_SEE_boolean_was_changed":False,
            "natural_mediation_not_claimed":True,
            "note":"Matches fully explicit measured tuple, not all hidden search state."}
