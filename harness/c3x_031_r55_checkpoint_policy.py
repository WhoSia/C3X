"""R55: outcome-blind checkpoint selection for a successor cohort.
The historical R46/R47 cohort remains immutable. Selection is conditional on
the available checkpoints; it does not promise uniform population strata.
"""
import hashlib
from collections import Counter

SEED = "C3X-R55-CHECKPOINT-v1"
CHECKPOINTS = (40, 41, 50, 51, 60, 61, 70, 71, 80, 81)

def choose_checkpoint(game_digest, eligible):
    """Return one (ply, board_key) or None, independent of input ordering."""
    if len(game_digest) != 64 or any(c not in "0123456789abcdef" for c in game_digest):
        raise ValueError("expected lowercase SHA256 game digest")
    rows = list(eligible)
    plies = [p for p, _ in rows]
    if len(set(plies)) != len(plies) or any(p not in CHECKPOINTS for p in plies):
        raise ValueError("duplicate or invalid checkpoint")
    if any(not isinstance(k, str) or not k for _, k in rows):
        raise ValueError("empty board key")
    if not rows:
        return None
    def rank(row):
        p, _ = row
        return (hashlib.sha256(f"{SEED}/{game_digest}/{p}".encode("ascii")).digest(), p)
    return min(rows, key=rank)

def legal_checkpoints(board, moves, key):
    """Replay from initial board, without modifying caller's board."""
    b = board.copy(stack=True)
    rows = []
    for ply, move in enumerate(moves, 1):
        b.push(move)
        if ply in CHECKPOINTS and b.legal_moves.count() >= 2 and not b.is_game_over():
            rows.append((ply, key(b)))
        if ply >= CHECKPOINTS[-1]:
            break
    return rows

def distribution(rows):
    """Receipt diagnostics, not a selection rule or balancing target."""
    return {"ply": dict(sorted(Counter(r["ply"] for r in rows).items())),
            "side": dict(Counter("white" if r["ply"] % 2 == 0 else "black" for r in rows)),
            "eligible_count": dict(sorted(Counter(r["eligible_count"] for r in rows).items()))}
