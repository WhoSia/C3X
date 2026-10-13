"""Two PRE-EXPOSED historical games, original SF16 ECL claims and tiny-head resource counters.
Not a held-out benchmark or trained decision model. Preserves I10-P1 cases and source.
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
import chess
import chess.engine
from c3x_explain.evidence_compiler import compile_evidence
from tools.c3x_explain_i10_p1_historical_cases import (
    CASES,reconstruct_case,_analysis,original_focused_verified_moment
)

def run_one(engine_path:str,case:dict)->dict:
    board,played,reply,ply=reconstruct_case(case)
    engine=chess.engine.SimpleEngine.popen_uci(engine_path)
    try:
        engine.configure({"Threads":1,"Hash":16,"Use NNUE":False})
        scout=_analysis(engine,board,depth=9,multipv=3)
    finally:
        engine.quit()
    rivals=[x for x in scout if x["uci"]!=played.uci()]
    if not rivals:raise ValueError("NO_VALID_SCOUT_RIVAL")
    rival=chess.Move.from_uci(rivals[0]["uci"])
    if rival not in board.legal_moves:raise ValueError("NONLEGAL_SCOUT")
    engine=chess.engine.SimpleEngine.popen_uci(engine_path)
    try:
        engine.configure({"Threads":1,"Hash":16,"Use NNUE":False})
        start=time.perf_counter_ns()
        pair=_analysis(engine,board,depth=12,multipv=2,root_moves=[played,rival])
        engine_ns=time.perf_counter_ns()-start
    finally:
        engine.quit()
    if {x["uci"] for x in pair}!={played.uci(),rival.uci()}:
        raise ValueError("NOT_THE_PREDECLARED_SOURCE_SELECTED_PAIR")
    moment=original_focused_verified_moment(board,played,pair,ply)
    if not moment["firewall"]["pass"] or not moment["realization_verification"]["pass"]:
        raise ValueError("LEGACY_EXPLANATION_FIREWALL_HOLD")
    start=time.perf_counter_ns()
    compiled=compile_evidence(moment)
    compile_ns=time.perf_counter_ns()-start
    if compiled["verdict"]!="EMIT_BOUNDED_CONVENTIONAL":
        raise ValueError("ORIGINAL_SOURCE_ECL_PILOT_DID_NOT_EMIT:"+compiled["reason"])
    assert not compiled["source_causal_claim"]
    assert compiled["confidence_probability"] is None
    return {
        "case":case["id"],"development_only":True,"fen":board.fen(),
        "actual_played_san":case["played_san"],"original_recorded_opponent_reply_san":case["recorded_reply_san"],
        "original_engine":"official Stockfish sf_16 68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "source_scout_depth":9,"source_pair_depth":12,
        "original_candidate_pair":[{"uci":x["uci"],"san":x["san"],"cp":x["score_cp"],"depth":x["depth"],
                                    "nodes":x["nodes"],"pv_uci":x["pv_uci"]} for x in pair],
        "measured_uci_analyse_wall_ns_single_run":engine_ns,
        "measured_claim_compiler_wall_ns_single_run":compile_ns,
        "compiler_packet":compiled,
        "strong_Queen_Cui_CCC_executed":False,
        "new_original_source_causal_certificate":False,
        "independent_human_effect":None,
    }

def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--engine",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    rows=[run_one(args.engine,c) for c in CASES]
    result={
        "schema":"c3x-ecl-i10-p3-original-SF16-exposed-real-chess-pilot-v1",
        "status":"SOURCE_NATIVE_ENGINEERING_PILOT_ONLY",
        "source_cases":"I10_P1_ALREADY_EXPOSED_NOT_HELDOUT",
        "model_training":"NONE",
        "trained_parameter_count":0,
        "input_legacy_evidence":"I9_VERIFIED_ATOMS_I10_PROVENANCE",
        "native_cases":rows,
        "claimed_chess_Elo_gain":None,
        "claimed_speed_advantage_over_Queen_CCC_Cui":None,
        "claimed_explanation_superiority":None,
        "original_Ethereal_P16_certificate_admitted":False,
    }
    path=Path(args.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for row in rows:
        p=row["compiler_packet"]
        print("I10_P3_SOURCE_NATIVE_ECL",row["case"],p["verdict"],
              p["leader"],p["rival"],len(p["claims"]),
              "engine_ns",row["measured_uci_analyse_wall_ns_single_run"],
              "compiler_ns",row["measured_claim_compiler_wall_ns_single_run"])

if __name__=="__main__":
    main()
