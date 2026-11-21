"""Apply frozen recommendation, reply and TT event selection to unseen games."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r23_native_replay import NET, digest
from c3x_030_r28_reliance import measure
from c3x_030_r29_local_tt_move import probe_signature, replay, trace_at, write


def stratum(margins):
    if len(margins) != 2 or None in margins:
        return "point-unavailable"
    low, high = sorted(margins)
    if low <= -15 and high >= 15:
        return "depth-reversal"
    if low >= 100 or high <= -100:
        return "large-stable"
    if low >= -30 and high <= 30:
        return "close"
    return "intermediate"


def choose_events(probes, cutoffs, producer, foil, reply):
    eligible = [row for row in probes if row["root"] == foil and row["excluded"] == "0"
                and int(row["attempt"]) <= producer and row["hit"] == "1"]
    moves = [row for row in eligible if row["hint"] == reply]
    cutoff_ids = {row["seq"] for row in cutoffs}
    values = [row for row in eligible if int(row["attempt"]) == producer and row["seq"] in cutoff_ids]
    targets = {}
    if moves:
        latest = max(int(row["attempt"]) for row in moves)
        targets["move"] = next(row for row in moves if int(row["attempt"]) == latest)
    if values:
        targets["value"] = values[0]
    return targets


def observe(case, clean, patched, net, berserk, berserk_net, output):
    outcome = measure(case, clean, berserk, berserk_net)
    item = {"history": case["moves"]}
    dirs = output / case["id"]
    observed, _ = replay(clean, item, net, dirs / "clean", logging=False, probe=False)
    plain, proof = replay(patched, item, net, dirs / "sham")
    if plain != observed or proof["best"]["move"] != outcome["recommendation"]:
        raise ValueError(f"Noninterference failed at {case['id']}")
    log_path = dirs / "sham" / "stderr.txt"
    log = log_path.read_text().splitlines()
    foil = outcome["alternative"]
    deep = outcome["judge"]["rows"][-1]["measurements"][foil]["point"]
    reply = deep["pv"][0] if deep and deep["pv"] else None
    producer = int(proof["best_source"]["attempt"])
    targets = choose_events(fields(log, "C3X_R29_PLY1"), fields(log, "C3X_R29_CUTOFF"),
                            producer, foil, reply)
    write(dirs / "targets.json", {"discovery_trace_sha256": digest(log_path),
                                  "independent_reply": reply, "targets": targets})
    row = {
        "id": case["id"],
        "source": outcome,
        "stratum": stratum([entry["margin_cp"] for entry in outcome["judge"]["rows"]]),
        "independent_reply": reply,
        "source_attempt": producer,
        "arms": {},
    }
    for policy, target in targets.items():
        arms = {}
        for arm in ("mask", "restore"):
            folder = dirs / f"{policy}-{arm}"
            uci, arm_proof = replay(patched, item, net, folder,
                                    target=int(target["seq"]), mask=arm == "mask", policy=policy)
            data = trace_at(folder, arm_proof, target, roots=(outcome["recommendation"], foil))
            if probe_signature(data["read"]) != probe_signature(target):
                raise ValueError("Unexpected pre-treatment divergence")
            if len(data["masked"]) != int(arm == "mask"):
                raise ValueError("Unexpected mask count")
            if data["read"][f"mask_{policy}"] != str(int(arm == "mask")):
                raise ValueError("Wrong mask channel")
            if arm == "restore" and (uci != plain or log_path.read_bytes() !=
                                      (folder / "stderr.txt").read_bytes()):
                raise ValueError("Restore did not reproduce")
            arms[arm] = data
            data["uci_changed"] = uci != plain
        arms["sham"] = trace_at(dirs / "sham", proof, target, roots=(outcome["recommendation"], foil))
        row["arms"][policy] = arms
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("cohort", "clean", "patched", "net", "berserk", "berserk_net", "output"):
        parser.add_argument(arg, type=Path)
    parser.add_argument("--cohort-sha256", required=True)
    args = parser.parse_args()
    assets = {name: digest(getattr(args, name))
              for name in ("cohort", "clean", "patched", "net", "berserk", "berserk_net")}
    if assets["cohort"] != args.cohort_sha256 or assets["net"] != NET:
        raise ValueError("Unexpected frozen history or NNUE")
    args.output.mkdir()
    cases = json.loads(args.cohort.read_text())["positions"]
    engines = [getattr(args, name).resolve() for name in ("clean", "patched", "net", "berserk", "berserk_net")]
    with ThreadPoolExecutor(max_workers=4) as pool:
        positions = list(pool.map(lambda case: observe(case, *engines, args.output), cases))
    write(args.output / "result.json", {"assets": assets, "positions": positions})


if __name__ == "__main__":
    main()
