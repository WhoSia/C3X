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

STAGE="C3X 0.7.0-G9.5-P17"
ENGINES=("stockfish_19","berserk","ethereal")
FAMILIES=("H","R_GAIN","R_PREF","R_SIDE","R_ENDPOINT")
RIVALS=("R_GAIN","R_PREF","R_SIDE","R_ENDPOINT")
FAMILY_SPEC={
 "H":("OWN",("DISPREFERRED_FROM_LOSS",)),
 "R_GAIN":("OWN",("DISPREFERRED_FROM_GAIN",)),
 "R_PREF":("OWN",("PREFERRED_FROM_LOSS",)),
 "R_SIDE":("OPPONENT",("DISPREFERRED_FROM_LOSS",)),
 "R_ENDPOINT":("OWN",("DISPREFERRED_TO_LOSS",)),
}

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
def gap_band(n):return p13.gap_band(abs(int(n)))

def load_design(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p17-design-precommit-v1" or x.get("intervention_outcomes_consulted") is not False:raise SystemExit("P17_DESIGN")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P17_DESIGN_HASH")
 return x

def load_pair(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p17-pair-pool-freeze-v1":raise SystemExit("P17_PAIR_POOL")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P17_PAIR_POOL_HASH")
 return x

def load_exposure(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p17-exposure-freeze-v1":raise SystemExit("P17_EXPOSURE_FREEZE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P17_EXPOSURE_HASH")
 return x

def family_for(side,eatoms):
 key=(side,tuple(sorted(eatoms)))
 for fam,spec in FAMILY_SPEC.items():
  if key==spec:return fam
 return None

def atomic_chains(fen,A,B,cfg):
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
   if ld>int(cfg["max_abs_legal_root_move_count_delta"]) or ad>int(cfg["max_moved_piece_attack_set_symmetric_difference"]):continue
   edits.append(p16.edit_doc(b,fr,to,endpoints))
 groups=defaultdict(list)
 for e in edits:groups[(e["from"],e["piece_color"],e["piece_type"],e["distance"])].append(e)
 out=[]
 for _,rows in sorted(groups.items()):
  shams=sorted([x for x in rows if len(x["atoms"])==0],
    key=lambda x:(abs(x["legal_move_count_delta"]),x["attack_set_symmetric_difference"],x["edit_id"]))
  if not shams:continue
  sham=shams[0]
  for t in sorted([x for x in rows if len(x["atoms"])==1],
    key=lambda x:(abs(x["legal_move_count_delta"]),x["attack_set_symmetric_difference"],x["edit_id"])):
   out.append({"chain_id":t["edit_id"]+"::SHAM::"+sham["edit_id"],"chain_type":"ATOMIC_CHAIN",
    "target":t,"sham":sham,"target_atom_count":1})
 return out

def candidate_sort(ex):
 t=ex["chain"]["target"]
 return (abs(t["legal_move_count_delta"]),t["attack_set_symmetric_difference"],t["distance"],
  t["piece_type"],ex["position_id"],t["edit_id"],ex["chain"]["sham"]["edit_id"],ex["exposure_id"])

def design(a):
 c=load(a.constitution);corp=load(a.corpus);parent=load(a.p16_closure)
 if c.get("schema")!="c3x-g95-p17-constitution-v1":raise SystemExit("P17_CONSTITUTION")
 if parent.get("receipt_sha256")!=c["parent"]["closure_receipt_sha256"]:raise SystemExit("P17_PARENT")
 if corp.get("schema")!="c3x-g95-p17-corpus-v1" or corp["selection"]["intervention_outcomes_consulted"] is not False:raise SystemExit("P17_CORPUS")
 builds=Path(a.build_dir);variants={}
 for e in ENGINES:
  fs=list(builds.rglob(f"c3x-p17-{e}"))
  if len(fs)!=1:raise SystemExit(f"P17_BUILD {e} {len(fs)}")
  variants[e]={"sha256":sha_file(fs[0]),"protocol":p32.protocol_for(e)}
 cases=[]
 for pos in corp["positions"]:
  for e in ENGINES:
   cases.append({"case_id":f'p17:{e}:{pos["position_id"]}',"engine":e,"position_id":pos["position_id"],
    "source_id":pos["source_id"],"source_ply":pos["source_ply"],"candidate_sha256":pos["candidate_sha256"],
    "complexity":pos["complexity"],"cell":pos["cell"]})
 if len(cases)!=216:raise SystemExit("P17_CASE_COUNT")
 out={"schema":"c3x-g95-p17-design-precommit-v1","scientific_stage":STAGE,"intervention_outcomes_consulted":False,
  "constitution_sha256":digest(c),"corpus_sha256":digest(corp),"parent_p16_receipt_sha256":parent["receipt_sha256"],
  "variants":variants,"execution":c["execution"],"unordered_pair_constitution":c["unordered_pair_constitution"],
  "board_intervention_family":c["board_intervention_family"],"family_classification":c["family_classification"],
  "prequalification_pool":c["prequalification_pool"],"edited_pair_marginality":c["edited_pair_marginality"],
  "matched_sets":c["matched_sets"],"exact_event_mediator":c["exact_event_mediator"],"estimand":c["estimand"],
  "replication_rule":c["replication_rule"],"specificity_rule":c["specificity_rule"],"support_gate":c["support_gate"],
  "frozen_hypothesis":c["frozen_hypothesis"],"rival_families":c["rival_families"],
  "claim_ceiling":c["claim_ceiling"],"forbidden":c["forbidden"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P17_DESIGN_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def qualify(a):
 pre=load_design(a.design);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P17_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P17_BINARY")
 ex=pre["execution"];fen=case["cell"]["fen"];board=chess.Board(fen)
 root=Path(a.out).parent/".p17-qual-private";root.mkdir(parents=True,exist_ok=True)
 base=p13.run_context(a.binary,v["protocol"],case["cell"],"CATALOG",None,root/"base")
 legal=sorted(m.uci() for m in board.legal_moves);shallow=[]
 for i,m in enumerate(legal):
  r=p13.run_forced(a.binary,v["protocol"],fen,m,int(ex["shallow_legal_move_nodes"]),root/"shallow",f"{i:02d}")
  s=r["semantic"].get("score");shallow.append({"uci":m,"move":p13.move_doc(fen,m),"rank_value":p13.rank_value(s)})
 shortlist=sorted(shallow,key=lambda z:(-z["rank_value"],z["uci"]))[:int(ex["shortlist_size"])]
 qshort=[]
 for i,z in enumerate(shortlist):
  vals=[]
  for rep in range(int(ex["isolated_confirm_repeats"])):
   r=p13.run_forced(a.binary,v["protocol"],fen,z["uci"],int(ex["isolated_confirm_nodes"]),root/"confirm",f"{i:02d}-{rep}")
   vals.append(r["semantic"].get("score"))
  cps=[p13.score_cp(s) for s in vals];stable=len(cps)==2 and None not in cps and cps[0]==cps[1]
  qshort.append({"move":z["move"],"confirm_scores":vals,"stable":stable,"confirm_cp":cps[0] if stable else None})
 out={"schema":"c3x-g95-p17-engine-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"source_id":case["source_id"],"source_ply":case["source_ply"],"candidate_sha256":case["candidate_sha256"],
  "baseline":{k:base["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")},
  "shortlist":qshort,"intervention_outcomes_consulted":False,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P17_QUALIFY",case["case_id"],"stable",sum(z["stable"] for z in qshort),"baseline",out["baseline"]["bestmove"])

def pair_pool_freeze(a):
 pre=load_design(a.design);found={}
 for p in Path(a.qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p17-engine-qualification-v1":found[x["case_id"]]=x
 if set(found)!={x["case_id"] for x in pre["cases"]}:raise SystemExit(f"P17_QUAL_N {len(found)}")
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
    if A in s and B in s and abs(s[A]-s[B])<=50 and bm in (A,B):
     support.append({"engine":c["engine"],"gap_cp_abs":abs(s[A]-s[B]),"baseline_preferred":bm})
   if len(support)>=2:
    gs=[x["gap_cp_abs"] for x in support]
    cand.append({"pair_id":pair_id(A,B),"moves":[A,B],"support_count":len(support),
      "median_gap_cp":float(statistics.median(gs)),"max_gap_cp":max(gs)})
  cand.sort(key=lambda z:(-z["support_count"],z["median_gap_cp"],z["max_gap_cp"],z["pair_id"]))
  c0,q0=rows[0];fen=c0["cell"]["fen"]
  if not cand:
   positions[pid]={"position_id":pid,"source_id":c0["source_id"],"admitted":False,"pair":None,"engine_views":{},"atomic_chains":[]};continue
  sel=cand[0];A,B=sel["moves"];views={}
  for c,q in rows:
   s=stable[c["engine"]];bm=q["baseline"].get("bestmove");both=A in s and B in s
   gap=None if not both else abs(s[A]-s[B]);active=bool(both and gap<=50 and bm in (A,B))
   if active:active_worlds+=1
   views[c["engine"]]={"active":active,"baseline_preferred":bm if active else None,"A_cp":s.get(A),"B_cp":s.get(B),
    "gap_cp_abs":gap,"gap_band":gap_band(gap) if active else None}
  chains=atomic_chains(fen,A,B,pre["board_intervention_family"])
  positions[pid]={"position_id":pid,"source_id":c0["source_id"],"source_ply":c0["source_ply"],"candidate_sha256":c0["candidate_sha256"],
   "admitted":True,"pair":{"pair_id":sel["pair_id"],"A":p13.move_doc(fen,A),"B":p13.move_doc(fen,B),
    "support_count":sel["support_count"],"median_gap_cp":sel["median_gap_cp"],"max_gap_cp":sel["max_gap_cp"]},
   "engine_views":views,"atomic_chains":chains}
 all_exposures=[]
 cases=[]
 maxpw=int(pre["execution"]["max_atomic_candidates_per_family_per_world"])
 for c in pre["cases"]:
  pos=positions[c["position_id"]];view=pos["engine_views"].get(c["engine"],{})
  exposures=[]
  if pos.get("admitted") and view.get("active"):
   A=pos["pair"]["A"]["uci"];pref=view["baseline_preferred"];turn=chess.Board(c["cell"]["fen"]).turn
   for ch in pos["atomic_chains"]:
    eat=p16.engine_atoms(ch["target"]["atoms"],A,pref)
    side="OWN" if ch["target"]["piece_color"]==("WHITE" if turn else "BLACK") else "OPPONENT"
    fam=family_for(side,eat)
    if fam is None:continue
    ex={"exposure_id":c["case_id"]+"::"+ch["chain_id"],"case_id":c["case_id"],"engine":c["engine"],
      "source_id":c["source_id"],"position_id":c["position_id"],"family":fam,"moved_side_role":side,
      "engine_relative_atoms":eat,"original_pair_gap_cp_abs":view["gap_cp_abs"],"chain":ch}
    exposures.append(ex)
   keep=[]
   for fam in FAMILIES:
    xs=sorted([z for z in exposures if z["family"]==fam],key=candidate_sort)[:maxpw];keep+=xs
   exposures=keep
  cases.append({**c,"position_pair":pos,"engine_view":view,"qualification":found[c["case_id"]],"all_family_exposures":exposures})
  all_exposures+=exposures
 quota=int(pre["prequalification_pool"]["quota"]);pool_ids=set();pool_counts={}
 for e in ENGINES:
  for src in sorted({c["source_id"] for c in pre["cases"]}):
   for fam in FAMILIES:
    xs=sorted([z for z in all_exposures if z["engine"]==e and z["source_id"]==src and z["family"]==fam],key=candidate_sort)[:quota]
    pool_ids.update(z["exposure_id"] for z in xs);pool_counts[f"{e}|{src}|{fam}"]=len(xs)
 for c in cases:c["candidate_exposures"]=[z for z in c["all_family_exposures"] if z["exposure_id"] in pool_ids]
 out={"schema":"c3x-g95-p17-pair-pool-freeze-v1","scientific_stage":STAGE,"design_receipt_sha256":pre["receipt_sha256"],
  "intervention_outcomes_consulted":False,"edited_native_choice_consulted":False,
  "admitted_pair_positions":sum(z["admitted"] for z in positions.values()),"active_original_engine_worlds":active_worlds,
  "candidate_pool_exposures":len(pool_ids),"candidate_pool_counts":dict(sorted(pool_counts.items())),
  "execution":pre["execution"],"edited_pair_marginality":pre["edited_pair_marginality"],"matched_sets":pre["matched_sets"],
  "exact_event_mediator":pre["exact_event_mediator"],"estimand":pre["estimand"],"replication_rule":pre["replication_rule"],
  "specificity_rule":pre["specificity_rule"],"support_gate":pre["support_gate"],"claim_ceiling":pre["claim_ceiling"],
  "variants":pre["variants"],"positions":positions,"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P17_PAIR_POOL_FREEZE",out["receipt_sha256"],"pairs",out["admitted_pair_positions"],"pool",len(pool_ids))

def exposure_qualify(a):
 pre=load_pair(a.freeze);case=next(x for x in pre["cases"] if x["case_id"]==a.case_id)
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P17_BINARY")
 if not case.get("candidate_exposures"):
  out={"schema":"c3x-g95-p17-exposure-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
   "position_id":case["position_id"],"active":False,"exposure_support":[],"search_event_outcomes_consulted":False,"edited_native_choice_consulted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P17_EXPOSUREQUAL_SKIP",case["case_id"]);return
 pos=case["position_pair"];A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"]
 root=Path(a.out).parent/".p17-exposurequal-private";root.mkdir(parents=True,exist_ok=True)
 rows=[];nodes=int(pre["execution"]["exposure_pair_confirm_nodes"]);reps=int(pre["execution"]["exposure_pair_confirm_repeats"])
 for i,ex in enumerate(case["candidate_exposures"]):
  detail={};ok=True;maxgap=0
  for bn,key in (("TARGET","target"),("SHAM","sham")):
   fen=ex["chain"][key]["fen"];vals={}
   for mi,m in enumerate((A,B)):
    scores=[]
    for rep in range(reps):
     r=p13.run_forced(a.binary,v["protocol"],fen,m,nodes,root/f"{i:02d}-{bn}",f"{mi}-{rep}")
     scores.append(r["semantic"].get("score"))
    cps=[p13.score_cp(s) for s in scores];stable=len(cps)==reps and None not in cps and len(set(cps))==1
    vals[m]={"stable":stable,"cp":cps[0] if stable else None}
   gap=None if not all(vals[m]["stable"] for m in (A,B)) else abs(vals[A]["cp"]-vals[B]["cp"])
   legal=A in {x.uci() for x in chess.Board(fen).legal_moves} and B in {x.uci() for x in chess.Board(fen).legal_moves}
   supported=bool(legal and gap is not None and gap<=int(pre["edited_pair_marginality"]["pair_gap_max_abs_cp"]))
   ok=ok and supported
   if gap is not None:maxgap=max(maxgap,gap)
   detail[bn]={"pair":vals,"gap_cp_abs":gap,"supported":supported}
  rows.append({"exposure_id":ex["exposure_id"],"family":ex["family"],"supported":ok,"max_gap_cp_abs":maxgap if ok else None,"boards":detail})
 out={"schema":"c3x-g95-p17-exposure-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"active":True,"exposure_support":rows,
  "search_event_outcomes_consulted":False,"edited_native_choice_consulted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P17_EXPOSUREQUAL",case["case_id"],"supported",sum(z["supported"] for z in rows),"/",len(rows))

def match_distance(a,b,w):
 ta=a["chain"]["target"];tb=b["chain"]["target"]
 return (w["piece_type_mismatch"]*(ta["piece_type"]!=tb["piece_type"]) +
  w["relocation_distance_abs_diff"]*abs(ta["distance"]-tb["distance"]) +
  w["legal_root_delta_abs_diff"]*abs(abs(ta["legal_move_count_delta"])-abs(tb["legal_move_count_delta"])) +
  w["attack_symdiff_abs_diff"]*abs(ta["attack_set_symmetric_difference"]-tb["attack_set_symmetric_difference"]) +
  w["original_pair_gap_abs_diff"]*abs(a["original_pair_gap_cp_abs"]-b["original_pair_gap_cp_abs"]) +
  w["edited_max_pair_gap_abs_diff"]*abs(a["edited_max_pair_gap_cp_abs"]-b["edited_max_pair_gap_cp_abs"]))

def exposure_freeze(a):
 pre=load_pair(a.freeze);found={}
 for p in Path(a.exposure_qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p17-exposure-qualification-v1":found[x["case_id"]]=x
 if set(found)!={x["case_id"] for x in pre["cases"]}:raise SystemExit("P17_EXPOSUREQUAL_N")
 supported=[]
 for c in pre["cases"]:
  q={z["exposure_id"]:z for z in found[c["case_id"]].get("exposure_support",[]) if z["supported"]}
  for ex in c.get("candidate_exposures",[]):
   if ex["exposure_id"] in q:
    supported.append({**ex,"edited_max_pair_gap_cp_abs":q[ex["exposure_id"]]["max_gap_cp_abs"]})
 weights=pre["matched_sets"]["distance_components"];quota=int(pre["matched_sets"]["max_sets_per_engine_source"])
 sets=[];used=set()
 for e in ENGINES:
  for src in sorted({c["source_id"] for c in pre["cases"]}):
   cell=[z for z in supported if z["engine"]==e and z["source_id"]==src]
   chosen=0
   while chosen<quota:
    hs=[z for z in cell if z["family"]=="H" and z["exposure_id"] not in used]
    proposals=[]
    for h in hs:
     arms={"H":h};cost=0.0;ok=True
     for fam in RIVALS:
      xs=[z for z in cell if z["family"]==fam and z["exposure_id"] not in used]
      if not xs:ok=False;break
      xs.sort(key=lambda z:(match_distance(h,z,weights),z["exposure_id"]))
      arms[fam]=xs[0];cost+=match_distance(h,xs[0],weights)
     if ok:proposals.append((cost,h["exposure_id"],arms))
    if not proposals:break
    proposals.sort(key=lambda z:(z[0],z[1]));cost,_,arms=proposals[0]
    sid=f"p17:set:{e}:{src}:{chosen}"
    sets.append({"matched_set_id":sid,"engine":e,"source_id":src,"total_match_distance":cost,
      "arms":{fam:arms[fam]["exposure_id"] for fam in FAMILIES}})
    used.update(z["exposure_id"] for z in arms.values());chosen+=1
 selected=[z for z in supported if z["exposure_id"] in used];byid={z["exposure_id"]:z for z in selected}
 membership={}
 for st in sets:
  for fam,eid in st["arms"].items():membership[eid]={"matched_set_id":st["matched_set_id"],"family":fam}
 family_counts=Counter(z["family"] for z in selected)
 cases=[]
 for c in pre["cases"]:
  xs=[]
  for ex in c.get("candidate_exposures",[]):
   if ex["exposure_id"] in membership:
    xs.append({**byid[ex["exposure_id"]],**membership[ex["exposure_id"]]})
  cases.append({**c,"selected_exposures":xs,"factorial_active":bool(xs),"exposure_qualification":found[c["case_id"]]})
 out={"schema":"c3x-g95-p17-exposure-freeze-v1","scientific_stage":STAGE,"pair_pool_receipt_sha256":pre["receipt_sha256"],
  "search_event_outcomes_consulted":False,"edited_native_choice_consulted":False,
  "admitted_pair_positions":pre["admitted_pair_positions"],"supported_candidate_exposures":len(supported),
  "complete_matched_sets":len(sets),"selected_exposure_count":len(selected),
  "family_exposure_counts":dict(sorted(family_counts.items())),
  "active_engines":sorted({z["engine"] for z in selected}),"sources":sorted({z["source_id"] for z in selected}),
  "matched_sets":sets,"execution":pre["execution"],"exact_event_mediator":pre["exact_event_mediator"],
  "estimand":pre["estimand"],"replication_rule":pre["replication_rule"],"specificity_rule":pre["specificity_rule"],
  "support_gate":pre["support_gate"],"claim_ceiling":pre["claim_ceiling"],"variants":pre["variants"],
  "positions":pre["positions"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P17_EXPOSURE_FREEZE",out["receipt_sha256"],"sets",len(sets),"exposures",len(selected),"families",dict(family_counts))

def factorial(a):
 pre=load_exposure(a.freeze);case=next(x for x in pre["cases"] if x["case_id"]==a.case_id)
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P17_BINARY")
 if not case["factorial_active"]:
  out={"schema":"c3x-g95-p17-factorial-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
   "position_id":case["position_id"],"source_id":case["source_id"],"active":False,"exposures":[],"address_misses":[],"raw_tt_key_emitted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P17_FACTORIAL_SKIP",case["case_id"]);return
 pos=case["position_pair"];A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"];pref=case["engine_view"]["baseline_preferred"];anchor=B if pref==A else A
 root=Path(a.out).parent/".p17-factorial-private";root.mkdir(parents=True,exist_ok=True)
 b0=p15.run_board_cell(a.binary,v["protocol"],case["cell"],case["cell"]["fen"],A,B,anchor,root,"B0",int(pre["execution"]["max_semantic_targets_per_board"]))
 if b0["native"].get("bestmove")!=pref:raise SystemExit("P17_B0_DRIFT")
 worlds=[];misses=[{"exposure":"B0","board":"B0",**m} for m in b0["address_misses"]]
 for i,ex in enumerate(case["selected_exposures"]):
  target=p15.run_board_cell(a.binary,v["protocol"],case["cell"],ex["chain"]["target"]["fen"],A,B,anchor,root,f"E{i}-TARGET",int(pre["execution"]["max_semantic_targets_per_board"]))
  sham=p15.run_board_cell(a.binary,v["protocol"],case["cell"],ex["chain"]["sham"]["fen"],A,B,anchor,root,f"E{i}-SHAM",int(pre["execution"]["max_semantic_targets_per_board"]))
  misses += [{"exposure":ex["exposure_id"],"board":"TARGET",**m} for m in target["address_misses"]]
  misses += [{"exposure":ex["exposure_id"],"board":"SHAM",**m} for m in sham["address_misses"]]
  br=[];mods=[]
  for bound in ("LOWER","UPPER"):
   z=p16.bridge(b0,target,sham,bound,A,B)
   if z:
    br.append({**z,"kind":"MINIMAL_FULL_BRIDGE","family":ex["family"],"matched_set_id":ex["matched_set_id"],
      "moved_side_role":ex["moved_side_role"],"engine_relative_atoms":ex["engine_relative_atoms"],
      "exact_signature":"|".join([ex["family"],ex["moved_side_role"],"+".join(ex["engine_relative_atoms"]),bound,"MINIMAL_FULL_BRIDGE"])})
   s0=b0["bounds"][bound]["state"];st=target["bounds"][bound]["state"]
   if s0!=st:mods.append({"kind":"SUSCEPTIBILITY_MODULATION","family":ex["family"],"bound":bound,"original_state":s0,"target_state":st})
  worlds.append({"exposure_id":ex["exposure_id"],"matched_set_id":ex["matched_set_id"],"family":ex["family"],
    "target":ex["chain"]["target"],"sham":ex["chain"]["sham"],"moved_side_role":ex["moved_side_role"],
    "engine_relative_atoms":ex["engine_relative_atoms"],"bridge_records":br,"susceptibility_records":mods,
    "boards":{"B0":b0,"TARGET":target,"SHAM":sham}})
 out={"schema":"c3x-g95-p17-factorial-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"source_id":case["source_id"],"active":True,"pair":pos["pair"],"exposures":worlds,
  "address_misses":misses,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P17_FACTORIAL",case["case_id"],"exposures",len(worlds),"lower_minimal",sum(r["bound"]=="LOWER" for w in worlds for r in w["bridge_records"]),"miss",len(misses))

def adjudicate(a):
 pre=load_exposure(a.freeze);worlds=[]
 for p in Path(a.worlds).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p17-factorial-world-v1":worlds.append(x)
 if len(worlds)!=216:raise SystemExit(f"P17_WORLD_N {len(worlds)}")
 active=[w for w in worlds if w["active"]];misses=sum(len(w["address_misses"]) for w in worlds)
 engines=sorted({w["engine"] for w in active});sources=sorted({w["source_id"] for w in active})
 rows=[];mods=[];fired_worlds=0
 for w in active:
  anyfire=False
  for ew in w["exposures"]:
   for bd in ew["boards"].values():
    if any(q["record"] for q in bd["bounds"].values()):anyfire=True
   for r in ew["bridge_records"]:
    rows.append({"engine":w["engine"],"position_id":w["position_id"],"source_id":w["source_id"],"pair_id":w["pair"]["pair_id"],
      "exposure_id":ew["exposure_id"],"physical_edit_id":ew["target"]["edit_id"],**r})
   for r in ew["susceptibility_records"]:
    mods.append({"engine":w["engine"],"position_id":w["position_id"],"source_id":w["source_id"],"exposure_id":ew["exposure_id"],**r})
  fired_worlds+=int(anyfire)
 famcounts={f:int(pre["family_exposure_counts"].get(f,0)) for f in FAMILIES}
 gate=pre["support_gate"];equal=len(set(famcounts.values()))==1
 support=(pre["admitted_pair_positions"]>=gate["min_admitted_pair_positions"] and pre["complete_matched_sets"]>=gate["min_complete_matched_sets"] and
  len(engines)>=gate["min_active_engines"] and len(sources)>=gate["min_sources"] and famcounts["H"]>=gate["min_h_exposures"] and
  (equal or not gate["require_equal_family_exposure_counts"]) and fired_worlds>=gate["min_worlds_with_any_fired_semantic_target"] and
  misses<=gate["max_address_misses"])
 lower=[r for r in rows if r["bound"]=="LOWER"];upper=[r for r in rows if r["bound"]=="UPPER"]
 req=pre["replication_rule"]["per_family_lower_requires"]
 def replication(fam):
  v=[r for r in lower if r["family"]==fam]
  ok=(len(v)>=req["witnesses"] and len({x["engine"] for x in v})>=req["engines"] and
   len({x["position_id"] for x in v})>=req["positions"] and len({x["source_id"] for x in v})>=req["sources"] and
   len({x["physical_edit_id"] for x in v})>=req["distinct_physical_edits"])
  return {"family":fam,"replicated":ok,"witnesses":len(v),"engines":sorted({x["engine"] for x in v}),
   "positions":len({x["position_id"] for x in v}),"sources":sorted({x["source_id"] for x in v}),
   "physical_edits":len({x["physical_edit_id"] for x in v})}
 reps={fam:replication(fam) for fam in FAMILIES};hrep=reps["H"]["replicated"];rrep=[f for f in RIVALS if reps[f]["replicated"]]
 lower_counts=Counter(r["family"] for r in lower);upper_counts=Counter(r["family"] for r in upper)
 max_rival=max([lower_counts[f] for f in RIVALS] or [0]);adv=lower_counts["H"]-max_rival
 if not support:verdict="P17_EXPOSURE_SUPPORT_HOLD"
 elif hrep and not rrep and adv>=int(pre["specificity_rule"]["min_h_lower_bridge_advantage_over_strongest_rival"]):
  verdict="P17_HYPOTHESIS_SURVIVES_FATAL_REPLICATION_SPECIFICALLY"
 elif rrep:verdict="P17_RIVAL_FAMILY_REPLICATES_HYPOTHESIS_DEFEATED"
 elif hrep:verdict="P17_HYPOTHESIS_REPLICATES_BUT_NOT_SPECIFIC"
 else:verdict="P17_HYPOTHESIS_FAILS_UNDER_BALANCED_EXPOSURE"
 stats={}
 for fam in FAMILIES:
  n=famcounts[fam];stats[fam]={"exposures":n,"lower_minimal_full_bridges":lower_counts[fam],
   "upper_minimal_full_bridges":upper_counts[fam],"lower_rate":(lower_counts[fam]/n if n else None),
   "lower_replication":reps[fam]}
 certs=[]
 for r in rows:
  certs.append({"schema":"c3x-causal-contrast-certificate-v1","provenance_class":"C3X_CAUSAL_CONTRAST",
   "certificate_id":hashlib.sha256((r["engine"]+"|"+r["position_id"]+"|"+r["exposure_id"]+"|"+r["bound"]).encode()).hexdigest()[:24],
   "engine":r["engine"],"position_id":r["position_id"],"source_id":r["source_id"],"pair_id":r["pair_id"],
   "family":r["family"],"matched_set_id":r["matched_set_id"],"physical_edit_id":r["physical_edit_id"],
   "moved_side_role":r["moved_side_role"],"engine_relative_atoms":r["engine_relative_atoms"],"bound":r["bound"],
   "collapse_to":r["collapse_to"],"sham_reproduced":r["sham_reproduced"],"concept_label":None,
   "replication_status":"P17_PRIMARY_REPLICATED_FAMILY_MEMBER" if r["family"]=="H" and r["bound"]=="LOWER" and hrep else "LOCAL_ONLY",
   "authority_ceiling":pre["claim_ceiling"]})
 out={"schema":"c3x-g95-p17-adjudication-v1","scientific_stage":STAGE,"status":"CLOSED_PASS" if support else "HOLD","verdict":verdict,
  "world_count":len(worlds),"support":{"pass":support,"admitted_pair_positions":pre["admitted_pair_positions"],
   "complete_matched_sets":pre["complete_matched_sets"],"selected_exposure_count":pre["selected_exposure_count"],
   "family_exposure_counts":famcounts,"equal_family_exposure_counts":equal,"active_engines":engines,"sources":sources,
   "worlds_with_any_fired_semantic_target":fired_worlds,"address_misses":misses},
  "family_statistics":stats,"h_lower_advantage_over_strongest_rival":adv,"replicated_rival_families":rrep,
  "primary_hypothesis_replication":reps["H"],"lower_minimal_full_bridge_records":len(lower),
  "upper_diagnostic_minimal_full_bridge_records":len(upper),"susceptibility_modulation_records":len(mods),
  "bridge_records":rows,"causal_explanation_certificates":certs,"upper_is_diagnostic_only":True,
  "claim_ceiling":pre["claim_ceiling"],"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 lines=["# C3X G9.5-P17 — Exposure-Balanced Relation-Atom Fatal Replication","",
  f"Status: **{out['status']} / {verdict}**",
  f"Complete matched sets: **{pre['complete_matched_sets']}**; selected exposures: **{pre['selected_exposure_count']}**; address misses: **{misses}**.",
  f"H LOWER minimal bridges: **{lower_counts['H']}** / {famcounts['H']}; strongest rival: **{max_rival}**; advantage: **{adv}**.","",
  "## LOWER family results"]
 for fam in FAMILIES:
  z=stats[fam];lines.append(f"- {fam}: {z['lower_minimal_full_bridges']}/{z['exposures']} LOWER minimal bridges; replicated={z['lower_replication']['replicated']}; engines={','.join(z['lower_replication']['engines'])}; positions={z['lower_replication']['positions']}; sources={','.join(z['lower_replication']['sources'])}.")
 lines+=["","UPPER results are diagnostic only and cannot rescue the frozen LOWER prediction.",
  "Family matching is prospective observable-covariate balance, not randomized assignment. No human strategic concept or objective-chess-truth authority is claimed."]
 Path(a.markdown).write_text("\n".join(lines)+"\n")
 print("P17_ADJUDICATE",verdict,out["support"],"H_lower",lower_counts["H"],"max_rival",max_rival,"rivals",rrep)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("design");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p16-closure",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=design)
 q=sp.add_parser("qualify");q.add_argument("--design",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=qualify)
 q=sp.add_parser("pair-pool-freeze");q.add_argument("--design",required=True);q.add_argument("--qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=pair_pool_freeze)
 q=sp.add_parser("exposure-qualify");q.add_argument("--freeze",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=exposure_qualify)
 q=sp.add_parser("exposure-freeze");q.add_argument("--freeze",required=True);q.add_argument("--exposure-qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=exposure_freeze)
 q=sp.add_parser("factorial");q.add_argument("--freeze",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=factorial)
 q=sp.add_parser("adjudicate");q.add_argument("--freeze",required=True);q.add_argument("--worlds",required=True);q.add_argument("--out",required=True);q.add_argument("--markdown",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
