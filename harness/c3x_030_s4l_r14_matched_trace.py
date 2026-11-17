"""Freeze same-search public and source-root forecasts, then independently judge."""

import argparse
import json
import logging
from pathlib import Path

import chess.engine

from c3x_030_s4l_r10_reply_transport import analysis, board_at, digest, selection
from c3x_030_s4l_r11_allocation import BERSERK, NET, SF, receipt, single
from c3x_030_s4l_r12_reply_questions import freeze
from c3x_030_s4l_r14_trace_projection import pair_signs, projections


LEAGUE_1 = "1c06ef681343b833d2b76e7b89d3f7b669d916f8e714a084e2bb01ba84d19899"
EXCLUDED = (
    "b81c2b31e733d4f151cbe068be3a98e79724a472c34ec14ce7f6f92e0a27983a",
    "ed72a8d3ec09560f355fac5f21e31f973c8b7b043068742b9007e74eb6283136",
)
OPTIONS = {"Threads": 1, "Hash": 16, "Use NNUE": False}
BUDGET = 12000


class RecordedUci(chess.engine.UciProtocol):
    def __init__(self):
        super().__init__()
        self.stdout = []
        self.stderr = []

    def line_received(self, line):
        self.stdout.append(line)

    def error_line_received(self, line):
        self.stderr.append(line)


def positions(question):
    board = board_at(question["history"])
    for move in question["roots"]:
        branch = board.copy()
        branch.push_uci(move)
        branch.push_uci(question["reply"])
        yield branch, board.turn


def nominate(engine_path, pgn, excluded):
    if tuple(map(digest, excluded)) != EXCLUDED:
        raise ValueError("Expected the frozen R10 and R11 cohort bytes in order")
    openings = [
        tuple(case["history"][:12])
        for path in excluded for case in json.loads(path.read_text())["selection"]
    ]
    requests, discovery_rows = [], {}
    with chess.engine.SimpleEngine.popen_uci(str(engine_path.resolve()), timeout=45) as engine:
        engine.configure(OPTIONS)
        cohort = selection(engine, pgn, excluded_openings=openings, expected_sha=LEAGUE_1)
        for case in cohort["selection"]:
            board = board_at(case["history"])
            first, second = board.copy(), board.copy()
            first.push_uci(case["roots"][0])
            second.push_uci(case["roots"][1])
            discovered = analysis(engine, first, board.turn, nodes=BUDGET, count=3)
            discovery_rows[case["round"]] = discovered
            for report in discovered:
                reply = report["pv"][0]
                if chess.Move.from_uci(reply) in second.legal_moves:
                    request = {"round": case["round"], "reply": reply}
                    if not any(leaf.is_game_over(claim_draw=False)
                               for leaf, _ in positions({**case, **request})):
                        requests.append(request)
                    break
    return {"cohort": cohort, "discovery": discovery_rows, "questions": freeze(cohort, requests)}


def leaf_forecast(path, leaf, mover):
    reports = []
    with chess.engine.SimpleEngine.popen(RecordedUci, str(path.resolve()), timeout=45) as engine:
        engine.configure(OPTIONS)
        with engine.analysis(leaf, chess.engine.Limit(nodes=BUDGET), game=object()) as stream:
            for info in stream:
                value = receipt(info, mover, leaf)
                if value is not None:
                    reports.append(value)
            result = stream.wait()
        engine.quit()
        stdout, stderr = engine.protocol.stdout, engine.protocol.stderr
    if result.move not in leaf.legal_moves or not reports:
        raise ValueError("No legal leaf receipt")
    return {
        **projections(reports, stderr, leaf.turn == mover),
        "stdout": stdout, "stderr": stderr,
        "nodes": reports[-1]["nodes"], "leaf_fen": leaf.fen(), "public_reports": reports,
    }


def forecast(path, questions_file):
    questions = json.loads(questions_file.read_text())["questions"]
    rows = {}
    for key, question in questions.items():
        points = [leaf_forecast(path, leaf, mover) for leaf, mover in positions(question)]
        rows[key] = {"points": points, "signs": pair_signs(points)}
    return {"questions_sha256": digest(questions_file), "engine_sha256": digest(path),
            "requested_nodes_per_leaf": BUDGET, "rows": rows}


def reference(path, net, questions_file, depth):
    questions = json.loads(questions_file.read_text())["questions"]
    results = {}
    with chess.engine.SimpleEngine.popen_uci(str(path.resolve()), timeout=90) as engine:
        engine.configure({"Threads": 1, "Hash": 16, "EvalFile": str(net.resolve())})
        for key, question in questions.items():
            results[key] = [single(engine, leaf, mover, depth=depth)
                            for leaf, mover in positions(question)]
    return {"questions_sha256": digest(questions_file), "engine_sha256": digest(path),
            "net_sha256": digest(net), "depth": depth, "rows": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="stage", required=True)
    select = subparsers.add_parser("select")
    select.add_argument("engine", type=Path)
    select.add_argument("pgn", type=Path)
    select.add_argument("excluded", nargs=2, type=Path)
    for stage in ("predict", "judge"):
        child = subparsers.add_parser(stage)
        child.add_argument("engine", type=Path)
        child.add_argument("questions", type=Path)
        if stage == "judge":
            child.add_argument("net", type=Path)
            child.add_argument("depth", type=int, choices=(16, 18))
    args = parser.parse_args()
    logging.getLogger("chess.engine").setLevel(logging.ERROR)
    if args.stage == "judge":
        if digest(args.engine) != BERSERK or digest(args.net) != NET:
            parser.error("Expected the pinned R11 judge and network")
        result = reference(args.engine, args.net, args.questions, args.depth)
    else:
        if digest(args.engine) != SF:
            parser.error("Expected the pinned R4 Stockfish")
        result = (nominate(args.engine, args.pgn, args.excluded) if args.stage == "select"
                  else forecast(args.engine, args.questions))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
