import json,sys,hashlib
from pathlib import Path
import chess
def taken(b,m):
 if b.is_en_passant(m):return 1
 t=b.piece_at(m.to_square)
 return {chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9}.get(t.piece_type,0) if t else 0
def exchange(b,first,H):
 side=b.turn;target=first.to_square
 initial=taken(b,first);b.push(first)
 visited=[1]
 def recurse(left):
  if left==0:return 0
  replies=[m for m in b.legal_moves if m.to_square==target and b.is_capture(m)]
  options=[0]
  for m in replies:
   visited[0]+=1
   if visited[0]>20000:raise OverflowError
   piece=taken(b,m);sgn=1 if b.turn==side else -1
   b.push(m);future=recurse(left-1);b.pop()
   options.append(sgn*piece+future)
  return max(options) if b.turn==side else min(options)
 try:
  net=initial+recurse(H-1)
  return {"nominal_material_units":net,"explored_edges":visited[0],"status":"FINITE_LEGAL_EXCHANGE"}
 except OverflowError:return {"status":"UNKNOWN_BUDGET","explored_edges":visited[0]}
data=json.loads(Path(sys.argv[1]).read_text());out=[]
for r in data["records"]:
 b=chess.Board(r["fen"]);m=chess.Move.from_uci(r["move"])
 assert m in b.legal_moves
 scores={str(h):exchange(b.copy(),m,h) for h in (1,2,3,4,5,6)}
 out.append({"event":r["move"],"site":r["site"],"threshold_cp":r["threshold"],"native_SEE_bool":r["original_see"],"event_fen_sha256":hashlib.sha256(r["fen"].encode()).hexdigest(),"full_legal_exchange":scores,"same_game_as_original_root_unproved":True})
Path(sys.argv[2]).write_text(json.dumps({"schema":"c3x027-native-see-board-legal-exchange-profile-v1","interpretation":"nominal capture-only minimax; not Stockfish SEE or exact threshold comparator","records":out},indent=2)+"\n")
for x in out:print("C3X027_EXCHANGE",x["event"],x["threshold_cp"],x["event_fen_sha256"][:12],[(h,v.get("nominal_material_units")) for h,v in x["full_legal_exchange"].items()])
print("C3X027_EXCHANGE_PROFILE_PASS",len(out))
