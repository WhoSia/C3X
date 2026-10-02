from __future__ import annotations
import json
from pathlib import Path
from typing import Any

STAGE_TITLE="C3X 0.8.0-G10-P3 — Sealed-Evidence Explanation-Invariant Constitution, Canonical-State→Preference-Sign→Candidate-Fate→Local-Causal-Certificate Quotient Lattice, Metrology↔Mechanism Back-Transport, Chess-Native Consequence Preservation, Counterexample-Guided Coarsening & Minimal Explanation-Object Court"

CANDIDATES=[
    "CANONICAL_STATE",
    "REGIME_TAGGED_PAIR_SIGN",
    "CANDIDATE_FATE",
    "INTERVENTION_RESPONSE",
    "LOCAL_CAUSAL_CERTIFICATE",
]

AUTHORITY_ORDER={
    "CANONICAL_STATE":"MEASUREMENT_STATE_ONLY",
    "REGIME_TAGGED_PAIR_SIGN":"MEASUREMENT_ROUTING_ONLY",
    "CANDIDATE_FATE":"CHESS_NATIVE_SURFACE_ONLY",
    "INTERVENTION_RESPONSE":"MECHANISM_CANDIDATE_ONLY",
    "LOCAL_CAUSAL_CERTIFICATE":"LOCAL_CAUSAL_EXPLANATION",
}

