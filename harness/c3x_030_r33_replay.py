"""Replay the two physical early-return interventions on frozen R33 events."""
import argparse
from collections import Counter
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r29_local_tt_move import write
from c3x_030_r33_gate_panel import COHORT, digest, events, trial

DISCOVERY = "a65f4aea903d4fed86cba4cddb480acbd4f93241ace849784342332ce46cbdeb"
PRETREATMENT = ("attempt", "candidate", "root", "excluded", "tested", "parent_stage",
                "key", "ply", "depth", "alpha", "beta", "floor", "eval", "static",
                "null_eligible")


def focus(rows, target):
    matches = [row for row in rows if row["open"]["event"] == target["event"]]
    if len(matches) != 1 or any(matches[0]["open"][key] != target[key] for key in PRETREATMENT):
        raise ValueError("Target event lost its pre-intervention identity")
    return matches[0]


def source(rows, target):
    selected = [row for row in rows if row["attempt"] == target["attempt"]
                and row["move"] == target["root"]]
    return selected[0] if len(selected) == 1 else None


def replay(args, cohort, frozen):
    if digest(args.cohort) != COHORT or digest(args.discovery) != DISCOVERY:
        raise ValueError("Frozen panel or source discovery changed")
    selected = frozen["targets"]
    if args.limit:
        selected = selected[:args.limit]
    outcomes=[]
    for i, target in enumerate(selected):
        case = next(row for row in cohort["positions"] if row["id"] == target["position"])
        position = target["position"]
        record = {"target": target, "arms": {}}
        original = frozen["cases"][position]["bestmove"]
        for name, f, n in (("futility_off", True, False), ("both_off", True, True)):
            variants=[]
            for repeat in range(2):
                new = trial(args, case, f"{position}/{target['group']}/{name}-{repeat}",
                            binary=args.patch, observer=True, target=int(target["target"]["event"]),
                            skip_f=f, skip_n=n)
                selected_event = focus(new["events"], target["target"])
                if selected_event["close"]["skip_f"] != "1" or selected_event["close"]["skip_n"] != str(int(n)):
                    raise ValueError("Intervention not registered by native source")
                log = (args.out / f"{position}/{target['group']}/{name}-{repeat}/stderr.txt").read_text().splitlines()
                candidates = fields(log, "C3X_R23_CANDIDATE")
                matched = [row for row in candidates if row["id"] == target["target"]["candidate"]]
                if len(matched) > 1:
                    raise ValueError("Duplicate root candidate identity")
                new_source = matched[0] if matched else None
                if new_source and (new_source["move"] != target["target"]["root"]
                                   or new_source["attempt"] != target["target"]["attempt"]):
                    raise ValueError("Event and root-candidate link changed")
                variants.append({"target": selected_event, "best": new["proof"]["best"],
                                 "producer":new["proof"]["best_source"], "source":new_source,
                                 "uci":new["uci"],"stderr_sha256":new["trace"]})
            if any(variants[0][field] != variants[1][field] for field in
                   ("target", "best", "source", "producer", "uci")):
                raise ValueError("Repeated intervention did not reproduce")
            record["arms"][name] = variants
        record["changed"] = {name: arm[0]["best"]["move"] != original
                             for name, arm in record["arms"].items()}
        outcomes.append(record)
    return {"discovery_sha256": DISCOVERY, "cohort_sha256": COHORT, "outcomes": outcomes}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("cohort","discovery","patch","net","out"):
        parser.add_argument(name,type=Path)
    parser.add_argument("--limit",type=int)
    args=parser.parse_args()
    frozen=json.loads(args.discovery.read_text())
    cohort=json.loads(args.cohort.read_text())
    args.out.mkdir(parents=True,exist_ok=True)
    write(args.out/"result.json",replay(args,cohort,frozen))


if __name__=="__main__":
    main()
