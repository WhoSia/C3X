#!/usr/bin/env python3
"""C3X S4-H2/R2: retain auditable physical TT mask -> child -> root links.

Requires exact source-mask receipt identity (not a postprobe miss), matching
invocation ID/parent, true pre-hit, after-mask miss and signed value relation.
Bounded event logs do not prove whole-tree mediation.
"""
ARMS=("original","sham","zero","one","two","many")

def verify_and_preserve(masks, edges, target):
    result={}
    for arm in ARMS:
        raw=masks[arm]
        physical={}
        ordinals=set()
        for r in raw:
            ident=r["id"]
            ordinal=int(r["ordinal"])
            if ident in physical or ordinal in ordinals:
                raise ValueError("S4H2_R2_DUPLICATE_PHYSICAL_MASK")
            if (r["key"]!=str(target) or r["ply"]!="1" or
                r["hit_before"]!="1" or r["hit_after"]!="0"):
                raise ValueError("S4H2_R2_NOT_ACTUAL_TARGET_MASK")
            physical[ident]=r
            ordinals.add(ordinal)
        if arm in ("original","sham","zero") and raw:
            raise ValueError("S4H2_R2_MASK_IN_NEGATIVE_CONTROL")
        if arm=="one" and len(raw)>1 or arm=="two" and len(raw)>2 or arm=="many" and len(raw)>8:
            raise ValueError("S4H2_R2_MASK_LOG_BOUND")
        if ordinals!=set(range(len(raw))):
            raise ValueError("S4H2_R2_MASK_ORDINAL_GAP")
        matched=[]
        seen=set()
        for edge in edges[arm]["records"]:
            receipt=physical.get(edge["child_id"])
            if receipt is None:continue
            if edge["child_id"] in seen:
                raise ValueError("S4H2_R2_DUPLICATE_PHYSICAL_LINK")
            seen.add(edge["child_id"])
            if (edge["parent_id"]!=receipt["parent"] or
                edge["probe_hit_after_mask"]!="0" or
                edge["root_score"]!=-edge["child_return"]):
                raise ValueError("S4H2_R2_FALSE_PARENT_OR_VALUE_LINK")
            matched.append({
                "physical_mask_ordinal":int(receipt["ordinal"]),
                "physical_tt_key":receipt["key"],
                "child_invocation_id":edge["child_id"],
                "parent_root_invocation_id":edge["parent_id"],
                "child_return_value":edge["child_return"],
                "observed_root_candidate_value":edge["root_score"],
                "root_move_raw":edge["root_raw_move"]})
        result[arm]={
            "mask_receipts":raw,
            "physically_supported_child_root_arithmetic_links":matched,
            "bounded_mask_count":len(raw),
            "verified_links":len(matched),
            "physical_mask_log_truncated_possible":arm=="many" and len(raw)==8,
            "not_full_counterfactual_mediation":True}
    return result