def load_json(path:str|Path)->dict[str,Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _mediation_status_counts(p12:dict[str,Any])->dict[str,int]:
    return dict((p12.get("science") or {}).get("mediation_status_counts") or {})

def build_evidence(metrology:dict[str,Any],p12:dict[str,Any],p16:dict[str,Any])->dict[str,Any]:
    m03=metrology["metrology_0_3"]
    m04=metrology["metrology_0_4"]
    m05=metrology["metrology_0_5"]
    m06=metrology["metrology_0_6"]
    p12s=p12["science"]
    p16r=p16["result"]
    cert=p16["representative_minimal_bridge"]
    return {
        "metrology":{
            "canonical_repeatability_zero_positions_each_movetime_arm":m03["canonical_repeatability_zero_positions_each_arm"],
            "pair_sign_repeatability_1000ms":m03["pair_sign_repeatability_1000ms"],
            "nonzero_fixed_node_sign_transport_1000ms":m03["nonzero_fixed_node_sign_transport_1000ms"],
            "fixed_node_load_canonical_identity":m04["fixed_node_load_canonical_identity"],
            "movetime_load_canonical_difference":m04["movetime_load_canonical_difference"],
            "movetime_load_pair_sign_difference":m04["movetime_load_pair_sign_difference"],
            "realized_node_pair_sign_reproduction":m05["realized_node_pair_sign_reproduction"],
            "search_state_reproduction_without_node_counter":m05["search_state_reproduction_without_node_counter"],
            "residual_states_exactly_reachable":m06["residual_states_exactly_reachable"],
        },
        "p12":{
            "root_change_targets":p12s["root_change_targets"],
            "mediated_targets":p12s["mediated_targets"],
            "mediation_status_counts":_mediation_status_counts(p12),
            "replicated_mediated_transition_signatures":p12s["replicated_mediated_transition_signatures"],
        },
        "p16":{
            "minimal_full_bridge_records":p16r["minimal_full_bridge_records"],
            "certificate_count":p16r["certificate_count"],
            "replicated_exact_structural_signatures":p16r["replicated_exact_structural_signatures"],
            "replicated_coarse_full_bridge_signatures":p16r["replicated_coarse_full_bridge_signatures"],
            "representative_pair":cert["pair_uci"],
            "replication_status":cert["replication_status"],
            "subset_reproduced":cert["subset_reproduced"],
            "sham_reproduced":cert["sham_reproduced"],
        },
    }

def counterexamples(e:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    m=e["metrology"];p12=e["p12"];p16=e["p16"]

    # Exact state is too fine for robust preference routing across measurement regimes.
    if m["canonical_repeatability_zero_positions_each_movetime_arm"]==34 and m["pair_sign_repeatability_1000ms"]==34:
        out.append({
            "candidate":"CANONICAL_STATE",
            "failure":"NOT_NECESSARY_FOR_ROBUST_PREFERENCE_ROUTING",
            "witness":"METROLOGY_0_3",
            "detail":"Full canonical repeatability is 0/34 at every movetime arm while pair sign is repeat-stable 34/34 at 1000ms.",
        })

    # Pair sign is measurement-useful but not sufficient for causal mechanism identity.
    statuses=p12["mediation_status_counts"]
    if p12["root_change_targets"]>p12["mediated_targets"] and len([k for k,v in statuses.items() if v>0])>=2:
        out.append({
            "candidate":"REGIME_TAGGED_PAIR_SIGN",
            "failure":"MERGES_CAUSALLY_DISTINCT_ROOT_CHANGE_WITNESSES",
            "witness":"G9_5_P12",
            "detail":"The same root-change evidence class contains mediation-positive and colocation/partial cases; preference direction cannot identify mediation status.",
        })

    # Candidate fate also merges different mediation statuses.
    if statuses.get("CUTOFF_COLOCATION_ONLY",0)>0 and (
        statuses.get("EXACT_CUTOFF_BRIDGE",0)+statuses.get("EXACT_CUTOFF_INTERACTION_REDIRECT",0)
    )>0:
        out.append({
            "candidate":"CANDIDATE_FATE",
            "failure":"ROOT_CHOICE_TRANSITION_DOES_NOT_IDENTIFY_CAUSAL_BRIDGE",
            "witness":"G9_5_P12",
            "detail":"Legal root-choice change occurs both in exact-mediation and colocation-only witnesses.",
        })

    # Intervention response without falsifier/minimality fields is insufficient for certificate authority.
    if p16["minimal_full_bridge_records"]==1 and p16["subset_reproduced"] is False and p16["sham_reproduced"] is False:
        out.append({
            "candidate":"INTERVENTION_RESPONSE",
            "failure":"OMITS_MINIMALITY_AND_FALSIFIER_CONTRACT",
            "witness":"G9_5_P16",
            "detail":"P16 causal authority depends on failed subset/sham reproduction in addition to observed response.",
        })

    return out

def adjudicate(metrology:dict[str,Any],p12:dict[str,Any],p16:dict[str,Any])->dict[str,Any]:
    e=build_evidence(metrology,p12,p16)
    cx=counterexamples(e)
    failed={x["candidate"] for x in cx}

    routing_ok=(
        "REGIME_TAGGED_PAIR_SIGN" in failed
        and e["metrology"]["realized_node_pair_sign_reproduction"]==340
        and e["metrology"]["residual_states_exactly_reachable"]==4
    )
    candidate_surface_ok=(
        "CANDIDATE_FATE" in failed and e["p12"]["root_change_targets"]>0
    )
    certificate_ok=(
        e["p16"]["certificate_count"]==1
        and e["p16"]["replication_status"]=="LOCAL_ONLY"
        and e["p16"]["replicated_exact_structural_signatures"]==[]
        and e["p16"]["replicated_coarse_full_bridge_signatures"]==[]
    )

    if not certificate_ok:
        verdict="HOLD_SEALED_EVIDENCE_INSUFFICIENT_FOR_QUOTIENT_ADJUDICATION"
    elif routing_ok and candidate_surface_ok and {"CANONICAL_STATE","REGIME_TAGGED_PAIR_SIGN","CANDIDATE_FATE","INTERVENTION_RESPONSE"}<=failed:
        verdict="PASS_TWO_LEVEL_INVARIANT_ARCHITECTURE"
    else:
        verdict="PASS_FULL_CERTIFICATE_ONLY_CAUSAL_AUTHORITY"

    return {
        "schema":"c3x-g10-p3-invariant-court-v1",
        "stage":STAGE_TITLE,
        "verdict":verdict,
        "evidence":e,
        "counterexamples":cx,
        "adjudication":{
            "measurement_routing_object":{
                "representation":"REGIME_TAGGED_LEGAL_PAIR_PLUS_PREFERENCE_SIGN",
                "authority":"MEASUREMENT_ROUTING_ONLY",
                "reason":"Pair sign can remain stable when full canonical state does not, but must carry measurement-regime identity because movetime/load boundary cases can flip sign.",
            },
            "explanation_surface_object":{
                "representation":"LEGAL_CANDIDATE_FATE_OR_ROOT_CHOICE_TRANSITION",
                "authority":"CHESS_NATIVE_SURFACE_ONLY",
                "reason":"This is the coarsest object that preserves the legal chess consequence consumed by explanation, but P12 shows it does not identify mediation.",
            },
            "causal_authority_object":{
                "representation":"LOCAL_CAUSAL_CERTIFICATE",
                "authority":"LOCAL_CAUSAL_EXPLANATION",
                "reason":"P16 authority requires board intervention, exact search response, legal preference consequence, falsifiers and chain-relative minimality. LOCAL_ONLY ceiling is preserved.",
            },
            "single_universal_quotient_rejected":True,
        },
        "p2_predictions":[
            "Exact ordered/canonical identity should be less repeatable than regime-tagged pair/sign or candidate-neighborhood summaries.",
            "Any P2 stable-object representation that omits regime identity should fail near stopping-budget boundaries.",
            "Even a highly repeatable candidate-fate object must not be promoted to causal explanation authority without an independent local certificate.",
        ],
        "authority_ceiling":[
            "No new causal witness is created.",
            "P16 remains LOCAL_ONLY.",
            "P12 replicated colocation is not promoted to replicated mediation.",
            "No objective chess truth, human cognition or human utility claim is authorized.",
        ],
    }

def main(metrology_path:str,p12_path:str,p16_path:str,out_path:str)->None:
    result=adjudicate(load_json(metrology_path),load_json(p12_path),load_json(p16_path))
    Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
