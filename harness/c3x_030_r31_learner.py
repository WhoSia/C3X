"""Extend the Nd7/a4 pilot with matched native and public-evidence panels."""
import argparse
from html import escape
import json
from pathlib import Path

import chess

from c3x_030_r23_native_replay import RECEIPT, digest
from c3x_030_r29_learner import lesson, trace_text
from c3x_030_r29_local_tt_move import CASE

BASE = "14c55e4c4cafb1061d4570ef3f9229f8d6cfd9c0ed1a5f0e92dc91495b12aefc"
SOURCE = "f1987f3f3d82ad5a68aefb9062c8e661f582c790791de78244912643f9178323"
PUBLIC = "eadeea7668f314ca722cce9a159dc9301baf635408b80d5cc4f16044075b4178"

NATIVE_PANEL = (
    "Stockfish가 …Nd7을 앞세운 뒤 …a4를 확인했어. "
    "그때 저장해 둔 값으로 …a4의 확인을 끝냈어. "
    "그 값만 가리고 다시 탐색해도 …Nd7 추천은 유지됐어."
)
PUBLIC_PANEL = (
    "Stockfish는 깊이 9와 10에서 …a4를 앞세웠어. "
    "깊이 11에서는 …Nd7을 첫 수로 보고했어. "
    "그 뒤 깊이를 더 늘렸을 때도 …Nd7 추천은 유지됐어."
)


def check_public(lines):
    reports = [(int(m[1]), m[6]) for line in lines if (m := RECEIPT.match(line))]
    tail = [(9, "a5a4"), (10, "a5a4")] + [(depth, "f6d7") for depth in range(11, 16)]
    if [row for row in reports if row[0] >= 9] != tail:
        raise ValueError("Public lesson text disagrees with the iteration history")
    if [line.split()[1] for line in lines if line.startswith("bestmove ")] != ["f6d7"]:
        raise ValueError("Public lesson final move disagrees with the log")


def build(cohort, proof_file, uci, assessment, output):
    if (digest(proof_file), digest(uci), digest(assessment)) != (SOURCE, PUBLIC, BASE):
        raise ValueError("Unexpected archived R29 inputs")
    proof = json.loads(proof_file.read_text())
    if digest(cohort) != proof["frozen"]["assets"]["cohort"] or proof["frozen"]["case"] != CASE:
        raise ValueError("Lesson history and proof mismatch")
    selected, = (case for case in json.loads(cohort.read_text())["positions"] if case["id"] == CASE)
    board = chess.Board()
    for move in selected["moves"]:
        board.push_uci(move)
    trace_text(proof)
    if proof["frozen"]["target"]["attempt"] != proof["frozen"]["original_producer"]["attempt"]:
        raise ValueError("The cutoff was not in the recommendation-producing attempt")
    check_public(uci.read_text().splitlines())

    panels = {"C": NATIVE_PANEL, "D": PUBLIC_PANEL}
    native, public = panels.values()
    if abs(len(native) - len(public)) > max(len(native), len(public)) / 10:
        raise ValueError("Panel length mismatch")
    if abs(len(native.split()) - len(public.split())) > 2:
        raise ValueError("Word-count mismatch")

    minimal = lesson(board.fen(), "A", proof)
    board_only = lesson(board.fen(), "B", proof)
    close = "</section></details>"
    if board_only.count(close) != 1:
        raise ValueError("Ambiguous lesson insertion point")
    for condition, body in {"A": minimal, "B": board_only, **{arm: board_only.replace(
            close, "<aside>" + escape(text) + "</aside>" + close) for arm, text in panels.items()}}.items():
        dest = output / condition
        dest.mkdir(parents=True)
        (dest / "lesson.html").write_text(body, encoding="utf-8")
        (dest / "assessment.html").write_bytes(assessment.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("cohort", "proof", "uci", "assessment", "output"):
        parser.add_argument(field, type=Path)
    args = parser.parse_args()
    build(args.cohort, args.proof, args.uci, args.assessment, args.output)


if __name__ == "__main__":
    main()
