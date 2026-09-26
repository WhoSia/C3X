#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import chess

STAGE="C3X 0.7.0-G9.5-P3"

def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def rows(path):
 seen=set();out=[]
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
  seen.add(f);out.append((hashlib.sha256(f.encode()).hexdigest(),f))
 return sorted(out)

def select(rs,n,excluded):
 avail=[z for z in rs if z[0] not in excluded and not any(z[0].startswith(p) for p in ("0020c0362348","0095cdadc5f2"))]
 if len(avail)<n+3:raise SystemExit("P3_CORPUS_TOO_SMALL")
 targets=avail[:n];tf={f for _,f in targets};out=[]
 for h,fen in targets:
  start=rs.index((h,fen));dec=[];j=1
  while len(dec)<3 and j<=len(rs):
   hh,ff=rs[(start+j)%len(rs)];j+=1
   if ff==fen or ff in tf or hh in excluded or any(x["fen"]==ff for x in dec):continue
   dec.append({"candidate_sha256":hh,"fen":ff})
  if len(dec)!=3:raise SystemExit("P3_DECOY")
  out.append({"position_id":"p3:"+h[:12],"candidate_sha256":h,"cell":{"fen":fen,"history":{"decoys":dec}},"family":"MOVE_ORDER+EVAL","frontier":1})
 return out

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--discovery-epd",required=True);ap.add_argument("--heldout-epd",required=True);ap.add_argument("--p2-precommit",required=True)
 ap.add_argument("--source-repo",required=True);ap.add_argument("--source-commit",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args()
 p2=json.loads(Path(a.p2_precommit).read_text())
 if p2.get("schema")!="c3x-g95-p2-precommit-v1":raise SystemExit("P3_P2_PRE")
 excluded={c["candidate_sha256"] for c in p2["cases"]}
 dr,hr=rows(a.discovery_epd),rows(a.heldout_epd)
 disc=select(dr,8,excluded);excluded2=excluded|{x["candidate_sha256"] for x in disc}
 hold=select(hr,8,excluded2)
 if {x["cell"]["fen"] for x in disc}&{x["cell"]["fen"] for x in hold}:raise SystemExit("P3_DISC_HOLD_OVERLAP")
 out={"schema":"c3x-g95-p3-corpus-v1","scientific_stage":STAGE,
  "source":{"repository":a.source_repo,"commit":a.source_commit,
   "discovery":{"logical":"6mvs_+90_+99.epd","sha256":sha_file(a.discovery_epd),"legal_unique":len(dr)},
   "heldout":{"logical":"8mvs_big_+80_+109.epd","sha256":sha_file(a.heldout_epd),"legal_unique":len(hr)}},
  "selection":{"rule":"unique legal FENs sorted by SHA-256(FEN), exclude all P2 position hashes and P1 prefixes, first eight remaining targets, three hash-ordered non-target decoys","engine_outcomes_consulted":False,"p3_selective_results_consulted":False},
  "discovery_positions":disc,"heldout_positions":hold}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P3_CORPUS_PASS","disc",*[x["position_id"] for x in disc],"hold",*[x["position_id"] for x in hold])

if __name__=="__main__":main()
