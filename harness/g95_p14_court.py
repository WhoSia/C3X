#!/usr/bin/env python3
import argparse,hashlib,itertools,json,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path
import chess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import g95_p13_court as p13
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P14"
ENGINES=("stockfish_19","berserk","ethereal")
BOUND_NAME={1:"UPPER",2:"LOWER"}
CLS=("CUTOFF","MOVE_ORDER_SEED","EVAL_REUSE","TT_VALUE_AS_EVAL")

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
def pair_parts(pid):return pid.split("::",1)
def gap_band(n):return p13.gap_band(abs(int(n)))
def address(e):
 z=dict(e["address"]);z["address_id"]=e["address_id"];return z

def select_targets(events,key_to_move,pair,preferred,maxn):
 rows=[]
 pair=set(pair)
 for i,e in enumerate(events):
  if e.get("class")!="MOVE_ORDER_SEED" or e.get("scope")!="MAIN" or int(e.get("ply",-1))!=1:continue
  d=int(e.get("depth",0));b=int(e.get("bound",0))
  if not (5<=d<=8) or b not in (1,2) or int(e.get("tt_move",0))==0:continue
  m=key_to_move.get(e.get("key"))
  if m not in pair:continue
  same=[z for z in events[:i] if z.get("key")==e.get("key")]
  if not same or int(same[-1].get("tt_move",0))!=int(e.get("tt_move",0)):continue
  relation="BASELINE_PREFERRED" if m==preferred else "BASELINE_DISPREFERRED"
  rows.append((e["address_id"],i,e,m,relation))
 rows.sort(key=lambda z:z[0])
 return rows[:maxn],len(rows)

