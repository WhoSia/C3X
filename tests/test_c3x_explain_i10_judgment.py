"""Fail-closed I10 typed judgment tests. No external LLM/Jev/Clef calls."""
from c3x_explain.judgment import judge_moment, judgment_packet, judgment_markdown

def fixture():
    return {
        "ply": 7, "played_uci": "e2e4",
        "firewall": {"pass": True},
        "realization_verification": {"pass": True},
        "candidates": [
            {"rank": 1, "uci": "e2e4", "san": "e4", "depth": 8, "score_cp": 45},
            {"rank": 2, "uci": "d2d4", "san": "d4", "depth": 8, "score_cp": 29},
        ],
        "atoms": [{"atom_id": "p7:a0", "type": "candidate_contrast",
                   "provenance": "CONVENTIONAL_HEURISTIC_COMMENTARY",
                   "claim": {"top_uci": "e2e4"}}],
        "typed_graph": {"nodes": []},
    }

def test_i10_engine_snapshot_is_typed_but_not_chess_truth():
    j = judge_moment(fixture())
    assert j["decision"] == "ENGINE_SNAPSHOT_PREFERENCE_ONLY"
    assert j["preferred_move"] == "e2e4" and j["challenger"] == "d2d4"
    assert j["candidate_gap_cp"] == 16 and j["completed_depth"] == 8
    assert j["evidence_atom_ids"] == ["p7:a0"]
    assert j["calibrated_probability"] is None and j["objective_chess_truth"] is None
    assert "not a proof" in j["explanation"]

def test_i10_no_engine_candidate_abstains_not_guess():
    m = fixture(); m["candidates"] = []
    j = judge_moment(m)
    assert j["decision"] == "ABSTAIN"
    assert j["reason"] == "TWO_DISTINCT_ORIGINAL_ENGINE_CANDIDATES_REQUIRED"

def test_i10_blocks_mismatched_depth_or_root():
    m = fixture(); m["candidates"][1]["depth"] = 7
    assert judge_moment(m)["reason"] == "ROOT_IDENTITY_OR_COMPLETED_DEPTH_NOT_COMPARABLE"
    m = fixture(); m["candidates"][1]["uci"] = "e2e4"
    assert judge_moment(m)["decision"] == "ABSTAIN"

def test_i10_bound_only_engine_info_abstains():
    m = fixture(); m["candidates"][0]["score_bound"] = True
    assert judge_moment(m)["reason"] == "BOUND_ONLY_ENGINE_INFO_NOT_EXACT_ROOT_COMPARISON"
    m = fixture(); m["candidates"][1]["score_bound"] = True
    assert judge_moment(m)["decision"] == "ABSTAIN"

def test_i10_blocks_cp_mate_surrogates_and_ties():
    for v in (99999, None, 20.3):
        m = fixture(); m["candidates"][0]["score_cp"] = v
        assert judge_moment(m)["reason"] == "UNKNOWN_MATE_OR_NONINTEGER_CP_VALUE"
    m = fixture(); m["candidates"][0]["score_cp"] = 29
    assert judge_moment(m)["reason"] == "NO_STRICT_COMPARABLE_LEADER"

def test_i10_provenance_and_existing_firewall_gate():
    m = fixture(); m["atoms"] = []
    assert judge_moment(m)["reason"] == "NO_PROVENANCE_LINKED_ENGINE_CONTRAST"
    m = fixture(); m["firewall"]["pass"] = False
    assert judge_moment(m)["reason"] == "LEGACY_LEGALITY_PROVENANCE_FIREWALL_NOT_PASS"
    m = fixture(); m["realization_verification"]["pass"] = False
    assert judge_moment(m)["reason"] == "I7_REALIZATION_VERIFICATION_NOT_PASS"

def test_i10_local_causal_cert_not_auto_promoted():
    m = fixture()
    m["atoms"].append({
        "atom_id": "p7:a1", "type": "causal_contrast",
        "provenance": "C3X_CAUSAL_CONTRAST",
        "claim": {"certificate": {"certificate_id": "real-a", "pair": "e2e4::d2d4"}}
    })
    m["typed_graph"]["nodes"].append({
        "node_type": "causal_certificate", "payload": {"certificate_id": "real-a"}
    })
    j = judge_moment(m)
    assert j["local_causal_certificate_ids"] == ["real-a"]
    assert j["objective_chess_truth"] is None and j["calibrated_probability"] is None
    m["atoms"][-1]["claim"]["certificate"]["pair"] = "a2a3::d2d4"
    assert judge_moment(m)["local_causal_certificate_ids"] == []

def test_i10_both_candidate_pv_lines_are_legally_replayed_not_rival_refutation():
    import chess
    m = fixture(); m["fen"] = chess.Board().fen()
    m["candidates"][0]["pv_uci"] = ["e2e4", "e7e5", "g1f3"]
    m["candidates"][1]["pv_uci"] = ["d2d4", "d7d5", "c2c4"]
    j = judge_moment(m)
    assert j["decision"] == "ENGINE_SNAPSHOT_PREFERENCE_ONLY"
    assert {x["candidate"] for x in j["legally_replayed_candidate_lines"]} == {"e2e4", "d2d4"}
    rival = next(x for x in j["legally_replayed_candidate_lines"] if x["candidate"] == "d2d4")
    assert rival["opponent_first_reply_uci"] == "d7d5"
    assert rival["semantic_scope"] == "CHESS_LEGALITY_REPLAY_ONLY_NOT_FORCED_REFUTATION"
    assert "필연적인 반박은 아닙니다" in j["explanation_ko"]
    m["candidates"][1]["pv_uci"] = ["d2d4", "d2d4"]  # impossible consecutive same-colour pawn push
    j = judge_moment(m)
    assert all(x["candidate"] != "d2d4" for x in j["legally_replayed_candidate_lines"])


def test_i10_unregistered_certificate_fails_causal_link():
    m = fixture()
    m["atoms"].append({
        "atom_id": "p7:a1", "type": "causal_contrast",
        "provenance": "C3X_CAUSAL_CONTRAST",
        "claim": {"certificate": {"certificate_id": "forged", "pair": "e2e4::d2d4"}}
    })
    assert judge_moment(m)["local_causal_certificate_ids"] == []

def test_i10_packet_and_markdown_are_useful_without_training_claim():
    m = fixture()
    pkt = judgment_packet({"schema": "c3x-explanation-graph-v1", "moments": [m]})
    assert pkt["decision_count"] == 1 and pkt["abstention_count"] == 0
    assert "NOT_TRAINED" in pkt["model_kind"]
    text = judgment_markdown(pkt)
    assert "e4" in text and "d4" in text and "Supporting atoms" in text
    assert "C3X" in text

def test_i10_real_legacy_PGN_without_uci_engine_abstains():
    from c3x_explain.core import analyze_pgn
    out = analyze_pgn('[Event "I10 simple"]\n[Result "*"]\n\n1. f3 e5 2. g4 Qh4# *')
    p = judgment_packet(out)
    assert p["decision_count"] == 0
    assert all(j["decision"] == "ABSTAIN" for j in p["judgments"])
