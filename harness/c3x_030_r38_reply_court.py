"""R38: independent verification of R37's actual 540-native-search archive.

This is a *post-outcome analysis* of one exposed FEN-only position, not a
new Stockfish search, independent-game cohort, or proof of plan optimality.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import zipfile

import chess

SOURCE_ARCHIVE_SHA = "5c3ed07315986fe2336f9ee4481c6a2de825285de343169a78d8a403d4eb61e6"
SOURCE_JSON_SHA = "0fa5eadedbdff69b692f1d5d713a4a7649f90f57bfb480eb5f738eccb4bd4fcd"
SOURCE_MEMBER = "C3X_030_R37_R30_017_EXHAUSTIVE_BOARD_ONLY_BERSERK.json"
FEN = "5rk1/pp1bqppp/6r1/3pP3/3N4/2P1R3/PP2QRPP/6K1 w - - 25 36"
DEPTHS = ("10", "12")
CANDIDATES = ("e2f3", "e2d3", "a2a3")
NETWORK_SHA = "9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084"
COMMIT = "8ae895a6151695be4a50d4fb65b0c131659c513a"


def require(ok, why):
    if not ok:
        raise ValueError(why)


def verify(data):
    require(data["id"] == "C3X_030_R37_R30_017_THIRD_MOVE_REFEREE",
            "wrong experiment identity")
    require(data["classification"] == "POST_SELECTED_EXPOSED_BOARD_ONLY_INDEPENDENT_REFEREE",
            "unfounded prospective status")
    require(data["complete_original_PGN_history_used"] is False, "history claim mismatch")
    require(data["source_position_fen"] == FEN, "position mismatch")
    require(data["referee_source_commit"] == COMMIT and
            data["referee_network_sha256"] == NETWORK_SHA, "referee source/network mismatch")
    require(data["search_parameters"]["Threads"] == 1 and
            data["search_parameters"]["Hash_MiB"] == 16 and
            data["search_parameters"]["fresh_UCI_game_per_leaf"] is True,
            "referee setting mismatch")
    require(tuple(data["search_parameters"]["leaf_depths"]) == (10, 12) and
            data["search_parameters"]["repeats"] == 2, "search schedule mismatch")
    cases = {x["candidate"]: x for x in data["unfiltered_results"]}
    require(len(data["unfiltered_results"]) == 3 and set(cases) == set(CANDIDATES),
            "candidate set changed or duplicated")
    board = chess.Board(FEN)
    source_replies = []
    total = 0
    node_total = 0
    minima = {}
    for candidate in CANDIDATES:
        item = cases[candidate]
        move = chess.Move.from_uci(candidate)
        require(move in board.legal_moves and board.san(move) == item["san"],
                "illegal or mismatched original candidate")
        child = board.copy(stack=True)
        child.push(move)
        legal = {m.uci() for m in child.legal_moves}
        advertised = item["legal_replies"]
        require(len(advertised) == len(set(advertised)) and set(advertised) == legal,
                "opponent first-reply census incomplete")
        require(len(legal) == data["total_legal_reply_counts"][candidate] == 45,
                "original legal reply denominator mismatch")
        require(set(item["results"]) == legal, "reply results support incomplete")
        source_replies.append(legal)
        minima[candidate] = {}
        for depth in DEPTHS:
            rows = {}
            for reply in sorted(legal):
                repeats = item["results"][reply].get(depth)
                require(isinstance(repeats, list) and len(repeats) == 2,
                        "missing native repeats")
                a, b = repeats
                require(a == b, "native replay changed")
                for observation in repeats:
                    require(observation["type"] == "cp" and type(observation["cp"]) is int,
                            "mate or noninteger centipawn leaf")
                    require(observation["completed"] is True and
                            observation["depth"] >= int(depth), "censored depth")
                    require(type(observation["nodes"]) is int and observation["nodes"] > 0,
                            "unknown native nodes")
                    require(isinstance(observation["pv"], list) and observation["pv"],
                            "missing finite line")
                    # Actual executed PV moves must be legal on the leaf.
                    leaf = child.copy(stack=True)
                    leaf.push_uci(reply)
                    for uci in observation["pv"]:
                        pv_move = chess.Move.from_uci(uci)
                        require(pv_move in leaf.legal_moves, "illegal reported PV")
                        leaf.push(pv_move)
                    node_total += observation["nodes"]
                    total += 1
                rows[reply] = a["cp"]
            value = min(rows.values())
            worst = min(reply for reply in rows if rows[reply] == value)
            original = data["referee_summary"]["candidate_depth_results"][candidate][depth]
            require(original["all_legal_replies_scored"] is True and
                    original["worst_white_cp"] == value and
                    original["worst_reply_uci"] == worst,
                    "official response minimum inconsistent with raw leaves")
            minima[candidate][depth] = {"score_cp_white": value,
                                        "worst_reply_uci": worst}
    require(source_replies[0] == source_replies[1] == source_replies[2],
            "no shared legal opponent reply panel")
    require(total == data["request_denominator"] == data["new_native_searches"] == 540,
            "native search denominator mismatch")
    response_rank = {}
    for depth in DEPTHS:
        ranks = {}
        for x, y in (("e2f3", "e2d3"), ("e2f3", "a2a3"), ("e2d3", "a2a3")):
            count = Counter()
            for reply in sorted(source_replies[0]):
                diff = (cases[x]["results"][reply][depth][0]["cp"] -
                        cases[y]["results"][reply][depth][0]["cp"])
                count["first_higher" if diff > 0 else "tie" if diff == 0 else "second_higher"] += 1
            ranks[x + "_vs_" + y] = {key: count[key] for key in
                                   ("first_higher", "tie", "second_higher")}
            require(sum(ranks[x + "_vs_" + y].values()) == 45, "pairwise missing replies")
        response_rank[depth] = ranks
        expected_order = sorted(CANDIDATES, key=lambda candidate:
                                (-minima[candidate][depth]["score_cp_white"], candidate))
        declared = data["referee_summary"]["comparison"][depth]
        require(declared["all_candidates_finite"] is True and
                declared["bounded_referee_ranking"] == expected_order,
                "derived candidate ranking mismatch")
        require(expected_order == list(CANDIDATES), "R37 two-depth ranking changed")
    require(data["referee_summary"]["not_strategic_oracle"] is True,
            "unlicensed strategic-oracle promotion")
    require(data["referee_summary"]["depth_order_status"] ==
            "FINITE_TWO_DEPTH_ORDER_STABLE", "finite-depth status incorrectly promoted")
    return {
        "authority": "R37_FROZEN_JSON_ALL_LEAF_RECOMPUTATION",
        "new_engine_searches_in_this_audit": 0,
        "originated_native_searches": total,
        "total_native_nodes": node_total,
        "same_45_opponent_replies_for_all_3_moves": True,
        "independent_game_count": 1,
        "response_minima": minima,
        "conditional_first_move_pairwise_comparison": response_rank,
        "universal_Qf3_over_Qd3": False,
        "strategic_winner_proved": False,
        "full_PGN_history_used": False,
        "human_transfer_measured": False,
    }


def audit_zip(path):
    raw = Path(path).read_bytes()
    require(sha256(raw).hexdigest() == SOURCE_ARCHIVE_SHA, "R37 archive SHA mismatch")
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, "R37 ZIP CRC invalid")
        require(SOURCE_MEMBER in z.namelist(), "R37 JSON member missing")
        data = z.read(SOURCE_MEMBER)
    require(sha256(data).hexdigest() == SOURCE_JSON_SHA, "original native JSON changed")
    return verify(json.loads(data))


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_zip", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()
    output = audit_zip(args.source_zip)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
