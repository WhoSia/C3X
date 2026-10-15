#!/usr/bin/env python3
"""Compile untreated Stage A receipt and literal pre-treatment forecasts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import chess


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":")) + "\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--stage-a", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    summary = json.loads((a.stage_a / "summary.json").read_bytes())
    if not summary["stage_A_pass"] or summary["completed_jobs"] != 192:
        raise SystemExit("STAGE_A_NOT_PASS")
    ledger_bytes = (a.stage_a / "ledger.jsonl").read_bytes()
    ledger = [json.loads(x) for x in ledger_bytes.splitlines()]
    jobs = [x for x in ledger if x["kind"] == "JOB"]
    if len(jobs) != 192 or any(not j["completed"] for j in jobs):
        raise SystemExit("LEDGER_INCOMPLETE")
    for j in jobs:
        path = a.stage_a / "raw" / (j["job"] + ".stdout")
        if sha(path.read_bytes()) != j["stdout_sha256"]:
            raise SystemExit("RAW_SHA_MISMATCH")
    roots = json.loads(a.manifest.read_bytes())["root_positions"]
    forecasts = []
    for rank, root in enumerate(roots):
        from_run = (a.stage_a / "raw" / f"r{rank:02d}_q1_original.stdout").read_text()
        best = [s.split()[1] for s in from_run.splitlines() if s.startswith("bestmove ")]
        if len(best) != 1:
            raise SystemExit("BESTMOVE_MISSING_OR_DUPLICATE")
        board = chess.Board()
        for move in root["root_history_uci"]:
            board.push_uci(move)
        legal = sorted(m.uci() for m in board.legal_moves)
        if best[0] not in legal:
            raise SystemExit("BESTMOVE_ILLEGAL")
        played = root["played_next_uci"]
        rival = played if played in legal and played != best[0] else next(m for m in legal if m != best[0])
        if rival == best[0]:
            raise SystemExit("NO_RIVAL")
        obs = (a.stage_a / "raw" / f"r{rank:02d}_q1_observer_sham.stdout").read_text()
        eligible = sum("event=Q_RETURN_ELIGIBILITY_BEFORE_POLICY" in s for s in obs.splitlines())
        forecasts.append({"rank": rank, "game_sha256": root["source_game_sha256"],
                          "root_history_sha256": root["root_history_sha256"],
                          "original_bestmove_candidate": best[0], "frozen_rival": rival,
                          "rival_rule": "source played next move if legal and distinct; else lexicographically first other legal UCI move",
                          "untreated_observer_eligibility_events_repeat1": eligible,
                          "forecast": "Record whether SCORE changes root bestmove and whether a fixed contender contrast is identifiable; no positive effect assumed."})
    a.out.mkdir(parents=True, exist_ok=False)
    receipt = {"stage": "A_UNTREATED", "preseal_commit": "86064b15c348bb2b7ac9124f84e0b8524240abaa",
               "manifest_sha256": sha(a.manifest.read_bytes()), "ledger_sha256": sha(ledger_bytes),
               "summary_sha256": sha((a.stage_a / "summary.json").read_bytes()),
               "jobs": 192, "pairs": 64, "original_active_sham_mismatches": 0,
               "active_sham_observer_sham_mismatches": 0, "failures": 0,
               "stage_A_pass": True, "stage_B_preseal": "PENDING"}
    dump(a.out / "stage_a_receipt.json", receipt)
    dump(a.out / "literal_forecasts.json", {"schema": "c3x-i10-p6-r3-literal-forecast-v1",
                                            "stage_B_untouched": True, "positions": forecasts,
                                            "treatment_arm": "OBSERVER_SCORE",
                                            "treatment_jobs": 64,
                                            "no_sample_replacement": True,
                                            "no_budget_extension": True,
                                            "natural_tt_see_mediation_authority": "HOLD"})
    print("STAGE_A_RECEIPT_SHA", sha((a.out / "stage_a_receipt.json").read_bytes()))
    print("FORECAST_SHA", sha((a.out / "literal_forecasts.json").read_bytes()))
    print("ELIGIBLE_POSITIONS", sum(x["untreated_observer_eligibility_events_repeat1"] > 0 for x in forecasts))


if __name__ == "__main__":
    main()
