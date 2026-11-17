"""Replay one development position with and without a single ply-one TT hit."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path

import chess.engine

from c3x_030_s4l_r10_reply_transport import board_at, digest
from c3x_030_s4l_r11_allocation import SF
from c3x_030_s4l_r14_matched_trace import OPTIONS, RecordedUci

HISTORY = "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3 g8f6".split()
SENTINEL = 2**64 - 1


def fields(lines, prefix):
    return [dict(field.split("=", 1) for field in line.split()[1:])
            for line in lines if line.startswith(prefix + " ")]


def run(binary, directory, target=0, mask=False):
    directory.mkdir()
    if target:
        control = directory / "c3x_s4l_r2_control.txt"
        control.write_text(f"{target} {target if mask else SENTINEL} 1 0\n")
    env = dict(os.environ, C3X_S4H2_ELIGIBILITY_MODE="1")
    engine = chess.engine.SimpleEngine.popen(RecordedUci, str(binary), cwd=directory, env=env)
    try:
        engine.configure(OPTIONS)
        result = engine.play(board_at(HISTORY), chess.engine.Limit(nodes=12000),
                             info=chess.engine.INFO_ALL, game=object())
    finally:
        engine.quit()
    stdout, stderr = engine.protocol.stdout, engine.protocol.stderr
    for name, lines in (("uci", stdout), ("stderr", stderr)):
        (directory / f"{name}.txt").write_text("\n".join(lines) + "\n")
    public = {
        "move": result.move.uci(),
        "pv": [move.uci() for move in result.info["pv"]],
        "score": result.info["score"].white().score(mate_score=100000),
        "depth": result.info["depth"],
        "nodes": result.info["nodes"],
    }
    return public, stderr


def summarize(public, stderr, target, mask):
    eligible = fields(stderr, "C3X_S4H2_ELIGIBLE")
    probes = [event for event in fields(stderr, "C3X_S4E") if event["kind"] == "probe"]
    masks = fields(stderr, "C3X_S4G_MASK")
    if not eligible or int(eligible[0]["key"]) != target or len(masks) != int(mask):
        raise ValueError("The nominated first hit or mask count did not reproduce")
    event = (next(row for row in probes if row["id"] == masks[0]["id"]) if mask
             else next(row for row in probes if row["hit"] == "1"))
    if int(event["key"]) != target or event["hit"] != ("0" if mask else "1"):
        raise ValueError("Unexpected hit state at the nominated probe")
    lifecycle = [row for row in fields(stderr, "C3X_S4E")
                 if row.get("id") == event["id"] and row["kind"] != "probe"]
    roots = [row for row in fields(stderr, "C3X_S4L_ROOT_SCORE")
             if row["child_id"] == event["id"] and row["root_id"] == event["parent"]]
    updates = [row for row in fields(stderr, "C3X_S4E")
               if row["kind"] == "root_candidate" and row.get("child_id") == event["id"]]
    return {"public": public, "probe": event, "masks": masks, "lifecycle": lifecycle,
            "parent_root_scores": roots, "target_root_updates": updates,
            "included_events": len(eligible),
            "trace_sha256": sha256("\n".join(stderr).encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("discover", "pair"))
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    binary = args.binary.resolve()
    if digest(binary) != SF:
        raise ValueError("Unexpected Stockfish binary")
    if args.mode == "discover":
        _, stderr = run(binary, args.output)
        first = fields(stderr, "C3X_S4H2_ELIGIBLE")[0]
        if first["ordinal"] != "0" or first["ply"] != "1" or first["hit_before"] != "1":
            raise ValueError("Unexpected nomination")
        print(json.dumps({"target": int(first["key"]), "history": HISTORY, "binary_sha256": SF,
                          "discovery_stderr_sha256": digest(args.output / "stderr.txt")}, indent=2))
        return
    if args.receipt is None:
        parser.error("pair requires a discovery receipt")
    receipt = json.loads(args.receipt.read_text())
    if receipt["binary_sha256"] != SF or receipt["history"] != HISTORY:
        raise ValueError("Unexpected discovery provenance")
    target = receipt["target"]
    args.output.mkdir()
    rows = {}
    for arm in ("sham", "mask"):
        for repeat in (1, 2):
            mask = arm == "mask"
            public, raw = run(binary, args.output / f"{arm}-{repeat}", target, mask)
            rows[f"{arm}-{repeat}"] = summarize(public, raw, target, mask)
        if rows[f"{arm}-1"] != rows[f"{arm}-2"]:
            raise ValueError(f"Non-repeating {arm} results")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
