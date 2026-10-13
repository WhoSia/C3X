"""I10-P3 fail-closed compiler and exact-source-bound tiny-interface tests."""
from __future__ import annotations
import copy
import chess
from c3x_explain.evidence_compiler import compile_evidence,compile_graph,render_markdown
from c3x_explain.judgment import judge_moment

def base():
    b=chess.Board()
    return {"ply":1,"played_uci":"e2e4","fen":b.fen(),
       "firewall":{"pass":True},"realization_verification":{"pass":True},
       "candidates":[
           {"rank":1,"uci":"e2e4","san":"e4","depth":12,"score_cp":52,
            "score_bound":False,"pv_uci":["e2e4","e7e5","g1f3"]},
           {"rank":2,"uci":"d2d4","san":"d4","depth":12,"score_cp":21,
            "score_bound":False,"pv_uci":["d2d4","d7d5","c2c4"]}],
       "atoms":[{"atom_id":"p1:contrast","type":"candidate_contrast",
                 "provenance":"CONVENTIONAL_HEURISTIC_COMMENTARY",
                 "claim":{"top_uci":"e2e4"}}],
       "typed_graph":{"nodes":[]}}

def test_compiles_legal_rival_evidence_as_korean_without_causing_truth():
    m=base()
    p=compile_evidence(m)
    assert p["verdict"]=="EMIT_BOUNDED_CONVENTIONAL"
    assert p["leader"]=="e2e4" and p["rival"]=="d2d4"
    assert p["actual_move_role"]=="LEADER"
    assert len(p["claims"])==3 and len(p["selected_claim_ids"])==3
    assert all(c["atom_ids"]==["p1:contrast"] for c in p["claims"])
    assert "31cp" in p["text_ko"] and "필연적인 반박은 아닙니다" in p["text_ko"]
    assert p["model_interface"]["trainable_parameters"]==0
    assert p["confidence_probability"] is None
    assert p["source_causal_claim"] is False

def test_alternative_played_move_preserved_as_challenger():
    m=base();m["played_uci"]="d2d4"
    assert compile_evidence(m)["actual_move_role"]=="CHALLENGER"

def test_no_engine_pair_abstains():
    m=base();m["candidates"]=[]
    assert compile_evidence(m)["verdict"]=="ABSTAIN"

def test_suspect_score_bound_abstains():
    m=base();m["candidates"][0]["score_bound"]=True
    assert compile_evidence(m)["verdict"]=="ABSTAIN"

def test_chess_fen_mismatch_blocks_compilation():
    m=base();m["fen"]=chess.Board().copy(stack=False).fen().replace(" w KQkq"," b KQkq")
    assert compile_evidence(m)["reason"]=="RIVAL_NOT_LEGAL_IN_ORIGINAL_BOARD"

def test_failed_original_renderer_gates_are_sticky():
    m=base();m["firewall"]["pass"]=False
    assert compile_evidence(m)["reason"]=="LEGACY_EVIDENCE_OR_REALIZATION_GATE_FAIL"

def test_external_caller_cannot_inject_fake_or_calibrated_probability():
    m=base()
    fake=judge_moment(m)
    fake["candidate_gap_cp"]=900
    fake["calibrated_probability"]=0.999
    assert compile_evidence(m,fake)["reason"]=="EXTERNAL_JUDGMENT_PACKET_DIVERGES_FROM_I10"

def test_wrong_source_atom_id_abstains():
    m=base()
    bad=judge_moment(m)
    bad["evidence_atom_ids"]=["p1:does_not_exist"]
    assert compile_evidence(m,bad)["verdict"]=="ABSTAIN"

def test_unreviewed_graph_certificate_never_becomes_causal_output():
    m=base()
    m["atoms"].append({
      "atom_id":"p1:fake","type":"causal_contrast",
      "provenance":"C3X_CAUSAL_CONTRAST",
      "claim":{"certificate":{"certificate_id":"fake-local","pair":"e2e4::d2d4"}}
    })
    m["typed_graph"]["nodes"].append({
        "node_type":"causal_certificate","payload":{"certificate_id":"fake-local"}
    })
    j=judge_moment(m)
    assert j["local_causal_certificate_ids"]==["fake-local"]
    compiled=compile_evidence(m)
    assert compiled["withheld_causal_certificate_ids"]==["fake-local"]
    assert compiled["source_causal_claim"] is False
    assert "인과 증명" not in compiled["text_ko"]
    assert all(c["kind"]!="CAUSAL" for c in compiled["claims"])

def test_empty_or_bad_lines_are_not_narrated_as_forced():
    m=base()
    m["candidates"][1]["pv_uci"]=["d2d4","d2d4"]
    p=compile_evidence(m)
    assert p["verdict"]=="EMIT_BOUNDED_CONVENTIONAL"
    assert len(p["claims"])==2
    assert "d7d5" not in p["text_ko"]

def test_compiler_graph_does_not_reclassify_abstention_as_utility():
    m=base()
    p=compile_graph({"schema":"c3x-explanation-graph-v1","moments":[m]})
    assert p["emitted"]==1 and p["abstained"]==0
    assert p["trained_neural_model"] is False
    assert p["independent_human_benefit"] is None
    assert "Ply 1" in render_markdown(p)

def test_zero_causal_guarantee_survives_trust_list_not_declared():
    m=base()
    p=compile_evidence(m)
    assert p["source_engine_identity"]=="NOT_AUTHENTICATED_BY_THIS_LAYER"
    assert p["model_interface"]["features"][-1]==0
    assert set(p["model_interface"]["permitted_actions"])=={"CHOOSE_CLAIM_IDS","ABSTAIN"}
