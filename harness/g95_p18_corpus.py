#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import chess,chess.pgn

STAGE="C3X 0.7.0-G9.5-P18"
PLY_LO=14;PLY_HI=27;DEV_PER_SOURCE=24;CONF_PER_SOURCE=24;SOURCE_PREFIX=16384
PIECE_VALUE={chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9,chess.KING:0}

def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def file_sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def canonical_board(b):
 f=b.fen(en_passant="fen").split();return " ".join(f[:4])+" 0 1"
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
  try:walk_hashes(json.loads(Path(p).read_text()),out)
  except Exception:pass
 return out
def material_balance(b):
 w=sum(PIECE_VALUE[p.piece_type] for p in b.piece_map().values() if p.color==chess.WHITE)
 q=sum(PIECE_VALUE[p.piece_type] for p in b.piece_map().values() if p.color==chess.BLACK)
 return w-q
def eligible(b):
 return b.is_valid() and not b.chess960 and not b.is_game_over(claim_draw=False) and not b.is_check() and 18<=b.legal_moves.count()<=48 and abs(material_balance(b))<=3
def audit(b):
 return {"legal_move_count":b.legal_moves.count(),"material_balance_pawns":material_balance(b),
  "side_to_move":"WHITE" if b.turn else "BLACK","fullmove_number":b.fullmove_number}
def game_candidate(g,source_id,game_index,excluded):
 b=g.board();xs=[];ply=0
 for m in g.mainline_moves():
  b.push(m);ply+=1
  if not (PLY_LO<=ply<=PLY_HI) or not eligible(b):continue
  fen=canonical_board(b);h=sha(fen)
  if h in excluded:continue
  xs.append((h,fen,ply,audit(b)))
 if not xs:return None
 h,fen,ply,aud=min(xs,key=lambda z:(z[0],z[2]))
 return {"trajectory_hash":sha(f"{source_id}|{game_index}|{h}"),"source_id":source_id,"game_index":game_index,
  "candidate_sha256":h,"fen":fen,"ply":ply,"complexity":aud}
def scan(path,source_id,excluded):
 out=[];games=0
 with open(path,errors="strict") as f:
  for gi in range(SOURCE_PREFIX):
   g=chess.pgn.read_game(f)
   if g is None:break
   games+=1;q=game_candidate(g,source_id,gi,excluded)
   if q:out.append(q)
 print("P18_SOURCE_CENSUS",source_id,games,len(out),flush=True)
 return sorted(out,key=lambda z:(z["trajectory_hash"],z["candidate_sha256"]))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",action="append",required=True)
 ap.add_argument("--exclude",action="append",default=[]);ap.add_argument("--out",required=True)
 a=ap.parse_args();excluded=load_exclusions(a.exclude);specs=[]
 for s in a.source:
  z=s.split("|")
  if len(z)!=4:raise SystemExit("P18_SOURCE_SPEC")
  specs.append({"id":z[0],"path":z[1],"logical":z[2],"compressed_sha256":z[3]})
 if len(specs)!=2:raise SystemExit("P18_SOURCE_COUNT")
 pools={s["id"]:scan(s["path"],s["id"],excluded) for s in specs}
 used=set();picked=[]
 for s in specs:
  zs=[]
  for q in pools[s["id"]]:
   if q["candidate_sha256"] in used:continue
   used.add(q["candidate_sha256"]);zs.append(q)
   if len(zs)==DEV_PER_SOURCE+CONF_PER_SOURCE:break
  if len(zs)!=DEV_PER_SOURCE+CONF_PER_SOURCE:raise SystemExit("P18_SOURCE_SHORT_"+s["id"])
  for i,q in enumerate(zs):q["split"]="development" if i<DEV_PER_SOURCE else "confirmation"
  picked+=zs
 target_fens={z["fen"] for z in picked};decoy_used=set();positions=[]
 for q in sorted(picked,key=lambda z:(z["source_id"],z["split"],z["trajectory_hash"])):
  dec=[]
  for other in pools[q["source_id"]]:
   h,fen=other["candidate_sha256"],other["fen"]
   if fen in target_fens or fen in decoy_used or h in excluded:continue
   decoy_used.add(fen);dec.append({"candidate_sha256":h,"fen":fen})
   if len(dec)==3:break
  if len(dec)!=3:raise SystemExit("P18_DECOY_SHORT_"+q["source_id"])
  logical=next(s["logical"] for s in specs if s["id"]==q["source_id"])
  pid=f"p18:{q['split']}:{q['source_id']}:{q['trajectory_hash'][:12]}"
  positions.append({"position_id":pid,"split":q["split"],"trajectory_id":f"p18:traj:{q['source_id']}:{q['trajectory_hash'][:12]}",
   "source_id":q["source_id"],"source_logical":logical,"source_ply":q["ply"],"candidate_sha256":q["candidate_sha256"],
   "complexity":q["complexity"],"cell":{"fen":q["fen"],"history":{"decoys":dec}},"family":"MOVE_ORDER","frontier":8})
 if len(positions)!=96 or len({z["candidate_sha256"] for z in positions})!=96:raise SystemExit("P18_CARDINALITY")
 if any(len([z for z in positions if z["source_id"]==s["id"] and z["split"]==sp])!=24 for s in specs for sp in ("development","confirmation")):raise SystemExit("P18_SPLIT")
 out={"schema":"c3x-g95-p18-corpus-v1","scientific_stage":STAGE,
  "source":{"sources":{s["id"]:{"logical":s["logical"],"compressed_sha256":s["compressed_sha256"],"decompressed_sha256":file_sha(s["path"]),"eligible_positions":len(pools[s["id"]])} for s in specs}},
  "selection":{"intervention_outcomes_consulted":False,"historical_target_labels_consulted":False,"historical_candidate_hashes_excluded":len(excluded),
   "source_prefix_games":SOURCE_PREFIX,"development_confirmation_disjoint":True,
   "confirmation_hashes_frozen_before_development_ecology_opened":True},
  "positions":positions}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P18_CORPUS_PASS","positions",len(positions),"development",sum(z["split"]=="development" for z in positions),"confirmation",sum(z["split"]=="confirmation" for z in positions),"excluded",len(excluded))
if __name__=="__main__":main()
