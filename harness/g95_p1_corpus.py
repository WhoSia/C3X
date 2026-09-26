#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import chess

STAGE="C3X 0.7.0-G9.5-P1"

def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def fen_from_epd(line):
 z=line.strip().split()
 if len(z)<4:return None
 fen=" ".join(z[:4])+" 0 1"
 try:
  b=chess.Board(fen)
  if not b.is_valid():return None
  return b.fen(en_passant="fen")
 except Exception:return None

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--epd",required=True);ap.add_argument("--source-repo",required=True);ap.add_argument("--source-commit",required=True)
 ap.add_argument("--source-path",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 raw=Path(a.epd).read_text(errors="strict").splitlines()
 seen=set();rows=[]
 for line in raw:
  fen=fen_from_epd(line)
  if not fen or fen in seen:continue
  seen.add(fen);rows.append((hashlib.sha256(fen.encode()).hexdigest(),fen))
 rows.sort()
 if len(rows)<8:raise SystemExit("G95_CORPUS_TOO_SMALL")
 pos=[]
 for i in range(2):
  h,fen=rows[i]
  dec=[rows[(i+j)%len(rows)][1] for j in (1,2,3)]
  pos.append({
   "position_id":"fresh:"+h[:12],
   "candidate_sha256":h,
   "cell":{"fen":fen,"history":{"decoys":[{"fen":x} for x in dec]}},
   "family":"MOVE_ORDER+EVAL","frontier":1
  })
 out={
  "schema":"c3x-g95-p1-fresh-corpus-v1","scientific_stage":STAGE,
  "source":{"repository":a.source_repo,"commit":a.source_commit,"path":a.source_path,"sha256":sha_file(a.epd)},
  "selection":{"rule":"unique legal EPD FENs sorted by SHA-256(FEN); first two targets; next three hash-ordered FENs cyclically as decoys","engine_outcomes_consulted":False},
  "legal_unique_positions":len(rows),"positions":pos
 }
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P1_CORPUS_PASS",len(rows),*[x["position_id"] for x in pos])

if __name__=="__main__":main()
