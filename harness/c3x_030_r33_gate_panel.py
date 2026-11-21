"""Discover frozen native early returns and replay selected interventions."""
import argparse
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r23_native_replay import NET, digest, run
from c3x_030_r29_local_tt_move import write

COHORT = "51bf007c7941afe29007ee295378a3ff701d014d649bc40682ba65db6be765a4"


def events(lines):
    opened = fields(lines, "C3X_R33_OPEN")
    closed = {row["event"]: row for row in fields(lines, "C3X_R33_CLOSE")}
    if len(closed) != len(opened) or len(opened) != len(set(row["event"] for row in opened)):
        raise ValueError("Unbalanced native gate events")
    if [int(row["event"]) for row in opened] != list(range(1, len(opened)+1)):
        raise ValueError("Broken event order")
    return [{"open": row, "close": closed[row["event"]]} for row in opened]


def trial(args, case, name, *, binary, observer, target=0, skip_f=False, skip_n=False,
          nodes=32000, depth=None):
    folder = args.out / name
    env = {"C3X_R33_OBSERVE": str(int(observer)), "C3X_R33_TARGET": str(target),
           "C3X_R33_SKIP_FUTILITY": str(int(skip_f)), "C3X_R33_SKIP_NULL": str(int(skip_n)),
           "C3X_R29_PROBES": "0", "C3X_R31_OBSERVE": "0", "C3X_NO_TT_PICKER": "0",
           "C3X_NO_TT_VALUE": "0", "C3X_R29_MASK_MOVE": "0", "C3X_R29_MASK_VALUE": "0"}
    uci, proof = run(binary, {"history": case["moves"]}, args.net, folder, logging=True,
                     paired=False, nnue=True, nodes=nodes, depth=depth, environment=env)
    stderr = (folder / "stderr.txt").read_text().splitlines()
    return {"uci": uci, "events": events(stderr) if observer else [],
            "proof": proof, "trace": digest(folder / "stderr.txt")}


def select(rows):
    strata = {}
    for event in rows:
        row = event["open"]
        group = row["null_eligible"]
        if not (1 <= int(row["depth"]) <= 5 and 2 <= int(row["ply"]) <= 5):
            raise ValueError("Engine emitted an event outside the registered range")
        slack = int(row["floor"]) - int(row["beta"])
        if slack < 0:
            raise ValueError("Engine emitted an ineligible futility gate")
        if group not in strata or slack < strata[group][0]:
            strata[group] = (slack, event)
    return {group: event for group, (_,event) in strata.items()}


def discover(args, cases):
    selected = []
    all_counts = {}
    for case in cases:
        stem = case["id"]
        baseline = trial(args,case,stem+"/old",binary=args.old,observer=False)
        off = trial(args,case,stem+"/off",binary=args.patch,observer=False)
        observed = trial(args,case,stem+"/observed",binary=args.patch,observer=True)
        if baseline["uci"] != off["uci"] or off["uci"] != observed["uci"] or baseline["proof"] != off["proof"] or off["proof"] != observed["proof"]:
            raise ValueError("Observer changed the source result for "+stem)
        nominations = select(observed["events"])
        all_counts[stem] = {"events": len(observed["events"]),
                            "strata": sorted(nominations),
                            "bestmove": observed["proof"]["best"]["move"]}
        for group,event in nominations.items():
            selected.append({"position":stem,"group":group,"target":event["open"],
                             "baseline":observed["proof"]["best"]["move"]})
    return {"source_sha256":digest(args.cohort),"reference_binary":digest(args.old),
            "observer_binary":digest(args.patch),"net_sha256":digest(args.net),
            "node_budget":32000,"cases":all_counts,"targets":selected}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("cohort","old","patch","net","out"):
        parser.add_argument(name,type=Path)
    parser.add_argument("--limit",type=int)
    args=parser.parse_args()
    if digest(args.cohort)!=COHORT or digest(args.net)!=NET:
        raise ValueError("Frozen source changed")
    cases=json.loads(args.cohort.read_text())["positions"]
    if args.limit:
        cases=cases[:args.limit]
    args.out.mkdir(parents=True,exist_ok=True)
    write(args.out/"discovery.json",discover(args,cases))


if __name__=="__main__":
    main()
