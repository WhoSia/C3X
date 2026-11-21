"""C3X 0.31/P1: extract untouched public and pre-treatment native features.

Reads immutable full R33 TWIC1671 ZIP. Never uses treated outcomes as features.
This is historical development, not newly obtained native search data.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

ZIP_SHA = "e72ba91c0ffdbbb075642f044706d356fca84b4fa257a3ebcb7755db5837d8bd"
COHORT_SHA = "51bf007c7941afe29007ee295378a3ff701d014d649bc40682ba65db6be765a4"
DISCOVERY_SHA = "a65f4aea903d4fed86cba4cddb480acbd4f93241ace849784342332ce46cbdeb"
REPLAY_SHA = "367f7bf4e3993312f41bdccaeb59caf77f97f28c0609d18144513d55e55cad9b"
MANIFEST_N = 1414


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def raw_fields(raw, tag):
    out = []
    for line in raw.decode().splitlines():
        if line.startswith(tag + " "):
            pairs = [part.split("=", 1) for part in line.split()[1:]]
            require(all(len(p) == 2 for p in pairs)
                    and len({k for k, _ in pairs}) == len(pairs),
                    "malformed native " + tag)
            out.append(dict(pairs))
    return out


def last_public(raw):
    rows, best = [], []
    for line in raw.decode().splitlines():
        p = line.split()
        if p[:2] == ["info", "depth"]:
            require("score" in p and "pv" in p, "incomplete public info")
            k, v = p.index("score"), p.index("pv")
            bound = 1 if "lowerbound" in p else 2 if "upperbound" in p else 0
            require(not ("lowerbound" in p and "upperbound" in p),
                    "contradictory public bounds")
            rows.append((int(p[2]), p[k + 1], int(p[k + 2]),
                         len(p[v + 1:]), bound))
        if p[:1] == ["bestmove"]:
            best.append(p[1])
    require(rows and len(best) == 1, "missing public result")
    last = rows[-1]
    require(last[1] == "cp", "non-cp terminal evaluation needs a new protocol")
    return (last[0], last[2], last[3],
            int(last[4] == 2), int(last[4] == 1)), best[0]


def audit(path):
    require(sha(Path(path).read_bytes()) == ZIP_SHA, "wrong R33 archive SHA")
    with ZipFile(path) as z:
        require(z.testzip() is None, "native ZIP CRC mismatch")
        names = z.namelist()
        require(len(names) == len(set(names)), "duplicate ZIP path")
        manifest = z.read("SHA256SUMS").decode().splitlines()
        require(len(manifest) == MANIFEST_N, "manifest count mismatch")
        seen = set()
        for entry in manifest:
            matched = re.fullmatch(r"([0-9a-f]{64})  (.+)", entry)
            require(matched is not None, "bad manifest row")
            digest, name = matched.groups()
            require(name in names and name not in seen, "missing or duplicate member")
            seen.add(name)
            require(sha(z.read(name)) == digest, "bad original member SHA " + name)
        require(set(names) == seen | {"SHA256SUMS"}, "unmanifested source entry")
        for path_name, expected in [
            ("cohort.json", COHORT_SHA),
            ("discovery/discovery.json", DISCOVERY_SHA),
            ("replay/result.json", REPLAY_SHA),
        ]:
            require(sha(z.read(path_name)) == expected,
                    "wrong inherited native JSON: " + path_name)
        cohort = json.loads(z.read("cohort.json"))
        discovery = json.loads(z.read("discovery/discovery.json"))
        replay = json.loads(z.read("replay/result.json"))
        require(len(cohort["positions"]) == 64 and len(replay["outcomes"]) == 128,
                "wrong game/event denominator")
        require(discovery["node_budget"] == 32000, "unexpected original budget")
        positions = {x["id"]: x for x in cohort["positions"]}
        require(len(positions) == 64
                and len({x["game_sha256"] for x in positions.values()}) == 64,
                "duplicated source games")
        require(len({x["family"] for x in positions.values()}) == 16,
                "incorrect event-family strata")
        selected = {(e["position"], e["group"]): e["target"]
                    for e in discovery["targets"]}
        require(len(selected) == 128, "duplicated nominated physical event")
        rows = []
        for record in replay["outcomes"]:
            meta = record["target"]
            name, group, target = meta["position"], meta["group"], meta["target"]
            require(group in ("0", "1") and name in positions
                    and selected.get((name, group)) == target,
                    "source nomination mismatch")
            require(meta["baseline"] == discovery["cases"][name]["bestmove"],
                    "untreated source best mismatch")
            public = z.read(f"discovery/{name}/observed/stdout.txt")
            (depth, cp, pvlen, upper, lower), best = last_public(public)
            require(best == meta["baseline"], "original actual UCI disagrees")
            opened = raw_fields(z.read(f"discovery/{name}/observed/stderr.txt"),
                                "C3X_R33_OPEN")
            found = [r for r in opened if r.get("event") == target["event"]]
            require(len(found) == 1 and found[0] == target,
                    "actual pre-treatment event not source-identified")
            treatment = record["arms"]["both_off"]
            require(len(treatment) == 2, "missing repeated treatment")
            for repeat, arm in enumerate(treatment):
                require(arm["target"]["open"] == target,
                        "treatment changed pre-contact source identity")
                close = arm["target"]["close"]
                require(close["skip_f"] == close["skip_n"] == "1"
                        and close["stopped"] == "0", "source treatment absent")
                prefix = f"replay/{name}/{group}/both_off-{repeat}/"
                _, real_best = last_public(z.read(prefix + "stdout.txt"))
                require(real_best == arm["best"]["move"],
                        "native treated UCI outcome mismatched")
                require(sha(z.read(prefix + "stderr.txt")) == arm["stderr_sha256"],
                        "native stderr SHA mismatched")
            require(treatment[0] == treatment[1], "original repeated run inconsistent")
            slack = int(target["floor"]) - int(target["beta"])
            require(slack >= 0 and target["null_eligible"] == group,
                    "selected early-return gate was not eligible")
            rows.append({
                "id": name + "-" + group,
                "game": positions[name]["game_sha256"],
                "family": positions[name]["family"],
                "stratum": int(group),
                "public_depth": depth,
                "public_score_cp": cp,
                "public_pv_len": pvlen,
                "public_upper_bound": upper,
                "public_lower_bound": lower,
                "source_depth": int(target["depth"]),
                "source_ply": int(target["ply"]),
                "futility_slack": slack,
                "source_progress_nodes": int(target["nodes"]),
                "source_attempt": int(target["attempt"]),
                "source_root_is_public_best": int(target["root"] == best),
                "y": int(treatment[0]["best"]["move"] != best),
            })
        require(len({x["id"] for x in rows}) == 128, "duplicated physical contrast")
        require(all(len([x for x in rows if x["game"] == p["game_sha256"]]) == 2
                    for p in positions.values()), "two targets per source game not retained")
        require({k: sum(x["y"] for x in rows if x["stratum"] == k)
                 for k in (0, 1)} == {0: 4, 1: 7}, "source effects do not match R33")
        kinds = {
            "exact": sum(not x["public_upper_bound"] and not x["public_lower_bound"]
                         for x in rows),
            "upper": sum(x["public_upper_bound"] for x in rows),
            "lower": sum(x["public_lower_bound"] for x in rows),
        }
        require(kinds == {"exact": 68, "upper": 46, "lower": 14},
                "public bound type removed")
    return {
        "schema": "c3x-031-p1-native-pre-treatment-features-v1",
        "classification": "RETROSPECTIVE_EXPOSED_R33_NO_NEW_NATIVE_SEARCH",
        "source_archive_sha256": ZIP_SHA,
        "source_archive_manifest_count": MANIFEST_N,
        "cohort_sha256": COHORT_SHA,
        "discovery_sha256": DISCOVERY_SHA,
        "replay_sha256": REPLAY_SHA,
        "source_game_count": 64,
        "physical_target_count": 128,
        "event_family_count": 16,
        "positives_by_stratum": {"0": 4, "1": 7},
        "rows": sorted(rows, key=lambda x: x["id"]),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archive", type=Path)
    ap.add_argument("out", type=Path)
    args = ap.parse_args()
    receipt = audit(args.archive)
    args.out.write_text(json.dumps(receipt, sort_keys=True,
                                   separators=(",", ":")) + "\n")
    print("P1_SOURCE_COURT", len(receipt["rows"]), "effects",
          sum(r["y"] for r in receipt["rows"]),
          "receipt_sha256", sha(args.out.read_bytes()))


if __name__ == "__main__":
    main()
