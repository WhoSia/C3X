#!/usr/bin/env python3
"""C3X P14-P9 real original SF16 perft/checker: source-typed mate-in-1
decision certificate. No NNUE/TT heuristic can certify chess legality.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ENGINE, OUTPUT = sys.argv[1:3]
FEN = "7k/8/5KQ1/8/8/8/8/8 w - - 0 1"
MOVE = re.compile(r"^([a-h][1-8][a-h][1-8][qrbn]?): (\d+)$")

def trial():
    process = subprocess.Popen(
        [ENGINE], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, bufsize=1)
    assert process.stdin and process.stdout
    def send(command):
        process.stdin.write(command + "\n")
        process.stdin.flush()
    def until(finish):
        result = []
        while True:
            line = process.stdout.readline()
            if line == "":
                raise RuntimeError("unmodified Stockfish terminated unexpectedly")
            line = line.strip()
            result.append(line)
            if finish(line):
                return result
    def position(command):
        send(command)
        send("d")
        send("isready")
        lines = until(lambda s: s == "readyok")
        fen = next((s[5:] for s in lines if s.startswith("Fen: ")), None)
        checkers = next((s[len("Checkers: "):] for s in lines
                         if s.startswith("Checkers: ")), None)
        if fen is None or checkers is None:
            raise AssertionError("Original source did not emit FEN/checkers")
        return {"fen": fen, "checkers": checkers.split()}
    def perft1():
        send("go perft 1")
        result = until(lambda s: s.startswith("Nodes searched: "))
        pairs = {}
        for s in result:
            m = MOVE.fullmatch(s)
            if m:
                if m[1] in pairs or int(m[2]) != 1:
                    raise AssertionError("Invalid original legal perft1 move entry")
                pairs[m[1]] = 1
        nodes = int(result[-1].split(": ")[1])
        if len(pairs) != nodes:
            raise AssertionError("Original source legal move list disagrees with perft1 count")
        return list(pairs)
    try:
        send("uci")
        until(lambda s: s == "uciok")
        for cmd in ["setoption name Threads value 1",
                    "setoption name Hash value 16",
                    "setoption name Use NNUE value false",
                    "ucinewgame", "isready"]:
            send(cmd)
        until(lambda s: s == "readyok")
        root = position("position fen " + FEN)
        if root["fen"] != FEN or root["checkers"]:
            raise AssertionError("Precommitted FEN invalid or current king in check")
        legal_root = perft1()
        if not legal_root:
            raise AssertionError("No legal original root moves")
        classifications = []
        for move in legal_root:
            child = position("position fen " + FEN + " moves " + move)
            replies = perft1()
            gives_check = bool(child["checkers"])
            mate = not replies and gives_check
            stalemate = not replies and not gives_check
            if not mate and not stalemate and not replies:
                raise AssertionError("Nonterminal non-mate has no reply")
            classifications.append({
                "root_legal_move": move,
                "child_checkers": child["checkers"],
                "opponent_legal_reply_count": len(replies),
                "mate_in_one": mate,
                "stalemate_in_one": stalemate,
                "nonmate_counterwitness": replies[0] if replies else
                   ("STALEMATE_NOT_MATE" if stalemate else None)
            })
        send("position fen " + FEN)
        send("go depth 4")
        search = until(lambda s: s.startswith("bestmove "))
        bestmove = search[-1].split()[1]
        info = next((s for s in reversed(search)
                     if s.startswith("info depth 4 ") and " nodes " in s), None)
        if not info:
            raise AssertionError("Depth4 original native analysis absent")
        score = re.search(r"\bscore (cp|mate) (-?\d+)", info)
        nodes = re.search(r"\bnodes (\d+)", info)
        if not score or not nodes or bestmove not in legal_root:
            raise AssertionError("Native depth4 result incomplete or illegal")
        return {
            "fen": FEN,
            "root_legal_moves": legal_root,
            "root_legal_move_count": len(legal_root),
            "certified_mate_in_one_moves":
                [r["root_legal_move"] for r in classifications if r["mate_in_one"]],
            "nonmate_alternatives":
                len([r for r in classifications if not r["mate_in_one"]]),
            "fully_classified_root_moves": classifications,
            "original_depth4_bestmove": bestmove,
            "original_depth4_bestmove_is_certified_mate":
                bestmove in [r["root_legal_move"] for r in classifications if r["mate_in_one"]],
            "native_depth4_score_type": score[1],
            "native_depth4_score": int(score[2]),
            "native_depth4_nodes": int(nodes[1]),
        }
    finally:
        try:
            send("quit")
            process.communicate(timeout=5)
        except (BrokenPipeError, subprocess.TimeoutExpired):
            process.kill()
            process.communicate()

a = trial()
b = trial()
if a != b:
    raise AssertionError("Official original SF16 cold repeat diverged")
if not a["certified_mate_in_one_moves"]:
    raise AssertionError("PREREGISTERED_MATE_IN_ONE_HYPOTHESIS_FALSE")
result = {
    "schema": "c3x025-P14-P9-source-native-bilateral-terminal-mate1-v1",
    "revision": "68e1e9b3811e16cad014b590d7443b9063b3eb52",
    "positions_are_synthetic_development": True,
    "two_independent_cold_source_sessions_agree": True,
    "sources": ["Stockfish16 original MoveList<LEGAL> via go perft 1",
                "original Position::checkers() via UCI d"],
    "eligibility": {
        "source_readable_terminal_chess_rule": True,
        "raw_TT_bound_is_accepted_as_chess_truth": False,
        "scope": "immediate checkmate only, not heuristic cp nor full minimax"
    },
    "native": a,
    "global_Stockfish_K_proven": False,
    "elo_games": 0,
}
Path(OUTPUT).write_text(json.dumps(result, indent=2) + "\n")
print("C3X025_P14P9_SOURCE_NATIVE_BILATERAL_TERMINAL_CERT_PASS",
      json.dumps({"fen": FEN,
                  "root_candidates": a["root_legal_move_count"],
                  "mate_witnesses": a["certified_mate_in_one_moves"],
                  "nonmate_with_counterwitness": a["nonmate_alternatives"],
                  "actual_bestmove": a["original_depth4_bestmove"],
                  "native_bestmove_certified_mate":
                    a["original_depth4_bestmove_is_certified_mate"],
                  "Elo": "UNTESTED"}))
