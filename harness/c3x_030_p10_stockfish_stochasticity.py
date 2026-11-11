#!/usr/bin/env python3
"""C3X P10: Real Stockfish16 stochasticity vs resource-dependent instability.

Four mutually labeled regimes: full strength fresh one thread, full strength
same-session warm hash one thread, full strength fresh four threads,
intentional handicap (Skill Level 0). This experiment is descriptive:
it never claims variance implies a true RNG outside the documented handicap.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics

import chess
import chess.engine

SCHEMA = "c3x030-p10-stockfish-repetition-factorial-v1"
STOCKFISH16_COMMIT = "68e1e9b3811e16cad014b590d7443b9063b3eb52"
POSITIONS = {
    "opening": ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6"],
    "middlegame": ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "c1g5", "f8e7",
                   "e2e3", "e8g8", "g1f3", "b8d7"],
}
ARM_SPECS = (
    ("full_fresh_1thread", 1, 20, False),
    ("full_warm_1thread", 1, 20, True),
    ("full_fresh_4threads", 4, 20, False),
    ("handicap_fresh_1thread", 1, 0, False),
)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def board_for(moves):
    board = chess.Board()
    for u in moves:
        move = chess.Move.from_uci(u)
        if move not in board.legal_moves:
            raise ValueError("P10_HOLD_INVALID_PIECE_HISTORY")
        board.push(move)
    if not board.is_valid() or board.is_game_over():
        raise ValueError("P10_HOLD_TERMINAL_POSITION")
    return board

def execute_trial(engine, board, nodes, game):
    response = engine.play(board, chess.engine.Limit(nodes=nodes),
                           info=chess.engine.INFO_ALL, game=game)
    if response.move is None or response.move not in board.legal_moves:
        raise ValueError("P10_HOLD_ILLEGAL_ENGINE_MOVE")
    info = response.info
    actual_nodes = info.get("nodes")
    depth = info.get("depth")
    if type(actual_nodes) is not int or actual_nodes <= 0:
        raise ValueError("P10_HOLD_MISSING_NATIVE_NODE_COUNT")
    if type(depth) is not int or depth <= 0:
        raise ValueError("P10_HOLD_MISSING_SEARCH_DEPTH")
    score = info.get("score")
    cp = score.pov(board.turn).score() if score else None
    pv = [x.uci() for x in info.get("pv", [])]
    return {"bestmove_uci": response.move.uci(), "actual_nodes": actual_nodes,
            "completed_depth": depth, "score_cp_or_null": cp,
            "pv_uci": pv[:12],
            "reported_pv_first_move_matches_bestmove": bool(pv and pv[0] == response.move)}

def summarize(trials):
    if not trials:
        raise ValueError("P10_HOLD_NO_TRIALS")
    counts = Counter(t["bestmove_uci"] for t in trials)
    return {"trials": len(trials), "distinct_best_moves": len(counts),
            "best_move_counts": dict(sorted(counts.items())),
            "best_move_changed_across_trials": len(counts)>1,
            "actual_native_nodes": sum(t["actual_nodes"] for t in trials),
            "minimum_depth": min(t["completed_depth"] for t in trials),
            "maximum_depth": max(t["completed_depth"] for t in trials)}

def run(binary, repeats, nodes):
    if repeats < 3 or nodes < 1000:
        raise ValueError("P10_HOLD_MINIMUM_EXPERIMENT")
    output = {"schema": SCHEMA, "pinned_stockfish_source_sha": STOCKFISH16_COMMIT,
              "binary_sha256": sha(binary), "requested_nodes_each_trial": nodes,
              "repeats_per_position_arm": repeats, "positions": {},
              "all_engine_work_executed_here": True,
              "engine_family": "Stockfish 16 classical (NNUE disabled)",
              "randomized_handicap_mode_explicitly_tested": True,
              "physical_randomness_outside_handicap_proven": False,
              "hypothesis": "Separate deliberate skill handicap stochasticity from search-state resource sensitivity."}
    for key, history in POSITIONS.items():
        board = board_for(history)
        experiments = {}
        for arm, threads, skill, warm in ARM_SPECS:
            trial_rows = []
            if warm:
                with chess.engine.SimpleEngine.popen_uci(binary,timeout=120) as eng:
                    eng.configure({"Threads":threads, "Hash":16, "Use NNUE":False,
                                   "Skill Level":skill,
                                   "UCI_LimitStrength":False})
                    session = object()
                    for _ in range(repeats):
                        trial_rows.append(execute_trial(eng,board,nodes,session))
            else:
                for _ in range(repeats):
                    with chess.engine.SimpleEngine.popen_uci(binary, timeout=120) as eng:
                        eng.configure({"Threads":threads, "Hash":16, "Use NNUE":False,
                                       "Skill Level":skill,
                                       "UCI_LimitStrength":False})
                        trial_rows.append(execute_trial(eng,board,nodes,object()))
            experiments[arm] = {"threads": threads, "skill_level": skill, 
                                "uci_limit_strength":False,
                                "fresh_process_each_trial":not warm,
                                "same_game_object_warm_search":warm,
                                "trials":trial_rows, "summary":summarize(trial_rows)}
        output["positions"][key] = {"fen":board.fen(en_passant="fen"),
                                     "history_uci":history,"arms":experiments}
    output["total_native_searches"] = len(POSITIONS) * len(ARM_SPECS) * repeats
    output["total_actual_native_nodes"] = sum(
        x["summary"]["actual_native_nodes"]
        for p in output["positions"].values() for x in p["arms"].values())
    output["causality_caution"] = ("Thread scheduling, hash state, weak-skill PRNG and "
        "node-budget stopping are partly confounded by arm; observational arm "
        "contrast, not a unique causal decomposition.")
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stockfish",required=True)
    parser.add_argument("--repeats",type=int,default=6)
    parser.add_argument("--nodes",type=int,default=15000)
    parser.add_argument("--out",required=True)
    a=parser.parse_args()
    d=run(a.stockfish,a.repeats,a.nodes)
    target=Path(a.out); target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    print("C3X_P10_NATIVE_REPETITIONS",d["total_native_searches"],
          "ACTUAL_NODES",d["total_actual_native_nodes"],"SHA256",sha(target))
    for p in d["positions"]:
        for arm in d["positions"][p]["arms"]:
            x=d["positions"][p]["arms"][arm]["summary"]
            print("P10_RESULT",p,arm,json.dumps(x,sort_keys=True))

if __name__=="__main__":
    main()
