"""Replay the Italian development case and join root calls to native TT masks."""
import argparse
import json
from pathlib import Path
import subprocess

FEN = "r1bqk2r/ppp2ppp/2np1n2/2b1p3/2B1P3/2PP1N2/PP3PPP/RNBQK2R w KQkq - 0 6"
TARGET = "1341504945262310742"
SHAM = "18446744073709551615"

def run(binary, arm, directory):
    work = directory / arm
    work.mkdir(exist_ok=True)
    key = TARGET if arm in ("one", "two", "second_only") else SHAM
    cap = {"original": 0, "sham": 10000, "one": 1, "two": 2, "second_only": 1}[arm]
    (work / "c3x_s4l_r2_control.txt").write_text(f"{TARGET} {key} {cap} {int(arm == 'second_only')}\n")
    with (directory / f"{arm}.stderr").open("w") as error_log:
        proc = subprocess.Popen([str(binary.resolve())], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=error_log, text=True, cwd=work)
    with proc:
        def send(command):
            print(command, file=proc.stdin, flush=True)

        def until(prefix):
            lines = []
            for line in proc.stdout:
                lines.append(line.strip())
                if line.startswith(prefix):
                    return lines
            raise RuntimeError(f"Missing {prefix} in {arm}")

        send("uci")
        until("uciok")
        for option in ("Threads value 1", "Hash value 16", "Use NNUE value false"):
            send("setoption name " + option)
        send("ucinewgame")
        send("isready")
        until("readyok")
        results = []
        with (directory / f"{arm}.uci").open("w") as output:
            for epoch in (1, 2):
                send("position fen " + FEN)
                send("go nodes 12000")
                lines = until("bestmove ")
                print(*lines, sep="\n", file=output)
                info = [line for line in lines if " score " in line and " pv " in line][-1]
                results.append({"epoch": epoch, "info": " ".join(info.split()[:info.split().index("nps")] + info.split()[info.split().index("pv"):]), "bestmove": lines[-1].split()[1]})
        send("quit")
    if proc.returncode:
        raise RuntimeError(f"Engine failed in {arm}")
    return results

def read_rows(path):
    selected = {"C3X_R2_EDGE", "C3X_S4G_MASK", "C3X_S4L_ROOT_SCORE", "C3X_R2_QRETURN"}
    for line in path.read_text().splitlines():
        prefix, _, payload = line.partition(" ")
        if prefix in selected:
            yield prefix, dict(token.split("=", 1) for token in payload.split())

def audit(path):
    edges, masks, receipts, qreturns = {}, [], {}, {}
    for kind, r in read_rows(path):
        if kind == "C3X_R2_EDGE":
            edges[r["epoch"], r["parent"], r["child"]] = r
        if kind == "C3X_R2_QRETURN":
            qreturns[r["parent"],r["id"]] = r
        if kind == "C3X_S4G_MASK":
            masks.append(r)
        if kind == "C3X_S4L_ROOT_SCORE":
            key = (r["epoch"], r["root_id"], r["child_id"])
            edge = edges[key]
            assert (edge["move"], edge["value"], edge["stopped"]) == (r["root_move_raw"], r["value"], "0")
            receipts[key] = r
    for m in masks:
        ret = qreturns[m["parent"], m["id"]]
        assert int(ret["value"]) == -int(edges[m["epoch"],m["parent"],m["id"]]["value"])
    return {"root_receipts":len(receipts), "root_child_edges":len(edges),
            "masked_calls":[{"mask":m, "edge":edges.get((m["epoch"],m["parent"],m["id"])),
                             "qreturn":qreturns.get((m["parent"],m["id"])),
                             "receipt":receipts.get((m["epoch"],m["parent"],m["id"]))} for m in masks]}

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("original", "instrumented", "directory"):
        p.add_argument(name, type=Path)
    a = p.parse_args()
    a.directory.mkdir(parents=True, exist_ok=True)
    runs = {}
    for arm in ("original", "sham", "one", "two", "second_only"):
        runs[arm] = run(a.original if arm == "original" else a.instrumented, arm, a.directory)
    assert runs["original"] == runs["sham"]
    evidence = {arm: audit(a.directory / f"{arm}.stderr") for arm in ("sham", "one", "two", "second_only")}
    assert [len(evidence[arm]["masked_calls"]) for arm in ("sham", "one", "two", "second_only")] == [0,1,2,1]
    print(json.dumps({"trials":runs, "audit":evidence}, indent=2))
