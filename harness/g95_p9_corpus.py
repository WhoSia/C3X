#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import chess,chess.pgn

STAGE="C3X 0.7.0-G9.5-P9"
PHASES=(
 ("EARLY_OPENING",4,7),
 ("DEVELOPING_OPENING",8,13),
 ("LATE_OPENING",14,21),
 ("EARLY_MIDDLEGAME",22,35),
)
PIECE_VALUE={chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9,chess.KING:0}

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
  if p:
   try:walk_hashes(json.loads(Path(p).read_text()),out)
   except Exception:pass
 return out
def material_balance(b):
 w=sum(PIECE_VALUE[p.piece_type] for p in b.piece_map().values() if p.color==chess.WHITE)
 bl=sum(PIECE_VALUE[p.piece_type] for p in b.piece_map().values() if p.color==chess.BLACK)
 return w-bl
def phase_units(b):
 u=0
 for p in b.piece_map().values():
  if p.piece_type in (chess.KNIGHT,chess.BISHOP):u+=1
  elif p.piece_type==chess.ROOK:u+=2
  elif p.piece_type==chess.QUEEN:u+=4
 return u
def castling_count(b):
 return sum(int(x) for x in (
  b.has_kingside_castling_rights(chess.WHITE),b.has_queenside_castling_rights(chess.WHITE),
  b.has_kingside_castling_rights(chess.BLACK),b.has_queenside_castling_rights(chess.BLACK)))
def eligible(b):
 if not b.is_valid() or b.chess960 or b.is_game_over(claim_draw=False) or b.is_check():return False
 legal=b.legal_moves.count()
 if not (18<=legal<=48):return False
 if abs(material_balance(b))>3:return False
 return True
def audit(b):
 return {"legal_move_count":b.legal_moves.count(),"material_balance_pawns":material_balance(b),
  "nonpawn_phase_units":phase_units(b),"castling_rights_count":castling_count(b)}
def game_candidate(g,source_id,game_index,excluded):
 b=g.board();by={pid:[] for pid,_,_ in PHASES};ply=0
 for m in g.mainline_moves():
  b.push(m);ply+=1
  for pid,lo,hi in PHASES:
   if lo<=ply<=hi and eligible(b):
    fen=canonical_board(b);h=sha(fen)
    if h not in excluded:by[pid].append((h,fen,ply,audit(b)))
 if any(not by[pid] for pid,_,_ in PHASES):return None
 chosen={}
 for pid,_,_ in PHASES:
  h,fen,ply,aud=min(by[pid],key=lambda z:(z[0],z[2]))
  chosen[pid]={"candidate_sha256":h,"fen":fen,"ply":ply,"complexity":aud}
 ids=[chosen[p]["candidate_sha256"] for p,_,_ in PHASES]
 if len(set(ids))!=4:return None
 tid=sha(source_id+"|"+str(game_index)+"|"+"|".join(ids))
 return {"trajectory_hash":tid,"source_id":source_id,"game_index":game_index,"phases":chosen}
