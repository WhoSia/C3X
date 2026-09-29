#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import chess,chess.pgn

STAGE="C3X 0.7.0-G9.5-P10"
PLY_LO=14;PLY_HI=21
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
  if not p:continue
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
 return 18<=legal<=48 and abs(material_balance(b))<=3
def audit(b):
 return {"legal_move_count":b.legal_moves.count(),"material_balance_pawns":material_balance(b),
  "nonpawn_phase_units":phase_units(b),"castling_rights_count":castling_count(b)}
def game_candidates(g,source_id,game_index,excluded):
 b=g.board();xs=[];ply=0
 for m in g.mainline_moves():
  b.push(m);ply+=1
  if not (PLY_LO<=ply<=PLY_HI) or not eligible(b):continue
  fen=canonical_board(b);h=sha(fen)
  if h in excluded:continue
  xs.append((h,fen,ply,audit(b)))
 if not xs:return []
 # One target-blind position per PGN trajectory.
 h,fen,ply,aud=min(xs,key=lambda z:(z[0],z[2]))
 tid=sha(f"{source_id}|{game_index}|{h}")
 return [{"trajectory_hash":tid,"source_id":source_id,"game_index":game_index,
   "candidate_sha256":h,"fen":fen,"ply":ply,"complexity":aud}]
def scan_source(path,source_id,excluded,limit=1024):
 out=[];games=0;eligible_games=0;max_ply=0
 with open(path,errors="strict") as f:
  for gi in range(limit):
   g=chess.pgn.read_game(f)
   if g is None:break
   games+=1
   try:max_ply=max(max_ply,g.end().ply())
   except Exception:pass
   xs=game_candidates(g,source_id,gi,excluded)
   if xs:eligible_games+=1;out.extend(xs)
 diag={"source_id":source_id,"games_scanned":games,"max_mainline_ply":max_ply,
  "eligible_late_opening_trajectories":eligible_games,"candidate_positions":len(out)}
 print("P10_SOURCE_CENSUS",json.dumps(diag,sort_keys=True))
 return sorted(out,key=lambda z:(z["trajectory_hash"],z["candidate_sha256"]))
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source",action="append",required=True,help="ID|path|logical")
 ap.add_argument("--exclude",action="append",default=[])
 ap.add_argument("--source-repo",required=True);ap.add_argument("--source-commit",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args();excluded=load_exclusions(a.exclude)
 specs=[]
 for s in a.source:
  z=s.split("|")
  if len(z)!=3:raise SystemExit("P10_SOURCE_SPEC")
  specs.append({"id":z[0],"path":z[1],"logical":z[2]})
 if len(specs)!=3:raise SystemExit("P10_SOURCE_COUNT")
 pools={};picked=[];used=set()
 for s in specs:pools[s["id"]]=scan_source(s["path"],s["id"],excluded)
 for s in specs:
  zs=[]
  for q in pools[s["id"]]:
   h=q["candidate_sha256"]
   if h in used:continue
   used.add(h);zs.append(q)
   if len(zs)==3:break
  if len(zs)!=3:raise SystemExit("P10_SOURCE_SHORT_"+s["id"])
  picked.extend(zs)
 target_fens={z["fen"] for z in picked};decoy_used=set();positions=[]
 for q in sorted(picked,key=lambda z:(z["source_id"],z["trajectory_hash"])):
  dec=[]
  for other in pools[q["source_id"]]:
   h,fen=other["candidate_sha256"],other["fen"]
   if fen in target_fens or fen in decoy_used or h in excluded:continue
   decoy_used.add(fen);dec.append({"candidate_sha256":h,"fen":fen})
   if len(dec)==3:break
  if len(dec)!=3:raise SystemExit("P10_DECOY_SHORT_"+q["source_id"])
  logical=next(s["logical"] for s in specs if s["id"]==q["source_id"])
  pos_id=f"p10:{q['source_id']}:{q['trajectory_hash'][:12]}"
  positions.append({"position_id":pos_id,"trajectory_id":f"p10:traj:{q['source_id']}:{q['trajectory_hash'][:12]}",
   "source_id":q["source_id"],"source_logical":logical,"source_ply":q["ply"],"candidate_sha256":q["candidate_sha256"],
   "complexity":q["complexity"],"cell":{"fen":q["fen"],"history":{"decoys":dec}},"family":"MOVE_ORDER","frontier":1})
 if len(positions)!=9 or len({z["candidate_sha256"] for z in positions})!=9:raise SystemExit("P10_POSITION_CARDINALITY")
 out={"schema":"c3x-g95-p10-corpus-v1","scientific_stage":STAGE,
  "source":{"repository":a.source_repo,"commit":a.source_commit,
    "sources":{s["id"]:{"logical":s["logical"],"eligible_positions":len(pools[s["id"]])} for s in specs}},
  "selection":{"engine_outcomes_consulted":False,"historical_target_labels_consulted":False,"p9_target_labels_consulted":False,
    "p9_positive_positions_consulted":False,"historical_candidate_hashes_excluded":len(excluded),
    "source_prefix_games":1024,"position_rule":"three lexicographically smallest fresh trajectory-position hashes per source after historical exclusion",
    "eligibility":"standard chess; nonterminal; not in check; plies 14-21; 18-48 legal moves; abs material balance <=3 pawns"},
  "positions":positions}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\\n")
 print("G95_P10_CORPUS_PASS","positions",len(positions),"excluded",len(excluded))
if __name__=="__main__":main()
