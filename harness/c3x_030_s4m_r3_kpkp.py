"""Compare a pawn-race heuristic with local Syzygy WDL on two published cases."""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.syzygy


CASES = {
    "reti_1921": ("7K/8/k1P5/7p/8/8/8/8 w - - 0 1", "c7"),
    "barth_1995_position_x": ("8/3K4/4P3/5p2/8/8/8/5k2 w - - 0 1", "e7"),
}
TABLE_SHA256 = {
    "KPvKP.rtbw": "6d21860e47a91d00841ccf63a657dc09b78f602e0ec005f925470e2449e1ae05",
    "KPvK.rtbw": "63ad9e15cd0f5e91e42e6f669a9f6116ae9f9eabd85757e9fb28d2be6074aed9",
}


def remaining_pawn_pushes(board, color):
    """Count single pushes on an open file, ignoring occupancy and tactics."""
    pawn, = board.pieces(chess.PAWN, color)
    rank = chess.square_rank(pawn)
    return 7 - rank if color == chess.WHITE else rank


def audit_case(tablebase, fen, inspect_move):
    board = chess.Board(fen)
    if not board.is_valid():
        raise ValueError(f"Invalid study position: {fen}")
    side = board.turn
    root_wdl = tablebase.probe_wdl(board)
    moves = {}
    for move in sorted(board.legal_moves, key=lambda move: move.uci()):
        san = board.san(move)
        board.push(move)
        race_lead = remaining_pawn_pushes(board, not side) - remaining_pawn_pushes(board, side)
        moves[san] = {"uci": move.uci(), "race_lead_pushes": race_lead,
                      "wdl_from_root_side": -tablebase.probe_wdl(board)}
        board.pop()
    if root_wdl != max(move["wdl_from_root_side"] for move in moves.values()):
        raise ValueError("Root and child WDL disagree")
    best_race = max(move["race_lead_pushes"] for move in moves.values())
    board.push_san(inspect_move)
    replies = {}
    for move in sorted(board.legal_moves, key=lambda move: move.uci()):
        san = board.san(move)
        board.push(move)
        replies[san] = tablebase.probe_wdl(board)
        board.pop()
    if moves[inspect_move]["wdl_from_root_side"] != min(replies.values()):
        raise ValueError("Selected move and reply WDL disagree")
    return {
        "fen": fen, "root_wdl": root_wdl, "legal_root_moves": moves,
        "race_preferred_moves": [san for san, move in moves.items() if move["race_lead_pushes"] == best_race],
        "wdl_optimal_moves": [san for san, move in moves.items() if move["wdl_from_root_side"] == root_wdl],
        "inspected_move": inspect_move, "all_replies_wdl_from_root_side": replies,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    for name, expected in TABLE_SHA256.items():
        if hashlib.sha256((args.tables / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Table SHA-256 mismatch: {name}")
    with chess.syzygy.open_tablebase(str(args.tables)) as tablebase:
        cases = {name: audit_case(tablebase, *fixture) for name, fixture in CASES.items()}
    reti = cases["reti_1921"]
    assert reti["race_preferred_moves"] == ["c7"]
    assert reti["wdl_optimal_moves"] == ["Kg7"]
    assert reti["all_replies_wdl_from_root_side"]["Kb7"] == -2
    position_x = cases["barth_1995_position_x"]
    assert len(position_x["legal_root_moves"]) == 8
    assert all(move["wdl_from_root_side"] == 0 for move in position_x["legal_root_moves"].values())
    assert position_x["race_preferred_moves"] == ["e7"]
    assert {san for san, wdl in position_x["all_replies_wdl_from_root_side"].items() if wdl == 0} == {"f4"}
    report = {"python_chess": chess.__version__, "tables_sha256": TABLE_SHA256, "cases": cases}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Verified 12 root moves and 12 replies across two historical KPKP positions")


if __name__ == "__main__":
    main()
