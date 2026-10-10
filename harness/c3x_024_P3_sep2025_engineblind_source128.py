#!/usr/bin/env python3
"""C3X 0.24 P3 independent NEW Sep2025 broadcast 128-game source-only SHA cohort.

No engine import, native execution or treatment labels. User-approved 0.24 P0
precommit sets official source and selection BEFORE archive inspection.
"""
import argparse,hashlib,io,json
from pathlib import Path
import chess
import chess.pgn
import zstandard

URL="https://database.lichess.org/broadcast/lichess_db_broadcast_2025-09.pgn.zst"
CHARTER="c3x/ontology/c3x-024-P3-September2025-fresh128-engineblind-cohort-and-M3v2-prospective-precommit-20261011.md"
SCAN_MAX=20000
FIRST_ELIGIBLE=4096
PICK=128
SCHEMA="c3x024-P3-blind-Sep2025-broadcast128-before-any-native-treatment-v1"

def sha(raw):return hashlib.sha256(raw).hexdigest()

def fens_in_material(data):
    """Extract only literal source FEN4 from already frozen source cohort sets.

    Other unrelated strings are never guessed to be FEN and no low-level
    original game mainlines are reconstructed.
    """
    found=set()
    def visit(v):
        if isinstance(v,dict):
            f=v.get("fen4")
            if isinstance(f,str) and len(f.split())==4:
                found.add(f)
            for key,child in v.items():
                if isinstance(child,(dict,list)) and key not in (
                    "full_original_mainline_uci","source_headers","moves","pgn"):
                    visit(child)
        elif isinstance(v,list):
            for q in v:visit(q)
    visit(data)
    return found

def historic_sources(entries):
    old=set()
    manifest={}
    for spec in entries:
        if "=" not in spec:
            raise ValueError("HISTORY_ARGUMENT_MUST_BE_NAME_EQUALS_PATH")
        name,path=spec.split("=",1)
        if not name or name in manifest:raise ValueError("HISTORY_DUPLICATE_NAME")
        raw=Path(path).read_bytes()
        obj=json.loads(raw)
        rows=fens_in_material(obj)
        if not rows:raise ValueError("HISTORY_HAS_NO_VALID_FEN4_"+name)
        manifest[name]={"source_json_sha256":sha(raw),
                        "fen4_count":len(rows)}
        old.update(rows)
    if len(manifest)<12:
        raise ValueError("HISTORICAL_DISJOINTNESS_SOURCE_COVERAGE_HOLD")
    return old,manifest

def game_digest(headers,uci):
    return sha(json.dumps({"headers":dict(headers),"moves_uci":uci},
             sort_keys=True,ensure_ascii=False,
             separators=(",",":")).encode())

def selected_ply(game_sha):
    if len(game_sha)!=64 or any(c not in "0123456789abcdef" for c in game_sha):
        raise ValueError("INVALID_SOURCE_GAME_SHA")
    return 30+(int(game_sha[:8],16)%15)

