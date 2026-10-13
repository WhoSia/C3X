"""I10-P1 development: historic move replay and original-I9 exact-footing adapters."""
import chess
from tools.c3x_explain_i10_p1_historical_cases import CASES,reconstruct_case,original_focused_verified_moment
from c3x_explain.judgment import judge_moment

def test_precommitted_two_distinct_actual_historical_moves_replay():
    assert len(CASES)==2
    for c in CASES:
        board,played,reply,ply=reconstruct_case(c)
        assert board.san(played)==c["played_san"]
        after=board.copy();after.push(played)
        assert after.san(reply)==c["recorded_reply_san"]
        assert ply>=20 and played in board.legal_moves

def test_original_I9_focused_atom_graph_and_firewall_preserve_contrast():
    board,played,reply,ply=reconstruct_case(CASES[1])
    # Test fixture with exact ranking is NOT claimed to have been emitted by SF16.
    rival=next(m for m in board.legal_moves if m!=played)
    m=original_focused_verified_moment(board,played,[
      {"rank":1,"uci":played.uci(),"san":board.san(played),"score_cp":40,
       "depth":12,"score_bound":False,"pv_uci":[played.uci()]},
      {"rank":2,"uci":rival.uci(),"san":board.san(rival),"score_cp":20,
       "depth":12,"score_bound":False,"pv_uci":[rival.uci()]}
    ],ply)
    assert m["firewall"]["pass"] and m["realization_verification"]["pass"]
    j=judge_moment(m)
    assert j["preferred_move"]==played.uci()
    assert j["candidate_gap_cp"]==20
    assert j["local_causal_certificate_ids"]==[]
    assert j["objective_chess_truth"] is None

def test_engine_rank_does_not_rewrite_chess_history():
    board,played,reply,ply=reconstruct_case(CASES[0])
    rival=next(m for m in board.legal_moves if m!=played)
    m=original_focused_verified_moment(board,played,[
      {"rank":1,"uci":rival.uci(),"san":board.san(rival),"score_cp":50,
       "depth":12,"score_bound":False,"pv_uci":[rival.uci()]},
      {"rank":2,"uci":played.uci(),"san":board.san(played),"score_cp":5,
       "depth":12,"score_bound":False,"pv_uci":[played.uci()]}
    ],ply)
    j=judge_moment(m)
    assert j["played_move_role"]=="CHALLENGER"
    assert j["preferred_move"]==rival.uci()
    assert j["played_uci"]==played.uci()
    assert j["calibrated_probability"] is None
