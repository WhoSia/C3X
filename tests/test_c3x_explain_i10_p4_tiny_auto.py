"""P4 source authority, game group split, real training, prior-auto abstention retention."""
import copy
import pytest
import chess
from c3x_explain.ecl_tiny_selector import train,select,benchmark,weak_proxy_examples
from c3x_explain.ecl_auto import preselect
from c3x_explain.evidence_compiler import compile_evidence
from tools.c3x_explain_i10_p1_historical_cases import CASES
from c3x_explain.ecl_test_fixture import base

def p():
    return compile_evidence(base())

def test_trained_actual_linear_not_static_zero_model():
    pkt=p()
    samples=weak_proxy_examples([pkt],"TRAIN_GAME_A")
    assert len(samples)==3
    m=train(samples,epochs=80)
    assert m["trained_parameter_count"]==9
    assert m["training_example_count"]==3
    assert any(abs(w)>0.1 for w in m["weights"])
    for q in ("ENGINE_PREFERENCE","PLAYED_CONTINUATION","ALTERNATIVE_CONTINUATION"):
        assert select(pkt,q,model=m)["weak_proxy_question_match"] is True
    assert select(pkt,"ENGINE_PREFERENCE")["weak_proxy_question_match"] is False

def test_chess_game_group_leakage_prohibited():
    m=train(weak_proxy_examples([p()],"TRAIN_GAME_A"))
    with pytest.raises(ValueError,match="TRAIN_TEST_GAME_GROUP_LEAKAGE"):
        benchmark([p()],m,"TRAIN_GAME_A")
    b=benchmark([p()],m,"OTHER_GAME_B")
    assert b["proxy_comparison"]["P4_TRAINED_9_PARAMETER_PROXY_SELECTOR"]["proxy_correct"]==3
    assert b["actual_Queen_Cui_CCC_called"] is False

def test_tampered_model_hash_or_nan_rejected():
    m=train(weak_proxy_examples([p()],"A"))
    bad=copy.deepcopy(m);bad["weights"][0]+=10
    with pytest.raises(ValueError,match="SHA256"):
        select(p(),"ENGINE_PREFERENCE",model=bad)
    bad=copy.deepcopy(m);bad["weights"][0]=float("nan")
    with pytest.raises(ValueError,match="INVALID"):
        select(p(),"ENGINE_PREFERENCE",model=bad)

def test_selector_refuses_causal_certificate_shaped_packet():
    packet=p()
    packet["source_causal_claim"]=True
    m=train(weak_proxy_examples([p()],"A"))
    assert select(packet,"ENGINE_PREFERENCE",model=m)["decision"]=="ABSTAIN"

def test_selector_does_not_mutate_original_claim_or_invent_text():
    packet=p(); original=copy.deepcopy(packet)
    m=train(weak_proxy_examples([packet],"A"))
    for q in ("ENGINE_PREFERENCE","PLAYED_CONTINUATION","ALTERNATIVE_CONTINUATION"):
        z=select(packet,q,model=m)
        assert z["text_ko"] in [c["text_ko"] for c in original["claims"]]
        assert set(z["selected_claim_ids"]).issubset({c["claim_id"] for c in original["claims"]})
        assert z["confidence_probability"] is None
        assert not z["source_causal_claim"]
    assert packet==original

def test_preoutcome_selection_is_stable_and_does_not_depend_on_search():
    x=preselect(CASES[0]["pgn"],max_moments=4,min_ply=10)
    y=preselect(CASES[0]["pgn"],max_moments=4,min_ply=10)
    assert x==y
    assert x["eligible_count"]>4
    assert x["chosen_for_source_analysis_count"]==4
    assert x["not_attempted_eligible_count"]==x["eligible_count"]-4
    assert all(r["ply"]>=10 for r in x["selected"])
    assert all(r["salience_basis"]=="BOARD_AND_PLAYED_MOVE_BEFORE_ENGINE_ONLY" for r in x["selected"])

def test_auto_preselector_never_promotes_forced_or_unrelated_move():
    x=preselect('[Event "Fool"]\n\n1. f3 e5 2. g4 Qh4# *',min_ply=1,max_moments=4)
    assert x["original_total_plies"]==4
    assert x["eligible_count"]==4

def test_preselect_no_game_and_invalid_limit_fail():
    with pytest.raises(ValueError):preselect("",min_ply=1)
    with pytest.raises(ValueError):preselect(CASES[0]["pgn"],max_moments=0)

def test_question_mismatch_is_explicitly_a_proxy_not_human_quality():
    packet=p()
    m=train(weak_proxy_examples([packet],"A"))
    z=select(packet,"ENGINE_PREFERENCE",model=m)
    assert z["human_outcome"] is None
    assert z["scope"]=="ONE_VERIFIED_CONVENTIONAL_SOURCE_CLAIM_ONLY"
    assert "score" in z["selected_claim_ids"][0]

def test_no_unsupported_target_for_training_when_pv_bad():
    moment=base()
    moment["candidates"][1]["pv_uci"]=["d2d4","d2d4"]
    pkt=compile_evidence(moment)
    rows=weak_proxy_examples([pkt],"A")
    assert len(rows)==2
    model=train(rows)
    assert select(pkt,"ALTERNATIVE_CONTINUATION",model=model)["decision"]=="EMIT_BOUNDED_CONVENTIONAL"
    assert select(pkt,"ALTERNATIVE_CONTINUATION",model=model)["weak_proxy_question_match"] is False
