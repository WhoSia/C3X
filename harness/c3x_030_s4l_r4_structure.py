"""Classify categorical TT/history donor maps without imposing an A/B outcome."""
import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

DONORS = ("sham", "two", "second")

def classify(matrix):
    tt = any(len({matrix[t,h] for t in DONORS}) > 1 for h in DONORS)
    history = any(len({matrix[t,h] for h in DONORS}) > 1 for t in DONORS)
    return {(False,False):"constant", (True,False):"tt_only",
            (False,True):"history_only", (True,True):"both"}[tt, history]

def interaction_rectangles(matrix):
    """A nonzero mixed difference of one-hot move labels is a witness."""
    result = []
    for a,b in combinations(DONORS,2):
        for c,d in combinations(DONORS,2):
            if Counter((matrix[a,c],matrix[b,d])) != Counter((matrix[a,d],matrix[b,c])):
                result.append({"tt": [a,b], "history": [c,d],
                               "moves": [[matrix[a,c],matrix[a,d]],[matrix[b,c],matrix[b,d]]]})
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("result",type=Path)
    a = p.parse_args()
    data = json.loads(a.result.read_text())
    out = {}
    for case,row in data.items():
        matrix = {(t,h): row["matrix"][f"{t}-{h}"]["move"] for t in DONORS for h in DONORS}
        diagonals = {k: matrix[k,k] == row["natural"][k]["go2"]["move"] for k in DONORS}
        out[case] = {"class": classify(matrix), "interaction_rectangles": interaction_rectangles(matrix),
                     "diagonal_matches_natural": diagonals,
                     "distinct_moves": sorted(set(matrix.values())),
                     "unique_tt":len({v["tt"] for v in row["snapshot_sha256"].values()}),
                     "unique_histories":len({v["history"] for v in row["snapshot_sha256"].values()})}
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__ == "__main__":
    main()
