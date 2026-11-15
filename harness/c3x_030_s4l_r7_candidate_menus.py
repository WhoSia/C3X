"""Run a matched menu-by-stopping-rule grid on the three R6 development cases."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import itertools
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from c3x_030_s4l_r4_exchange import DONORS, run
from c3x_030_s4l_r6_forced_probe import CANDIDATES

PAIRS = {
    "dev_italian_ply10": ("b2b4", "e1g1"),
    "dev_italian_ply8": ("d2d4", "d2d3"),
    "dev_london_ply8": ("b1d2", "f3e5"),
}


def study(binary, output, spec, archived, forced):
    ident = spec["case_id"]
    fen, target = spec["fen"], archived["target"]
    work = output / ident
    work.mkdir(parents=True)
    menus = {move: (move,) for move in CANDIDATES[ident]}
    menus.update(pair=PAIRS[ident], four=CANDIDATES[ident], all=())
    with TemporaryDirectory(prefix="snapshots-", dir=work) as snapshot_dir:
        paths = {arm: {block: Path(snapshot_dir) / f"{arm}-{block}.bin"
                       for block in ("tt", "history")} for arm in DONORS}
        result = {"natural": {}, "grid": {}}
        for arm in DONORS:
            row = run(binary, work / arm, fen, target, arm, exports=paths[arm].items())
            if row != archived["natural"][arm]:
                raise ValueError(f"Donor replay differs for {ident}/{arm}")
            result["natural"][arm] = row

        for tt, history in itertools.product(DONORS, repeat=2):
            cell = f"{tt}-{history}"
            cell_menus = dict(menus)
            if ident == "dev_london_ply8" and cell == "second-second":
                for move in CANDIDATES[ident][2:]:
                    cell_menus[f"pair-{move}"] = (*PAIRS[ident], move)
            imports = (("tt", paths[tt]["tt"]), ("history", paths[history]["history"]))
            grid = result["grid"][cell] = {}
            for limit, depth in (("depth8", 8), ("nodes12k", None)):
                for name, moves in cell_menus.items():
                    label = f"{limit}-{name}"
                    row = run(binary, work / cell / label, fen, target, "sham",
                              imports=imports, second_moves=moves, second_depth=depth)
                    if row["masks"] or row["go1"] != archived["natural"]["sham"]["go1"]:
                        raise ValueError(f"Recipient replay differs for {ident}/{cell}/{label}")
                    go2 = row["go2"]
                    if moves and go2["move"] not in moves:
                        raise ValueError(f"Winner outside menu for {ident}/{cell}/{label}")
                    if limit == "nodes12k" and name == "all" and go2 != archived["matrix"][cell]:
                        raise ValueError(f"Joint replay differs for {ident}/{cell}")
                    if depth and len(moves) == 1:
                        info = go2["info"].split()
                        index = info.index("score")
                        receipt = {"score": int(info[index + 2]), "unit": info[index + 1],
                                   "depth": int(info[2]), "nodes": go2["nodes"],
                                   "bound": next((x for x in info if x.endswith("bound")), None)}
                        if receipt != forced[f"{tt}/{history}/{name}"]:
                            raise ValueError(f"Singleton replay differs for {ident}/{cell}/{name}")
                    grid[label] = row
    return ident, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("binary", "protocol", "r4_result", "r6_result", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    specs = [x for x in json.loads(args.protocol.read_text())["cases"]
             if x["case_id"] in PAIRS]
    if {x["case_id"] for x in specs} != PAIRS.keys() or len(specs) != len(PAIRS):
        raise ValueError("Expected the three predeclared cases exactly once")
    if any(x["split"] != "development" for x in specs):
        raise ValueError("Development cases required")
    prior = json.loads(args.r4_result.read_text())
    forced = json.loads(args.r6_result.read_text())
    with ThreadPoolExecutor(max_workers=len(specs)) as pool:
        tasks = [pool.submit(study, args.binary.resolve(), args.output.resolve(), spec,
                             prior[spec["case_id"]], forced[spec["case_id"]]) for spec in specs]
        print(json.dumps(dict(task.result() for task in tasks), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
