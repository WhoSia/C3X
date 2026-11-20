"""Replay the R29-031 scout/PV TT writer and isolate fields at the consumer."""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r23_native_replay import NET, digest, run
from c3x_030_r29_local_tt_move import trace_at, write
from c3x_030_r30_child_chain import chain

COHORT = "1fcafbb3526c8a23f90cc2035b960db7995cc91ffdffe76e3ef89d4ae630e6ad"
SEAL = "4da675e5969d24b865e72c7bd639a0e823d7f5eaca01d2c983ed602a290e19a7"
R30 = "58ddc61bec7c03636cb2a1f5fef8c61f2a5e473e0189706ba3fed3349220a6e2"
KEY = "17109324142970305696"
CHANNELS = {"depth": "d", "value": "v", "bound": "b"}


@dataclass(frozen=True)
class Entry:
    tag: int
    depth: int
    bound: int
    pv: int
    generation: int
    move: int
    value: int
    eval: int

    @classmethod
    def parse(cls, raw):
        return cls(*map(int, raw.split(",")))


def slots(lines, scout, consumer):
    """Join actual saves/refreshes of the watched slot, in file order."""
    if scout["key"] != KEY or consumer["key"] != KEY or scout["slot"] != consumer["slot"]:
        raise ValueError("Scout and PV do not refer to the same physical slot")
    start = next(i for i, line in enumerate(lines) if line.startswith("C3X_R31_SCOUT "))
    stop = next(i for i, line in enumerate(lines) if line.startswith("C3X_R31_PV "))
    if start >= stop:
        raise ValueError("PV preceded the scout")
    live = Entry.parse(scout["tuple"])
    events = []
    for line in lines[start + 1:stop]:
        name, *_ = line.split(" ", 1)
        if name not in ("C3X_R31_WRITE", "C3X_R31_REFRESH"):
            continue
        row, = fields([line], name)
        row["kind"] = name.removeprefix("C3X_R31_").lower()
        if row["slot"] == scout["slot"]:
            before, after = (Entry.parse(row[part]) for part in ("before", "after"))
            if before != live:
                raise ValueError("Gap in the physical slot trace")
            if row["key"] != KEY:
                raise ValueError("Different full key touched the selected slot")
            live = after
        events.append(row)
    downstream = Entry.parse(consumer["tuple"])
    if live != downstream:
        raise ValueError("Writer does not account for the consumer tuple")
    if downstream.tag != int(KEY) & 0xffff:
        raise ValueError("Tag does not match the position key")
    return events


def extracted(folder, proof, target, override, masked):
    lines = (folder / "stderr.txt").read_text().splitlines()
    scout, = fields(lines, "C3X_R31_SCOUT")
    consumer, = fields(lines, "C3X_R31_PV")
    field, value = (ord(override[0]), int(override[1:])) if override else (0, 0)
    if (consumer["field"], consumer["replacement"]) != (str(field), str(value)):
        raise ValueError("Wrong or missing consumer override")
    data = trace_at(folder, proof, target, roots=("g6g5", "f6g7"))
    if len(data["masked"]) != int(masked) or data["read"]["mask_move"] != str(int(masked)):
        raise ValueError("Wrong sender intervention")
    paths = chain(folder / "stderr.txt", data)
    left, right = paths["children"]
    if (left["stage"], right["stage"]) != ("scout", "pv") or left["stopped"] != "0":
        raise ValueError("Expected scout followed by full-window PV")
    pvs = fields(lines, "C3X_R29_PLY1")
    read, = (row for row in pvs if all(row[key] == target[key]
                                     for key in ("attempt", "root", "candidate_next", "key"))
             and row["pv"] == "1" and row["excluded"] == "0" and int(right["before"]) < int(row["seq"])
             <= int(right["after"]))
    if right["stopped"] != "0" or paths["candidate"] is None:
        raise ValueError("PV did not complete and reach the candidate")
    tt = Entry.parse(consumer["tuple"])
    if (tt.depth, tt.bound) != tuple(int(read[k]) for k in ("tt_depth", "bound")):
        raise ValueError("Physical arrival and existing R29 probe disagree")
    gate, = fields(lines, "C3X_R31_GATE")
    for key, stored in (("effective_depth", tt.depth), ("effective_bound", tt.bound), ("tt_value", tt.value)):
        flag = {"effective_depth": "d", "effective_bound": "b", "tt_value": "v"}[key]
        if int(gate[key]) != (value if field == ord(flag) else stored):
            raise ValueError(f"Consumer field mismatch at {key}")
    return {"scout": scout, "consumer": consumer, "events": slots(lines, scout, consumer), "gate": gate,
            "lmr": fields(lines, "C3X_R31_LMR"), "chain": paths, "target_attempt_end": data["target_attempt_end"],
            "producer": data["producer"], "last_report": data["last_report"]}


