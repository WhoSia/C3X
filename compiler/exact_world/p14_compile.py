#!/usr/bin/env python3
import argparse, hashlib, json, math, random, time, urllib.parse, urllib.request
from collections import Counter, defaultdict
from pathlib import Path
import chess

API="https://tablebase.lichess.ovh/standard"
VERSION="c3x-p14-stage-a-v1"

MATERIALS=[
 ("KQBvKR",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.BISHOP),(chess.BLACK,chess.KING),(chess.BLACK,chess.ROOK)]),
 ("KQNvKR",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.KNIGHT),(chess.BLACK,chess.KING),(chess.BLACK,chess.ROOK)]),
 ("KQRvKB",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.ROOK),(chess.BLACK,chess.KING),(chess.BLACK,chess.BISHOP)]),
 ("KQRvKN",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.ROOK),(chess.BLACK,chess.KING),(chess.BLACK,chess.KNIGHT)]),
 ("KRBvKQ",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.BISHOP),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN)]),
 ("KRNvKQ",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.KNIGHT),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN)]),
 ("KBBvKR",[(chess.WHITE,chess.KING),(chess.WHITE,chess.BISHOP),(chess.WHITE,chess.BISHOP),(chess.BLACK,chess.KING),(chess.BLACK,chess.ROOK)]),
 ("KNNvKR",[(chess.WHITE,chess.KING),(chess.WHITE,chess.KNIGHT),(chess.WHITE,chess.KNIGHT),(chess.BLACK,chess.KING),(chess.BLACK,chess.ROOK)]),
]

def sha256_bytes(data): return hashlib.sha256(data).hexdigest()
def canon(obj): return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def state_key(b):
 ep="-" if b.ep_square is None else chess.square_name(b.ep_square)
 return " ".join([b.board_fen(),"w" if b.turn else "b",b.castling_xfen() or "-",ep,str(b.halfmove_clock)])

def candidate(material,pieces,side,index):
 seed=f"{VERSION}|{material}|{'w' if side else 'b'}|{10000+index}"
 rng=random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8],"big"))
 sq=list(chess.SQUARES); rng.shuffle(sq)
 b=chess.Board(None)
 for (color,pt),s in zip(pieces,sq): b.set_piece_at(s,chess.Piece(pt,color))
 b.turn=side; b.castling_rights=chess.BB_EMPTY; b.ep_square=None; b.halfmove_clock=0; b.fullmove_number=1
 if not b.is_valid() or b.is_game_over(claim_draw=False) or b.legal_moves.count()<2: return None
 return b

def query(fen,retries=5):
 url=API+"?"+urllib.parse.urlencode({"fen":fen}); last=None
 for i in range(retries):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"C3X-P14/1.0 fresh-world transport"})
   with urllib.request.urlopen(req,timeout=30) as resp: raw=resp.read()
   return json.loads(raw),sha256_bytes(raw),url
  except Exception as e:
   last=e; time.sleep(.75*(i+1))
 raise RuntimeError(f"tablebase query failed: {last}")

def world_receipt(b):
 obj,raw_sha,url=query(b.fen())
 c2w={"win":2,"draw":0,"loss":-2}
 if obj.get("category") not in c2w: return None
 moves=[]
 for x in obj.get("moves",[]):
  cat=x.get("category"); pd=x.get("precise_dtz")
  if cat not in c2w or pd is None: return None
  sw=c2w[cat]
  moves.append({
   "uci":x["uci"],"mover_wdl":-sw,"successor_category":cat,
   "successor_precise_dtz":int(pd),"mover_precise_dtz":-int(pd),
   "successor_dtz":x.get("dtz"),"successor_dtm":x.get("dtm"),
   "mover_dtm":None if x.get("dtm") is None else -int(x["dtm"]),
   "zeroing":bool(x.get("zeroing",False))
  })
 if len(moves)<2:return None
 vals=[m["mover_wdl"] for m in moves]; best=max(vals)
 if all(v==best for v in vals): return None
 counts=Counter(vals)
 return {
  "provider":"lichess-syzygy-http","endpoint":API,"query_url":url,
  "root_category":obj.get("category"),"root_wdl":c2w[obj["category"]],
  "root_precise_dtz":obj.get("precise_dtz"),"root_dtm":obj.get("dtm"),
  "moves":sorted(moves,key=lambda z:z["uci"]),
  "world_pattern":{str(k):counts[k] for k in sorted(counts)},
  "optimal_count":sum(v==best for v in vals),"strictly_worse_count":sum(v<best for v in vals),
  "raw_response_sha256":raw_sha
 }

