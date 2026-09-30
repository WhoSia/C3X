#!/usr/bin/env python3
import argparse,hashlib,itertools,json,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path
import chess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import g95_p13_court as p13
import g95_p15_court as p15
import g95_p16_court as p16
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P18"
ENGINES=("stockfish_19","berserk","ethereal")
H="OWN|DISPREFERRED_FROM_LOSS"
GRAMMARS=("G0","G1")

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def pair_id(a,b):return "::".join(sorted((a,b)))
def family_coords(f):
 side,atom=f.split("|",1);role,endpoint,direction=atom.split("_")
 return (side,role,endpoint,direction)
def family_hamming(a,b):return sum(x!=y for x,y in zip(family_coords(a),family_coords(b)))
def family_universe():
 return sorted(f"{s}|{r}_{e}_{d}" for s in ("OWN","OPPONENT") for r in ("PREFERRED","DISPREFERRED")
  for e in ("FROM","TO") for d in ("GAIN","LOSS"))
FAMILIES=tuple(family_universe())

def load_design(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p18-design-precommit-v1":raise SystemExit("P18_DESIGN")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P18_DESIGN_HASH")
 return x
def load_pool(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p18-pair-pool-freeze-v1":raise SystemExit("P18_POOL")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P18_POOL_HASH")
 return x
def load_ecology(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p18-development-ecology-v1":raise SystemExit("P18_ECOLOGY")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P18_ECOLOGY_HASH")
 return x
def load_confirm(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p18-confirmation-freeze-v1":raise SystemExit("P18_CONFIRM")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P18_CONFIRM_HASH")
 return x

def edit_candidates(fen,A,B,cfg):
 b=chess.Board(fen);ma=chess.Move.from_uci(A);mb=chess.Move.from_uci(B)
 endpoints=[ma.from_square,ma.to_square,mb.from_square,mb.to_square]
 blocked=set(endpoints);moving={ma.from_square,mb.from_square};edits=[]
 for fr,piece in sorted(b.piece_map().items()):
  if fr in moving or piece.piece_type not in p16.PIECE_NAME:continue
  if piece.piece_type==chess.ROOK and bool(b.castling_rights&chess.BB_SQUARES[fr]):continue
  for to in sorted(b.attacks(fr)):
   if to in blocked or b.piece_at(to) is not None:continue
   q=p16.apply_edit(b,fr,to)
   if not q.is_valid() or q.is_game_over(claim_draw=False) or q.is_check():continue
   legal={m.uci() for m in q.legal_moves}
   if A not in legal or B not in legal:continue
   ld=abs(q.legal_moves.count()-b.legal_moves.count())
   ad=len(set(b.attacks(fr))^set(q.attacks(to)))
   if ld>6 or ad>10:continue
   edits.append(p16.edit_doc(b,fr,to,endpoints))
 groups=defaultdict(list)
 for e in edits:groups[e["from"]].append(e)
 out=[]
 for fr,rows in sorted(groups.items()):
  shams=[x for x in rows if len(x["atoms"])==0]
  targets=[x for x in rows if len(x["atoms"])==1]
  for t in targets:
   for grammar,maxdd in (("G0",0),("G1",1)):
    zs=[s for s in shams if abs(int(s["distance"])-int(t["distance"]))<=maxdd]
    if not zs:continue
    zs.sort(key=lambda s:(abs(int(s["distance"])-int(t["distance"])),
      abs(abs(int(s["legal_move_count_delta"]))-abs(int(t["legal_move_count_delta"]))),
      abs(int(s["attack_set_symmetric_difference"])-int(t["attack_set_symmetric_difference"])),s["edit_id"]))
    sham=zs[0]
    out.append({"chain_id":f"{grammar}:{t['edit_id']}::SHAM::{sham['edit_id']}","grammar":grammar,
      "target":t,"sham":sham,"target_atom_count":1})
 return out

def ex_sort(ex):
 t=ex["chain"]["target"]
 return (abs(t["legal_move_count_delta"]),t["attack_set_symmetric_difference"],t["distance"],
  t["piece_type"],ex["position_id"],t["edit_id"],ex["chain"]["sham"]["edit_id"],ex["exposure_id"])

def match_distance(a,b,w):
 ta=a["chain"]["target"];tb=b["chain"]["target"]
 return (w["piece_type_mismatch"]*(ta["piece_type"]!=tb["piece_type"]) +
  w["relocation_distance_abs_diff"]*abs(ta["distance"]-tb["distance"]) +
  w["legal_root_delta_abs_diff"]*abs(abs(ta["legal_move_count_delta"])-abs(tb["legal_move_count_delta"])) +
  w["attack_symdiff_abs_diff"]*abs(ta["attack_set_symmetric_difference"]-tb["attack_set_symmetric_difference"]) +
  w["original_pair_gap_abs_diff"]*abs(a["original_pair_gap_cp_abs"]-b["original_pair_gap_cp_abs"]) +
  w["edited_max_pair_gap_abs_diff"]*abs(a["edited_max_pair_gap_cp_abs"]-b["edited_max_pair_gap_cp_abs"]))

