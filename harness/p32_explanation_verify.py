#!/usr/bin/env python3
import argparse,hashlib,json,statistics
from collections import Counter,defaultdict
from pathlib import Path
import chess

STAGE="C3X 0.7.0-G9.4-P32"
PIECE={chess.PAWN:"pawn",chess.KNIGHT:"knight",chess.BISHOP:"bishop",chess.ROOK:"rook",chess.QUEEN:"queen",chess.KING:"king"}

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o

def load_pre(p):
 x=json.loads(Path(p).read_text())
 if x.get("schema")!="c3x-p32-precommit-v1" or x.get("event_results_consulted") is not False:raise SystemExit("P32_VERIFY_PRE")
 return x

def collect(path):
 out={}
 for p in Path(path).rglob("*.json"):
  try:x=json.loads(p.read_text())
  except:continue
  if x.get("schema")!="c3x-p32-case-v1":continue
  if x["case_id"] in out:raise SystemExit("P32_VERIFY_DUP")
  out[x["case_id"]]=x
 return out

def material(board):
 d={}
 for color,name in ((chess.WHITE,"white"),(chess.BLACK,"black")):
  d[name]={PIECE[pt]:len(board.pieces(pt,color)) for pt in PIECE}
 return d

def king_dist(board):
 a=board.king(chess.WHITE);b=board.king(chess.BLACK)
 if a is None or b is None:return None
 return max(abs(chess.square_file(a)-chess.square_file(b)),abs(chess.square_rank(a)-chess.square_rank(b)))

def passed_pawn(board,sq,color):
 if board.piece_type_at(sq)!=chess.PAWN:return None
 f=chess.square_file(sq);r=chess.square_rank(sq)
 for ef in range(max(0,f-1),min(7,f+1)+1):
  for er in range(8):
   if color==chess.WHITE and er<=r:continue
   if color==chess.BLACK and er>=r:continue
   es=chess.square(ef,er)
   if board.piece_type_at(es)==chess.PAWN and board.color_at(es)!=color:return False
 return True

def move_atom(fen,uci):
 b=chess.Board(fen);m=chess.Move.from_uci(uci)
 if m not in b.legal_moves:return {"uci":uci,"legal":False}
 piece=b.piece_at(m.from_square);capt=None
 if b.is_capture(m):
  csq=m.to_square
  if b.is_en_passant(m):csq=m.to_square+(-8 if b.turn==chess.WHITE else 8)
  cp=b.piece_at(csq);capt=PIECE.get(cp.piece_type) if cp else "unknown"
 before_mat=material(b);before_legal=b.legal_moves.count();before_check=b.is_check();before_k=king_dist(b)
 san=b.san(m);gives=b.gives_check(m);castle=b.is_castling(m);color=b.turn
 b.push(m)
 after_mat=material(b);after_legal=b.legal_moves.count();after_check=b.is_check();after_k=king_dist(b)
 return {"uci":uci,"legal":True,"san":san,"piece":PIECE.get(piece.piece_type) if piece else None,
  "capture":capt is not None,"captured_piece":capt,"check":bool(gives),"promotion":PIECE.get(m.promotion) if m.promotion else None,
  "castling":bool(castle),"material_before":before_mat,"material_after":after_mat,
  "legal_moves_before":before_legal,"legal_moves_after":after_legal,"side_in_check_before":bool(before_check),"side_in_check_after":bool(after_check),
  "king_distance_before":before_k,"king_distance_after":after_k,
  "king_distance_delta":None if before_k is None or after_k is None else after_k-before_k,
  "moved_pawn_passed_after":passed_pawn(b,m.to_square,color) if piece and piece.piece_type==chess.PAWN else None}

def replay_pv(fen,pv):
 b=chess.Board(fen);moves=(pv or "").split();rows=[]
 for i,u in enumerate(moves):
  try:m=chess.Move.from_uci(u)
  except: return {"tokens":moves,"legal_prefix":len(rows),"complete":False,"failure":{"ply":i,"uci":u,"reason":"PARSE"},"rows":rows}
  if m not in b.legal_moves:return {"tokens":moves,"legal_prefix":len(rows),"complete":False,"failure":{"ply":i,"uci":u,"reason":"ILLEGAL"},"rows":rows}
  rows.append({"ply":i,"uci":u,"san":b.san(m),"check":b.gives_check(m),"capture":b.is_capture(m),"piece":PIECE.get(b.piece_type_at(m.from_square))})
  b.push(m)
 return {"tokens":moves,"legal_prefix":len(rows),"complete":True,"failure":None,"rows":rows}

def divergence(a,b):
 aa=(a or "").split();bb=(b or "").split();n=min(len(aa),len(bb))
 for i in range(n):
  if aa[i]!=bb[i]:return {"ply":i,"base":aa[i],"counterfactual":bb[i],"kind":"MOVE"}
 if len(aa)!=len(bb):return {"ply":n,"base":aa[n] if n<len(aa) else None,"counterfactual":bb[n] if n<len(bb) else None,"kind":"TERMINATION"}
 return None

