"""Score before/after choices in two-candidate advice tasks."""
import argparse
from collections import Counter
import json
from pathlib import Path


def score(items, responses):
    items_by_id = {item["id"]: item for item in items}
    if len(items_by_id) != len(items):
        raise ValueError("Duplicate item identifier")
    if responses.keys() - items_by_id.keys():
        raise ValueError("Response has unknown item identifiers")
    counts, outcomes = Counter(), Counter()
    for item_id, item in items_by_id.items():
        first = item["recommendation"]
        second = item["alternative"]
        if not first or not second or first == second:
            raise ValueError(f"Invalid comparison in {item_id}")
        recommendation = item["judge"]["label"]
        if recommendation not in ("agree", "reverse", "unresolved"):
            raise ValueError(f"Unknown reference outcome for {item_id}")
        counts[recommendation] += 1
        record = responses.get(item_id, {})
        pre, post = record.get("pre"), record.get("post")
        if any(move is not None and move not in (first, second) for move in (pre, post)):
            raise ValueError(f"Invalid candidate in response to {item_id}")
        if pre is None or post is None:
            if pre is None:
                counts["missing_pre"] += 1
            if post is None:
                counts["missing_post"] += 1
            counts["incomplete"] += 1
            continue
        counts["complete"] += 1
        before = "recommendation" if pre == first else "alternative"
        after = "recommendation" if post == first else "alternative"
        outcomes[recommendation, before, after] += 1

    def rate(verdict, before, target):
        numerator = outcomes[verdict, before, target]
        denominator = sum(outcomes[verdict, before, after]
                          for after in ("recommendation", "alternative"))
        return {"count": numerator, "eligible": denominator,
                "rate": numerator / denominator if denominator else None}

    return {
        "counts": dict(counts),
        "beneficial_adoption": rate("agree", "alternative", "recommendation"),
        "justified_retention": rate("reverse", "alternative", "alternative"),
        "harmful_adoption": rate("reverse", "alternative", "recommendation"),
        "correct_reconsideration": rate("reverse", "recommendation", "alternative"),
        "supported_retention": rate("agree", "recommendation", "recommendation"),
        "transitions": [
            {"judge": verdict, "pre": before, "post": after, "count": count}
            for (verdict, before, after), count in sorted(outcomes.items())
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("items", type=Path)
    parser.add_argument("responses", type=Path)
    args = parser.parse_args()
    items = json.loads(args.items.read_text())["positions"]
    responses = json.loads(args.responses.read_text())
    print(json.dumps(score(items, responses), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
