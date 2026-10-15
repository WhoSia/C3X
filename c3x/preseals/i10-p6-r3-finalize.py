#!/usr/bin/env python3
"""Independent raw-log verification and deterministic C3X I10-P6-R3 custody."""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":")) + "\n")


def module(path: Path):
    spec = importlib.util.spec_from_file_location("native", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verified_jobs(stage: Path, name: str, parser) -> dict:
    ledger = [json.loads(x) for x in (stage / "ledger.jsonl").read_bytes().splitlines()]
    jobs = [x for x in ledger if x["kind"] == "JOB"]
    expected = 192 if name == "A" else 64
    if len(jobs) != expected or any(not j["completed"] for j in jobs):
        raise ValueError(f"STAGE_{name}_INCOMPLETE")
    parsed = {}
    for row in jobs:
        raw = (stage / "raw" / (row["job"] + ".stdout")).read_bytes()
        stderr = (stage / "raw" / (row["job"] + ".stderr")).read_bytes()
        if sha(raw) != row.get("stdout_sha256", row.get("raw_sha256")) or sha(stderr) != row["stderr_sha256"]:
            raise ValueError(f"STAGE_{name}_RAW_SHA_MISMATCH {row['job']}")
        parsed[row["job"]] = {"canonical": parser(raw), "lines": raw.decode("utf-8", "replace").splitlines()}
    return parsed


def zip_deterministic(path: Path, files: dict[str, Path], extra: dict[str, bytes] | None = None) -> tuple[str, dict]:
    all_bytes = {name: source.read_bytes() for name, source in files.items()}
    all_bytes.update(extra or {})
    index = {name: {"sha256": sha(raw), "bytes": len(raw)} for name, raw in sorted(all_bytes.items())}
    all_bytes["PACKAGE_SHA256_INDEX.json"] = (json.dumps(index, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, raw in sorted(all_bytes.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, raw)
    with zipfile.ZipFile(path) as z:
        for name, record in index.items():
            if sha(z.read(name)) != record["sha256"]:
                raise ValueError("PACKAGE_READBACK_SHA_FAIL")
    return sha(path.read_bytes()), index


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", required=True, type=Path)
    p.add_argument("--repo", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    if a.out.exists():
        raise SystemExit("FINAL_CUSTODY_DIR_ALREADY_EXISTS")
    ws = a.workspace
    repo = a.repo
    cohort = ws / "cohorts/i10_p6_r3"
    A = ws / "results/i10_p6_r3_stage_A_86064b1"
    B = ws / "results/i10_p6_r3_stage_B_a4d67e4"
    contract_path = repo / "c3x/preseals/i10-p6-r3-contract.json"
    contract = json.loads(contract_path.read_bytes())
    source = cohort / "british_championship_2026_parent_CDVYxqmL.pgn"
    if sha(source.read_bytes()) != contract["source"]["raw_pgn_sha256"]:
        raise ValueError("SOURCE_SHA_MISMATCH")
    script = module(repo / "c3x/preseals/i10-p6-r3-native-run.py")
    roots = json.loads((cohort / "audit/candidate_manifest.json").read_bytes())["root_positions"]
    forecasts = json.loads((repo / "c3x/preseals/i10-p6-r3-literal-forecasts.json").read_bytes())["positions"]
    if len(roots) != 32 or len(forecasts) != 32:
        raise ValueError("ROOT_COUNT_INVALID")
    parsedA = verified_jobs(A, "A", script.canonical)
    parsedB = verified_jobs(B, "B", script.canonical)
    parity = []
    score_jobs = []
    for rank in range(32):
        for q in (1, 2):
            stem = f"r{rank:02d}_q{q}_"
            o = parsedA[stem + "original"]["canonical"]
            s = parsedA[stem + "active_sham"]["canonical"]
            n = parsedA[stem + "observer_sham"]["canonical"]
            t = parsedB[stem + "observer_score"]["canonical"]
            if o != s or s != n:
                parity.append(stem)
            lines = parsedB[stem + "observer_score"]["lines"]
            terminal_o = o["trace"][-1]
            terminal_t = t["trace"][-1]
            score_jobs.append({"job": stem + "observer_score", "rank": rank,
                               "source_game_sha256": roots[rank]["source_game_sha256"],
                               "fixed_candidate": forecasts[rank]["original_bestmove_candidate"],
                               "fixed_rival": forecasts[rank]["frozen_rival"],
                               "untreated_bestmove": o["bestmove"], "treated_bestmove": t["bestmove"],
                               "root_choice_changed": o["bestmove"] != t["bestmove"],
                               "fixed_rival_won": t["bestmove"] == forecasts[rank]["frozen_rival"],
                               "canonical_publication_changed": o != t,
                               "untreated_terminal_score": terminal_o.get("score"),
                               "treated_terminal_score": terminal_t.get("score"),
                               "untreated_terminal_nodes": terminal_o.get("nodes"),
                               "treated_terminal_nodes": terminal_t.get("nodes"),
                               "prepolicy_eligible_first_events": sum("event=Q_RETURN_ELIGIBILITY_BEFORE_POLICY" in x for x in lines),
                               "score_mutation_first_events": sum("kind=Q_SCORE_RETURN_BOUND_CONTACT" in x and "mutated=1" in x for x in lines)})
    if parity:
        raise ValueError("STAGE_A_PARITY_CONTRADICTION")
    resultB = json.loads((B / "results.json").read_bytes())
    flip_jobs = [x["job"] for x in score_jobs if x["root_choice_changed"]]
    if sorted(flip_jobs) != sorted(resultB["root_flip_jobs"]):
        raise ValueError("STAGE_B_RESULT_CONTRADICTION")
    by_rank = collections.defaultdict(list)
    for x in score_jobs:
        by_rank[x["rank"]].append(x)
    repeat_mismatch = [rank for rank, items in by_rank.items()
                       if (items[0]["untreated_bestmove"], items[0]["treated_bestmove"],
                           items[0]["untreated_terminal_score"], items[0]["treated_terminal_score"],
                           items[0]["untreated_terminal_nodes"], items[0]["treated_terminal_nodes"])
                       != (items[1]["untreated_bestmove"], items[1]["treated_bestmove"],
                           items[1]["untreated_terminal_score"], items[1]["treated_terminal_score"],
                           items[1]["untreated_terminal_nodes"], items[1]["treated_terminal_nodes"])]
    a.out.mkdir(parents=True)
    summary = {"stage": "C3X I10-P6-R3", "status": "INDEPENDENT_NATIVE_EXECUTION_DESCRIPTIVE_ONLY",
               "source_preseal_commit": "86064b15c348bb2b7ac9124f84e0b8524240abaa",
               "forecast_preseal_commit": "a4d67e4a77ffd5b2797f95b9657ca409ec90a7da",
               "source_sha256": sha(source.read_bytes()),
               "stage_A_completed": 192, "stage_A_pair_count": 64, "stage_A_mismatches": len(parity),
               "stage_B_completed": 64, "stage_B_failures": 0,
               "score_mutation_contact_jobs": sum(x["score_mutation_first_events"] > 0 for x in score_jobs),
               "score_eligibility_jobs": sum(x["prepolicy_eligible_first_events"] > 0 for x in score_jobs),
               "root_choice_changed_jobs": flip_jobs,
               "root_choice_changed_unique_games": sorted({x["source_game_sha256"] for x in score_jobs if x["root_choice_changed"]}),
               "frozen_rival_won_jobs": [x["job"] for x in score_jobs if x["fixed_rival_won"]],
               "repeat_terminal_mismatch_ranks": repeat_mismatch,
               "natural_tt_see_root_mediation": "NOT_IDENTIFIED",
               "source_causal_scope": "One event section, one Stockfish16 qsearch SCORE suppression, depth7, NNUE off",
               "chess_semantic": "UNADJUDICATED",
               "evidence_bridge": "HOLD",
               "pedagogical": "HOLD",
               "c3x_026": "HOLD",
               "p7": "PROTOCOL_ONLY"}
    write_json(a.out / "verified_summary.json", summary)
    write_json(a.out / "verified_job_table.json", score_jobs)
    (a.out / "P7_AUTHORITY_NOTE.md").write_text(
        "# C3X I10-P7 evidence boundary\n\n"
        "SOURCE_CAUSAL: one observed native root-choice response to the pinned SCORE intervention in one of 32 game roots (two cold repeats). "
        "This is the treatment contrast only.\n\n"
        "CHESS_SEMANTIC: no independent tactical/strategic adjudication.\n\n"
        "EVIDENCE_BRIDGE: natural TT writer-reader-SEE-root mediation remains unproved because the first-contact trace lacks a complete same-run identity chain and no distinct SEE intervention was executed here.\n\n"
        "PEDAGOGICAL: no human-utility validation.\n\n"
        "C3X 0.26 remains HOLD. The fixed rival did not become the treated bestmove in the observed flip; no frozen pairwise preference effect is promoted.\n")
    source_files = {"raw_source.pgn": source}
    for path in sorted((cohort / "audit").rglob("*")):
        if path.is_file():
            source_files["audit/" + path.name] = path
    for path in sorted((cohort / "history").rglob("*")):
        if path.is_file():
            source_files["history/" + path.name] = path
    for path in sorted(cohort.glob("historical_artifact_*.zip")):
        source_files["history/" + path.name] = path
    source_sha, source_index = zip_deterministic(a.out / "C3X_I10_P6_R3_SOURCE_EVIDENCE.zip", source_files)
    result_files = {}
    for prefix, root in (("stage_A", A), ("stage_B", B)):
        for path in sorted(root.rglob("*")):
            if path.is_file():
                result_files[prefix + "/" + path.relative_to(root).as_posix()] = path
    for path in sorted(a.out.glob("*.json")) + sorted(a.out.glob("*.md")):
        result_files["verification/" + path.name] = path
    for path in sorted((repo / "c3x/preseals").glob("i10-p6-r3-*")):
        if path.is_file():
            result_files["git_preseals/" + path.name] = path
    result_sha, result_index = zip_deterministic(a.out / "C3X_I10_P6_R3_NATIVE_RESULTS.zip", result_files)
    runtime_files = {
        "ORIGINAL_stockfish": ws / "builds/original/src/stockfish",
        "ACTIVE_SHAM_stockfish": ws / "builds/sham/src/stockfish",
        "OBSERVER_SHAM_SCORE_stockfish": ws / "builds/p6_observer/src/stockfish",
    }
    for key, path in runtime_files.items():
        expect = contract["engine"]["binary_sha256"]["OBSERVER_SHAM_AND_SCORE" if key.startswith("OBSERVER") else key.replace("_stockfish", "")]
        if sha(path.read_bytes()) != expect:
            raise ValueError("RUNTIME_BINARY_SHA_MISMATCH")
    runtime_sha, runtime_index = zip_deterministic(a.out / "C3X_I10_P6_R3_RUNTIME_BINARIES.zip", runtime_files)
    write_json(a.out / "custody_receipt.json", {"source_evidence_zip_sha256": source_sha,
                                              "native_results_zip_sha256": result_sha,
                                              "runtime_binaries_zip_sha256": runtime_sha,
                                              "source_file_count": len(source_index),
                                              "result_file_count": len(result_index),
                                              "runtime_file_count": len(runtime_index),
                                              "verified_summary_sha256": sha((a.out / "verified_summary.json").read_bytes()),
                                              "verified_job_table_sha256": sha((a.out / "verified_job_table.json").read_bytes())})
    print(json.dumps({"stage_A": 192, "stage_B": 64, "root_flip_jobs": len(flip_jobs),
                      "root_flip_games": len(summary["root_choice_changed_unique_games"]),
                      "source_zip_sha256": source_sha, "results_zip_sha256": result_sha,
                      "runtime_zip_sha256": runtime_sha}))


if __name__ == "__main__":
    main()
