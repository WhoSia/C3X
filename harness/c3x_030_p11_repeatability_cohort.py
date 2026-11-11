#!/usr/bin/env python3
"""C3X 0.30/P11 — predeclared 20-position Stockfish16 full-strength repeatability.

Three comparative arms at the SAME REQUESTED node limit:
(1) fresh 1-thread, (2) warm reused 1-thread, (3) fresh 4-thread.
No weak-skill RNG, no randomized policy sampling, no cherry-picked positions.
Descriptive clustered estimates, not proof of causal mediation.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import chess
import chess.engine

SOURCE_COMMIT = "68e1e9b3811e16cad014b590d7443b9063b3eb52"
SCHEMA = "c3x030-p11-precommitted-20-position-full-strength-repetition-v1"
OPENING_HISTORIES = {
    "ruy_lopez": ("e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 f1a4 g8f6 e1g1 f8e7 f1e1 b7b5").split(),
    "queens_gambit": ("d2d4 d7d5 c2c4 e7e6 b1c3 g8f6 c1g5 f8e7 e2e3 e8g8 g1f3 b8d7").split(),
    "sicilian_najdorf": ("e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 a7a6 c1e3 e7e6").split(),
    "english": ("c2c4 e7e5 b1c3 g8f6 g2g3 d7d5 c4d5 f6d5 f1g2 d5b6 g1f3 b8c6").split(),
}
CHECKPOINTS = (4, 6, 8, 10, 12)
ARMS = (
    ("cold_single", 1, False),
    ("warm_single", 1, True),
    ("cold_parallel4", 4, False),
)

def hexdigest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def positions():
    result = {}
    seen = set()
    for opening, seq in OPENING_HISTORIES.items():
        board = chess.Board()
        for ply, u in enumerate(seq, start=1):
            move = chess.Move.from_uci(u)
            if move not in board.legal_moves:
                raise ValueError(f"P11_HOLD_ILLEGAL_PREDECLARED_HISTORY:{opening}:{ply}:{u}")
            board.push(move)
            if ply not in CHECKPOINTS:
                continue
            if not board.is_valid() or board.is_game_over(claim_draw=False):
                raise ValueError("P11_HOLD_INVALID_CHECKPOINT")
            fen = board.fen(en_passant="fen")
            if fen in seen:
                raise ValueError("P11_HOLD_DUPLICATE_CHESS_POSITION")
            seen.add(fen)
            result[f"{opening}_ply{ply}"] = {"fen":fen, "history_uci":seq[:ply]}
    if len(result) != 20:
        raise ValueError("P11_HOLD_PREDECLARED_COHORT_NOT_20")
    return result

def draw(engine, board, budget, game):
    response = engine.play(board, chess.engine.Limit(nodes=budget),
                           game=game, info=chess.engine.INFO_ALL)
    if not response.move or response.move not in board.legal_moves:
        raise ValueError("P11_HOLD_INVALID_ENGINE_MOVE")
    info = response.info
    nodes, depth = info.get("nodes"), info.get("depth")
    if type(nodes) is not int or nodes <= 0 or type(depth) is not int or depth < 1:
        raise ValueError("P11_HOLD_MISSING_NATIVE_SEARCH_PROVENANCE")
    score = info.get("score")
    pv = [x.uci() for x in info.get("pv", [])[:12]]
    return {"move_uci":response.move.uci(), "nodes_actual":nodes, "depth":depth,
            "score_cp_or_null":score.pov(board.turn).score() if score else None,
            "pv_first_uci_or_null":pv[0] if pv else None}

def arm_summary(trials):
    if not trials:
        raise ValueError("P11_HOLD_EMPTY_ARM")
    counts = Counter(row["move_uci"] for row in trials)
    ps = [n/len(trials) for n in counts.values()]
    return {"count":len(trials), "distinct_moves":len(counts),
            "counts":dict(sorted(counts.items())),
            "switch_observed":len(counts)>1,
            "empirical_move_entropy_bits": -sum(p*math.log2(p) for p in ps),
            "actual_nodes_total":sum(t["nodes_actual"] for t in trials),
            "actual_nodes_min":min(t["nodes_actual"] for t in trials),
            "actual_nodes_max":max(t["nodes_actual"] for t in trials),
            "depth_min":min(t["depth"] for t in trials),
            "depth_max":max(t["depth"] for t in trials)}

def engine_options(threads):
    return {"Threads":threads,"Hash":16,"Use NNUE":False,
            "Skill Level":20,"UCI_LimitStrength":False}

def run(binary, repeats, nodes):
    if repeats<4 or nodes<1000:
        raise ValueError("P11_HOLD_UNDERPOWERED_CONTRACT")
    cohort = positions()
    report = {"schema":SCHEMA, "source_commit":SOURCE_COMMIT, "binary_sha256":hexdigest(binary),
              "repeats_per_arm":repeats, "requested_nodes_each_trial":nodes,
              "classical_evaluation_nnue_disabled":True, "skill_level":20,
              "intentional_handicap_rng_enabled":False, "cohort":{},
              "causal_interpretation":"Descriptive only: changing threads and hash state does not uniquely identify source cause."}
    for pid, entry in cohort.items():
        board = chess.Board(entry["fen"])
        data = dict(entry, arms={})
        for name, threads, warm in ARMS:
            trials=[]
            if warm:
                with chess.engine.SimpleEngine.popen_uci(binary,timeout=120) as eng:
                    eng.configure(engine_options(threads))
                    same_game=object()
                    for _ in range(repeats):
                        trials.append(draw(eng, board, nodes, same_game))
            else:
                for _ in range(repeats):
                    with chess.engine.SimpleEngine.popen_uci(binary,timeout=120) as eng:
                        eng.configure(engine_options(threads))
                        trials.append(draw(eng, board, nodes, object()))
            data["arms"][name]={"threads":threads,"fresh_engine_per_trial":not warm,
                               "warm_same_game_object":warm,
                               "trials":trials,"summary":arm_summary(trials)}
        report["cohort"][pid]=data
        print("P11_POSITION",pid, " / ".join(
            f"{n}:{data['arms'][n]['summary']['distinct_moves']} moves"
            for n,_,_ in ARMS),flush=True)
    report["total_native_searches"]=len(cohort)*len(ARMS)*repeats
    report["total_actual_native_nodes"]=sum(
        arm["summary"]["actual_nodes_total"]
        for x in report["cohort"].values() for arm in x["arms"].values())
    report["per_arm_position_switch_fractions"]={
        name:sum(x["arms"][name]["summary"]["switch_observed"]
                 for x in report["cohort"].values())/len(cohort)
        for name,_,_ in ARMS}
    report["per_arm_position_mean_entropy_bits"]={
        name:sum(x["arms"][name]["summary"]["empirical_move_entropy_bits"]
                 for x in report["cohort"].values())/len(cohort)
        for name,_,_ in ARMS}
    report["same_position_not_same_search_cost"] = True
    report["all_unseen_positions_were_predeclared_from_fixed_opening_sequences"] = True
    report["native_source_causal_intervention_performed"] = False
    report["variance_cannot_be_assigned_to_rl_policy_sampling"] = True
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stockfish",required=True)
    p.add_argument("--repeats",type=int,default=6)
    p.add_argument("--nodes",type=int,default=12000)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    report=run(a.stockfish,a.repeats,a.nodes)
    file=Path(a.out);file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True,
                               allow_nan=False)+"\n",encoding="utf-8")
    print("C3X_P11_REAL_NATIVE",report["total_native_searches"],
          "NODES",report["total_actual_native_nodes"],"SWITCH",
          report["per_arm_position_switch_fractions"],"SHA",hexdigest(file),flush=True)

if __name__=="__main__":
    main()