def greedy_sets(exposures,families,weights,quota,prefix):
 used=set();sets=[]
 for e in ENGINES:
  for src in sorted({x["source_id"] for x in exposures}):
   cell=[x for x in exposures if x["engine"]==e and x["source_id"]==src]
   chosen=0
   while chosen<quota:
    hs=[x for x in cell if x["family"]==H and x["exposure_id"] not in used]
    proposals=[]
    for h in hs:
     arms={H:h};cost=0.0;ok=True
     for fam in families:
      if fam==H:continue
      xs=[x for x in cell if x["family"]==fam and x["exposure_id"] not in used]
      if not xs:ok=False;break
      xs.sort(key=lambda z:(match_distance(h,z,weights),z["exposure_id"]))
      arms[fam]=xs[0];cost+=match_distance(h,xs[0],weights)
     if ok:proposals.append((cost,h["exposure_id"],arms))
    if not proposals:break
    proposals.sort(key=lambda z:(z[0],z[1]));cost,_,arms=proposals[0]
    sid=f"{prefix}:{e}:{src}:{chosen}"
    sets.append({"matched_set_id":sid,"engine":e,"source_id":src,"total_match_distance":cost,
      "arms":{fam:arms[fam]["exposure_id"] for fam in families}})
    used.update(z["exposure_id"] for z in arms.values());chosen+=1
 return sets,used

