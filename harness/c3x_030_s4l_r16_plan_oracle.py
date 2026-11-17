"""Verify a named nonpawn capture against every defense in three plies."""

import chess


TARGETS = frozenset((chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN))
VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}


def target_after(board, move, target):
    """Advance the square of a tracked nonpawn piece along a legal move."""
    if target is None:
        return None
    if move.from_square == target:
        return move.to_square
    if board.is_castling(move):
        kingside = board.is_kingside_castling(move)
        rank = chess.square_rank(move.from_square)
        if target == chess.square(7 if kingside else 0, rank):
            return chess.square(5 if kingside else 3, rank)
        return target
    return None if move.to_square == target and board.is_capture(move) else target


def balance(board, mover):
    return sum(weight * (len(board.pieces(piece, mover)) - len(board.pieces(piece, not mover)))
               for piece, weight in VALUES.items())


def attained(board, target, mover, initial_balance):
    return target is None and balance(board, mover) >= initial_balance


def finishing_move(board, target, mover, baseline):
    if board.is_game_over(claim_draw=False):
        return attained(board, target, mover, baseline), None
    moves = (board.legal_moves if target is None
             else board.generate_legal_captures(to_mask=chess.BB_SQUARES[target]))
    for move in sorted(moves, key=chess.Move.uci):
        final_target = target_after(board, move, target)
        board.push(move)
        success = attained(board, final_target, mover, baseline)
        board.pop()
        if success:
            return True, move.uci()
    return False, None


def branch_witness(board, move, target, mover, baseline):
    current_target = target_after(board, move, target)
    board.push(move)
    try:
        if board.is_game_over(claim_draw=False):
            return {"holds": attained(board, current_target, mover, baseline),
                    "terminal_after_move": True}
        finishes = {}
        for defense in sorted(board.legal_moves, key=chess.Move.uci):
            next_target = target_after(board, defense, current_target)
            board.push(defense)
            success, finish = finishing_move(board, next_target, mover, baseline)
            board.pop()
            if not success:
                return {"holds": False, "refuting_defense": defense.uci()}
            finishes[defense.uci()] = finish
        return {"holds": True, "finishes": finishes}
    finally:
        board.pop()


def solve(board, victim):
    occupant = board.piece_at(victim)
    if (board.chess960 or occupant is None or occupant.color == board.turn
            or occupant.piece_type not in TARGETS or board.is_game_over(claim_draw=False)):
        raise ValueError("The leaf must have a live enemy nonpawn victim in standard chess")
    mover = board.turn
    baseline = balance(board, mover)
    return {move.uci(): branch_witness(board, move, victim, mover, baseline)
            for move in sorted(board.legal_moves, key=chess.Move.uci)}