def scan_source(path,source_id,excluded,limit=8000):
 out=[];phase_games={pid:0 for pid,_,_ in PHASES};max_ply=0;games=0
 with open(path,errors="strict") as f:
  gi=0
  while gi<limit:
   g=chess.pgn.read_game(f)
   if g is None:break
   games+=1
   b=g.board();ply=0;seen_phase=set()
   for m in g.mainline_moves():
    b.push(m);ply+=1;max_ply=max(max_ply,ply)
    for pid,lo,hi in PHASES:
     if lo<=ply<=hi and eligible(b):seen_phase.add(pid)
   for pid in seen_phase:phase_games[pid]+=1
   cand=game_candidate(g,source_id,gi,excluded)
   if cand:out.append(cand)
   gi+=1
 diag={"source_id":source_id,"games_scanned":games,"max_mainline_ply":max_ply,
  "eligible_games_by_phase":phase_games,"complete_trajectory_candidates":len(out)}
 print("P9_SOURCE_CENSUS",json.dumps(diag,sort_keys=True))
 return sorted(out,key=lambda z:z["trajectory_hash"])
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source",action="append",required=True,help="ID|path|logical")
 ap.add_argument("--exclude",action="append",default=[])
 ap.add_argument("--source-repo",required=True);ap.add_argument("--source-commit",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args();excluded=load_exclusions(a.exclude)
 specs=[]
 for s in a.source:
  z=s.split("|")
  if len(z)!=3:raise SystemExit("P9_SOURCE_SPEC")
  specs.append({"id":z[0],"path":z[1],"logical":z[2]})
 if len(specs)!=3:raise SystemExit("P9_SOURCE_COUNT")
 trajectories=[];pools={}
 used_fens=set()
 for s in specs:
  pool=scan_source(s["path"],s["id"],excluded);pools[s["id"]]=pool
  picked=[]
  for tr in pool:
   hs=[tr["phases"][p]["candidate_sha256"] for p,_,_ in PHASES]
   if any(h in used_fens for h in hs):continue
   picked.append(tr);used_fens.update(hs)
   if len(picked)==2:break
  if len(picked)!=2:raise SystemExit("P9_TRAJECTORY_SHORT_"+s["id"])
  trajectories.extend(picked)
 target_fens={tr["phases"][p]["fen"] for tr in trajectories for p,_,_ in PHASES}
 # deterministic source+phase decoy pools from non-selected trajectories
 decoy_used=set();positions=[]
 for ti,tr in enumerate(sorted(trajectories,key=lambda z:(z["source_id"],z["trajectory_hash"]))):
  trajectory_id=f"p9:traj:{tr['source_id']}:{tr['trajectory_hash'][:12]}"
  for pid,_,_ in PHASES:
   z=tr["phases"][pid];dec=[]
   candidates=[]
   for other in pools[tr["source_id"]]:
    q=other["phases"][pid]
    candidates.append((q["candidate_sha256"],q["fen"]))
   candidates=sorted(set(candidates))
   for h,fen in candidates:
    if fen in target_fens or fen in decoy_used or h in excluded:continue
    decoy_used.add(fen);dec.append({"candidate_sha256":h,"fen":fen})
    if len(dec)==3:break
   if len(dec)!=3:raise SystemExit("P9_DECOY_SHORT_"+tr["source_id"]+"_"+pid)
   pos_id=f"{trajectory_id}:{pid}"
   positions.append({"trajectory_id":trajectory_id,"phase":pid,"source_id":tr["source_id"],
    "source_logical":next(s["logical"] for s in specs if s["id"]==tr["source_id"]),
    "candidate_sha256":z["candidate_sha256"],"position_id":pos_id,"source_ply":z["ply"],"complexity":z["complexity"],
    "cell":{"fen":z["fen"],"history":{"decoys":dec}},"family":"MOVE_ORDER+EVAL","frontier":1})
 if len(positions)!=24 or len({z["candidate_sha256"] for z in positions})!=24:raise SystemExit("P9_POSITION_CARDINALITY")
 out={"schema":"c3x-g95-p9-corpus-v1","scientific_stage":STAGE,
  "source":{"repository":a.source_repo,"commit":a.source_commit,
   "sources":{s["id"]:{"logical":s["logical"],"eligible_trajectories":len(pools[s["id"]])} for s in specs}},
  "selection":{"engine_outcomes_consulted":False,"historical_target_labels_consulted":False,"p8_target_labels_consulted":False,
   "historical_candidate_hashes_excluded":len(excluded),"trajectory_rule":"two lexicographically smallest fresh eligible trajectory hashes per source",
   "phase_position_rule":"minimum SHA256 canonical legal FEN within each frozen ply window",
   "eligibility":"standard chess; nonterminal; not in check; 18-48 legal moves; abs material balance <=3 pawns"},
  "phase_windows":[{"id":p,"ply_lo":lo,"ply_hi":hi} for p,lo,hi in PHASES],
  "trajectories":[{"trajectory_id":f"p9:traj:{tr['source_id']}:{tr['trajectory_hash'][:12]}","source_id":tr["source_id"],
    "trajectory_hash":tr["trajectory_hash"]} for tr in sorted(trajectories,key=lambda z:(z["source_id"],z["trajectory_hash"]))],
  "positions":positions}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P9_CORPUS_PASS","trajectories",len(trajectories),"positions",len(positions),"excluded",len(excluded))
if __name__=="__main__":main()
