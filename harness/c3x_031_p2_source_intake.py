"""0.31/P2: source-original TWIC1669 PGN intake and pre-native sample freeze.

This program **never executes an engine** and cannot read intervention outcomes.
It freezes full legal histories and the source exclusion ledger before contact.
Original publisher archive/complete PGN belongs in private Drive, never Git.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
from zipfile import ZipFile

import chess
import chess.pgn

from c3x_030_r28_freeze import family

SOURCE_ISSUE=1669
SOURCE_DATE="2026-11-02"
PUBLISHER_LISTED_GAMES=8091
PUBLISHER_RAW_GAMES=8165
SOURCE_ORIGINAL_ZIP_SHA="0d5e76cff28bc18faea0f03987586cceee419471fd7bee963c43b1f7cf6569c1"
SOURCE_ORIGINAL_PGN_SHA="25fe81d76ab9fe53394b2fa59fd313014cfe27ac854b44f95b2e438b07208efb"
SOURCE_LINK="https://theweekinchess.com/zips/twic1669g.zip"
BLOCKLIST_SHA="7b93f5c4539c4da5f6e6d3775a670dba0bc05aaf7588cf8bd0ccaa300a13366a"
SEED="C3X-031-P2-TWIC1669-BLIND-v1"
CHECKPOINTS=(30,41,50,61,70,81)
CAP=64


def require(ok,reason):
    if not ok:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def ordered_hash(label):
    return digest((SEED+"/"+label).encode())


def check_blocklist(path):
    raw=Path(path).read_bytes()
    require(digest(raw)==BLOCKLIST_SHA, "prior R26-R33 family exclusions changed")
    vals=raw.decode().splitlines()
    require(len(vals)==94 and vals==sorted(set(vals)), "incomplete 94-family exclusion census")
    return set(vals)


def make_p2_cohort(archive,blocklist):
    excluded=check_blocklist(blocklist)
    raw=Path(archive).read_bytes()
    archive_sha=digest(raw)
    require(archive_sha == SOURCE_ORIGINAL_ZIP_SHA, "publisher original ZIP changed since initial source prefreeze")
    with ZipFile(io.BytesIO(raw)) as z:
        require(z.testzip() is None, "published ZIP CRC failure")
        members=z.namelist()
        require(len(members)==1 and members[0].lower().endswith(".pgn"),
                "not a single official TWIC PGN")
        member=members[0]
        require("1669" in member.lower(), "wrong source issue inside ZIP")
        pgn_raw=z.read(member)
        pgn_sha=digest(pgn_raw)
        require(pgn_sha == SOURCE_ORIGINAL_PGN_SHA, "publisher PGN member changed")
        require(pgn_raw.count(b'[Event "') == PUBLISHER_RAW_GAMES,
                "publisher source tag census differs from original raw 8165")

    # Latin-1 preserves the bytes used by the original R28 parser; all
    # transformations, including UCI moves and family exclusions, are fixed.
    stream=io.StringIO(pgn_raw.decode("latin-1"))
    counts=Counter()
    pools=defaultdict(list)
    all_games=set()
    seen_all=0
    all_families=set()
    duplicate_games=0
    first_errors=[]
    while game:=chess.pgn.read_game(stream):
        seen_all+=1
        event=game.headers.get("Event","?")
        group=family(event)
        all_families.add(group)
        counts["parsed_games"]+=1
        if event=="?" or not group or game.errors:
            counts["invalid_header_or_moves"]+=1
            if game.errors and len(first_errors)<3:
                first_errors.append({"ordinal":seen_all,"error":str(game.errors[0])[:160]})
            continue
        board=game.board()
        if board.chess960 or board.fen()!=chess.STARTING_FEN:
            counts["nonstandard_start"]+=1
            continue
        moves=[move.uci() for move in game.mainline_moves()]
        game_hash=digest(" ".join(moves).encode())
        if game_hash in all_games:
            duplicate_games+=1
            counts["same_issue_duplicate_full_move_history"]+=1
            continue
        all_games.add(game_hash)
        if group in excluded:
            counts["historical_family_excluded"]+=1
            continue
        ply=CHECKPOINTS[int(ordered_hash(game_hash),16)%len(CHECKPOINTS)]
        if len(moves)<ply:
            counts["too_short_for_fixed_checkpoint"]+=1
            continue
        for uci in moves[:ply]:
            board.push_uci(uci)
        if board.is_game_over() or board.legal_moves.count()<2:
            counts["terminal_or_single_move_position"]+=1
            continue
        counts["eligible_candidate_game"]+=1
        pools[group].append({
            "game_sha256":game_hash,"source_ordinal":seen_all,
            "event":event,"family":group,"ply":ply,"fen":board.fen(),
            "moves":moves[:ply],"legal_moves":board.legal_moves.count(),
        })

    require(seen_all==PUBLISHER_RAW_GAMES,
            f"PGN parser read {seen_all}, but source has {PUBLISHER_RAW_GAMES} event records")
    groups=sorted(pools,key=ordered_hash)
    for group in groups:
        pools[group].sort(key=lambda r:ordered_hash(r["game_sha256"]))
    chosen, seen_games, seen_boards=[],set(),set()
    for index in range(max((len(p) for p in pools.values()),default=0)):
        for group in groups:
            if index>=len(pools[group]):
                continue
            case=pools[group][index]
            fen_key=tuple(case["fen"].split()[:4])
            if case["game_sha256"] in seen_games or fen_key in seen_boards:
                counts["candidate_duplicate_game_or_board"]+=1
                continue
            seen_games.add(case["game_sha256"])
            seen_boards.add(fen_key)
            chosen.append({"id":f"P2-{len(chosen)+1:03}",**case})
            if len(chosen)==CAP:
                break
        if len(chosen)==CAP:
            break
    require(len(chosen)>0,"no P2 candidate games after exclusions")
    require(len({case["family"] for case in chosen})>=min(CAP,len(groups)),
            "failed event-family round-robin")
    require(not ({case["family"] for case in chosen} & excluded),
            "historical event family leakage")

    return {
        "schema":"c3x-031-p2-original-source-candidate-cohort-v1",
        "study_state":"PRE_NATIVE_SOURCE_FREEZE_NOT_EXPERIMENTAL_OUTCOME",
        "origin":"The Week in Chess, Mark Crowther, free personal research use; original rights reserved",
        "publisher_source":SOURCE_LINK,"publisher_issue":SOURCE_ISSUE,
        "publisher_date":SOURCE_DATE,
        "source_zip_sha256":archive_sha,"source_member":member,
        "source_pgn_sha256":pgn_sha,
        "publisher_listed_games":PUBLISHER_LISTED_GAMES,
        "original_pgn_header_records":PUBLISHER_RAW_GAMES,
        "publisher_listing_shortfall":PUBLISHER_RAW_GAMES-PUBLISHER_LISTED_GAMES,
        "parsed_games":seen_all,
        "all_source_distinct_game_hashes":len(all_games),
        "all_source_event_families":len(all_families),
        "prior_event_families_excluded":len(excluded),
        "excluded_families_sha256":BLOCKLIST_SHA,
        "counts":dict(counts),"reported_parse_errors":first_errors,
        "frozen_seed":SEED,"frozen_checkpoints":list(CHECKPOINTS),
        "candidate_eligible_families":len(groups),
        "preselected_games":len(chosen),
        "preselected_unique_families":len({r["family"] for r in chosen}),
        "previous_direct_game_hash_collision_checked":"R33 64 only where separate SHA list available; other prior history blocked by event family",
        "source_native_treatments_seen":0,
        "source_native_discovery_seen":0,
        "positions":chosen,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("publisher_zip",type=Path)
    ap.add_argument("excluded_families",type=Path)
    ap.add_argument("output_json",type=Path)
    args=ap.parse_args()
    result=make_p2_cohort(args.publisher_zip,args.excluded_families)
    args.output_json.write_text(json.dumps(result,indent=2,sort_keys=True,
                                            ensure_ascii=False)+"\n")
    print("P2_SOURCE_PREFREEZE",result["source_zip_sha256"],
          "games",result["parsed_games"],"families",
          result["preselected_unique_families"],"preselected",
          result["preselected_games"],"cohort_sha256",
          digest(args.output_json.read_bytes()))


if __name__=="__main__":
    main()
