#!/usr/bin/env python3
"""M6-S source-only independent July2026 broadcast 64, engine blind.
Frozen choice before opening July archive, using prior source-only selector.
"""
import sys,hashlib,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c3x_024_P3_sep2025_engineblind_source128 as frozen
frozen.URL="https://database.lichess.org/broadcast/lichess_db_broadcast_2026-07.pgn.zst"
frozen.CHARTER="c3x/ontology/c3x-025-P14-P3-M6-July2026-selective-invariance-preregister-20261012.md"
frozen.SCAN_MAX=16000
frozen.FIRST_ELIGIBLE=2048
frozen.PICK=64
frozen.SCHEMA="c3x025-M6-S-july2026-source-only-independent-64-v1"
def traverse(obj):
 if isinstance(obj,dict):
  v=obj.get("source_game_sha256")
  if isinstance(v,str) and len(v)==64:yield v
  for child in obj.values():yield from traverse(child)
 elif isinstance(obj,list):
  for child in obj:yield from traverse(child)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--zst",required=True)
 ap.add_argument("--history",action="append",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 cohort=frozen.produce(a.zst,a.history)
 prior_game=set();prior_exposed=0
 for spec in a.history:
  name,path=spec.split("=",1)
  old=json.loads(Path(path).read_bytes())
  hashes=set(traverse(old))
  prior_game.update(hashes)
  if name=="june2026":
   if len(old["selected"])!=32 or len(hashes)!=32:raise ValueError("M6_JUNE32_FULL_GAME_IDENTITIES_MISSING")
   prior_exposed=len(hashes)
 selected={r["source_game_sha256"] for r in cohort["selected"]}
 if selected & prior_game:raise ValueError("M6_HISTORIC_FULL_GAME_DUPLICATE_HOLD")
 if len(cohort["historical_source_receipts"])!=15 or prior_exposed!=32:
  raise ValueError("M6_HISTORY_15_INCLUDING_REAL_JUNE_M5_REQUIRED")
 cohort["prior_full_game_sha256_count"]=len(prior_game)
 cohort["overlap_prior_full_game_SHA256_count"]=0
 cohort["M5_June2026_32game_historical_manifest_SHA256"]="71ab8e4c4ddb52d8f63e6e51ea6b4cf991e135246773460c3d6f4800288521be"
 cohort["release_limit"]="Official Lichess broadcast July2026 CC BY-SA 4.0, only minimally derived legal FEN4/game hashes and single played move; full original PGN/player metadata not distributed."
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(cohort,sort_keys=True,indent=2)+"\n")
 print("C3X025_M6_S_JULY_SOURCE_ONLY_64",cohort["source_fen_count"],
       cohort["original_compressed_source_sha256"],
       hashlib.sha256(out.read_bytes()).hexdigest(),
       "historic_fen",cohort["prior_unique_fen4_count"],
       "historic_games",len(prior_game),flush=True)
if __name__=="__main__":main()
