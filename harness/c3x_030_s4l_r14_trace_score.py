"""Score sealed projections against the independent fixed-reply reference."""

import argparse
import json
from pathlib import Path

from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r11_allocation import BERSERK, NET, SF
from c3x_030_s4l_r12_explanation_score import sign
from c3x_030_s4l_r14_trace_projection import ARMS


def judge_sign(runs, depth):
    if len(runs) != 2:
        raise ValueError("A question needs two forced leaves")
    points = [run["point"] for run in runs]
    if not all(p and p["depth"] == depth and not p["bound"] and p["cp"] is not None
               for p in points):
        return None
    return sign(points[0]["cp"] - points[1]["cp"])


def score(forecast, judge):
    if (forecast["rows"].keys() != judge["rows"].keys()
            or forecast["questions_sha256"] != judge["questions_sha256"]):
        raise ValueError("Forecast and referee questions differ")
    counts = {arm: {"judged": 0, "correct": 0} for arm in ARMS}
    comparisons = {"changed": 0, "gained": 0, "lost": 0}
    report = {}
    for key, row in forecast["rows"].items():
        target = judge_sign(judge["rows"][key], judge["depth"])
        values = row["signs"]
        if values.keys() != set(ARMS) or any(v is not None and v not in (-1, 0, 1)
                                            for v in values.values()):
            raise ValueError("Invalid projection labels")
        if target is not None:
            for arm, prediction in values.items():
                counts[arm]["judged"] += int(prediction is not None)
                counts[arm]["correct"] += int(prediction == target)
            base, trace = values["public_tree"], values["trace"]
            if base is not None and trace is not None and base != trace:
                comparisons["changed"] += 1
                comparisons["gained"] += int(trace == target)
                comparisons["lost"] += int(base == target)
        report[key] = {"target": target, "signs": values}
    return {"depth": judge["depth"], "counts": counts, "paired_trace": comparisons,
            "rows": report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("forecast", type=Path)
    parser.add_argument("judge", type=Path)
    parser.add_argument("forecast_sha256")
    args = parser.parse_args()
    if digest(args.forecast) != args.forecast_sha256:
        raise ValueError("Forecast digest differs from its freeze")
    forecasts, judge = (json.loads(path.read_text()) for path in (args.forecast, args.judge))
    if forecasts["engine_sha256"] != SF or judge["engine_sha256"] != BERSERK or judge["net_sha256"] != NET:
        raise ValueError("Expected the pinned different source and reference engines")
    print(json.dumps(score(forecasts, judge), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