def tau4(board,max_paths=350000):
 endpoints=defaultdict(list); path_count=0; excluded=0; overflow=False; root=state_key(board)
 def dfs(b,d,moves,seen):
  nonlocal path_count,excluded,overflow
  if overflow:return
  if d==4:
   path_count+=1
   if path_count>max_paths: overflow=True; return
   key=state_key(b); lh=sha256_bytes(" ".join(sorted(m.uci() for m in b.legal_moves)).encode())
   endpoints[(key,lh)].append(" ".join(moves)); return
  if b.is_game_over(claim_draw=False):return
  for mv in list(b.legal_moves):
   b.push(mv); key=state_key(b)
   if key in seen: excluded+=1; b.pop(); continue
   dfs(b,d+1,moves+[mv.uci()],seen|{key}); b.pop()
   if overflow:return
 dfs(board.copy(stack=False),0,[],{root})
 if overflow:return {"tau4":None,"overflow":True,"enumerated_depth4_paths":path_count,"excluded_history_paths":excluded}
 tau=0; dup=0; witnesses=[]
 for (key,lh),paths in endpoints.items():
  u=sorted(set(paths))
  if len(u)>=2:
   dup+=1; tau+=len(u)-1
   if len(witnesses)<3:witnesses.append({"endpoint_state":key,"legal_move_set_sha256":lh,"paths":u[:4]})
 return {"tau4":tau,"duplicate_endpoint_states":dup,"enumerated_depth4_paths":path_count,"excluded_history_paths":excluded,"overflow":False,"witnesses":witnesses}

def sig(b):
 out=[]
 for color,prefix in [(chess.WHITE,"W"),(chess.BLACK,"B")]:
  c=Counter(p.symbol().upper() for p in b.piece_map().values() if p.color==color)
  out.append(prefix+"".join(p*c[p] for p in "KQRBN" if c[p]))
 return "_".join(out)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); ap.add_argument("--target-count",type=int,default=48); ap.add_argument("--max-generated",type=int,default=640); a=ap.parse_args()
 accepted=[]; audited=0; world_pass=0
 per=max(1,a.max_generated//(len(MATERIALS)*2))
 schedule=[(m,p,s,i) for i in range(per) for m,p in MATERIALS for s in (chess.WHITE,chess.BLACK)][:a.max_generated]
 for m,p,s,i in schedule:
  if len(accepted)>=a.target_count:break
  b=candidate(m,p,s,i)
  if b is None:continue
  audited+=1
  try:w=world_receipt(b)
  except RuntimeError as e:
   print("WORLD_QUERY_RETRY_EXHAUSTED",e,flush=True);continue
  time.sleep(.05)
  if w is None:continue
  world_pass+=1
  t=tau4(b)
  if t["overflow"] or not t["tau4"]:continue
  base={"compiler_version":VERSION,"generation_index":10000+i,"material_seed_name":m,"material_signature":sig(b),"side_to_move":"WHITE" if b.turn else "BLACK","fen":b.fen(),"legal_move_count":b.legal_moves.count(),"world":w,"tau4":t}
  base["candidate_sha256"]=sha256_bytes(canon(base));accepted.append(base)
  print(f"STAGE_A_ACCEPT {len(accepted):02d}/{a.target_count} id={base['candidate_sha256'][:12]} material={base['material_signature']} turn={base['side_to_move']} tau4={t['tau4']}",flush=True)
 if len(accepted)<a.target_count: raise SystemExit(f"WORLD-AUTHORITY-FAIL {len(accepted)}/{a.target_count} audited={audited} world_pass={world_pass}")
 payload={"schema":"c3x-p14-stage-a-pool-v1","scientific_stage":"C3X 0.7.0-G9.4-P14","compiler_version":VERSION,"stockfish_outcomes_consulted":False,
 "freshness":{"p13_material_family_overlap":False,"generation_index_offset":10000},
 "world_authority":{"provider":"Lichess public Syzygy tablebase API","endpoint":API,"robust_categories_only":["win","draw","loss"],"precise_dtz_required_for_every_move":True,"root_halfmove_clock":0,"pawnless":True},
 "audit_counts":{"generated_schedule":len(schedule),"legal_nonterminal_audited":audited,"world_split_pass":world_pass,"stage_a_accepted":len(accepted)},"candidates":accepted}
 payload["pool_sha256"]=sha256_bytes(canon(payload))
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
 print(f"STAGE_A_PASS n={len(accepted)} pool_sha256={payload['pool_sha256']}")
if __name__=="__main__":main()
