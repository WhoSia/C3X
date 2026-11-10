"""C3X 0.30/R2 — exact finite-coalition Shapley kernel, piece-attribution donor.

Read original Drive-owned Spinnato (2025):
https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view
'Towards Piece-by-Piece Explanations for Chess Positions with SHAP'
The original paper uses nonking pieces as features, king-only baseline,
Stockfish 17.1 and a SamplingExplainer with up to 10,000 perturbations.
This module computes exact Shapley for *small complete coalition tables*;
it is NOT the original 10000-sample chess explanation benchmark.

All coalition values must come from a declared common evaluator with no
missing masks. No invalid chess positions, imputation or normalization is
hidden here. Thus this is a mathematically exact method component, NOT a
source-engine natural decision cause.
"""
import argparse
import json
import math
from pathlib import Path


def shapley_exact(feature_names, coalition_values):
    if (not isinstance(feature_names,list) or not 1 <= len(feature_names) <= 12
        or any(type(x) is not str or not x for x in feature_names)
        or len(set(feature_names))!=len(feature_names)
        or not isinstance(coalition_values,dict)):
        raise ValueError("R030_SHAP_HOLD_NONKING_FEATURE_SUPPORT")
    n=len(feature_names)
    masks={str(k) for k in range(1<<n)}
    if set(coalition_values)!=masks:
        raise ValueError("R030_SHAP_HOLD_COMPLETE_COALITION_TABLE_REQUIRED")
    if any(type(v) not in (int,float) or not math.isfinite(v)
           for v in coalition_values.values()):
        raise ValueError("R030_SHAP_HOLD_NONFINITE_EVALUATOR_OUTPUT")
    # Shapley_i = sum_{S ⊆ N\{i}} |S|!(n-|S|-1)!/n! * (v(S∪{i})-v(S)).
    weights={k:(1.0/n)/math.comb(n-1,k) for k in range(n)}
    effects={}
    for i,key in enumerate(feature_names):
        terms=[]
        for s in range(1<<n):
            if s & (1<<i): continue
            marginal=coalition_values[str(s|(1<<i))]-coalition_values[str(s)]
            terms.append(weights[s.bit_count()]*marginal)
        effects[key]=math.fsum(terms)
    baseline=coalition_values["0"]
    final=coalition_values[str((1<<n)-1)]
    reconstructed=baseline+math.fsum(effects.values())
    discrepancy=final-reconstructed
    scale=max(1.0,abs(baseline),abs(final))
    if abs(discrepancy)>1e-10*scale:
        raise ValueError("R030_SHAP_HOLD_ADDIVITY_FAILED")
    return {
        "schema":"c3x030-r2-exact-shapley-finite-coalitions-v1",
        "owned_primary_source_pdf":"https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view",
        "method":"exact discrete Shapley over fully specified coalitions, not paper's SamplingExplainer",
        "features":feature_names,
        "baseline_coalition_value":baseline,
        "complete_coalition_value":final,
        "piece_feature_shapley_values":effects,
        "efficiency_residual":discrepancy,
        "coalitions_evaluated":len(coalition_values),
        "chess_piece_removal_may_be_illegal":True,
        "source_decision_causality_inferred":False,
        "full_chess_SHAP_reproduction":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    d=json.loads(Path(a.input).read_text(encoding="utf-8"))
    out=shapley_exact(d["feature_names"],d["coalition_values"])
    dest=Path(a.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("C3X_030_R2_SHAPLEY_EXACT_COMPLETE_COALITIONS",out["coalitions_evaluated"])

if __name__=="__main__":
    main()
