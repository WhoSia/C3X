#!/usr/bin/env python3
"""C3X 0.28 engine-blind PGN intake for WSL: no engine calls, no outcome fishing.

Private positions stay in --private-output; public summary contains no FEN,
names or original PGN. A verified prior-cohort canonical-ID manifest is REQUIRED.
"""
import argparse,hashlib,json,sys
from pathlib import Path
try:
 import chess, chess.pgn
except ImportError:
 raise SystemExit("Install python-chess in a local venv before intake")

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--pgn",required=True)
 p.add_argument("--prior-ids",required=True,help="verified list of all historical canonical-game IDs")
 p.add_argument("--prior-complete-attestation",required=True,
                choices=["ALL_018_THROUGH_027_CHECKED"])
 p.add_argument("--source",required=True)
 p.add_argument("--rights",required=True)
 p.add_argument("--seed",default="C3X028_ENGINE_BLIND_V1")
 p.add_argument("--count",type=int,default=64)
 p.add_argument("--private-output",required=True)
 p.add_argument("--public-output",required=True)
 a=p.parse_args()
 if a.count<1 or a.count>512:raise SystemExit("INVALID_TARGET_COUNT")
 raw=Path(a.pgn).read_bytes()
 prior_path=Path(a.prior_ids)
 if not prior_path.is_file():raise SystemExit("HOLD_NO_PRIOR_ID_MANIFEST")
 old=set()
 for ln in prior_path.read_text().splitlines():
  item=ln.strip().lower()
  if not item or item.startswith("#"):continue
  if len(item)!=64 or any(ch not in "0123456789abcdef" for ch in item):
   raise SystemExit("BAD_PRIOR_GAME_HASH")
  old.add(item)
 if not old:raise SystemExit("HOLD_EMPTY_PRIOR_MANIFEST")
 from io import StringIO
 infile=StringIO(raw.decode("utf-8-sig"))
 scanned=legal=duplicate=excluded=0
 candidates={}
 while True:
  game=chess.pgn.read_game(infile)
  if game is None:break
  scanned+=1
  if game.errors:excluded+=1;continue
  try:
   board=game.board()
   moves=list(game.mainline_moves())
   if len(moves)<24:excluded+=1;continue
   # position after fixed 16 legal halfmoves: chosen before any engine is used
   uci=[]
   for mv in moves:
    if mv not in board.legal_moves:raise ValueError("illegal")
    uci.append(mv.uci());board.push(mv)
   board=game.board()
   for mv in moves[:16]:board.push(mv)
   if board.is_game_over():excluded+=1;continue
   canonical=sha((game.board().fen()+"|"+",".join(uci)).encode())
   legal+=1
   if canonical in old or canonical in candidates:duplicate+=1;continue
   candidates[canonical]={"canonical_id":canonical,"fen":board.fen(),
      "source_ply":16,"game_moves":len(moves)}
  except (ValueError,AssertionError):
   excluded+=1
 ordered=sorted(candidates.values(),
   key=lambda x:sha((a.seed+"|"+x["canonical_id"]).encode()))
 chosen=ordered[:a.count]
 if len(chosen)!=a.count:
  raise SystemExit(f"HOLD_INSUFFICIENT_DISJOINT_COHORT_{len(chosen)}_OF_{a.count}")
 pri={"schema":"c3x028-private-engine-blind-cohort-v1",
  "input_pgn_sha256":sha(raw),"prior_manifest_sha256":sha(prior_path.read_bytes()),
  "prior_ids_count":len(old),"seed":a.seed,"source":a.source,
  "rights":a.rights,"selection_rule":"one post-ply16 position per game",
  "positions":chosen}
 out=Path(a.private_output);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(pri,sort_keys=True,indent=2)+"\n")
 public={"schema":"c3x028-engine-blind-intake-summary-v1",
  "input_pgn_sha256":sha(raw),"prior_manifest_sha256":sha(prior_path.read_bytes()),
  "source":a.source,"rights":a.rights,"seed":a.seed,
  "target_count":a.count,"scanned_games":scanned,
  "legal_eligible_games":legal,"duplicate_or_historical":duplicate,
  "invalid_or_too_short":excluded,"independent_candidates":len(candidates),
  "selected":len(chosen),"private_cohort_sha256":sha(out.read_bytes()),
  "engine_calls":0,"no_raw_PGN_FEN_or_names":True,
  "verification_limit":"prior manifest completeness requires independent custody audit"}
 dest=Path(a.public_output);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(public,sort_keys=True,indent=2)+"\n")
 print("C3X028_ENGINE_BLIND_INTAKE_FROZEN",public["private_cohort_sha256"])
if __name__=="__main__":main()
