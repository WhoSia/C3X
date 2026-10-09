#!/usr/bin/env python3
"""C3X018 blind independent 2025-11 Lichess broadcast PGN source cohort.

Run once before any SF16 search outcomes, then commit the resulting manifest
unchanged. Candidate ranking is game hash only, not engine evaluation.
"""
import argparse,hashlib,io,json,sys
from pathlib import Path
import chess,chess.pgn,zstandard

SOURCE="https://database.lichess.org/broadcast/lichess_db_broadcast_2025-11.pgn.zst"
N_ELIGIBLE=512
N_SELECT=12
MAX_SCANNED=20000

def digest(b):return hashlib.sha256(b).hexdigest()
def fail(label):raise RuntimeError("C3X018_BLIND_SOURCE_"+label)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--zst",required=True)
 p.add_argument("--prior",required=True)
 p.add_argument("--october",required=True)
 p.add_argument("--out",required=True)
 a=p.parse_args()
 old=json.loads(Path(a.prior).read_text())
 historic={q["fen4"] for q in old["selected"]}
 october=json.loads(Path(a.october).read_text())
 historic.update(x["fen4"] for x in october["selected"])
 compressed=Path(a.zst)
 archive_sha=digest(compressed.read_bytes())
 eligible=[]
 exclusions={}
 distinct_games=set()
 distinct_fens=set()
 seen=0
 with compressed.open("rb") as raw:
  with zstandard.ZstdDecompressor().stream_reader(raw) as stream:
   with io.TextIOWrapper(stream,encoding="utf-8",errors="strict") as fp:
    while seen<MAX_SCANNED and len(eligible)<N_ELIGIBLE:
     game=chess.pgn.read_game(fp)
     if game is None:break
     seen+=1
     def excluded(label):
      exclusions[label]=exclusions.get(label,0)+1
     if game.errors:
      excluded("PGN_PARSE_ERROR")
      continue
     if game.headers.get("Variant","Standard") not in ("Standard","Chess"):
      excluded("NONSTANDARD_VARIANT");continue
     board=game.board()
     if not board.is_valid():
      excluded("INVALID_INITIAL_BOARD");continue
     moves=list(game.mainline_moves())
     if len(moves)<70:
      excluded("SHORT_GAME");continue
     history=[m.uci() for m in moves]
     fingerprint_obj={"headers":dict(game.headers),"moves_uci":history}
     fingerprint=digest(json.dumps(fingerprint_obj,sort_keys=True,
                                  ensure_ascii=False,separators=(",",":")).encode("utf-8"))
     if fingerprint in distinct_games:
      excluded("DUPLICATE_GAME");continue
     distinct_games.add(fingerprint)
     at=30+(int(fingerprint[:8],16)%15)
     try:
      for m in moves[:at]:
       if m not in board.legal_moves:fail("ILLEGAL_MAINLINE")
       board.push(m)
      played=moves[at]
      if played not in board.legal_moves:
       excluded("ILLEGAL_SELECTED_MOVE");continue
      if played.promotion:
       excluded("PROMOTION_MOVE");continue
      if board.legal_moves.count()<3:
       excluded("FEWER_THAN_THREE_ROOT_MOVES");continue
      fen4=" ".join(board.fen(en_passant="fen").split()[:4])
      if fen4 in historic or fen4 in distinct_fens:
       excluded("DUPLICATE_OR_PRIOR_FEN");continue
      distinct_fens.add(fen4)
      eligible.append({
        "source_game_sha256":fingerprint,
        "source_ordinal":seen,
        "id":None,
        "game_url":game.headers.get("GameURL") or game.headers.get("Site",""),
        "source_headers":dict(game.headers),
        "full_original_mainline_uci":history,
        "original_mainline_halfmoves":len(history),
        "source_ply_before_original_move":at,
        "fen4":fen4,
        "played_legal_move_uci":played.uci(),
        "native_move":played.from_square*64+played.to_square,
        "source_root_legal_count":board.legal_moves.count()
      })
     except ValueError:
      excluded("INVALID_GAME_MOVE");continue
 if len(eligible)!=N_ELIGIBLE:fail("ELIGIBLE_512_NOT_FOUND_"+str(len(eligible)))
 eligible.sort(key=lambda x:x["source_game_sha256"])
 selected=eligible[:N_SELECT]
 if len({x["source_game_sha256"] for x in selected})!=N_SELECT:fail("NOT_UNIQUE")
 for i,row in enumerate(selected,1):row["id"]=i
 obj={
  "schema":"c3x018-blind-16-2025oct-broadcast-original-game-histories-v1",
  "selection_preregistration":"c3x/ontology/c3x-018-independent-2025-broadcast-value-mediation-preregistered-court.md",
  "source_url":SOURCE,"source_license":"Lichess broadcast PGN CC BY-SA 4.0",
  "compressed_source_sha256":archive_sha,
  "selection":"First 512 eligible standard games >=70 plies, SHA-sort, first 16, before move at ply 30+(first8_SHA_hex mod15); no SF16 evaluations",
  "scanned_games":seen,"eligible_games":len(eligible),
  "excluded_counts":exclusions,
  "previous_12_and_october16_FEN_overlap":0,
  "unique_original_game_histories":12,
  "original_move_histories_present":True,
  "selected":selected,
  "limits":["Games sampled from one broadcast month (shared ecology possible)",
            "Original PGN moves retained; native engine tests use standalone FEN4 and reset clock",
            "No outcomes viewed while choosing records",
            "Source headers and UCI mainlines are derived factual game records; attribute Lichess"]
 }
 path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
 print("C3X018_NOVEMBER_BLIND_SOURCE_COHORT_SEALED",
       len(selected),archive_sha,hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
