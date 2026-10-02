from c3x_g10.authority_dynamics import *

def test_evidence_set_confluence_for_semantic_atoms():
    seqs=[
      [{"LOCAL_MINIMALITY_LOST"},{"UNRESOLVED_DIRECT_CONTRADICTION"}],
      [{"UNRESOLVED_DIRECT_CONTRADICTION"},{"LOCAL_MINIMALITY_LOST"}],
    ]
    x=evidence_set_confluent("LOCAL_CAUSAL_EXPLANATION",seqs)
    assert x["confluent"] is True
    assert x["finals"][0][:2]==["SUSPENDED","LOCAL_CAUSAL_EXPLANATION"]

def test_procedural_order_violation_is_irreversible_retraction():
    c=Claim("x","LOCAL_CAUSAL_EXPLANATION")
    apply_evidence(c,{"OBSERVED_OUTCOME"},"bad","OUTCOME_BEFORE_REQUIRED_FREEZE")
    assert c.status==ClaimStatus.RETRACTED
    assert rendered_language_allowed(c)["causal"] is False

def test_demotion_preserves_lower_authority():
    c=Claim("x","LOCAL_CAUSAL_EXPLANATION")
    apply_evidence(c,{"LOCAL_MINIMALITY_LOST"},"e")
    assert c.status==ClaimStatus.DEMOTED
    assert c.authority=="MECHANISM_CANDIDATE"

def test_retraction_is_stronger_than_demotion():
    c=Claim("x","LOCAL_CAUSAL_EXPLANATION")
    apply_evidence(c,{"PROVENANCE_INVALID","LOCAL_MINIMALITY_LOST"},"e")
    assert c.status==ClaimStatus.RETRACTED
    assert c.authority=="MEASUREMENT_ROUTING"

def test_restoration_after_resolved_suspension():
    c=Claim("x","LOCAL_CAUSAL_EXPLANATION")
    apply_evidence(c,{"UNRESOLVED_DIRECT_CONTRADICTION"},"e1")
    resolve_atoms(c,{"UNRESOLVED_DIRECT_CONTRADICTION"},{"CONTRADICTION_RESOLVED"},"e2")
    assert c.status==ClaimStatus.RESTORED
    assert rendered_language_allowed(c)["causal"] is True

def test_context_split_branches_without_retraction():
    a={"certificate_id":"a","correspondence_id":"r","context_signature":"opening","mechanism_signature":"m","consequence_schema":"root","provenance_id":"p1","world_id":"w1"}
    b={"certificate_id":"b","correspondence_id":"r","context_signature":"endgame","mechanism_signature":"m","consequence_schema":"root","provenance_id":"p2","world_id":"w2"}
    assert classify_certificate_conflict(a,b)["class"]=="CONTEXT_SPLIT"

def test_same_context_different_mechanism_is_conflict():
    a={"certificate_id":"a","correspondence_id":"r","context_signature":"x","mechanism_signature":"m1","consequence_schema":"root","provenance_id":"p1","world_id":"w1"}
    b={"certificate_id":"b","correspondence_id":"r","context_signature":"x","mechanism_signature":"m2","consequence_schema":"root","provenance_id":"p2","world_id":"w2"}
    assert classify_certificate_conflict(a,b)["class"]=="MECHANISM_CONFLICT"

def test_dependency_retraction_withdraws_downstream_causal_wording():
    cert=Claim("cert","LOCAL_CAUSAL_EXPLANATION")
    atom=Claim("atom","LOCAL_CAUSAL_EXPLANATION",dependencies={"cert"})
    comp=Claim("comp","COMPOSITION_CANDIDATE",dependencies={"cert"})
    claims={"cert":cert,"atom":atom,"comp":comp}
    apply_evidence(cert,{"PROVENANCE_INVALID"},"e")
    out=propagate_revision(claims)
    assert out["claims"]["atom"]["status"]=="SUSPENDED"
    assert rendered_language_allowed(atom)["causal"] is False
    assert out["claims"]["comp"]["status"]=="SUSPENDED"
