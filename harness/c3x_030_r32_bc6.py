"""Trace the first Kg7/Bc6 PV child and check the R31 endpoints."""
import argparse
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r23_native_replay import NET, digest, run
from c3x_030_r29_local_tt_move import write
from c3x_030_r31_tt_pv import COHORT, SEAL, Entry, extracted

R31 = "ef182a418b5522a400a713788d90f8846e8b5d204c182e41729648a19e066a50"
REPLY = "b5c6"
NESTED_RESULTS = "9db0da4b57ee9adb7ba47c350bc8ed7e0ec1ec9ebcb84f95653c60e1fbf6419b"
SINGULAR_RESULTS = "b34c113ce4b35093aa176553f0e0ea39cef8e835a3b8dbf5de8acb97e0ee9c45"
FIELD_CROSS = "2796317d74c59835e50d5c2ae8cc5af60c6fa38097764355df3d8464a386a5b1"
PASSIVE = "6b99c9b5f603318e7022310c8886064241f36980ce5d6e1641c4265be946569b"


def replay(args, binary, name, history, target, *, masked, trace, extra=None):
    folder = args.out / name
    env = {"C3X_R29_PROBES": "1", "C3X_R29_TARGET": target["seq"],
           "C3X_R29_MASK_MOVE": str(int(masked)), "C3X_R29_MASK_VALUE": "0",
           "C3X_R30_PICKER_ONLY": "0", "C3X_R30_SKIP_SINGULAR": "0",
           "C3X_NO_TT_PICKER": "0", "C3X_NO_TT_VALUE": "0",
           "C3X_R31_OBSERVE": "1", "C3X_R32_OBSERVE": str(int(trace))}
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


def intervention(lines, passive, swaps):
    observed = focal(lines)
    physical = observed["bc6_pv_read"]
    if physical != passive["bc6_pv_read"] or observed["enters"] != passive["enters"]:
        raise ValueError("Treatment contaminated the prefix or used a different entry")
    effective, = fields(lines, "C3X_R32_EFFECTIVE")
    natural = Entry.parse(physical["tuple"])
    expected = {channel: swaps.get(channel, getattr(natural, channel)) for channel in ("depth", "value")}
    if {channel: int(effective[channel]) for channel in expected} != expected:
        raise ValueError("The focal read did not consume the assigned fields")
    singular, = fields(lines, "C3X_R32_SINGULAR")
    extension, = fields(lines, "C3X_R32_EXTENSION")
    verifies, = (row for row in observed["reads"] if row["mode"] == "p"
                 and row["ply"] == "2" and row["excluded"] != "0")
    rc1_read = next(row for row in observed["reads"] if row["mode"] == "p" and row["ply"] == "3"
                    and row["pv"] == "1" and row["parent"] == "b1c1")
    if (singular["threshold"], singular["depth"], physical["tuple"]) != (
        verifies["beta"], verifies["depth"], verifies["tuple"]
    ) or extension["child_depth"] != rc1_read["depth"]:
        raise ValueError("Singular or Rc1 call did not match the log")
    return dict(observed, effective=effective, singular=singular, extension=extension, rc1_read=rc1_read)


