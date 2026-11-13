#!/usr/bin/env python3
"""C3X 0.30/F3: paper-aligned BinProp concept evaluation adapter.

Implements the *documented* BinProp support-fit and held-out triplet-score
metrics for already-executed Boolean chess predicates. Does NOT synthesize
positions, engine evaluations, independent labels, motifs, or empirical wins.

Other explanation types (SARFA saliency, SHAP piece attribution, native
Stockfish TT events) must not be silently coerced into Boolean motifs.
They require separately preregistered adapters and independent label audits.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SCHEMA="c3x030-f3-binary-concept-matched-episode-v1"
GROUPS={"support_positive":4,"support_negative":4,
        "holdout_positive":8,"holdout_negative":8,
        "holdout_nearby_negative":8}
METHODS=("direct","binprop","c3x_boolean_concept")

def ratio(v, wanted):
    return sum(x is wanted for x in v)/len(v)

def check_episode(e):
    if e.get("schema")!=SCHEMA or e.get("labels_are_external") is not True:
        raise ValueError("F3_NO_EXTERNAL_GROUND_TRUTH")
    if e.get("paper_episode_same_game_continuations") is not True:
        raise ValueError("F3_EPISODE_LINEAGE_UNDECLARED")
    pools=e.get("pools",{})
    if set(pools)!=set(GROUPS):
        raise ValueError("F3_PAPER_POOL_SCHEMA")
    seen=set()
    for name,count in GROUPS.items():
        members=pools[name]
        if not isinstance(members,list) or len(members)!=count:
            raise ValueError("F3_PAPER_POOL_SIZE")
        for item in members:
            if not isinstance(item,dict) or set(item)!={"position_id","game_id","fen"}:
                raise ValueError("F3_POOL_ROW_IDENTITY")
            if any(not isinstance(item[k],str) or not item[k] for k in item):
                raise ValueError("F3_POOL_ROW_EMPTY")
            ident=item["position_id"]
            if ident in seen:
                raise ValueError("F3_SUPPORT_HELDOUT_POSITION_OVERLAP")
            seen.add(ident)
    if not isinstance(e.get("episode_id"),str) or not e["episode_id"]:
        raise ValueError("F3_EPISODE_ID")
    if set(e.get("methods",{}))-set(METHODS):
        raise ValueError("F3_UNCOMPARABLE_METHOD_FAMILY")
    return pools

def score_candidate(c):
    if not isinstance(c,dict) or set(c)!={"name","delta","predictions","valid","source_kind"}:
        raise ValueError("F3_MOTIF_CONTRACT")
    if c["valid"] is not True or c["source_kind"] not in ("externally_executed_boolean","paper_released_boolean"):
        raise ValueError("F3_UNVERIFIED_MOTIF_EXECUTION")
    delta=c["delta"]
    if not isinstance(delta,(float,int)) or isinstance(delta,bool) or not math.isfinite(delta) or delta<=0 or delta>1:
        raise ValueError("F3_MOTIF_DELTA_MUST_BE_EXTERNAL_POSITIVE")
    preds=c["predictions"]
    if set(preds)!=set(GROUPS):
        raise ValueError("F3_PREDICTION_POOL_SCHEMA")
    for group,count in GROUPS.items():
        v=preds[group]
        if not isinstance(v,list) or len(v)!=count or any(type(x) is not bool for x in v):
            raise ValueError("F3_PREDICTION_LENGTH_OR_BOOLEAN")
    support_pos=ratio(preds["support_positive"],True)
    support_neg=ratio(preds["support_negative"],False)
    fit=min(support_pos,support_neg)
    heldout_rates={
      "positive_true":ratio(preds["holdout_positive"],True),
      "negative_false":ratio(preds["holdout_negative"],False),
      "nearby_negative_false":ratio(preds["holdout_nearby_negative"],False)}
    return {"name":c["name"],"delta":delta,"support_fit":fit,
       "weighted_fit":fit*delta,
       "heldout_rates":heldout_rates,
       "score":min(heldout_rates.values())}

def evaluate_episode(e):
    check_episode(e)
    rows={}
    for method in METHODS:
        candidates=e["methods"].get(method,[])
        if not isinstance(candidates,list):
            raise ValueError("F3_METHOD_LIST")
        scored=[score_candidate(x) for x in candidates]
        if len({x["name"] for x in scored})!=len(scored):
            raise ValueError("F3_DUPLICATE_MOTIF")
        if method=="binprop":
            scored.sort(key=lambda x:(-x["weighted_fit"],-x["support_fit"],-x["delta"],x["name"]))
        else:
            # Direct / C3X models are required to preregister their ranking:
            # preserve caller order; do not rank by heldout outcomes.
            if e.get("ranking_frozen_before_heldout") is not True:
                raise ValueError("F3_UNSEALED_NONBINPROP_RANK")
        qualified=[x for x in scored if x["support_fit"]>=0.5]
        selected=qualified[:3]
        used_fallback=False
        if not selected and scored:
            selected=scored[:1]
            used_fallback=True
        rows[method]={"candidate_count":len(scored),"qualified_count":len(qualified),
          "selection_names":[x["name"] for x in selected],
          "used_fallback":used_fallback,
          "score":sum(x["score"] for x in selected)/len(selected) if selected else 0.,
          "no_valid_motif":not bool(scored),
          "paper_metric_only_not_independent_game_holdout":True}
    return {"schema":"c3x030-f3-binprop-comparator-result-v1",
       "episode_id":e["episode_id"],"methods":rows,
       "real_engine_searches":0,"empirical_results_provenance":"INPUT_ONLY",
       "comparison_is_method_family_specific":True,
       "source_engine_causal_mediation_proven":False,
       "paper_superiority_verdict":"HOLD",
       "game_disjoint_external_cohort_claim":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    e=json.loads(Path(args.input).read_text())
    result=evaluate_episode(e)
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("F3_BINPROP_PAPER_METRIC_CONTRACT",result["episode_id"],"NO_NEW_ENGINE_SEARCHES")
if __name__=="__main__":main()
