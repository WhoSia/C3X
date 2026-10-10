#!/usr/bin/env python3
"""C3X022-P2 TWO new chess source ecologies, no chess engine.

TWIC issue zip is input only: NEVER redistributed in action artifacts.
Lichess puzzle FEN is before first scripted adversary move: MUST push it first.
"""
import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path
import chess
import chess.pgn
import zstandard
from c3x_020_C_March2026_enginefree_blind16 import canonical_game_fingerprint,chosen_ply

HISTORY=("prior","october","november","december","january","february","march","april")
TWIC_URL="https://theweekinchess.com/zips/twic1656g.zip"
PUZZLE_URL="https://database.lichess.org/lichess_db_puzzle.csv.zst"
TWIC_ISSUE=1656
N_ELIGIBLE=512
N_SELECT=16
TWIC_MAX_SCANNED=20000
PUZZLE_MAX_SCANNED=20000
P2_PRECOMMIT="c3x/ontology/c3x-022-P2-TWIC-Lichess-puzzles-exact-move-forecast-precommit.md"
SOURCE_SHA_PINS={
  "march":"d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee",
  "april":"0e5516fc0cd49203bf7cc366f4133d6c9b20a2f21de0667468f121e398d2fa93"
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def prior_fens(paths):
    if set(paths)!=set(HISTORY):
        raise ValueError("EXACT_8_HISTORY_INPUTS_REQUIRED")
    seen=set()
    prior={}
    for name in HISTORY:
        raw=Path(paths[name]).read_bytes()
        digest=sha(raw)
        if name in SOURCE_SHA_PINS and digest != SOURCE_SHA_PINS[name]:
            raise ValueError("HISTORIC_SHA_CHANGED_"+name)
        d=json.loads(raw)
        selected=d.get("selected")
        if not selected:
            raise ValueError("EMPTY_PRIOR_GAME_SOURCE_"+name)
        for x in selected:
            fen4=x["fen4"]
            if len(fen4.split())!=4:
                raise ValueError("BAD_HISTORY_FEN4")
            seen.add(fen4)
        prior[name]={"sha256":digest,"selected_games":len(selected)}
    return seen,prior

def twic(path,history):
    archive=Path(path)
    archive_sha=sha(archive.read_bytes())
    accepted=[]
    within=set()
    fingerprints=set()
    excluded={}
    scanned=0
    def reject(reason):
        excluded[reason]=excluded.get(reason,0)+1
    with zipfile.ZipFile(archive) as z:
        members=sorted(n for n in z.namelist() if n.lower().endswith(".pgn") and not n.startswith("__MACOSX"))
        if not members:
            raise ValueError("TWIC_OFFICIAL_ZIP_LACKS_PGN")
        with z.open(members[0]) as raw, io.TextIOWrapper(raw,encoding="utf-8",errors="replace") as fp:
            while scanned<TWIC_MAX_SCANNED and len(accepted)<N_ELIGIBLE:
                game=chess.pgn.read_game(fp)
                if game is None:
                    break
                scanned+=1
                if game.errors:
                    reject("PGN_ERROR");continue
                if game.headers.get("Variant","Standard") not in ("Standard","Chess"):
                    reject("NONSTANDARD");continue
                moves=list(game.mainline_moves())
                if len(moves)<70:
                    reject("SHORT");continue
                uci=[m.uci() for m in moves]
                fingerprint=canonical_game_fingerprint(game.headers,uci)
                if fingerprint in fingerprints:
                    reject("REPEATED_GAME");continue
                fingerprints.add(fingerprint)
                index=chosen_ply(fingerprint)
                board=game.board()
                if not board.is_valid():
                    reject("INVALID_BOARD");continue
                ok=True
                for m in moves[:index]:
                    if m not in board.legal_moves:
                        ok=False;break
                    board.push(m)
                if not ok:
                    reject("ILLEGAL_PREFIX");continue
                played=moves[index]
                if played not in board.legal_moves or played.promotion:
                    reject("ILLEGAL_OR_PROMOTION");continue
                if board.legal_moves.count()<3:
                    reject("FEW_MOVES");continue
                fen4=" ".join(board.fen(en_passant="fen").split()[:4])
                if fen4 in history or fen4 in within:
                    reject("HISTORIC_OR_LOCAL_DUPLICATE");continue
                within.add(fen4)
                accepted.append({
                    "id":None,
                    "source_game_sha256":fingerprint,
                    "fen4":fen4,
                    "played_legal_move_uci":played.uci(),
                    "native_move":played.from_square*64+played.to_square,
                    "source_root_legal_count":board.legal_moves.count(),
                    "source_ordinal":scanned,
                    "source_ply_before_original_move":index,
                    "source_original_mainline_halfmoves":len(uci),
                    "source_halfmove_clock":board.halfmove_clock,
                    "source_fullmove_number":board.fullmove_number,
                    "source_issue":TWIC_ISSUE,
                    "source_event":game.headers.get("Event",""),
                    "source_game_date":game.headers.get("Date",""),
                    # no full game moves or headers redistributed
                })
    if len(accepted)!=N_ELIGIBLE:
        raise RuntimeError("TWIC_ELIGIBLE_512_NOT_FOUND_"+str(len(accepted)))
    chosen=sorted(accepted,key=lambda row:row["source_game_sha256"])[:N_SELECT]
    for idx,row in enumerate(chosen,1):row["id"]=idx
    return chosen,{"zip_sha256":archive_sha,"zip_member_names":members,
                   "scanned":scanned,"eligible":N_ELIGIBLE,
                   "excluded":excluded,"no_TWIC_PGN_redistributed":True}

def puzzles(path,history):
    compressed=Path(path)
    archive_sha=sha(compressed.read_bytes())
    accepted=[]
    seen_ids=set()
    within=set()
    scanned=0
    excluded={}
    def reject(reason):
        excluded[reason]=excluded.get(reason,0)+1
    with compressed.open("rb") as raw:
        with zstandard.ZstdDecompressor().stream_reader(raw) as stream:
            with io.TextIOWrapper(stream,encoding="utf-8",errors="strict",newline="") as fp:
                reader=csv.DictReader(fp)
                required={"PuzzleId","FEN","Moves","Rating","Themes","GameUrl"}
                if not required.issubset(set(reader.fieldnames or [])):
                    raise ValueError("OFFICIAL_PUZZLE_CSV_SCHEMA_DRIFT")
                while scanned<PUZZLE_MAX_SCANNED and len(accepted)<N_ELIGIBLE:
                    try:
                        row=next(reader)
                    except StopIteration:
                        break
                    scanned+=1
                    ident=row["PuzzleId"]
                    if not ident or ident in seen_ids:
                        reject("BAD_OR_DUPLICATE_PUZZLE_ID");continue
                    seen_ids.add(ident)
                    moves=row["Moves"].strip().split()
                    if len(moves)<2:
                        reject("NO_SOLVER_REPLY");continue
                    try:
                        b=chess.Board(row["FEN"])
                        if not b.is_valid():
                            reject("INVALID_BOARD");continue
                        sequence=[chess.Move.from_uci(u) for u in moves]
                        if any(m not in b.legal_moves for m in sequence[:1]):
                            reject("ILLEGAL_SOURCE_FIRST_MOVE");continue
                        b.push(sequence[0])
                        if b.legal_moves.count()<3 or sequence[1] not in b.legal_moves or sequence[1].promotion:
                            reject("ILLEGAL_SOLVER_ROOT");continue
                        fen4=" ".join(b.fen(en_passant="fen").split()[:4])
                        if fen4 in history or fen4 in within:
                            reject("HISTORIC_OR_TWIC_OR_LOCAL_DUPLICATE");continue
                        # Validate entire given solution script without using chess engine.
                        check=b.copy()
                        for m in sequence[1:]:
                            if m not in check.legal_moves:
                                raise ValueError("ILLEGAL_SCRIPT_MOVE")
                            check.push(m)
                    except (ValueError,TypeError,chess.InvalidMoveError):
                        reject("BROKEN_MOVE_SCRIPT");continue
                    within.add(fen4)
                    key=sha((ident+"|"+fen4).encode("utf-8"))
                    accepted.append({
                        "id":None,"source_game_sha256":key,
                        "source_puzzle_id":ident,
                        "source_ordinal":scanned,
                        "fen4":fen4,
                        # Puzzle solution initial move is the F prioritization source.
                        # It is NOT a blind independent chess prediction.
                        "played_legal_move_uci":sequence[1].uci(),
                        "native_move":sequence[1].from_square*64+sequence[1].to_square,
                        "source_root_legal_count":b.legal_moves.count(),
                        "source_ply_before_original_move":1,
                        "source_halfmove_clock":b.halfmove_clock,
                        "source_fullmove_number":b.fullmove_number,
                        "puzzle_rating":row["Rating"],
                        "puzzle_themes":row["Themes"].split(),
                        "source_game_url":row["GameUrl"],
                        "source_moves_sha256":sha(row["Moves"].encode("utf-8")),
                        "puzzle_solution_was_used_to_define_F_source_move":True
                    })
    if len(accepted)!=N_ELIGIBLE:
        raise RuntimeError("PUZZLE_ELIGIBLE_512_NOT_FOUND_"+str(len(accepted)))
    chosen=sorted(accepted,key=lambda r:r["source_game_sha256"])[:N_SELECT]
    for idx,row in enumerate(chosen,1):row["id"]=idx
    return chosen,{"compressed_file_sha256":archive_sha,
                   "scanned":scanned,"eligible":N_ELIGIBLE,
                   "excluded":excluded,
                   "puzzle_csv_snapshot_mutable_until_SHA_seal":True}

def select_all(twic_zip,puzzle_zst,history):
    excluded,receipts=prior_fens(history)
    twic_rows,twic_meta=twic(twic_zip,excluded)
    exclude_puzzle=excluded|{r["fen4"] for r in twic_rows}
    puzzles_rows,puzzle_meta=puzzles(puzzle_zst,exclude_puzzle)
    if len(set(x["fen4"] for x in twic_rows+puzzles_rows))!=32:
        raise ValueError("CROSS_ECOLOGY_32_FEN_OVERLAP")
    return {
        "schema":"c3x022-P2-TWIC1656-plus-Lichess-puzzles-engine-free-16x2-v1",
        "phase":"ENGINE_BLIND_SOURCE_FREEZE_NO_TT_FORECAST_OUTCOME",
        "precommit":P2_PRECOMMIT,
        "historical_exclusions":receipts,
        "historical_fen4_unique":len(excluded),
        "ecologies":{
            "twic":{"source_url":TWIC_URL,"rights":"TWIC personal use only, all rights reserved; original PGN not redistributed",
                    "archive":twic_meta,"selected":twic_rows},
            "lichess_puzzles":{"source_url":PUZZLE_URL,"rights":"Lichess public CC0 source",
                               "archive":puzzle_meta,"selected":puzzles_rows}
        },
        "selected_count":32,
        "engine_calls_during_source_freeze":0,
        "source_frozen_before_any_new_TT_intervention":True
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--twic",required=True)
    a.add_argument("--puzzles",required=True)
    for name in HISTORY:a.add_argument("--"+name,required=True)
    a.add_argument("--out",required=True)
    args=a.parse_args()
    r=select_all(args.twic,args.puzzles,{name:getattr(args,name) for name in HISTORY})
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_P2_TWIC_PUZZLE_SOURCE_32_ENGINE_FREE",
          r["historical_fen4_unique"],
          {n:{"scanned":v["archive"]["scanned"],"eligible":v["archive"]["eligible"]}
           for n,v in r["ecologies"].items()},
          sha(out.read_bytes()),flush=True)
if __name__=="__main__":main()
