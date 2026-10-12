#!/usr/bin/env python3
"""Read-only UCI harness for official SF16; C++ owns all chess/hash rules."""
import json
import re
import subprocess
import sys
from pathlib import Path

BINARY, OUTPUT = sys.argv[1:3]
BOARD = "5k2/8/8/8/8/8/4Q3/4K3 w - -"
FENS = [BOARD + " 0 51", BOARD + " 100 51"]


def session(fen):
    p = subprocess.Popen([BINARY], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, bufsize=1)
    assert p.stdin and p.stdout

    def send(cmd):
        p.stdin.write(cmd + "\n")
        p.stdin.flush()

    def collect(done):
        lines = []
        while True:
            line = p.stdout.readline()
            if not line:
                raise RuntimeError("native engine terminated")
            line = line.strip()
            lines.append(line)
            if done(line):
                return lines

    try:
        send("uci")
        collect(lambda s: s == "uciok")
        for command in ("setoption name Threads value 1",
                        "setoption name Hash value 16",
                        "setoption name Use NNUE value false",
                        "ucinewgame", "isready"):
            send(command)
        collect(lambda s: s == "readyok")
        send("position fen " + fen)
        send("d")
        send("isready")
        dump = collect(lambda s: s == "readyok")
        key = next((m.group(1) for line in dump
                    if (m := re.fullmatch(r"Key: ([A-Fa-f0-9]{16})", line))), None)
        actual_fen = next((m.group(1) for line in dump
                           if (m := re.fullmatch(r"Fen: (.*)", line))), None)
        if not key or actual_fen != fen:
            raise AssertionError("original Stockfish FEN/Key not verified")
        send("go depth 4")
        lines = collect(lambda s: s.startswith("bestmove "))
        depth4 = [s for s in lines if s.startswith("info depth 4 ") and " nodes " in s]
        if not depth4:
            raise AssertionError("no completed native depth4")
        info = depth4[-1]
        score = re.search(r" score (cp|mate) (-?\d+)", info)
        nodes = re.search(r" nodes (\d+)", info)
        move = lines[-1].split()[1]
        if not score or not nodes or move == "(none)":
            raise AssertionError("no complete native bestmove/score/nodes")
        return {"fen": fen, "board_key_64": key,
                "halfmove_clock": int(fen.split()[4]), "bestmove": move,
                "score_type": score.group(1), "score": int(score.group(2)),
                "nodes": int(nodes.group(1))}
    finally:
        try:
            send("quit")
            p.communicate(timeout=5)
        except (BrokenPipeError, subprocess.TimeoutExpired):
            p.kill()
            p.communicate()


pairs = []
for fen in FENS:
    first = session(fen)
    repeat = session(fen)
    if first != repeat:
        raise AssertionError("original cold repeat nondeterministic")
    pairs.append(first)
if pairs[0]["board_key_64"] != pairs[1]["board_key_64"]:
    raise AssertionError("same board gave different full original Position::key")
if [r["halfmove_clock"] for r in pairs] != [0, 100]:
    raise AssertionError("halfmove-clock synthetic contrast absent")
differ = any(pairs[0][k] != pairs[1][k]
             for k in ("bestmove", "score_type", "score", "nodes"))
result = {
    "schema": "c3x025-P14-P7-original-SF16-context-identity-v1",
    "status": "ACTUAL_ORIGINAL_FULL_KEY_SAME_BUT_RULE50_DIFFERENT",
    "source_revision": "68e1e9b3811e16cad014b590d7443b9063b52",
    "original_source_draw_guard": "rule50>99 subject to legal check/move",
    "synthetic_development_FEN_not_historical_game": True,
    "same_full_zobrist_board_key": True,
    "observed_root_score_or_search_difference": differ,
    "true_TT_bound_corruption_observed": False,
    "original_full_K_constructed": False,
    "Elo_trial_performed": False,
    "cases": pairs,
}
Path(OUTPUT).write_text(json.dumps(result, indent=2) + "\n")
print("C3X025_P14P7_ORIGINAL_RULE50_CONTEXT_NATIVE_PASS", json.dumps(result))
