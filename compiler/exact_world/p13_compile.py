#!/usr/bin/env python3
import argparse
import hashlib
import json
import random
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import chess

API = "https://tablebase.lichess.ovh/standard"
VERSION = "c3x-p13-stage-a-v1"

MATERIALS = [
    ("KQvKR", [(chess.WHITE, chess.KING), (chess.WHITE, chess.QUEEN),
               (chess.BLACK, chess.KING), (chess.BLACK, chess.ROOK)]),
    ("KRvKQ", [(chess.WHITE, chess.KING), (chess.WHITE, chess.ROOK),
               (chess.BLACK, chess.KING), (chess.BLACK, chess.QUEEN)]),
    ("KQvKB", [(chess.WHITE, chess.KING), (chess.WHITE, chess.QUEEN),
               (chess.BLACK, chess.KING), (chess.BLACK, chess.BISHOP)]),
    ("KQvKN", [(chess.WHITE, chess.KING), (chess.WHITE, chess.QUEEN),
               (chess.BLACK, chess.KING), (chess.BLACK, chess.KNIGHT)]),
    ("KRBvKR", [(chess.WHITE, chess.KING), (chess.WHITE, chess.ROOK), (chess.WHITE, chess.BISHOP),
                (chess.BLACK, chess.KING), (chess.BLACK, chess.ROOK)]),
    ("KRNvKR", [(chess.WHITE, chess.KING), (chess.WHITE, chess.ROOK), (chess.WHITE, chess.KNIGHT),
                (chess.BLACK, chess.KING), (chess.BLACK, chess.ROOK)]),
    ("KRRvKR", [(chess.WHITE, chess.KING), (chess.WHITE, chess.ROOK), (chess.WHITE, chess.ROOK),
                (chess.BLACK, chess.KING), (chess.BLACK, chess.ROOK)]),
    ("KBBvKN", [(chess.WHITE, chess.KING), (chess.WHITE, chess.BISHOP), (chess.WHITE, chess.BISHOP),
                (chess.BLACK, chess.KING), (chess.BLACK, chess.KNIGHT)]),
]

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def conservative_state_key(board: chess.Board) -> str:
    ep = "-" if board.ep_square is None else chess.square_name(board.ep_square)
    return " ".join([
        board.board_fen(),
        "w" if board.turn == chess.WHITE else "b",
        board.castling_xfen() or "-",
        ep,
        str(board.halfmove_clock),
    ])

def position_candidate(material_name, pieces, side, generation_index):
    seed_text = f"{VERSION}|{material_name}|{'w' if side else 'b'}|{generation_index}"
    seed = int.from_bytes(hashlib.sha256(seed_text.encode()).digest()[:8], "big")
    rng = random.Random(seed)
    squares = list(chess.SQUARES)
    rng.shuffle(squares)

    board = chess.Board(None)
    for (color, piece_type), sq in zip(pieces, squares):
        board.set_piece_at(sq, chess.Piece(piece_type, color))
    board.turn = side
    board.castling_rights = chess.BB_EMPTY
    board.ep_square = None
    board.halfmove_clock = 0
    board.fullmove_number = 1

    if not board.is_valid():
        return None
    if board.is_game_over(claim_draw=False):
        return None
    legal = list(board.legal_moves)
    if len(legal) < 2:
        return None
    return board

def tb_query(fen, retries=5):
    url = API + "?" + urllib.parse.urlencode({"fen": fen})
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "C3X-P13/1.0 outcome-blind exact-world compiler"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
            obj = json.loads(raw)
            return obj, sha256_bytes(raw), url
        except Exception as exc:
            last = exc
            time.sleep(0.75 * (attempt + 1))
    raise RuntimeError(f"tablebase query failed for {fen}: {last}")

def robust_world_receipt(board):
    obj, raw_sha, url = tb_query(board.fen())
    # Current Lichess tablebase API exposes robust WDL through category strings.
    # Cursed-win / blessed-loss are intentionally excluded from the first tranche.
    cat_to_wdl = {"win": 2, "draw": 0, "loss": -2}
    root_category = obj.get("category")
    if root_category not in cat_to_wdl:
        return None
    root_wdl = cat_to_wdl[root_category]

    move_rows = []
    for item in obj.get("moves", []):
        successor_category = item.get("category")
        if successor_category not in cat_to_wdl:
            return None
        sw = cat_to_wdl[successor_category]
        mover_wdl = -sw
        move_rows.append({
            "uci": item["uci"],
            "mover_wdl": mover_wdl,
            "successor_wdl_raw": sw,
            "successor_category": successor_category,
            "dtz": item.get("dtz"),
            "zeroing": bool(item.get("zeroing", False)),
        })
    if len(move_rows) < 2:
        return None

    vals = [m["mover_wdl"] for m in move_rows]
    best = max(vals)
    if all(v == best for v in vals):
        return None

    counts = Counter(vals)
    receipt = {
        "provider": "lichess-syzygy-http",
        "endpoint": API,
        "query_url": url,
        "root_wdl": int(root_wdl),
        "root_category": root_category,
        "moves": sorted(move_rows, key=lambda x: x["uci"]),
        "world_pattern": {str(k): counts[k] for k in sorted(counts)},
        "optimal_count": sum(v == best for v in vals),
        "strictly_worse_count": sum(v < best for v in vals),
        "raw_response_sha256": raw_sha,
    }
    return receipt

