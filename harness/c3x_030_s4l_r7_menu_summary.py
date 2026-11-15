"""Summarize winner reversals among candidates shared by nested root menus."""
import argparse
import json
from pathlib import Path

from c3x_030_s4l_r6_forced_probe import CANDIDATES
from c3x_030_s4l_r7_candidate_menus import PAIRS


def summarize(result):
    summary = {}
    for case, data in result.items():
        inner = {"pair": set(PAIRS[case]), "four": set(CANDIDATES[case])}
        counts = {}
        for limit in ("depth8", "nodes12k"):
            transitions = {}
            for a, b in (("pair", "four"), ("pair", "all"), ("four", "all")):
                comparable = []
                outside = []
                for state, grid in data["grid"].items():
                    old = grid[f"{limit}-{a}"]["go2"]["move"]
                    new = grid[f"{limit}-{b}"]["go2"]["move"]
                    if new not in inner[a]:
                        outside.append(state)
                    elif new != old:
                        comparable.append(state)
                transitions[f"{a}->{b}"] = {"shared_winner_reversals": comparable,
                                             "larger_winner_outside_smaller": outside}
            counts[limit] = transitions
        summary[case] = counts
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(json.loads(args.result.read_text())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
