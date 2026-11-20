"""Validate Stockfish's emitted result against its exact native root producer."""

import argparse
import json
import os
from pathlib import Path
import re

import chess.engine

from c3x_030_s4l_r10_reply_transport import board_at, digest
from c3x_030_s4l_r14_matched_trace import RecordedUci

CASES = "95cd7437db2e7f7a8862c8320bd22f0c875bdf79ddd4ea1c4dc348b57d180c9f"
NET = "5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b"
RECEIPT = re.compile(r"^info depth (\d+) .*? score (cp|mate) (-?\d+)(?: (lowerbound|upperbound))? nodes (\d+) .*? pv (\S+)(?: |$)")


def records(stderr, label):
    prefix = "C3X_R23_" + label + " "
    return [dict(pair.split("=", 1) for pair in line[len(prefix):].split())
            for line in stderr if line.startswith(prefix)]


def indexed(rows, key):
    output = {row[key]: row for row in rows}
    if len(output) != len(rows):
        raise ValueError(f"Duplicate {key}")
    return output


def source_result(row):
    value, alpha, beta = (int(row[key]) for key in ("value", "alpha", "beta"))
    if value <= alpha:
        return alpha, "upper"
    if value >= beta:
        return beta, "lower"
    return value, "none"


def join(stdout, stderr):
    if stderr.count("C3X_R23_GO_BEGIN") != 1:
        raise ValueError("Expected one native GO")
    starts = indexed(records(stderr, "START"), "attempt")
    ends = indexed(records(stderr, "END"), "attempt")
    candidates = indexed(records(stderr, "CANDIDATE"), "id")
    if starts.keys() != ends.keys() or list(map(int, starts)) != list(range(1, len(starts) + 1)):
        raise ValueError("Unbalanced native root attempts")
    if list(map(int, candidates)) != list(range(1, len(candidates) + 1)):
        raise ValueError("Missing native candidate receipt")
    if any(c["attempt"] not in starts for c in candidates.values()):
        raise ValueError("Candidate names an unknown native attempt")
    rows = records(stderr, "PUBLIC")
    matches = [match.groups() for line in stdout if (match := RECEIPT.match(line))]
    if len(rows) != len(matches):
        raise ValueError("Public root receipts differ from UCI")
    links = []
    for row, match in zip(rows, matches, strict=True):
        depth, kind, score, bound, nodes, move = match
        emitted_bound = bound.removesuffix("bound") if bound else "none"
        if (row["depth"], row["kind"], row["score"], row["bound"], row["nodes"], row["move"]) != (
                depth, kind, score, emitted_bound, nodes, move):
            raise ValueError("Native sink did not match public output")
        producer = candidates.get(row["producer"])
        if row["tb"] == "1":
            status = "tablebase"
        elif row["updated"] == "0":
            status = "previous"
        elif producer is None:
            status = "unknown"
        else:
            value, native_bound = source_result(producer)
            if (producer["move"] != move or producer["update"] != "1"
                    or int(row["value"]) != value or emitted_bound not in (native_bound, "none")
                    or int(producer["attempt"]) > int(row["sink_attempt"])):
                raise ValueError("Invalid native producer–consumer link")
            status = "exact" if native_bound == emitted_bound == "none" else "bounded"
        links.append({"public": row, "status": status, "source": producer,
                      "attempt": starts[producer["attempt"]] if producer else None,
                      "attempt_end": ends[producer["attempt"]] if producer else None})
    best, = records(stderr, "BEST")
    final, = (line.split()[1] for line in stdout if line.startswith("bestmove "))
    producer = candidates.get(best["producer"])
    if best["move"] != final or (producer and (producer["move"] != final or producer["update"] != "1")):
        raise ValueError("Bestmove producer differs")
    return {"reports": links, "best": best, "best_source": producer,
            "best_attempt": starts[producer["attempt"]] if producer else None,
            "best_attempt_end": ends[producer["attempt"]] if producer else None,
            "counts": {"attempts": len(starts), "candidate_returns": len(candidates)}}


def run(binary, case, net, directory, *, logging, paired, nnue, nodes=None, depth=None, hash_mib=16,
        environment=None):
    directory.mkdir(parents=True)
    env = dict(os.environ)
    if environment is not None:
        env.update(environment)
    env.pop("C3X_ROOT_PROVENANCE", None)
    if logging:
        env["C3X_ROOT_PROVENANCE"] = "1"
    board = board_at(case["history"])
    engine = chess.engine.SimpleEngine.popen(RecordedUci, str(binary.resolve()), cwd=directory, env=env)
    try:
        engine.configure({"Threads": 1, "Hash": hash_mib, "Use NNUE": nnue,
                          "EvalFile": str(net.resolve()), "Skill Level": 20, "UCI_LimitStrength": False})
        roots = [board.parse_uci(move) for move in case["roots"]] if paired else None
        result = engine.play(board, chess.engine.Limit(nodes=nodes, depth=depth),
                             root_moves=roots, info=chess.engine.INFO_ALL, game=object())
    finally:
        engine.quit()
    stdout, stderr = engine.protocol.stdout, engine.protocol.stderr
    for name, lines in (("stdout", stdout), ("stderr", stderr)):
        (directory / f"{name}.txt").write_text("\n".join(lines) + "\n")
    normalized = [re.sub(r"\b(?:nps|time) \d+ ?", "", line) for line in stdout
                  if line.startswith(("info depth ", "bestmove "))]
    if result.move not in board.legal_moves or (paired and result.move not in roots):
        raise ValueError("Illegal chosen root move")
    for line in normalized:
        if " pv " not in line:
            continue
        after = board.copy()
        for move in line.split(" pv ", 1)[1].split():
            if move == "0000":
                raise ValueError("Null move in UCI PV")
            after.push_uci(move)
    if not logging and any(line.startswith("C3X_R23_") for line in stderr):
        raise ValueError("Trace-off build emitted experimental data")
    return normalized, join(stdout, stderr) if logging else None


def scenarios():
    for paired in (False, True):
        for mode in ({"nodes": 24000}, {"depth": 10}):
            yield {"paired": paired, "nnue": True, **mode}
    yield {"paired": True, "nnue": False, "nodes": 24000}


def label(case, mode):
    return "-".join((case["id"], "paired" if mode["paired"] else "all",
                     "nnue" if mode["nnue"] else "classic", str(mode.get("nodes", mode.get("depth")))))


def suite(cases, clean, trace, net, output):
    rows = {}
    for case in cases:
        for mode in scenarios():
            name = label(case, mode)
            root = output / name
            baseline, _ = run(clean, case, net, root / "clean", logging=False, **mode)
            disabled, _ = run(trace, case, net, root / "off", logging=False, **mode)
            enabled, proof = run(trace, case, net, root / "on", logging=True, **mode)
            replay, repeat = run(trace, case, net, root / "repeat", logging=True, **mode)
            if baseline != disabled or disabled != enabled or enabled != replay or proof != repeat:
                raise ValueError(f"Run changed after tracing or repeat at {name}")
            rows[name] = {"uci": baseline, "proof": proof, "mode": mode}
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clean", type=Path)
    parser.add_argument("trace", type=Path)
    parser.add_argument("net", type=Path)
    parser.add_argument("cases", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if digest(args.cases) != CASES or digest(args.net) != NET:
        raise ValueError("Unexpected freeze or network")
    rows = suite(json.loads(args.cases.read_text())["cases"], args.clean, args.trace, args.net, args.output)
    print(json.dumps({"clean_sha256": digest(args.clean), "trace_sha256": digest(args.trace),
                      "net_sha256": NET, "cases_sha256": CASES, "rows": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
