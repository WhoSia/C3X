#!/usr/bin/env python3
import subprocess, sys, re, json
from pathlib import Path

ENGINE, OUTPUT = sys.argv[1:3]
FEN = "5k2/8/8/8/8/8/4Q3/4K3 w - - 24 55"
POSITIONS = [
  "position fen " + FEN,
  "position fen 5k2/8/8/8/8/8/4Q3/4K3 w - - 16 51 moves e2e3 f8g8 e3e2 g8f8 e2e3 f8g8 e3e2 g8f8"
]

def observe(position):
    p = subprocess.Popen([ENGINE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
    def cmd(q):
        p.stdin.write(q + "\n")
        p.stdin.flush()
    def read_until(end):
        found=[]
        while True:
            x=p.stdout.readline()
            if not x:
                raise RuntimeError("SF16 terminated prematurely")
            x=x.strip()
            found.append(x)
            if end(x): return found
    try:
        cmd("uci")
        read_until(lambda x:x=="uciok")
        for c in ("setoption name Threads value 1","setoption name Hash value 16",
                  "setoption name Use NNUE value false","ucinewgame","isready"):
            cmd(c)
        read_until(lambda x:x=="readyok")
        cmd(position)
        cmd("d")
        cmd("isready")
        status=read_until(lambda x:x=="readyok")
        fen=next((x[5:] for x in status if x.startswith("Fen: ")),None)
        key=next((x[5:] for x in status if x.startswith("Key: ")),None)
        history=[x for x in status if x.startswith("info string c3xp8_history ")]
        if fen!=FEN or not key: raise AssertionError("different final original FEN")
        cmd("go depth 4")
        lines=read_until(lambda x:x.startswith("bestmove "))
        info=next((x for x in reversed(lines) if x.startswith("info depth 4 ") and " nodes " in x),None)
        if not info:raise AssertionError("missing depth4")
        score=re.search(r"score (cp|mate) (-?\d+)",info)
        nodes=re.search(r"nodes (\d+)",info)
        if not score or not nodes:raise AssertionError("incomplete score/nodes")
        return dict(fen=fen,key=key,move=lines[-1].split()[1],
                    score_type=score[1],score=int(score[2]),nodes=int(nodes[1]),history=history)
    finally:
        try:
            cmd("quit")
            p.communicate(timeout=5)
        except Exception:
            p.kill()
            p.communicate()

runs=[]
for q in POSITIONS:
    a,b=observe(q),observe(q)
    if a!=b:raise AssertionError("not cold deterministic")
    runs.append(a)
if runs[0]["key"]!=runs[1]["key"]:raise AssertionError("full key differs")
if runs[0]["fen"]!=runs[1]["fen"]:raise AssertionError("full FEN differs")
result=dict(schema="c3x025-P14-P8-native-original-history-pair-v1",
            development_not_independent=True,
            original_exact_current_FEN_and_key_equal=True,
            root_action_changed=runs[0]["move"]!=runs[1]["move"],
            TT_true_semantic_bound_certified=False, Elo_measured=False,cases=runs)
Path(OUTPUT).write_text(json.dumps(result,indent=2)+"\n")
print("C3X025_P14P8_ORIGINAL_HISTORY_PAIR_VERIFIED",json.dumps(result))
