#!/usr/bin/env python3
"""Actual native Stockfish16 minimal-board Fritz §VI-A source measurement.

Produce paired forced-root scores for three explicitly legal root actions,
original board and three empty squares with both pawn colors. Chess rules
via python-chess, pinned native upstream Stockfish16 with NNUE disabled,
1 thread, 16MB hash, same fixed *requested node cap*. Actual executed
nodes are recorded and may differ. This is a DEMONSTRATION on a manually
constructed legal position, not Fritz paper's published benchmark.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

from c3x_030_p8_fritz_empty_square_saliency import summarize

SOURCE_COMMIT = "68e1e9b3811e16cad014b590d7443b9063b3eb52"
FEN = "4k3/8/8/8/8/8/4P3/4K1N1 w - - 0 1"
ACTIONS = ("g1f3", "g1h3", "e1f1")
SQUARES = ("d4", "e4", "f4")
NODES_CAP = 3000

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def forced_q(engine, board, labels, nodes_cap):
    if (not board.is_valid() or board.is_game_over(claim_draw=False)
            or len(labels) < 3):
        raise ValueError("P8_NATIVE_HOLD_INVALID_POSITION")
    details = {}
    for u in labels:
        m = chess.Move.from_uci(u)
        if m not in board.legal_moves:
            raise ValueError("P8_NATIVE_HOLD_LOST_ACTION_SUPPORT")
        info = engine.analyse(board, chess.engine.Limit(nodes=nodes_cap),
                              root_moves=[m], game=object(), info=chess.engine.INFO_ALL)
        pv = info.get("pv")
        nodes = info.get("nodes")
        depth = info.get("depth")
        score = info.get("score")
        if (not pv or pv[0] != m or type(nodes) is not int or nodes <= 0
                or type(depth) is not int or depth <= 0 or score is None):
            raise ValueError("P8_NATIVE_HOLD_ENGINE_PROVENANCE")
        cp = score.pov(chess.WHITE).score()
        if type(cp) is not int:
            raise ValueError("P8_NATIVE_HOLD_MATE_CP")
        details[u] = {"q_cp": cp, "nodes": nodes, "depth": depth,
                      "first_pv_uci": pv[0].uci()}
    return details

def produce(engine, engine_path):
    b = chess.Board(FEN)
    if not b.is_valid() or b.is_game_over(claim_draw=False):
        raise ValueError("P8_NATIVE_HOLD_SOURCE_BOARD")
    if not all(chess.Move.from_uci(u) in b.legal_moves for u in ACTIONS):
        raise ValueError("P8_NATIVE_HOLD_SOURCE_ACTION_SET")
    original = forced_q(engine, b, ACTIONS, NODES_CAP)
    record = {"schema": "c3x030-p8-fritz-raw-probe-v1",
              "original_q": {k: v["q_cp"] for k, v in original.items()},
              "selected_action": ACTIONS[0], "temperature": 100.0,
              "square_probes": []}
    audit_rows = [{"world": "original", "fen": b.fen(en_passant="fen"),
                   "forced_root_actual": original}]
    for sq in SQUARES:
        square = chess.parse_square(sq)
        if b.piece_at(square) is not None:
            raise ValueError("P8_NATIVE_HOLD_NOT_EMPTY")
        row = {"square": sq, "was_empty_at_source": True, "pawn_probes": {}}
        for name, color in (("white", chess.WHITE), ("black", chess.BLACK)):
            pert = b.copy(stack=True)
            pert.set_piece_at(square, chess.Piece(chess.PAWN, color))
            legal = pert.is_valid() and not pert.is_game_over(claim_draw=False)
            moves_ok = legal and all(chess.Move.from_uci(u) in pert.legal_moves
                                     for u in ACTIONS)
            if not moves_ok:
                row["pawn_probes"][name] = {"status": "not_measured",
                                            "reason": "INVALID_BOARD_OR_LOST_FIXED_ACTION_SUPPORT"}
                continue
            q = forced_q(engine, pert, ACTIONS, NODES_CAP)
            row["pawn_probes"][name] = {
                "status": "legal_measured",
                "position_legality_verified_externally": True,
                "same_action_legal_in_perturbation": True,
                "same_engine_and_search_budget": True,
                "perturbed_q": {k: v["q_cp"] for k, v in q.items()}}
            audit_rows.append({"world": name + "_pawn_" + sq,
                               "fen": pert.fen(en_passant="fen"),
                               "forced_root_actual": q})
        record["square_probes"].append(row)
    result = summarize(record)
    result["actual_native_measurement"] = {
        "source_fen": b.fen(en_passant="fen"),
        "source_commit": SOURCE_COMMIT,
        "stockfish_binary_sha256": digest(engine_path),
        "engine_name": engine.id.get("name"),
        "use_nnue": False, "threads": 1, "hash_mb": 16,
        "requested_nodes_cap_each_forced_action": NODES_CAP,
        "actual_native_forced_search_count": len(audit_rows) * len(ACTIONS),
        "actual_native_nodes_total": sum(v["nodes"] for r in audit_rows
                                         for v in r["forced_root_actual"].values()),
        "all_probed_worlds": audit_rows,
        "source_type": "MANUALLY_CONSTRUCTED_LEGAL_SMALL_PIECE_POSITION",
        "published_fritz_benchmark_reproduced": False,
        "full_all_legal_opponent_responses_measured": False,
        "source_root_causal_event_proven": False}
    if len(audit_rows) < 2 or result["complete_two_color_count"] < 1:
        raise ValueError("P8_NATIVE_HOLD_NO_COMPLETE_MEASURED_SQUARE")
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stockfish", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with chess.engine.SimpleEngine.popen_uci(a.stockfish, timeout=120) as engine:
        if "stockfish" not in engine.id.get("name", "").lower():
            raise ValueError("P8_NATIVE_HOLD_ENGINE_FAMILY")
        options = engine.options
        if not {"Use NNUE", "Threads", "Hash"}.issubset(options):
            raise ValueError("P8_NATIVE_HOLD_REQUIRED_ENGINE_OPTIONS")
        engine.configure({"Use NNUE": False, "Threads": 1, "Hash": 16})
        data = produce(engine, a.stockfish)
    path = Path(a.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n",
                    encoding="utf-8")
    print("C3X_P8_REAL_NATIVE_FRITZ_PAWN_WORLD_MEASUREMENT",
          data["actual_native_measurement"]["actual_native_forced_search_count"],
          "nodes", data["actual_native_measurement"]["actual_native_nodes_total"],
          "complete", data["complete_two_color_count"], "SHA", digest(path), flush=True)

if __name__ == "__main__":
    main()
