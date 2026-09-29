#!/usr/bin/env python3
import argparse,hashlib,itertools,json,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path
import chess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import g95_p13_court as p13
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P15"
ENGINES=("stockfish_19","berserk","ethereal")
BOUND_NAME={1:"UPPER",2:"LOWER"}
PIECE_NAME={chess.KNIGHT:"KNIGHT",chess.BISHOP:"BISHOP",chess.ROOK:"ROOK",chess.QUEEN:"QUEEN"}

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def sem(s):return {k:s.get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}
def pair_id(a,b):return "::".join(sorted((a,b)))
def gap_band(n):return p13.gap_band(abs(int(n)))
def address(e):
 z=dict(e["address"]);z["address_id"]=e["address_id"];return z
def canonical_fen(b):
 f=b.fen(en_passant="fen").split();return " ".join(f[:4])+" 0 1"
def move_squares(uci):
 m=chess.Move.from_uci(uci);return m.from_square,m.to_square
def cheb(a,b):
 return max(abs(chess.square_file(a)-chess.square_file(b)),abs(chess.square_rank(a)-chess.square_rank(b)))
def relvec(b,sq,endpoints):
 aa=b.attacks(sq)
 return [bool(aa & chess.BB_SQUARES[x]) for x in endpoints]
def bitdiff(a,b):return [i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
def edit_id(fr,to):return chess.square_name(fr)+chess.square_name(to)
def apply_edit(b,fr,to):
 q=b.copy(stack=False);piece=q.piece_at(fr)
 q.remove_piece_at(fr);q.set_piece_at(to,piece)
 q.halfmove_clock=0
 return q
def edit_doc(base,fr,to,endpoints,kind):
 piece=base.piece_at(fr);before=relvec(base,fr,endpoints)
 q=apply_edit(base,fr,to);after=relvec(q,to,endpoints);d=bitdiff(before,after)
 ac=sum(i<2 for i in d);bc=sum(i>=2 for i in d)
 attacks_before=set(base.attacks(fr));attacks_after=set(q.attacks(to))
 role=("A_DOMINANT" if ac>bc else "B_DOMINANT" if bc>ac else "BALANCED")
 return {"edit_id":edit_id(fr,to),"kind":kind,"piece_color":"WHITE" if piece.color else "BLACK",
  "piece_type":PIECE_NAME[piece.piece_type],"from":chess.square_name(fr),"to":chess.square_name(to),
  "distance":cheb(fr,to),"relation_before":before,"relation_after":after,"relation_delta_indices":d,
  "a_relation_delta_count":ac,"b_relation_delta_count":bc,"lexical_relation_role":role,
  "legal_move_count_delta":q.legal_moves.count()-base.legal_moves.count(),
  "attack_set_symmetric_difference":len(attacks_before^attacks_after),"fen":canonical_fen(q)}
def generate_edit_pairs(fen,A,B,cfg):
 b=chess.Board(fen);ma=chess.Move.from_uci(A);mb=chess.Move.from_uci(B)
 endpoints=[ma.from_square,ma.to_square,mb.from_square,mb.to_square];blocked=set(endpoints)
 moving_sources={ma.from_square,mb.from_square};targets=[];shams=[]
 for fr,piece in sorted(b.piece_map().items()):
  if fr in moving_sources or piece.piece_type not in PIECE_NAME:continue
  if piece.piece_type==chess.ROOK and bool(b.castling_rights&chess.BB_SQUARES[fr]):continue
  for to in sorted(b.attacks(fr)):
   if to in blocked or b.piece_at(to) is not None:continue
   q=apply_edit(b,fr,to)
   if not q.is_valid() or q.is_game_over(claim_draw=False) or q.is_check():continue
   if chess.Move.from_uci(A) not in q.legal_moves or chess.Move.from_uci(B) not in q.legal_moves:continue
   ld=abs(q.legal_moves.count()-b.legal_moves.count())
   ad=len(set(b.attacks(fr))^set(q.attacks(to)))
   if ld>int(cfg["collateral_budget"]["max_abs_legal_root_move_count_delta"]):continue
   if ad>int(cfg["collateral_budget"]["max_moved_piece_attack_set_symmetric_difference"]):continue
   before=relvec(b,fr,endpoints);after=relvec(q,to,endpoints);d=bitdiff(before,after)
   ac=sum(i<2 for i in d);bc=sum(i>=2 for i in d)
   if d and ac!=bc:targets.append(edit_doc(b,fr,to,endpoints,"TARGET_EDIT"))
   elif not d:shams.append(edit_doc(b,fr,to,endpoints,"SHAM_EDIT"))
 pairs=[]
 for t in targets:
  matches=[s for s in shams if s["from"]==t["from"] and s["piece_type"]==t["piece_type"] and
           s["piece_color"]==t["piece_color"] and s["distance"]==t["distance"]]
  for s in matches:
   pairs.append({"edit_pair_id":t["edit_id"]+"::"+s["edit_id"],"target":t,"sham":s,
    "target_collateral":[abs(t["legal_move_count_delta"]),t["attack_set_symmetric_difference"]],
    "sham_collateral":[abs(s["legal_move_count_delta"]),s["attack_set_symmetric_difference"]]})
 pairs.sort(key=lambda z:(z["target_collateral"],z["sham_collateral"],z["edit_pair_id"]))
 out=[];seen=set()
 for z in pairs:
  k=(z["target"]["edit_id"],z["sham"]["edit_id"])
  if k in seen:continue
  seen.add(k);out.append(z)
  if len(out)>=int(cfg["max_candidate_edit_pairs_before_engine_marginality_checks"]):break
 return out

def select_anchor_targets(events,key_to_move,anchor,maxn):
 rows=[]
 for i,e in enumerate(events):
  if e.get("class")!="MOVE_ORDER_SEED" or e.get("scope")!="MAIN" or int(e.get("ply",-1))!=1:continue
  d=int(e.get("depth",0));b=int(e.get("bound",0))
  if not (5<=d<=8) or b not in (1,2) or int(e.get("tt_move",0))==0:continue
  if key_to_move.get(e.get("key"))!=anchor:continue
  same=[z for z in events[:i] if z.get("key")==e.get("key")]
  if not same or int(same[-1].get("tt_move",0))!=int(e.get("tt_move",0)):continue
  rows.append((e["address_id"],i,e))
 rows.sort(key=lambda z:z[0])
 chosen=[];used=set()
 for z in rows:
  bn=BOUND_NAME[int(z[2]["bound"])]
  if bn in used:continue
  used.add(bn);chosen.append(z)
  if len(chosen)>=maxn:break
 return chosen,len(rows)

def design(a):
 c=load(a.constitution);corp=load(a.corpus);p14c=load(a.p14_closure)
 if c.get("schema")!="c3x-g95-p15-constitution-v1":raise SystemExit("P15_CONSTITUTION")
 if p14c.get("receipt_sha256")!=c["parent"]["closure_receipt_sha256"]:raise SystemExit("P15_PARENT")
 if corp.get("schema")!="c3x-g95-p15-corpus-v1" or corp["selection"]["intervention_outcomes_consulted"] is not False:raise SystemExit("P15_CORPUS")
 builds=Path(a.build_dir);variants={}
 for e in ENGINES:
  fs=list(builds.rglob(f"c3x-p15-{e}"))
  if len(fs)!=1:raise SystemExit(f"P15_BUILD {e} {len(fs)}")
  variants[e]={"sha256":sha_file(fs[0]),"protocol":p32.protocol_for(e)}
 cases=[]
 for pos in corp["positions"]:
  for e in ENGINES:
   cases.append({"case_id":f'p15:{e}:{pos["position_id"]}',"engine":e,"position_id":pos["position_id"],
    "source_id":pos["source_id"],"source_ply":pos["source_ply"],"candidate_sha256":pos["candidate_sha256"],
    "complexity":pos["complexity"],"cell":pos["cell"]})
 if len(cases)!=96:raise SystemExit("P15_CASE_COUNT")
 out={"schema":"c3x-g95-p15-design-precommit-v1","scientific_stage":STAGE,
  "intervention_outcomes_consulted":False,"constitution_sha256":digest(c),"corpus_sha256":digest(corp),
  "parent_p14_receipt_sha256":p14c["receipt_sha256"],"variants":variants,"execution":c["execution"],
  "unordered_pair_constitution":c["unordered_pair_constitution"],"board_intervention_grammar":c["board_intervention_grammar"],
  "board_edit_marginality_freeze":c["board_edit_marginality_freeze"],"exact_event_mediator":c["exact_event_mediator"],
  "factorial":c["factorial"],"operational_mediation":c["operational_mediation"],"support_gate":c["support_gate"],
  "replication_rule":c["replication_rule"],"mechanism_bridge_card":c["mechanism_bridge_card"],
  "claim_ceiling":c["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P15_DESIGN_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def load_design(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p15-design-precommit-v1" or x.get("intervention_outcomes_consulted") is not False:raise SystemExit("P15_DESIGN")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P15_DESIGN_HASH")
 return x

def qualify(a):
 pre=load_design(a.design);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P15_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P15_BINARY")
 ex=pre["execution"];fen=case["cell"]["fen"];board=chess.Board(fen)
 root=Path(a.out).parent/".p15-qual-private";root.mkdir(parents=True,exist_ok=True)
 base=p13.run_context(a.binary,v["protocol"],case["cell"],"CATALOG",None,root/"base")
 legal=sorted(m.uci() for m in board.legal_moves);shallow=[]
 for i,m in enumerate(legal):
  r=p13.run_forced(a.binary,v["protocol"],fen,m,int(ex["shallow_legal_move_nodes"]),root/"shallow",f"{i:02d}")
  s=r["semantic"].get("score")
  shallow.append({"uci":m,"move":p13.move_doc(fen,m),"score":s,"rank_value":p13.rank_value(s)})
 shortlist=sorted(shallow,key=lambda z:(-z["rank_value"],z["uci"]))[:int(ex["shortlist_size"])]
 qshort=[]
 for i,z in enumerate(shortlist):
  vals=[]
  for rep in range(int(ex["isolated_confirm_repeats"])):
   r=p13.run_forced(a.binary,v["protocol"],fen,z["uci"],int(ex["isolated_confirm_nodes"]),root/"confirm",f"{i:02d}-{rep}")
   vals.append(r["semantic"].get("score"))
  cps=[p13.score_cp(s) for s in vals];stable=len(cps)==2 and None not in cps and cps[0]==cps[1]
  qshort.append({"move":z["move"],"shallow_score":z["score"],"confirm_scores":vals,
                 "stable":stable,"confirm_cp":cps[0] if stable else None})
 out={"schema":"c3x-g95-p15-engine-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],
  "engine":case["engine"],"position_id":case["position_id"],"source_id":case["source_id"],"source_ply":case["source_ply"],
  "candidate_sha256":case["candidate_sha256"],"legal_root_move_count":len(legal),"baseline":sem(base["semantic"]),
  "shortlist":qshort,"intervention_outcomes_consulted":False,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P15_QUALIFY",case["case_id"],"stable",sum(z["stable"] for z in qshort),"baseline",out["baseline"]["bestmove"])

def pair_freeze(a):
 pre=load_design(a.design);found={}
 for p in Path(a.qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p15-engine-qualification-v1":found[x["case_id"]]=x
 ids={x["case_id"] for x in pre["cases"]}
 if set(found)!=ids:raise SystemExit(f"P15_QUAL_N {len(found)} expected {len(ids)}")
 bypos=defaultdict(list)
 for c in pre["cases"]:bypos[c["position_id"]].append((c,found[c["case_id"]]))
 frozen_positions={};active_worlds=0
 for pid,rows in sorted(bypos.items()):
  stable={}
  for c,q in rows:stable[c["engine"]]={z["move"]["uci"]:int(z["confirm_cp"]) for z in q["shortlist"] if z["stable"]}
  universe=sorted(set().union(*(set(x) for x in stable.values())));candidates=[]
  for a0,b0 in itertools.combinations(universe,2):
   support=[]
   for c,q in rows:
    e=c["engine"];s=stable[e]
    if a0 not in s or b0 not in s:continue
    gap=abs(s[a0]-s[b0]);bm=q["baseline"].get("bestmove")
    if gap<=int(pre["unordered_pair_constitution"]["near_equal_max_abs_cp"]) and bm in (a0,b0):
     support.append({"engine":e,"gap_cp_abs":gap,"baseline_preferred":bm})
   if len(support)<2:continue
   gaps=[z["gap_cp_abs"] for z in support]
   candidates.append({"pair_id":pair_id(a0,b0),"moves":sorted((a0,b0)),"support":support,
     "support_count":len(support),"median_gap_cp":float(statistics.median(gaps)),"max_gap_cp":max(gaps)})
  candidates.sort(key=lambda z:(-z["support_count"],z["median_gap_cp"],z["max_gap_cp"],z["pair_id"]))
  sel=candidates[0] if candidates else None;c0,q0=rows[0];fen=c0["cell"]["fen"]
  if sel is None:
   frozen_positions[pid]={"position_id":pid,"source_id":c0["source_id"],"source_ply":c0["source_ply"],
    "candidate_sha256":c0["candidate_sha256"],"admitted":False,"pair":None,"geometry":None,"engine_views":{},"board_candidates":[]}
   continue
  A,B=sel["moves"];views={};prefs=[]
  for c,q in rows:
   e=c["engine"];s=stable[e];bm=q["baseline"].get("bestmove");both=A in s and B in s
   signed=None if not both else s[A]-s[B];absgap=None if signed is None else abs(signed)
   active=bool(both and absgap<=int(pre["unordered_pair_constitution"]["near_equal_max_abs_cp"]) and bm in (A,B))
   if active:prefs.append(bm);active_worlds+=1
   views[e]={"active":active,"baseline_bestmove":bm,"baseline_preferred":bm if active else None,
    "A_cp":s.get(A),"B_cp":s.get(B),"signed_A_minus_B_cp":signed,"gap_cp_abs":absgap,
    "gap_band":gap_band(absgap) if active else None}
  geom="SPLIT_ORIENTATION" if len(set(prefs))>=2 else "CONSENSUS_ORIENTATION"
  edits=generate_edit_pairs(fen,A,B,pre["board_intervention_grammar"])
  frozen_positions[pid]={"position_id":pid,"source_id":c0["source_id"],"source_ply":c0["source_ply"],
   "candidate_sha256":c0["candidate_sha256"],"admitted":True,
   "pair":{"pair_id":sel["pair_id"],"A":p13.move_doc(fen,A),"B":p13.move_doc(fen,B),
     "support_count":sel["support_count"],"median_gap_cp":sel["median_gap_cp"],"max_gap_cp":sel["max_gap_cp"]},
   "geometry":geom,"engine_views":views,"board_candidates":edits}
 cases=[]
 for c in pre["cases"]:
  cases.append({**c,"qualification":found[c["case_id"]],"position_pair":frozen_positions[c["position_id"]],
    "engine_view":frozen_positions[c["position_id"]]["engine_views"].get(c["engine"],{})})
 admitted=[z for z in frozen_positions.values() if z["admitted"]]
 out={"schema":"c3x-g95-p15-pair-freeze-v1","scientific_stage":STAGE,"design_receipt_sha256":pre["receipt_sha256"],
  "intervention_outcomes_consulted":False,"admitted_pair_positions":len(admitted),"active_engine_worlds":active_worlds,
  "active_engines":sorted({c["engine"] for c in cases if c["engine_view"].get("active")}),
  "sources":sorted({z["source_id"] for z in admitted}),"geometry_counts":dict(sorted(Counter(z["geometry"] for z in admitted).items())),
  "execution":pre["execution"],"unordered_pair_constitution":pre["unordered_pair_constitution"],
  "board_intervention_grammar":pre["board_intervention_grammar"],"board_edit_marginality_freeze":pre["board_edit_marginality_freeze"],
  "exact_event_mediator":pre["exact_event_mediator"],"factorial":pre["factorial"],
  "operational_mediation":pre["operational_mediation"],"support_gate":pre["support_gate"],
  "replication_rule":pre["replication_rule"],"claim_ceiling":pre["claim_ceiling"],"variants":pre["variants"],
  "positions":frozen_positions,"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P15_PAIR_FREEZE",out["receipt_sha256"],"positions",len(admitted),"active_worlds",active_worlds,
       "board_candidate_positions",sum(bool(z["board_candidates"]) for z in admitted))

def load_pair_freeze(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p15-pair-freeze-v1" or x.get("intervention_outcomes_consulted") is not False:raise SystemExit("P15_PAIR_FREEZE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P15_PAIR_FREEZE_HASH")
 return x

def board_qualify(a):
 pre=load_pair_freeze(a.freeze);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P15_CASE")
 pos=case["position_pair"];view=case["engine_view"];v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P15_BINARY")
 if not pos.get("admitted") or not view.get("active") or not pos.get("board_candidates"):
  out={"schema":"c3x-g95-p15-board-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],
   "engine":case["engine"],"position_id":case["position_id"],"active":False,"candidate_support":[],"search_event_outcomes_consulted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P15_BOARDQUAL_SKIP",case["case_id"]);return
 A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"];ex=pre["execution"];root=Path(a.out).parent/".p15-boardqual-private";root.mkdir(parents=True,exist_ok=True)
 rows=[]
 for i,ep in enumerate(pos["board_candidates"]):
  boards={"TARGET":ep["target"]["fen"],"SHAM":ep["sham"]["fen"]};detail={};ok=True;maxgap=0
  for bn,fen in boards.items():
   vals={}
   for mi,m in enumerate((A,B)):
    scores=[]
    for rep in range(int(ex["board_pair_confirm_repeats"])):
     r=p13.run_forced(a.binary,v["protocol"],fen,m,int(ex["board_pair_confirm_nodes"]),root/f"{i:02d}-{bn}",f"{mi}-{rep}")
     scores.append(r["semantic"].get("score"))
    cps=[p13.score_cp(s) for s in scores];stable=len(cps)==2 and None not in cps and cps[0]==cps[1]
    vals[m]={"scores":scores,"stable":stable,"cp":cps[0] if stable else None}
   gap=None if not all(vals[m]["stable"] for m in (A,B)) else abs(vals[A]["cp"]-vals[B]["cp"])
   legal=A in [x.uci() for x in chess.Board(fen).legal_moves] and B in [x.uci() for x in chess.Board(fen).legal_moves]
   boardok=bool(legal and gap is not None and gap<=int(pre["unordered_pair_constitution"]["near_equal_max_abs_cp"]))
   if not boardok:ok=False
   if gap is not None:maxgap=max(maxgap,gap)
   detail[bn]={"pair":vals,"gap_cp_abs":gap,"supported":boardok}
  rows.append({"edit_pair_id":ep["edit_pair_id"],"supported":ok,"max_gap_cp_abs":maxgap if ok else None,"boards":detail})
 out={"schema":"c3x-g95-p15-board-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],
  "engine":case["engine"],"position_id":case["position_id"],"active":True,"candidate_support":rows,
  "search_event_outcomes_consulted":False,"board_native_root_choice_consulted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P15_BOARDQUAL",case["case_id"],"supported",sum(z["supported"] for z in rows),"/",len(rows))

def board_freeze(a):
 pre=load_pair_freeze(a.freeze);found={}
 for p in Path(a.board_qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p15-board-qualification-v1":found[x["case_id"]]=x
 ids={x["case_id"] for x in pre["cases"]}
 if set(found)!=ids:raise SystemExit(f"P15_BOARDQUAL_N {len(found)} expected {len(ids)}")
 selected={};active_worlds=0
 for pid,pos in sorted(pre["positions"].items()):
  if not pos.get("admitted"):
   selected[pid]={"admitted":False,"reason":"NO_PAIR"};continue
  byid={z["edit_pair_id"]:z for z in pos.get("board_candidates",[])};cands=[]
  for eid,ep in byid.items():
   supporters=[];gaps=[]
   for c in pre["cases"]:
    if c["position_id"]!=pid or not c["engine_view"].get("active"):continue
    q=found[c["case_id"]]
    row=next((z for z in q.get("candidate_support",[]) if z["edit_pair_id"]==eid and z["supported"]),None)
    if row:supporters.append(c["engine"]);gaps.append(row["max_gap_cp_abs"])
   if len(supporters)>=2:
    cands.append({"edit_pair_id":eid,"supporting_engines":sorted(supporters),"support_count":len(supporters),
     "max_gap_cp_abs":max(gaps),"edit_pair":ep})
  cands.sort(key=lambda z:(-z["support_count"],z["max_gap_cp_abs"],z["edit_pair"]["target_collateral"],
    z["edit_pair"]["sham_collateral"],z["edit_pair_id"]))
  if not cands:selected[pid]={"admitted":False,"reason":"NO_CROSS_ENGINE_EDIT_PAIR"};continue
  z=cands[0];active_worlds+=len(z["supporting_engines"])
  selected[pid]={"admitted":True,**z}
 cases=[]
 for c in pre["cases"]:
  s=selected[c["position_id"]];support=bool(s.get("admitted") and c["engine"] in s.get("supporting_engines",[]))
  cases.append({**c,"board_edit_selection":s,"factorial_active":support,
    "board_qualification":found[c["case_id"]]})
 out={"schema":"c3x-g95-p15-board-freeze-v1","scientific_stage":STAGE,
  "pair_freeze_receipt_sha256":pre["receipt_sha256"],"search_event_outcomes_consulted":False,
  "board_native_root_choice_consulted":False,"admitted_pair_positions":pre["admitted_pair_positions"],
  "board_edit_pair_positions":sum(bool(z.get("admitted")) for z in selected.values()),
  "factorial_active_engine_worlds":active_worlds,
  "active_engines":sorted({c["engine"] for c in cases if c["factorial_active"]}),
  "sources":sorted({c["source_id"] for c in cases if c["factorial_active"]}),
  "execution":pre["execution"],"exact_event_mediator":pre["exact_event_mediator"],"factorial":pre["factorial"],
  "operational_mediation":pre["operational_mediation"],"support_gate":pre["support_gate"],
  "replication_rule":pre["replication_rule"],"claim_ceiling":pre["claim_ceiling"],"variants":pre["variants"],
  "positions":pre["positions"],"selected_board_edits":selected,"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P15_BOARD_FREEZE",out["receipt_sha256"],"positions",out["board_edit_pair_positions"],"active_worlds",active_worlds)

def load_board_freeze(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p15-board-freeze-v1" or x.get("search_event_outcomes_consulted") is not False:raise SystemExit("P15_BOARD_FREEZE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P15_BOARD_FREEZE_HASH")
 return x

def relation_role_for_engine(edit,pair,anchor_dispreferred):
 a=edit["a_relation_delta_count"];b=edit["b_relation_delta_count"]
 dom=pair["A"]["uci"] if a>b else pair["B"]["uci"] if b>a else None
 if dom is None:return "BALANCED"
 return "ANCHOR_DISPREFERRED_DOMINANT" if dom==anchor_dispreferred else "ANCHOR_PREFERRED_DOMINANT"

def susceptibility(native_root,t_root,A,B):
 if native_root not in (A,B) or t_root not in (A,B):return "EVENT_THIRD_ESCAPE"
 if t_root==native_root:return "EVENT_NULL"
 return "EVENT_PAIR_REVERSAL"

def run_board_cell(binary,protocol,base_cell,fen,A,B,anchor,root,tag,max_targets):
 cell={"fen":fen,"history":base_cell["history"]}
 native=p13.run_context(binary,protocol,cell,"CATALOG",None,root/f"{tag}-native")
 fp,key_to_move,coll=p13.fingerprint(binary,protocol,fen,[A,B],12000,root/f"{tag}-fp")
 selected,eligible=select_anchor_targets(native["trace"]["events"],key_to_move,anchor,max_targets)
 out={"fen":fen,"native":sem(native["semantic"]),"native_root":p13.move_doc(fen,native["semantic"].get("bestmove")),
  "fingerprint_public_summary":fp,"fingerprint_collision_count":len(coll),"eligible_targets":eligible,
  "bounds":{"UPPER":{"state":"NO_EVENT","record":None},"LOWER":{"state":"NO_EVENT","record":None}},"address_misses":[]}
 for j,(eid,bi,e) in enumerate(selected):
  bn=BOUND_NAME[int(e["bound"])]
  t=p13.run_context(binary,protocol,cell,"REMOVE_SET",[address(e)],root/f"{tag}-t-{j}")
  fired=bool(t["trace"]["targets"] and t["trace"]["targets"][0]["fired"])
  matches=[z for z in t["trace"]["events"] if z["address_id"]==eid]
  if not fired or len(matches)!=1:
   out["address_misses"].append({"bound":bn,"event_prefix":eid[:16],"fired":fired,"trace_matches":len(matches)});continue
  nr=native["semantic"].get("bestmove");tr=t["semantic"].get("bestmove")
  state=susceptibility(nr,tr,A,B)
  out["bounds"][bn]={"state":state,"record":{"target_event_id":eid,"target_event_id_prefix":eid[:16],
    "target_bound":bn,"native_root":p13.move_doc(fen,nr),"t_only_root":p13.move_doc(fen,tr),
    "native":sem(native["semantic"]),"t_only":sem(t["semantic"]),
    "native_pv_san":p13.pv_san(fen,native["semantic"].get("pv")),"t_only_pv_san":p13.pv_san(fen,t["semantic"].get("pv")),
    "first_pv_divergence_ply":p13.pv_div(native["semantic"].get("pv"),t["semantic"].get("pv"))}}
 return out

def factorial_case(a):
 pre=load_board_freeze(a.freeze);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P15_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P15_BINARY")
 if not case.get("factorial_active"):
  out={"schema":"c3x-g95-p15-factorial-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],
   "engine":case["engine"],"position_id":case["position_id"],"source_id":case["source_id"],"active":False,
   "overall_class":"INACTIVE","bridge_records":[],"address_misses":[],"raw_tt_key_emitted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P15_FACTORIAL_SKIP",case["case_id"]);return
 pos=case["position_pair"];sel=case["board_edit_selection"];pair=pos["pair"];A=pair["A"]["uci"];B=pair["B"]["uci"]
 preferred=case["engine_view"]["baseline_preferred"];anchor=B if preferred==A else A
 ep=sel["edit_pair"];root=Path(a.out).parent/".p15-factorial-private";root.mkdir(parents=True,exist_ok=True)
 boards={"B0_ORIGINAL":case["cell"]["fen"],"B1_TARGET":ep["target"]["fen"],"BS_SHAM":ep["sham"]["fen"]}
 results={}
 for tag,fen in boards.items():
  results[tag]=run_board_cell(a.binary,v["protocol"],case["cell"],fen,A,B,anchor,root,tag,int(pre["execution"]["max_semantic_targets_per_board"]))
 if results["B0_ORIGINAL"]["native"].get("bestmove")!=preferred:raise SystemExit("P15_B0_BASELINE_DRIFT")
 misses=[{"board":bn,**m} for bn,z in results.items() for m in z["address_misses"]]
 b0=results["B0_ORIGINAL"];b1=results["B1_TARGET"];bs=results["BS_SHAM"]
 native0=b0["native"].get("bestmove");native1=b1["native"].get("bestmove");natives=bs["native"].get("bestmove")
 board_pair_flip=native0 in (A,B) and native1 in (A,B) and native0!=native1
 sham_pair_flip=native0 in (A,B) and natives in (A,B) and native0!=natives
 relation_role=relation_role_for_engine(ep["target"],pair,anchor)
 bridge_records=[];mod_records=[];common_fired=0
 for bound in ("UPPER","LOWER"):
  r0=b0["bounds"][bound]["record"];r1=b1["bounds"][bound]["record"];rs=bs["bounds"][bound]["record"]
  if r0 and r1:
   common_fired+=1;t0=r0["t_only_root"]["uci"];t1=r1["t_only_root"]["uci"]
   collapse=t0 in (A,B) and t1 in (A,B) and t0==t1
   sham_collapse=False
   if rs and sham_pair_flip:
    ts=rs["t_only_root"]["uci"];sham_collapse=t0 in (A,B) and ts in (A,B) and t0==ts
   if board_pair_flip and collapse and not sham_collapse:
    bridge_records.append({"kind":"FULL_BRIDGE","target_bound":bound,"target_relation_delta_role":relation_role,
      "native_original":native0,"native_target":native1,"t_only_collapse_to":t0,
      "sham_native":natives,"sham_reproduced":False})
   elif b0["bounds"][bound]["state"]!=b1["bounds"][bound]["state"]:
    mod_records.append({"kind":"SUSCEPTIBILITY_MODULATION","target_bound":bound,
      "target_relation_delta_role":relation_role,"original_state":b0["bounds"][bound]["state"],
      "target_state":b1["bounds"][bound]["state"]})
  elif b0["bounds"][bound]["state"]!=b1["bounds"][bound]["state"]:
   mod_records.append({"kind":"SUSCEPTIBILITY_MODULATION","target_bound":bound,
    "target_relation_delta_role":relation_role,"original_state":b0["bounds"][bound]["state"],
    "target_state":b1["bounds"][bound]["state"]})
 if bridge_records:overall="FULL_BRIDGE"
 elif mod_records:overall="SUSCEPTIBILITY_MODULATION"
 elif board_pair_flip:overall="DIRECT_BOARD_ONLY"
 elif any(b0["bounds"][q]["state"]=="EVENT_PAIR_REVERSAL" for q in ("UPPER","LOWER")):overall="SEARCH_ONLY_NO_BOARD_LINK"
 else:overall="NULL"
 card={"position_id":case["position_id"],"source_id":case["source_id"],"engine":case["engine"],
  "pair":pair,"original_fen":boards["B0_ORIGINAL"],"target_edit":ep["target"],"sham_edit":ep["sham"],
  "anchor_preferred":p13.move_doc(boards["B0_ORIGINAL"],preferred),"anchor_dispreferred":p13.move_doc(boards["B0_ORIGINAL"],anchor),
  "relation_delta_role":relation_role,"board_results":results,"overall_class":overall}
 out={"schema":"c3x-g95-p15-factorial-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],
  "engine":case["engine"],"position_id":case["position_id"],"source_id":case["source_id"],"active":True,
  "pair_id":pair["pair_id"],"board_edit_pair_id":sel["edit_pair_id"],"board_pair_flip":board_pair_flip,
  "sham_pair_flip":sham_pair_flip,"common_fired_bounds":common_fired,"overall_class":overall,
  "bridge_records":bridge_records+mod_records,"mechanism_bridge_card":card,"address_misses":misses,
  "raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P15_FACTORIAL",case["case_id"],overall,"bridge",len(bridge_records),"mod",len(mod_records),"miss",len(misses))

def adjudicate(a):
 pre=load_board_freeze(a.freeze);worlds=[]
 for p in Path(a.worlds).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p15-factorial-world-v1":worlds.append(x)
 if len(worlds)!=96:raise SystemExit(f"P15_WORLD_N {len(worlds)}")
 active=[w for w in worlds if w.get("active")];misses=sum(len(w.get("address_misses",[])) for w in worlds)
 engines=sorted({w["engine"] for w in active});sources=sorted({w["source_id"] for w in active})
 fired_worlds=sum(any(q["record"] for br in w["mechanism_bridge_card"]["board_results"].values() for q in br["bounds"].values()) for w in active)
 gate=pre["support_gate"]
 support=(pre["admitted_pair_positions"]>=gate["min_admitted_pair_positions"] and
  pre["board_edit_pair_positions"]>=gate["min_board_edit_pair_positions"] and
  len(active)>=gate["min_factorial_active_engine_worlds"] and len(engines)>=gate["min_active_engines"] and
  len(sources)>=gate["min_sources"] and fired_worlds>=gate["min_worlds_with_any_fired_semantic_target"] and
  misses<=gate["max_address_misses"])
 rows=[]
 for w in active:
  for i,r in enumerate(w["bridge_records"]):
   rows.append({"record_id":f'{w["case_id"]}:{r["kind"]}:{r["target_bound"]}:{i}',"engine":w["engine"],
    "position_id":w["position_id"],"source_id":w["source_id"],"pair_id":w["pair_id"],
    "board_edit_pair_id":w["board_edit_pair_id"],**r})
 full=[r for r in rows if r["kind"]=="FULL_BRIDGE"];mods=[r for r in rows if r["kind"]=="SUSCEPTIBILITY_MODULATION"]
 def replicate(xs,kind,req):
  g=defaultdict(list)
  for r in xs:g[f'{r["target_relation_delta_role"]}|{r["target_bound"]}|{kind}'].append(r)
  out=[]
  for k,v in sorted(g.items()):
   if len(v)>=req["witnesses"] and len({x["engine"] for x in v})>=req["engines"] and len({x["position_id"] for x in v})>=req["positions"] and len({x["source_id"] for x in v})>=req["sources"]:
    out.append({"signature":k,"witnesses":len(v),"engines":sorted({x["engine"] for x in v}),
      "positions":len({x["position_id"] for x in v}),"sources":sorted({x["source_id"] for x in v})})
  return out
 repfull=replicate(full,"FULL_BRIDGE",pre["replication_rule"]["replicated_full_bridge_requires"])
 repmod=replicate(mods,"SUSCEPTIBILITY_MODULATION",pre["replication_rule"]["replicated_susceptibility_requires"])
 cls=Counter(w["overall_class"] for w in active)
 if not support:verdict="P15_FRESH_SUPPORT_HOLD"
 elif repfull:verdict="P15_REPLICATED_CHESS_STRUCTURE_SEARCH_PREFERENCE_FULL_BRIDGE"
 elif repmod:verdict="P15_REPLICATED_CHESS_STRUCTURE_SUSCEPTIBILITY_MODULATION"
 elif full or mods:verdict="P15_LOCAL_CHESS_STRUCTURE_SEARCH_BRIDGE_ONLY"
 elif cls["DIRECT_BOARD_ONLY"]:verdict="P15_BOARD_DIRECT_PREFERENCE_EFFECT_WITHOUT_SEARCH_MEDIATION"
 else:verdict="P15_NO_CHESS_STRUCTURE_SEARCH_BRIDGE_UNDER_FROZEN_GRAMMAR"
 out={"schema":"c3x-g95-p15-adjudication-v1","scientific_stage":STAGE,"status":"CLOSED_PASS" if support else "HOLD",
  "verdict":verdict,"world_count":len(worlds),"support":{"pass":support,
    "admitted_pair_positions":pre["admitted_pair_positions"],"board_edit_pair_positions":pre["board_edit_pair_positions"],
    "factorial_active_engine_worlds":len(active),"active_engines":engines,"sources":sources,
    "worlds_with_any_fired_semantic_target":fired_worlds,"address_misses":misses},
  "overall_class_counts":dict(sorted(cls.items())),"full_bridge_records":len(full),
  "susceptibility_modulation_records":len(mods),"replicated_full_bridge_signatures":repfull,
  "replicated_susceptibility_signatures":repmod,"records":rows,
  "mechanism_bridge_cards":[w["mechanism_bridge_card"] for w in active],
  "claim_ceiling":pre["claim_ceiling"],"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 lines=["# C3X G9.5-P15 — Chess-Structure → Search Pair-Mediation Diagnostic","",
  f"Status: **{out['status']} / {verdict}**",
  f"Pair positions: **{pre['admitted_pair_positions']}/32**; board-edit positions: **{pre['board_edit_pair_positions']}**; active factorial worlds: **{len(active)}**.",
  f"FULL_BRIDGE records: **{len(full)}**; susceptibility-modulation records: **{len(mods)}**; address misses: **{misses}**.","",
  "## Replicated full-bridge signatures"]
 if repfull:
  for z in repfull:lines.append(f"- {z['signature']}: witnesses={z['witnesses']}; engines={','.join(z['engines'])}; positions={z['positions']}; sources={','.join(z['sources'])}.")
 else:lines.append("- None under the frozen rule.")
 lines+=["","## Representative bridge cards"]
 for w in active:
  if w["overall_class"] not in ("FULL_BRIDGE","SUSCEPTIBILITY_MODULATION"):continue
  c=w["mechanism_bridge_card"];lines.append(f"- {w['engine']} / {w['position_id']} / {w['pair_id']}: {w['overall_class']}; edit={c['target_edit']['edit_id']}; sham={c['sham_edit']['edit_id']}; role={c['relation_delta_role']}.")
 lines+=["","P15 uses operational observed board×search interaction/collapse only. It does not claim natural direct/indirect effects, human strategic concepts, objective move truth, or native-address identity."]
 Path(a.markdown).write_text("\n".join(lines)+"\n")
 print("P15_ADJUDICATE",verdict,out["support"],"classes",out["overall_class_counts"])

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("design");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p14-closure",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=design)
 q=sp.add_parser("qualify");q.add_argument("--design",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=qualify)
 q=sp.add_parser("pair-freeze");q.add_argument("--design",required=True);q.add_argument("--qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=pair_freeze)
 q=sp.add_parser("board-qualify");q.add_argument("--freeze",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=board_qualify)
 q=sp.add_parser("board-freeze");q.add_argument("--freeze",required=True);q.add_argument("--board-qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=board_freeze)
 q=sp.add_parser("factorial");q.add_argument("--freeze",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=factorial_case)
 q=sp.add_parser("adjudicate");q.add_argument("--freeze",required=True);q.add_argument("--worlds",required=True);q.add_argument("--out",required=True);q.add_argument("--markdown",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