def tau4(board, max_paths=350000):
    endpoints = defaultdict(list)
    path_count = 0
    excluded_history = 0
    overflow = False
    root_key = conservative_state_key(board)

    def dfs(b, depth, moves, seen):
        nonlocal path_count, excluded_history, overflow
        if overflow:
            return
        if depth == 4:
            path_count += 1
            if path_count > max_paths:
                overflow = True
                return
            key = conservative_state_key(b)
            legal_hash = sha256_bytes(" ".join(sorted(m.uci() for m in b.legal_moves)).encode())
            endpoints[(key, legal_hash)].append(" ".join(moves))
            return

        if b.is_game_over(claim_draw=False):
            return

        for mv in list(b.legal_moves):
            b.push(mv)
            key = conservative_state_key(b)
            repeated = key in seen
            # Root halfmove clock is 0, the universe is pawnless, and depth is only 4.
            # With repeated conservative states rejected here, neither a threefold
            # claim nor a fifty-move claim can become newly available inside this
            # path. Avoid python-chess's expensive claim search without weakening
            # the frozen history-safety condition.
            if repeated:
                excluded_history += 1
                b.pop()
                continue
            dfs(b, depth + 1, moves + [mv.uci()], seen | {key})
            b.pop()
            if overflow:
                return

    dfs(board.copy(stack=False), 0, [], {root_key})
    if overflow:
        return {
            "tau4": None,
            "duplicate_endpoint_states": None,
            "enumerated_depth4_paths": path_count,
            "excluded_history_paths": excluded_history,
            "overflow": True,
        }

    dup_states = 0
    tau = 0
    witnesses = []
    for (key, legal_hash), paths in endpoints.items():
        unique = sorted(set(paths))
        if len(unique) >= 2:
            dup_states += 1
            tau += len(unique) - 1
            if len(witnesses) < 3:
                witnesses.append({
                    "endpoint_state": key,
                    "legal_move_set_sha256": legal_hash,
                    "paths": unique[:4],
                })
    return {
        "tau4": tau,
        "duplicate_endpoint_states": dup_states,
        "enumerated_depth4_paths": path_count,
        "excluded_history_paths": excluded_history,
        "overflow": False,
        "witnesses": witnesses,
    }

def material_signature(board):
    chars = []
    for color, prefix in [(chess.WHITE, "W"), (chess.BLACK, "B")]:
        c = Counter()
        for piece in board.piece_map().values():
            if piece.color == color:
                c[piece.symbol().upper()] += 1
        body = "".join(p * c[p] for p in "KQRBN" if c[p])
        chars.append(prefix + body)
    return "_".join(chars)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--target-count", type=int, default=32)
    ap.add_argument("--max-generated", type=int, default=320)
    args = ap.parse_args()

    accepted = []
    audited = 0
    world_pass = 0

    schedule = []
    per_material = max(1, args.max_generated // (len(MATERIALS) * 2))
    for generation_index in range(per_material):
        for material_name, pieces in MATERIALS:
            for side in (chess.WHITE, chess.BLACK):
                schedule.append((material_name, pieces, side, generation_index))
    schedule = schedule[:args.max_generated]

    for material_name, pieces, side, generation_index in schedule:
        if len(accepted) >= args.target_count:
            break
        board = position_candidate(material_name, pieces, side, generation_index)
        if board is None:
            continue
        audited += 1

        try:
            world = robust_world_receipt(board)
        except RuntimeError as exc:
            print(f"WORLD_QUERY_RETRY_EXHAUSTED {exc}", flush=True)
            continue
        time.sleep(0.06)
        if world is None:
            continue
        world_pass += 1

        tau = tau4(board)
        if tau["overflow"] or not tau["tau4"] or tau["tau4"] <= 0:
            continue

        base = {
            "compiler_version": VERSION,
            "generation_index": generation_index,
            "material_seed_name": material_name,
            "material_signature": material_signature(board),
            "side_to_move": "WHITE" if board.turn else "BLACK",
            "fen": board.fen(),
            "legal_move_count": board.legal_moves.count(),
            "world": world,
            "tau4": tau,
        }
        cid = sha256_bytes(canonical_json(base))
        base["candidate_sha256"] = cid
        accepted.append(base)
        print(
            f"STAGE_A_ACCEPT {len(accepted):02d}/{args.target_count} "
            f"id={cid[:12]} material={base['material_signature']} "
            f"turn={base['side_to_move']} tau4={tau['tau4']}",
            flush=True,
        )

    if len(accepted) < args.target_count:
        raise SystemExit(
            f"WORLD-AUTHORITY-FAIL insufficient Stage-A pool: {len(accepted)}/{args.target_count}; "
            f"audited={audited} world_pass={world_pass}"
        )

    payload = {
        "schema": "c3x-p13-stage-a-pool-v1",
        "scientific_stage": "C3X 0.7.0-G9.4-P13",
        "compiler_version": VERSION,
        "stockfish_outcomes_consulted": False,
        "world_authority": {
            "provider": "Lichess public Syzygy tablebase API",
            "endpoint": API,
            "root_halfmove_clock": 0,
            "pawnless": True,
            "robust_wdl_only": [-2, 0, 2],
        },
        "tau4_definition": {
            "depth": 4,
            "state_key": "board + side + castling + en-passant + halfmove clock",
            "history_guard": "no repeated conservative state within path; no claimable threefold/fifty-move state",
        },
        "audit_counts": {
            "generated_schedule": len(schedule),
            "legal_nonterminal_audited": audited,
            "world_split_pass": world_pass,
            "stage_a_accepted": len(accepted),
        },
        "candidates": accepted,
    }
    payload["pool_sha256"] = sha256_bytes(canonical_json(payload))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"STAGE_A_PASS n={len(accepted)} pool_sha256={payload['pool_sha256']}")

if __name__ == "__main__":
    main()
