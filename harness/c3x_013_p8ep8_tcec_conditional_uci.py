#!/usr/bin/env python3
"""C3X 0.13 P8-EP8: frozen TCEC confluence, descriptive UCI reply experiment."""
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

def worlds():
    output = {}
    for key, (candidate, forced_reply) in BRANCHES.items():
        b = chess.Board(ROOT)
        root_move = chess.Move.from_uci(candidate)
        assert root_move in b.legal_moves
        b.push(root_move)
        r = chess.Move.from_uci(forced_reply)
        assert r in b.legal_moves and b.is_capture(r)
        kind = "EN_PASSANT" if b.is_en_passant(r) else "NORMAL_CAPTURE"
        after_candidate = b.copy()
        b.push(r)
        assert b.fen(en_passant="fen") == EXPECTED
        output[key] = (after_candidate, b, kind)
    assert output["a"][2] == "NORMAL_CAPTURE"
    assert output["b"][2] == "EN_PASSANT"
    return output

def measure(executable, board, depth):
    # A new engine process means the TT and adaptive search state are cold.
    with chess.engine.SimpleEngine.popen_uci(executable, timeout=120) as engine:
        engine.configure({"Threads": 1, "Hash": 16})
        info = engine.analyse(board, chess.engine.Limit(depth=depth), info=chess.engine.INFO_ALL)
        score = info["score"].white()
        return {"score_white_cp": score.score(mate_score=None),
                "mate_white": score.mate(),
                "depth": info.get("depth"),
                "nodes": info.get("nodes"),
                "first_move": info.get("pv", [None])[0].uci() if info.get("pv") else None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stockfish", required=True)
    ap.add_argument("--ethereal", required=True)
    ap.add_argument("--output", required=True)
    args=ap.parse_args()
    pairs=worlds()
    record={"schema":"c3x-013-p8-ep8-conditional-reply-observation-v1",
            "scientific_status":"DEVELOPMENTAL_ENGINE_OBSERVATION_NOT_CAUSAL",
            "root_fen":ROOT,"expected_converged_full_fen":EXPECTED,
            "engines":{},"source_events":1,"independent_provider_replication":False,
            "C3X_014":"UNOPENED_UNNAMED"}
    for name, exe in [("Stockfish", args.stockfish),("Ethereal_classical", args.ethereal)]:
        record["engines"][name]={"binary_sha256":hashlib.sha256(Path(exe).read_bytes()).hexdigest(),
                                 "depths":{}}
        for depth in DEPTHS:
            repeats=[]
            for _ in range(2):
                branches={}
                for k,(pre,post,kind) in pairs.items():
                    free=measure(exe,pre,depth)
                    forced=measure(exe,post,depth)
                    branches[k]={"root_move":BRANCHES[k][0],
                                 "convergence_capture":BRANCHES[k][1],
                                 "capture_kind":kind,"free_reply":free,
                                 "forced_after_capture":forced,
                                 "free_reply_chooses_capture":free["first_move"]==BRANCHES[k][1]}
                repeats.append(branches)
            record["engines"][name]["depths"][str(depth)]={"trials":repeats}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(record,indent=2)+"\n")
    print("P8_EP8_REAL_UCI_PANEL_COMPLETED",len(record["engines"]),len(DEPTHS))
if __name__=="__main__":
    main()
