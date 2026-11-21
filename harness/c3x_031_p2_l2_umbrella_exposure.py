"""0.31/P2-L2: predeclared macrofamily and conservative alias sensitivity.

Reuses the actual original R26↔P2 ZIP/JSON byte verifiers from P2-L1.
Reuses the originally frozen P2 independent court's macro-family dictionary
without modifying it. An extra more-conservative alias scenario is EXPLORATORY.
No native search, selection, model fitting, chess strategy or human study.
"""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
import json
from pathlib import Path
import random

from c3x_031_p2_l1_historical_family_audit import (
    audit as l1_audit, brier, metrics, norm, read_json, read_publisher, require,
    P2_TREATMENT_SHA,
)

ORIGINAL_EXPECTED_MACRO = {
    "iii ch-sudamericano women": "iii ch-sudamericano",
    "iii ch-sudamericano blitz": "iii ch-sudamericano",
    "fide world open u20 rapid": "fide world open u20",
    "fide world open u20 blitz": "fide world open u20",
    "world girls u20 rapid": "world girls u20",
    "world girls u20 blitz": "world girls u20",
    "future stars chn w rapid": "future stars chn w",
    "future stars chn w blitz": "future stars chn w",
    "tal memorial rapid 2026": "tal memorial 2026",
    "tal memorial blitz 2026": "tal memorial 2026",
}
# Additional possibilities, NOT original preregistered aliases: do not promote
# their exclusion to primary validation, and do not assert festival identity.
LATER_SCENARIO_ALIASES = {
    "iii ch-sudamericano 2026": "iii ch-sudamericano",
    "7th asean plus ind 2026": "7th asean plus ind",
    "7th asean plus ind women": "7th asean plus ind",
}
BOOT = 2000
MACRO_SEED = 310222
SCENARIO_SEED = 310223


def frozen_original_macro(path: Path) -> dict:
    """Read the ORIGINAL macro map from a prior source file as an AST literal."""
    tree = ast.parse(path.read_text(encoding="utf8"), filename=str(path))
    candidates = [
        n.value for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "PREDECLARED_MACRO"
                for t in n.targets)
    ]
    require(len(candidates) == 1, "original macro-family map absent or duplicated")
    mapping = ast.literal_eval(candidates[0])
    require(mapping == ORIGINAL_EXPECTED_MACRO,
            "original P2 secondary macro group definition has drifted")
    return mapping


def source_rows(treated: dict) -> list[dict]:
    rows = []
    for case in treated["cases"]:
        for group, intervention in case["targets"].items():
            require(intervention["status"] == "ACTUAL_SOURCE_TREATMENT_OBSERVED",
                    "physical source target missing")
            prob = intervention["frozen_predictions"]
            rows.append({
                "id": case["id"] + "-" + group,
                "family": case["family"],
                "y": int(intervention["treatment_bestmove_changed"]),
                **{k: prob[k] for k in ("m0", "m1", "m2")},
            })
    require(len(rows) == 128 and sum(r["y"] for r in rows) == 7,
            "original P2 changed or selected after outcome")
    return sorted(rows, key=lambda r: r["id"])


def intervals(rows: list[dict], mapping: dict, seed: int) -> dict:
    """Resample whole declared macro groups, never individual game/event rows."""
    families = sorted({mapping.get(row["family"], row["family"]) for row in rows})
    buckets = {f: [row for row in rows
                   if mapping.get(row["family"], row["family"]) == f]
               for f in families}
    rng = random.Random(seed)
    draws = {"m0": [], "m1": []}
    for _ in range(BOOT):
        sampled = [r for g in (rng.choice(families) for _ in families)
                   for r in buckets[g]]
        for baseline in draws:
            draws[baseline].append(brier(sampled, baseline) - brier(sampled, "m2"))
    return {
        baseline + "_minus_m2": {
            "gain": brier(rows, baseline) - brier(rows, "m2"),
            "macro_family_bootstrap95": [
                sorted(draws[baseline])[50], sorted(draws[baseline])[1949]
            ]
        } for baseline in draws
    }


def tier(rows: list[dict], prior_normalized: set[str],
         mapping: dict, seed: int, classification: str) -> dict:
    old_clusters = {mapping.get(key, key) for key in prior_normalized}
    excluded = [r for r in rows if mapping.get(r["family"], r["family"]) in old_clusters]
    kept = [r for r in rows if mapping.get(r["family"], r["family"]) not in old_clusters]
    require(len(kept) + len(excluded) == 128, "incomplete source-family partition")
    all_groups = {mapping.get(r["family"], r["family"]) for r in kept}
    return {
        "evidence_class": classification,
        "source_previous_family_names": sorted(old_clusters),
        "overlap_p2_exact_families": sorted({r["family"] for r in excluded}),
        "overlap_p2_macro_groups": sorted({
            mapping.get(r["family"], r["family"]) for r in excluded
        }),
        "removed_game_count": len({r["id"].rsplit("-",1)[0] for r in excluded}),
        "removed_event_count": len(excluded),
        "removed_true_flip_events": sorted(r["id"] for r in excluded if r["y"]),
        "retained_games": len({r["id"].rsplit("-",1)[0] for r in kept}),
        "retained_events": len(kept),
        "retained_exact_event_families": len({r["family"] for r in kept}),
        "retained_macro_event_families": len(all_groups),
        "retained_true_root_flips": sum(r["y"] for r in kept),
        "scores": metrics(kept),
        "differences": intervals(kept, mapping, seed),
        "source_gain_gate": "NO_VALIDATED_M2_BRIER_ADVANTAGE"
              if not (all(
                  v["gain"] >= .01 and v["macro_family_bootstrap95"][0] > 0
                  for v in intervals(kept, mapping, seed).values())
                  and metrics(kept)["m2"]["average_precision"] >= max(
                      metrics(kept)["m0"]["average_precision"],
                      metrics(kept)["m1"]["average_precision"]))
              else "SURPRISING_RETROSPECTIVE_THRESHOLD_PASSED_NEEDS_PROSPECTIVE_RETEST",
    }


