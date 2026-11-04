#!/usr/bin/env python3
"""P35/R2 margin stratification and contamination gate. Analytic model, not Stockfish evidence."""
import math
from collections import defaultdict

BINS = (("near", 0, 20), ("intermediate", 20, 100), ("wide", 100, math.inf))

def margin_bin(abs_gap_cp):
    if not isinstance(abs_gap_cp, (int, float)) or not math.isfinite(abs_gap_cp) or abs_gap_cp < 0:
        raise ValueError("invalid absolute cp gap")
    return next(name for name, lo, hi in BINS if lo <= abs_gap_cp < hi)

def misranking_probability(true_gap_cp, per_move_noise_sd_cp):
    """Independent per-move N(0, sigma^2) errors; toy model, NOT measured engine noise.

    For zero gap, return 0.5 by continuity; no unique true ordering exists.
    """
    if not math.isfinite(true_gap_cp) or not math.isfinite(per_move_noise_sd_cp) or per_move_noise_sd_cp <= 0:
        raise ValueError("invalid gap or noise")
    return 0.5 * math.erfc(abs(true_gap_cp) / (2 * per_move_noise_sd_cp))

def validate_registry(records):
    """Reject any source game appearing in both dev and heldout splits."""
    games = defaultdict(set)
    counts = defaultdict(int)
    for r in records:
        game = r.get("game_id")
        split = r.get("split")
        if not isinstance(game, str) or not game.strip() or split not in ("dev", "heldout"):
            raise ValueError("bad identity or split")
        b = margin_bin(r["abs_gap_cp"])
        games[game].add(split)
        counts[(split, b)] += 1
    leakage = sorted(game for game, splits in games.items() if len(splits) != 1)
    if leakage:
        raise ValueError("game-level contamination: " + ",".join(leakage))
    return {"counts": {f"{split}:{b}": counts[(split, b)]
                       for split in ("dev", "heldout") for b, _, _ in BINS},
            "games": len(games), "status": "DESIGN_CHECK_ONLY"}

if __name__ == "__main__":
    for gap in (0, 5, 10, 20, 50, 100):
        print(f"true gap {gap:>3} cp, sigma 20 cp => p(rank error)={misranking_probability(gap,20):.6f}")
