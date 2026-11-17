"""Freeze exact named-plan entries and judge their positional value independently."""

import argparse
import json
from pathlib import Path

import chess
import chess.engine

from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r11_allocation import NET, single
from c3x_030_s4l_r16_plan_oracle import solve
from c3x_030_s4l_r16_plan_source import post_reply, root_boards

GOALS = "745645505b89849b54ace84a30491b3f0af0ef632801a436990ca230d6632da0"
BINARY = "2d92b7eb89569045b6250345471a1320ba3010733a663d8bef75564563e045c7"
SOURCE = "8ae895a6151695be4a50d4fb65b0c131659c513a"
CASES = (("2.2", "h1g1", "h8g8"), ("2.2", "e1e2", "h8g8"), ("1.5", "e5g5", "a5a2"))


def leaves(goals):
    if digest(goals) != GOALS:
        raise ValueError("Unexpected R17 source")
    plans = {row["round"]: row for row in json.loads(goals.read_text())["plans"]}
    for round_id, root, reply in CASES:
        case = plans[round_id]
        branch = root_boards(case)[case["roots"].index(root)]
        board, target = post_reply(branch, reply, chess.parse_square(case["target"]))
        yield f"{round_id}/{root}/{reply}", board, target


def freeze(goals):
    rows = {}
    for label, board, target in leaves(goals):
        proof = solve(board, target, settle_final=True)
        rows[label] = {"fen": board.fen(), "target": chess.square_name(target),
                       "legal": list(proof), "admits": [move for move in proof if proof[move]["holds"]]}
    return {"goals_sha256": GOALS, "source_commit": SOURCE,
            "binary_sha256": BINARY, "net_sha256": NET, "leaves": rows}


def maximum(moves, scores):
    if not moves or any(scores[move]["point"] is None for move in moves):
        return None
    ordered = max(scores[move]["point"]["ordered"] for move in moves)
    best = [move for move in moves if scores[move]["point"]["ordered"] == ordered]
    return {"moves": best, "cp": scores[best[0]]["point"]["cp"], "ordered": ordered}


def evaluate(engine, goals, receipt):
    output = {}
    for label, board, _ in leaves(goals):
        specification = receipt["leaves"][label]
        legal, admits = specification["legal"], specification["admits"]
        rows = {}
        for depth in (10, 12):
            scores = {}
            for candidate in legal:
                child = board.copy()
                child.push_uci(candidate)
                scores[candidate] = single(engine, child, board.turn, depth=depth)
            open_max, admit_max = maximum(legal, scores), maximum(admits, scores)
            gap = (open_max["cp"] - admit_max["cp"] if open_max and admit_max
                   and open_max["cp"] is not None and admit_max["cp"] is not None else None)
            rows[str(depth)] = {"covered": sum(v["point"] is not None for v in scores.values()),
                                "open_max": open_max, "admit_max": admit_max, "gap_cp": gap,
                                "scores": scores}
        output[label] = rows
    return output



def root_screen(engine, goals):
    plans = {row["round"]: row for row in json.loads(goals.read_text())["plans"]}
    result = {}
    for round_id in ("2.2", "1.5"):
        plan = plans[round_id]
        pair = {}
        for move, board in zip(plan["roots"], root_boards(plan), strict=True):
            pair[move] = {str(depth): single(engine, board, not board.turn, depth=depth)
                          for depth in (10, 12)}
        result[round_id] = pair
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goals", type=Path)
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--net", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--root-screen", action="store_true")
    args = parser.parse_args()
    receipt = freeze(args.goals)
    if args.binary is None:
        print(json.dumps(receipt, indent=2))
        return
    if not args.receipt or json.loads(args.receipt.read_text()) != receipt:
        raise ValueError("Judge requires the frozen entry receipt")
    if not args.net or digest(args.net) != NET or digest(args.binary) != BINARY:
        raise ValueError("Unexpected judge binary or network")
    with chess.engine.SimpleEngine.popen_uci(str(args.binary.resolve())) as engine:
        engine.configure({"Threads": 1, "Hash": 16})
        values = (root_screen(engine, args.goals) if args.root_screen
                  else evaluate(engine, args.goals, receipt))
    print(json.dumps(values, indent=2))


if __name__ == "__main__":
    main()