def cf_semantic(case):
 if case.get("removal",{}).get("status")=="CERTIFIED":return case["removal"]["semantic"],"minimal_removal"
 f=case.get("selected_frontier")
 if f is not None:
  for r in case.get("frontier_ladder",[]):
   if r["frontier"]==f:return r["semantic"],"frontier_null"
 return None,None

def build_ast(case,ground):
 ast=[]
 rem=case.get("removal",{})
 if rem.get("status")=="CERTIFIED":
  ast.append({"type":"EVENT_NECESSITY","set_size":len(rem["address_ids"]),"interaction_only":bool(rem.get("interaction_only")),
              "address_ids":rem["address_ids"]})
  if rem.get("interaction_only"):ast.append({"type":"EVENT_INTERACTION","set_size":len(rem["address_ids"])})
 ret=case.get("retaining",{})
 if ret.get("status")=="CERTIFIED":
  ast.append({"type":"EVENT_SUFFICIENCY","set_size":len(ret["address_ids"]),"address_ids":ret["address_ids"]})
 if ground.get("pv_divergence") is not None:
  ast.append({"type":"PV_DIVERGENCE",**ground["pv_divergence"]})
 b=ground.get("base_move");c=ground.get("counterfactual_move")
 if b and c and b.get("legal") and c.get("legal"):
  keys=["san","piece","capture","captured_piece","check","promotion","castling","legal_moves_after","king_distance_delta"]
  ast.append({"type":"CHESS_ATOMIC_CONTRAST","base":{k:b.get(k) for k in keys},"counterfactual":{k:c.get(k) for k in keys}})
 ast.append({"type":"LIMITATION","text":"Claims are relative to the frozen 1 MiB, single-thread, 80k-node warmed-TT replay and address-trigger semantics; inclusion-minimal does not mean globally minimum-cardinality or unique cause."})
 return ast

def verify_ast(case,ground,ast):
 errors=[]
 for n in ast:
  t=n["type"]
  if t=="EVENT_NECESSITY":
   r=case.get("removal",{})
   if r.get("status")!="CERTIFIED" or n["set_size"]!=len(r.get("address_ids",[])):errors.append("NECESSITY")
   if n.get("interaction_only")!=bool(r.get("interaction_only")):errors.append("INTERACTION_FLAG")
  elif t=="EVENT_INTERACTION":
   r=case.get("removal",{})
   if not (r.get("status")=="CERTIFIED" and r.get("interaction_only") and len(r.get("address_ids",[]))>1):errors.append("INTERACTION")
  elif t=="EVENT_SUFFICIENCY":
   r=case.get("retaining",{})
   if r.get("status")!="CERTIFIED" or n["set_size"]!=len(r.get("address_ids",[])):errors.append("SUFFICIENCY")
  elif t=="PV_DIVERGENCE":
   if ground.get("pv_divergence")!= {k:n[k] for k in ("ply","base","counterfactual","kind")}:errors.append("PV")
  elif t=="CHESS_ATOMIC_CONTRAST":
   if not (ground.get("base_move",{}).get("legal") and ground.get("counterfactual_move",{}).get("legal")):errors.append("CHESS")
  elif t=="LIMITATION":pass
  else:errors.append("UNKNOWN_"+t)
 return {"pass":not errors,"errors":errors}

