#!/usr/bin/env python3
import argparse,hashlib,json,random
from pathlib import Path
import chess,chess.pgn

STAGE="C3X 0.7.0-G9.5-P7"

def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def canonical_board(b):
 f=b.fen(en_passant="fen").split()
 return " ".join(f[:4])+" 0 1"

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
  if p:walk_hashes(json.loads(Path(p).read_text()),out)
 return out

def epd_candidates(path,limit=4096):
 seen=set();xs=[]
 for line in Path(path).read_text(errors="strict").splitlines():
  z=line.strip().split()
  if len(z)<4:continue
  fen=" ".join(z[:4])+" 0 1"
  try:
   b=chess.Board(fen)
   if not b.is_valid() or b.chess960:continue
   fen=canonical_board(b)
  except Exception:continue
  if fen in seen:continue
  seen.add(fen);xs.append((sha(fen),fen))
 return sorted(xs)[:limit]

def pgn_candidates(path,lo,hi,limit=4096):
 seen=set();xs=[]
 with open(path,errors="strict") as f:
  while True:
   g=chess.pgn.read_game(f)
   if g is None:break
   b=g.board()
   ply=0
   for m in g.mainline_moves():
    b.push(m);ply+=1
    if ply<lo or ply>hi:continue
    fen=canonical_board(b)
    if fen in seen:continue
    seen.add(fen);xs.append((sha(fen),fen))
    if len(xs)>=limit*4:break
   if len(xs)>=limit*4:break
 return sorted(xs)[:limit]

def generated_candidates(seed,lo,hi,limit=4096):
 seen=set();xs=[]
 for i in range(limit*3):
  b=chess.Board()
  span=max(1,hi-lo+1)
  target=lo+(int(sha(f"{seed}|len|{i}")[:8],16)%span)
  ok=True
  for ply in range(target):
   moves=list(b.legal_moves)
   if not moves:ok=False;break
   moves.sort(key=lambda m:m.uci())
   j=int(sha(f"{seed}|{i}|{ply}|{canonical_board(b)}")[:16],16)%len(moves)
   b.push(moves[j])
   if b.is_game_over(claim_draw=False) and ply+1<target:ok=False;break
  if not ok or not b.is_valid():continue
  fen=canonical_board(b)
  if fen in seen:continue
  seen.add(fen);xs.append((sha(fen),fen))
  if len(xs)>=limit:break
 return sorted(xs)

def parse_spec(s):
 z=s.split("|")
 if z[1]=="GENERATED_LEGAL":
  return {"id":z[0],"kind":z[1],"seed":z[2],"lo":int(z[3]),"hi":int(z[4]),"n":int(z[5])}
 if z[1]=="PGN":
  return {"id":z[0],"kind":z[1],"path":z[2],"logical":z[3],"lo":int(z[4]),"hi":int(z[5]),"n":int(z[6])}
 return {"id":z[0],"kind":z[1],"path":z[2],"logical":z[3],"n":int(z[4])}

def source_candidates(s):
 if s["kind"]=="EPD":return epd_candidates(s["path"])
 if s["kind"]=="PGN":return pgn_candidates(s["path"],s["lo"],s["hi"])
 return generated_candidates(s["seed"],s["lo"],s["hi"])

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--train",action="append",default=[],required=True)
 ap.add_argument("--select",action="append",default=[],required=True)
 ap.add_argument("--transport",action="append",default=[],required=True)
 ap.add_argument("--exclude",action="append",default=[])
 ap.add_argument("--source-repo",required=True);ap.add_argument("--source-commit",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args()
 specs=[("STRUCTURAL_TRAIN",parse_spec(s)) for s in a.train]+[("STRUCTURAL_SELECTION",parse_spec(s)) for s in a.select]+[("UNTOUCHED_TRANSPORT",parse_spec(s)) for s in a.transport]
 excluded=load_exclusions(a.exclude);cache={};meta={}
 for role,s in specs:
  xs=source_candidates(s);cache[s["id"]]=xs
  meta[s["id"]]={"role":role,"kind":s["kind"],"logical":s.get("logical"),"seed":s.get("seed"),
    "candidate_pool":len(xs),"positions":s["n"],"ply_window":[s.get("lo"),s.get("hi")] if "lo" in s else None}
 used=set();targets=[]
 for role,s in specs:
  chosen=[]
  for h,fen in cache[s["id"]]:
   if h in excluded or h in used:continue
   used.add(h);chosen.append((h,fen))
   if len(chosen)==s["n"]:break
  if len(chosen)!=s["n"]:raise SystemExit("P7_CORPUS_SHORT_"+s["id"])
  for h,fen in chosen:
   targets.append({"role":role,"source_stratum":s["id"],"source_kind":s["kind"],"source_logical":s.get("logical"),
     "candidate_sha256":h,"fen":fen})
 target_fens={z["fen"] for z in targets};decoy_used=set()
 for t in targets:
  xs=cache[t["source_stratum"]];idx=xs.index((t["candidate_sha256"],t["fen"]));dec=[];j=1
  while len(dec)<3 and j<=len(xs):
   h,f=xs[(idx+j)%len(xs)];j+=1
   if h in excluded or f in target_fens or f in decoy_used:continue
   decoy_used.add(f);dec.append({"candidate_sha256":h,"fen":f})
  if len(dec)!=3:raise SystemExit("P7_DECOY_"+t["source_stratum"])
  t["position_id"]="p7:"+t["source_stratum"]+":"+t["candidate_sha256"][:12]
  t["cell"]={"fen":t["fen"],"history":{"decoys":dec}}
  t["family"]="MOVE_ORDER+EVAL";t["frontier"]=1
  del t["fen"]
 out={"schema":"c3x-g95-p7-corpus-v1","scientific_stage":STAGE,
  "source":{"repository":a.source_repo,"commit":a.source_commit,"regimes":meta},
  "selection":{"engine_outcomes_consulted":False,"historical_target_labels_consulted":False,"p6_target_labels_consulted":False,
   "historical_candidate_hashes_excluded":len(excluded),"cross_role_duplicates":0,
   "rule":"source-local deterministic candidate generation; SHA256(FEN) ordering; P1-P6 hash exclusion; cross-role de-duplication before engine execution"},
  "structural_train_positions":[z for z in targets if z["role"]=="STRUCTURAL_TRAIN"],
  "structural_selection_positions":[z for z in targets if z["role"]=="STRUCTURAL_SELECTION"],
  "untouched_transport_positions":[z for z in targets if z["role"]=="UNTOUCHED_TRANSPORT"]}
 ids=[]
 for k in ("structural_train_positions","structural_selection_positions","untouched_transport_positions"):ids += [z["candidate_sha256"] for z in out[k]]
 if len(ids)!=len(set(ids)):raise SystemExit("P7_CROSS_ROLE_DUPLICATE")
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P7_CORPUS_PASS","train",len(out["structural_train_positions"]),"select",len(out["structural_selection_positions"]),"transport",len(out["untouched_transport_positions"]),"excluded",len(excluded))

if __name__=="__main__":main()
