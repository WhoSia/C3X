"""0.31 P2-L1: immutable original R26↔P2 tournament-family overlap audit.

Reads the original publisher PGN, original R26 selected ordinal/hash receipt,
the exactly frozen P2 64 full-history sample and its 128 signed native treatments.
No new native search, no refit, no post-outcome resampling. Excluding known
R26-shared source families is POST-HOC historical sensitivity, not the P2 primary.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import random
import unicodedata
import zipfile

SOURCE_ZIP_SHA = "6e6866cfe57ea0db7849f9b686fded1c1fe9d1fcab783359030b97ace377eccf"
SOURCE_PGN_SHA = "bb166b4813aca824d4455ee51d0bbe3be75405586b310639c3eedfe02a32b77d"
P2_GAME_SHA = "2a174dcf56a333408693785eb0a844a419f7f8ba090c0a00187f3dab483d57e4"
P2_TREATMENT_SHA = "69904f920c21844f2a2f278f6332b7c8fdc9857a821c33fdc0f29dfa56aaf09f"
MODEL_SHA = "f27a89fd15efa3f35738ba8cf2a6d1243c8336268e4661c653bbd1e6c0bfee23"
BOOTSTRAP = 2000
BOOT_SEED = 310221


def h(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def norm(raw: str) -> str:
    return unicodedata.normalize("NFC", raw).strip().casefold()


def read_publisher(path: Path) -> list[str]:
    raw = path.read_bytes()
    require(h(raw) == SOURCE_ZIP_SHA, "original TWIC1670 ZIP byte identity changed")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        require(z.testzip() is None and z.namelist() == ["twic1670.pgn"],
                "unexpected publisher PGN ZIP structure")
        pgn = z.read("twic1670.pgn")
    require(h(pgn) == SOURCE_PGN_SHA, "original PGN byte identity changed")
    lines = pgn.decode("latin-1").splitlines()
    event_headers = []
    for line in lines:
        if line.startswith('[Event "'):
            require(line.endswith('"]'), "malformed original Event header")
            event_headers.append(line[8:-2])
    require(len(event_headers) == 8391, "publisher game ordinal census mismatch")
    return event_headers


def read_json(path: Path, expected_sha: str | None = None) -> dict:
    raw = path.read_bytes()
    if expected_sha is not None:
        require(h(raw) == expected_sha, "original sealed JSON SHA changed: " + path.name)
    return json.loads(raw)


def brier(rows: list[dict], model: str) -> float:
    return sum((r[model] - r["y"]) ** 2 for r in rows) / len(rows)


def logloss(rows: list[dict], model: str) -> float:
    return -sum(r["y"] * math.log(r[model]) +
                (1 - r["y"]) * math.log1p(-r[model]) for r in rows) / len(rows)


def ap(rows: list[dict], model: str) -> float | None:
    total_positive = sum(r["y"] for r in rows)
    if total_positive == 0:
        return None
    # Tied probability groups are handled without row-order dependence.
    bins: dict[float, list[int]] = defaultdict(lambda: [0, 0])
    for r in rows:
        bins[r[model]][0] += 1
        bins[r[model]][1] += r["y"]
    seen = captured = 0
    result = 0.0
    for probability in sorted(bins, reverse=True):
        n, hits = bins[probability]
        seen += n
        captured += hits
        if hits:
            result += (hits / total_positive) * (captured / seen)
    return result


def metrics(rows: list[dict]) -> dict:
    require(rows, "cannot rank empty sensitivity sample")
    return {
        model: {
            "brier": brier(rows, model),
            "log_loss": logloss(rows, model),
            "average_precision": ap(rows, model),
            "threshold_0_5_predicted_positive": sum(r[model] >= 0.5 for r in rows),
            "threshold_0_5_true_positive": sum(r[model] >= 0.5 and r["y"]
                                              for r in rows),
        } for model in ("m0", "m1", "m2")
    }


def uncertainty(rows: list[dict]) -> dict:
    fams = sorted({r["family"] for r in rows})
    groups = {f: [r for r in rows if r["family"] == f] for f in fams}
    rng = random.Random(BOOT_SEED)
    differences = {"m0_minus_m2": [], "m1_minus_m2": []}
    for _ in range(BOOTSTRAP):
        sample = [r for f in (rng.choice(fams) for _ in fams) for r in groups[f]]
        for tag, base in (("m0_minus_m2", "m0"), ("m1_minus_m2", "m1")):
            differences[tag].append(brier(sample, base) - brier(sample, "m2"))
    result = {}
    for tag, arr in differences.items():
        arr.sort()
        source = tag[:2]
        result[tag] = {
            "gain": brier(rows, source) - brier(rows, "m2"),
            "family_bootstrap_95": [arr[50], arr[1949]],
        }
    return result


def audit(source_path: Path, prior_path: Path, game_path: Path,
          treated_path: Path) -> dict:
    headers = read_publisher(source_path)
    prior = read_json(prior_path)
    freeze = read_json(game_path, P2_GAME_SHA)
    treatment = read_json(treated_path, P2_TREATMENT_SHA)

    old_source = prior["sources"]["twic1670"]
    require(old_source["archive_sha256"] == SOURCE_ZIP_SHA
            and old_source["pgn_sha256"] == SOURCE_PGN_SHA
            and old_source["records"] == 8391,
            "R26 did not use the same identified original publisher")
    r26 = [x for x in prior["game_history_hashes"]
           if x["id"].startswith("twic1670-")]
    require(len(r26) == 16 and
            len({r["game_sha256"] for r in r26}) == 16 and
            len({r["ordinal"] for r in r26}) == 16,
            "R26 old issue event sample denominator changed")
    require(all(1 <= x["ordinal"] <= len(headers) for x in r26),
            "invalid original R26 game ordinal")
    previous_families = {norm(headers[r["ordinal"] - 1]) for r in r26}
    previous_hashes = {r["game_sha256"] for r in r26}

    require(freeze["source_treatments_observed"] == 0 and
            len(freeze["sample"]) == 64,
            "P2 cohort not originally source-frozen before treatment")
    require(freeze["raw_source_sha256"] == SOURCE_ZIP_SHA and
            freeze["selected_event_family_count"] == 17,
            "wrong P2 publisher/family freeze")
    games = {row["id"]: row for row in freeze["sample"]}
    require(len(games) == 64 and
            len({g["game_sha256"] for g in games.values()}) == 64,
            "repeated P2 selected game")
    for row in games.values():
        require(norm(headers[row["source_ordinal"] - 1]) == row["family"],
                "P2 selection ordinal does not match actual publisher family")

    sample_families = {r["family"] for r in games.values()}
    shared = previous_families.intersection(sample_families)
    require(shared == {"fide world open u20 rapid", "world girls u20 blitz"},
            "historical R26 family collisions differ from re-audited original")
    game_overlap = {r["game_sha256"] for r in games.values()} & previous_hashes
    require(not game_overlap, "P2 full game accidentally repeated an R26 game")

    require(treatment["original_legal_game_sample_sha256"] == P2_GAME_SHA
            and treatment["original_p1_train_model_sha256"] == MODEL_SHA
            and treatment["observed_effect_denominator"] == 128
            and treatment["physical_target_statuses"] ==
              {"ACTUAL_SOURCE_TREATMENT_OBSERVED": 128}
            and treatment["new_source_native_searches_attempted"] == 576
            and len(treatment["cases"]) == 64,
            "incorrect actual signed P2 native treatment world")
    rows = []
    source_ids = set()
    for case in treatment["cases"]:
        name = case["id"]
        require(name in games and name not in source_ids,
                "duplicated/unknown original source game")
        source_ids.add(name)
        require(case["family"] == games[name]["family"] and
                case["game_sha256"] == games[name]["game_sha256"],
                "source game identity changed between freeze and treatment")
        require(set(case["targets"]) == {"0", "1"},
                "target stratum censored or replaced")
        for stratum, obs in case["targets"].items():
            require(obs["status"] == "ACTUAL_SOURCE_TREATMENT_OBSERVED" and
                    type(obs["treatment_bestmove_changed"]) is bool,
                    "physically unreachable source target was treated as negative")
            probs = obs["frozen_predictions"]
            require(set(probs) == {"m0", "m1", "m2"} and
                    all(type(v) is float and 0 < v < 1 for v in probs.values()),
                    "post-outcome replacement or invalid locked risk")
            rows.append({
                "id": name + "-" + stratum,
                "game": case["game_sha256"],
                "family": case["family"],
                "y": int(obs["treatment_bestmove_changed"]),
                **probs
            })
    require(len(rows) == 128 and len(source_ids) == 64,
            "incomplete original P2 events")
    rows.sort(key=lambda r: r["id"])
    require(sum(r["y"] for r in rows) == 7, "original positive source total drift")
    reported = treatment["result_over_eligible_events"]["scores"]
    for model in ("m0", "m1", "m2"):
        require(math.isclose(brier(rows, model), reported[model]["brier"],
                             rel_tol=0, abs_tol=1e-12),
                "existing signed P2 summary does not match original pairs")
    keep = [r for r in rows if r["family"] not in shared]
    omit = [r for r in rows if r["family"] in shared]
    require(len(keep) == 112 and len(omit) == 16
            and len({r["game"] for r in keep}) == 56
            and len({r["game"] for r in omit}) == 8
            and len({r["family"] for r in keep}) == 15
            and sum(r["y"] for r in keep) == 7
            and sum(r["y"] for r in omit) == 0,
            "lineage-exclusion sensitivity denominator drift")

    original_metrics = metrics(rows)
    retained_metrics = metrics(keep)
    original_uncertainty = uncertainty(rows)
    retained_uncertainty = uncertainty(keep)
    require(original_uncertainty["m1_minus_m2"]["gain"] < 0
            and original_uncertainty["m0_minus_m2"]["gain"] < 0
            and retained_uncertainty["m1_minus_m2"]["gain"] < 0
            and retained_uncertainty["m0_minus_m2"]["gain"] < 0,
            "published P2 negative changed sign under correction; amend conclusion")

    return {
        "id": "C3X_031_P2_L1_R26_EVENT_FAMILY_RETROSPECTIVE_LEAKAGE_AUDIT",
        "classification": "POSTOUTCOME_HISTORICAL_EXPOSURE_SENSITIVITY",
        "original_P2_primary_analysis_modified": False,
        "new_native_engine_searches": 0,
        "original_tw ic1670_source_sha256".replace(" ",""): SOURCE_ZIP_SHA,
        "original_R26_game_history_count": 16,
        "original_R26_distinct_source_event_families": len(previous_families),
        "R26_and_P2_shared_tournament_families": sorted(shared),
        "R26_and_P2_identical_full_game_histories": len(game_overlap),
        "original_P2": {
            "games": 64, "events": 128, "families": 17, "root_flips": 7,
            "scores": original_metrics, "brier_difference_95ci": original_uncertainty
        },
        "P2_R26_shared_family_subset": {
            "games": 8, "events": 16, "families": 2, "root_flips": 0,
            "event_ids": [r["id"] for r in omit],
        },
        "P2_excluding_R26_shared_families_POSTHOC": {
            "games": 56, "events": 112, "families": 15, "root_flips": 7,
            "scores": retained_metrics,
            "brier_difference_95ci": retained_uncertainty,
            "all_original_7_chess_move_switches_retained": True,
            "predictive_result": "NEGATIVE_TRANSFER_REMAINS",
        },
        "scientific_corrections": [
            "P2 has zero identity overlap with 16 R26 selected whole game histories",
            "P2 is not fully R26 tournament-event-family independent",
            "P2 and R26 used the same full TWIC1670 publisher file",
            "P2 family exclusion is retrospective and not a substitute for blind prespecified P2",
            "Negative M2 Brier gain survives deletion of previously seen R26 families",
            "No unique causal mediator, strategy merit or human learning effect measured",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("original_twic1670_zip", type=Path)
    p.add_argument("prior_r26_json", type=Path)
    p.add_argument("p2_original_full_game_freeze_json", type=Path)
    p.add_argument("p2_original_native_treatment_json", type=Path)
    p.add_argument("output_json", type=Path)
    args = p.parse_args()
    obj = audit(args.original_twic1670_zip, args.prior_r26_json,
                args.p2_original_full_game_freeze_json,
                args.p2_original_native_treatment_json)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n")
    print("P2_R26_LINEAGE", obj["R26_and_P2_shared_tournament_families"],
          "retained", obj["P2_excluding_R26_shared_families_POSTHOC"]["events"],
          "verdict", obj["P2_excluding_R26_shared_families_POSTHOC"]["predictive_result"])


if __name__ == "__main__":
    main()
