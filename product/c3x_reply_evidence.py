"""Render a reply-sensitive two-move briefing from a frozen C3X menu evaluation."""

import argparse
import json
from pathlib import Path

import chess


def legal_san(board, uci):
    return board.san(board.parse_uci(uci))


def shared_san(boards, move):
    left, right = (legal_san(board, move) for board in boards)
    return left if left == right else f"{left} / {right}"


def display(case, finding):
    board = chess.Board()
    for move in case["history"]:
        board.push_uci(move)
    if case["roots"] != finding["roots"] or case["discovery"]["menus"] != finding["menus"]:
        raise ValueError("Score and legal case do not describe the same menus")
    branches = [board.copy() for _ in case["roots"]]
    root_sans = [legal_san(board, move) for move in case["roots"]]
    for after, move in zip(branches, case["roots"], strict=True):
        after.push_uci(move)
    lines = [f"# {root_sans[0]}과 {root_sans[1]} 비교", "",
             f"FEN `{board.fen()}`", "",
             (f"Stockfish가 두 후보만 따로 탐색했을 때 {root_sans[0]}의 우세는 "
              f"24k에서 {case['gaps'][0]}cp, 48k에서 {case['gaps'][1]}cp였어."), "",
             f"공통 흑 응수 {finding['common_count']}개의 Berserk 최소 평가를 비교했어.", "",
             "| 깊이 | 후보 | 후보의 가장 불리한 응수 | 최소 평가(cp) |",
             "| --- | --- | --- | ---: |"]
    for depth, row in sorted(finding["depths"].items()):
        for root, after, point in zip(root_sans, branches, row["minima"], strict=True):
            moves = ", ".join(legal_san(after, move) for move in point["moves"]) if point else "보류"
            value = f"{point['cp']:+d}" if point else "—"
            lines.append(f"| {depth} | {root} | {moves} | {value} |")
    lines += ["", "세 응수만 골랐을 때 최악의 응수를 얼마나 놓쳤는지도 볼 수 있어. "
              "누락 오차는 제한된 목록의 최소 평가에서 전체 공통 응수의 최소 평가를 뺀 값이야. "
              f"각 셀의 왼쪽은 {root_sans[0]}, 오른쪽은 {root_sans[1]}에 해당해.",
              "", "| 선택 방식 | 포함한 흑 응수 | 깊이 12 누락 오차 | 깊이 14 누락 오차 |",
              "| --- | --- | --- | --- |"]
    labels = {"lead_pv": "선두 후보의 엔진 순위", "opponent_pv": "다른 후보의 엔진 순위",
              "mixed": "두 후보의 순위와 전술 응수"}
    for policy, menu in finding["menus"].items():
        moves = ", ".join(shared_san(branches, move) for move in menu)
        gaps = []
        for depth in ("12", "14"):
            regret = finding["depths"][depth]["policies"][policy]["regret_cp"]
            gaps.append(" / ".join("—" if value is None else str(value) for value in regret))
        lines.append(f"| {labels[policy]} | {moves} | {gaps[0]} | {gaps[1]} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("selection", type=Path)
    parser.add_argument("score", type=Path)
    parser.add_argument("round")
    args = parser.parse_args()
    selection, score = (json.loads(path.read_text()) for path in (args.selection, args.score))
    if selection["cohort"] != score["cohort"]:
        raise ValueError("Mismatched cohorts")
    case = next(row for row in selection["selection"] if row["round"] == args.round)
    print(display(case, score["rows"][args.round]), end="")


if __name__ == "__main__":
    main()
