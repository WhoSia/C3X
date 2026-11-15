"""Run reciprocal, identity and sham interventions on the London PV gate."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from c3x_030_s4l_r4_exchange import run

CASE = "dev_london_ply8"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("engine", "protocol", "r4", "r7", "r7_screen", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    engine, work = args.engine.resolve(), args.output.resolve()
    spec, = [x for x in json.loads(args.protocol.read_text())["cases"]
             if x["case_id"] == CASE and x["split"] == "development"]
    prior = json.loads(args.r4.read_text())[CASE]
    r7 = json.loads(args.r7.read_text())[CASE]
    screen = json.loads(args.r7_screen.read_text())
    fen, target = spec["fen"], prior["target"]
    work.mkdir(parents=True)
    result = {}
    with TemporaryDirectory(dir=work) as folder:
        paths = [(block, Path(folder) / f"{block}.bin") for block in ("tt", "history")]
        donor = run(engine, work / "donor", fen, target, "second", exports=paths)
        if donor != prior["natural"]["second"]:
            raise ValueError("Donor replay differs")
        for limit, depth in (("depth8", 8), ("nodes12k", None)):
            for menu, moves, old, value in (
                ("full", (), r7["grid"]["second-second"][f"{limit}-all"], 6),
                ("minus-a3", tuple(m for m in screen["legal"] if m != "a2a3"),
                 screen["grid"][limit]["omit-a2a3"], 0),
            ):
                for arm, change in (("sham", None), ("identity", (value, value)),
                                    ("swap", (value, 6 - value))):
                    label = f"{limit}-{menu}-{arm}"
                    row = run(engine, work / label, fen, target, "sham", imports=paths,
                              second_moves=moves, second_depth=depth, probe_return=change)
                    trace = (work / label / "stderr.txt").read_text().splitlines()
                    contacts = [line for line in trace if line.startswith("C3X_R8_PROBE ")]
                    if len(contacts) != int(change is not None):
                        raise ValueError(f"Unexpected probe contact for {label}")
                    if (row["go1"] != old["go1"] or row["masks"]
                            or (arm != "swap" and row != old)):
                        raise ValueError(f"Replay differs for {label}")
                    result[label] = {"run": row, "contacts": contacts}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