def extract(path,prior):
    original=Path(path)
    source_sha=sha(original.read_bytes())
    eligible=[]
    scanned=0
    reject={}
    seen_games=set()
    seen_positions=set()
    def skip(code):reject[code]=reject.get(code,0)+1
    with original.open("rb") as f:
        with zstandard.ZstdDecompressor().stream_reader(f) as stream:
            with io.TextIOWrapper(stream,encoding="utf-8",errors="strict") as reader:
                while scanned<SCAN_MAX and len(eligible)<FIRST_ELIGIBLE:
                    game=chess.pgn.read_game(reader)
                    if game is None:break
                    scanned+=1
                    if game.errors:skip("PGN_PARSE_ERROR");continue
                    if game.headers.get("Variant","Standard") not in ("Standard","Chess"):
                        skip("NON_STANDARD");continue
                    board=game.board()
                    if not board.is_valid():skip("ILLEGAL_INITIAL_BOARD");continue
                    moves=list(game.mainline_moves())
                    if len(moves)<70:skip("SHORT_GAME");continue
                    fingerprint=game_digest(game.headers,[m.uci() for m in moves])
                    if fingerprint in seen_games:skip("DUPLICATE_GAME");continue
                    seen_games.add(fingerprint)
                    at=selected_ply(fingerprint)
                    try:
                        for m in moves[:at]:
                            if m not in board.legal_moves:
                                raise ValueError("PGN_ILLEGAL_PREFIX")
                            board.push(m)
                        played=moves[at]
                        if played not in board.legal_moves:
                            raise ValueError("ILLEGAL_SELECTED_ROOT_MOVE")
                        if played.promotion:skip("PROMOTION");continue
                        legal=board.legal_moves.count()
                        if legal<3:skip("LOW_ROOT_BRANCHING");continue
                        fen4=" ".join(board.fen(en_passant="fen").split()[:4])
                        if fen4 in prior:
                            skip("PRIOR_FEN_OVERLAP");continue
                        if fen4 in seen_positions:
                            skip("INTRA_COHORT_FEN_OVERLAP");continue
                        seen_positions.add(fen4)
                        eligible.append({
                          "id":None,"source_game_sha256":fingerprint,
                          "source_ordinal":scanned,"source_ply_before_original_move":at,
                          "fen4":fen4,"played_legal_move_uci":played.uci(),
                          "native_move":played.from_square*64+played.to_square,
                          "root_legal_move_count":legal,
                          "source_halfmove_clock":board.halfmove_clock,
                          "source_fullmove_number":board.fullmove_number,
                          "engine_outcomes_seen":False
                        })
                    except ValueError:
                        skip("ILLEGAL_PREFIX");continue
    if len(eligible)!=FIRST_ELIGIBLE:
        raise RuntimeError("UNABLE_TO_GET_4096_ELIGIBLE_GAMES__HOLD_"+str(len(eligible)))
    selected=sorted(eligible,key=lambda p:p["source_game_sha256"])[:PICK]
    for idx,row in enumerate(selected,1):row["id"]=idx
    if len({r["fen4"] for r in selected})!=PICK:
        raise ValueError("SOURCE_NONUNIQUE_FINAL_FEN")
    return selected,source_sha,scanned,reject

def produce(zst,history):
    old,historical=historic_sources(history)
    selected,orig,scanned,reject=extract(zst,old)
    return {"schema":SCHEMA,
            "research_version":"C3X 0.24 P3",
            "phase":"SOURCE_ONLY_FROZEN_BEFORE_ENGINE_OR_INTERVENTION",
            "source_archive_url":URL,"source_category":"Lichess broadcast",
            "license":"CC BY-SA 4.0",
            "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
            "change_notice":"Extract 128 source legal root positions and single played source move, remove player headers, original PGN and complete game score",
            "original_compressed_source_sha256":orig,
            "precommit":CHARTER,
            "source_fen_count":PICK,"eligible_before_hash_sort":FIRST_ELIGIBLE,
            "scanned_game_count":scanned,"max_scan":SCAN_MAX,"exclude_counts":reject,
            "historical_source_receipts":historical,
            "prior_unique_fen4_count":len(old),
            "source_only_no_stockfish_used":True,
            "TT_FIRST_interventions":0,"SEE_forced_interventions":0,
            "treatment_outcomes_seen":False,
            "selected":selected,
            "scientific_status":"PRE_TREATMENT_SOURCE_FREEZE_ONLY__NO_M3_PREDICTION_SUCCESS",
            "release_limit":"Derived BY-SA minimal source positions only; no original full PGNs, player data, private TWIC correspondence or modified Stockfish binary"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zst",required=True)
    p.add_argument("--history",action="append",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=produce(a.zst,a.history)
    target=Path(a.out)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X024_P3_ENGINEBLIND_128_SOURCE_SHA_FROZEN",
          result["source_fen_count"],
          result["original_compressed_source_sha256"],
          sha(target.read_bytes()),
          len(result["historical_source_receipts"]),flush=True)
if __name__=="__main__":main()
