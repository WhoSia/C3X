"""Check R31-to-R33 observer parity at each fixed-depth diagnosis."""
import argparse
import json
from pathlib import Path

from c3x_030_r23_native_replay import NET,digest
from c3x_030_r29_local_tt_move import write
from c3x_030_r30_public_iteration import public_view
from c3x_030_r33_gate_panel import COHORT,trial


def execute(args):
    if digest(args.cohort)!=COHORT or digest(args.net)!=NET:
        raise ValueError("Source identity mismatch")
    cases={row["id"]:row for row in json.loads(args.cohort.read_text())["positions"]}
    combinations={(row["position"],row["depth"]) for row in json.loads(args.depth.read_text())["results"]}
    records=[]
    for position,depth in sorted(combinations):
        case=cases[position]
        old=trial(args,case,f"{position}-{depth}/r31",binary=args.old,observer=False,nodes=None,depth=depth)
        off=trial(args,case,f"{position}-{depth}/r33-off",binary=args.patch,observer=False,nodes=None,depth=depth)
        if old["uci"]!=off["uci"] or old["proof"]!=off["proof"] or off["events"]:
            raise ValueError("Fixed-depth binary parity failed")
        original=[row for row in json.loads(args.depth.read_text())["results"]
                  if row["position"]==position and row["depth"]==depth]
        for row in original:
            control=row["arms"]["control"]
            if (control["best"]!=off["proof"]["best"] or
                    control["public"]!=public_view("\n".join(off["uci"]))):
                raise ValueError("Observed fixed-depth baseline differs")
        records.append({"position":position,"depth":depth,"best":old["proof"]["best"],
                        "old_binary":digest(args.old),"patch_binary":digest(args.patch)})
    return records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ("cohort","depth","old","patch","net","out"):
        parser.add_argument(key,type=Path)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    write(args.out/"result.json",execute(args))


if __name__=="__main__":
    main()
