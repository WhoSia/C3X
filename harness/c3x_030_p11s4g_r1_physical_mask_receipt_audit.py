#!/usr/bin/env python3
"""C3X S4G/R1: rectify POST-PROBE hit=0 versus ACTUALLY MASKED provenance.

Original S4G result field "observed_links_with_masked_TT_hit" previously
counted all after-probe hit=0 (including natural cache misses).
This independent raw-byte auditor counts ONLY invocation IDs explicitly in
C3X_S4G_MASK physical source receipts, and follows their same-invocation
normal-return -> parent root candidate signed equality. No new engine search.
"""
import argparse,hashlib,json
from pathlib import Path

ORIGINAL_SHA="71cecc490edad3090263e7695359e21568b8206a53fe213cff633c12c18ccecf"
ORIGINAL_SCHEMA="c3x030-s4g-same-binary-TT-dose-invocation-court-v1"
SCHEMA="c3x030-s4g-r1-physical-source-mask-provenance-correction-v1"
ARMS=("original","sham","zero","one","two","many")

def sha(data):return hashlib.sha256(data).hexdigest()

def audit(source):
    if source.get("schema")!=ORIGINAL_SCHEMA or source.get("status")!="PASS_SOURCE_MASK_AND_VALUE_EDGE_OBSERVATION":
        raise ValueError("S4GR1_HOLD_ORIGINAL_SCHEMA_STATUS")
    if source.get("native_searches")!=36 or source.get("negative_controls_equal") is not True:
        raise ValueError("S4GR1_HOLD_ORIGINAL_NATIVE_SCOPE")
    if len(source.get("positions",{}))!=3:raise ValueError("S4GR1_HOLD_ORIGINAL_FEN_SCOPE")
    report={"schema":SCHEMA,"original_native_source_sha256":ORIGINAL_SHA,
            "original_native_searches_inherited":36,"new_native_searches":0,
            "original_native_nodes_inherited":source["native_actual_nodes"],
            "corrects_postprobe_hitfalse_as_NOT_necessarily_masked":True,
            "scope_is_reused_development_FENs":True,
            "proves_unique_TT_cell_causal_mediator":False,
            "proves_full_parent_root_counterfactual_mediation":False,
            "results":{}}
    for pos,case in sorted(source["positions"].items()):
        arms={}
        for arm in ARMS:
            physical=case["source_mask_receipts"][arm]
            physical_by_id={}
            for p in physical:
                id=p.get("id")
                if id in physical_by_id:raise ValueError("S4GR1_HOLD_DUPLICATE_PHYSICAL_MASK_INVOCATION")
                if p.get("hit_before")!="1" or p.get("hit_after")!="0" or p.get("ply")!="1":
                    raise ValueError("S4GR1_HOLD_INVALID_PHYSICAL_MASK")
                if p.get("key")!=case["frozen_physical_TT_key"]:
                    raise ValueError("S4GR1_HOLD_MASKED_WRONG_SOURCE_KEY")
                physical_by_id[id]=p
            records=case["same_invocation_arithmetic_edges"][arm]["records"]
            true_links=[]
            for e in records:
                if e["child_id"] not in physical_by_id:continue
                physical_receipt=physical_by_id[e["child_id"]]
                if (e["parent_id"]!=physical_receipt["parent"]
                    or e["probe_hit_after_mask"]!="0"
                    or e["root_score"]!=-e["child_return"]):
                    raise ValueError("S4GR1_HOLD_FALSE_PHYSICAL_MASK_LINK")
                true_links.append({
                    "exact_native_masked_invocation_id":e["child_id"],
                    "parent_root_invocation_id":e["parent_id"],
                    "actual_child_return":e["child_return"],
                    "actual_root_candidate_value":e["root_score"],
                    "physical_mask_ordinal":int(physical_receipt["ordinal"])
                })
            masks=len(physical)
            raw_zero=case["same_invocation_arithmetic_edges"][arm]["observed_links_with_masked_TT_hit"]
            if len(true_links)>masks or len(true_links)>raw_zero:
                raise ValueError("S4GR1_HOLD_COUNT_IMPLAUSIBILITY")
            arms[arm]={
                "actual_physical_mask_receipts_bounded":masks,
                "postprobe_hitfalse_negamax_edges_in_prior_result":raw_zero,
                "actual_physically_masked_invocation_negamax_edges":len(true_links),
                "physically_supported_links":true_links,
                "root_bestmove_changed_trials_against_sham":case["root_move_changes_vs_sham"][arm],
                "unlogged_masked_contacts_may_exist":arm=="many",
            }
        report["results"][pos]=arms
    report["physical_mask_link_totals"]={arm:sum(p[arm]["actual_physically_masked_invocation_negamax_edges"]
        for p in report["results"].values()) for arm in ARMS}
    report["old_postprobe_zero_links_totals"]={arm:sum(p[arm]["postprobe_hitfalse_negamax_edges_in_prior_result"]
        for p in report["results"].values()) for arm in ARMS}
    report["status"]="PASS_SOURCE_RECEIPT_IDENTIFIED_PHYSICAL_RETURN_ROOT_LINKS"
    return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--original",required=True);ap.add_argument("--out",required=True)
    args=ap.parse_args()
    raw=Path(args.original).read_bytes()
    if sha(raw)!=ORIGINAL_SHA:raise ValueError("S4GR1_HOLD_FROZEN_ORIGINAL_RAW_SHA")
    x=audit(json.loads(raw))
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("S4GR1_PHYSICAL_MASK_RETURN_ROOT_CORRECTED",x["physical_mask_link_totals"],
          "OLDER_AMBIGUOUS_POSTPROBE_ZERO_COUNT",x["old_postprobe_zero_links_totals"],
          "ZERO_NEW_NATIVE_SEARCHES",x["new_native_searches"],
          "JSON_SHA",sha(dest.read_bytes()))
if __name__=="__main__":main()
