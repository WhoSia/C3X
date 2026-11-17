"""Screen fixed candidate pairs on disjoint S28 Division P game histories."""

import argparse
from collections import Counter
import json
import logging
from pathlib import Path

import chess.engine
import chess.pgn

from c3x_030_s4l_r10_reply_transport import PLIES, analysis, board_at, digest, eligible
from c3x_030_s4l_r11_allocation import SF, receipt
from c3x_030_s4l_r12_reply_questions import freeze
from c3x_030_s4l_r14_matched_trace import OPTIONS

SOURCE = "5842788c3bb1e4e724989827d3aa64f92e8f9c2a3300e662bb61bc62183dada2"
EXCLUSIONS = (
    "b417f739dc4adfbbe2c65779336f3da5ab515e999dca1ad1a0c785b3980521c8",
    "60524a292b71ee2b4711e01ce22623a86e58483cc096aaa4f5c6e7584179e853",
    "295deb030c84f0952fab3ccf56c4c592aa69484566c39e7356f7ef0f706df54b",
    "59f4a9e2c4de583105a9d4051cb1e0b2d7d73a03bc69871cd3edd96a9c2fa38a",
)
BUDGETS = (24000, 48000)
GAME_CAP = 24
PAIR_CAP = 8


def games(path):
    with path.open(encoding="utf-8-sig") as stream:
        while game := chess.pgn.read_game(stream):
            yield game


def moves_of(game):
    if game.errors or game.board().fen() != chess.STARTING_FEN:
        raise ValueError("Unexpected archive game or start position")
    history = [move.uci() for move in game.mainline_moves()]
    if "0000" in history:
        raise ValueError("Unexpected null move in game history")
    return history


def excluded_prefixes(paths):
    if tuple(map(digest, paths)) != EXCLUSIONS:
        raise ValueError("Unexpected historical exclusion digest")
    prior = json.loads(paths[-1].read_text())["cohort"]["selection"]
    blocked = {tuple(case["history"][:12]) for case in prior}
    for path in paths[:-1]:
        blocked.update(tuple(moves_of(game)[:12]) for game in games(path))
    return blocked


def forced(engine, board, root, budget):
    point = None
    with engine.analysis(board, chess.engine.Limit(nodes=budget),
                         root_moves=[board.parse_uci(root)], game=object()) as stream:
        for info in stream:
            result = receipt(info, board.turn, board)
            if result and result["cp"] is not None and not result["bound"]:
                if result["pv"][0] != root:
                    raise ValueError("The result escaped the root restriction")
                point = result
        final_nodes = stream.info.get("nodes")
    return {"point": point, "actual_nodes": final_nodes}


def pair_screen(engine, board, *, allow_bound_nomination=False):
    preview = analysis(engine, board, board.turn, nodes=12000, count=2)
    nominations_ok = all(type(row["cp"]) is int for row in preview) if allow_bound_nomination else all(map(eligible, preview))
    if len(preview) != 2 or not nominations_ok:
        return {"status": "missing_preview", "preview": preview}
    roots = [row["pv"][0] for row in preview]
    if len(set(roots)) != 2:
        raise ValueError("Repeated nominee")
    runs = {str(budget): [forced(engine, board, root, budget) for root in roots]
            for budget in BUDGETS}
    points = [[r["point"] for r in pair] for pair in runs.values()]
    if any(point is None for pair in points for point in pair):
        return {"status": "missing_point", "nominees": roots, "runs": runs}
    gaps = [a["cp"] - b["cp"] for a, b in points]
    admitted = all(5 <= gap <= 25 for gap in gaps) or all(-25 <= gap <= -5 for gap in gaps)
    return {"status": "admitted" if admitted else "outside_contract", "nominees": roots,
            "runs": runs, "gaps": gaps, "roots": roots if gaps[0] > 0 else roots[::-1]}


def replies_for(engine, case):
    board = board_at(case["history"])
    branches = [board.copy() for _ in case["roots"]]
    for branch, root in zip(branches, case["roots"], strict=True):
        branch.push_uci(root)
        if branch.is_game_over(claim_draw=False) or branch.legal_moves.count() < 3:
            return [], []
    discovery = [analysis(engine, branch, board.turn, nodes=6000, count=3)
                 for branch in branches]
    chosen = []
    for rank in zip(*discovery, strict=True):
        for row in rank:
            reply = chess.Move.from_uci(row["pv"][0])
            if reply.uci() in chosen or any(reply not in branch.legal_moves for branch in branches):
                continue
            leaves = [branch.copy() for branch in branches]
            for leaf in leaves:
                leaf.push(reply)
            if any(leaf.is_game_over(claim_draw=False) for leaf in leaves):
                continue
            chosen.append(reply.uci())
            if len(chosen) == 2:
                return chosen, discovery
    return chosen, discovery


def select(engine, source, blocked, *, expected_sha=SOURCE, game_cap=GAME_CAP,
           pair_cap=PAIR_CAP, reply_selector=replies_for, allow_bound_nomination=False):
    if digest(source) != expected_sha:
        raise ValueError("Unexpected S28 archive digest")
    indexed = {}
    for game in games(source):
        key = tuple(map(int, game.headers["Round"].split(".")))
        if len(key) != 2 or key in indexed:
            raise ValueError("Unexpected round sequence in S28 archive")
        indexed[key] = game
    selected, requests, audit = [], [], []
    counts = Counter()
    roots_seen = set()
    screened_openings = set()
    for number, game in sorted(indexed.items()):
        if counts["screened_games"] == game_cap or len(selected) == pair_cap:
            break
        history = moves_of(game)
        prefix = tuple(history[:12])
        if game.headers["Result"] == "*" or len(history) <= min(PLIES):
            counts["ineligible_game"] += 1
            continue
        if prefix in blocked or prefix in screened_openings:
            counts["blocked_opening"] += 1
            continue
        screened_openings.add(prefix)
        counts["screened_games"] += 1
        round_id = ".".join(map(str, number))
        for ply in PLIES:
            if ply >= len(history):
                continue
            board = board_at(history[:ply])
            key = board.epd()
            if key in roots_seen or board.is_repetition(2) or board.is_game_over():
                counts["blocked_position"] += 1
                continue
            roots_seen.add(key)
            screen = pair_screen(engine, board, allow_bound_nomination=allow_bound_nomination)
            counts[screen["status"]] += 1
            audit.append({"round": round_id, "ply": ply, **screen})
            if screen["status"] != "admitted":
                continue
            case = {"round": round_id, "ply": ply, "history": history[:ply],
                    "roots": screen["roots"], "gaps": [abs(gap) for gap in screen["gaps"]]}
            replies, discovery = reply_selector(engine, case)
            selected.append({**case, "replies": replies, "discovery": discovery})
            if len(replies) == 2:
                requests.extend({"round": round_id, "reply": reply} for reply in replies)
            break
    cohort = {"source_sha256": expected_sha, "source_engine_sha256": SF, "games_read": len(indexed),
              "excluded_prefix_count": len(blocked), "counts": counts, "selection": selected,
              "audit": audit}
    return {**cohort, "questions": freeze(cohort, requests) if requests else {}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stockfish", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("excluded", type=Path, nargs=4)
    args = parser.parse_args()
    if digest(args.stockfish) != SF:
        raise ValueError("Expected the pinned native Stockfish binary")
    logging.getLogger("chess.engine").setLevel(logging.ERROR)
    with chess.engine.SimpleEngine.popen_uci(str(args.stockfish.resolve())) as engine:
        engine.configure(OPTIONS)
        output = select(engine, args.source, excluded_prefixes(args.excluded))
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
