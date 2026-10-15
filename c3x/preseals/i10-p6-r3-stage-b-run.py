#!/usr/bin/env python3
"""Frozen I10-P6-R3 SCORE arm, released only by two WhoSia Git seals."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def module(path: Path):
    spec = importlib.util.spec_from_file_location("p6_r3_native", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{commit}:{path}"], cwd=repo,
                          check=True, capture_output=True).stdout


def git_names(repo: Path, commit: str) -> list[str]:
    return subprocess.run(["git", "show", "-s", "--format=%an%n%cn", commit],
                          cwd=repo, check=True, capture_output=True, text=True).stdout.strip().splitlines()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--source-preseal", required=True)
    p.add_argument("--forecast-preseal", required=True)
    p.add_argument("--stage-a", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    m = module(a.repo / "c3x/preseals/i10-p6-r3-native-run.py")
    if a.out.exists():
        raise SystemExit("APPEND_ONLY_OUTPUT_ALREADY_EXISTS")
    if git_names(a.repo, a.source_preseal) != ["WhoSia", "WhoSia"] or git_names(a.repo, a.forecast_preseal) != ["WhoSia", "WhoSia"]:
        raise SystemExit("WHOSIA_PRESEAL_IDENTITY_FAIL")
    ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", a.source_preseal,
                               a.forecast_preseal], cwd=a.repo)
    if ancestry.returncode:
        raise SystemExit("SOURCE_PRESEAL_NOT_ANCESTOR")
    source_contract = git_bytes(a.repo, a.source_preseal, "c3x/preseals/i10-p6-r3-contract.json")
    source_manifest = git_bytes(a.repo, a.source_preseal, "c3x/preseals/i10-p6-r3-candidate-manifest.json")
    latest_contract = git_bytes(a.repo, a.forecast_preseal, "c3x/preseals/i10-p6-r3-contract.json")
    latest_manifest = git_bytes(a.repo, a.forecast_preseal, "c3x/preseals/i10-p6-r3-candidate-manifest.json")
    if source_contract != latest_contract or source_manifest != latest_manifest:
        raise SystemExit("SOURCE_OR_SAMPLE_MUTATED_BETWEEN_SEALS")
    forecast_raw = git_bytes(a.repo, a.forecast_preseal, "c3x/preseals/i10-p6-r3-literal-forecasts.json")
    receipt_raw = git_bytes(a.repo, a.forecast_preseal, "c3x/preseals/i10-p6-r3-stage-a-receipt.json")
    forecast = json.loads(forecast_raw)
    receipt = json.loads(receipt_raw)
    if receipt["stage_A_pass"] is not True or receipt["jobs"] != 192 or receipt["pairs"] != 64:
        raise SystemExit("STAGE_A_RECEIPT_NOT_PASS")
    if receipt["ledger_sha256"] != sha((a.stage_a / "ledger.jsonl").read_bytes()):
        raise SystemExit("STAGE_A_LEDGER_SHA_MISMATCH")
    if receipt["summary_sha256"] != sha((a.stage_a / "summary.json").read_bytes()):
        raise SystemExit("STAGE_A_SUMMARY_SHA_MISMATCH")
    contract = json.loads(source_contract)
    roots = json.loads(source_manifest)["root_positions"]
    if len(roots) != 32 or len(forecast["positions"]) != 32 or forecast["treatment_jobs"] != 64:
        raise SystemExit("STAGE_B_GEOMETRY_FAIL")
    if any(forecast["positions"][i]["game_sha256"] != roots[i]["source_game_sha256"] for i in range(32)):
        raise SystemExit("FORECAST_JOIN_FAIL")
    binary = a.workspace / "builds/p6_observer/src/stockfish"
    if sha(binary.read_bytes()) != contract["engine"]["binary_sha256"]["OBSERVER_SHAM_AND_SCORE"]:
        raise SystemExit("OBSERVER_BINARY_SHA_MISMATCH")
    a.out.mkdir(parents=True)
    (a.out / "raw").mkdir()
    ledger = a.out / "ledger.jsonl"
    m.append_jsonl(ledger, {"kind": "PRESEAL", "source_preseal": a.source_preseal,
                            "forecast_preseal": a.forecast_preseal,
                            "forecast_sha256": sha(forecast_raw), "stage_a_receipt_sha256": sha(receipt_raw)})
    completed = 0
    failures = []
    rows = []
    for rank, root in enumerate(roots):
        for repeat in (1, 2):
            job = f"r{rank:02d}_q{repeat}_observer_score"
            raw, err, ok, reason = m.execute(binary, "SCORE", root["root_history_uci"],
                                              contract["runtime"]["watchdog_seconds"])
            (a.out / "raw" / (job + ".stdout")).write_bytes(raw)
            (a.out / "raw" / (job + ".stderr")).write_bytes(err)
            row = {"kind": "JOB", "job": job, "rank": rank, "repeat": repeat,
                   "source_game_sha256": root["source_game_sha256"],
                   "raw_sha256": sha(raw), "raw_bytes": len(raw), "stderr_sha256": sha(err),
                   "completed": ok, "reason": reason}
            if ok:
                try:
                    treated = m.canonical(raw)
                    sham_raw = (a.stage_a / "raw" / f"r{rank:02d}_q{repeat}_observer_sham.stdout").read_bytes()
                    untreated = m.canonical(sham_raw)
                    lines = raw.decode("utf-8", "replace").splitlines()
                    eligibility = sum("event=Q_RETURN_ELIGIBILITY_BEFORE_POLICY" in s for s in lines)
                    contact = sum("kind=Q_SCORE_RETURN_BOUND_CONTACT" in s for s in lines)
                    mutated = sum("kind=Q_SCORE_RETURN_BOUND_CONTACT" in s and "mutated=1" in s for s in lines)
                    result = {"job": job, "rank": rank, "repeat": repeat,
                              "source_game_sha256": root["source_game_sha256"],
                              "fixed_candidate": forecast["positions"][rank]["original_bestmove_candidate"],
                              "fixed_rival": forecast["positions"][rank]["frozen_rival"],
                              "untreated_bestmove": untreated["bestmove"],
                              "treated_bestmove": treated["bestmove"],
                              "bestmove_changed": treated["bestmove"] != untreated["bestmove"],
                              "terminal_publication_changed": treated != untreated,
                              "untreated_terminal_info": untreated["trace"][-1],
                              "treated_terminal_info": treated["trace"][-1],
                              "eligible_first_event_count": eligibility,
                              "score_contact_event_count": contact,
                              "mutated_first_contact_event_count": mutated,
                              "trace_linkage_limit": "NO_COMPLETE_SAME_RUN_TT_TO_SEE_TO_ROOT_IDENTITY"}
                    rows.append(result)
                    completed += 1
                    row["bestmove_changed"] = result["bestmove_changed"]
                    row["mutated_first_contact_event_count"] = mutated
                except ValueError as exc:
                    ok = False
                    row["completed"] = False
                    row["reason"] = str(exc)
            m.append_jsonl(ledger, row)
            if not ok:
                failures.append({"job": job, "reason": row["reason"]})
                break
        if failures:
            break
    result = {"stage": "B_SCORE", "completed_jobs": completed, "expected_jobs": 64,
              "failures": failures, "source_preseal": a.source_preseal,
              "forecast_preseal": a.forecast_preseal,
              "root_flip_jobs": [r["job"] for r in rows if r["bestmove_changed"]],
              "score_contact_jobs": [r["job"] for r in rows if r["mutated_first_contact_event_count"] > 0],
              "natural_tt_see_mediation": "NOT_IDENTIFIED", "p7_semantic_authority": "HOLD",
              "c3x_026": "HOLD", "jobs": rows}
    (a.out / "results.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"completed": completed, "failures": len(failures),
                      "root_flip_jobs": len(result["root_flip_jobs"]),
                      "contact_jobs": len(result["score_contact_jobs"])}))


if __name__ == "__main__":
    main()
