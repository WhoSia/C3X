#!/usr/bin/env python3
"""I10-P6-R3 frozen native Stage A runner; no treatment without second seal.

Each job is a fresh Stockfish process. The append-only ledger retains failures;
the program never retries or changes a position in response to an engine output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import selectors
import subprocess
import time
from pathlib import Path


REPO_FILES = {
    "contract": "c3x/preseals/i10-p6-r3-contract.json",
    "manifest": "c3x/preseals/i10-p6-r3-candidate-manifest.json",
}
ARMS = {
    "ORIGINAL": ("builds/original/src/stockfish", None),
    "ACTIVE_SHAM": ("builds/sham/src/stockfish", "SHAM"),
    "OBSERVER_SHAM": ("builds/p6_observer/src/stockfish", "SHAM"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(repo: Path, commit: str, name: str) -> bytes:
    return subprocess.run(["git", "show", f"{commit}:{name}"], cwd=repo,
                          check=True, capture_output=True).stdout


def git_identity(repo: Path, commit: str) -> tuple[str, str]:
    raw = subprocess.run(["git", "show", "-s", "--format=%an%n%cn", commit],
                         cwd=repo, check=True, capture_output=True, text=True).stdout
    return tuple(raw.strip().splitlines())  # type: ignore[return-value]


def info_projection(line: str) -> dict | None:
    if not line.startswith("info ") or " pv " not in line:
        return None
    words = line.split()
    if "pv" not in words:
        return None
    stop = words.index("pv")
    head = words[:stop]
    rec: dict[str, object] = {"pv": words[stop + 1:]}
    for key in ("depth", "seldepth", "multipv", "nodes"):
        if key in head:
            i = head.index(key)
            if i + 1 >= len(head):
                raise ValueError(f"MALFORMED_{key}")
            rec[key] = int(head[i + 1])
    for key in ("score", "wdl"):
        if key in head:
            i = head.index(key)
            width = 2 if key == "score" else 3
            if key == "score":
                width = 2  # cp/mate + integer
            if i + width >= len(head):
                raise ValueError(f"MALFORMED_{key}")
            rec[key] = head[i + 1:i + 1 + width]
    rec["lowerbound"] = "lowerbound" in head
    rec["upperbound"] = "upperbound" in head
    if "depth" not in rec or "nodes" not in rec or not rec["pv"]:
        raise ValueError("INCOMPLETE_INFO_PV")
    return rec


def canonical(raw: bytes) -> dict:
    lines = raw.decode("utf-8", "replace").splitlines()
    traces = [r for line in lines if (r := info_projection(line)) is not None]
    best = [line.split() for line in lines if line.startswith("bestmove ")]
    if not traces or len(best) != 1 or len(best[0]) not in (2, 4):
        raise ValueError("NO_CANONICAL_PUBLICATION")
    if len(best[0]) == 4 and best[0][2] != "ponder":
        raise ValueError("INVALID_PONDER")
    return {"trace": traces, "bestmove": best[0][1],
            "ponder": best[0][3] if len(best[0]) == 4 else None}


def execute(binary: Path, arm: str, history: list[str], timeout: int) -> tuple[bytes, bytes, bool, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("C3X025_")}
    if arm in ("SHAM", "SCORE"):
        env.update({"C3X025_P8_TT_FIELDS": "1", "C3X025_P14_ARM": arm})
    position = "position startpos moves " + " ".join(history)
    script = "\n".join(("uci", "setoption name Threads value 1",
                        "setoption name Hash value 16",
                        "setoption name Use NNUE value false", "isready",
                        "ucinewgame", position, "go depth 7")) + "\n"
    proc = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, bufsize=0)
    assert proc.stdin and proc.stdout and proc.stderr
    raw = bytearray()
    partial = b""
    done = False
    reason = "WATCHDOG_TIMEOUT"
    start = time.monotonic()
    select = selectors.DefaultSelector()
    select.register(proc.stdout, selectors.EVENT_READ)
    try:
        proc.stdin.write(script.encode("ascii"))
        proc.stdin.flush()
        deadline = start + timeout
        while time.monotonic() < deadline and not done:
            for _, _ in select.select(min(0.5, max(0, deadline - time.monotonic()))):
                chunk = os.read(proc.stdout.fileno(), 65536)
                if not chunk:
                    reason = "EOF_BEFORE_BESTMOVE"
                    break
                raw.extend(chunk)
                partial += chunk
                while b"\n" in partial:
                    line, partial = partial.split(b"\n", 1)
                    if line.startswith(b"bestmove "):
                        done = True
                        reason = "COMPLETE"
                        break
            if proc.poll() is not None and not done:
                reason = "PROCESS_EXIT_BEFORE_BESTMOVE"
                break
        if done:
            proc.stdin.write(b"quit\n")
            proc.stdin.flush()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                reason = "QUIT_TIMEOUT_AFTER_BESTMOVE"
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
        stderr = proc.stderr.read()
    finally:
        select.close()
        if proc.poll() is None:
            proc.kill()
            proc.wait()
    return bytes(raw), stderr, done and reason == "COMPLETE", reason


def append_jsonl(path: Path, row: dict) -> None:
    with path.open("ab") as stream:
        stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")).encode() + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--preseal-commit", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    repo = args.repo.resolve()
    out = args.out.resolve()
    if out.exists():
        raise SystemExit("APPEND_ONLY_OUTPUT_ALREADY_EXISTS; no automatic resume")
    contract_raw = git_bytes(repo, args.preseal_commit, REPO_FILES["contract"])
    manifest_raw = git_bytes(repo, args.preseal_commit, REPO_FILES["manifest"])
    if git_identity(repo, args.preseal_commit) != ("WhoSia", "WhoSia"):
        raise SystemExit("PRESEAL_GIT_IDENTITY_INVALID")
    contract = json.loads(contract_raw)
    manifest = json.loads(manifest_raw)
    source = workspace / "cohorts/i10_p6_r3/british_championship_2026_parent_CDVYxqmL.pgn"
    audit = workspace / "cohorts/i10_p6_r3/audit/source_audit.json"
    history_index = workspace / "cohorts/i10_p6_r3/history/history_index.json"
    checks = (
        (source, contract["source"]["raw_pgn_sha256"]),
        (audit, contract["source_only_inputs"]["source_audit_sha256"]),
        (history_index, contract["source_only_inputs"]["history_index_sha256"]),
    )
    for path, expected in checks:
        if digest(path.read_bytes()) != expected:
            raise SystemExit(f"SOURCE_INPUT_SHA_MISMATCH {path}")
    if digest(manifest_raw) != contract["source_only_inputs"]["candidate_manifest_sha256"]:
        raise SystemExit("MANIFEST_SHA_MISMATCH")
    roots = manifest["root_positions"]
    if len(roots) != 32 or contract["stage_A_untreated"]["jobs"] != 192:
        raise SystemExit("FROZEN_GEOMETRY_INVALID")
    bins = {}
    for name, (relative, arm) in ARMS.items():
        binary = workspace / relative
        expected = contract["engine"]["binary_sha256"]["OBSERVER_SHAM_AND_SCORE" if name == "OBSERVER_SHAM" else name]
        if digest(binary.read_bytes()) != expected:
            raise SystemExit(f"BINARY_SHA_MISMATCH {name}")
        bins[name] = (binary, arm)
    out.mkdir(parents=True)
    raw_dir = out / "raw"
    raw_dir.mkdir()
    ledger = out / "ledger.jsonl"
    append_jsonl(ledger, {"kind": "PRESEAL", "commit": args.preseal_commit,
                          "contract_sha256": digest(contract_raw), "manifest_sha256": digest(manifest_raw),
                          "status": "VERIFIED"})
    completed = 0
    mismatches = []
    failures = []
    for rank, root in enumerate(roots):
        for repeat in (1, 2):
            pair = {}
            for name in contract["stage_A_untreated"]["arms_in_order"]:
                job = f"r{rank:02d}_q{repeat}_{name.lower()}"
                binary, arm = bins[name]
                raw, err, ok, reason = execute(binary, arm or "ORIGINAL", root["root_history_uci"],
                                                contract["runtime"]["watchdog_seconds"])
                (raw_dir / (job + ".stdout")).write_bytes(raw)
                (raw_dir / (job + ".stderr")).write_bytes(err)
                record = {"kind": "JOB", "job": job, "rank": rank, "repeat": repeat,
                          "arm": name, "source_game_sha256": root["source_game_sha256"],
                          "stdout_sha256": digest(raw), "stderr_sha256": digest(err),
                          "stdout_bytes": len(raw), "completed": ok, "reason": reason}
                if ok:
                    try:
                        pair[name] = canonical(raw)
                        record["canonical_sha256"] = digest(json.dumps(pair[name], sort_keys=True,
                            separators=(",", ":")).encode())
                        completed += 1
                    except ValueError as exc:
                        ok = False
                        record["completed"] = False
                        record["reason"] = str(exc)
                append_jsonl(ledger, record)
                if not ok:
                    failures.append(job)
                    break
            if failures:
                break
            for left, right in (("ORIGINAL", "ACTIVE_SHAM"), ("ACTIVE_SHAM", "OBSERVER_SHAM")):
                if pair[left] != pair[right]:
                    mismatches.append({"rank": rank, "repeat": repeat, "left": left, "right": right})
            append_jsonl(ledger, {"kind": "PAIR", "rank": rank, "repeat": repeat,
                                  "equal": not any(x["rank"] == rank and x["repeat"] == repeat for x in mismatches)})
            if mismatches:
                break
        if failures or mismatches:
            break
    summary = {"stage": "A_UNTREATED", "completed_jobs": completed, "expected_jobs": 192,
               "failure_jobs": failures, "mismatches": mismatches,
               "stage_A_pass": completed == 192 and not failures and not mismatches,
               "stage_B_authorized": False,
               "stage_B_reason": "SECOND_WHOSIA_FORECAST_GIT_SEAL_REQUIRED" if completed == 192 and not failures and not mismatches
                                 else "STAGE_A_NOT_PASSED"}
    (out / "summary.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"completed_jobs": completed, "mismatch_count": len(mismatches),
                      "failure_count": len(failures), "stage_A_pass": summary["stage_A_pass"]}))


if __name__ == "__main__":
    main()
