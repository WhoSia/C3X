"""Audit root gap comparability across the R4 crossed donor traces."""
import argparse
import itertools
import json
from pathlib import Path

DONORS = ("sham", "two", "second")
CELLS = tuple(itertools.product(DONORS, repeat=2))
RECEIPT = "C3X_S4L_ROOT_SCORE "

def read_scores(path):
    by_candidate = {}
    for line in path.read_text().splitlines():
        if not line.startswith(RECEIPT):
            continue
        row = dict(item.split("=", 1) for item in line[len(RECEIPT):].split())
        if row["epoch"] != "2":
            continue
        value, alpha, beta = (int(row[k]) for k in ("value", "alpha", "beta"))
        if not alpha < value < beta:
            continue
        # Root iteration and adjusted search depth can differ after retries.
        key = tuple(int(row[k]) for k in ("root_move_raw", "iteration", "depth", "alpha", "beta"))
        by_candidate.setdefault(key, []).append((value, int(row["root_id"])))
    return {k: v[0] for k, v in by_candidate.items() if len(v) == 1}

def audit(case):
    scores = {cell: read_scores(case / "-".join(cell) / "stderr.txt") for cell in CELLS}
    rectangles = []
    for tt in itertools.combinations(DONORS, 2):
        for hist in itertools.combinations(DONORS, 2):
            cells = tuple(itertools.product(tt, hist))
            common = set.intersection(*(set(scores[cell]) for cell in cells))
            # Different candidates can have different aspiration windows, but
            # each candidate must have the same window across all four cells.
            by_iteration = {}
            for key in sorted(common):
                move, iteration, depth, *_ = key
                by_iteration.setdefault((iteration, depth), []).append(key)
            contrasts = []
            for keys in by_iteration.values():
                for left, right in itertools.combinations(keys, 2):
                    if left[0] == right[0]:
                        continue
                    if any(scores[cell][left][1] != scores[cell][right][1] for cell in cells):
                        continue
                    gaps = [scores[cell][left][0] - scores[cell][right][0] for cell in cells]
                    contrasts.append({"a": left, "b": right, "gaps": gaps,
                                      "mixed_difference": gaps[0] - gaps[1] - gaps[2] + gaps[3]})
            rectangles.append({"tt": tt, "history": hist, "common_receipts": len(common),
                               "gap_contrasts": contrasts})
    return rectangles

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run", type=Path)
    a = p.parse_args()
    print(json.dumps({case.name: audit(case) for case in sorted(a.run.iterdir()) if case.is_dir()},
                     indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
