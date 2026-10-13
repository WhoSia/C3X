"""I10-P3 explicit original-PGN focus, no posthoc rival substitution."""
import pytest
from c3x_explain.ecl_focus import position_before_ply
from tools.c3x_explain_i10_p1_historical_cases import CASES,reconstruct_case

def test_kasparov_historical_24_Rxd4_exact_ply():
    c=CASES[0]; b,p=position_before_ply(c["pgn"],47)
    assert b.san(p)=="Rxd4"
    ref,m,reply,n=reconstruct_case(c)
    assert n==47 and b.fen()==ref.fen()
    assert p==m

def test_morphy_12_long_castle_exact_ply():
    c=CASES[1]; b,p=position_before_ply(c["pgn"],23)
    assert b.san(p)=="O-O-O"
    assert c["recorded_reply_san"]=="Rd8"
    assert len(list(b.legal_moves))>=2

def test_illegal_or_absent_ply_refused():
    c=CASES[0]
    for n in (0,48,-3,999):
        with pytest.raises(ValueError,match="PLY_NOT_IN_PGN"):
            position_before_ply(c["pgn"],n)

def test_bad_pgn_refused():
    with pytest.raises(ValueError,match="INVALID_OR_UNREPLAYABLE_PGN"):
        position_before_ply("",1)

def test_focused_source_not_public_causal_cert():
    from c3x_explain.evidence_compiler import compile_evidence
    from tools.c3x_explain_i10_p1_historical_cases import original_focused_verified_moment
    c=CASES[1]; b,p,reply,n=reconstruct_case(c)
    alt=next(x for x in b.legal_moves if x!=p)
    rows=[{"rank":1,"uci":p.uci(),"san":b.san(p),"score_cp":100,"depth":12,
           "pv_uci":[p.uci()]},{"rank":2,"uci":alt.uci(),"san":b.san(alt),
           "score_cp":50,"depth":12,"pv_uci":[alt.uci()]}]
    m=original_focused_verified_moment(b,p,rows,n)
    packet=compile_evidence(m)
    assert packet["verdict"]=="EMIT_BOUNDED_CONVENTIONAL"
    assert packet["source_causal_claim"] is False
    assert packet["model_interface"]["trainable_parameters"]==0
