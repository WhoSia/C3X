"""Seal baseline selections, then test the observed-reply fallback on each frozen history."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r23_native_replay import NET, digest
from c3x_030_r28_reliance import measure
from c3x_030_r29_local_tt_move import replay, trace_at, write
from c3x_030_r29_unseen import choose_events, stratum


def select(probes, cutoffs, replies, producer, foil, reference_reply):
    targets = choose_events(probes, cutoffs, producer, foil, reference_reply)
    if "move" in targets:
        return targets
    first_replies = {}
    for reply in replies:
        first_replies.setdefault(reply["seq"], reply["move"])
    cutoff_ids = {row["seq"] for row in cutoffs}
    fallback = [row for row in probes
                if row["root"] == foil and row["excluded"] == "0" and row["hit"] == "1"
                and int(row["attempt"]) <= producer and row["seq"] not in cutoff_ids
                and bool(first_replies.get(row["seq"])) and row["hint"] == first_replies[row["seq"]]]
    if fallback:
        latest = max(int(row["attempt"]) for row in fallback)
        targets["fallback"] = next(row for row in fallback if int(row["attempt"]) == latest)
    return targets


def discover(case, bins, output):
    clean, patched, net, berserk, berserk_net = bins
    pos = {"history": case["moves"]}
    directory = output / case["id"]
    source = measure(case, clean, berserk, berserk_net)
    control, _ = replay(clean, pos, net, directory / "clean", logging=False, probe=False)
    logged, proof = replay(patched, pos, net, directory / "baseline")
    if logged != control or proof["best"]["move"] != source["recommendation"]:
        raise ValueError(f"Unexpected source behavior in {case['id']}")
    log = directory / "baseline" / "stderr.txt"
    lines = log.read_text().splitlines()
    opponent = source["alternative"]
    point = source["judge"]["rows"][-1]["measurements"][opponent]["point"]
    reply = point["pv"][0] if point and point["pv"] else None
    producer = int(proof["best_source"]["attempt"])
    targets = select(fields(lines, "C3X_R29_PLY1"), fields(lines, "C3X_R29_CUTOFF"),
                     fields(lines, "C3X_R29_REPLY"), producer, opponent, reply)
    return {
        "id": case["id"], "source": source, "reference_reply": reply,
        "source_attempt": producer,
        "stratum": stratum([entry["margin_cp"] for entry in source["judge"]["rows"]]),
        "trace_sha256": digest(log), "uci": logged, "targets": targets,
        "sham": {channel: trace_at(directory / "baseline", proof, event,
                                   roots=(source["recommendation"], opponent))
                 for channel, event in targets.items()},
    }


def test_case(case, receipt, bins, output):
    _, patched, net, _, _ = bins
    if receipt["id"] != case["id"]:
        raise ValueError("Frozen receipts and corpus do not agree")
    path = output / case["id"]
    source = receipt["source"]
    roots = (source["recommendation"], source["alternative"])
    arms = {}
    for channel, event in receipt["targets"].items():
        policy = "value" if channel == "value" else "move"
        results = {}
        for arm in ("mask", "restore"):
            folder = path / f"{channel}-{arm}"
            uci, proof = replay(patched, {"history": case["moves"]}, net, folder,
                                target=int(event["seq"]), mask=arm == "mask", policy=policy)
            result = trace_at(folder, proof, event, roots=roots)
            masked = arm == "mask"
            if len(result["masked"]) != int(masked) or result["read"][f"mask_{policy}"] != str(int(masked)):
                raise ValueError(f"Invalid {channel} {arm} at {case['id']}")
            other = "move" if policy == "value" else "value"
            if result["read"][f"mask_{other}"] != "0":
                raise ValueError(f"Unexpected second intervention in {case['id']}")
            if arm == "restore" and (digest(folder / "stderr.txt") != receipt["trace_sha256"]
                                     or uci != receipt["uci"] or result != receipt["sham"][channel]):
                raise ValueError(f"Restored behavior differs in {case['id']}")
            result["uci_changed"] = uci != receipt["uci"]
            results[arm] = result
        arms[channel] = {"sham": receipt["sham"][channel], **results}
    return {key: receipt[key] for key in ("id", "source", "source_attempt", "stratum")} | {"arms": arms}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("discover", "intervene"))
    for arg in ("cohort", "clean", "patched", "net", "berserk", "berserk_net", "work", "seal"):
        parser.add_argument(arg, type=Path)
    parser.add_argument("--cohort-sha256", required=True)
    parser.add_argument("--seal-sha256")
    args = parser.parse_args()
    binaries = ("clean", "patched", "net", "berserk", "berserk_net")
    assets = {key: digest(getattr(args, key)) for key in ("cohort", *binaries)}
    if assets["cohort"] != args.cohort_sha256 or assets["net"] != NET:
        raise ValueError("Unexpected cohort or Stockfish NNUE")
    bins = [getattr(args, key).resolve() for key in binaries]
    cases = json.loads(args.cohort.read_bytes())["positions"]
    args.work.mkdir(exist_ok=False)
    with ThreadPoolExecutor(max_workers=4) as pool:
        if args.phase == "discover":
            positions = list(pool.map(lambda case: discover(case, bins, args.work), cases))
            write(args.seal, {"assets": assets, "positions": positions})
        else:
            if digest(args.seal) != args.seal_sha256:
                raise ValueError("Missing or invalid preintervention SHA-256")
            seal = json.loads(args.seal.read_bytes())
            if seal["assets"] != assets:
                raise ValueError("Engine or history differs from the discovery run")
            receipts = seal["positions"]
            list(zip(cases, receipts, strict=True))
            positions = list(pool.map(lambda c, r: test_case(c, r, bins, args.work), cases, receipts))
            write(args.work / "result.json", {"assets": assets, "positions": positions})


if __name__ == "__main__":
    main()
