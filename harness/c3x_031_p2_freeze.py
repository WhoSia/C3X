"""C3X 0.31 P2: strictly pre-treatment, family-filtered TWIC1670 game freeze.

The complete histories are kept in a private workflow artifact/Drive, never in
Git. Selection sees PGN metadata/legal board only and no intervention label.
The original R33 family blacklist is already incorporated in a fixed 17-family
admission map committed before this program is invoked.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import unicodedata
import zipfile

import chess
import chess.pgn

ZIP_SHA = "6e6866cfe57ea0db7849f9b686fded1c1fe9d1fcab783359030b97ace377eccf"
SEED = "C3X-031-P2-TWIC1670-game-freeze-v1"
CHECKPOINTS = (40, 41, 50, 51, 60, 61, 70, 71, 80, 81)
CAP = 64
ADMISSION = "c3x031-p2-prefreeze-family-admission-v1"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def order(value):
    return digest(f"{SEED}/{value}".encode())


def normalize(event):
    return unicodedata.normalize("NFC", event).strip().casefold()


def choose(archive, control):
    raw = Path(archive).read_bytes()
    require(digest(raw) == ZIP_SHA, "publisher byte identity mismatch")
    admission = json.loads(Path(control).read_bytes())
    require(admission.get("schema") == ADMISSION
            and admission.get("source_zip_sha256") == ZIP_SHA
            and admission.get("selection_seed") == SEED
            and admission.get("candidate_ply_order") == list(CHECKPOINTS)
            and admission.get("target_cap") == CAP, "not pre-frozen admission")
    allowed = admission["admitted_family_counts"]
    require(len(allowed) == 17 and sum(allowed.values()) == 2326,
            "original eligible family denominator mismatch")
    pools = defaultdict(list)
    families, rejected, games, total = Counter(), Counter(), set(), 0
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        require(zf.namelist() == ["twic1670.pgn"] and zf.testzip() is None,
                "wrong publisher inner zip")
        stream = io.TextIOWrapper(io.BytesIO(zf.read("twic1670.pgn")), encoding="latin-1")
        while (game := chess.pgn.read_game(stream)) is not None:
            total += 1
            event = normalize(game.headers.get("Event", "?"))
            families[event] += 1
            if event not in allowed:
                rejected["previously_seen_event_family"] += 1
                continue
            if game.errors:
                rejected["pgn_parser_error_in_allowed_family"] += 1
                continue
            board = game.board()
            if board.fen() != chess.STARTING_FEN or board.chess960:
                rejected["nonstandard_start_in_allowed_family"] += 1
                continue
            moves = [move.uci() for move in game.mainline_moves()]
            game_hash = digest(" ".join(moves).encode())
            if game_hash in games:
                rejected["duplicated_full_history_among_allowed"] += 1
                continue
            games.add(game_hash)
            if len(moves) < CHECKPOINTS[0]:
                rejected["shorter_than_first_checkpoint"] += 1
                continue
            # First legal and nonterminal *board* checkpoint from frozen list.
            # Source-native early-return event eligibility remains unknown.
            target = None
            board = game.board()
            for ply, move in enumerate(moves, 1):
                board.push_uci(move)
                if ply not in CHECKPOINTS:
                    continue
                if board.legal_moves.count() >= 2 and not board.is_game_over():
                    target = (ply, board.fen(), list(moves[:ply]))
                    break
            if target is None:
                rejected["no_legal_open_checkpoint"] += 1
                continue
            ply, fen, history = target
            pools[event].append({
                "game_sha256": game_hash,
                "source_ordinal": total,
                "event": game.headers.get("Event", "?"),
                "family": event,
                "ply": ply,
                "fen": fen,
                "moves": history,
                "legal_moves": chess.Board(fen).legal_moves.count(),
            })
    require(total == 8391 and len(families) == 47,
            "original publisher game-family census changed")
    require({name:families[name] for name in allowed} == allowed,
            "family input count changed since preregistration")
    require(sum(families[name] for name in allowed) == 2326,
            "pre-frozen admission total did not match original PGN")
    groups = sorted(pools, key=order)
    for group in groups:
        pools[group].sort(key=lambda row: order(row["game_sha256"]))
    sample, used_games, used_boards = [], set(), set()
    for offset in range(max((len(v) for v in pools.values()), default=0)):
        for group in groups:
            if offset >= len(pools[group]):
                continue
            row = pools[group][offset]
            key = tuple(row["fen"].split()[:4])
            if row["game_sha256"] in used_games or key in used_boards:
                rejected["duplicated_sample_game_or_board"] += 1
                continue
            used_games.add(row["game_sha256"])
            used_boards.add(key)
            sample.append({"id":f"P2-{len(sample)+1:03d}", **row})
            if len(sample) == CAP:
                break
        if len(sample) == CAP:
            break
    require(len(sample) == CAP, "underfilled P2 sample: don't silently change cap")
    require(len({x["family"] for x in sample}) == len(groups),
            "lost a source-eligible family during round robin")
    require(all(len(x["moves"]) == x["ply"] for x in sample),
            "invalid frozen history")
    receipt = {
        "id": "C3X_031_P2_TWIC1670_PRETREATMENT_GAME_FREEZE",
        "admission_input_sha256": digest(Path(control).read_bytes()),
        "raw_source_sha256": ZIP_SHA,
        "selection_seed": SEED,
        "original_pgn_games": total,
        "event_families_in_issue": len(families),
        "admitted_raw_game_headers": 2326,
        "prior_source_family_excluded_raw_headers":
            sum(value for key,value in families.items() if key not in allowed),
        "pretreated_game_count": len(sample),
        "selected_event_family_count": len(groups),
        "eligible_games_by_admitted_family":
            {key:len(value) for key,value in sorted(pools.items())},
        "rejected_raw_records": dict(sorted(rejected.items())),
        "stage": "GAME_HISTORY_SAMPLE_FROZEN_NO_NATIVE_TREATMENTS",
        "source_native_event_selected": False,
        "new_native_stockfish_searches": 0,
        "source_treatments_observed": 0,
        "sample": sample,
    }
    compact = {key:value for key,value in receipt.items() if key != "sample"}
    compact["sample_ids_game_and_position_hashes"] = [
        {"id":r["id"],"game_sha256":r["game_sha256"],"family":r["family"],
         "ply":r["ply"],"board_four_field_sha256":
            digest(" ".join(r["fen"].split()[:4]).encode())}
        for r in sample]
    return receipt, compact


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("twic1670_zip",type=Path)
    p.add_argument("frozen_admission_json",type=Path)
    p.add_argument("private_full_history_output",type=Path)
    p.add_argument("public_manifest_output",type=Path)
    args=p.parse_args()
    raw, compact=choose(args.twic1670_zip,args.frozen_admission_json)
    for dest,val in [(args.private_full_history_output,raw),
                     (args.public_manifest_output,compact)]:
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(val,sort_keys=True,indent=2)+"\n")
    print("P2_GAME_FREEZE",raw["pretreated_game_count"],"families",
          raw["selected_event_family_count"],"SHA_PRIVATE",
          digest(args.private_full_history_output.read_bytes()),"SHA_PUBLIC",
          digest(args.public_manifest_output.read_bytes()),
          "ENGINE_TREATMENTS",raw["source_treatments_observed"])


if __name__=="__main__":
    main()
