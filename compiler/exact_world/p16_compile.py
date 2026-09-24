#!/usr/bin/env python3
import argparse,hashlib,json,random,time,urllib.parse,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
import chess
API="https://tablebase.lichess.ovh/standard";VERSION="c3x-p16-stage-a-v1";OFFSET=30000
MATERIALS=[
("KBBvKB",[(chess.WHITE,chess.KING),(chess.WHITE,chess.BISHOP),(chess.WHITE,chess.BISHOP),(chess.BLACK,chess.KING),(chess.BLACK,chess.BISHOP)]),
("KBBvKQ",[(chess.WHITE,chess.KING),(chess.WHITE,chess.BISHOP),(chess.WHITE,chess.BISHOP),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN)]),
("KNNvKB",[(chess.WHITE,chess.KING),(chess.WHITE,chess.KNIGHT),(chess.WHITE,chess.KNIGHT),(chess.BLACK,chess.KING),(chess.BLACK,chess.BISHOP)]),
("KNNvKN",[(chess.WHITE,chess.KING),(chess.WHITE,chess.KNIGHT),(chess.WHITE,chess.KNIGHT),(chess.BLACK,chess.KING),(chess.BLACK,chess.KNIGHT)]),
("KNNvKQ",[(chess.WHITE,chess.KING),(chess.WHITE,chess.KNIGHT),(chess.WHITE,chess.KNIGHT),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN)]),
("KRRvKQ",[(chess.WHITE,chess.KING),(chess.WHITE,chess.ROOK),(chess.WHITE,chess.ROOK),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN)]),
("KQBvKQ",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.BISHOP),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN)]),
("KQNvKQ",[(chess.WHITE,chess.KING),(chess.WHITE,chess.QUEEN),(chess.WHITE,chess.KNIGHT),(chess.BLACK,chess.KING),(chess.BLACK,chess.QUEEN)])]
def h(x):return hashlib.sha256(x).hexdigest()
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sk(b):
 ep="-" if b.ep_square is None else chess.square_name(b.ep_square)
 return " ".join([b.board_fen(),"w" if b.turn else "b",b.castling_xfen() or "-",ep,str(b.halfmove_clock)])
def candidate(m,pieces,side,i):
 seed=f"{VERSION}|{m}|{'w' if side else 'b'}|{OFFSET+i}";rng=random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8],"big"));sq=list(chess.SQUARES);rng.shuffle(sq)
 b=chess.Board(None)
 for (c,pt),s in zip(pieces,sq):b.set_piece_at(s,chess.Piece(pt,c))
 b.turn=side;b.castling_rights=chess.BB_EMPTY;b.ep_square=None;b.halfmove_clock=0;b.fullmove_number=1
 return None if (not b.is_valid() or b.is_game_over(claim_draw=False) or b.legal_moves.count()<2) else b
def query(fen,retries=5):
 url=API+"?"+urllib.parse.urlencode({"fen":fen});last=None
 for i in range(retries):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"C3X-P16/1.0 dynamic-phase"})
   with urllib.request.urlopen(req,timeout=30) as r:raw=r.read()
   return json.loads(raw),h(raw),url
  except Exception as e:last=e;time.sleep(.75*(i+1))
 raise RuntimeError(last)
def world(b):
 obj,raw,url=query(b.fen());c={"win":2,"draw":0,"loss":-2}
 if obj.get("category") not in c:return None
 moves=[]
 for x in obj.get("moves",[]):
  cat=x.get("category");pd=x.get("precise_dtz")
  if cat not in c or pd is None:return None
  moves.append({"uci":x["uci"],"mover_wdl":-c[cat],"successor_category":cat,"successor_precise_dtz":int(pd),"mover_precise_dtz":-int(pd),"zeroing":bool(x.get("zeroing",False))})
 if len(moves)<2:return None
 vals=[x["mover_wdl"] for x in moves];best=max(vals)
 if all(v==best for v in vals):return None
 cnt=Counter(vals)
 return {"provider":"lichess-syzygy-http","endpoint":API,"query_url":url,"root_category":obj.get("category"),"root_wdl":c[obj["category"]],"root_precise_dtz":obj.get("precise_dtz"),"moves":sorted(moves,key=lambda z:z["uci"]),"world_pattern":{str(k):cnt[k] for k in sorted(cnt)},"optimal_count":sum(v==best for v in vals),"strictly_worse_count":sum(v<best for v in vals),"raw_response_sha256":raw}
