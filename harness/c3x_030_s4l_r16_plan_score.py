"""Audit frozen witnesses against the exact three-ply named-plan oracle."""

import argparse
from collections import Counter
import json
from pathlib import Path

import chess

from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r11_allocation import SF
from c3x_030_s4l_r16_plan_oracle import solve
from c3x_030_s4l_r16_plan_source import SLOTS, post_reply, root_boards


POLICIES = ("public", "augmented")


def assess_leaf(branch, reply, origin, receipt):
    board, target = post_reply(branch, reply, origin)
    if receipt["status"] != "ready":
        return {"status": receipt["status"]}
    if (chess.square_name(target) != receipt["target_after_reply"]
            or board.fen() != receipt["source"]["leaf_fen"]):
        raise ValueError("Frozen leaf does not match target and game replay")
    proof = solve(board, target)
    menus = receipt["menus"]
    hits = {}
    for policy in POLICIES:
        moves = menus[policy]
        if len(moves) != min(SLOTS, len(proof)) or len(set(moves)) != len(moves):
            raise ValueError("Unexpected menu slot count")
        hits[policy] = [move for move in moves if proof[move]["holds"]]
    truth = [move for move, witness in proof.items() if witness["holds"]]
    return {"status": "judged", "truth": truth, "hits": hits, "proof": proof, "menus": menus,
            "target_moved": target != origin}


def assess(goals, menus):
    leaves = Counter()
    pairs = Counter()
    material = Counter()
    cases = {}
    if menus.keys() != {plan["round"] for plan in goals}:
        raise ValueError("Frozen cases differ")
    for case in goals:
        round_id = case["round"]
        branches = root_boards(case)
        target = chess.parse_square(case["target"])
        outputs = {}
        if menus[round_id].keys() != set(case["replies"]):
            raise ValueError("Frozen replies differ")
        for reply in case["replies"]:
            results = [assess_leaf(branch, reply, target, receipt)
                       for branch, receipt in zip(branches, menus[round_id][reply], strict=True)]
            outputs[reply] = results
            for row in results:
                leaves[row["status"]] += 1
                if row["status"] != "judged":
                    continue
                truth = bool(row["truth"])
                a, b = (bool(row["hits"][policy]) for policy in POLICIES)
                leaves["positive"] += truth
                leaves["public_hits"] += a
                leaves["augmented_hits"] += b
                leaves["gain"] += b and not a
                leaves["loss"] += a and not b
                leaves["substitutions"] += bool(row["menus"]["substitution"])
                if row["target_moved"]:
                    material["moved"] += 1
                    material["moved_positive"] += truth
            if len(results) == 2 and all(row["status"] == "judged" for row in results):
                true_sides = [bool(row["truth"]) for row in results]
                pairs["complete"] += 1
                pairs["different"] += true_sides[0] != true_sides[1]
                for policy in POLICIES:
                    predicted = [bool(row["hits"][policy]) for row in results]
                    pairs[f"{policy}_both_correct"] += predicted == true_sides
                    pairs[f"{policy}_contrast_correct"] += predicted == true_sides and true_sides[0] != true_sides[1]
        nominal = outputs[case["replies"][0]]
        for reply in case["replies"][1:]:
            for baseline, alternative in zip(nominal, outputs[reply], strict=True):
                if baseline["status"] == alternative["status"] == "judged":
                    material["comparable_alternate"] += 1
                    material["nominal_survives"] += bool(baseline["truth"])
                    material["alternate_breaks"] += bool(baseline["truth"]) and not alternative["truth"]
        cases[round_id] = outputs
    return {"leaves": dict(leaves), "pairs": dict(pairs), "target_and_reply": dict(material), "cases": cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goals", type=Path)
    parser.add_argument("menus", type=Path)
    parser.add_argument("menus_sha256")
    args = parser.parse_args()
    if digest(args.menus) != args.menus_sha256:
        raise ValueError("Menus differ from their before-judgment seal")
    goals = json.loads(args.goals.read_text())
    menus = json.loads(args.menus.read_text())
    if menus["goals_sha256"] != digest(args.goals) or menus["engine_sha256"] != SF:
        raise ValueError("Goals or source engine differ")
    print(json.dumps(assess(goals["plans"], menus["rows"]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
