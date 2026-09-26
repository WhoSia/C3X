#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import chess

STAGE="C3X 0.7.0-G9.5-P2"

def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def normalize_epd(path):
 seen=set();rows=[]
 for line in Path(path).read_text(errors="strict").splitlines():
  z=line.strip().split()
  if len(z)<4:continue
  fen=" ".join(z[:4])+" 0 1"
  try:
   b=chess.Board(fen)
   if not b.is_valid():continue
   f=b.fen(en_passant="fen")
  except Exception:continue
  if f in seen:continue
  seen.add(f);rows.append((hashlib.sha256(f.encode()).hexdigest(),f))
 return sorted(rows)

def choose(rows,n,exclude_prefixes):
 avail=[x for x in rows if not any(x[0].startswith(p) for p in exclude_prefixes)]
 if len(avail)<n+3:raise SystemExit("G95_P2_CORPUS_TOO_SMALL")
 targets=avail[:n];target_fens={f for _,f in targets};out=[]
 for i,(h,fen) in enumerate(targets):
  start=rows.index((h,fen));dec=[];j=1
  while len(dec)<3 and j<=len(rows):
   hh,ff=rows[(start+j)%len(rows)];j+=1
   if ff==fen or ff in target_fens:continue
   if ff in [x["fen"] for x in dec]:continue
   dec.append({"candidate_sha256":hh,"fen":ff})
  if len(dec)!=3:raise SystemExit("G95_P2_DECOY")
  out.append({"position_id":"p2:"+h[:12],"candidate_sha256":h,
              "cell":{"fen":fen,"history":{"decoys":dec}},
              "family":"MOVE_ORDER+EVAL","frontier":1})
 return out

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--discovery-epd",required=True);ap.add_argument("--heldout-epd",required=True)
 ap.add_argument("--source-repo",required=True);ap.add_argument("--source-commit",required=True)
 ap.add_argument("--discovery-logical",required=True);ap.add_argument("--heldout-logical",required=True)
 ap.add_argument("--out",required=True);a=ap.parse_args()
 dr=normalize_epd(a.discovery_epd);hr=normalize_epd(a.heldout_epd)
 disc=choose(dr,8,["0020c0362348","0095cdadc5f2"]);hold=choose(hr,8,[])
 if {x["cell"]["fen"] for x in disc}&{x["cell"]["fen"] for x in hold}:raise SystemExit("G95_P2_DISC_HOLD_OVERLAP")
 out={"schema":"c3x-g95-p2-corpus-v1","scientific_stage":STAGE,
      "source":{"repository":a.source_repo,"commit":a.source_commit,
        "discovery":{"logical":a.discovery_logical,"sha256":sha_file(a.discovery_epd),"legal_unique":len(dr)},
        "heldout":{"logical":a.heldout_logical,"sha256":sha_file(a.heldout_epd),"legal_unique":len(hr)}},
      "selection":{"rule":"unique legal FENs sorted by SHA-256(FEN); discovery excludes the two P1 position prefixes; first eight targets; next three hash-ordered non-target FENs as deterministic decoys",
                   "engine_outcomes_consulted":False,"p2_selective_results_consulted":False},
      "discovery_positions":disc,"heldout_positions":hold}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P2_CORPUS_PASS","discovery",*[x["position_id"] for x in disc],"heldout",*[x["position_id"] for x in hold])

if __name__=="__main__":main()
