"""Authentic P16 original evidence vs public release trust; **no Ethereal source rerun**."""
from __future__ import annotations
from copy import deepcopy
import json
import pytest
from tools.c3x_explain_i10_p2_p16_original_certificate_boundary import (
    P16,TRUST,produce,audit_original,EXPECTED_PAIR,CERT_ID
)

def inputs():
    blob=P16.read_bytes()
    return json.loads(blob),json.loads(TRUST.read_text()),blob

def test_readonly_p16_sourced_certificate_binds_exact_git_bytes():
    x=produce()
    assert x["original_legacy_certificate_id"]==CERT_ID
    assert x["original_engine"]=="Ethereal"
    assert x["source_reproduction_this_run"]=="NOT_REEXECUTED"
    assert x["user_facing_I9_I10_trust_status"]=="NOT_PUBLICLY_ADMITTED"
    assert x["human_utility_score"] is None
    assert x["new_C3X_P2_independent_scientific_contribution"] is False

def test_original_d5_castling_legal_rival_on_actual_b0_chess_board():
    x=produce()
    assert {z["uci"] for z in x["root_pair"]}==set(EXPECTED_PAIR)
    assert {z["san"] for z in x["root_pair"]}=={"d5","O-O"}
    assert all(z["legal"] for z in x["root_pair"])

def test_source_event_discriminates_worlds_that_same_native_move_does_not():
    c=produce()["actual_original_certificate_observation"]
    assert c["B0"]["native_bestmove"]=="d6d5"
    assert c["TARGET"]["native_bestmove"]==c["SUBSET"]["native_bestmove"]=="e8g8"
    assert c["TARGET"]["source_lower_event_state"]=="EVENT_NULL"
    assert c["SUBSET"]["source_lower_event_state"]=="EVENT_PAIR_REVERSAL"
    assert c["SUBSET"]["source_lower_event_state"]==c["SHAM"]["source_lower_event_state"]

def test_original_certificate_pair_falsification_fails_closed():
    c,t,b=inputs()
    c["pair"]["pair_id"]="e8g8::d6d5"
    with pytest.raises(ValueError,match="RIVAL_PAIR"):
        audit_original(c,t,original_blob=b)

def test_wrong_engine_can_never_be_mistaken_for_stockfish16():
    c,t,b=inputs()
    c["engine"]="stockfish"
    with pytest.raises(ValueError,match="ENGINE_OR_CERTIFICATE"):
        audit_original(c,t,original_blob=b)

def test_wrong_chess_world_fails_closed():
    c,t,b=inputs()
    c["counterfactual_boards"]["B0"]["fen"]="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    with pytest.raises(ValueError,match="CHESS_WORLD"):
        audit_original(c,t,original_blob=b)

def test_fake_admission_fails_closed_without_changing_public_manifest():
    c,t,b=inputs()
    t["approved"]=[{"certificate_id":CERT_ID}]
    with pytest.raises(ValueError,match="TRUST_POLICY"):
        audit_original(c,t,original_blob=b)

def test_historical_blob_identity_cannot_be_silently_swapped():
    c,t,b=inputs()
    with pytest.raises(ValueError,match="BYTE_IDENTITY"):
        audit_original(c,t,original_blob=b+b" " )

def test_event_falsifier_discovers_mislabeled_sham_event():
    c,t,b=inputs()
    c["decision_cells"]["SHAM"]["bounds"]["LOWER"]["state"]="EVENT_NULL"
    with pytest.raises(ValueError,match="ENGINE_EVENT_RESPONSE"):
        audit_original(c,t,original_blob=b)

def test_original_authentication_is_not_scientific_certification():
    x=produce()
    assert x["stockfish_source_causal_authority"]=="NONE"
    assert x["chess_concept_semantic_validation"]=="NOT_PERFORMED_CONCEPT_LABEL_NULL"
    assert x["generic_public_Stockfish_commentator_would_be_unauthorized"] is True
    assert x["human_utility_score"] is None
