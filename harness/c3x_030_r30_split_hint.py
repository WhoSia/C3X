"""Isolate the picker and singular verification in the exposed R29-031 trace."""
import argparse
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r23_native_replay import NET, digest, run
from c3x_030_r29_local_tt_move import trace_at, write
from c3x_030_r30_child_chain import chain

ARMS = {
    "sham": (False, False, False),
    "whole_hint": (True, False, False),
    "picker_only": (False, True, False),
    "singular_only": (False, False, True),
    "restore": (False, False, False),
}


def execute(args, history, event):
    pos = {"history": history}
    baseline = run(args.clean, pos, args.net, args.out / "upstream",
                   logging=False, paired=False, nnue=True, nodes=32000)[0]
    rows = {}
    for arm, flags in ARMS.items():
        folder = args.out / arm
        whole, picker, singular = flags
        env = {"C3X_R29_PROBES": "1", "C3X_R29_TARGET": event["seq"],
               "C3X_NO_TT_PICKER": "0", "C3X_NO_TT_VALUE": "0", "C3X_R29_MASK_VALUE": "0",
               "C3X_R29_MASK_MOVE": str(int(whole)), "C3X_R30_PICKER_ONLY": str(int(picker)),
               "C3X_R30_SKIP_SINGULAR": str(int(singular))}
        uci, proof = run(args.patch, pos, args.net, folder, logging=True, paired=False, nnue=True,
                         nodes=32000, environment=env)
        data = trace_at(folder, proof, event, roots=("g6g5", "f6g7"))
        lines = (folder / "stderr.txt").read_text().splitlines()
        gates = {kind: fields(lines, f"C3X_R30_{kind.upper()}") for kind in ("picker", "singular")}
        if gates["picker"] != [{"seq": event["seq"], "skip": str(int(picker))}]:
            raise ValueError(f"Picker gate mismatch at {arm}")
        if gates["singular"] != ([] if whole else [{"seq": event["seq"], "skip": str(int(singular))}]):
            raise ValueError(f"Singular gate mismatch at {arm}")
        if len(data["masked"]) != int(whole):
            raise ValueError(f"Unexpected whole hint at {arm}")
        if arm in ("sham", "restore") and uci != baseline:
            raise ValueError("The refined build changed untreated UCI")
        rows[arm] = {"trace": data, "chain": chain(folder / "stderr.txt", data), "gates": gates, "uci": uci}
    if rows["sham"] != rows["restore"]:
        raise ValueError("Restored behavior differs")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("cohort", "seal", "clean", "patch", "net", "out"):
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    data = json.loads(args.seal.read_text())
    if data["assets"]["cohort"] != digest(args.cohort) or digest(args.net) != NET:
        raise ValueError("Frozen source mismatch")
    selected, = (row for row in data["positions"] if row["id"] == "R29-031")
    event = selected["targets"]["fallback"]
    if (event["seq"], event["hint"], event["attempt"]) != ("233", "b5c6", "14"):
        raise ValueError("Unexpected frozen target")
    cohort = json.loads(args.cohort.read_text())
    case, = (row for row in cohort["positions"] if row["id"] == "R29-031")
    rows = execute(args, case["moves"], event)
    write(args.out / "result.json",
          {"source_sha256": digest(args.seal), "patch_binary_sha256": digest(args.patch), "arms": rows})


if __name__ == "__main__":
    main()