def field_cross(args):
    if digest(args.passive) != PASSIVE:
        raise ValueError("The R32 discovery result has changed")
    baseline = json.loads(args.passive.read_text())["arms"]
    target, history, _ = load_case(args)
    arms = {}
    for world, donor in (("sham", "whole_hint"), ("whole_hint", "sham")):
        expected = baseline[world]
        resident = Entry.parse(expected["bc6"]["bc6_pv_read"]["tuple"])
        opposite = Entry.parse(baseline[donor]["bc6"]["bc6_pv_read"]["tuple"])
        probes = {"control": {}, "identity": {"value": resident.value, "depth": resident.depth},
                  "value": {"value": opposite.value}, "depth": {"depth": opposite.depth},
                  "both": {"value": opposite.value, "depth": opposite.depth}}
        world_results = {}
        for arm, swaps in probes.items():
            extra = {"C3X_R32_" + channel.upper(): str(value) for channel, value in swaps.items()}
            out, lines = replay(args, args.patch, world + "-" + arm, history, target,
                                masked=world == "whole_hint", trace=True, extra=extra)
            bc6 = intervention(lines, expected["bc6"], swaps)
            world_results[arm] = {"r31": out, "bc6": bc6}
            if arm in ("control", "identity") and (out != expected["r31"] or any(
                bc6[key] != val for key, val in expected["bc6"].items()
            )):
                raise ValueError("R32 control or identity mismatched the passive result")
        if world_results["identity"] != world_results["control"]:
            raise ValueError("Assigning the current values changed the result")
        arms[world] = world_results
    return {"sources": {"r31": R31, "passive": PASSIVE, "patch": digest(args.patch)}, "arms": arms}


def same_alpha_changes(control, treatment):
    """Find the first changed score and leader at a common root threshold."""
    candidates = {row["move"]: row for row in control}
    comparables = [[candidates[row["move"]], row] for row in treatment if row["move"] in candidates
                   and row["alpha"] == candidates[row["move"]]["alpha"]]
    first_value = next((pair for pair in comparables if pair[0]["value"] != pair[1]["value"]), None)
    first_update = next((pair for pair in comparables if pair[0]["update"] != pair[1]["update"]), None)
    return {"first_value": first_value, "first_update": first_update}


def singular_controls(args):
    if digest(args.cross) != FIELD_CROSS or digest(args.passive) != PASSIVE:
        raise ValueError("Prior field-cross or discovery result changed")
    baseline = json.loads(args.cross.read_text())["arms"]
    target, history, _ = load_case(args)
    arms = {}
    for world, donor in (("sham", "whole_hint"), ("whole_hint", "sham")):
        prior = baseline[world]
        other = baseline[donor]["control"]["bc6"]
        own = prior["control"]["bc6"]
        assigned = {"control": {},
                    "value": {"value": int(other["effective"]["value"])},
                    "identity": {"window": int(own["singular"]["threshold"]),
                                 "extension": int(own["extension"]["extension"])},
                    "window": {"window": int(other["singular"]["threshold"])},
                    "extension": {"extension": int(other["extension"]["extension"])}}
        rows = {}
        for arm, swaps in assigned.items():
            env = {"C3X_R32_" + channel.upper(): str(value) for channel, value in swaps.items()}
            out, lines = replay(args, args.patch, world + "-" + arm, history, target,
                                masked=world == "whole_hint", trace=True, extra=env)
            bc6 = intervention(lines, own, swaps)
            for assigned_field, name, native_name, field in (
                ("window", "singular", "native_threshold", "threshold"),
                ("extension", "extension", "native_extension", "extension"),
            ):
                row = bc6[name]
                if int(row[field]) != swaps.get(assigned_field, int(row[native_name])):
                    raise ValueError("Inactive or unexpected " + assigned_field)
            if arm in ("control", "value"):
                prior_arm = prior[arm]
                equivalent = all({k: bc6[key][k] for k in val} == val if key in ("singular", "extension")
                                 else bc6[key] == val for key, val in prior_arm["bc6"].items())
                if out != prior_arm["r31"] or not equivalent:
                    raise ValueError("Singular overlay disturbed an inherited run")
            roots = [row for row in fields(lines, "C3X_R23_CANDIDATE") if row["attempt"] == "14"]
            if len(roots) != len({row["move"] for row in roots}):
                raise ValueError("Ambiguous focal root order")
            rows[arm] = {"r31": out, "bc6": bc6, "roots": roots, "cutoffs": fields(lines, "C3X_R32_CUTOFF")}
        if rows["identity"] != rows["control"]:
            raise ValueError("Identity intervention changed the search")
        for arm, row in rows.items():
            row["root_difference"] = same_alpha_changes(rows["control"]["roots"], row["roots"])
        arms[world] = rows
    return {"sources": {"r31": R31, "passive": PASSIVE, "cross": FIELD_CROSS,
                        "patch": digest(args.patch)}, "arms": arms}


