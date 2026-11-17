"""Make matched source forecasts and judge them on the exact same legal histories."""

import argparse
import json
import logging
from pathlib import Path
import re
from tempfile import TemporaryDirectory

import chess.engine

from c3x_030_r20_p40_value import BINARY
from c3x_030_r21_root_screen import SOURCE
from c3x_030_s4l_r10_reply_transport import analysis, board_at, digest
from c3x_030_s4l_r11_allocation import NET, SF, receipt, single
from c3x_030_s4l_r12_explanation_score import sign
from c3x_030_s4l_r12_reply_questions import fingerprint
from c3x_030_s4l_r14_matched_trace import OPTIONS, RecordedUci, positions
from c3x_030_s4l_r14_trace_projection import (
    ORDINARY_LIMIT, complete_root_events, ordinary_cp, trace_candidate,
)

ARMS = ("pv", "pv_strict", "tree", "trace", "trace_r14")
DEPTHS = (14, 16)


def trace_point(reports, lines, mover_is_leaf_turn):
    exact = [row for row in reports if row["cp"] is not None and not row["bound"]]
    if not exact:
        return None, "missing_public_point"
    events, status = complete_root_events(lines)
    if events is None:
        return None, status
    for event in sorted(events, key=lambda row: (row["iteration"], row["ordinal"]), reverse=True):
        value = event["value"]
        iteration = event["iteration"]
        if (iteration <= exact[-1]["depth"] or abs(value) >= ORDINARY_LIMIT
                or not event["alpha"] < value < event["beta"] or not event["will_update_root_pv"]):
            continue
        cp = ordinary_cp(value)
        if not mover_is_leaf_turn:
            cp = -cp
        bounds = [row for row in reports if row["depth"] == iteration and row["bound"]]
        if any(row["cp"] is None or (row["upper"] and cp > row["cp"])
               or (row["lower"] and cp < row["cp"]) for row in bounds):
            continue
        return {**event, "cp": cp}, "added"
    return None, "no_compatible_deeper_event"


def traced_leaf(binary, board, mover):
    reports = []
    with TemporaryDirectory(prefix="c3x-r21-") as directory:
        with chess.engine.SimpleEngine.popen(RecordedUci, str(binary.resolve()), cwd=directory) as engine:
            engine.configure(OPTIONS)
            with engine.analysis(board, chess.engine.Limit(nodes=24000), game=object()) as stream:
                for info in stream:
                    row = receipt(info, mover, board)
                    if row is None:
                        continue
                    upper = bool(info.get("upperbound"))
                    lower = bool(info.get("lowerbound"))
                    if mover != board.turn:
                        upper, lower = lower, upper
                    reports.append({**row, "upper": upper, "lower": lower})
                result = stream.wait()
            engine.quit()
            trace = engine.protocol.stderr
            stdout = [re.sub(r"\b(?:nps|time) \d+ ?", "", line) for line in engine.protocol.stdout
                      if line.startswith(("info depth ", "bestmove "))]
    if not reports or result.move not in board.legal_moves:
        raise ValueError("Invalid tree leaf receipt")
    exact = [row for row in reports if row["cp"] is not None and not row["bound"]]
    base = exact[-1]["cp"] if exact else None
    event, status = trace_point(reports, trace, board.turn == mover)
    strict, _ = trace_candidate(trace, max(row["depth"] for row in reports))
    strict_cp = ordinary_cp(strict["value"]) if strict and base is not None else None
    if strict_cp is not None and mover != board.turn:
        strict_cp = -strict_cp
    values = {"tree": base, "trace": event["cp"] if event else base,
              "trace_r14": strict_cp if strict_cp is not None else base}
    return {"values": values, "trace_status": status, "event": event, "reports": reports,
            "stdout": stdout, "stderr": trace, "nodes": reports[-1]["nodes"]}


def pv_pair(engine, question):
    board = board_at(question["history"])
    points = []
    for root in question["roots"]:
        branch = board.copy()
        branch.push_uci(root)
        search, = analysis(engine, branch, board.turn, nodes=48000)
        points.append(search)
    return points


def difference(values):
    first, second = values
    return None if first is None or second is None else sign(first - second)


def predict(binary, cohort):
    rows, pv = {}, {}
    with chess.engine.SimpleEngine.popen_uci(str(binary.resolve())) as engine:
        engine.configure(OPTIONS)
        for question in cohort["questions"].values():
            if question["round"] not in pv:
                pv[question["round"]] = pv_pair(engine, question)
    for key, question in cohort["questions"].items():
        pair = pv[question["round"]]
        points = [row["last_unbounded"] for row in pair]
        pv_label = difference([p["cp"] if p else None for p in points])
        strict = all(p and p["pv"][0] == question["reply"] for p in points)
        leaves = [traced_leaf(binary, board, mover) for board, mover in positions(question)]
        signs = {arm: difference([row["values"][arm] for row in leaves])
                 for arm in ("tree", "trace", "trace_r14")}
        rows[key] = {"round": question["round"], "reply": question["reply"], "leaves": leaves,
                     "signs": {"pv": pv_label, "pv_strict": pv_label if strict else None, **signs}}
    return {"pv": pv, "rows": rows}


def judge(binary, net, cohort):
    rows = {}
    with chess.engine.SimpleEngine.popen_uci(str(binary.resolve()), timeout=120) as engine:
        engine.configure({"Threads": 1, "Hash": 16, "EvalFile": str(net.resolve())})
        for key, question in cohort["questions"].items():
            rows[key] = {str(depth): [single(engine, board, mover, depth=depth)
                                      for board, mover in positions(question)] for depth in DEPTHS}
    return {"binary_sha256": BINARY, "net_sha256": NET, "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("predict", "judge"))
    parser.add_argument("binary", type=Path)
    parser.add_argument("cohort", type=Path)
    parser.add_argument("cohort_sha256")
    parser.add_argument("--net", type=Path)
    parser.add_argument("--forecast", type=Path)
    parser.add_argument("--forecast-sha256")
    args = parser.parse_args()
    logging.getLogger("chess.engine").setLevel(logging.ERROR)
    if digest(args.cohort) != args.cohort_sha256:
        raise ValueError("Cohort differs from the selection freeze")
    cohort = json.loads(args.cohort.read_text())
    if cohort["source_sha256"] != SOURCE or cohort["source_engine_sha256"] != SF or not cohort["questions"]:
        raise ValueError("Expected a nonempty pinned S28 cohort")
    if any(key != fingerprint(question) for key, question in cohort["questions"].items()):
        raise ValueError("Malformed question key")
    if args.stage == "predict":
        if digest(args.binary) != SF:
            raise ValueError("Unexpected Stockfish binary")
        result = {**predict(args.binary, cohort), "binary_sha256": SF}
    else:
        if (not args.net or digest(args.net) != NET or digest(args.binary) != BINARY
                or not args.forecast or digest(args.forecast) != args.forecast_sha256):
            raise ValueError("Judge environment or frozen forecasts did not match")
        predictions = json.loads(args.forecast.read_text())
        if (predictions["cohort_sha256"] != args.cohort_sha256 or predictions["binary_sha256"] != SF
                or predictions["rows"].keys() != cohort["questions"].keys()):
            raise ValueError("Forecast question or source mismatch")
        result = {**judge(args.binary, args.net, cohort), "forecast_sha256": args.forecast_sha256}
    print(json.dumps({**result, "cohort_sha256": args.cohort_sha256}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
