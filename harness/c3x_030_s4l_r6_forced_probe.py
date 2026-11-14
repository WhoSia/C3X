"""Replay R4 state exchange with a forced root candidate on each go 2."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import itertools
import json
from pathlib import Path

from c3x_030_s4l_r4_exchange import DONORS, run

CANDIDATES = {
    "dev_italian_ply10": ("b2b4", "e1g1", "d3d4", "h2h3"),
    "dev_italian_ply8": ("d2d4", "d2d3", "e1g1", "a2a3"),
    "dev_london_ply8": ("f3e5", "b1d2", "f4d6", "c2c3"),
}

def study(binary, output, spec, previous):
    ident, fen = spec["case_id"], spec["fen"]
    work = output / ident
    target = previous["target"]
    snapshots = {arm: {block: work / f"{arm}-{block}.bin" for block in ("tt", "history")}
                 for arm in DONORS}
    for arm in DONORS:
        row = run(binary, work / arm, fen, target, arm, exports=snapshots[arm].items())
        assert row == previous["natural"][arm]
    matrix = {}
    for t, h in itertools.product(DONORS, repeat=2):
        for move in CANDIDATES[ident]:
            imports = (("tt", snapshots[t]["tt"]), ("history", snapshots[h]["history"]))
            row = run(binary, work/f"{t}-{h}-{move}", fen, target, "sham",
                      imports=imports, second_move=move, second_depth=8)
            assert row["go1"] == previous["natural"]["sham"]["go1"] and not row["masks"]
            info = row["go2"]["info"].split()
            assert row["go2"]["move"] == move and info[info.index("pv")+1] == move
            idx = info.index("score")
            matrix[f"{t}/{h}/{move}"] = {
                "score": int(info[idx+2]), "unit": info[idx+1],
                "depth": int(info[2]), "bound": next((x for x in info if x.endswith("bound")), None),
                "nodes": row["go2"]["nodes"],
            }
    for paths in snapshots.values():
        for path in paths.values():
            path.unlink()
    return ident, matrix

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("binary", "protocol", "r4_result", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    specs = [x for x in json.loads(args.protocol.read_text())["cases"] if x["case_id"] in CANDIDATES]
    assert len(specs) == len(CANDIDATES) and all(x["split"] == "development" for x in specs)
    old = json.loads(args.r4_result.read_text())
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs = [pool.submit(study, args.binary.resolve(), args.output.resolve(), x, old[x["case_id"]]) for x in specs]
        print(json.dumps(dict(job.result() for job in jobs), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
