#!/usr/bin/env python3
import argparse,hashlib,itertools,json,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path
import chess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import g95_p13_court as p13
import g95_p15_court as p15
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P16"
ENGINES=("stockfish_19","berserk","ethereal")
PIECE_NAME={chess.KNIGHT:"KNIGHT",chess.BISHOP:"BISHOP",chess.ROOK:"ROOK",chess.QUEEN:"QUEEN"}
ATOM_BASE=("A_FROM","A_TO","B_FROM","B_TO")

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def canonical_fen(b):
 f=b.fen(en_passant="fen").split();return " ".join(f[:4])+" 0 1"
def pair_id(a,b):return "::".join(sorted((a,b)))
def gap_band(n):return p13.gap_band(abs(int(n)))
def cheb(a,b):return max(abs(chess.square_file(a)-chess.square_file(b)),abs(chess.square_rank(a)-chess.square_rank(b)))
def apply_edit(b,fr,to):
 q=b.copy(stack=False);piece=q.piece_at(fr);q.remove_piece_at(fr);q.set_piece_at(to,piece);q.halfmove_clock=0;return q
def relvec(b,sq,endpoints):
 aa=b.attacks(sq);return [bool(aa&chess.BB_SQUARES[x]) for x in endpoints]
def atoms(before,after):
 out=[]
 for i,(x,y) in enumerate(zip(before,after)):
  if x==y:continue
  out.append(ATOM_BASE[i]+("_GAIN" if (not x and y) else "_LOSS"))
 return sorted(out)
def edit_id(fr,to):return chess.square_name(fr)+chess.square_name(to)

def edit_doc(base,fr,to,endpoints):
 piece=base.piece_at(fr);q=apply_edit(base,fr,to)
 before=relvec(base,fr,endpoints);after=relvec(q,to,endpoints);ats=atoms(before,after)
 return {"edit_id":edit_id(fr,to),"piece_color":"WHITE" if piece.color else "BLACK",
  "piece_type":PIECE_NAME[piece.piece_type],"from":chess.square_name(fr),"to":chess.square_name(to),
  "distance":cheb(fr,to),"relation_before":before,"relation_after":after,"atoms":ats,
  "legal_move_count_delta":q.legal_moves.count()-base.legal_moves.count(),
  "attack_set_symmetric_difference":len(set(base.attacks(fr))^set(q.attacks(to))),
  "fen":canonical_fen(q)}

def lexical_asym(ats):
 a=sum(x.startswith("A_") for x in ats);b=sum(x.startswith("B_") for x in ats);return a!=b

def generate_chains(fen,A,B,cfg):
 b=chess.Board(fen);ma=chess.Move.from_uci(A);mb=chess.Move.from_uci(B)
 endpoints=[ma.from_square,ma.to_square,mb.from_square,mb.to_square];blocked=set(endpoints);moving={ma.from_square,mb.from_square}
 edits=[]
 for fr,piece in sorted(b.piece_map().items()):
  if fr in moving or piece.piece_type not in PIECE_NAME:continue
  if piece.piece_type==chess.ROOK and bool(b.castling_rights&chess.BB_SQUARES[fr]):continue
  for to in sorted(b.attacks(fr)):
   if to in blocked or b.piece_at(to) is not None:continue
   q=apply_edit(b,fr,to)
   if not q.is_valid() or q.is_game_over(claim_draw=False) or q.is_check():continue
   legal={m.uci() for m in q.legal_moves}
   if A not in legal or B not in legal:continue
   ld=abs(q.legal_moves.count()-b.legal_moves.count())
   ad=len(set(b.attacks(fr))^set(q.attacks(to)))
   if ld>int(cfg["max_abs_legal_root_move_count_delta"]) or ad>int(cfg["max_moved_piece_attack_set_symmetric_difference"]):continue
   edits.append(edit_doc(b,fr,to,endpoints))
 groups=defaultdict(list)
 for e in edits:groups[(e["from"],e["piece_color"],e["piece_type"],e["distance"])].append(e)
 chains=[]
 for key,rows in sorted(groups.items()):
  shams=[x for x in rows if not x["atoms"]]
  if not shams:continue
  sham=sorted(shams,key=lambda x:(abs(x["legal_move_count_delta"]),x["attack_set_symmetric_difference"],x["edit_id"]))[0]
  targets=[x for x in rows if x["atoms"] and lexical_asym(x["atoms"])]
  for t in targets:
   S=set(t["atoms"])
   if len(S)==1:
    chains.append({"chain_id":t["edit_id"]+"::SHAM::"+sham["edit_id"],"chain_type":"ATOMIC_CHAIN",
      "target":t,"subset":sham,"sham":sham,"target_atom_count":1,"subset_atom_count":0})
    continue
   subs=[x for x in rows if x["atoms"] and set(x["atoms"])<S]
   if not subs:continue
   subs.sort(key=lambda x:(0 if len(S)-len(x["atoms"])==1 else 1,-len(x["atoms"]),
     abs(x["legal_move_count_delta"]),x["attack_set_symmetric_difference"],x["edit_id"]))
   s=subs[0]
   chains.append({"chain_id":t["edit_id"]+"::"+s["edit_id"]+"::"+sham["edit_id"],"chain_type":"COMPOSITE_DELETION_CHAIN",
    "target":t,"subset":s,"sham":sham,"target_atom_count":len(S),"subset_atom_count":len(s["atoms"])})
 chains.sort(key=lambda z:(0 if z["chain_type"]=="COMPOSITE_DELETION_CHAIN" else 1,z["target_atom_count"],
  abs(z["target"]["legal_move_count_delta"])+abs(z["subset"]["legal_move_count_delta"])+abs(z["sham"]["legal_move_count_delta"]),
  z["target"]["attack_set_symmetric_difference"]+z["subset"]["attack_set_symmetric_difference"]+z["sham"]["attack_set_symmetric_difference"],z["chain_id"]))
 return chains[:int(cfg["max_chain_candidates_per_position"])]

