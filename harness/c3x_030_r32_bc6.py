"""Trace the first Kg7/Bc6 PV child and check the R31 endpoints."""
import argparse
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r23_native_replay import NET, digest, run
from c3x_030_r29_local_tt_move import write
from c3x_030_r31_tt_pv import COHORT, SEAL, extracted

R31 = "ef182a418b5522a400a713788d90f8846e8b5d204c182e41729648a19e066a50"
REPLY = "b5c6"


def replay(args, binary, name, history, target, *, masked, trace, extra=None):
    folder = args.out / name
    env = {"C3X_R29_PROBES": "1", "C3X_R29_TARGET": target["seq"],
           "C3X_R29_MASK_MOVE": str(int(masked)), "C3X_R29_MASK_VALUE": "0",
           "C3X_R30_PICKER_ONLY": "0", "C3X_R30_SKIP_SINGULAR": "0",
           "C3X_NO_TT_PICKER": "0", "C3X_NO_TT_VALUE": "0",
           "C3X_R31_OBSERVE": "1", "C3X_R31_OVERRIDE": "",
           "C3X_R32_OBSERVE": str(int(trace))}
    # R31_OVERRIDE is optional, and an empty value is not a valid override.
    env.pop("C3X_R31_OVERRIDE")
    if extra:
        env.update(extra)
    uci, proof = run(binary, {"history": history}, args.net, folder, logging=True, paired=False,
                     nnue=True, nodes=32000, environment=env)
    return dict(extracted(folder, proof, target, "", masked), uci=uci), (
        folder / "stderr.txt").read_text().splitlines()


def focal(lines):
    watch, = fields(lines, "C3X_R32_WATCH")
    enter = fields(lines, "C3X_R32_ENTER")
    exit_rows = fields(lines, "C3X_R32_EXIT")
    if [row["mode"] for row in enter] != ["s", "p"] or [row["mode"] for row in exit_rows] != ["s", "p"]:
        raise ValueError("Missing or ambiguous scout/PV Bc6 move")
    if any(row["key"] != watch["key"] or row["index"] != "1" for row in enter):
        raise ValueError("Unexpected Bc6 move or key")
    reads = fields(lines, "C3X_R32_READ")
    child, = (row for row in reads if row["mode"] == "p" and row["ply"] == "2"
              and row["pv"] == "1" and row["excluded"] == "0")
    parent = enter[1]
    if (child["key"], child["parent"], child["depth"], int(child["alpha"]), int(child["beta"])) != (
        watch["key"], REPLY, parent["depth"], -int(parent["beta"]), -int(parent["alpha"])
    ):
        raise ValueError("The read did not belong to the first Bc6 PV move")
    returns = fields(lines, "C3X_R32_RETURN")
    bc6, = (row for row in returns if row["mode"] == "p" and row["ply"] == "1")
    if (bc6["key"], bc6["move"], bc6["stage"], bc6["value"]) != (watch["key"], REPLY, "pv", exit_rows[1]["value"]):
        raise ValueError("Return does not join to Bc6")
    return {"enters": enter, "exits": exit_rows, "bc6_pv_read": child, "bc6_pv_return": bc6,
            "reads": reads, "returns": returns, "writes": fields(lines, "C3X_R32_WRITE"),
            "refreshes": fields(lines, "C3X_R32_REFRESH")}


def load_case(args):
    if (digest(args.cohort), digest(args.seal), digest(args.r31), digest(args.net)) != (COHORT, SEAL, R31, NET):
        raise ValueError("The R31 fixture has changed")
    case = "R29-031"
    target, = (row["targets"]["fallback"] for row in json.loads(args.seal.read_text())["positions"]
               if row["id"] == case)
    history, = (row["moves"] for row in json.loads(args.cohort.read_text())["positions"] if row["id"] == case)
    return target, history, json.loads(args.r31.read_text())["arms"]


def execute(args):
    target, history, receipts = load_case(args)
    arms = {}
    for world in ("sham", "whole_hint"):
        masked = world == "whole_hint"
        old, _ = replay(args, args.old, world + "-r31", history, target, masked=masked, trace=False)
        off, _ = replay(args, args.patch, world + "-off", history, target, masked=masked, trace=False)
        on, lines = replay(args, args.patch, world, history, target, masked=masked, trace=True)
        if not old == off == on == receipts[world]:
            raise ValueError("R31 receipt or passive invariance mismatch for " + world)
        arms[world] = {"r31": on, "bc6": focal(lines)}
    return {"sources": {"r31": R31, "old": digest(args.old), "patch": digest(args.patch)}, "arms": arms}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("cohort", "seal", "r31", "old", "patch", "net", "out"):
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    write(args.out / "result.json", execute(args))


if __name__ == "__main__":
    main()
