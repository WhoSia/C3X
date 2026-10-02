#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import harness.g95_p16_court as p16
from c3x_g10.graded_recoverability import census

def load(path):
    return json.loads(Path(path).read_text())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair-freeze", action="append", required=True)
    ap.add_argument("--ecology", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pfs = [p16.load_pair(x) for x in a.pair_freeze]
    out = census(pfs, load(a.ecology))
    Path(a.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("G10_P9_PREOUTCOME", out["verdict"])
    for source, stats in sorted(out["source_stats"].items()):
        print(source, stats)

if __name__ == "__main__":
    main()