def invoke(args, history, name, binary, target, *, masked=False, observe=True, override=""):
    folder = args.out / name
    env = {"C3X_R29_PROBES": "1", "C3X_R29_TARGET": target["seq"],
           "C3X_R29_MASK_MOVE": str(int(masked)), "C3X_R29_MASK_VALUE": "0",
           "C3X_R30_PICKER_ONLY": "0", "C3X_R30_SKIP_SINGULAR": "0",
           "C3X_NO_TT_PICKER": "0", "C3X_NO_TT_VALUE": "0",
           "C3X_R31_OBSERVE": str(int(observe))}
    if override:
        env["C3X_R31_OVERRIDE"] = override
    uci, proof = run(binary, {"history": history}, args.net, folder, logging=True, paired=False,
                     nnue=True, nodes=32000, environment=env)
    if observe:
        result = extracted(folder, proof, target, override, masked)
    else:
        log = (folder / "stderr.txt").read_text().splitlines()
        if any(line.startswith("C3X_R31_") for line in log):
            raise ValueError("Disabled observer leaked trace")
        trace = trace_at(folder, proof, target, roots=("g6g5", "f6g7"))
        result = {"trace": trace, "chain": chain(folder / "stderr.txt", trace), "uci": uci}
    return dict(result, uci=uci)


def execute(args):
    if (digest(args.cohort), digest(args.seal), digest(args.r30), digest(args.net)) != (COHORT, SEAL, R30, NET):
        raise ValueError("Frozen R30 assets changed")
    seal = json.loads(args.seal.read_text())
    source, = (row for row in seal["positions"] if row["id"] == "R29-031")
    target = source["targets"]["fallback"]
    cohort = json.loads(args.cohort.read_text())
    case, = (row for row in cohort["positions"] if row["id"] == "R29-031")
    history = case["moves"]
    r30 = json.loads(args.r30.read_text())["arms"]
    arms = {}
    for name, masked in (("sham", False), ("whole_hint", True)):
        legacy = invoke(args, history, f"{name}-r30", args.old, target, masked=masked, observe=False)
        disabled = invoke(args, history, f"{name}-observer-off", args.patch, target, masked=masked, observe=False)
        if disabled != legacy or any(legacy[k] != r30[name][k] for k in legacy):
            raise ValueError(f"Historical replay or observer-off parity failed for {name}")
        observed = invoke(args, history, name, args.patch, target, masked=masked)
        if any(observed[key] != legacy[key] for key in ("uci", "chain")):
            raise ValueError(f"Observer changed {name}")
        arms[name] = observed

    restored = invoke(args, history, "restore", args.patch, target)
    if restored != arms["sham"]:
        raise ValueError("Restore failed")
    if args.phase == "swap":
        for name, masked, donor in (("sham", False, "whole_hint"), ("whole_hint", True, "sham")):
            base = arms[name]
            arrival = Entry.parse(base["consumer"]["tuple"])
            other = Entry.parse(arms[donor]["consumer"]["tuple"])
            for channel, prefix in CHANNELS.items():
                value = getattr(other, channel)
                key = f"{name}-{channel}-from-{donor}"
                treatment = invoke(args, history, key, args.patch, target, masked=masked, override=f"{prefix}{value}")
                if any(base[k] != treatment[k] for k in ("scout", "events")) or any(
                    base["consumer"][field] != treatment["consumer"][field] for field in ("key", "slot", "tuple")
                ):
                    raise ValueError("The intervention changed the input world before PV")
                if value == getattr(arrival, channel) and any(base[k] != treatment[k]
                                                            for k in base.keys() - {"consumer"}):
                    raise ValueError(f"Identity swap changed {key}")
                arms[key] = treatment
    return {"sources": {"cohort": COHORT, "seal": SEAL, "r30": R30, "nnue": NET,
                        "old_binary": digest(args.old), "patched_binary": digest(args.patch)},
            "arms": arms, "restore": restored}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("observe", "swap"))
    for key in ("cohort", "seal", "r30", "old", "patch", "net", "out"):
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    result = execute(args)
    write(args.out / "result.json", result)


if __name__ == "__main__":
    main()