def tau4(board,max_paths=350000):
 ep=defaultdict(list);n=0;exc=0;overflow=False;root=sk(board)
 def dfs(b,d,path,seen):
  nonlocal n,exc,overflow
  if overflow:return
  if d==4:
   n+=1
   if n>max_paths:overflow=True;return
   key=sk(b);lh=h(" ".join(sorted(m.uci() for m in b.legal_moves)).encode());ep[(key,lh)].append(" ".join(path));return
  if b.is_game_over(claim_draw=False):return
  for mv in list(b.legal_moves):
   b.push(mv);key=sk(b)
   if key in seen:exc+=1;b.pop();continue
   dfs(b,d+1,path+[mv.uci()],seen|{key});b.pop()
   if overflow:return
 dfs(board.copy(stack=False),0,[],{root})
 if overflow:return {"tau4":None,"overflow":True,"enumerated_depth4_paths":n,"excluded_history_paths":exc}
 tau=0;dup=0;wit=[]
 for (key,lh),paths in ep.items():
  u=sorted(set(paths))
  if len(u)>=2:
   dup+=1;tau+=len(u)-1
   if len(wit)<3:wit.append({"endpoint_state":key,"legal_move_set_sha256":lh,"paths":u[:4]})
 return {"tau4":tau,"duplicate_endpoint_states":dup,"enumerated_depth4_paths":n,"excluded_history_paths":exc,"overflow":False,"witnesses":wit}
def sig(b):
 out=[]
 for color,prefix in [(chess.WHITE,"W"),(chess.BLACK,"B")]:
  c=Counter(p.symbol().upper() for p in b.piece_map().values() if p.color==color);out.append(prefix+"".join(p*c[p] for p in "KQRBN" if c[p]))
 return "_".join(out)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);ap.add_argument("--target-count",type=int,default=48);ap.add_argument("--max-generated",type=int,default=800);a=ap.parse_args()
 acc=[];aud=wp=0;per=max(1,a.max_generated//(len(MATERIALS)*2));sched=[(m,p,s,i) for i in range(per) for m,p in MATERIALS for s in (chess.WHITE,chess.BLACK)][:a.max_generated]
 for m,p,s,i in sched:
  if len(acc)>=a.target_count:break
  b=candidate(m,p,s,i)
  if b is None:continue
  aud+=1
  try:w=world(b)
  except RuntimeError as e:print("WORLD_QUERY_RETRY_EXHAUSTED",e,flush=True);continue
  time.sleep(.05)
  if w is None:continue
  wp+=1;t=tau4(b)
  if t["overflow"] or not t["tau4"]:continue
  x={"compiler_version":VERSION,"generation_index":OFFSET+i,"material_seed_name":m,"material_signature":sig(b),"side_to_move":"WHITE" if b.turn else "BLACK","fen":b.fen(),"legal_move_count":b.legal_moves.count(),"world":w,"tau4":t};x["candidate_sha256"]=h(canon(x));acc.append(x);print(f"STAGE_A_ACCEPT {len(acc):02d}/{a.target_count} id={x['candidate_sha256'][:12]} material={x['material_signature']} turn={x['side_to_move']} tau4={t['tau4']}",flush=True)
 if len(acc)<a.target_count:raise SystemExit(f"WORLD-AUTHORITY-FAIL {len(acc)}/{a.target_count} audited={aud} world_pass={wp}")
 payload={"schema":"c3x-p16-stage-a-pool-v1","scientific_stage":"C3X 0.7.0-G9.4-P16","compiler_version":VERSION,"stockfish_outcomes_consulted":False,"freshness":{"p13_p14_p15_material_family_overlap":False,"generation_index_offset":OFFSET},"world_authority":{"provider":"Lichess public Syzygy tablebase API","endpoint":API,"robust_categories_only":["win","draw","loss"],"precise_dtz_required_for_every_move":True,"root_halfmove_clock":0,"pawnless":True},"audit_counts":{"generated_schedule":len(sched),"legal_nonterminal_audited":aud,"world_split_pass":wp,"stage_a_accepted":len(acc)},"candidates":acc};payload["pool_sha256"]=h(canon(payload))
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print("STAGE_A_PASS",len(acc),payload["pool_sha256"])
if __name__=="__main__":main()
