"""Build rule-checked practice items for the R27 Stockfish learner pilot."""
import argparse
import io
import json
from pathlib import Path
import zipfile

import chess
import chess.pgn

from c3x_030_s4l_r10_reply_transport import board_at, digest
from c3x_030_r27_native_choice import CASE_ID

LESSON = (
    (("a5a4", "d2d1", "f6d7"), "b3"),
    (("a5a4", "b3a4", "f6d7"), "a4"),
)
CHECKPOINTS = (40, 41, 50, 51, 60, 61, 70, 71, 80, 81)
GAME_LIMIT = 384
TWIC_SHA256 = "84ef391278c0dcf1b95a9d7732882d1e34377ad807608306812450b3b7aa62b8"
# One positive and one negative per color, with distinct events and games.
QUOTAS = {(turn, label) for turn in (chess.WHITE, chess.BLACK) for label in (True, False)}


def legal_witnesses(board, pawn, bishop, knight):
    """Accept a straight pawn advance with a legal recapture of the knight."""
    color = board.turn
    for square, piece in ((pawn, chess.Piece(chess.PAWN, color)),
                          (bishop, chess.Piece(chess.BISHOP, color)),
                          (knight, chess.Piece(chess.KNIGHT, not color))):
        if board.piece_at(square) != piece:
            raise ValueError(f"Unexpected piece at {chess.square_name(square)}")
    capture = chess.Move(knight, bishop)
    witnesses = {}
    for advance in board.generate_legal_moves(from_mask=chess.BB_SQUARES[pawn]):
        if advance.promotion is not None:
            continue
        if chess.square_file(advance.to_square) != chess.square_file(pawn):
            continue
        child = board.copy(stack=False)
        child.push(advance)
        if capture not in child.legal_moves:
            continue
        capture_san = child.san(capture)
        child.push(capture)
        for retake in child.generate_legal_moves(from_mask=chess.BB_SQUARES[advance.to_square],
                                                  to_mask=chess.BB_SQUARES[bishop]):
            witnesses[advance.uci()] = [board.san(advance), capture_san, child.san(retake)]
    return witnesses


def item(board, pawn, bishop, knight, source):
    return {"fen": board.fen(), "pawn": chess.square_name(pawn), "bishop": chess.square_name(bishop),
            "knight": chess.square_name(knight), "witnesses": legal_witnesses(board, pawn, bishop, knight),
            "source": source}


def training_reply_items(lesson_board):
    rows = []
    for path, pawn in LESSON:
        branch = lesson_board.copy()
        sequence = branch.variation_san([chess.Move.from_uci(move) for move in path])
        for move in path:
            branch.push_uci(move)
        rows.append(item(branch, chess.parse_square(pawn), chess.C5, chess.D7, sequence))
    return rows


def plausible_items(board, source):
    color = board.turn
    if board.is_check():
        return
    for knight in sorted(board.pieces(chess.KNIGHT, not color)):
        for bishop in sorted(board.pieces(chess.BISHOP, color) & board.attacks(knight)):
            for pawn in sorted(board.pieces(chess.PAWN, color)):
                file_distance = abs(chess.square_file(bishop) - chess.square_file(pawn))
                advance_needed = (chess.square_rank(bishop) - chess.square_rank(pawn)) * (1 if color else -1) - 1
                if file_distance == 1 and 1 <= advance_needed <= 2:
                    yield item(board, pawn, bishop, knight, source)


def new_game_items(pgn, banned_prefixes, banned_events):
    quota = set(QUOTAS)
    events = set(banned_events)
    rows = []
    for ordinal in range(1, GAME_LIMIT + 1):
        game = chess.pgn.read_game(pgn)
        if game is None:
            break
        board = game.board()
        moves = list(game.mainline_moves())
        event = game.headers.get("Event", "?")
        prefix = tuple(move.uci() for move in moves[:12])
        if game.errors or board.fen() != chess.STARTING_FEN or prefix in banned_prefixes or event in events:
            continue
        found = False
        for ply, move in enumerate(moves[:max(CHECKPOINTS)], 1):
            board.push(move)
            if ply not in CHECKPOINTS:
                continue
            source = {"twic_issue": 1671, "game_ordinal": ordinal, "ply": ply, "event": event}
            for row in plausible_items(board, source):
                label = board.turn, bool(row["witnesses"])
                if label not in quota:
                    continue
                rows.append(row)
                quota.remove(label)
                banned_prefixes.add(prefix)
                events.add(event)
                found = True
                break
            if found:
                break
        if not quota:
            break
    if quota:
        raise ValueError(f"Unfilled disjoint game practice quotas: {quota}")
    return rows


def build(cohort, archive):
    if digest(archive) != TWIC_SHA256:
        raise ValueError("Expected the byte-frozen TWIC 1671 ZIP")
    data = json.loads(cohort.read_bytes())
    root, = (row for row in data["positions"] if row["id"] == CASE_ID)
    banned_events = {row["event"] for row in data["games"]}
    banned_prefixes = {tuple(row["moves"][:12]) for row in data["games"]}
    board = board_at(root["moves"])
    if board.fen() != root["fen"]:
        raise ValueError("Worked example history mismatch")
    with zipfile.ZipFile(archive) as z:
        name, = (n for n in z.namelist() if n.lower().endswith(".pgn"))
        pgn = io.StringIO(z.read(name).decode("latin-1"))
    near = training_reply_items(board)
    transfer = new_game_items(pgn, banned_prefixes, banned_events)
    return {"lesson": {"fen": board.fen(), "case": CASE_ID},
            "near": dict(zip(("N1", "N2"), near, strict=True)),
            "transfer": {f"T{i}": row for i, row in enumerate(transfer, 1)},
            "cohort_sha256": digest(cohort), "archive_sha256": digest(archive)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "archive", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    result = build(args.cohort, args.archive)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
