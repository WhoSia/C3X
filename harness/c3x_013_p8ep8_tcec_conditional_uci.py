#!/usr/bin/env python3
"""C3X 0.13 P8-EP8: legal TCEC confluence, free/forced/endpoint three-arm UCI court.

The forced arm uses UCI 'go searchmoves', NOT analysis after a reply.
No causal or minimax certificate follows from depth-limited scores.
"""
import argparse
import hashlib
import json
from pathlib import Path
import chess
import chess.engine

ROOT = "r5k1/6p1/p5qn/4p2p/2ppP3/3Q3P/1P1B1PP1/R5K1 w - - 0 25"
EXPECTED = "r5k1/6p1/p5qn/4p2p/3pP3/1p1Q3P/3B1PP1/R5K1 w - - 0 26"
BRANCHES = {"a": ("b2b3", "c4b3"), "b": ("b2b4", "c4b3")}
DEPTHS = (8, 12, 16)
ETH_COMMIT = "0e47e9b67f345c75eb965d9fb3e2493b6a11d09a"

def worlds():
    result = {}
    for key, (first, reply) in BRANCHES.items():
        board = chess.Board(ROOT)
        assert board.is_valid() and board.turn == chess.WHITE
        m = chess.Move.from_uci(first)
        assert m in board.legal_moves
        board.push(m)
        r = chess.Move.from_uci(reply)
        assert r in board.legal_moves and board.is_capture(r)
        kind = "EN_PASSANT" if board.is_en_passant(r) else "NORMAL_CAPTURE"
        after_first = board.copy(stack=True)
        board.push(r)
        assert board.fen(en_passant="fen") == EXPECTED
        result[key] = (after_first, board.copy(stack=True), kind, r)
    assert result["a"][2] == "NORMAL_CAPTURE"
    assert result["b"][2] == "EN_PASSANT"
    assert result["a"][1].fen(en_passant="fen") == result["b"][1].fen(en_passant="fen")
    return result

def measure(executable, board, depth, forced_reply=None):
    """Every call starts its own engine: avoids leaking TT/history across arms."""
    with chess.engine.SimpleEngine.popen_uci(executable, timeout=120) as engine:
        required = {"Threads": 1, "Hash": 16}
        missing = set(required) - set(engine.options)
        if missing:
            raise ValueError(f"Engine lacks frozen UCI options: {sorted(missing)}")
        engine.configure(required)
        kwargs = {"info": chess.engine.INFO_ALL}
        if forced_reply is not None:
            assert forced_reply in board.legal_moves
            kwargs["root_moves"] = [forced_reply]
        info = engine.analyse(board, chess.engine.Limit(depth=depth), **kwargs)
        assert info.get("depth") == depth, ("incomplete depth", depth, info.get("depth"))
        pv = info.get("pv", [])
        if forced_reply is not None:
            assert pv and pv[0] == forced_reply, "UCI searchmoves ignored or invalid"
        score = info["score"].white()
        return {
            "score_white_cp": score.score(mate_score=None),
            "mate_white": score.mate(),
            "depth_completed": info.get("depth"),
            "nodes": info.get("nodes"),
            "seldepth": info.get("seldepth"),
            "first_move": pv[0].uci() if pv else None,
            "root_reply_constrained": forced_reply is not None
        }

def sample(exe, depth, worlds_map):
    branches = {}
    for key, (pre, post, kind, legal_reply) in worlds_map.items():
        # All three arms are mutually cold.
        free = measure(exe, pre, depth)
        forced = measure(exe, pre, depth, legal_reply)
        # One less ply, for comparison of a fixed reply followed by continuation.
        endpoint = measure(exe, post, depth-1)
        free_cp, forced_cp = free["score_white_cp"], forced["score_white_cp"]
        branches[key] = {
            "root_move": BRANCHES[key][0],
            "reply_uci": legal_reply.uci(),
            "capture_kind": kind,
            "free_opponent_reply": free,
            "forced_convergence_reply_via_go_searchmoves": forced,
            "cold_equal_FEN_after_capture_depth_minus_one": endpoint,
            "PV_first_reply_is_convergence_capture": free["first_move"] == legal_reply.uci(),
            "forced_minus_free_white_cp": None if free_cp is None or forced_cp is None
                                           else forced_cp-free_cp
        }
    t_a=branches["a"]["cold_equal_FEN_after_capture_depth_minus_one"]
    t_b=branches["b"]["cold_equal_FEN_after_capture_depth_minus_one"]
    # This is an empirical reproducibility diagnostic, not a universal equality assumption.
    equal_terminal = all(t_a.get(field) == t_b.get(field)
                         for field in ("score_white_cp","mate_white","first_move","nodes","depth_completed"))
    return {"branches": branches, "equal_endpoint_cold_run_exact": equal_terminal}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stockfish", required=True)
    p.add_argument("--ethereal", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    games = worlds()
    record = {
        "schema": "c3x-013-p8-ep8-three-arm-conditional-reply-v2",
        "status": "DEVELOPMENTAL_REAL_ENGINE_COMPARISON_NOT_CAUSAL",
        "root_fen": ROOT, "common_six_field_fen": EXPECTED,
        "source": {"broadcast": "TCEC S30 Playoff Swiss 10 Playoff Cat 2",
                   "rank":111,"ply":48,
                   "game_url":"https://lichess.org/broadcast/tcec-s30-playoff-swiss-10-playoff-cat-2/round-1/kpZI9MVi/1oANqqKQ",
                   "independent_source_provider_replication":False},
        "condition_names": ["free_reply_from_after_root", "forced_reply_from_after_root",
                            "cold_converged_endpoint_at_depth_minus_one"],
        "forced_UCI_semantics": "python-chess root_moves => go searchmoves at same after-root position",
        "engines": {}, "C3X_014": "UNOPENED_UNNAMED"
    }
    for name, exe in (("Stockfish",args.stockfish),("Ethereal_classical",args.ethereal)):
        x={"binary_sha256":hashlib.sha256(Path(exe).read_bytes()).hexdigest(),
           "engine_source_commit":ETH_COMMIT if name=="Ethereal_classical" else "ubuntu_runner_stockfish_apt_version_to_record",
           "depths":{}}
        for d in DEPTHS:
            trials = [sample(exe,d,games) for _ in range(2)]
            x["depths"][str(d)] = {"trials":trials,
                "same_terminal_cold_result_both_paths":all(t["equal_endpoint_cold_run_exact"] for t in trials)}
        record["engines"][name]=x
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(record,indent=2)+"\n")
    print("P8_EP8_THREE_ARM_UCI_PANEL", {k: {d: v["same_terminal_cold_result_both_paths"]
                                       for d,v in row["depths"].items()}
                                        for k,row in record["engines"].items()})
    assert record["C3X_014"]=="UNOPENED_UNNAMED"
if __name__ == "__main__":
    main()
