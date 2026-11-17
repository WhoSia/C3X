"""Replay the rook alternatives in Wilkins (1980), Figures 1 and 2, p. 212."""

import json

import chess


FIGURES = {
    "1": "7k/pR6/7K/6r1/6p1/6P1/8/8 b - - 0 1",
    "2": "7k/pR6/7K/6r1/b5p1/6P1/8/8 b - - 0 1",
}
ROOK_MOVES = ("g5c5", "g5d5", "g5e5", "g5f5")
FIRST_CHECK = "b7b8"
HORIZON = 5


def white_mate(board, plies):
    """Return distance to forced White mate within the requested horizon."""
    outcome = board.outcome(claim_draw=False)
    if outcome is not None:
        return 0 if outcome.winner == chess.WHITE else None
    if plies == 0:
        return None
    distances = []
    for move in list(board.legal_moves):
        board.push(move)
        result = white_mate(board, plies - 1)
        board.pop()
        if result is None:
            if board.turn == chess.BLACK:
                return None
        else:
            distances.append(1 + result)
    if not distances:
        return None
    return min(distances) if board.turn == chess.WHITE else max(distances)


def replay():
    figures = {}
    for figure, fen in FIGURES.items():
        board = chess.Board(fen)
        if not board.is_valid():
            raise ValueError(f"Invalid source diagram {figure}")
        rows = {}
        for root in ROOK_MOVES:
            after = board.copy()
            after.push_uci(root)
            mate = white_mate(after, HORIZON)
            after.push_uci(FIRST_CHECK)
            first_check_mate = white_mate(after, HORIZON - 1)
            defenses = {}
            for move in sorted(after.legal_moves, key=lambda move: move.uci()):
                san = after.san(move)
                after.push(move)
                defenses[san] = white_mate(after, HORIZON - 2)
                after.pop()
            rows[board.san(chess.Move.from_uci(root))] = {
                "mate_plies_after_black_move": mate,
                "mate_plies_after_rb8": first_check_mate,
                "mate_plies_after_each_defense": defenses,
            }
        figures[figure] = {"fen": fen, "rook_alternatives": rows}
    return {"white_horizon_in_plies": HORIZON, "figures": figures}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
