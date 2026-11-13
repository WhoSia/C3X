"""Exhaustive bounded reachability for the Cerrado c-pawn goal."""
import json
from functools import lru_cache

import chess

FEN = "1r3rk1/2pq1ppp/4pn2/1b2B3/2p5/6P1/3PPPBP/2RQ1RK1 w - - 1 16"
VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
          chess.ROOK: 5, chess.QUEEN: 9}

def material(board):
    return sum(value * (len(board.pieces(piece, chess.WHITE))
                        - len(board.pieces(piece, chess.BLACK)))
               for piece, value in VALUES.items())

def track(board, move, pawn):
    if move.to_square == pawn:
        return None
    if board.is_en_passant(move):
        captured = move.to_square + (-8 if board.turn else 8)
        if captured == pawn:
            return None
    return move.to_square if move.from_square == pawn else pawn

def assess(board, pawn, initial_material, horizon, guard):
    """Return all first White moves guaranteeing the goal at the deadline."""
    def step(move, square, remaining):
        next_square = track(board, move, square)
        remaining -= int(board.turn == chess.WHITE)
        board.push(move)
        try:
            return solve(board._transposition_key(), next_square, remaining)
        finally:
            board.pop()

    @lru_cache(maxsize=None)
    def solve(_position, square, remaining):
        # The deadline comes after Black's response to the final White move.
        if board.turn and remaining == 0:
            return square is None and (not guard or material(board) >= initial_material)
        if square is None and not guard:
            return True
        legal = list(board.legal_moves)
        if not legal:
            return square is None and (not guard or material(board) >= initial_material)
        if board.turn:
            if remaining == 1 and square is not None:
                legal = [move for move in legal if track(board, move, square) is None]
            return any(step(move, square, remaining) for move in legal)
        return all(step(move, square, remaining) for move in legal)

    return [board.san(move) for move in list(board.legal_moves) if step(move, pawn, horizon)]

def main():
    initial = chess.Board(FEN)
    for san in ("Bxf6", "gxf6"):
        initial.push_san(san)
    rows = []
    initial_material = material(initial)
    for san in ("Qc2", "Qe1", "e3", "h3"):
        initial.push_san(san)
        for move in list(initial.legal_moves):
            reply = initial.san(move)
            pawn = track(initial, move, chess.C4)
            initial.push(move)
            try:
                assert pawn is None or initial.piece_at(pawn) == chess.Piece(chess.PAWN, chess.BLACK)
                rows.append(dict(candidate=san, reply=reply, reply_uci=move.uci(),
                                 goals={f"{horizon}_{guard}": assess(initial, pawn, initial_material, horizon, guard)
                                        for horizon, guard in ((1, False), (1, True), (2, False), (2, True))}))
            finally:
                initial.pop()
        initial.pop()
    print(json.dumps(rows, indent=2))

if __name__ == "__main__":
    main()