def audit(source: Path, prior: Path, games: Path, treatment: Path,
          independent_court_py: Path) -> dict:
    verified_l1 = l1_audit(source, prior, games, treatment)
    mapping = frozen_original_macro(independent_court_py)
    publisher_headers = read_publisher(source)
    old = read_json(prior)
    selected = [row for row in old["game_history_hashes"]
                if row["id"].startswith("twic1670-")]
    require(len(selected) == 16, "R26 original exposure group changed")
    old_names = {norm(publisher_headers[r["ordinal"] - 1]) for r in selected}
    treated = read_json(treatment, P2_TREATMENT_SHA)
    rows = source_rows(treated)
    exact = tier(rows, old_names, {}, 310221,
                 "POSTOUTCOME_EXACT_FAMILY_SENSITIVITY")
    require(exact["removed_event_count"] == 16 and
            exact["retained_events"] == verified_l1[
                "P2_excluding_R26_shared_families_POSTHOC"]["events"],
            "macro analysis does not reproduce exact L1 basis")
    macro = tier(rows, old_names, mapping, MACRO_SEED,
                 "POSTOUTCOME_PRIOR_REGISTERED_MACRO_FAMILY_SENSITIVITY")
    require(macro["removed_event_count"] == 32 and macro["retained_events"] == 96
            and macro["retained_true_root_flips"] == 6
            and macro["removed_true_flip_events"] == ["P2-028-0"],
            "original preregistered macro-family exposure mismatch")
    # Additional umbrella claims are *explicitly hypothetical* name aliases.
    alias = {**mapping, **LATER_SCENARIO_ALIASES}
    scenario = tier(rows, old_names, alias, SCENARIO_SEED,
                    "LATER_HYPOTHETICAL_UMBRELLA_NAME_ALIAS_SCENARIO")
    require(scenario["removed_event_count"] == 52
            and scenario["retained_events"] == 76
            and scenario["retained_true_root_flips"] == 5
            and scenario["removed_true_flip_events"] ==
                ["P2-028-0", "P2-055-0"],
            "later possible alias scenario denominator mismatch")
    return {
        "id": "C3X_031_P2_L2_R26_UMBRELLA_EXPOSURE_SENSITIVITY",
        "source_R26_original_selected_histories": 16,
        "P2_original_native_source_events_untouched": 128,
        "P2_original_root_flips_untouched": 7,
        "new_engine_searches": 0,
        "model_retrained": False,
        "no_chess_strategy_claim": True,
        "no_causal_TT_or_history_mediator_claim": True,
        "macro_mapping_source":
            "harness/c3x_031_p2_independent_court.py:PREDECLARED_MACRO",
        "original_macro_mapping_exactly_matches_source": True,
        "primary_P2_scientific_gate": "NEGATIVE_PROSPECTIVE_TRANSPORT",
        "literal_exact": exact,
        "predeclared_macro_names": macro,
        "later_conservative_name_alias_scenario_NOT_VERIFIED": scenario,
        "priority_P2_D1_original_pair_P2_028": {
            "selected_original_history_is_R26_duplicate": False,
            "same_literal_R26_event_header": False,
            "same_PREDECLARED_macro_event_family_as_R26": True,
            "scientific_claim": "valid_exposed_development_mechanism_candidate_NOT_entirely_prior_family_blind",
        },
        "scientific_note":
          "P2 failed preregistered +0.01 Brier gain under ALL lineage exclusion "
          "definitions, but the numerical sign of M2-M1 Brier difference is "
          "not stable under macro-family exclusion. All variants are postoutcome.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("publisher_zip", type=Path)
    p.add_argument("r26_original_receipt", type=Path)
    p.add_argument("p2_original_64game_json", type=Path)
    p.add_argument("p2_original_128treatment_json", type=Path)
    p.add_argument("original_prior_independent_court_py", type=Path)
    p.add_argument("output_json", type=Path)
    a = p.parse_args()
    result = audit(a.publisher_zip, a.r26_original_receipt,
                   a.p2_original_64game_json, a.p2_original_128treatment_json,
                   a.original_prior_independent_court_py)
    a.output_json.parent.mkdir(parents=True, exist_ok=True)
    a.output_json.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    for key in ("literal_exact", "predeclared_macro_names",
                "later_conservative_name_alias_scenario_NOT_VERIFIED"):
        row = result[key]
        print("P2_L2", key, row["retained_events"], row["retained_true_root_flips"],
              row["differences"]["m1_minus_m2"])
    print("P2_L2_SCIENCE", result["primary_P2_scientific_gate"],
          "native_searches", result["new_engine_searches"])


if __name__ == "__main__":
    main()
