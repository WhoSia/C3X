"""Test whether categorical root choices admit additive donor scores.

Usage: python c3x_030_s4l_r5_additive_choice.py R4_RESULT.json
Requires scipy. All-cell fitting is descriptive. The four unseen interior cells
are scored against a model constrained only by the sham row and column.
"""
import argparse
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

DONORS = ("sham", "two", "second")
CELLS = tuple(itertools.product(DONORS, repeat=2))
ANCHORS = tuple(cell for cell in CELLS if "sham" in cell)

def fit(moves, choices):
    variables = [(axis, donor, move) for axis in range(2) for donor in DONORS for move in moves]
    index = {item: i for i, item in enumerate(variables)}
    inequalities = []
    for cell, winner in choices.items():
        for rival in moves:
            if rival == winner:
                continue
            row = np.zeros(len(variables))
            for axis, donor in enumerate(cell):
                row[index[axis, donor, winner]] = -1
                row[index[axis, donor, rival]] = 1
            inequalities.append(row)
    if not inequalities:
        return {}
    result = linprog(np.zeros(len(variables)), A_ub=inequalities,
                     b_ub=-np.ones(len(inequalities)), bounds=(None, None), method="highs")
    if result.status == 2:
        return None
    if not result.success or np.max(np.asarray(inequalities) @ result.x) > -0.999999:
        raise RuntimeError(f"Could not verify solver result: {result.message}")
    return {"/".join(map(str, key)): float(value) for key, value in zip(variables, result.x)}

def audit(case):
    observed = {(t, h): case["matrix"][f"{t}-{h}"]["move"] for t, h in CELLS}
    # Use only anchor winners as candidate universe for prediction. Preserve unseen
    # moves as explicit misses. Full fit uses every observed winner.
    all_moves = sorted(set(observed.values()))
    known = {cell: observed[cell] for cell in ANCHORS}
    candidates = sorted(set(known.values()))
    fitted = fit(all_moves, observed)
    forecasts = {}
    for cell in CELLS:
        if cell in known:
            continue
        possible = [m for m in candidates if fit(candidates, {**known, cell: m}) is not None]
        forecasts["/".join(cell)] = {"possible": possible, "observed": observed[cell],
            "covers": observed[cell] in possible,
            "outside_anchor_vocabulary": observed[cell] not in candidates}
    return {"strict_additive_witness": fitted, "anchor_candidates": candidates, "interior": forecasts}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path)
    raw = json.loads(parser.parse_args().result.read_text())
    print(json.dumps({key: audit(value) for key, value in raw.items()}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
