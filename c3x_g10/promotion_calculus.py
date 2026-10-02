from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Iterable

class Authority(str, Enum):
    MEASUREMENT_ROUTING="MEASUREMENT_ROUTING"
    CHESS_NATIVE_SURFACE="CHESS_NATIVE_SURFACE"
    MECHANISM_CANDIDATE="MECHANISM_CANDIDATE"
    LOCAL_CAUSAL_EXPLANATION="LOCAL_CAUSAL_EXPLANATION"
    COMPOSITION_CANDIDATE="COMPOSITION_CANDIDATE"
    TRANSPORTABLE_CAUSAL_PATTERN="TRANSPORTABLE_CAUSAL_PATTERN"

@dataclass(frozen=True)
class PromotionRule:
    rule_id:str
    source:Authority
    target:Authority
    required_all:frozenset[str]
    forbidden_if_present:frozenset[str]=frozenset()

RULES={
    "ROUTING_TO_SURFACE":PromotionRule(
        "ROUTING_TO_SURFACE",Authority.MEASUREMENT_ROUTING,Authority.CHESS_NATIVE_SURFACE,
        frozenset({"LEGAL_POSITION","LEGAL_CANDIDATE_OBJECT","OBSERVED_CANDIDATE_FATE","PROVENANCE_BOUND"})
    ),
    "SURFACE_TO_MECHANISM":PromotionRule(
        "SURFACE_TO_MECHANISM",Authority.CHESS_NATIVE_SURFACE,Authority.MECHANISM_CANDIDATE,
        frozenset({"DECLARED_INTERVENTION","MATCHED_BASELINE","OBSERVED_INTERVENTION_RESPONSE","REGIME_IDENTITY","PROVENANCE_BOUND"})
    ),
    "MECHANISM_TO_LOCAL_CAUSAL":PromotionRule(
        "MECHANISM_TO_LOCAL_CAUSAL",Authority.MECHANISM_CANDIDATE,Authority.LOCAL_CAUSAL_EXPLANATION,
        frozenset({
            "EXACT_INTERVENTION_ADDRESS","LEGAL_CHESS_CONSEQUENCE",
            "SUBSET_FALSIFIER_FAILED","SHAM_FALSIFIER_FAILED",
            "CHAIN_RELATIVE_MINIMALITY","LOCAL_SCOPE_DECLARED","PROVENANCE_BOUND"
        }),
        frozenset({"FALSIFIER_CONTRADICTION"})
    ),
    "COMPOSITION_TO_TRANSPORT":PromotionRule(
        "COMPOSITION_TO_TRANSPORT",Authority.COMPOSITION_CANDIDATE,Authority.TRANSPORTABLE_CAUSAL_PATTERN,
        frozenset({
            "PROSPECTIVE_HELDOUT_REPLICATION","FROZEN_CORRESPONDENCE",
            "INDEPENDENT_WORLD_SUPPORT","FATAL_REPLICATION_SURVIVED",
            "TRANSPORT_SCOPE_DECLARED","PROVENANCE_BOUND"
        }),
        frozenset({"FALSIFIER_CONTRADICTION","CORRESPONDENCE_CHANGED_AFTER_OUTCOME"})
    ),
}

CAUSAL_WORDS={"causal","causes","caused","because_of_mechanism","mechanism_established"}

def _atoms(xs:Iterable[str])->frozenset[str]:
    return frozenset(str(x) for x in xs)

def evaluate_promotion(current:Authority|str, rule_id:str, evidence:Iterable[str])->dict[str,Any]:
    current=Authority(current); rule=RULES[rule_id]; ev=_atoms(evidence)
    if rule.source != current:
        return {
            "allowed":False,"current":current.value,"target":rule.target.value,"rule_id":rule_id,
            "satisfied":[],"missing":sorted(rule.required_all),
            "blockers":["SOURCE_AUTHORITY_MISMATCH"],"promotion_debt":sorted(rule.required_all),
        }
    missing=rule.required_all-ev
    blockers=rule.forbidden_if_present & ev
    allowed=not missing and not blockers
    return {
        "allowed":allowed,"current":current.value,
        "target":rule.target.value if allowed else current.value,
        "proposed_target":rule.target.value,"rule_id":rule_id,
        "satisfied":sorted(rule.required_all & ev),
        "missing":sorted(missing),"blockers":sorted(blockers),
        "promotion_debt":sorted(missing | blockers),
    }

