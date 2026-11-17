"""Freeze shared legal reply questions for matched explanation arms."""

import argparse
import hashlib
import json
from pathlib import Path

from c3x_030_s4l_r10_reply_transport import board_at


def fingerprint(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def freeze(cohort, requests):
    """Requests nominate a reply before independent judgment, never from its scores."""
    cases = {case["round"]: case for case in cohort["selection"]}
    if len(cases) != len(cohort["selection"]):
        raise ValueError("Duplicate cohort round")
    output = {}
    for request in requests:
        case = cases[request["round"]]
        roots = case["roots"]
        if len(roots) != 2 or len(set(roots)) != 2:
            raise ValueError("Expected two distinct competitors")
        board = board_at(case["history"])
        reply = request["reply"]
        for root in roots:
            after = board.copy()
            after.push_uci(root)
            after.push_uci(reply)
        question = {"round": case["round"], "history": case["history"],
                    "roots": roots, "reply": reply}
        key = fingerprint(question)
        if key in output:
            raise ValueError("Duplicate question")
        output[key] = question
    if not output:
        raise ValueError("No questions to freeze")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", type=Path)
    parser.add_argument("requests", type=Path)
    args = parser.parse_args()
    cohort, requests = (json.loads(path.read_text()) for path in (args.cohort, args.requests))
    print(json.dumps(freeze(cohort, requests), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
