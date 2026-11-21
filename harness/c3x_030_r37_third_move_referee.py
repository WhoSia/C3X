"""R37 independent board-only three-winner referee, no prior PGN history.

Preregistered in docs/C3X_030_R37_THIRD_MOVE_REFEREE_PREREG_20261121.md.
Actual native experiment only when executed with pinned Berserk14 binary and net.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import chess
import chess.engine

FEN = "5rk1/pp1bqppp/6r1/3pP3/3N4/2P1R3/PP2QRPP/6K1 w - - 25 36"
CANDIDATES = {"e2f3": "Qf3", "e2d3": "Qd3", "a2a3": "a3"}
DEPTHS = (10, 12)
REPEATS = (0, 1)
BERSERK_SOURCE_SHA = "8ae895a6151695be4a50d4fb65b0c131659c513a"
BERSERK_NET_SHA = "9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084"
SOURCE_R30_ZIP_SHA = "b42d19601f98fb00ff00e03fb7881bff3bd93114dc9c7b3bcd5876263727449e"


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare():
    """Pre-score inclusion: three frozen moves and every legal first Black reply."""
    board = chess.Board(FEN)
    require(board.turn == chess.WHITE, "source turn changed")
    result = []
    for uci, san in CANDIDATES.items():
        move = chess.Move.from_uci(uci)
        require(move in board.legal_moves, "illegal R30-017 root " + uci)
        require(board.san(move) == san, "source SAN mismatch " + uci)
        child = board.copy(stack=True)
        child.push(move)
        replies = sorted(m.uci() for m in child.legal_moves)
        require(replies, "no eligible Black reply")
        for reply in replies:
            sub = child.copy(stack=True)
            sub.push_uci(reply)
            require(not sub.is_game_over(claim_draw=False), "terminal leaf; new protocol required")
        result.append({"candidate": uci, "san": san, "legal_replies": replies})
    return result


def score_one(eng, board, depth):
    info = eng.analyse(board, chess.engine.Limit(depth=depth),
                       game=object(), info=chess.engine.INFO_ALL)
    complete = int(info.get("depth", -1)) >= depth
    sc = info.get("score")
    require(sc is not None, "referee score absent")
    pov = sc.pov(chess.WHITE)
    mate = pov.mate()
    cp = pov.score(mate_score=None)
    nodes = info.get("nodes")
    pv = [m.uci() for m in info.get("pv", [])]
    require(type(nodes) is int and nodes > 0, "native node count unavailable")
    return {"type": "mate" if mate is not None else "cp",
            "cp": int(cp) if cp is not None else None,
            "mate": int(mate) if mate is not None else None,
            "depth": int(info.get("depth", -1)),
            "nodes": nodes,
            "pv": pv,
            "completed": bool(complete)}


def summarize(cases):
    """No silent pruning of missing replies; judge only complete cold pairs."""
    output = {}
    for c in cases:
        legal = c["legal_replies"]
        require(len(set(legal)) == len(legal), "duplicate opponent reply")
        replies = c["results"]
        require(set(replies) == set(legal), "missing or added legal replies")
        depth_results = {}
        for depth in DEPTHS:
            rows = []
            for reply in legal:
                samples = replies[reply].get(str(depth), [])
                require(len(samples) == len(REPEATS), "missing replay samples")
                a, b = samples
                stable = all(a.get(k) == b.get(k) for k in
                             ("type", "cp", "mate", "depth", "nodes", "pv", "completed"))
                admissible = stable and a["completed"] and b["completed"] and (
                    a["type"] == b["type"] == "cp" and
                    type(a["cp"]) is int and type(b["cp"]) is int)
                rows.append({"reply": reply, "status":
                             "FINITE_REPLAY_PASS" if admissible else
                             "HOLD_MATE_INCOMPLETE_OR_REPLAY_MISMATCH",
                             "score_cp": a["cp"] if admissible else None,
                             "repeats_equal": stable})
            finite = all(x["status"] == "FINITE_REPLAY_PASS" for x in rows)
            worst = min(rows, key=lambda x: (x["score_cp"], x["reply"])) if finite else None
            depth_results[str(depth)] = {
                "all_legal_replies_scored": finite,
                "worst_reply_uci": worst["reply"] if worst else None,
                "worst_white_cp": worst["score_cp"] if worst else None,
                "replies": rows}
        output[c["candidate"]] = depth_results
    comparative = {}
    for depth in DEPTHS:
        all_cp = {k: output[k][str(depth)]["worst_white_cp"] for k in CANDIDATES}
        finite = all(type(v) is int for v in all_cp.values())
        comparative[str(depth)] = {
            "all_candidates_finite": finite,
            "bounded_referee_ranking": sorted(all_cp, key=lambda k: (-all_cp[k], k))
                                       if finite else None,
            "white_cp_minima": all_cp}
    a, b = comparative[str(DEPTHS[0])], comparative[str(DEPTHS[1])]
    stable = a["all_candidates_finite"] and b["all_candidates_finite"] and (
        a["bounded_referee_ranking"] == b["bounded_referee_ranking"])
    return {"candidate_depth_results": output,
            "comparison": comparative,
            "depth_order_status":
                "FINITE_TWO_DEPTH_ORDER_STABLE" if stable else
                "HOLD_OR_DEPTH_ORDER_CHANGED",
            "not_strategic_oracle": True}


def run(engine_path, net_path):
    require(sha(net_path) == BERSERK_NET_SHA, "Berserk network SHA mismatch")
    plan = prepare()
    count = 0
    with chess.engine.SimpleEngine.popen_uci(str(engine_path), timeout=180) as eng:
        require("berserk" in eng.id.get("name", "").lower(),
                "independent Berserk referee identity mismatch")
        require({"Threads", "Hash"}.issubset(eng.options),
                "Berserk Threads/Hash options unavailable")
        eng.configure({"Threads": 1, "Hash": 16})
        for c in plan:
            base = chess.Board(FEN)
            base.push_uci(c["candidate"])
            c["results"] = {}
            for reply in c["legal_replies"]:
                leaf = base.copy(stack=True)
                leaf.push_uci(reply)
                c["results"][reply] = {}
                for depth in DEPTHS:
                    c["results"][reply][str(depth)] = []
                    for _ in REPEATS:
                        c["results"][reply][str(depth)].append(
                            score_one(eng, leaf, depth))
                        count += 1
                        print("R37_COMPLETED", c["candidate"], reply, depth,
                              "search", count, flush=True)
    result = summarize(plan)
    expected = sum(len(c["legal_replies"]) for c in plan) * len(DEPTHS) * len(REPEATS)
    require(count == expected, "new referee search denominator incomplete")
    return {"id": "C3X_030_R37_R30_017_THIRD_MOVE_REFEREE",
            "classification": "POST_SELECTED_EXPOSED_BOARD_ONLY_INDEPENDENT_REFEREE",
            "complete_original_PGN_history_used": False,
            "new_native_searches": count,
            "request_denominator": expected,
            "referee_source_commit": BERSERK_SOURCE_SHA,
            "referee_network_sha256": BERSERK_NET_SHA,
            "referee_binary_sha256": sha(engine_path),
            "source_R30_native_zip_sha256": SOURCE_R30_ZIP_SHA,
            "source_position_fen": FEN,
            "board_side": "white",
            "search_parameters": {"Threads": 1, "Hash_MiB": 16,
                                  "leaf_depths": DEPTHS, "repeats": len(REPEATS),
                                  "fresh_UCI_game_per_leaf": True},
            "total_legal_reply_counts": {c["candidate"]: len(c["legal_replies"]) for c in plan},
            "unfiltered_results": plan,
            "referee_summary": result,
            "claim_limit": ("Finite-depth FEN-only reply-minimum, not exact minimax, "
                            "same-history Stockfish cause, original PGN match, "
                            "population strength, or learner effect.")}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", type=Path, required=True)
    ap.add_argument("--network", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    data = run(args.engine, args.network)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    for depth, row in data["referee_summary"]["comparison"].items():
        print("R37_DEPTH_ORDER", depth, row["bounded_referee_ranking"], row["white_cp_minima"])
    print("R37_FINAL", data["referee_summary"]["depth_order_status"],
          "native_searches", data["new_native_searches"], "json_sha256", sha(args.out))


if __name__ == "__main__":
    main()