def nested_window(args):
    if digest(args.singular) != SINGULAR_RESULTS:
        raise ValueError("Prior singular-stage experiment changed")
    base = json.loads(args.singular.read_text())["arms"]["whole_hint"]
    target, history, _ = load_case(args)
    configs = {"control": {}, "singular_window": {"window": -1961},
               "g5_only": {"g5": 1962}, "g5_repair": {"window": -1961, "g5": 1909}}
    if args.futility:
        if digest(args.futility) != NESTED_RESULTS:
            raise ValueError("Nested-window fixture changed")
        frozen = json.loads(args.futility.read_text())["arms"]
        configs.update({"g5_force_search": {"futility": 0}, "g5_force_prune": {"g5": 1962, "futility": 1}})
    arms = {}
    for arm, swaps in configs.items():
        env = {"C3X_R32_" + channel.upper(): str(value) for channel, value in swaps.items()}
        out, lines = replay(args, args.patch, arm, history, target, masked=True, trace=True, extra=env)
        bc6 = intervention(lines, base["control"]["bc6"], swaps)
        focal_g5, = fields(lines, "C3X_R32_G5")
        initial = 1962 if "window" in swaps else 1909
        if (focal_g5["before"], focal_g5["used"], focal_g5["depth"], focal_g5["key"]) != (
            str(initial), str(swaps.get("g5", initial)), "3", "15895136417853702231"
        ):
            raise ValueError("Nested g5 changed its call identity")
        nulls = fields(lines, "C3X_R32_G5_NULL")
        roots = [row for row in fields(lines, "C3X_R23_CANDIDATE") if row["attempt"] == "14"]
        if arm in ("control", "singular_window"):
            prior = base["control" if arm == "control" else "window"]
            if (out, bc6, roots) != (prior["r31"], prior["bc6"], prior["roots"]):
                raise ValueError("Nested instrumentation disturbed an inherited run")
        row = {"r31": out, "bc6": bc6, "roots": roots, "g5": focal_g5, "nulls": nulls,
               "root_difference": same_alpha_changes(arms["control"]["roots"] if arms else roots, roots)}
        if args.futility:
            if arm in frozen and row != frozen[arm]:
                raise ValueError("Futility observer disturbed a frozen run")
            gate, = fields(lines, "C3X_R32_G5_FUTILITY")
            if gate["beta"] != focal_g5["used"] or int(gate["used"]) != swaps.get("futility", int(gate["native"])):
                raise ValueError("Wrong futility decision")
            row["gate"] = gate
            row["replies"] = fields(lines, "C3X_R32_G5_REPLY")
            row["history"] = fields(lines, "C3X_R32_G5_HISTORY")
        arms[arm] = row
    return {"sources": {"r31": R31, "singular": SINGULAR_RESULTS, "patch": digest(args.patch)}, "arms": arms}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("cohort", "seal", "r31", "old", "patch", "net", "out"):
        parser.add_argument(key, type=Path)
    parser.add_argument("--passive", type=Path)
    parser.add_argument("--cross", type=Path)
    parser.add_argument("--singular", type=Path)
    parser.add_argument("--futility", type=Path)
    args = parser.parse_args()
    if args.futility and not args.singular:
        parser.error("--futility requires --singular")
    if args.cross and not args.passive:
        parser.error("--cross requires --passive")
    if args.singular:
        result = nested_window(args)
    elif args.cross:
        result = singular_controls(args)
    elif args.passive:
        result = field_cross(args)
    else:
        result = execute(args)
    write(args.out / "result.json", result)


if __name__ == "__main__":
    main()
