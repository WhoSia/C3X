"""Render a verified Stockfish root choice and a bounded legal board explanation."""

import argparse
import json
from pathlib import Path
import sys

import chess

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))

from c3x_030_r23_native_replay import CASES, join, records, source_result
from c3x_030_s4l_r10_reply_transport import board_at, digest


def san(board, uci):
    return board.san(board.parse_uci(uci))


def board_observation(case_id, root, pv):
    """Attach only propositions whose relevant moves occur and can be replayed."""
    board = root.copy()
    if case_id == "r21" and pv[:3] == ["c1d2", "b8b2", "c3d1"]:
        text = board.variation_san([board.parse_uci(pv[0])])
        for move in pv[:3]:
            board.push_uci(move)
        if board.piece_at(chess.B2) != chess.Piece(chess.ROOK, chess.BLACK):
            raise ValueError("Unexpected target on b2")
        if board.piece_at(chess.D1) != chess.Piece(chess.KNIGHT, chess.WHITE) or chess.B2 not in board.attacks(chess.D1):
            raise ValueError("The stated knight attack did not occur")
        return f"{text} 뒤 공개 PV에서 흑은 …Rxb2로 폰을 잡았어. 백의 Nd1은 b2의 흑 룩을 공격해."
    if case_id == "r22" and pv[:2] == ["f1e1", "h8e8"]:
        board.push_uci(pv[0])
        if (board.piece_at(chess.E5) != chess.Piece(chess.PAWN, chess.BLACK)
                or chess.E1 not in board.attackers(chess.WHITE, chess.E5)):
            raise ValueError("The stated rook attack did not occur")
        board.push_uci(pv[1])
        if chess.E8 not in board.attackers(chess.BLACK, chess.E5):
            raise ValueError("The stated defensive rook ray did not occur")
        return "Rfe1은 e5의 흑 폰을 공격해. 공개 PV의 …Rhe8은 e8의 룩으로 같은 폰을 지켜."
    return None


def render(case, stdout, stderr):
    board = board_at(case["history"])
    proof = join(stdout, stderr)
    source, attempt, end = (proof[key] for key in ("best_source", "best_attempt", "best_attempt_end"))
    if source is None:
        raise ValueError("No recorded producer for the final move")
    last = proof["reports"][-1]
    public = last["public"]
    if last["source"] != source:
        raise ValueError("The last score and selected move came from different producers")
    if int(attempt["roots"]) != board.legal_moves.count():
        raise ValueError("Full-legal root receipt required")
    move = san(board, source["move"])
    chosen_depth = last["public"]["depth"]
    rawline = next(line for line in reversed(stdout) if " pv " in line)
    pv = rawline.split(" pv ", 1)[1].split()
    copy = board.copy()
    for uci in pv:
        copy.push_uci(uci)
    line = board.variation_san([chess.Move.from_uci(uci) for uci in pv[:4]])
    value, relation = source_result(source)
    qualifier = {"none": "", "upper": " 이하", "lower": " 이상"}[public["bound"]]
    lines = [f"# Stockfish의 선택 · {move}", "",
             "Stockfish 16 · 기본 NNUE · 전체 합법수 · 24,000노드 요청", "",
             f"FEN `{board.fen()}`", "",
             f"최종 선택은 **{move}**, 마지막 UCI 평가는 **{int(public['score']):+d} "
             f"{public['kind']}{qualifier}**였어. 화면에 표시된 깊이는 {chosen_depth}, "
             f"이 점수를 만든 호출의 반복 깊이는 {attempt['iteration']}이었어.", "",
             f"공개 주요 수순은 `{line}`이야.", "",
             "## 선두 후보를 기록한 호출", ""]
    all_candidates = records(stderr, "CANDIDATE")
    if relation == "none":
        lines.append(f"호출 {attempt['attempt']}에서 {move}의 반환값은 {source['value']}였어. 당시 기준 "
                     f"{source['alpha']}보다 크고 상한 {source['beta']}보다 작았기 때문에 "
                     f"이 값이 교체된 선두의 점수로 기록됐어.")
        prior = next((row for row in reversed(all_candidates)
                      if row["attempt"] == attempt["attempt"] and row["update"] == "1"
                      and int(row["id"]) < int(source["id"])), None)
        if prior:
            prior_move = san(board, prior["move"])
            lines.append(f"같은 호출에서 {prior_move}가 먼저 기록됐고, 이후 {move}가 선두를 넘겨받았어.")
    else:
        lines.append(f"호출 {attempt['attempt']}에서 {move}의 반환값은 {source['value']}였어. "
                     f"당시 창의 경계가 {value}여서 엔진은 이 값을 공개했어. "
                     "출력에는 경계 표시가 함께 붙었어.")
    if public["sink_attempt"] != attempt["attempt"]:
        stopped = next(row for row in records(stderr, "END") if row["attempt"] == public["sink_attempt"])
        if stopped["stopped"] == "1":
            lines.append(f"호출 {stopped['attempt']}에서 노드 한도에 도달해 탐색이 중단됐어. "
                         f"최종 출력에는 호출 {attempt['attempt']}의 점수와 수가 남았어.")
    candidates = {row["move"]: row for row in all_candidates
                  if row["attempt"] == end["attempt"]}
    lines.extend(["", "| 기존 비교 후보 | 반환값 | 당시 α | 후보 기록 |",
                  "| --- | ---: | ---: | --- |"])
    for root in case["roots"]:
        row = candidates.get(root)
        if row:
            status = ("첫 후보" if row["count"] == "1" else
                      "선두 갱신" if row["update"] == "1" else "선두 유지")
            lines.append(f"| {san(board, root)} | {row['value']} | {row['alpha']} | {status} |")
    lines.extend(["", "반환값과 갱신 기준은 엔진 내부 단위이고, 후보별 탐색 깊이는 달라질 수 있어.", "",
                  "## 보드에서 확인할 수 있는 것", ""])
    observed = board_observation(case["id"], board, pv)
    lines.append(observed or "이 수순에는 검증된 보드 설명이 아직 없어.")
    lines.extend(["", "위의 공격과 수비는 보드 규칙으로 확인한 사실이야. NNUE가 그 특징에 "
                  "얼마나 의존했는지는 별도의 개입으로 확인할 문제야.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", type=Path)
    parser.add_argument("case", choices=("r21", "r22"))
    parser.add_argument("search", type=Path, help="Directory with the full-legal 24k NNUE stdout/stderr")
    args = parser.parse_args()
    if digest(args.cases) != CASES:
        raise ValueError("Unexpected frozen case list")
    case = next(row for row in json.loads(args.cases.read_text())["cases"] if row["id"] == args.case)
    stdout, stderr = ((args.search / f"{name}.txt").read_text().splitlines()
                      for name in ("stdout", "stderr"))
    print(render(case, stdout, stderr), end="")


if __name__ == "__main__":
    main()
