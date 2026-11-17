"""Freeze the first strict continuation fork and test operational reproduction."""

import argparse
import json
from pathlib import Path

import chess.engine

from c3x_030_r20_p40_value import BINARY
from c3x_030_r22_bd2 import run as judge_move
from c3x_030_r24_pv_stability import CASES, check_inputs, validated_search
from c3x_030_s4l_r10_reply_transport import board_at, digest
from c3x_030_s4l_r11_allocation import NET


def nominate(cases, sampled, native=True):
    for case in cases:
        item = sampled[case["id"]]
        pairs = [pair for pair in item["trajectory_pairs"]
                 if pair["kind"] == "divergent" and (pair["native_equal"] or not native)
                 and 2 <= pair["first_divergence_ply"] <= 5]
        if not pairs:
            continue
        first = min(pairs, key=lambda pair: tuple(reversed(pair["indices"])))
        rows = [item["continuous"]["reports"][i] for i in first["indices"]]
        return {"case": case["id"], "pair": first, "reports": rows}
    raise ValueError("No eligible equal-native continuation fork")


def select_report(run):
    final = run["reports"][-1]
    if (final["move"], final["producer"]) != (run["bestmove"], run["best_producer"]):
        return None
    return final


def evaluate(clean, trace, net, case, selected, output):
    index = selected["pair"]["first_divergence_ply"] - 1
    result = {}
    for i, expected in enumerate(selected["reports"]):
        for spec in ({"depth": expected["depth"]}, {"nodes": expected["nodes"] + 1}):
            mode = next(iter(spec))
            label = f"arm-{i}-{mode}"
            actual = validated_search(clean, trace, net, case, output / label, **spec)
            report = select_report(actual)
            result[label] = {
                "search": actual, "final_report": report,
                "same_recommendation": actual["bestmove"] == expected["move"],
                "same_score": bool(report and report["eligible"] and report["cp"] == expected["cp"]),
                "same_native": bool(report and report["eligible"] and report["native"] == expected["native"]),
                "same_fork_prefix": bool(report and len(report["pv"]) > index
                                         and report["pv"][:index + 1] == expected["pv"][:index + 1]),
            }
    return result


def independent(case, spec, binary, net):
    if not net or (digest(binary), digest(net)) != (BINARY, NET):
        raise ValueError("Unexpected independent judge")
    fork = spec["pair"]
    pv = spec["reports"][0]["pv"]
    board = board_at([*case["history"], *pv[:fork["first_divergence_ply"] - 1]])
    result = {}
    with chess.engine.SimpleEngine.popen_uci(str(binary.resolve()), timeout=120) as engine:
        engine.configure({"Threads": 1, "Hash": 16, "EvalFile": str(net.resolve())})
        for uci in fork["moves"]:
            move = board.parse_uci(uci)
            result[uci] = {str(d): judge_move(engine, board, d, [move]) for d in (12, 14)}
    return {"fen": board.fen(), "chooser": fork["chooser"], "forced_moves": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cases", "sampled", "clean", "trace", "net"):
        parser.add_argument(name, type=Path)
    for name in ("freeze", "output", "judge", "judge-net"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--match", choices=("native", "displayed"), default="native")
    parser.add_argument("--case-sha", default=CASES)
    args = parser.parse_args()
    check_inputs(args.cases, args.clean, args.trace, args.net, case_sha=args.case_sha)
    cases = json.loads(args.cases.read_text())["cases"]
    selected = {**nominate(cases, json.loads(args.sampled.read_text()), args.match == "native"),
                "sample_sha256": digest(args.sampled), "case_sha256": args.case_sha, "match": args.match}
    if args.freeze:
        if json.loads(args.freeze.read_text()) != selected or not args.output:
            raise ValueError("Wrong frozen fork or missing output path")
        case = next(case for case in cases if case["id"] == selected["case"])
        rescored = independent(case, selected, args.judge, args.judge_net) if args.judge else None
        selected = {"freeze_sha256": digest(args.freeze),
                    "reruns": evaluate(args.clean, args.trace, args.net, case, selected, args.output),
                    "independent": rescored}
    print(json.dumps(selected, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
