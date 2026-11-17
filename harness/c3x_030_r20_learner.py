"""Generate and score the R20 Korean pilot with an exact move-based answer key."""

import argparse
import json
from pathlib import Path

import chess

from c3x_030_s4l_r10_reply_transport import board_at, digest
from c3x_030_s4l_r16_plan_oracle import solve
from c3x_030_s4l_r16_plan_source import post_reply
from c3x_030_r20_p40_value import GOALS

EXAMPLE = ("2.2", ("h1g1", "e1e2"), ("h8g8", "a8a7"))
TRANSFER = ("2.1", ("f1c1", "d3b5"), ("c5c4", "a8c8"))
INTRO = """백의 후보 수와 흑의 응수를 한 번씩 둔 뒤 시작해. 백은 자기 차례 두 번 안에
처음 지정한 흑 기물을 잡아야 해. 흑은 매 차례 합법수 중 어느 것이든 둘 수 있어.
백이 기물을 잡은 뒤 흑의 마지막 응수까지 끝났을 때, 백의 기물 점수에서 흑의
기물 점수를 뺀 값이 시작할 때보다 낮아지면 실패야. 폰·나이트·비숍·룩·퀸은
각각 1·3·3·5·9점이야. 시작할 때는 표에 적힌 두 수를 이미 둔 상태야.
"""
EXPLANATION = """백이 Rg1을 두고 흑이 …Rg8로 응수하면, 처음 h8에 있던 흑 룩이 g8로 이동해.
여기서 백은 Nd6+로 체크할 수 있어. 흑의 합법적 응수는 …Kd8, …Ke7,
…Qxd6 세 가지이고, 어느 경우에도 백의 Rxg8이 그 룩을 잡아.
흑의 마지막 응수까지 고려해도 기물 점수 차는 시작값 이상이야. 백이 대신 Qa4를
두면 흑의 …b5가 반례야. 백은 남은 한 번의 차례에 조건을 충족할 수 없어.
"""


def case_grid(goals, specification, prefix):
    round_id, roots, replies = specification
    plan = goals[round_id]
    if set(roots) != set(plan["roots"]) or not set(replies) <= set(plan["replies"]):
        raise ValueError("Pilot grid differs from the exposed case")
    board = board_at(plan["history"])
    target = chess.parse_square(plan["target"])
    cells = []
    for root in roots:
        move = board.parse_uci(root)
        root_san = board.san(move)
        branch = board.copy()
        branch.push(move)
        for reply in replies:
            reply_san = branch.san(branch.parse_uci(reply))
            leaf, victim = post_reply(branch, reply, target)
            proof = solve(leaf, victim, settle_final=True)
            cells.append({"id": f"{prefix}{len(cells) + 1}", "root": root_san,
                          "reply": reply_san, "fen": leaf.fen(), "proof": proof})
    return board.fen(), plan["target"], cells


def witnesses(cell):
    return [move for move, row in cell["proof"].items() if row["holds"]]


def verify_example(cells):
    proof = cells[0]["proof"]
    expected_finishes = {"e8d8": "g1g8", "e8e7": "g1g8", "f8d6": "g1g8"}
    if proof["c4d6"] != {"holds": True, "finishes": expected_finishes}:
        raise ValueError("Worked explanation does not match the exhaustive witness")
    if proof["d1a4"] != {"holds": False, "refuting_defense": "b7b5"}:
        raise ValueError("Worked refutation does not match the oracle")
    if [bool(witnesses(cell)) for cell in cells] != [True, False, False, False]:
        raise ValueError("Unexpected worked verdicts")


def section(title, fen, target, cells, reveal):
    rows = [f"## {title}", "", f"시작 FEN `{fen}`", "", f"처음 지정한 흑 기물의 칸은 **{target}**이야.",
            "", "| 문항 | 백 후보 | 흑 응수 | 두 수를 둔 뒤 FEN | 답 |",
            "| --- | --- | --- | --- | --- |"]
    for cell in cells:
        verdict = ("가능" if witnesses(cell) else "불가능") if reveal else ""
        rows.append(f"| {cell['id']} | {cell['root']} | {cell['reply']} | `{cell['fen']}` | {verdict} |")
    return "\n".join(rows)


def render(example, transfer, explanation):
    extras = f"\n\n{EXPLANATION.rstrip()}" if explanation else ""
    return (f"# 백이 흑의 특정 기물을 잡을 수 있을까\n\n{INTRO}\n"
            f"{section('연습 예제', *example, True)}{extras}\n\n"
            f"{section('평가 문제', *transfer, False)}\n\n"
            "평가 시간은 8분이야. 각 문항에 가능·불가능·모르겠음 중 하나를 적어 줘.\n"
            "가능이라고 답한 문항에는 백이 먼저 둘 수 한 개도 적어 줘.\n")


def score(cells, responses):
    valid_ids = {cell["id"] for cell in cells}
    if not isinstance(responses, dict) or set(responses) - valid_ids:
        raise ValueError("Unexpected response item")
    scores = {}
    for cell in cells:
        ident = cell["id"]
        response = responses.get(ident, {"answer": "abstain"})
        verdict = response["answer"]
        if verdict not in {"yes", "no", "abstain"}:
            raise ValueError(f"Unexpected answer at {ident}")
        entry = response.get("entry", "").strip()
        moves = witnesses(cell)
        valid = None
        if verdict == "yes":
            board = chess.Board(cell["fen"])
            try:
                move = board.parse_san(entry)
            except ValueError:
                valid = False
            else:
                valid = move.uci() in moves
        scores[ident] = {"answer": verdict,
                         "verdict_correct": None if verdict == "abstain" else ((verdict == "yes") == bool(moves)),
                         "entry_valid": valid}
    return scores


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goals", type=Path)
    parser.add_argument("mode", choices=("comparison", "explanation", "key", "score"))
    parser.add_argument("--responses", type=Path)
    args = parser.parse_args()
    if digest(args.goals) != GOALS:
        raise ValueError("Unexpected R17 goals")
    goals = {row["round"]: row for row in json.loads(args.goals.read_text())["plans"]}
    example, transfer = case_grid(goals, EXAMPLE, "E"), case_grid(goals, TRANSFER, "T")
    verify_example(example[2])
    if args.mode == "key":
        print(json.dumps({cell["id"]: witnesses(cell) for cell in transfer[2]}, indent=2))
    elif args.mode == "score":
        if args.responses is None:
            parser.error("score requires --responses")
        print(json.dumps(score(transfer[2], json.loads(args.responses.read_text())), indent=2))
    else:
        print(render(example, transfer, args.mode == "explanation"), end="")


if __name__ == "__main__":
    main()
