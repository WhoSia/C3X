"""No competitor 'run' may be claimed from common evidence JSON alone."""
import copy,pytest
from c3x_explain.ecl_rival_equal_evidence import equal_input,freeze_rivals

FEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def source():
    return {"schema":"c3x-ecl-i10-p4-strong-rival-equal-information-contract-v1",
       "source_game_group":"PROXY_DEVELOPMENT_ONLY",
       "original_ply":1,"fen":FEN,"played_uci":"e2e4",
       "original_source_rival":"d2d4",
       "source_rival_rows":[
           {"rank":1,"uci":"e2e4","san":"e4","score_cp":45,"score_bound":False,
            "depth":12,"pv_uci":["e2e4","e7e5","g1f3"]},
           {"rank":2,"uci":"d2d4","san":"d4","score_cp":26,"score_bound":False,
            "depth":12,"pv_uci":["d2d4","d7d5","c2c4"]}],
       "same_compiled_eligible_claims":[]}

def test_every_competitor_gets_exact_same_frozen_source_blob():
    x=equal_input(source())
    assert len(x["arms"])==5
    assert len({a["input_sha256"] for a in x["arms"]})==1
    assert len(x["common_sha256"])==64
    assert x["common_evidence"]["actual_played_san"]=="e4"
    assert all(not a["paper_model_executed"] for a in x["arms"])
    assert not x["full_search_trace_equal_comparison_admissible"]

def test_bad_pv_and_fen_and_uci_are_rejected():
    for mode in ("badfen","wrongpair","badline","baddepth","bound"):
        s=source()
        if mode=="badfen":s["fen"]="8/8/8/8/8/8/8/8 w - - 0 1"
        if mode=="wrongpair":s["source_rival_rows"][1]["uci"]="a7a6"
        if mode=="badline":s["source_rival_rows"][1]["pv_uci"]=["d2d4","d2d4"]
        if mode=="baddepth":s["source_rival_rows"][1]["depth"]=11
        if mode=="bound":s["source_rival_rows"][1]["score_bound"]=True
        with pytest.raises(ValueError):
            equal_input(s)

def test_model_results_are_never_fabricated():
    x=freeze_rivals([source(),source()])
    assert x["scientific_C3X_outperformance_of_original_rivals"] is None
    assert x["original_Queen_run"] is False
    assert x["original_Cui_run"] is False
    assert x["original_CCC_run"] is False
