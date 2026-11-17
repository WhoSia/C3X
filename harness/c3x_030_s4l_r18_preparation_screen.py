"""Find paired preparation questions without reading any plan labels."""

import argparse
from collections import Counter
import json
import logging
from pathlib import Path

import chess.engine

from c3x_030_s4l_r10_reply_transport import analysis, digest, selection
from c3x_030_s4l_r11_allocation import SF
from c3x_030_s4l_r14_matched_trace import OPTIONS
from c3x_030_s4l_r16_plan_source import R14, named_victim, post_reply, root_boards


PGN = "295deb030c84f0952fab3ccf56c4c592aa69484566c39e7356f7ef0f706df54b"
R16 = "745645505b89849b54ace84a30491b3f0af0ef632801a436990ca230d6632da0"


def requires_preparation(board, victim):
    return (not board.is_game_over(claim_draw=False) and
            not any(board.generate_legal_captures(to_mask=chess.BB_SQUARES[victim])))


def admissible_replies(boards, ordered, victim):
    accepted = []
    for reply in ordered:
        if all(requires_preparation(*post_reply(branch, reply, victim)) for branch in boards):
            accepted.append(reply)
    return accepted


def pick_plan(case, boards, lines, counts):
    first, second = boards
    common = {m.uci() for m in first.legal_moves} & {m.uci() for m in second.legal_moves}
    shared = [record["pv"] for record in lines if record["pv"][0] in common]
    for line in shared:
        target = named_victim(first, second, line)
        if target is None:
            continue
        counts["named_lines"] += 1
        reply = line[0]
        if not admissible_replies(boards, [reply], target):
            counts["nominal_reply_ineligible"] += 1
            continue
        ordered = list(dict.fromkeys([reply, *(pv[0] for pv in shared), *sorted(common)]))
        replies = admissible_replies(boards, ordered, target)[:4]
        if len(replies) < 2:
            counts["insufficient_eligible_replies"] += 1
            continue
        return {**case, "target": chess.square_name(target),
                "target_piece": first.piece_at(target).symbol(), "replies": replies,
                "nominal_pv": line, "source_lines": lines}
    return None


def nominate(engine, pgn, r14, r16):
    prior_cases = [case for path in (r14, r16)
                   for case in json.loads(path.read_text())["cohort"]["selection"]]
    excluded = [tuple(case["history"][:12]) for case in prior_cases]
    with chess.engine.SimpleEngine.popen_uci(str(engine.resolve()), timeout=45) as source:
        source.configure(OPTIONS)
        cohort = selection(source, pgn, count=64, expected_sha=PGN, excluded_openings=excluded)
        plans = []
        counts = Counter()
        for case in cohort["selection"]:
            counts["near_pairs_examined_for_preparation"] += 1
            boards = root_boards(case)
            lines = analysis(source, boards[0], not boards[0].turn, nodes=12000, count=3)
            plan = pick_plan(case, boards, lines, counts)
            if plan is not None:
                plans.append(plan)
            if len(plans) == 8:
                break
    return {"cohort": cohort, "plans": plans, "screen_counts": dict(counts)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("engine", "pgn", "r14", "r16"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    if (digest(args.engine), digest(args.pgn), digest(args.r14), digest(args.r16)) != (SF, PGN, R14, R16):
        parser.error("Expected the frozen engine, Swiss 9 PGN and parent cohorts")
    logging.getLogger("chess.engine").setLevel(logging.ERROR)
    print(json.dumps(nominate(args.engine, args.pgn, args.r14, args.r16), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
