"""Run R10 selection, equal-request predictions and separate Berserk judgments."""

import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine
import chess.pgn

PLIES = (24, 32, 40)
COUNT = 8
PGN_SHA = "b417f739dc4adfbbe2c65779336f3da5ab515e999dca1ad1a0c785b3980521c8"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def board_at(history):
    board = chess.Board()
    for move in history:
        board.push_uci(move)
    return board


def analysis(engine, board, perspective, *, nodes=None, depth=None, count=1):
    limit = chess.engine.Limit(nodes=nodes, depth=depth)
    rows = engine.analyse(board, limit, multipv=count, game=object())
    output = []
    for row in rows:
        pv = row.get("pv", [])
        copy = board.copy()
        for move in pv:
            if move not in copy.legal_moves:
                raise ValueError(f"Illegal engine PV: {move.uci()}")
            copy.push(move)
        if row.get("nodes", 0) <= 0 or not pv or (depth and row.get("depth") != depth):
            raise ValueError("Incomplete engine receipt")
        output.append({"cp": row["score"].pov(perspective).score(),
                       "bound": bool(row.get("lowerbound") or row.get("upperbound")),
                       "pv": [m.uci() for m in pv], "nodes": row["nodes"],
                       "depth": row["depth"]})
    return output


def eligible(row):
    return type(row["cp"]) is int and not row["bound"]


def selection(engine, source):
    selections, audit, seen, openings = [], [], set(), set()
    if digest(source) != PGN_SHA:
        raise ValueError("Expected the pinned Division P PGN bytes")
    games = {}
    with source.open(encoding="utf-8-sig") as f:
        while game := chess.pgn.read_game(f):
            raw_round = game.headers["Round"]
            number = tuple(map(int, raw_round.split(".")))
            if len(number) != 2:
                raise ValueError(f"Expected compound round, got {raw_round!r}")
            if number in games:
                raise ValueError(f"Duplicate round {number}")
            games[number] = game
    for number, game in sorted(games.items()):
        round_id = ".".join(map(str, number))
        if game.errors or game.headers.get("Result") == "*" or game.board().fen() != chess.STARTING_FEN:
            audit.append({"round": round_id, "status": "ineligible_game"})
            continue
        moves = [m.uci() for m in game.mainline_moves()]
        opening = tuple(moves[:12])
        if opening in openings:
            audit.append({"round": round_id, "status": "duplicate_opening_prefix"})
            continue
        for ply in PLIES:
            if ply >= len(moves):
                continue
            history = moves[:ply]
            board = board_at(history)
            key = board.epd()
            if key in seen or board.is_repetition(2) or board.is_game_over():
                continue
            rows = analysis(engine, board, board.turn, nodes=48000, count=2)
            audit.append({"round": round_id, "ply": ply, "scan": rows})
            if (len(rows) != 2 or not all(map(eligible, rows))
                    or rows[0]["pv"][0] == rows[1]["pv"][0]
                    or abs(rows[0]["cp"] - rows[1]["cp"]) > 30):
                continue
            seen.add(key)
            openings.add(opening)
            selections.append({"round": round_id, "ply": ply, "history": history,
                               "roots": [r["pv"][0] for r in rows]})
            break
        if len(selections) == COUNT:
            break
    return {"source_sha256": digest(source), "games_read": len(games),
            "selection": selections, "audit": audit}


def predict(engine, board, mover):
    pv, = analysis(engine, board, mover, nodes=48000)
    discovery = analysis(engine, board, mover, nodes=24000, count=3)
    replies = [row["pv"][0] for row in discovery]
    if len(set(replies)) != 3:
        return {"pv": pv, "discovery": discovery, "leaves": {}}
    leaves = {}
    for reply in replies:
        leaf = board.copy()
        leaf.push_uci(reply)
        leaves[reply], = analysis(engine, leaf, mover, nodes=8000)
    return {"pv": pv, "discovery": discovery, "leaves": leaves}


def judge(engine, board, mover):
    replies = dict()
    for move in sorted(board.legal_moves, key=lambda m: m.uci()):
        leaf = board.copy()
        leaf.push(move)
        if leaf.is_game_over(claim_draw=False):
            outcome = leaf.outcome(claim_draw=False)
            cp = 0 if outcome.winner is None else None
            replies[move.uci()] = {"cp": cp, "bound": False, "terminal": True,
                                   "nodes": 0, "pv": [], "depth": 0}
        else:
            replies[move.uci()], = analysis(engine, leaf, mover, depth=12)
    return replies


def evaluate(engine, source, mode):
    data = json.loads(source.read_text())
    rows = []
    positions = data["selection"]
    if data["source_sha256"] != PGN_SHA or not positions:
        raise ValueError("Expected nonempty cohort from the pinned source")
    if len(positions) > COUNT or len({r["round"] for r in positions}) != len(positions):
        raise ValueError("Invalid frozen cohort")
    for position in positions:
        board = board_at(position["history"])
        roots = {}
        for move in position["roots"]:
            after = board.copy()
            after.push_uci(move)
            roots[move] = (predict if mode == "predict" else judge)(engine, after, board.turn)
        rows.append({"round": position["round"], "roots": roots})
    return {"cohort_sha256": digest(source), "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("select", "predict", "judge"))
    parser.add_argument("engine", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("--net", type=Path)
    args = parser.parse_args()
    options = {"Threads": 1, "Hash": 16}
    if args.stage == "judge":
        if not args.net or digest(args.net) != "9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084":
            parser.error("Pinned Berserk network required")
        options["EvalFile"] = str(args.net.resolve())
    else:
        options["Use NNUE"] = False
    with chess.engine.SimpleEngine.popen_uci(str(args.engine.resolve())) as engine:
        engine.configure(options)
        result = (selection(engine, args.source) if args.stage == "select"
                  else evaluate(engine, args.source, args.stage))
        result["binary_sha256"] = digest(args.engine)
        result["engine"] = engine.id
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