def design(a):
 c=load(a.constitution);corp=load(a.corpus);parent=load(a.p17_closure)
 if c.get("schema")!="c3x-g95-p18-constitution-v1":raise SystemExit("P18_CONSTITUTION")
 if parent.get("receipt_sha256")!=c["parent"]["closure_receipt_sha256"]:raise SystemExit("P18_PARENT")
 if corp.get("schema")!="c3x-g95-p18-corpus-v1":raise SystemExit("P18_CORPUS")
 variants={}
 for e in ENGINES:
  fs=list(Path(a.build_dir).rglob(f"c3x-p18-{e}"))
  if len(fs)!=1:raise SystemExit(f"P18_BUILD {e} {len(fs)}")
  variants[e]={"sha256":sha_file(fs[0]),"protocol":p32.protocol_for(e)}
 cases=[]
 for pos in corp["positions"]:
  for e in ENGINES:
   cases.append({"case_id":f'p18:{e}:{pos["position_id"]}',"engine":e,"position_id":pos["position_id"],"split":pos["split"],
    "source_id":pos["source_id"],"source_ply":pos["source_ply"],"candidate_sha256":pos["candidate_sha256"],"cell":pos["cell"]})
 if len(cases)!=288:raise SystemExit("P18_CASE_COUNT")
 out={"schema":"c3x-g95-p18-design-precommit-v1","scientific_stage":STAGE,"intervention_outcomes_consulted":False,
  "constitution_sha256":digest(c),"corpus_sha256":digest(corp),"parent_p17_receipt_sha256":parent["receipt_sha256"],
  "variants":variants,"execution":c["execution"],"pair":c["unordered_pair_constitution"],"control_grammar_ladder":c["control_grammar_ladder"],
  "development_rival_eligibility":c["development_rival_eligibility"],"ecology_selection":c["ecology_selection"],
  "confirmation":c["confirmation"],"exact_event_mediator":c["exact_event_mediator"],"estimand":c["estimand"],
  "replication_rule":c["replication_rule"],"claim_ceiling":["Engine-preference mediation under the frozen P18 intervention/search regime only.",
   "No objective chess truth, cognition, human intention or strategic-concept semantics."],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P18_DESIGN_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def qualify(a):
 pre=load_design(a.design);case=next(x for x in pre["cases"] if x["case_id"]==a.case_id);v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P18_BINARY")
 ex=pre["execution"];fen=case["cell"]["fen"];board=chess.Board(fen);root=Path(a.out).parent/".p18-qual";root.mkdir(parents=True,exist_ok=True)
 base=p13.run_context(a.binary,v["protocol"],case["cell"],"CATALOG",None,root/"base")
 legal=sorted(m.uci() for m in board.legal_moves);shallow=[]
 for i,m in enumerate(legal):
  z=p13.run_forced(a.binary,v["protocol"],fen,m,int(ex["shallow_legal_move_nodes"]),root/"shallow",f"{i:02d}")
  shallow.append({"uci":m,"move":p13.move_doc(fen,m),"rank_value":p13.rank_value(z["semantic"].get("score"))})
 shortlist=sorted(shallow,key=lambda z:(-z["rank_value"],z["uci"]))[:int(ex["shortlist_size"])]
 qshort=[]
 for i,z in enumerate(shortlist):
  vals=[]
  for rep in range(int(ex["isolated_confirm_repeats"])):
   rr=p13.run_forced(a.binary,v["protocol"],fen,z["uci"],int(ex["isolated_confirm_nodes"]),root/"confirm",f"{i}-{rep}")
   vals.append(rr["semantic"].get("score"))
  cps=[p13.score_cp(s) for s in vals];stable=len(cps)==int(ex["isolated_confirm_repeats"]) and None not in cps and len(set(cps))==1
  qshort.append({"move":z["move"],"confirm_scores":vals,"stable":stable,"confirm_cp":cps[0] if stable else None})
 out={"schema":"c3x-g95-p18-engine-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"split":case["split"],"source_id":case["source_id"],"source_ply":case["source_ply"],
  "candidate_sha256":case["candidate_sha256"],"baseline":{k:base["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")},
  "shortlist":qshort,"intervention_outcomes_consulted":False,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P18_QUALIFY",case["case_id"],"stable",sum(z["stable"] for z in qshort))

def pair_pool_freeze(a):
 pre=load_design(a.design);found={}
 for p in Path(a.qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p18-engine-qualification-v1":found[x["case_id"]]=x
 if set(found)!={x["case_id"] for x in pre["cases"]}:raise SystemExit(f"P18_QUAL_N {len(found)}")
 bypos=defaultdict(list)
 for c in pre["cases"]:bypos[c["position_id"]].append((c,found[c["case_id"]]))
 positions={};active_worlds=0
 for pid,rows in sorted(bypos.items()):
  stable={c["engine"]:{z["move"]["uci"]:int(z["confirm_cp"]) for z in q["shortlist"] if z["stable"]} for c,q in rows}
  universe=sorted(set().union(*(set(z) for z in stable.values())));cand=[]
  for A,B in itertools.combinations(universe,2):
   support=[]
   for c,q in rows:
    s=stable[c["engine"]];bm=q["baseline"].get("bestmove")
    if A in s and B in s and abs(s[A]-s[B])<=50 and bm in (A,B):support.append({"engine":c["engine"],"gap":abs(s[A]-s[B])})
   if len(support)>=2:
    gs=[z["gap"] for z in support];cand.append({"pair_id":pair_id(A,B),"moves":[A,B],"support_count":len(support),
      "median_gap_cp":float(statistics.median(gs)),"max_gap_cp":max(gs)})
  cand.sort(key=lambda z:(-z["support_count"],z["median_gap_cp"],z["max_gap_cp"],z["pair_id"]))
  c0,q0=rows[0];fen=c0["cell"]["fen"]
  if not cand:
   positions[pid]={"position_id":pid,"split":c0["split"],"source_id":c0["source_id"],"admitted":False,"pair":None,"engine_views":{},"chains":[]};continue
  sel=cand[0];A,B=sel["moves"];views={}
  for c,q in rows:
   s=stable[c["engine"]];bm=q["baseline"].get("bestmove");both=A in s and B in s;gap=None if not both else abs(s[A]-s[B])
   active=bool(both and gap<=50 and bm in (A,B));active_worlds+=int(active)
   views[c["engine"]]={"active":active,"baseline_preferred":bm if active else None,"A_cp":s.get(A),"B_cp":s.get(B),"gap_cp_abs":gap}
  chains=edit_candidates(fen,A,B,pre["control_grammar_ladder"])
  positions[pid]={"position_id":pid,"split":c0["split"],"source_id":c0["source_id"],"source_ply":c0["source_ply"],
   "candidate_sha256":c0["candidate_sha256"],"admitted":True,"pair":{"pair_id":sel["pair_id"],"A":p13.move_doc(fen,A),"B":p13.move_doc(fen,B),
   "support_count":sel["support_count"],"median_gap_cp":sel["median_gap_cp"],"max_gap_cp":sel["max_gap_cp"]},"engine_views":views,"chains":chains}
 all_ex=[];cases=[];maxpw=int(pre["execution"]["max_atomic_candidates_per_family_per_world"])
 for c in pre["cases"]:
  pos=positions[c["position_id"]];view=pos["engine_views"].get(c["engine"],{});xs=[]
  if pos.get("admitted") and view.get("active"):
   A=pos["pair"]["A"]["uci"];pref=view["baseline_preferred"];turn=chess.Board(c["cell"]["fen"]).turn
   for ch in pos["chains"]:
    eat=p16.engine_atoms(ch["target"]["atoms"],A,pref)
    if len(eat)!=1:continue
    side="OWN" if ch["target"]["piece_color"]==("WHITE" if turn else "BLACK") else "OPPONENT"
    fam=f"{side}|{eat[0]}"
    if fam not in FAMILIES:continue
    xs.append({"exposure_id":c["case_id"]+"::"+ch["chain_id"],"case_id":c["case_id"],"engine":c["engine"],"split":c["split"],
      "source_id":c["source_id"],"position_id":c["position_id"],"family":fam,"grammar":ch["grammar"],"moved_side_role":side,
      "engine_relative_atoms":eat,"original_pair_gap_cp_abs":view["gap_cp_abs"],"chain":ch})
   keep=[]
   for g in GRAMMARS:
    for fam in FAMILIES:keep+=sorted([z for z in xs if z["grammar"]==g and z["family"]==fam],key=ex_sort)[:maxpw]
   xs=keep
  all_ex+=xs;cases.append({**c,"position_pair":pos,"engine_view":view,"qualification":found[c["case_id"]],"all_exposures":xs})
 quota=int(pre["execution"]["prequalification_pool_quota_per_engine_source_family_grammar"]);pool=set();counts={}
 for split in ("development","confirmation"):
  for e in ENGINES:
   for src in sorted({c["source_id"] for c in pre["cases"]}):
    for g in GRAMMARS:
     for fam in FAMILIES:
      zs=sorted([z for z in all_ex if z["split"]==split and z["engine"]==e and z["source_id"]==src and z["grammar"]==g and z["family"]==fam],key=ex_sort)[:quota]
      pool.update(z["exposure_id"] for z in zs);counts[f"{split}|{e}|{src}|{g}|{fam}"]=len(zs)
 for c in cases:c["candidate_exposures"]=[z for z in c["all_exposures"] if z["exposure_id"] in pool]
 out={"schema":"c3x-g95-p18-pair-pool-freeze-v1","scientific_stage":STAGE,"design_receipt_sha256":pre["receipt_sha256"],
  "intervention_outcomes_consulted":False,"edited_native_choice_consulted":False,
  "admitted_pair_positions":{"development":sum(z["admitted"] and z["split"]=="development" for z in positions.values()),
   "confirmation":sum(z["admitted"] and z["split"]=="confirmation" for z in positions.values())},
  "active_original_engine_worlds":active_worlds,"candidate_pool_exposures":len(pool),"candidate_pool_counts":dict(sorted(counts.items())),
  "execution":pre["execution"],"development_rival_eligibility":pre["development_rival_eligibility"],"ecology_selection":pre["ecology_selection"],
  "confirmation":pre["confirmation"],"exact_event_mediator":pre["exact_event_mediator"],"estimand":pre["estimand"],
  "replication_rule":pre["replication_rule"],"claim_ceiling":pre["claim_ceiling"],"variants":pre["variants"],"positions":positions,"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P18_PAIR_POOL",out["receipt_sha256"],out["admitted_pair_positions"],"pool",len(pool))

def exposure_qualify(a):
 pre=load_pool(a.freeze);case=next(x for x in pre["cases"] if x["case_id"]==a.case_id);phase=a.phase
 if case["split"]!=phase:
  out={"schema":"c3x-g95-p18-exposure-qualification-v1","scientific_stage":STAGE,"phase":phase,"case_id":case["case_id"],"engine":case["engine"],
   "position_id":case["position_id"],"active":False,"exposure_support":[],"search_event_outcomes_consulted":False,"edited_native_choice_consulted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");return
 ecology=load_ecology(a.ecology) if phase=="confirmation" else None
 if ecology and ecology["status"]!="PASS":allowed=[]
 elif ecology:allowed=[z for z in case["candidate_exposures"] if z["grammar"]==ecology["selected_grammar"] and z["family"] in ecology["families"]]
 else:allowed=case["candidate_exposures"]
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P18_BINARY")
 if not allowed:
  out={"schema":"c3x-g95-p18-exposure-qualification-v1","scientific_stage":STAGE,"phase":phase,"case_id":case["case_id"],"engine":case["engine"],
   "position_id":case["position_id"],"active":False,"exposure_support":[],"search_event_outcomes_consulted":False,"edited_native_choice_consulted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");return
 pos=case["position_pair"];A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"];root=Path(a.out).parent/f".p18-{phase}-exq";root.mkdir(parents=True,exist_ok=True)
 rows=[];nodes=int(pre["execution"]["exposure_pair_confirm_nodes"]);reps=int(pre["execution"]["exposure_pair_confirm_repeats"])
 for i,ex in enumerate(allowed):
  detail={};ok=True;maxgap=0
  for bn,key in (("TARGET","target"),("SHAM","sham")):
   fen=ex["chain"][key]["fen"];vals={}
   for mi,m in enumerate((A,B)):
    scores=[]
    for rep in range(reps):
     rr=p13.run_forced(a.binary,v["protocol"],fen,m,nodes,root/f"{i}-{bn}",f"{mi}-{rep}");scores.append(rr["semantic"].get("score"))
    cps=[p13.score_cp(s) for s in scores];stable=len(cps)==reps and None not in cps and len(set(cps))==1
    vals[m]={"stable":stable,"cp":cps[0] if stable else None}
   gap=None if not all(vals[m]["stable"] for m in (A,B)) else abs(vals[A]["cp"]-vals[B]["cp"])
   legal=A in {x.uci() for x in chess.Board(fen).legal_moves} and B in {x.uci() for x in chess.Board(fen).legal_moves}
   supported=bool(legal and gap is not None and gap<=50);ok=ok and supported
   if gap is not None:maxgap=max(maxgap,gap)
   detail[bn]={"pair":vals,"gap_cp_abs":gap,"supported":supported}
  rows.append({"exposure_id":ex["exposure_id"],"family":ex["family"],"grammar":ex["grammar"],"supported":ok,
   "max_gap_cp_abs":maxgap if ok else None,"boards":detail})
 out={"schema":"c3x-g95-p18-exposure-qualification-v1","scientific_stage":STAGE,"phase":phase,"case_id":case["case_id"],
  "engine":case["engine"],"position_id":case["position_id"],"active":True,"exposure_support":rows,
  "search_event_outcomes_consulted":False,"edited_native_choice_consulted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P18_EXPOSUREQUAL",phase,case["case_id"],sum(z["supported"] for z in rows),"/",len(rows))

def development_ecology(a):
 pre=load_pool(a.freeze);found={}
 for p in Path(a.exposure_qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p18-exposure-qualification-v1" and x.get("phase")=="development":found[x["case_id"]]=x
 devcases=[x for x in pre["cases"] if x["split"]=="development"]
 if set(found)!={x["case_id"] for x in devcases}:raise SystemExit(f"P18_DEV_EXQ_N {len(found)}")
 supported=[]
 bycase={c["case_id"]:c for c in devcases}
 for cid,q in found.items():
  ok={z["exposure_id"]:z for z in q.get("exposure_support",[]) if z["supported"]}
  for ex in bycase[cid].get("candidate_exposures",[]):
   if ex["exposure_id"] in ok:supported.append({**ex,"edited_max_pair_gap_cp_abs":ok[ex["exposure_id"]]["max_gap_cp_abs"]})
 eligcfg=pre["development_rival_eligibility"];weights=pre["ecology_selection"]["matching_distance"];quota=int(pre["execution"]["max_confirmation_sets_per_engine_source"])
 chosen=None;audit={}
 for grammar in GRAMMARS:
  sg=[z for z in supported if z["grammar"]==grammar];stats={}
  for fam in FAMILIES:
   v=[z for z in sg if z["family"]==fam];stats[fam]={"supported":len(v),"engines":sorted({z["engine"] for z in v}),
    "sources":sorted({z["source_id"] for z in v}),"strata":len({(z["engine"],z["source_id"]) for z in v})}
  audit[grammar]=stats
  eligible=[f for f in FAMILIES if f!=H and stats[f]["supported"]>=int(eligcfg["min_supported_exposures"]) and
    len(stats[f]["engines"])>=int(eligcfg["min_engines"]) and len(stats[f]["sources"])>=2 and stats[f]["strata"]>=int(eligcfg["min_engine_source_strata"])]
  for n in pre["ecology_selection"]["rival_count_order"]:
   candidates=[]
   for rivals in itertools.combinations(sorted(eligible),int(n)):
    fams=(H,)+tuple(rivals);sets,_=greedy_sets(sg,fams,weights,quota,"p18:dev")
    if len(sets)<int(pre["ecology_selection"]["min_development_complete_sets"]):continue
    ham=sum(family_hamming(H,f) for f in rivals);floor=min(stats[f]["supported"] for f in fams)
    candidates.append((-len(sets),ham,-floor,tuple(rivals),sets))
   if candidates:
    candidates.sort(key=lambda z:(z[0],z[1],z[2],z[3]));_,_,_,rivals,sets=candidates[0]
    chosen={"selected_grammar":grammar,"rivals":list(rivals),"families":[H,*rivals],"development_complete_matched_sets":len(sets),
      "development_matched_sets":sets};break
  if chosen:break
 out={"schema":"c3x-g95-p18-development-ecology-v1","scientific_stage":STAGE,"status":"PASS" if chosen else "HOLD",
  "pair_pool_receipt_sha256":pre["receipt_sha256"],"development_bridge_outcomes_consulted":False,
  "edited_native_choice_consulted":False,"event_firing_consulted":False,"t_only_outcome_consulted":False,
  "supported_development_exposures":len(supported),"grammar_family_support":audit,
  "selected_grammar":chosen["selected_grammar"] if chosen else None,"rivals":chosen["rivals"] if chosen else [],
  "families":chosen["families"] if chosen else [H],"development_complete_matched_sets":chosen["development_complete_matched_sets"] if chosen else 0,
  "development_matched_sets":chosen["development_matched_sets"] if chosen else [],
  "matching_distance":weights,"confirmation_support_gate":pre["confirmation"]["support_gate"],"replication_rule":pre["replication_rule"],
  "claim_ceiling":pre["claim_ceiling"]}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P18_DEVELOPMENT_ECOLOGY",out["status"],out["selected_grammar"],out["rivals"],out["development_complete_matched_sets"])

def confirmation_freeze(a):
 pre=load_pool(a.freeze);eco=load_ecology(a.ecology);found={}
 for p in Path(a.exposure_qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p18-exposure-qualification-v1" and x.get("phase")=="confirmation":found[x["case_id"]]=x
 confcases=[x for x in pre["cases"] if x["split"]=="confirmation"]
 if set(found)!={x["case_id"] for x in confcases}:raise SystemExit(f"P18_CONF_EXQ_N {len(found)}")
 supported=[];bycase={c["case_id"]:c for c in confcases}
 if eco["status"]=="PASS":
  for cid,q in found.items():
   ok={z["exposure_id"]:z for z in q.get("exposure_support",[]) if z["supported"]}
   for ex in bycase[cid].get("candidate_exposures",[]):
    if ex["exposure_id"] in ok and ex["grammar"]==eco["selected_grammar"] and ex["family"] in eco["families"]:
     supported.append({**ex,"edited_max_pair_gap_cp_abs":ok[ex["exposure_id"]]["max_gap_cp_abs"]})
 sets,used=greedy_sets(supported,tuple(eco["families"]),eco["matching_distance"],int(pre["execution"]["max_confirmation_sets_per_engine_source"]),"p18:conf")
 selected=[z for z in supported if z["exposure_id"] in used];byid={z["exposure_id"]:z for z in selected};membership={}
 for st in sets:
  for fam,eid in st["arms"].items():membership[eid]={"matched_set_id":st["matched_set_id"],"family":fam}
 cases=[]
 for c in pre["cases"]:
  xs=[]
  if c["split"]=="confirmation":
   for ex in c.get("candidate_exposures",[]):
    if ex["exposure_id"] in membership:xs.append({**byid[ex["exposure_id"]],**membership[ex["exposure_id"]]})
  cases.append({**c,"selected_exposures":xs,"factorial_active":bool(xs)})
 counts=Counter(z["family"] for z in selected)
 out={"schema":"c3x-g95-p18-confirmation-freeze-v1","scientific_stage":STAGE,"status":"PASS" if eco["status"]=="PASS" else "DEVELOPMENT_HOLD",
  "development_ecology_receipt_sha256":eco["receipt_sha256"],"selected_grammar":eco["selected_grammar"],"families":eco["families"],"rivals":eco["rivals"],
  "search_event_outcomes_consulted":False,"edited_native_choice_consulted":False,
  "admitted_pair_positions":pre["admitted_pair_positions"]["confirmation"],"supported_confirmation_exposures":len(supported),
  "complete_matched_sets":len(sets),"selected_exposure_count":len(selected),"family_exposure_counts":dict(sorted(counts.items())),
  "active_engines":sorted({z["engine"] for z in selected}),"sources":sorted({z["source_id"] for z in selected}),
  "matched_sets":sets,"execution":pre["execution"],"support_gate":pre["confirmation"]["support_gate"],
  "exact_event_mediator":pre["exact_event_mediator"],"estimand":pre["estimand"],"replication_rule":pre["replication_rule"],
  "claim_ceiling":pre["claim_ceiling"],"variants":pre["variants"],"positions":pre["positions"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P18_CONFIRM_FREEZE",out["status"],"sets",len(sets),"families",dict(counts))

def factorial(a):
 pre=load_confirm(a.freeze);case=next(x for x in pre["cases"] if x["case_id"]==a.case_id);v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P18_BINARY")
 if not case["factorial_active"]:
  out={"schema":"c3x-g95-p18-factorial-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
   "position_id":case["position_id"],"split":case["split"],"source_id":case["source_id"],"active":False,"exposures":[],"address_misses":[]}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");return
 pos=case["position_pair"];A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"];pref=case["engine_view"]["baseline_preferred"];anchor=B if pref==A else A
 root=Path(a.out).parent/".p18-factorial";root.mkdir(parents=True,exist_ok=True)
 b0=p15.run_board_cell(a.binary,v["protocol"],case["cell"],case["cell"]["fen"],A,B,anchor,root,"B0",int(pre["execution"]["max_semantic_targets_per_board"]))
 if b0["native"].get("bestmove")!=pref:raise SystemExit("P18_B0_DRIFT")
 worlds=[];misses=[{"exposure":"B0","board":"B0",**m} for m in b0["address_misses"]]
 for i,ex in enumerate(case["selected_exposures"]):
  target=p15.run_board_cell(a.binary,v["protocol"],case["cell"],ex["chain"]["target"]["fen"],A,B,anchor,root,f"E{i}-T",int(pre["execution"]["max_semantic_targets_per_board"]))
  sham=p15.run_board_cell(a.binary,v["protocol"],case["cell"],ex["chain"]["sham"]["fen"],A,B,anchor,root,f"E{i}-S",int(pre["execution"]["max_semantic_targets_per_board"]))
  misses += [{"exposure":ex["exposure_id"],"board":"TARGET",**m} for m in target["address_misses"]]
  misses += [{"exposure":ex["exposure_id"],"board":"SHAM",**m} for m in sham["address_misses"]]
  br=[];mods=[]
  for bound in ("LOWER","UPPER"):
   z=p16.bridge(b0,target,sham,bound,A,B)
   if z:br.append({**z,"kind":"ATOMIC_FULL_BRIDGE","family":ex["family"],"matched_set_id":ex["matched_set_id"],"bound":bound})
   s0=b0["bounds"][bound]["state"];st=target["bounds"][bound]["state"]
   if s0!=st:mods.append({"kind":"SUSCEPTIBILITY_MODULATION","family":ex["family"],"bound":bound,"original_state":s0,"target_state":st})
  worlds.append({"exposure_id":ex["exposure_id"],"matched_set_id":ex["matched_set_id"],"family":ex["family"],
    "target":ex["chain"]["target"],"sham":ex["chain"]["sham"],"bridge_records":br,"susceptibility_records":mods,
    "boards":{"B0":b0,"TARGET":target,"SHAM":sham}})
 out={"schema":"c3x-g95-p18-factorial-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"split":case["split"],"source_id":case["source_id"],"active":True,"pair":pos["pair"],
  "exposures":worlds,"address_misses":misses,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P18_FACTORIAL",case["case_id"],"exposures",len(worlds),"lower",sum(r["bound"]=="LOWER" for w in worlds for r in w["bridge_records"]))

def adjudicate(a):
 pre=load_confirm(a.freeze);eco=load_ecology(a.ecology);worlds=[]
 for p in Path(a.worlds).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p18-factorial-world-v1":worlds.append(x)
 if len(worlds)!=288:raise SystemExit(f"P18_WORLD_N {len(worlds)}")
 active=[w for w in worlds if w["active"]];misses=sum(len(w["address_misses"]) for w in worlds);engines=sorted({w["engine"] for w in active});sources=sorted({w["source_id"] for w in active})
 rows=[];mods=[];fired=0
 for w in active:
  anyfire=False
  for ew in w["exposures"]:
   for bd in ew["boards"].values():
    if any(q["record"] for q in bd["bounds"].values()):anyfire=True
   for r in ew["bridge_records"]:rows.append({"engine":w["engine"],"position_id":w["position_id"],"source_id":w["source_id"],
    "pair_id":w["pair"]["pair_id"],"exposure_id":ew["exposure_id"],"physical_edit_id":ew["target"]["edit_id"],**r})
   for r in ew["susceptibility_records"]:mods.append({"engine":w["engine"],"position_id":w["position_id"],"source_id":w["source_id"],"exposure_id":ew["exposure_id"],**r})
  fired+=int(anyfire)
 fams=pre["families"];counts={f:int(pre["family_exposure_counts"].get(f,0)) for f in fams};gate=pre["support_gate"];equal=len(set(counts.values()))<=1
 support=(pre["status"]=="PASS" and pre["complete_matched_sets"]>=gate["min_complete_matched_sets"] and len(engines)>=gate["min_active_engines"] and
  len(sources)>=gate["min_sources"] and (equal or not gate["require_equal_family_exposure_counts"]) and fired>=gate["min_worlds_with_any_fired_semantic_target"] and misses<=gate["max_address_misses"])
 lower=[r for r in rows if r["bound"]=="LOWER"];upper=[r for r in rows if r["bound"]=="UPPER"];req=pre["replication_rule"]["per_family_lower_requires"]
 def rep(f):
  v=[r for r in lower if r["family"]==f]
  ok=(len(v)>=req["witnesses"] and len({x["engine"] for x in v})>=req["engines"] and len({x["position_id"] for x in v})>=req["positions"] and
   len({x["source_id"] for x in v})>=req["sources"] and len({x["physical_edit_id"] for x in v})>=req["distinct_physical_edits"])
  return {"replicated":ok,"witnesses":len(v),"engines":sorted({x["engine"] for x in v}),"positions":len({x["position_id"] for x in v}),
   "sources":sorted({x["source_id"] for x in v}),"physical_edits":len({x["physical_edit_id"] for x in v})}
 reps={f:rep(f) for f in fams};rivals=[f for f in fams if f!=H];rrep=[f for f in rivals if reps[f]["replicated"]]
 lc=Counter(r["family"] for r in lower);uc=Counter(r["family"] for r in upper);maxr=max([lc[f] for f in rivals] or [0]);adv=lc[H]-maxr
 if eco["status"]!="PASS":verdict="P18_DEVELOPMENT_ECOLOGY_HOLD"
 elif not support:verdict="P18_CONFIRMATION_SUPPORT_HOLD"
 elif reps[H]["replicated"] and not rrep and adv>=int(pre["replication_rule"]["H_advantage_over_strongest_rival"]):verdict="P18_HYPOTHESIS_SURVIVES_SUPPORT_REALIZED_FATAL_REPLICATION"
 elif rrep:verdict="P18_RIVAL_REPLICATES_HYPOTHESIS_DEFEATED"
 elif reps[H]["replicated"]:verdict="P18_HYPOTHESIS_REPLICATES_BUT_NOT_SPECIFIC"
 else:verdict="P18_HYPOTHESIS_FAILS_WITH_ADEQUATE_SUPPORT"
 stats={f:{"exposures":counts[f],"lower_full_bridges":lc[f],"upper_full_bridges":uc[f],"lower_replication":reps[f]} for f in fams}
 certs=[]
 for r in rows:
  certs.append({"schema":"c3x-causal-contrast-certificate-v1","provenance_class":"C3X_CAUSAL_CONTRAST",
   "certificate_id":hashlib.sha256((r["engine"]+"|"+r["position_id"]+"|"+r["exposure_id"]+"|"+r["bound"]).encode()).hexdigest()[:24],
   "engine":r["engine"],"position_id":r["position_id"],"source_id":r["source_id"],"pair_id":r["pair_id"],"family":r["family"],
   "physical_edit_id":r["physical_edit_id"],"bound":r["bound"],"collapse_to":r["collapse_to"],"sham_reproduced":r["sham_reproduced"],
   "concept_label":None,"replication_status":"P18_PRIMARY_REPLICATED_FAMILY_MEMBER" if r["family"]==H and r["bound"]=="LOWER" and reps[H]["replicated"] else "LOCAL_ONLY",
   "authority_ceiling":pre["claim_ceiling"]})
 out={"schema":"c3x-g95-p18-adjudication-v1","scientific_stage":STAGE,"status":"CLOSED_PASS" if support else "HOLD","verdict":verdict,
  "development_ecology":{"receipt_sha256":eco["receipt_sha256"],"selected_grammar":eco["selected_grammar"],"families":eco["families"],
   "rivals":eco["rivals"],"development_complete_matched_sets":eco["development_complete_matched_sets"]},
  "confirmation_support":{"pass":support,"admitted_pair_positions":pre["admitted_pair_positions"],"complete_matched_sets":pre["complete_matched_sets"],
   "selected_exposure_count":pre["selected_exposure_count"],"family_exposure_counts":counts,"active_engines":engines,"sources":sources,
   "worlds_with_any_fired_semantic_target":fired,"address_misses":misses},
  "family_statistics":stats,"h_lower_advantage_over_strongest_rival":adv,"replicated_rival_families":rrep,"primary_hypothesis_replication":reps.get(H),
  "lower_full_bridge_records":len(lower),"upper_diagnostic_full_bridge_records":len(upper),"susceptibility_modulation_records":len(mods),
  "bridge_records":rows,"causal_explanation_certificates":certs,"upper_is_diagnostic_only":True,"claim_ceiling":pre["claim_ceiling"],"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 lines=["# C3X G9.5-P18 — Falsifier-Ecology Reconstitution & Fatal Replication","",f"**{out['status']} / {verdict}**",
  f"Development grammar: **{eco['selected_grammar']}**; rivals: **{', '.join(eco['rivals']) or 'none'}**; dev matched sets: **{eco['development_complete_matched_sets']}**.",
  f"Confirmation matched sets: **{pre['complete_matched_sets']}**; H LOWER bridges: **{lc[H]}**; strongest rival: **{maxr}**; advantage: **{adv}**.","","## Family results"]
 for f in fams:lines.append(f"- {f}: {lc[f]}/{counts[f]} LOWER bridges; replicated={reps[f]['replicated']}; engines={','.join(reps[f]['engines'])}; positions={reps[f]['positions']}.")
 lines+=["","UPPER is diagnostic-only. Development used no bridge/search-response outcome. Track-B commentary quality cannot change this verdict."]
 Path(a.markdown).write_text("\n".join(lines)+"\n")
 print("P18_ADJUDICATE",verdict,"support",support,"H_lower",lc[H],"max_rival",maxr,"rivals",rrep)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("design");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p17-closure",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=design)
 q=sp.add_parser("qualify");q.add_argument("--design",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=qualify)
 q=sp.add_parser("pair-pool-freeze");q.add_argument("--design",required=True);q.add_argument("--qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=pair_pool_freeze)
 q=sp.add_parser("exposure-qualify");q.add_argument("--freeze",required=True);q.add_argument("--phase",choices=["development","confirmation"],required=True);q.add_argument("--ecology");q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=exposure_qualify)
 q=sp.add_parser("development-ecology");q.add_argument("--freeze",required=True);q.add_argument("--exposure-qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=development_ecology)
 q=sp.add_parser("confirmation-freeze");q.add_argument("--freeze",required=True);q.add_argument("--ecology",required=True);q.add_argument("--exposure-qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=confirmation_freeze)
 q=sp.add_parser("factorial");q.add_argument("--freeze",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=factorial)
 q=sp.add_parser("adjudicate");q.add_argument("--freeze",required=True);q.add_argument("--ecology",required=True);q.add_argument("--worlds",required=True);q.add_argument("--out",required=True);q.add_argument("--markdown",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
