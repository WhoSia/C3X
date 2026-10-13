"""Native original C3X P5 intervention semantic scope negative tests."""
import copy
import pytest
import chess
from c3x_explain.ecl_p5_source_semantics import audit,board_proxies,replay

START=chess.Board().fen()
def world(pv1,pv2):
    return {
      "game_id":"PRETEST","ply":1,"played_san":"e4","fen":START,
      "source_world_cells":{
         "O":{"uci":{"pv":pv1,"bestmove":"e2e4"},
              "physical_source":{"source_reorder":0}},
         "F":{"uci":{"pv":pv2,"bestmove":"e2e4"},
              "physical_source":{"source_reorder":1}},
         "Z":{"uci":{"pv":pv1,"bestmove":"e2e4"},
              "physical_source":{"source_reorder":0}},
      }
    }

def packet(w):
    return {"schema":"c3x-i10-p5-new-Olympiad-original-SF16-eight-game-source-order-O-F-Z-native-v1",
            "worlds":[dict(copy.deepcopy(w),game_id=str(i)) for i in range(8)]}

def test_equal_root_and_reply_but_different_later_legal_source_PV():
    a=["e2e4","e7e5","g1f3","b8c6"]
    b=["e2e4","e7e5","f1c4","b8c6"]
    p=audit(packet(world(a,b)))
    assert p["later_hypothetical_PV_changed"]==8
    assert p["bestmove_unchanged"]==8
    assert p["first_opponent_reply_unchanged"]==8
    assert p["new_public_C3X_certificate"] is None
    assert not p["independent_new_engine_source_causal_chess_semantics"]
    assert all(x["source_PV_common_prefix_halfmoves"]==2 for x in p["samples"])
    assert all(not x["human_semantic_chess_concept_caused"] for x in p["samples"])

def test_identical_lines_source_event_was_real_not_strategy_effect():
    x=["e2e4","e7e5","g1f3"]
    r=audit(packet(world(x,x)))
    assert r["later_hypothetical_PV_changed"]==0
    assert "동일" in r["samples"][0]["human_readable_korean_bounded_report"]

def test_forged_sham_or_no_contact_source_cannot_pass():
    x=["e2e4","e7e5"]
    y=["e2e4","c7c5"]
    w=world(x,x)
    w["source_world_cells"]["Z"]["uci"]["pv"]=y
    with pytest.raises(ValueError,match="SHAM"):
        audit(packet(w))
    w=world(x,x);w["source_world_cells"]["F"]["physical_source"]["source_reorder"]=0
    with pytest.raises(ValueError,match="NO_CONTACT"):
        audit(packet(w))

def test_illegal_pv_replay_will_not_be_textualized():
    with pytest.raises(ValueError,match="ILLEGAL"):
        replay(START,["e2e4","e2e4"])

def test_different_source_intervention_must_not_be_falsely_named_concept_cause():
    a=["e2e4","e7e5","g1f3"]
    b=["e2e4","e7e5","f1c4"]
    r=audit(packet(world(a,b)))
    for k in ["strategic_concept_caused_actual_bestmove",
              "verified_high_level_source_concept_alignment"]:
        assert k in r["not_admissible_claims"]
    assert r["source_intervention_supported_claim"]=="EXACT_ORIGINAL_ENGINE_ROOT_ORDER_CAUSED_LOCAL_PV_TEXT_DIFFERENCE_WHERE_OBSERVED"
