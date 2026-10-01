import json

import chess

from c3x_g10.loop import (
    QUESTION_ONLY,
    build_roundtrip_packet,
    compress_chess_native_consequence,
    demand_from_candidate_packet,
    g10_p0_preseal,
    historical_contract_witness,
    normalize_local_certificate,
)


P16="c3x/certificates/g95-p16-local-minimal-full-bridge.json"


def _p16():
    return json.load(open(P16,encoding="utf-8"))


def test_preseal_returns_to_origin_without_h_privilege():
    p=g10_p0_preseal()
    assert p["schema"]=="c3x-g10-p0-preseal-v1"
    assert p["h_family_privileged"] is False
    assert p["fresh_intervention_outcomes_opened"] is False
    assert "no transportable causal law" in p["authority_ceiling"]


def test_outcome_blind_demand_admission_is_question_only():
    board=chess.Board()
    candidates=[
        {"rank":1,"uci":"e2e4","san":"e4","score_cp":31,"pv_uci":["e2e4","e7e5"]},
        {"rank":2,"uci":"d2d4","san":"d4","score_cp":22,"pv_uci":["d2d4","d7d5"]},
        {"rank":3,"uci":"g1f3","san":"Nf3","score_cp":18,"pv_uci":["g1f3","d7d5"]},
    ]
    q=demand_from_candidate_packet(
        position_fen=board.fen(),played_uci="e2e4",candidates=candidates,
        source_id="fixture-real-pgn",game_id="g1",ply=1,
    )
    assert q["admitted"] is True
    assert q["authority"]==QUESTION_ONLY
    assert q["candidate_pair"]=="e2e4::d2d4"
    assert q["causal_outcomes_opened"] is False
    assert q["certificate_attached"] is False
    for forbidden in ("certificate_id","decision_cells","falsifiers","structural_signature"):
        assert forbidden not in q
        assert forbidden not in q["features"]


def test_demand_rejects_non_near_equal_or_played_outside_window():
    board=chess.Board()
    candidates=[
        {"rank":1,"uci":"e2e4","san":"e4","score_cp":80,"pv_uci":["e2e4"]},
        {"rank":2,"uci":"d2d4","san":"d4","score_cp":10,"pv_uci":["d2d4"]},
        {"rank":3,"uci":"g1f3","san":"Nf3","score_cp":0,"pv_uci":["g1f3"]},
    ]
    q=demand_from_candidate_packet(
        position_fen=board.fen(),played_uci="e2e4",candidates=candidates,
        source_id="fixture",game_id="g2",ply=1,
    )
    assert q["admitted"] is False
    assert "failed:top2_near_equal" in q["admission_reasons"]


def test_actual_p16_certificate_normalizes_without_promoting_to_law():
    c=_p16()
    n=normalize_local_certificate(c)
    assert n["certificate_id"]=="398eca8d6adf00525e6d5bf7"
    assert n["pair_id"]=="d6d5::e8g8"
    assert n["bound"]=="LOWER"
    assert n["replication_status"]=="LOCAL_ONLY"
    assert n["transportable_law"] is False
    assert n["human_concept_label"] is None


def test_p16_chess_native_compression_replays_legal_consequences():
    x=compress_chess_native_consequence(_p16())
    assert x["verified_legal_objects_only"] is True
    assert x["candidate_pair"]=="d6d5::e8g8"
    assert x["baseline"]["native_bestmove"]=="d6d5"
    assert x["board_preference_transition"]["after"]=="e8g8"
    assert x["board_preference_transition"]["changed"] is True
    assert x["search_mediation_transition"]["event_suppressed"]=="e8g8"
    assert x["search_mediation_transition"]["changed"] is True
    assert x["human_semantic_label"] is None


def test_historical_p16_roundtrip_is_contract_witness_not_fresh_discovery():
    c=_p16()
    q=historical_contract_witness(c)
    assert q["fresh"] is False
    assert q["outcome_blind_eligible"] is False
    assert q["contract_witness_only"] is True
    out=build_roundtrip_packet(q,certificate=c)
    assert out["causal_status"]=="LOCAL_CERTIFICATE_ATTACHED"
    assert out["commentary_route"]["causal_wording_authorized"] is True
    assert out["transportable_law_claim"] is False
    assert out["human_utility_claim"] is False


def test_fresh_demand_without_certificate_stays_heuristic_only():
    board=chess.Board()
    q=demand_from_candidate_packet(
        position_fen=board.fen(),played_uci="e2e4",
        candidates=[
            {"rank":1,"uci":"e2e4","san":"e4","score_cp":25,"pv_uci":["e2e4"]},
            {"rank":2,"uci":"d2d4","san":"d4","score_cp":20,"pv_uci":["d2d4"]},
            {"rank":3,"uci":"g1f3","san":"Nf3","score_cp":18,"pv_uci":["g1f3"]},
        ],
        source_id="real-source",game_id="fresh-g",ply=1,
    )
    out=build_roundtrip_packet(q)
    assert out["causal_status"]=="NO_CERTIFICATE"
    assert out["commentary_route"]["causal_wording_authorized"] is False
    assert out["commentary_route"]["allowed_provenance"]==["CONVENTIONAL_HEURISTIC_COMMENTARY"]


def test_certificate_position_or_pair_mismatch_is_fatal():
    c=_p16()
    try:
        normalize_local_certificate(c,expected_fen=chess.Board().fen())
    except ValueError as e:
        assert "position mismatch" in str(e)
    else:
        raise AssertionError("position mismatch should fail")

    n=normalize_local_certificate(c)
    try:
        normalize_local_certificate(c,expected_fen=n["position_fen"],expected_pair="e2e4::d2d4")
    except ValueError as e:
        assert "pair mismatch" in str(e)
    else:
        raise AssertionError("pair mismatch should fail")
