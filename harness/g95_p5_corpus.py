#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import chess

STAGE="C3X 0.7.0-G9.5-P5"

def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def walk_hashes(x,out):
 if isinstance(x,dict):
  for k,v in x.items():
   if k=="candidate_sha256" and isinstance(v,str):out.add(v)
   else:walk_hashes(v,out)
 elif isinstance(x,list):
  for v in x:walk_hashes(v,out)

def load_exclusions(paths):
 out=set()
 for p in paths:
  if not p:continue
  walk_hashes(json.loads(Path(p).read_text()),out)
 return out

def rows(path):
 seen=set();out=[]
 for line in Path(path).read_text(errors="strict").splitlines():
  z=line.strip().split()
  if len(z)<4:continue
  fen=" ".join(z[:4])+" 0 1"
  try:
   b=chess.Board(fen)
   if not b.is_valid() or b.chess960:continue
   f=b.fen(en_passant="fen")
  except Exception:continue
  if f in seen:continue
  seen.add(f);out.append((hashlib.sha256(f.encode()).hexdigest(),f))
 return sorted(out)

def parse(s):
 z=s.split("|")
 if len(z)!=4:raise SystemExit("P5_SOURCE_SPEC")
 return {"id":z[0],"path":z[1],"logical":z[2],"n":int(z[3])}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--train",action="append",default=[],required=True)
 ap.add_argument("--select",action="append",default=[],required=True)
 ap.add_argument("--transport",action="append",default=[],required=True)
 ap.add_argument("--exclude",action="append",default=[])
 ap.add_argument("--source-repo",required=True);ap.add_argument("--source-commit",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args()
 specs=[("REPRESENTATION_TRAIN",parse(s)) for s in a.train]+[("SCHEMA_SELECTION",parse(s)) for s in a.select]+[("HELDOUT_TRANSPORT",parse(s)) for s in a.transport]
 excluded=load_exclusions(a.exclude);cache={};meta={}
 for role,s in specs:
  rr=rows(s["path"]);cache[s["id"]]=rr
  meta[s["id"]]={"role":role,"logical":s["logical"],"sha256":sha_file(s["path"]),"legal_unique":len(rr),"positions":s["n"]}
 used=set();targets=[]
 for role,s in specs:
  chosen=[]
  for h,fen in cache[s["id"]]:
   if h in excluded or h in used:continue
   used.add(h);chosen.append((h,fen))
   if len(chosen)==s["n"]:break
  if len(chosen)!=s["n"]:raise SystemExit("P5_CORPUS_SHORT_"+s["id"])
  for h,fen in chosen:
   targets.append({"role":role,"source_stratum":s["id"],"source_logical":s["logical"],"candidate_sha256":h,"fen":fen})
 target_fens={z["fen"] for z in targets};decoy_used=set()
 for t in targets:
  rr=cache[t["source_stratum"]];idx=rr.index((t["candidate_sha256"],t["fen"]));dec=[];j=1
  while len(dec)<3 and j<=len(rr):
   h,f=rr[(idx+j)%len(rr)];j+=1
   if h in excluded or f in target_fens or f in decoy_used:continue
   decoy_used.add(f);dec.append({"candidate_sha256":h,"fen":f})
  if len(dec)!=3:raise SystemExit("P5_DECOY_"+t["source_stratum"])
  t["position_id"]="p5:"+t["source_stratum"]+":"+t["candidate_sha256"][:12]
  t["cell"]={"fen":t["fen"],"history":{"decoys":dec}}
  t["family"]="MOVE_ORDER+EVAL";t["frontier"]=1
  del t["fen"]
 out={"schema":"c3x-g95-p5-corpus-v1","scientific_stage":STAGE,
  "source":{"repository":a.source_repo,"commit":a.source_commit,"regimes":meta},
  "selection":{"engine_outcomes_consulted":False,"historical_target_labels_consulted":False,
   "historical_candidate_hashes_excluded":len(excluded),
   "rule":"within-source unique legal FENs sorted by SHA-256(FEN); fixed role/source quotas; P1-P4 hashes and cross-role duplicates excluded before engine execution"},
  "representation_train_positions":[z for z in targets if z["role"]=="REPRESENTATION_TRAIN"],
  "schema_selection_positions":[z for z in targets if z["role"]=="SCHEMA_SELECTION"],
  "transport_positions":[z for z in targets if z["role"]=="HELDOUT_TRANSPORT"]}
 ids=[]
 for k in ("representation_train_positions","schema_selection_positions","transport_positions"):
  ids += [z["candidate_sha256"] for z in out[k]]
 if len(ids)!=len(set(ids)):raise SystemExit("P5_CROSS_ROLE_DUPLICATE")
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P5_CORPUS_PASS","train",len(out["representation_train_positions"]),"select",len(out["schema_selection_positions"]),"transport",len(out["transport_positions"]),"excluded",len(excluded))

if __name__=="__main__":main()