def language_permissions(authority:Authority|str)->dict[str,Any]:
    a=Authority(authority)
    causal=a in {Authority.LOCAL_CAUSAL_EXPLANATION,Authority.TRANSPORTABLE_CAUSAL_PATTERN}
    transport=a==Authority.TRANSPORTABLE_CAUSAL_PATTERN
    return {
        "authority":a.value,
        "causal_language_allowed":causal,
        "transport_language_allowed":transport,
        "allowed_claim_types":{
            Authority.MEASUREMENT_ROUTING:["measurement_stability","preference_sign","routing"],
            Authority.CHESS_NATIVE_SURFACE:["legal_candidate_fate","root_choice_transition","chess_native_consequence"],
            Authority.MECHANISM_CANDIDATE:["intervention_response","mechanism_candidate"],
            Authority.LOCAL_CAUSAL_EXPLANATION:["local_causal_contrast","local_mechanism"],
            Authority.COMPOSITION_CANDIDATE:["cross_certificate_similarity","composition_hypothesis"],
            Authority.TRANSPORTABLE_CAUSAL_PATTERN:["transported_causal_pattern"],
        }[a],
    }

def guard_claim(authority:Authority|str, requested_claim_type:str)->dict[str,Any]:
    p=language_permissions(authority)
    causal=requested_claim_type in {"causal","local_causal_contrast","local_mechanism","transported_causal_pattern"}
    transport=requested_claim_type=="transported_causal_pattern"
    allowed=(not causal or p["causal_language_allowed"]) and (not transport or p["transport_language_allowed"])
    return {"allowed":allowed,"requested_claim_type":requested_claim_type,**p}

def compose_local_certificates(certificates:list[dict[str,Any]])->dict[str,Any]:
    debt=[]
    if len(certificates)<2: debt.append("AT_LEAST_TWO_LOCAL_CERTIFICATES")
    for i,c in enumerate(certificates):
        if c.get("authority")!="LOCAL_CAUSAL_EXPLANATION": debt.append(f"CERT_{i}_NOT_LOCAL_CAUSAL")
        if c.get("scope")!="LOCAL_ONLY": debt.append(f"CERT_{i}_SCOPE_NOT_LOCAL_ONLY")
    worlds=[c.get("world_id") for c in certificates]
    prov=[c.get("provenance_id") for c in certificates]
    grammars={c.get("intervention_grammar") for c in certificates}
    consequences={c.get("consequence_schema") for c in certificates}
    correspondences={c.get("correspondence_id") for c in certificates}
    if len(worlds)!=len(set(worlds)): debt.append("DISJOINT_WORLD_SUPPORT")
    if len(prov)!=len(set(prov)): debt.append("INDEPENDENT_PROVENANCE")
    if len(grammars)>1: debt.append("COMPATIBLE_INTERVENTION_GRAMMAR")
    if len(consequences)>1: debt.append("COMPATIBLE_CONSEQUENCE_SCHEMA")
    if None in correspondences or len(correspondences)>1: debt.append("EXPLICIT_SHARED_CORRESPONDENCE")
    if any(c.get("falsifier_contradiction") for c in certificates): debt.append("NO_FALSIFIER_CONTRADICTION")
    allowed=not debt
    return {
        "allowed":allowed,
        "target":Authority.COMPOSITION_CANDIDATE.value if allowed else Authority.LOCAL_CAUSAL_EXPLANATION.value,
        "promotion_debt":sorted(set(debt)),
        "certificate_count":len(certificates),
        "transport_authorized":False,
        "note":"Composition never grants transportable causal authority by itself.",
    }

def competitor_novelty_adjudication(rows:list[dict[str,Any]])->dict[str,Any]:
    public_contract_matches=[
        r["name"] for r in rows
        if r.get("typed_authority_promotion_contract_public") is True
        and r.get("causal_wording_evidence_gate_public") is True
        and r.get("promotion_debt_public") is True
    ]
    return {
        "frozen_ecology_count":len(rows),
        "public_contract_matches":public_contract_matches,
        "novelty_survives_frozen_public_ecology":len(public_contract_matches)==0,
        "claim_scope":"No equivalent public contract was identified in the frozen competitor evidence; this is not a universal nonexistence claim.",
    }