def engine_atoms(lex_atoms,A,preferred):
 amap={"A":"PREFERRED" if A==preferred else "DISPREFERRED","B":"DISPREFERRED" if A==preferred else "PREFERRED"}
 return sorted(amap[x[0]]+x[1:] for x in lex_atoms)

def dominance(eatoms):
 p=sum(x.startswith("PREFERRED_") for x in eatoms);d=sum(x.startswith("DISPREFERRED_") for x in eatoms)
 return "PREFERRED_DOMINANT" if p>d else "DISPREFERRED_DOMINANT" if d>p else "BALANCED"

def design(a):
 c=load(a.constitution);corp=load(a.corpus);parent=load(a.p15_closure)
 if c.get("schema")!="c3x-g95-p16-constitution-v1":raise SystemExit("P16_CONSTITUTION")
 if parent.get("receipt_sha256")!=c["parent"]["closure_receipt_sha256"]:raise SystemExit("P16_PARENT")
 if corp.get("schema")!="c3x-g95-p16-corpus-v1" or corp["selection"]["intervention_outcomes_consulted"] is not False:raise SystemExit("P16_CORPUS")
 builds=Path(a.build_dir);variants={}
 for e in ENGINES:
  fs=list(builds.rglob(f"c3x-p16-{e}"))
  if len(fs)!=1:raise SystemExit(f"P16_BUILD {e} {len(fs)}")
  variants[e]={"sha256":sha_file(fs[0]),"protocol":p32.protocol_for(e)}
 cases=[]
 for pos in corp["positions"]:
  for e in ENGINES:
   cases.append({"case_id":f'p16:{e}:{pos["position_id"]}',"engine":e,"position_id":pos["position_id"],
    "source_id":pos["source_id"],"source_ply":pos["source_ply"],"candidate_sha256":pos["candidate_sha256"],
    "complexity":pos["complexity"],"cell":pos["cell"]})
 if len(cases)!=108:raise SystemExit("P16_CASE_COUNT")
 out={"schema":"c3x-g95-p16-design-precommit-v1","scientific_stage":STAGE,"intervention_outcomes_consulted":False,
  "constitution_sha256":digest(c),"corpus_sha256":digest(corp),"parent_p15_receipt_sha256":parent["receipt_sha256"],
  "variants":variants,"execution":c["execution"],"unordered_pair_constitution":c["unordered_pair_constitution"],
  "board_intervention_family":c["board_intervention_family"],"relation_atoms":c["relation_atoms"],"chain_constitution":c["chain_constitution"],
  "exact_event_mediator":c["exact_event_mediator"],"bridge_definitions":c["bridge_definitions"],
  "structural_equivalence":c["structural_equivalence"],"support_gate":c["support_gate"],"certificate":c["certificate"],
  "claim_ceiling":c["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P16_DESIGN_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def load_design(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p16-design-precommit-v1" or x.get("intervention_outcomes_consulted") is not False:raise SystemExit("P16_DESIGN")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P16_DESIGN_HASH")
 return x

def qualify(a):
 pre=load_design(a.design);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P16_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P16_BINARY")
 ex=pre["execution"];fen=case["cell"]["fen"];board=chess.Board(fen)
 root=Path(a.out).parent/".p16-qual-private";root.mkdir(parents=True,exist_ok=True)
 base=p13.run_context(a.binary,v["protocol"],case["cell"],"CATALOG",None,root/"base")
 legal=sorted(m.uci() for m in board.legal_moves);shallow=[]
 for i,m in enumerate(legal):
  r=p13.run_forced(a.binary,v["protocol"],fen,m,int(ex["shallow_legal_move_nodes"]),root/"shallow",f"{i:02d}")
  s=r["semantic"].get("score");shallow.append({"uci":m,"move":p13.move_doc(fen,m),"score":s,"rank_value":p13.rank_value(s)})
 shortlist=sorted(shallow,key=lambda z:(-z["rank_value"],z["uci"]))[:int(ex["shortlist_size"])]
 qshort=[]
 for i,z in enumerate(shortlist):
  vals=[]
  for rep in range(int(ex["isolated_confirm_repeats"])):
   r=p13.run_forced(a.binary,v["protocol"],fen,z["uci"],int(ex["isolated_confirm_nodes"]),root/"confirm",f"{i:02d}-{rep}")
   vals.append(r["semantic"].get("score"))
  cps=[p13.score_cp(s) for s in vals];stable=len(cps)==2 and None not in cps and cps[0]==cps[1]
  qshort.append({"move":z["move"],"confirm_scores":vals,"stable":stable,"confirm_cp":cps[0] if stable else None})
 out={"schema":"c3x-g95-p16-engine-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"source_id":case["source_id"],"source_ply":case["source_ply"],"candidate_sha256":case["candidate_sha256"],
  "baseline":{k:base["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")},"shortlist":qshort,
  "intervention_outcomes_consulted":False,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P16_QUALIFY",case["case_id"],"stable",sum(z["stable"] for z in qshort),"baseline",out["baseline"]["bestmove"])

def pair_freeze(a):
 pre=load_design(a.design);found={}
 for p in Path(a.qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p16-engine-qualification-v1":found[x["case_id"]]=x
 ids={x["case_id"] for x in pre["cases"]}
 if set(found)!=ids:raise SystemExit(f"P16_QUAL_N {len(found)} expected {len(ids)}")
 bypos=defaultdict(list)
 for c in pre["cases"]:bypos[c["position_id"]].append((c,found[c["case_id"]]))
 positions={};active_worlds=0
 for pid,rows in sorted(bypos.items()):
  stable={c["engine"]:{z["move"]["uci"]:int(z["confirm_cp"]) for z in q["shortlist"] if z["stable"]} for c,q in rows}
  universe=sorted(set().union(*(set(z) for z in stable.values())));candidates=[]
  for A,B in itertools.combinations(universe,2):
   support=[]
   for c,q in rows:
    s=stable[c["engine"]];bm=q["baseline"].get("bestmove")
    if A in s and B in s and abs(s[A]-s[B])<=50 and bm in (A,B):
     support.append({"engine":c["engine"],"gap_cp_abs":abs(s[A]-s[B]),"baseline_preferred":bm})
   if len(support)>=2:
    gs=[x["gap_cp_abs"] for x in support]
    candidates.append({"pair_id":pair_id(A,B),"moves":[A,B],"support_count":len(support),
      "median_gap_cp":float(statistics.median(gs)),"max_gap_cp":max(gs)})
  candidates.sort(key=lambda z:(-z["support_count"],z["median_gap_cp"],z["max_gap_cp"],z["pair_id"]))
  c0,q0=rows[0];fen=c0["cell"]["fen"]
  if not candidates:
   positions[pid]={"position_id":pid,"source_id":c0["source_id"],"admitted":False,"pair":None,"engine_views":{},"chain_candidates":[]};continue
  sel=candidates[0];A,B=sel["moves"];views={};prefs=[]
  for c,q in rows:
   s=stable[c["engine"]];bm=q["baseline"].get("bestmove");both=A in s and B in s
   gap=None if not both else abs(s[A]-s[B]);active=bool(both and gap<=50 and bm in (A,B))
   if active:active_worlds+=1;prefs.append(bm)
   views[c["engine"]]={"active":active,"baseline_preferred":bm if active else None,"A_cp":s.get(A),"B_cp":s.get(B),"gap_cp_abs":gap,
    "gap_band":gap_band(gap) if active else None}
  chains=generate_chains(fen,A,B,{
   "max_abs_legal_root_move_count_delta":pre["board_intervention_family"]["max_abs_legal_root_move_count_delta"],
   "max_moved_piece_attack_set_symmetric_difference":pre["board_intervention_family"]["max_moved_piece_attack_set_symmetric_difference"],
   "max_chain_candidates_per_position":pre["execution"]["max_chain_candidates_per_position"]})
  positions[pid]={"position_id":pid,"source_id":c0["source_id"],"source_ply":c0["source_ply"],"candidate_sha256":c0["candidate_sha256"],
   "admitted":True,"pair":{"pair_id":sel["pair_id"],"A":p13.move_doc(fen,A),"B":p13.move_doc(fen,B),**{k:sel[k] for k in ("support_count","median_gap_cp","max_gap_cp")}},
   "geometry":"SPLIT_ORIENTATION" if len(set(prefs))>=2 else "CONSENSUS_ORIENTATION","engine_views":views,"chain_candidates":chains}
 cases=[]
 for c in pre["cases"]:
  pos=positions[c["position_id"]];cases.append({**c,"position_pair":pos,"engine_view":pos["engine_views"].get(c["engine"],{}),"qualification":found[c["case_id"]]})
 out={"schema":"c3x-g95-p16-pair-freeze-v1","scientific_stage":STAGE,"design_receipt_sha256":pre["receipt_sha256"],
  "intervention_outcomes_consulted":False,"admitted_pair_positions":sum(z["admitted"] for z in positions.values()),
  "active_engine_worlds":active_worlds,"positions_with_chain_candidates":sum(bool(z.get("chain_candidates")) for z in positions.values()),
  "execution":pre["execution"],"chain_constitution":pre["chain_constitution"],"exact_event_mediator":pre["exact_event_mediator"],
  "bridge_definitions":pre["bridge_definitions"],"structural_equivalence":pre["structural_equivalence"],"support_gate":pre["support_gate"],
  "certificate":pre["certificate"],"claim_ceiling":pre["claim_ceiling"],"variants":pre["variants"],"positions":positions,"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P16_PAIR_FREEZE",out["receipt_sha256"],"pairs",out["admitted_pair_positions"],"active",active_worlds,"chain_positions",out["positions_with_chain_candidates"])

def load_pair(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p16-pair-freeze-v1":raise SystemExit("P16_PAIR_FREEZE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P16_PAIR_HASH")
 return x

def chain_qualify(a):
 pre=load_pair(a.freeze);case=next(x for x in pre["cases"] if x["case_id"]==a.case_id)
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P16_BINARY")
 pos=case["position_pair"];view=case["engine_view"]
 if not pos.get("admitted") or not view.get("active") or not pos.get("chain_candidates"):
  out={"schema":"c3x-g95-p16-chain-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
   "position_id":case["position_id"],"active":False,"chain_support":[],"search_event_outcomes_consulted":False,"edited_native_choice_consulted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P16_CHAINQUAL_SKIP",case["case_id"]);return
 A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"];ex=pre["execution"];root=Path(a.out).parent/".p16-chainqual-private";root.mkdir(parents=True,exist_ok=True)
 rows=[]
 for i,ch in enumerate(pos["chain_candidates"]):
  boards={"TARGET":ch["target"]["fen"],"SUBSET":ch["subset"]["fen"],"SHAM":ch["sham"]["fen"]};detail={};ok=True;maxgap=0
  for bn,fen in boards.items():
   vals={}
   for mi,m in enumerate((A,B)):
    scores=[]
    for rep in range(int(ex["chain_pair_confirm_repeats"])):
     r=p13.run_forced(a.binary,v["protocol"],fen,m,int(ex["chain_pair_confirm_nodes"]),root/f"{i:02d}-{bn}",f"{mi}-{rep}")
     scores.append(r["semantic"].get("score"))
    cps=[p13.score_cp(s) for s in scores];stable=len(cps)==2 and None not in cps and cps[0]==cps[1]
    vals[m]={"stable":stable,"cp":cps[0] if stable else None}
   gap=None if not all(vals[m]["stable"] for m in (A,B)) else abs(vals[A]["cp"]-vals[B]["cp"])
   legal=A in {x.uci() for x in chess.Board(fen).legal_moves} and B in {x.uci() for x in chess.Board(fen).legal_moves}
   supported=bool(legal and gap is not None and gap<=50);ok=ok and supported
   if gap is not None:maxgap=max(maxgap,gap)
   detail[bn]={"pair":vals,"gap_cp_abs":gap,"supported":supported}
  rows.append({"chain_id":ch["chain_id"],"chain_type":ch["chain_type"],"supported":ok,"max_gap_cp_abs":maxgap if ok else None,"boards":detail})
 out={"schema":"c3x-g95-p16-chain-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"active":True,"chain_support":rows,"search_event_outcomes_consulted":False,"edited_native_choice_consulted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P16_CHAINQUAL",case["case_id"],"supported",sum(z["supported"] for z in rows),"/",len(rows))

def chain_freeze(a):
 pre=load_pair(a.freeze);found={}
 for p in Path(a.chain_qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p16-chain-qualification-v1":found[x["case_id"]]=x
 if set(found)!={x["case_id"] for x in pre["cases"]}:raise SystemExit("P16_CHAINQUAL_N")
 selected={};active_chain_worlds=0
 for pid,pos in sorted(pre["positions"].items()):
  if not pos.get("admitted"):selected[pid]=[];continue
  admitted=[]
  for ch in pos.get("chain_candidates",[]):
   supporters=[];gaps=[]
   for c in pre["cases"]:
    if c["position_id"]!=pid or not c["engine_view"].get("active"):continue
    row=next((z for z in found[c["case_id"]].get("chain_support",[]) if z["chain_id"]==ch["chain_id"] and z["supported"]),None)
    if row:supporters.append(c["engine"]);gaps.append(row["max_gap_cp_abs"])
   if len(supporters)>=2:admitted.append({"chain":ch,"supporting_engines":sorted(supporters),"support_count":len(supporters),"max_gap_cp_abs":max(gaps)})
  picks=[]
  for typ in ("COMPOSITE_DELETION_CHAIN","ATOMIC_CHAIN"):
   xs=[z for z in admitted if z["chain"]["chain_type"]==typ]
   xs.sort(key=lambda z:(-z["support_count"],z["max_gap_cp_abs"],z["chain"]["target_atom_count"],z["chain"]["chain_id"]))
   if xs:picks.append(xs[0])
  selected[pid]=picks;active_chain_worlds+=sum(len(z["supporting_engines"]) for z in picks)
 cases=[]
 for c in pre["cases"]:
  rows=[]
  for z in selected[c["position_id"]]:
   if c["engine"] in z["supporting_engines"]:rows.append(z)
  cases.append({**c,"selected_chains":rows,"factorial_active":bool(rows),"chain_qualification":found[c["case_id"]]})
 out={"schema":"c3x-g95-p16-chain-freeze-v1","scientific_stage":STAGE,"pair_freeze_receipt_sha256":pre["receipt_sha256"],
  "search_event_outcomes_consulted":False,"edited_native_choice_consulted":False,
  "admitted_pair_positions":pre["admitted_pair_positions"],"chain_positions":sum(bool(v) for v in selected.values()),
  "selected_chain_count":sum(len(v) for v in selected.values()),"active_chain_engine_worlds":active_chain_worlds,
  "active_engines":sorted({c["engine"] for c in cases if c["factorial_active"]}),"sources":sorted({c["source_id"] for c in cases if c["factorial_active"]}),
  "execution":pre["execution"],"exact_event_mediator":pre["exact_event_mediator"],"bridge_definitions":pre["bridge_definitions"],
  "structural_equivalence":pre["structural_equivalence"],"support_gate":pre["support_gate"],"certificate":pre["certificate"],
  "claim_ceiling":pre["claim_ceiling"],"variants":pre["variants"],"positions":pre["positions"],"selected_chains":selected,"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P16_CHAIN_FREEZE",out["receipt_sha256"],"positions",out["chain_positions"],"chains",out["selected_chain_count"],"active_chain_worlds",active_chain_worlds)

def load_chain(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p16-chain-freeze-v1":raise SystemExit("P16_CHAIN_FREEZE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P16_CHAIN_HASH")
 return x

def bridge(b0,bx,bs,bound,A,B):
 r0=b0["bounds"][bound]["record"];rx=bx["bounds"][bound]["record"]
 if not r0 or not rx:return None
 n0=b0["native"].get("bestmove");nx=bx["native"].get("bestmove")
 if n0 not in (A,B) or nx not in (A,B) or n0==nx:return None
 t0=r0["t_only_root"]["uci"];tx=rx["t_only_root"]["uci"]
 if t0 not in (A,B) or tx not in (A,B) or t0!=tx:return None
 sham_rep=False;rs=bs["bounds"][bound]["record"];ns=bs["native"].get("bestmove")
 if rs and n0 in (A,B) and ns in (A,B) and n0!=ns:
  ts=rs["t_only_root"]["uci"];sham_rep=ts in (A,B) and ts==t0
 if sham_rep:return None
 return {"bound":bound,"original_native":n0,"edited_native":nx,"collapse_to":t0,"sham_reproduced":False}

def factorial(a):
 pre=load_chain(a.freeze);case=next(x for x in pre["cases"] if x["case_id"]==a.case_id)
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P16_BINARY")
 if not case["factorial_active"]:
  out={"schema":"c3x-g95-p16-factorial-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
   "position_id":case["position_id"],"source_id":case["source_id"],"active":False,"chains":[],"address_misses":[],"raw_tt_key_emitted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P16_FACTORIAL_SKIP",case["case_id"]);return
 pos=case["position_pair"];A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"];preferred=case["engine_view"]["baseline_preferred"];anchor=B if preferred==A else A
 root=Path(a.out).parent/".p16-factorial-private";root.mkdir(parents=True,exist_ok=True)
 b0=p15.run_board_cell(a.binary,v["protocol"],case["cell"],case["cell"]["fen"],A,B,anchor,root,"B0",int(pre["execution"]["max_semantic_targets_per_board"]))
 if b0["native"].get("bestmove")!=preferred:raise SystemExit("P16_B0_DRIFT")
 worlds=[];misses=[{"chain":"B0","board":"B0",**m} for m in b0["address_misses"]]
 for ci,z in enumerate(case["selected_chains"]):
  ch=z["chain"];boards={}
  for bn,key in (("TARGET","target"),("SUBSET","subset"),("SHAM","sham")):
   boards[bn]=p15.run_board_cell(a.binary,v["protocol"],case["cell"],ch[key]["fen"],A,B,anchor,root,f"C{ci}-{bn}",int(pre["execution"]["max_semantic_targets_per_board"]))
   misses += [{"chain":ch["chain_id"],"board":bn,**m} for m in boards[bn]["address_misses"]]
  eatoms=engine_atoms(ch["target"]["atoms"],A,preferred)
  side="OWN" if ch["target"]["piece_color"]==("WHITE" if chess.Board(case["cell"]["fen"]).turn else "BLACK") else "OPPONENT"
  brs=[];mods=[]
  for bound in ("UPPER","LOWER"):
   bt=bridge(b0,boards["TARGET"],boards["SHAM"],bound,A,B)
   if bt:
    bs=bridge(b0,boards["SUBSET"],boards["SHAM"],bound,A,B)
    minimal=bs is None
    brs.append({**bt,"kind":"MINIMAL_FULL_BRIDGE" if minimal else "FULL_BRIDGE_NONMINIMAL",
      "subset_reproduced":not minimal,"moved_side_role":side,"engine_relative_atoms":eatoms,
      "exact_signature":"|".join([side,"+".join(eatoms),bound,"MINIMAL_FULL_BRIDGE"]) if minimal else None,
      "coarse_role":dominance(eatoms)})
   s0=b0["bounds"][bound]["state"];st=boards["TARGET"]["bounds"][bound]["state"]
   if s0!=st:mods.append({"kind":"SUSCEPTIBILITY_MODULATION","bound":bound,"original_state":s0,"target_state":st})
  worlds.append({"chain_id":ch["chain_id"],"chain_type":ch["chain_type"],"supporting_engines":z["supporting_engines"],
    "target":ch["target"],"subset":ch["subset"],"sham":ch["sham"],"moved_side_role":side,"engine_relative_atoms":eatoms,
    "bridge_records":brs,"susceptibility_records":mods,"boards":{"B0":b0,**boards}})
 out={"schema":"c3x-g95-p16-factorial-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"source_id":case["source_id"],"active":True,"pair":pos["pair"],"chains":worlds,
  "address_misses":misses,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P16_FACTORIAL",case["case_id"],"chains",len(worlds),"minimal",sum(r["kind"]=="MINIMAL_FULL_BRIDGE" for w in worlds for r in w["bridge_records"]),"miss",len(misses))

def adjudicate(a):
 pre=load_chain(a.freeze);worlds=[]
 for p in Path(a.worlds).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p16-factorial-world-v1":worlds.append(x)
 if len(worlds)!=108:raise SystemExit(f"P16_WORLD_N {len(worlds)}")
 active=[w for w in worlds if w["active"]];misses=sum(len(w["address_misses"]) for w in worlds)
 engines=sorted({w["engine"] for w in active});sources=sorted({w["source_id"] for w in active})
 fired_worlds=0;rows=[];mods=[]
 for w in active:
  anyfire=False
  for cw in w["chains"]:
   for brd in cw["boards"].values():
    if any(q["record"] for q in brd["bounds"].values()):anyfire=True
   for r in cw["bridge_records"]:rows.append({"engine":w["engine"],"position_id":w["position_id"],"source_id":w["source_id"],
     "pair_id":w["pair"]["pair_id"],"chain_id":cw["chain_id"],"physical_edit_id":cw["target"]["edit_id"],**r})
   for r in cw["susceptibility_records"]:mods.append({"engine":w["engine"],"position_id":w["position_id"],"source_id":w["source_id"],"chain_id":cw["chain_id"],**r})
  fired_worlds+=int(anyfire)
 gate=pre["support_gate"];support=(pre["admitted_pair_positions"]>=gate["min_admitted_pair_positions"] and pre["chain_positions"]>=gate["min_chain_positions"] and
  pre["active_chain_engine_worlds"]>=gate["min_active_chain_engine_worlds"] and len(engines)>=gate["min_active_engines"] and len(sources)>=gate["min_sources"] and
  fired_worlds>=gate["min_worlds_with_any_fired_semantic_target"] and misses<=gate["max_address_misses"])
 minimal=[r for r in rows if r["kind"]=="MINIMAL_FULL_BRIDGE"];full=[r for r in rows if r["kind"] in ("MINIMAL_FULL_BRIDGE","FULL_BRIDGE_NONMINIMAL")]
 eq=defaultdict(list)
 for r in minimal:eq[r["exact_signature"]].append(r)
 req=pre["structural_equivalence"]["exact_replication_requires"];rep_exact=[]
 for k,v in sorted(eq.items()):
  if len(v)>=req["witnesses"] and len({x["engine"] for x in v})>=req["engines"] and len({x["position_id"] for x in v})>=req["positions"] and len({x["source_id"] for x in v})>=req["sources"] and len({x["physical_edit_id"] for x in v})>=req["distinct_physical_edits"]:
   rep_exact.append({"signature":k,"witnesses":len(v),"engines":sorted({x["engine"] for x in v}),"positions":len({x["position_id"] for x in v}),
    "sources":sorted({x["source_id"] for x in v}),"physical_edits":sorted({x["physical_edit_id"] for x in v})})
 cg=defaultdict(list)
 for r in full:cg[f'{r["coarse_role"]}|{r["bound"]}|FULL_BRIDGE'].append(r)
 cr=pre["structural_equivalence"]["coarse_replication_requires"];rep_coarse=[]
 for k,v in sorted(cg.items()):
  if len(v)>=cr["witnesses"] and len({x["engine"] for x in v})>=cr["engines"] and len({x["position_id"] for x in v})>=cr["positions"] and len({x["source_id"] for x in v})>=cr["sources"]:
   rep_coarse.append({"signature":k,"witnesses":len(v),"engines":sorted({x["engine"] for x in v}),"positions":len({x["position_id"] for x in v}),"sources":sorted({x["source_id"] for x in v})})
 # P15 susceptibility replication is not redefined here; this flag only reports whether the frozen P16 sample still contains modulation.
 if not support:verdict="P16_FRESH_SUPPORT_HOLD"
 elif rep_exact:verdict="P16_REPLICATED_MINIMAL_STRUCTURAL_EQUIVALENCE_FULL_BRIDGE"
 elif rep_coarse:verdict="P16_REPLICATED_FULL_PREFERENCE_MEDIATION_NO_STABLE_MINIMAL_EQUIVALENCE"
 elif minimal:verdict="P16_LOCAL_MINIMAL_FULL_BRIDGE_ONLY"
 elif mods:verdict="P16_REPLICATED_SUSCEPTIBILITY_ONLY"
 else:verdict="P16_NO_FULL_BRIDGE_UNDER_FROZEN_MINIMIZATION_FAMILY"
 rep_sigs={z["signature"] for z in rep_exact};certs=[]
 for i,r in enumerate(minimal):
  certs.append({"schema":"c3x-causal-contrast-certificate-v1","provenance_class":"C3X_CAUSAL_CONTRAST",
   "certificate_id":hashlib.sha256((r["engine"]+"|"+r["position_id"]+"|"+r["chain_id"]+"|"+r["bound"]).encode()).hexdigest()[:24],
   "engine":r["engine"],"position_id":r["position_id"],"source_id":r["source_id"],"pair_id":r["pair_id"],
   "chain_id":r["chain_id"],"physical_edit_id":r["physical_edit_id"],"moved_side_role":r["moved_side_role"],
   "engine_relative_atoms":r["engine_relative_atoms"],"bound":r["bound"],"collapse_to":r["collapse_to"],
   "subset_reproduced":r["subset_reproduced"],"sham_reproduced":r["sham_reproduced"],
   "structural_signature":r["exact_signature"],"replication_status":"REPLICATED_FAMILY_MEMBER" if r["exact_signature"] in rep_sigs else "LOCAL_ONLY",
   "concept_label":None,"authority_ceiling":pre["claim_ceiling"]})
 out={"schema":"c3x-g95-p16-adjudication-v1","scientific_stage":STAGE,"status":"CLOSED_PASS" if support else "HOLD","verdict":verdict,
  "world_count":len(worlds),"support":{"pass":support,"admitted_pair_positions":pre["admitted_pair_positions"],"chain_positions":pre["chain_positions"],
   "selected_chain_count":pre["selected_chain_count"],"active_chain_engine_worlds":pre["active_chain_engine_worlds"],"active_engines":engines,"sources":sources,
   "worlds_with_any_fired_semantic_target":fired_worlds,"address_misses":misses},
  "minimal_full_bridge_records":len(minimal),"all_full_bridge_records":len(full),"susceptibility_modulation_records":len(mods),
  "replicated_exact_structural_signatures":rep_exact,"replicated_coarse_full_bridge_signatures":rep_coarse,
  "bridge_records":rows,"causal_explanation_certificates":certs,"claim_ceiling":pre["claim_ceiling"],"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 lines=["# C3X G9.5-P16 — Minimal Distinguishing Chess Structure","",f"Status: **{out['status']} / {verdict}**",
  f"Pair positions: **{pre['admitted_pair_positions']}/36**; chain positions: **{pre['chain_positions']}**; selected chains: **{pre['selected_chain_count']}**; active chain-worlds: **{pre['active_chain_engine_worlds']}**.",
  f"Minimal FULL_BRIDGE: **{len(minimal)}**; all FULL_BRIDGE: **{len(full)}**; susceptibility records: **{len(mods)}**; address misses: **{misses}**.","",
  "## Replicated exact minimal structural signatures"]
 if rep_exact:
  for z in rep_exact:lines.append(f"- {z['signature']}: witnesses={z['witnesses']}; engines={','.join(z['engines'])}; positions={z['positions']}; sources={','.join(z['sources'])}.")
 else:lines.append("- None under the frozen rule.")
 lines+=["","## Replicated coarse full-bridge signatures"]
 if rep_coarse:
  for z in rep_coarse:lines.append(f"- {z['signature']}: witnesses={z['witnesses']}; engines={','.join(z['engines'])}; positions={z['positions']}; sources={','.join(z['sources'])}.")
 else:lines.append("- None under the frozen rule.")
 lines+=["","Certificates are intervention-family-relative causal contrast evidence. Human strategic concept labels remain unset."]
 Path(a.markdown).write_text("\n".join(lines)+"\n")
 print("P16_ADJUDICATE",verdict,out["support"],"minimal",len(minimal),"full",len(full),"rep_exact",len(rep_exact),"rep_coarse",len(rep_coarse))

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("design");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p15-closure",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=design)
 q=sp.add_parser("qualify");q.add_argument("--design",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=qualify)
 q=sp.add_parser("pair-freeze");q.add_argument("--design",required=True);q.add_argument("--qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=pair_freeze)
 q=sp.add_parser("chain-qualify");q.add_argument("--freeze",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=chain_qualify)
 q=sp.add_parser("chain-freeze");q.add_argument("--freeze",required=True);q.add_argument("--chain-qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=chain_freeze)
 q=sp.add_parser("factorial");q.add_argument("--freeze",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=factorial)
 q=sp.add_parser("adjudicate");q.add_argument("--freeze",required=True);q.add_argument("--worlds",required=True);q.add_argument("--out",required=True);q.add_argument("--markdown",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
