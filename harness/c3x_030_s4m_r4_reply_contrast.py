"""Replay queen promotions after each legal reply to the R3 candidate moves."""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.syzygy

from c3x_030_s4m_r3_kpkp import CASES, TABLE_SHA256

TABLES = {
    **TABLE_SHA256,
    "KQvKP.rtbw": "2f92788170e8a5c05608f44a47fd42f3f4fff372d0af64633c56bd081039d8f9",
    "KQvK.rtbw": "45c453e5113a714bd4ece1cb5ba78cf5d21dd8b06f89708675d164fbe9bd3b53",
}


def inspect_replies(tablebase, fen, candidate):
    board = chess.Board(fen)
    if not board.is_valid() or board.turn != chess.WHITE:
        raise ValueError("Expected a legal White-to-move study position")
    board.push_san(candidate)
    rows = {}
    for reply in sorted(board.legal_moves, key=chess.Move.uci):
        reply_san = board.san(reply)
        board.push(reply)
        before = tablebase.probe_wdl(board)
        promotion, = (move for move in board.legal_moves if move.promotion == chess.QUEEN)
        promotion_san = board.san(promotion)
        board.push(promotion)
        after = -tablebase.probe_wdl(board)
        defenses = {}
        queen_captures = []
        for defense in sorted(board.legal_moves, key=chess.Move.uci):
            san = board.san(defense)
            if defense.to_square == promotion.to_square and board.is_capture(defense):
                queen_captures.append(san)
            board.push(defense)
            defenses[san] = tablebase.probe_wdl(board)
            board.pop()
        if not defenses or min(defenses.values()) != after:
            raise ValueError(f"Promotion/reply WDL mismatch after {reply_san}")
        rows[reply_san] = {
            "white_wdl_before_promotion": before,
            "queen_promotion": promotion_san,
            "gives_check": board.is_check(),
            "white_wdl_after_promotion": after,
            "immediate_queen_captures": queen_captures,
            "black_replies_white_wdl": defenses,
        }
        board.pop()
        board.pop()
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    for name, expected in TABLES.items():
        actual = hashlib.sha256((args.tables / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Table SHA-256 mismatch: {name}")
    with chess.syzygy.open_tablebase(str(args.tables)) as tablebase:
        cases = {name: inspect_replies(tablebase, *fixture) for name, fixture in CASES.items()}
    reti = cases["reti_1921"]
    barth = cases["barth_1995_position_x"]
    assert reti["Kb7"]["immediate_queen_captures"] == ["Kxc8"]
    assert reti["Kb7"]["black_replies_white_wdl"]["Kxc8"] == -2
    assert reti["h4"]["gives_check"] and reti["h4"]["white_wdl_after_promotion"] == 2
    assert barth["f4"]["immediate_queen_captures"] == []
    assert {san for san, wdl in barth["f4"]["black_replies_white_wdl"].items() if wdl == 0} == {"f3"}
    rows = [row for case in cases.values() for row in case.values()]
    assert len(rows) == 12
    assert all(row["white_wdl_before_promotion"] == row["white_wdl_after_promotion"] for row in rows)
    check_vs_win = {
        "check_and_win": sum(row["gives_check"] and row["white_wdl_after_promotion"] == 2 for row in rows),
        "check_and_nonwin": sum(row["gives_check"] and row["white_wdl_after_promotion"] != 2 for row in rows),
        "no_check_and_win": sum(not row["gives_check"] and row["white_wdl_after_promotion"] == 2 for row in rows),
        "no_check_and_nonwin": sum(not row["gives_check"] and row["white_wdl_after_promotion"] != 2 for row in rows),
    }
    assert check_vs_win == {"check_and_win": 3, "check_and_nonwin": 1,
                            "no_check_and_win": 7, "no_check_and_nonwin": 1}
    report = {"tables_sha256": TABLES, "cases": cases, "check_vs_win": check_vs_win}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Verified 12 promotions and", sum(len(row["black_replies_white_wdl"]) for row in rows),
          "legal post-promotion replies")


if __name__ == "__main__":
    main()
