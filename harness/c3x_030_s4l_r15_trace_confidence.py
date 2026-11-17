"""Freeze and score a within-iteration root-switch uncertainty signal."""

import argparse
import json
from pathlib import Path

from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r11_allocation import BERSERK, NET, SF
from c3x_030_s4l_r14_trace_projection import complete_root_events
from c3x_030_s4l_r14_trace_score import judge_sign


SCALE = 32
LABELS = (-1, 0, 1)
ARMS = ("constant", "public_warning", "trace_warning")


def public_warning(point):
    leaders = {}
    for report in point["public_reports"]:
        if report["cp"] is not None and not report["bound"]:
            leaders[report["depth"]] = report["pv"][0]
    recent = sorted(leaders)[-2:]
    return bool(point["last_is_bound"]) or len({leaders[depth] for depth in recent}) == 2


def within_iteration_switch(lines):
    events, _ = complete_root_events(lines)
    if not events:
        return None
    newest = max(event["iteration"] for event in events)
    updates = {}
    for event in events:
        if event["iteration"] == newest and event["will_update_root_pv"] == 1:
            updates.setdefault(event["root_id"], set()).add(event["root_move_raw"])
    return any(len(moves) > 1 for moves in updates.values())


def probabilities(label, warning):
    if label is None or warning is None:
        return None
    mass = 20 if warning else 24
    return [mass if value == label else (SCALE - mass) // 2 for value in LABELS]


def project(forecast):
    result = {}
    for key, row in forecast["rows"].items():
        label = row["signs"]["public_tree"]
        flagged_public = any(public_warning(point) for point in row["points"])
        switches = [within_iteration_switch(p["stderr"]) for p in row["points"]]
        flagged_trace = None if None in switches else flagged_public or any(switches)
        result[key] = {
            "public_warning": flagged_public, "switches": switches,
            "probabilities": {arm: probabilities(label, warning) for arm, warning in
                              zip(ARMS, (False, flagged_public, flagged_trace))},
        }
    return {"questions_sha256": forecast["questions_sha256"], "scale": SCALE, "rows": result}


def evaluate(projected, judge):
    if (projected["questions_sha256"] != judge["questions_sha256"]
            or projected["rows"].keys() != judge["rows"].keys() or projected["scale"] != SCALE):
        raise ValueError("Projected and reference scopes differ")
    scores = {}
    for key, row in projected["rows"].items():
        outcome = judge_sign(judge["rows"][key], judge["depth"])
        if outcome is None or any(p is None for p in row["probabilities"].values()):
            continue
        scores[key] = {
            arm: sum((m - SCALE * int(outcome == value)) ** 2 for m, value in zip(p, LABELS))
            for arm, p in row["probabilities"].items()
        }
    return {"depth": judge["depth"], "shared_questions": len(scores), "scale_squared": SCALE ** 2,
            "squared_error_sums": {arm: sum(v[arm] for v in scores.values()) for arm in ARMS},
            "rows": scores}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("forecast", type=Path)
    parser.add_argument("forecast_sha256")
    parser.add_argument("--judge", type=Path)
    args = parser.parse_args()
    if digest(args.forecast) != args.forecast_sha256:
        raise ValueError("Forecast digest differs from its freeze")
    source = json.loads(args.forecast.read_text())
    if args.judge is None:
        if source["engine_sha256"] != SF:
            raise ValueError("Expected pinned Stockfish trace")
        result = {**project(source), "r14_forecast_sha256": args.forecast_sha256}
    else:
        ref = json.loads(args.judge.read_text())
        if ref["engine_sha256"] != BERSERK or ref["net_sha256"] != NET:
            raise ValueError("Expected pinned independent reference")
        result = evaluate(source, ref)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
