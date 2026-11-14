"""Summarize depth-matched forced-root gap contrasts and sham-anchor forecasts."""
import argparse
import itertools
import json
from pathlib import Path

DONORS = ("sham", "two", "second")

def summarize(rows):
    moves = sorted({key.split("/")[-1] for key in rows})
    def score(t, h, m):
        row = rows[f"{t}/{h}/{m}"]
        if row["depth"] != 8 or row["unit"] != "cp" or row["bound"] is not None:
            raise ValueError("Expected unbounded depth-8 cp result")
        return row["score"]
    contrasts = []
    for ts, hs, pair in itertools.product(itertools.combinations(DONORS, 2),
                                          itertools.combinations(DONORS, 2),
                                          itertools.combinations(moves, 2)):
        gaps = [score(t,h,pair[0]) - score(t,h,pair[1]) for t,h in itertools.product(ts,hs)]
        contrasts.append(dict(tt=ts, history=hs, pair=pair, gaps=gaps,
                              mixed_difference=gaps[0]-gaps[1]-gaps[2]+gaps[3]))
    def best(values):
        return [m for m in moves if values[m] == max(values.values())]
    forecasts = {}
    for t,h in itertools.product(DONORS[1:], repeat=2):
        observed = best({m:score(t,h,m) for m in moves})
        predicted = best({m:score(t,"sham",m)+score("sham",h,m)-score("sham","sham",m)
                          for m in moves})
        forecasts[f"{t}/{h}"] = dict(observed=observed, predicted=predicted,
                                      intersects=bool(set(observed)&set(predicted)))
    return dict(contrasts=contrasts, forecasts=forecasts)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("forced", type=Path)
    print(json.dumps({k:summarize(v) for k,v in json.loads(p.parse_args().forced.read_text()).items()},
                     indent=2,sort_keys=True))