def design(a):
 c=load(a.constitution);corp=load(a.corpus);p13c=load(a.p13_closure)
 if c.get("schema")!="c3x-g95-p14-constitution-v1":raise SystemExit("P14_CONSTITUTION")
 if p13c.get("receipt_sha256")!=c["parent"]["closure_receipt_sha256"]:raise SystemExit("P14_PARENT")
 if corp.get("schema")!="c3x-g95-p14-corpus-v1" or corp["selection"]["intervention_outcomes_consulted"] is not False:raise SystemExit("P14_CORPUS")
 builds=Path(a.build_dir);variants={}
 for e in ENGINES:
  fs=list(builds.rglob(f"c3x-p14-{e}"))
  if len(fs)!=1:raise SystemExit(f"P14_BUILD {e} {len(fs)}")
  variants[e]={"sha256":sha_file(fs[0]),"protocol":p32.protocol_for(e)}
 cases=[]
 for pos in corp["positions"]:
  for e in ENGINES:
   cases.append({"case_id":f'p14:{e}:{pos["position_id"]}',"engine":e,"position_id":pos["position_id"],
    "source_id":pos["source_id"],"source_ply":pos["source_ply"],"candidate_sha256":pos["candidate_sha256"],
    "complexity":pos["complexity"],"cell":pos["cell"]})
 if len(cases)!=72:raise SystemExit("P14_CASE_COUNT")
 out={"schema":"c3x-g95-p14-design-precommit-v1","scientific_stage":STAGE,
  "intervention_outcomes_consulted":False,"constitution_sha256":digest(c),"corpus_sha256":digest(corp),
  "parent_p13_receipt_sha256":p13c["receipt_sha256"],"variants":variants,"execution":c["execution"],
  "engine_qualification":c["engine_qualification"],"unordered_pair_constitution":c["unordered_pair_constitution"],
  "invariance_constitution":c["invariance_constitution"],"root_child_attribution":c["root_child_attribution"],
  "exact_target":c["exact_target"],"orientation_free_effects":c["orientation_free_effects"],
  "same_position_transport":c["same_position_transport"],"support_gate":c["support_gate"],
  "replication_rule":c["replication_rule"],"claim_ceiling":c["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P14_DESIGN_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def load_design(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p14-design-precommit-v1" or x.get("intervention_outcomes_consulted") is not False:raise SystemExit("P14_DESIGN")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P14_DESIGN_HASH")
 return x

def qualify(a):
 pre=load_design(a.design);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P14_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P14_BINARY")
 ex=pre["execution"];fen=case["cell"]["fen"];board=chess.Board(fen)
 root=Path(a.out).parent/".p14-qual-private";root.mkdir(parents=True,exist_ok=True)
 base=p13.run_context(a.binary,v["protocol"],case["cell"],"CATALOG",None,root/"base")
 legal=sorted(m.uci() for m in board.legal_moves)
 shallow=[]
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
  cps=[p13.score_cp(s) for s in vals]
  stable=len(cps)==2 and None not in cps and cps[0]==cps[1]
  qshort.append({"move":z["move"],"shallow_score":z["score"],"confirm_scores":vals,
                 "stable":stable,"confirm_cp":cps[0] if stable else None})
 out={"schema":"c3x-g95-p14-engine-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],
  "engine":case["engine"],"position_id":case["position_id"],"source_id":case["source_id"],"source_ply":case["source_ply"],
  "candidate_sha256":case["candidate_sha256"],"legal_root_move_count":len(legal),"baseline":sem(base["semantic"]),
  "baseline_incumbent_timeline":base["incumbent_timeline"],"shortlist":qshort,
  "intervention_outcomes_consulted":False,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P14_QUALIFY",case["case_id"],"stable",sum(z["stable"] for z in qshort),"baseline",out["baseline"]["bestmove"])

def freeze(a):
 pre=load_design(a.design);found={}
 for p in Path(a.qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p14-engine-qualification-v1":found[x["case_id"]]=x
 ids={x["case_id"] for x in pre["cases"]}
 if set(found)!=ids:raise SystemExit(f"P14_QUAL_N {len(found)} expected {len(ids)}")
 bypos=defaultdict(list)
 for c in pre["cases"]:
  q=found[c["case_id"]]
  if q.get("intervention_outcomes_consulted") is not False or q.get("raw_tt_key_emitted") is not False:raise SystemExit("P14_QUAL_AUTHORITY")
  bypos[c["position_id"]].append((c,q))
 frozen_positions={};active_worlds=0
 for pid,rows in sorted(bypos.items()):
  if len(rows)!=3:raise SystemExit("P14_POSITION_ENGINE_COUNT")
  stable={}
  for c,q in rows:
   stable[c["engine"]]={z["move"]["uci"]:int(z["confirm_cp"]) for z in q["shortlist"] if z["stable"]}
  universe=sorted(set().union(*(set(x) for x in stable.values())))
  candidates=[]
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
  sel=candidates[0] if candidates else None
  c0,q0=rows[0];fen=c0["cell"]["fen"]
  if sel is None:
   frozen_positions[pid]={"position_id":pid,"source_id":c0["source_id"],"source_ply":c0["source_ply"],
    "candidate_sha256":c0["candidate_sha256"],"admitted":False,"pair":None,"geometry":None,"engine_views":{}}
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
  frozen_positions[pid]={"position_id":pid,"source_id":c0["source_id"],"source_ply":c0["source_ply"],
   "candidate_sha256":c0["candidate_sha256"],"admitted":True,
   "pair":{"pair_id":sel["pair_id"],"A":p13.move_doc(fen,A),"B":p13.move_doc(fen,B),
           "support_count":sel["support_count"],"median_gap_cp":sel["median_gap_cp"],"max_gap_cp":sel["max_gap_cp"]},
   "geometry":geom,"engine_views":views}
 cases=[]
 for c in pre["cases"]:
  cases.append({**c,"qualification":found[c["case_id"]],"position_pair":frozen_positions[c["position_id"]],
                "engine_view":frozen_positions[c["position_id"]]["engine_views"].get(c["engine"],{})})
 admitted=[z for z in frozen_positions.values() if z["admitted"]]
 out={"schema":"c3x-g95-p14-unordered-pair-freeze-v1","scientific_stage":STAGE,
  "design_receipt_sha256":pre["receipt_sha256"],"intervention_outcomes_consulted":False,
  "admitted_pair_positions":len(admitted),"active_engine_worlds":active_worlds,
  "active_engines":sorted({c["engine"] for c in cases if c["engine_view"].get("active")}),
  "sources":sorted({z["source_id"] for z in admitted}),"geometry_counts":dict(sorted(Counter(z["geometry"] for z in admitted).items())),
  "execution":pre["execution"],"unordered_pair_constitution":pre["unordered_pair_constitution"],
  "invariance_constitution":pre["invariance_constitution"],"root_child_attribution":pre["root_child_attribution"],
  "exact_target":pre["exact_target"],"orientation_free_effects":pre["orientation_free_effects"],
  "same_position_transport":pre["same_position_transport"],"support_gate":pre["support_gate"],
  "replication_rule":pre["replication_rule"],"claim_ceiling":pre["claim_ceiling"],
  "variants":pre["variants"],"positions":frozen_positions,"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P14_PAIR_FREEZE",out["receipt_sha256"],"positions",len(admitted),"active_worlds",active_worlds,"geometry",out["geometry_counts"])

def load_freeze(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p14-unordered-pair-freeze-v1" or x.get("intervention_outcomes_consulted") is not False:raise SystemExit("P14_FREEZE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P14_FREEZE_HASH")
 return x

def case_run(a):
 pre=load_freeze(a.freeze);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P14_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P14_BINARY")
 pos=case["position_pair"];view=case["engine_view"]
 if not pos.get("admitted") or not view.get("active"):
  out={"schema":"c3x-g95-p14-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
   "position_id":case["position_id"],"source_id":case["source_id"],"active":False,
   "skip_reason":"NO_ADMITTED_PAIR" if not pos.get("admitted") else "ENGINE_NOT_ACTIVE_ON_FROZEN_PAIR",
   "selected_targets":0,"eligible_targets":0,"fired_targets":0,"address_misses":[],"records":[],"raw_tt_key_emitted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P14_WORLD_SKIP",case["case_id"],out["skip_reason"]);return
 fen=case["cell"]["fen"];A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"];preferred=view["baseline_preferred"]
 other=B if preferred==A else A
 root=Path(a.out).parent/".p14-world-private";root.mkdir(parents=True,exist_ok=True)
 base=p13.run_context(a.binary,v["protocol"],case["cell"],"CATALOG",None,root/"base")
 if base["semantic"].get("bestmove")!=preferred or base["semantic"].get("score")!=case["qualification"]["baseline"].get("score"):raise SystemExit("P14_BASELINE_DRIFT")
 fp,key_to_move,collisions=p13.fingerprint(a.binary,v["protocol"],fen,[A,B],int(pre["execution"]["root_child_fingerprint_nodes"]),root/"fingerprint")
 base_exp=p13.exposure_summary(base["trace"]["events"],key_to_move,[A,B],base["incumbent_timeline"],preferred)
 selected,eligible=select_targets(base["trace"]["events"],key_to_move,(A,B),preferred,int(pre["execution"]["max_targets_per_active_world"]))
 records=[];miss=[]
 for j,(eid,bi,e,target_move,relation) in enumerate(selected):
  t=p13.run_context(a.binary,v["protocol"],case["cell"],"REMOVE_SET",[address(e)],root/f"t-{j:02d}")
  matches=[z for z in t["trace"]["events"] if z["address_id"]==eid]
  fired=bool(t["trace"]["targets"] and t["trace"]["targets"][0]["fired"])
  if not fired or len(matches)!=1:
   miss.append({"target_event_id_prefix":eid[:16],"fired":fired,"trace_matches":len(matches)});continue
  tm=t["semantic"].get("bestmove")
  if tm==other:effect="EDGE_REVERSAL"
  elif tm==preferred:effect="EDGE_PRESERVED"
  else:effect="EDGE_TO_THIRD_ESCAPE"
  t_exp=p13.exposure_summary(t["trace"]["events"],key_to_move,[A,B],t["incumbent_timeline"],tm)
  rec={"record_id":f'{case["case_id"]}:{eid[:16]}',"engine":case["engine"],"position_id":case["position_id"],
   "source_id":case["source_id"],"source_ply":case["source_ply"],"candidate_sha256":case["candidate_sha256"],
   "pair_id":pos["pair"]["pair_id"],"pair":{"A":pos["pair"]["A"],"B":pos["pair"]["B"]},"position_geometry":pos["geometry"],
   "engine_gap_cp_signed_A_minus_B":view["signed_A_minus_B_cp"],"engine_gap_cp_abs":view["gap_cp_abs"],"engine_gap_band":view["gap_band"],
   "baseline_preferred":p13.move_doc(fen,preferred),"baseline_dispreferred":p13.move_doc(fen,other),
   "target_event_id":eid,"target_event_id_prefix":eid[:16],"target_relation":relation,
   "target_candidate":p13.move_doc(fen,target_move),"target_bound":BOUND_NAME[int(e["bound"])],
   "effect_category":effect,"edge_reversed":effect=="EDGE_REVERSAL",
   "baseline":sem(base["semantic"]),"t_only":sem(t["semantic"]),"t_only_root":p13.move_doc(fen,tm),
   "baseline_pv_san":p13.pv_san(fen,base["semantic"].get("pv")),"t_only_pv_san":p13.pv_san(fen,t["semantic"].get("pv")),
   "first_pv_divergence_ply":p13.pv_div(base["semantic"].get("pv"),t["semantic"].get("pv")),
   "baseline_incumbent_timeline":base["incumbent_timeline"],"t_only_incumbent_timeline":t["incumbent_timeline"],
   "baseline_pair_exposure":{m:base_exp[m] for m in (A,B)},"t_only_pair_exposure":{m:t_exp[m] for m in (A,B)},
   "pair_exposure_delta":p13.exposure_delta({m:base_exp[m] for m in (A,B)},{m:t_exp[m] for m in (A,B)}),
   "raw_tt_key_emitted":False}
  rec["pair_edge_transition"]=f'{rec["baseline_preferred"]["san"]} -> {rec["t_only_root"].get("san",tm)}; {relation}/{rec["target_bound"]}; {effect}'
  records.append(rec)
 out={"schema":"c3x-g95-p14-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"source_id":case["source_id"],"active":True,"pair":pos["pair"],"position_geometry":pos["geometry"],
  "fingerprint_public_summary":fp,"fingerprint_collision_count":len(collisions),"selected_targets":len(selected),
  "eligible_targets":eligible,"fired_targets":len(records),"address_misses":miss,"records":records,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P14_WORLD",case["case_id"],pos["geometry"],"eligible",eligible,"selected",len(selected),"fired",len(records),
       "reversals",sum(r["effect_category"]=="EDGE_REVERSAL" for r in records))

def event_sig(r):
 return "|".join([r["position_geometry"],r["target_relation"],r["target_bound"],r["engine_gap_band"],"EDGE_REVERSAL"])

def adjudicate(a):
 pre=load_freeze(a.freeze);worlds=[]
 for p in Path(a.worlds).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p14-world-v1":worlds.append(x)
 if len(worlds)!=72:raise SystemExit(f"P14_WORLD_N {len(worlds)}")
 active=[w for w in worlds if w.get("active")];rows=sorted([r for w in worlds for r in w["records"]],key=lambda z:z["record_id"])
 worlds_with_targets=sum(1 for w in active if int(w.get("selected_targets",0))>0)
 misses=sum(len(w.get("address_misses",[])) for w in worlds)
 gate=pre["support_gate"];admitted=int(pre["admitted_pair_positions"]);active_eng=sorted({w["engine"] for w in active})
 sources=sorted({w["source_id"] for w in active})
 support=(admitted>=gate["min_admitted_pair_positions"] and len(active)>=gate["min_active_engine_worlds"]
  and len(active_eng)>=gate["min_active_engines"] and len(sources)>=gate["min_sources"]
  and worlds_with_targets>=gate["min_worlds_with_selected_target"] and len(rows)>=gate["min_fired_target_records"]
  and misses<=gate["max_address_misses"])
 effects=Counter(r["effect_category"] for r in rows);revs=[r for r in rows if r["effect_category"]=="EDGE_REVERSAL"]
 groups=defaultdict(list)
 for r in revs:groups[event_sig(r)].append(r)
 req=pre["replication_rule"]["replicated_orientation_free_reversal_requires"];rep=[]
 for k,v in groups.items():
  if len(v)>=req["witnesses"] and len({x["engine"] for x in v})>=req["engines"] and len({x["position_id"] for x in v})>=req["positions"] and len({x["source_id"] for x in v})>=req["sources"]:
   rep.append({"signature":k,"witnesses":len(v),"engines":sorted({x["engine"] for x in v}),
    "positions":len({x["position_id"] for x in v}),"sources":sorted({x["source_id"] for x in v})})
 same_groups=defaultdict(list)
 for r in revs:same_groups[(r["position_id"],r["target_relation"],r["target_bound"])].append(r)
 transports=[]
 for (pid,rel,bound),v in sorted(same_groups.items()):
  engines=sorted({x["engine"] for x in v})
  if len(engines)<2:continue
  byeng={}
  for x in v:byeng.setdefault(x["engine"],x)
  prefs={e:byeng[e]["baseline_preferred"]["uci"] for e in engines}
  kind="RECIPROCAL_MULTIENGINE_REVERSAL" if len(set(prefs.values()))>=2 else "CONSENSUS_MULTIENGINE_REVERSAL"
  x0=next(iter(byeng.values()))
  transports.append({"position_id":pid,"pair_id":x0["pair_id"],"source_id":x0["source_id"],"position_geometry":x0["position_geometry"],
    "target_relation":rel,"target_bound":bound,"kind":kind,"engines":engines,"baseline_preferred_by_engine":prefs,
    "witness_records":sum(1 for x in v)})
 reciprocal=[z for z in transports if z["kind"]=="RECIPROCAL_MULTIENGINE_REVERSAL"]
 rg=defaultdict(list)
 for z in reciprocal:rg[f'{z["target_relation"]}|{z["target_bound"]}|RECIPROCAL_MULTIENGINE_REVERSAL'].append(z)
 rr=pre["replication_rule"]["replicated_reciprocal_requires"];rep_recip=[]
 for k,v in rg.items():
  if len({x["position_id"] for x in v})>=rr["positions"] and len({x["source_id"] for x in v})>=rr["sources"] and len(set(e for x in v for e in x["engines"]))>=rr["minimum_distinct_engines_across_positions"]:
   rep_recip.append({"signature":k,"positions":len({x["position_id"] for x in v}),"sources":sorted({x["source_id"] for x in v}),
    "engines":sorted(set(e for x in v for e in x["engines"]))})
 if not support:verdict="P14_FRESH_SUPPORT_HOLD"
 elif rep_recip:verdict="P14_REPLICATED_RECIPROCAL_CROSS_ENGINE_PAIR_GEOMETRY"
 elif rep:verdict="P14_REPLICATED_ORIENTATION_FREE_PAIR_REVERSAL_TRANSPORT"
 elif transports:verdict="P14_LOCAL_MULTIENGINE_UNORDERED_PAIR_TRANSPORT_ONLY"
 elif revs:verdict="P14_LOCAL_UNORDERED_PAIR_EDGE_CAUSALITY_ONLY"
 else:verdict="P14_NO_PAIR_EDGE_REVERSAL_UNDER_FROZEN_EXACT_EVENT_INTERVENTION"
 out={"schema":"c3x-g95-p14-adjudication-v1","scientific_stage":STAGE,"status":"CLOSED_PASS" if support else "HOLD",
  "verdict":verdict,"world_count":len(worlds),"support":{"pass":support,"admitted_pair_positions":admitted,
   "active_engine_worlds":len(active),"active_engines":active_eng,"sources":sources,
   "worlds_with_selected_target":worlds_with_targets,"fired_target_records":len(rows),"address_misses":misses},
  "pair_geometry_counts":pre["geometry_counts"],"effect_counts":dict(sorted(effects.items())),
  "edge_reversal_per_engine":dict(sorted(Counter(r["engine"] for r in revs).items())),
  "edge_reversal_per_source":dict(sorted(Counter(r["source_id"] for r in revs).items())),
  "replicated_orientation_free_reversal_signatures":rep,
  "same_position_multiengine_reversal_transports":transports,
  "reciprocal_multiengine_reversal_transports":reciprocal,
  "replicated_reciprocal_signatures":rep_recip,
  "records":rows,"claim_ceiling":pre["claim_ceiling"],"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 lines=["# C3X G9.5-P14 — Unordered Legal-Move Pair Transport Diagnostic","",f"Status: **{out['status']} / {verdict}**",
  f"Admitted pair positions: **{admitted}/24**; active worlds: **{len(active)}/72**; fired exact targets: **{len(rows)}**; edge reversals: **{len(revs)}**.",
  f"Same-position multi-engine reversal transports: **{len(transports)}**; reciprocal: **{len(reciprocal)}**.","",
  "## Pair-edge reversal witnesses"]
 if revs:
  for r in revs[:60]:
   lines.append(f"- {r['engine']} / {r['position_id']} / {r['pair_id']}: {r['baseline_preferred']['san']} → {r['t_only_root']['san']}; {r['position_geometry']}; gap={r['engine_gap_cp_abs']} cp; {r['target_relation']}/{r['target_bound']}.")
 else:lines.append("- None.")
 lines+=["","## Same-position multi-engine transport"]
 if transports:
  for z in transports:lines.append(f"- {z['position_id']} / {z['pair_id']}: {z['kind']}; {z['target_relation']}/{z['target_bound']}; engines={','.join(z['engines'])}; baseline={z['baseline_preferred_by_engine']}.")
 else:lines.append("- None.")
 lines+=["","## Replicated reciprocal signatures"]
 if rep_recip:
  for z in rep_recip:lines.append(f"- {z['signature']}: positions={z['positions']}; sources={','.join(z['sources'])}; engines={','.join(z['engines'])}.")
 else:lines.append("- None under the frozen rule.")
 lines+=["","Raw TT keys are not emitted. Pair-label permutation is prospectively quotiented; canonical UCI labels remain only for reconstruction."]
 Path(a.markdown).write_text("\n".join(lines)+"\n")
 print("P14_ADJUDICATE",verdict,out["support"])

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("design");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p13-closure",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=design)
 q=sp.add_parser("qualify");q.add_argument("--design",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=qualify)
 q=sp.add_parser("freeze");q.add_argument("--design",required=True);q.add_argument("--qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=freeze)
 q=sp.add_parser("case");q.add_argument("--freeze",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("adjudicate");q.add_argument("--freeze",required=True);q.add_argument("--worlds",required=True);q.add_argument("--out",required=True);q.add_argument("--markdown",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
