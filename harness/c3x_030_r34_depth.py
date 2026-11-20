"""Compare the same completed search depth for the R33 selected final flips."""
import argparse
import json
from pathlib import Path

from c3x_030_r29_local_tt_move import write
from c3x_030_r30_public_iteration import public_view
from c3x_030_r33_gate_panel import COHORT, digest, trial
from c3x_030_r33_replay import PRETREATMENT

SUMMARY = "b5f03e9e773467d4ef8e46c9a637626e5a7b691f21116d7a115236eacf31bf67"
REPLAY = "367f7bf4e3993312f41bdccaeb59caf77f97f28c0609d18144513d55e55cad9b"


def event_match(rows, target):
    matches = [row for row in rows if row["open"]["event"] == target["event"]]
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError("Reached a duplicate target event")
    event=matches[0]
    if any(event["open"][key] != target[key] for key in PRETREATMENT):
        raise ValueError("Reached a different target read")
    return event


def fixed_depth(args, cases, summary, replay):
    original = {case["id"]:case for case in cases["positions"]}
    experiments = {(row["target"]["position"], row["target"]["group"]):row
                   for row in replay["outcomes"]}
    selected = [row for row in summary["per_target"] if row["arms"]["both_off"]["final_changed"]]
    if len(selected) != 11:
        raise ValueError("Expected all eleven R33 flips")
    results=[]
    for row in selected:
        name, group = row["position"], row["stratum"]
        history=original[name]
        treatment=experiments[(name,group)]["arms"]["both_off"][0]
        targets={int(row["original_best"]["completed"]),
                 int(treatment["best"]["completed"])}
        if 0 in targets:
            raise ValueError("Invalid completed depth")
        for depth in sorted(targets):
            arms={}
            for arm in ("control","both_off"):
                observed=[]
                for repeat in range(2):
                    receipt=trial(args,history,f"{name}/{group}/{depth}/{arm}-{repeat}",
                                  binary=args.patch, observer=True,
                                  target=int(row["target"]["event"]),
                                  skip_f=arm=="both_off", skip_n=arm=="both_off" and group=="1",
                                  nodes=None, depth=depth)
                    event=event_match(receipt["events"],row["target"])
                    if not event or event["close"]["stopped"] != "0":
                        raise ValueError("Target absent or interrupted under fixed depth")
                    if (receipt["proof"]["best"]["completed"] != str(depth)
                            or public_view("\n".join(receipt["uci"]))["iterations"][-1][0] != depth):
                        raise ValueError("Depth-limited run stopped prematurely")
                    observed.append({"best":receipt["proof"]["best"],
                                     "producer":receipt["proof"]["best_source"],
                                     "event":event,
                                     "public":public_view("\n".join(receipt["uci"])),
                                     "stderr_sha256":receipt["trace"]})
                if observed[0] != observed[1]:
                    raise ValueError("Fixed-depth repeat differs")
                arms[arm] = observed[0]
            results.append({"position":name,"stratum":group,"depth":depth,
                            "node_limited_original":row["original_best"]["move"],
                            "node_limited_treatment":treatment["best"]["move"],
                            "arms":arms,"fixed_depth_changed":arms["control"]["best"]["move"] != arms["both_off"]["best"]["move"]})
    return {"source_sha256":{"cohort":COHORT,"summary":SUMMARY,"replay":REPLAY,
                             "patched_binary":digest(args.patch)},
            "results":results}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ("cohort","summary","replay","patch","net","out"):
        parser.add_argument(key,type=Path)
    args=parser.parse_args()
    if (digest(args.cohort),digest(args.summary),digest(args.replay)) != (COHORT,SUMMARY,REPLAY):
        raise ValueError("The earlier panel changed")
    args.out.mkdir(parents=True,exist_ok=True)
    result=fixed_depth(args,json.loads(args.cohort.read_text()),
                       json.loads(args.summary.read_text()),
                       json.loads(args.replay.read_text()))
    write(args.out/"result.json",result)


if __name__=="__main__":
    main()
