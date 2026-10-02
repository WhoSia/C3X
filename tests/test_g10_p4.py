from c3x_g10.promotion_calculus import *

P16={
 "LEGAL_POSITION","LEGAL_CANDIDATE_OBJECT","OBSERVED_CANDIDATE_FATE","PROVENANCE_BOUND",
 "DECLARED_INTERVENTION","MATCHED_BASELINE","OBSERVED_INTERVENTION_RESPONSE","REGIME_IDENTITY",
 "EXACT_INTERVENTION_ADDRESS","LEGAL_CHESS_CONSEQUENCE","SUBSET_FALSIFIER_FAILED",
 "SHAM_FALSIFIER_FAILED","CHAIN_RELATIVE_MINIMALITY","LOCAL_SCOPE_DECLARED"
}

def test_root_change_does_not_get_causal_authority():
    x=evaluate_promotion(Authority.CHESS_NATIVE_SURFACE,"SURFACE_TO_MECHANISM",{"OBSERVED_CANDIDATE_FATE","PROVENANCE_BOUND"})
    assert x["allowed"] is False
    assert "DECLARED_INTERVENTION" in x["promotion_debt"]
    assert guard_claim(Authority.CHESS_NATIVE_SURFACE,"causal")["allowed"] is False

def test_intervention_response_without_falsifiers_stops_at_mechanism_candidate():
    e={"DECLARED_INTERVENTION","MATCHED_BASELINE","OBSERVED_INTERVENTION_RESPONSE","REGIME_IDENTITY","PROVENANCE_BOUND"}
    x=evaluate_promotion(Authority.CHESS_NATIVE_SURFACE,"SURFACE_TO_MECHANISM",e)
    assert x["allowed"] is True
    y=evaluate_promotion(Authority.MECHANISM_CANDIDATE,"MECHANISM_TO_LOCAL_CAUSAL",e)
    assert y["allowed"] is False
    assert "SUBSET_FALSIFIER_FAILED" in y["missing"]

def test_p16_shape_can_reach_local_but_not_transport():
    m=evaluate_promotion(Authority.CHESS_NATIVE_SURFACE,"SURFACE_TO_MECHANISM",P16)
    assert m["allowed"] is True
    c=evaluate_promotion(Authority.MECHANISM_CANDIDATE,"MECHANISM_TO_LOCAL_CAUSAL",P16)
    assert c["allowed"] is True
    assert guard_claim(Authority.LOCAL_CAUSAL_EXPLANATION,"local_causal_contrast")["allowed"] is True
    assert guard_claim(Authority.LOCAL_CAUSAL_EXPLANATION,"transported_causal_pattern")["allowed"] is False

def test_falsifier_contradiction_blocks_local_promotion():
    e=set(P16)|{"FALSIFIER_CONTRADICTION"}
    x=evaluate_promotion(Authority.MECHANISM_CANDIDATE,"MECHANISM_TO_LOCAL_CAUSAL",e)
    assert x["allowed"] is False
    assert "FALSIFIER_CONTRADICTION" in x["blockers"]

def cert(i,prov=None):
    return {"authority":"LOCAL_CAUSAL_EXPLANATION","scope":"LOCAL_ONLY","world_id":f"w{i}","provenance_id":prov or f"p{i}","intervention_grammar":"TT_EVENT_SUPPRESSION","consequence_schema":"ROOT_CHOICE_TRANSITION","correspondence_id":"corr-v1","falsifier_contradiction":False}

def test_composition_requires_independence_and_never_grants_transport():
    x=compose_local_certificates([cert(1),cert(2)])
    assert x["allowed"] is True and x["target"]=="COMPOSITION_CANDIDATE"
    assert x["transport_authorized"] is False
    y=compose_local_certificates([cert(1,"same"),cert(2,"same")])
    assert y["allowed"] is False
    assert "INDEPENDENT_PROVENANCE" in y["promotion_debt"]

def test_transport_requires_prospective_heldout_obligations():
    x=evaluate_promotion(Authority.COMPOSITION_CANDIDATE,"COMPOSITION_TO_TRANSPORT",{"PROVENANCE_BOUND"})
    assert x["allowed"] is False
    assert "PROSPECTIVE_HELDOUT_REPLICATION" in x["promotion_debt"]

def test_competitor_novelty_is_bounded_not_universal():
    rows=[{"name":"A","typed_authority_promotion_contract_public":False,"causal_wording_evidence_gate_public":False,"promotion_debt_public":False}]
    x=competitor_novelty_adjudication(rows)
    assert x["novelty_survives_frozen_public_ecology"] is True
    assert "not a universal" in x["claim_scope"]
