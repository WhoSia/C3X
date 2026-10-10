#!/usr/bin/env python3
"""C3X020-C2: engine-free March 2026 broadcast PGN selection, BEFORE native outcomes.

Immutable selector inherited from C3X019 Feb16 with one extra disjoint-month
exclusion. Importing python-chess verifies move legality; NO chess engines.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path

import chess
import chess.pgn
import zstandard

SOURCE_URL = "https://database.lichess.org/broadcast/lichess_db_broadcast_2026-03.pgn.zst"
N_ELIGIBLE = 512
N_SELECT = 16
MAX_SCANNED = 20000
HISTORY_NAMES = ("prior", "october", "november", "december", "january", "february")
REGISTRATION = "c3x/ontology/c3x-020-C-alpha-gate-root-choice-transmission-and-prospective-forecast-precommit.md"

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical_game_fingerprint(headers, moves_uci):
    record = {"headers":dict(headers),"moves_uci":list(moves_uci)}
    return digest(json.dumps(record,sort_keys=True,ensure_ascii=False,
                             separators=(",",":")).encode("utf-8"))

def chosen_ply(fingerprint):
    if not (isinstance(fingerprint,str) and len(fingerprint)==64):
        raise ValueError("INVALID_FINGERPRINT")
    return 30 + (int(fingerprint[:8],16)%15)

def history_overlap(sources):
    if set(sources) != set(HISTORY_NAMES):
        raise ValueError("HISTORICAL_SOURCE_COUNT")
    all_fens=set()
    receipts={}
    for name in HISTORY_NAMES:
        raw=Path(sources[name]).read_bytes()
        data=json.loads(raw)
        candidates=data.get("selected")
        if not isinstance(candidates,list) or len(candidates)==0:
            raise ValueError("EMPTY_PRIOR_HISTORY_"+name)
        receipt={"sha256":digest(raw),"selection_count":len(candidates)}
        receipts[name]=receipt
        for row in candidates:
            fen=row["fen4"]
            if fen in all_fens:
                # Redundant historical FENs do not license new selection.
                continue
            all_fens.add(fen)
    return all_fens, receipts

def select_compressed_archive(path, old_fens):
    archive=Path(path)
    source_sha=digest(archive.read_bytes())
    eligible=[]
    counted={}
    games_seen=set()
    local_fens=set()
    scanned=0
    def excluded(reason):
        counted[reason]=counted.get(reason,0)+1
    with archive.open("rb") as raw:
        with zstandard.ZstdDecompressor().stream_reader(raw) as stream:
            with io.TextIOWrapper(stream,encoding="utf-8",errors="strict") as fp:
                while scanned<MAX_SCANNED and len(eligible)<N_ELIGIBLE:
                    game=chess.pgn.read_game(fp)
                    if game is None:
                        break
                    scanned+=1
                    if game.errors:
                        excluded("PGN_PARSE_ERROR");continue
                    if game.headers.get("Variant","Standard") not in ("Standard","Chess"):
                        excluded("NONSTANDARD_VARIANT");continue
                    board=game.board()
                    if not board.is_valid():
                        excluded("INVALID_INITIAL_BOARD");continue
                    moves=list(game.mainline_moves())
                    if len(moves)<70:
                        excluded("SHORT_GAME");continue
                    uci=[m.uci() for m in moves]
                    fingerprint=canonical_game_fingerprint(game.headers,uci)
                    if fingerprint in games_seen:
                        excluded("DUPLICATE_GAME");continue
                    games_seen.add(fingerprint)
                    at=chosen_ply(fingerprint)
                    try:
                        for move in moves[:at]:
                            if move not in board.legal_moves:
                                raise ValueError("INVALID_MAINLINE")
                            board.push(move)
                        played=moves[at]
                        if played not in board.legal_moves:
                            excluded("ILLEGAL_SELECTED_MOVE");continue
                        if played.promotion:
                            excluded("PROMOTION_MOVE");continue
                        legal_count=board.legal_moves.count()
                        if legal_count<3:
                            excluded("FEWER_THAN_THREE_ROOT_MOVES");continue
                        fen4=" ".join(board.fen(en_passant="fen").split()[:4])
                        if fen4 in old_fens or fen4 in local_fens:
                            excluded("HISTORICAL_OR_MARCH_FEN_OVERLAP");continue
                        local_fens.add(fen4)
                        eligible.append({
                            "id":None,"source_game_sha256":fingerprint,
                            "source_ordinal":scanned,
                            "source_headers":dict(game.headers),
                            "game_url":game.headers.get("GameURL") or game.headers.get("Site",""),
                            "full_original_mainline_uci":uci,
                            "original_mainline_halfmoves":len(uci),
                            "source_ply_before_original_move":at,
                            "fen4":fen4,"played_legal_move_uci":played.uci(),
                            "native_move":played.from_square*64+played.to_square,
                            "source_root_legal_count":legal_count
                        })
                    except ValueError:
                        excluded("INVALID_GAME_MOVE");continue
    if len(eligible)!=N_ELIGIBLE:
        raise RuntimeError("MARCH_ELIGIBLE_512_NOT_FOUND_"+str(len(eligible)))
    selected=sorted(eligible,key=lambda v:v["source_game_sha256"])[:N_SELECT]
    if (len(selected)!=N_SELECT or len({x["fen4"] for x in selected})!=N_SELECT
            or len({x["source_game_sha256"] for x in selected})!=N_SELECT):
        raise RuntimeError("MARCH_SELECTION_UNIQUE_DENOMINATOR")
    for index,row in enumerate(selected,1):
        row["id"]=index
    return selected,source_sha,scanned,counted

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zst",required=True)
    for name in HISTORY_NAMES:
        p.add_argument("--"+name,required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    sources={k:getattr(args,k) for k in HISTORY_NAMES}
    seen,receipts=history_overlap(sources)
    selected,source_sha,scanned,excluded=select_compressed_archive(args.zst,seen)
    report={
        "schema":"c3x020-C2-blind-march2026-engine-free-source16-v1",
        "phase":"SOURCE_ONLY_BEFORE_ANY_MARCH_ENGINE_RESULT",
        "source_url":SOURCE_URL,
        "source_license":"Lichess broadcast PGN CC BY-SA 4.0",
        "compressed_source_sha256":source_sha,
        "prior_input_sha256":receipts,
        "selection_registration":REGISTRATION,
        "selection":"First 512 eligible March games within first 20000 PGN; sort game SHA and take first16; ply 30+SHAprefix8 mod15; exclude six historical sources; no engine",
        "scanned_games":scanned,"eligible_games":N_ELIGIBLE,
        "excluded_counts":excluded,
        "n_historical_unique_fen4":len(seen),
        "selected":selected,
        "limits":["Source month is a shared broadcast ecology; selected games not guaranteed independent random games",
                  "No native chess engine consulted during cohort selection",
                  "This source freeze alone does not validate prospective alpha mechanism"]
    }
    dest=Path(args.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("C3X020_C2_MARCH_ENGINE_FREE_PGN_SELECTED",source_sha,
          digest(dest.read_bytes()),flush=True)
if __name__=="__main__":
    main()
