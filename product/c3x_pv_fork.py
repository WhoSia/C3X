"""Render a pair of public Stockfish continuations without conflating their scores."""

import argparse
import json
from pathlib import Path
import sys

import chess

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))

from c3x_030_s4l_r10_reply_transport import board_at, digest


def local_fact(board, moves):
    if moves == ["d2d4", "f1e1"]:
        pawn, rook = board.copy(), board.copy()
        pawn.push_uci(moves[0])
        rook.push_uci(moves[1])
        if (pawn.piece_at(chess.E5) == chess.Piece(chess.PAWN, chess.BLACK)
                and chess.E5 in pawn.attacks(chess.D4)
                and rook.piece_at(chess.E4) == chess.Piece(chess.KNIGHT, chess.BLACK)
                and chess.E4 in rook.attacks(chess.E1)):
            return "d4는 e5의 흑 폰을 공격하고, Re1은 e4의 흑 나이트를 공격해."
    if moves == ["d6h2", "d6e7"]:
        checked, quiet = (board.gives_check(board.parse_uci(move)) for move in moves)
        if checked and not quiet:
            return "…Bh2+는 체크를 걸어 백에게 즉시 대응을 요구해. …Be7 뒤에는 백이 체크 상태에 놓이지 않아."
    return None


def render(case, freeze, replay):
    a, b = freeze["reports"]
    root = board_at(case["history"])
    fork = freeze["pair"]
    pivot = board_at([*case["history"], *a["pv"][:fork["first_divergence_ply"] - 1]])
    rec = root.san(root.parse_uci(a["move"]))
    moves = [pivot.san(pivot.parse_uci(move)) for move in fork["moves"]]
    lines = [f"# {rec} 이후의 서로 다른 두 수순", "",
             f"시작 FEN `{root.fen()}`", "",
             f"두 실행의 추천 수는 **{rec}**, 표시 평가는 **{a['cp']:+d}cp**였어.",
             "", "| Stockfish 관측 | GUI에 보고한 주요 수순 | 내부값 |",
             "| --- | --- | ---: |"]
    for row in (a, b):
        san = root.variation_san([chess.Move.from_uci(uci) for uci in row["pv"]])
        lines.append(f"| 깊이 {row['depth']} | `{san}` | {row['native']} |")
    chooser = "백" if fork["chooser"] == "white" else "흑"
    lines.extend(["", f"{fork['first_divergence_ply']}번째 반수에서 {chooser} 수가 "
                  f"**{moves[0]} / {moves[1]}**로 갈렸어."])
    fact = local_fact(pivot, fork["moves"])
    if fact:
        lines.append(fact)
    reproduced = sum(all(row[key] for key in ("same_recommendation", "same_score", "same_native", "same_fork_prefix"))
                     for row in replay["reruns"].values())
    lines.append(f"고정 깊이와 노드 제한으로 분리한 재실행에서 {reproduced}/{len(replay['reruns'])}회 재현했어.")
    independent = replay.get("independent")
    if independent:
        if independent["fen"] != pivot.fen() or independent["chooser"] != fork["chooser"]:
            raise ValueError("Referee read a different fork position")
        lines.extend(["", f"같은 분기점에서 두 수를 각각 고정한 Berserk 평가도 비교했어. 점수는 {chooser} 기준이야.",
                      "", "| 분기 수 | 깊이 12 | 깊이 14 |", "| --- | ---: | ---: |"])
        for uci, label in zip(fork["moves"], moves, strict=True):
            values = [independent["forced_moves"][uci][str(d)] for d in (12, 14)]
            scores = [f"{v['cp']:+d}cp" if v and v["cp"] is not None else "보류" for v in values]
            lines.append(f"| {label} | {scores[0]} | {scores[1]} |")
    lines.extend(["", "표시 점수는 추천 수와 함께 나온 값이야. 여기서 달라진 건 엔진이 보여 준 후속 수순이야.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cases", "freeze", "replay"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    cases, freeze, replay = (json.loads(path.read_text()) for path in (args.cases, args.freeze, args.replay))
    if digest(args.cases) != freeze["case_sha256"] or digest(args.freeze) != replay["freeze_sha256"]:
        raise ValueError("Mismatched case, fork or replays")
    case = next(row for row in cases["cases"] if row["id"] == freeze["case"])
    print(render(case, freeze, replay), end="")


if __name__ == "__main__":
    main()