def render(case,ground,ast):
 s=[]
 s.append(f'{case["engine"]} on {case["candidate_sha256"][:12]} chose {case["baseline"]["bestmove"]} in the frozen native replay.')
 for n in ast:
  if n["type"]=="EVENT_NECESSITY":
   if n["set_size"]==1:s.append("Removing one specifically addressed TT semantic-use event changed the root move.")
   else:s.append(f'Removing an inclusion-minimal set of {n["set_size"]} addressed TT semantic-use events changed the root move.')
  elif n["type"]=="EVENT_INTERACTION":
   s.append("No member of that certified set changed the root move alone, so the event-level dependence is interaction-only under this replay.")
  elif n["type"]=="EVENT_SUFFICIENCY":
   s.append(f'Against the corresponding frontier-null intervention, retaining an inclusion-minimal set of {n["set_size"]} addressed events restored the native root move.')
  elif n["type"]=="PV_DIVERGENCE":
   s.append(f'The certified counterfactual principal variation first diverged at ply {n["ply"]}: {n["base"] or "∅"} versus {n["counterfactual"] or "∅"}.')
  elif n["type"]=="CHESS_ATOMIC_CONTRAST":
   b=n["base"];c=n["counterfactual"]
   s.append(f'The root-move contrast is {b["san"]} versus {c["san"]}; mechanically verified move properties are recorded in the concept certificate rather than expanded into an unverified strategic story.')
  elif n["type"]=="LIMITATION":s.append(n["text"])
 return " ".join(s)

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--precommit",required=True);ap.add_argument("--results",required=True);ap.add_argument("--out",required=True);ap.add_argument("--ast",required=True);ap.add_argument("--grounding",required=True);ap.add_argument("--markdown",required=True);a=ap.parse_args()
 pre=load_pre(a.precommit);by=collect(a.results)
 expected={c["case_id"] for c in pre["cases"]}
 if set(by)!=expected:raise SystemExit(f"P32_VERIFY_CASESET {len(by)}/{len(expected)} missing={sorted(expected-set(by))}")
 certs=[];asts=[];grounds=[];bad=[]
 for c0 in pre["cases"]:
  c=by[c0["case_id"]];fen=c0["cell"]["fen"];cf,cfkind=cf_semantic(c)
  bpv=replay_pv(fen,c["baseline"].get("pv"));cpv=replay_pv(fen,(cf or {}).get("pv")) if cf else None
  bm=move_atom(fen,c["baseline"]["bestmove"]);cm=move_atom(fen,cf["bestmove"]) if cf and cf.get("bestmove") else None
  g={"case_id":c["case_id"],"fen":fen,"counterfactual_kind":cfkind,"base_pv":bpv,"counterfactual_pv":cpv,
     "pv_divergence":divergence(c["baseline"].get("pv"),cf.get("pv")) if cf else None,"base_move":bm,"counterfactual_move":cm}
  ast=build_ast(c,g);vr=verify_ast(c,g,ast);txt=render(c,g,ast)
  if not vr["pass"]:bad.append({"case_id":c["case_id"],"errors":vr["errors"]})
  certs.append({"case":c,"grounding":g,"ast":ast,"verification":vr,"explanation":txt});asts.append({"case_id":c["case_id"],"ast":ast});grounds.append(g)
 status=Counter(c["case"]["status"] for c in certs);primary=[c for c in certs if c["case"]["primary"]]
 rem=sum(c["case"].get("removal",{}).get("status")=="CERTIFIED" for c in primary)
 ret=sum(c["case"].get("retaining",{}).get("status")=="CERTIFIED" for c in primary)
 both=sum(c["case"].get("removal",{}).get("status")=="CERTIFIED" and c["case"].get("retaining",{}).get("status")=="CERTIFIED" for c in primary)
 legal_base=sum(c["grounding"]["base_pv"]["complete"] for c in certs)
 legal_cf=sum(bool(c["grounding"]["counterfactual_pv"] and c["grounding"]["counterfactual_pv"]["complete"]) for c in certs)
 inter=sum(bool(c["case"].get("removal",{}).get("interaction_only")) for c in primary)
 verdict="EVENT_LEVEL_CAUSAL_EXPLANATION_COMPILER_MATERIALIZED"
 if both:verdict+="_WITH_MINIMAL_NECESSITY_AND_SUFFICIENCY"
 elif rem or ret:verdict+="_WITH_PARTIAL_EVENT_CERTIFICATION"
 else:verdict+="_LOCALIZATION_HOLD"
 if bad:verdict="EXPLANATION_VERIFICATION_FAIL"
 out={"schema":"c3x-p32-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],
  "verdict":verdict,"case_status_counts":dict(status),"primary_cases":len(primary),"diagnostic_cases":len(certs)-len(primary),
  "certified":{"minimal_removal":rem,"minimal_retaining":ret,"both":both,"interaction_only_removal_sets":inter},
  "pv_legality":{"base_complete":legal_base,"counterfactual_complete":legal_cf,"cases":len(certs)},
  "explanation_verification":{"passed":len(certs)-len(bad),"failed":len(bad),"errors":bad},
  "certificates":certs,
  "authority_ceiling":"selected P31 root-dependent cases only; 1 MiB/Threads=1/80k measurement; address-trigger event interventions; inclusion-minimal not minimum-cardinality; atomic chess grounding only"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 Path(a.ast).write_text(json.dumps({"schema":"c3x-p32-explanation-ast-v1","items":asts},indent=2,sort_keys=True)+"\n")
 Path(a.grounding).write_text(json.dumps({"schema":"c3x-p32-chess-grounding-v1","items":grounds},indent=2,sort_keys=True)+"\n")
 md=["# P32 Verified Event-Level Chess-Engine Explanations","",f"Verdict: `{verdict}`",""]
 for z in certs:md += [f'## {z["case"]["case_id"]}',z["explanation"],""]
 Path(a.markdown).write_text("\n".join(md)+"\n")
 if bad:raise SystemExit("P32_EXPLANATION_VERIFICATION_FAIL")
 print("P32_ADJ",verdict,"primary",len(primary),"rem",rem,"ret",ret,"both",both,"interaction",inter)

if __name__=="__main__":main()
