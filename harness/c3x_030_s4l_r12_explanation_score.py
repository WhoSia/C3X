"""Compare trace-added forecasts with PV and tree forecasts on identical reply questions."""

import argparse
import json
from pathlib import Path

from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r12_reply_questions import fingerprint

ARMS = ("pv", "tree", "trace")


def sign(value):
    return (value > 0) - (value < 0)


def score(questions, predictions, judge):
    if predictions["question_sha256"] != fingerprint(questions):
        raise ValueError("Predictions do not match frozen questions")
    if type(judge["depth"]) is not int or judge["depth"] < 1:
        raise ValueError("Expected judge depth")
    if predictions["forecasts"].keys() != questions.keys():
        raise ValueError("Forecast keys differ from question keys")
    records = {row["round"]: row["roots"] for row in judge["rows"]}
    if len(records) != len(judge["rows"]):
        raise ValueError("Duplicate judge round")
    results = {}
    for key, question in questions.items():
        if key != fingerprint(question):
            raise ValueError("Malformed question key")
        row = predictions["forecasts"][key]
        if row.keys() != set(ARMS):
            raise ValueError("Expected all three arms, with explicit null on abstention")
        points = [records[question["round"]][root][question["reply"]]["point"]
                  for root in question["roots"]]
        complete = all(
            point is not None and not point["bound"]
            and (point["depth"] == judge["depth"]
                 or (point["depth"] == 0 and point["nodes"] == 0 and not point["pv"]))
            for point in points
        )
        actual = sign(points[0]["ordered"] - points[1]["ordered"]) if complete else None
        for value in row.values():
            if value is not None and (type(value) is not int or value not in (-1, 0, 1)):
                raise ValueError("Forecast must be an ordinal sign or null")
        results[key] = {"round": question["round"], "judge_sign": actual,
                        "forecasts": row,
                        "paired": complete and all(value is not None for value in row.values())}
    paired = [row for row in results.values() if row["paired"]]
    eligible = [row for row in results.values() if row["judge_sign"] is not None]
    coverage = {arm: sum(row["forecasts"][arm] is not None for row in eligible)
                for arm in ARMS}
    observed_correct = {
        arm: sum(row["forecasts"][arm] == row["judge_sign"] for row in eligible)
        if coverage[arm] else None for arm in ARMS
    }
    return {"depth": judge["depth"], "questions": len(results), "judge_coverage": len(eligible),
            "observed_correct": observed_correct,
            "arm_coverage": coverage, "joint_coverage": len(paired),
            "paired_correct": {arm: sum(row["forecasts"][arm] == row["judge_sign"] for row in paired)
                               for arm in ARMS} if paired else None,
            "rows": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", type=Path)
    parser.add_argument("questions", type=Path)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("judge", type=Path)
    parser.add_argument("--forecast-sha256", required=True,
                        help="SHA-256 recorded before the judge was opened")
    args = parser.parse_args()
    if digest(args.predictions) != args.forecast_sha256:
        raise ValueError("Forecast file differs from its pre-judge seal")
    questions, predictions, judge = (json.loads(path.read_text()) for path in
                                      (args.questions, args.predictions, args.judge))
    if judge["cohort_sha256"] != digest(args.cohort):
        raise ValueError("Judge cohort hash mismatch")
    cases = {case["round"]: case for case in json.loads(args.cohort.read_text())["selection"]}
    for question in questions.values():
        case = cases[question["round"]]
        if question["history"] != case["history"] or question["roots"] != case["roots"]:
            raise ValueError("Question does not match the judge's complete game history and candidates")
    print(json.dumps(score(questions, predictions, judge), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
