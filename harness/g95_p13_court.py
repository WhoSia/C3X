#!/usr/bin/env python3
import argparse,hashlib,json,os,re,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
import chess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32
import p27_age_morphism as p27

STAGE="C3X 0.7.0-G9.5-P13"
ENGINES=("stockfish_19","berserk","ethereal")
BOUND_NAME={1:"UPPER",2:"LOWER"}
CLS=("CUTOFF","MOVE_ORDER_SEED","EVAL_REUSE","TT_VALUE_AS_EVAL")
PRIME=20000;DECOY=20000;ANCHOR=80000

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
def score_cp(s):
 if not isinstance(s,str):return None
 m=re.fullmatch(r"cp (-?\d+)",s.strip())
 return int(m.group(1)) if m else None
def rank_value(s):
 if not isinstance(s,str):return -10**9
 m=re.fullmatch(r"(cp|mate) (-?\d+)",s.strip())
 if not m:return -10**9
 v=int(m.group(2))
 return v if m.group(1)=="cp" else (100000-abs(v) if v>0 else -100000+abs(v))
def gap_band(n):
 n=abs(int(n))
 return "VERY_TIGHT" if n<=15 else "TIGHT" if n<=30 else "MARGINAL" if n<=50 else "OUTSIDE"
def move_doc(fen,uci):
 if not uci:return None
 b=chess.Board(fen)
 try:m=chess.Move.from_uci(uci)
 except:return {"uci":uci,"legal":False}
 if m not in b.legal_moves:return {"uci":uci,"legal":False}
 return {"uci":uci,"san":b.san(m),"legal":True,"capture":b.is_capture(m),"check":b.gives_check(m),
         "castling":b.is_castling(m),"promotion":bool(m.promotion)}
def pv_san(fen,pv,limit=10):
 moves=[x for x in (pv.split() if isinstance(pv,str) else list(pv or [])) if x]
 b=chess.Board(fen);out=[]
 for u in moves[:limit]:
  try:m=chess.Move.from_uci(u)
  except:break
  if m not in b.legal_moves:break
  out.append(b.san(m));b.push(m)
 return out
def pv_div(a,b):
 a=[x for x in (a.split() if isinstance(a,str) else list(a or [])) if x]
 b=[x for x in (b.split() if isinstance(b,str) else list(b or [])) if x]
 i=0
 while i<min(len(a),len(b)) and a[i]==b[i]:i+=1
 return None if i==len(a)==len(b) else i
def address(e):
 z=dict(e["address"]);z["address_id"]=e["address_id"];return z
def quitp(p):
 try:p.stdin.write("quit\n");p.stdin.flush()
 except:pass
 try:p.communicate(timeout=8)
 except subprocess.TimeoutExpired:p.kill();p.communicate()
 finally:
  if p.poll() is None:p.kill()

def parse_incumbents(lines):
 by={}
 for line in lines:
  if not line.startswith("info ") or " pv " not in line:continue
  md=re.search(r"\bdepth (\d+)",line);mp=re.search(r"\bpv ([a-h][1-8][a-h][1-8][qrbn]?)(?:\s|$)",line)
  if not md or not mp:continue
  ms=re.search(r"\bscore ((?:cp|mate) -?\d+)",line);mn=re.search(r"\bnodes (\d+)",line)
  d=int(md.group(1))
  by[d]={"depth":d,"root_uci":mp.group(1),"score":ms.group(1) if ms else None,"nodes":int(mn.group(1)) if mn else None}
 return [by[d] for d in sorted(by)]

def run_context(path,protocol,cell,mode,addresses,work):
 work=Path(work);work.mkdir(parents=True,exist_ok=True)
 trace=work/"p32.csv";tt=work/"tt.csv";target=work/"targets.tsv"
 if addresses is not None:p32.write_targets(target,addresses)
 p=p32.setup(path,protocol,mode,"ALL",8,target if addresses is not None else None,trace,tt)
 try:
  p27.go(p,cell["fen"],PRIME,protocol)
  for d in cell["history"]["decoys"]:p27.go(p,d["fen"],DECOY,protocol)
  p.stdin.write(f'position fen {cell["fen"]}\ngo nodes {ANCHOR}\n');p.stdin.flush()
  lines=p27.read_until(p,lambda x:x.startswith("bestmove "))
  s=p27.parse_sem(lines)
  quitp(p)
 finally:
  if p.poll() is None:p.kill()
 tr=p32.parse_trace(trace)
 for q in (trace,tt,target):q.unlink(missing_ok=True)
 return {"semantic":s,"trace":tr,"incumbent_timeline":parse_incumbents(lines)}

def run_forced(path,protocol,fen,move,nodes,work,tag,observe_rootchild=False):
 work=Path(work);work.mkdir(parents=True,exist_ok=True)
 trace=work/f"{tag}.csv";tt=work/f"{tag}-tt.csv";rc=work/f"{tag}-rootchild.csv"
 old=os.environ.get("C3X_P13_ROOTCHILD_TRACE")
 if observe_rootchild:os.environ["C3X_P13_ROOTCHILD_TRACE"]=str(rc)
 else:os.environ.pop("C3X_P13_ROOTCHILD_TRACE",None)
 try:
  p=p32.setup(path,protocol,"CATALOG","ALL",8,None,trace,tt)
 finally:
  if old is None:os.environ.pop("C3X_P13_ROOTCHILD_TRACE",None)
  else:os.environ["C3X_P13_ROOTCHILD_TRACE"]=old
 try:
  p.stdin.write(f"position fen {fen}\ngo nodes {nodes} searchmoves {move}\n");p.stdin.flush()
  lines=p27.read_until(p,lambda x:x.startswith("bestmove "))
  s=p27.parse_sem(lines)
  quitp(p)
 finally:
  if p.poll() is None:p.kill()
 tr=p32.parse_trace(trace);keys=[]
 if observe_rootchild and rc.exists():
  for line in rc.read_text().splitlines():
   z=line.split(",")
   if len(z)==2 and z[0]=="K":keys.append(z[1].lower())
 for q in (trace,tt,rc):q.unlink(missing_ok=True)
 return {"semantic":s,"trace":tr,"incumbent_timeline":parse_incumbents(lines),"rootchild_keys":sorted(set(keys))}

def fingerprint(path,protocol,fen,moves,nodes,work):
 out={};collisions=[];key_to_move={}
 for i,m in enumerate(moves):
  r=run_forced(path,protocol,fen,m,nodes,work,f"fp-{i:02d}",observe_rootchild=True)
  keys=r["rootchild_keys"]
  ok=len(keys)==1
  out[m]={"mapped":ok,"ply1_key_count":len(keys)}
  if not ok:continue
  k=keys[0]
  if k in key_to_move and key_to_move[k]!=m:
   collisions.append([key_to_move[k],m]);continue
  key_to_move[k]=m
 return out,key_to_move,collisions

def exposure_summary(events,key_to_move,moves,timeline,final_move):
 rows={m:{"event_count":0,"class_counts":{c:0 for c in CLS},"null_window_count":0,
          "max_depth":None,"first_trace_ordinal":None,"last_trace_ordinal":None} for m in moves}
 for i,e in enumerate(events):
  if int(e.get("ply",-1))!=1:continue
  m=key_to_move.get(e.get("key"))
  if m not in rows:continue
  z=rows[m];z["event_count"]+=1
  c=e.get("class")
  if c in z["class_counts"]:z["class_counts"][c]+=1
  if int(e.get("beta",0))-int(e.get("alpha",0))<=1:z["null_window_count"]+=1
  d=int(e.get("depth",0));z["max_depth"]=d if z["max_depth"] is None else max(z["max_depth"],d)
  if z["first_trace_ordinal"] is None:z["first_trace_ordinal"]=i
  z["last_trace_ordinal"]=i
 incumb={x["root_uci"] for x in timeline}
 for m,z in rows.items():
  if m==final_move:fate="FINAL_WINNER"
  elif m in incumb:fate="PV_DISPLACED"
  elif z["event_count"]>0:fate="SEARCH_EXPOSED_NEVER_PV"
  else:fate="NO_MAPPED_ROOTCHILD_EXPOSURE"
  z["fate"]=fate
 return rows

def exposure_delta(a,b):
 out={}
 for m in sorted(set(a)|set(b)):
  x=a.get(m,{}) ; y=b.get(m,{})
  out[m]={
   "event_count":int(y.get("event_count",0))-int(x.get("event_count",0)),
   "null_window_count":int(y.get("null_window_count",0))-int(x.get("null_window_count",0)),
   "class_counts":{c:int(y.get("class_counts",{}).get(c,0))-int(x.get("class_counts",{}).get(c,0)) for c in CLS},
   "fate_before":x.get("fate"),"fate_after":y.get("fate")
  }
 return out

def select_targets(events,key_to_move,pair,maxn):
 rows=[]
 for i,e in enumerate(events):
  if e.get("class")!="MOVE_ORDER_SEED" or e.get("scope")!="MAIN" or int(e.get("ply",-1))!=1:continue
  d=int(e.get("depth",0));b=int(e.get("bound",0))
  if not (5<=d<=8) or b not in (1,2) or int(e.get("tt_move",0))==0:continue
  m=key_to_move.get(e.get("key"))
  if m not in pair:continue
  same=[z for z in events[:i] if z.get("key")==e.get("key")]
  if not same or int(same[-1].get("tt_move",0))!=int(e.get("tt_move",0)):continue
  rows.append((e["address_id"],i,e,m))
 rows.sort(key=lambda z:z[0])
 return rows[:maxn],len(rows)

def design(a):
 c=load(a.constitution);corp=load(a.corpus);p12=load(a.p12_closure)
 if c.get("schema")!="c3x-g95-p13-constitution-v1":raise SystemExit("P13_CONSTITUTION")
 if p12.get("receipt_sha256")!=c["parent"]["closure_receipt_sha256"]:raise SystemExit("P13_PARENT")
 if corp.get("schema")!="c3x-g95-p13-corpus-v1" or corp["selection"]["engine_outcomes_consulted"] is not False:raise SystemExit("P13_CORPUS")
 builds=Path(a.build_dir);variants={}
 for e in ENGINES:
  fs=list(builds.rglob(f"c3x-p13-{e}"))
  if len(fs)!=1:raise SystemExit(f"P13_BUILD {e} {len(fs)}")
  variants[e]={"sha256":sha_file(fs[0]),"protocol":p32.protocol_for(e)}
 cases=[]
 for pos in corp["positions"]:
  for e in ENGINES:
   cases.append({"case_id":f'p13:{e}:{pos["position_id"]}',"engine":e,"position_id":pos["position_id"],
    "source_id":pos["source_id"],"source_ply":pos["source_ply"],"candidate_sha256":pos["candidate_sha256"],
    "complexity":pos["complexity"],"cell":pos["cell"]})
 if len(cases)!=48:raise SystemExit("P13_CASE_COUNT")
 out={"schema":"c3x-g95-p13-design-precommit-v1","scientific_stage":STAGE,"engine_outcomes_consulted":False,
  "intervention_outcomes_consulted":False,"constitution_sha256":digest(c),"corpus_sha256":digest(corp),
  "parent_p12_receipt_sha256":p12["receipt_sha256"],"variants":variants,"execution":c["execution"],
  "candidate_qualification":c["candidate_qualification"],"root_child_attribution":c["root_child_attribution"],
  "exact_target":c["exact_target"],"preference_boundary":c["preference_boundary"],"support_gate":c["support_gate"],
  "replication_rule":c["replication_rule"],"claim_ceiling":c["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P13_DESIGN_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def load_design(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p13-design-precommit-v1" or x.get("engine_outcomes_consulted") is not False:raise SystemExit("P13_DESIGN")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P13_DESIGN_HASH")
 return x

def qualify(a):
 pre=load_design(a.design);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P13_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P13_BINARY")
 ex=pre["execution"];fen=case["cell"]["fen"];board=chess.Board(fen)
 root=Path(a.out).parent/".p13-qual-private";root.mkdir(parents=True,exist_ok=True)
 base=run_context(a.binary,v["protocol"],case["cell"],"CATALOG",None,root/"base")
 legal=sorted(m.uci() for m in board.legal_moves)
 shallow=[]
 for i,m in enumerate(legal):
  r=run_forced(a.binary,v["protocol"],fen,m,int(ex["shallow_legal_move_nodes"]),root/"shallow",f"{i:02d}")
  s=r["semantic"].get("score")
  shallow.append({"uci":m,"move":move_doc(fen,m),"score":s,"rank_value":rank_value(s)})
 shortlist=sorted(shallow,key=lambda z:(-z["rank_value"],z["uci"]))[:int(ex["shortlist_size"])]
 confirms={}
 for i,z in enumerate(shortlist):
  vals=[]
  for rep in range(int(ex["isolated_confirm_repeats"])):
   r=run_forced(a.binary,v["protocol"],fen,z["uci"],int(ex["isolated_confirm_nodes"]),root/"confirm",f"{i:02d}-{rep}")
   vals.append(r["semantic"].get("score"))
  cps=[score_cp(s) for s in vals]
  stable=len(cps)==2 and None not in cps and cps[0]==cps[1]
  confirms[z["uci"]]={"scores":vals,"stable":stable,"cp":cps[0] if stable else None}
 winner=base["semantic"].get("bestmove");reason=None;pair=None
 sm={z["uci"]:z for z in shortlist}
 if winner not in sm:reason="CONTEXTUAL_WINNER_OUTSIDE_SHORTLIST"
 elif not confirms[winner]["stable"]:reason="CONTEXTUAL_WINNER_NOT_STABLE_CP"
 else:
  wc=confirms[winner]["cp"]
  rivals=[m for m in confirms if m!=winner and confirms[m]["stable"]]
  if not rivals:reason="NO_STABLE_RIVAL"
  else:
   rival=sorted(rivals,key=lambda m:(abs(confirms[m]["cp"]-wc),-confirms[m]["cp"],m))[0]
   gap=wc-confirms[rival]["cp"];mx=int(pre["candidate_qualification"]["near_equal_max_abs_cp"])
   if abs(gap)>mx:reason="RIVAL_OUTSIDE_NEAR_EQUAL_BAND"
   else:
    pair={"winner":move_doc(fen,winner),"rival":move_doc(fen,rival),"winner_cp":wc,"rival_cp":confirms[rival]["cp"],
          "gap_cp_signed":gap,"gap_cp_abs":abs(gap),"gap_band":gap_band(gap)}
 qshort=[]
 for z in shortlist:
  qshort.append({"move":z["move"],"shallow_score":z["score"],"confirm_scores":confirms[z["uci"]]["scores"],
                 "stable":confirms[z["uci"]]["stable"],"confirm_cp":confirms[z["uci"]]["cp"]})
 out={"schema":"c3x-g95-p13-qualification-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"source_id":case["source_id"],"source_ply":case["source_ply"],
  "candidate_sha256":case["candidate_sha256"],"baseline":sem(base["semantic"]),
  "baseline_incumbent_timeline":base["incumbent_timeline"],"legal_root_move_count":len(legal),"shortlist":qshort,
  "qualified":pair is not None,"qualification_reason":"QUALIFIED" if pair is not None else reason,"pair":pair,
  "intervention_outcomes_consulted":False,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P13_QUALIFY",case["case_id"],out["qualified"],out["qualification_reason"])

def freeze(a):
 pre=load_design(a.design);found={}
 for p in Path(a.qualifications).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p13-qualification-v1":found[x["case_id"]]=x
 ids={x["case_id"] for x in pre["cases"]}
 if set(found)!=ids:raise SystemExit(f"P13_QUAL_N {len(found)} expected {len(ids)}")
 cases=[]
 for c in pre["cases"]:
  q=found[c["case_id"]]
  if q.get("intervention_outcomes_consulted") is not False or q.get("raw_tt_key_emitted") is not False:raise SystemExit("P13_QUAL_AUTHORITY")
  cases.append({**c,"qualification":q})
 qs=[c for c in cases if c["qualification"]["qualified"]]
 out={"schema":"c3x-g95-p13-pair-freeze-v1","scientific_stage":STAGE,
  "design_receipt_sha256":pre["receipt_sha256"],"intervention_outcomes_consulted":False,
  "qualified_worlds":len(qs),"qualified_engines":sorted({c["engine"] for c in qs}),
  "qualified_sources":sorted({c["source_id"] for c in qs}),"qualified_positions":len({c["position_id"] for c in qs}),
  "execution":pre["execution"],"root_child_attribution":pre["root_child_attribution"],"exact_target":pre["exact_target"],
  "preference_boundary":pre["preference_boundary"],"support_gate":pre["support_gate"],"replication_rule":pre["replication_rule"],
  "claim_ceiling":pre["claim_ceiling"],"variants":pre["variants"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P13_PAIR_FREEZE",out["receipt_sha256"],"qualified",len(qs))

def load_freeze(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p13-pair-freeze-v1" or x.get("intervention_outcomes_consulted") is not False:raise SystemExit("P13_FREEZE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P13_FREEZE_HASH")
 return x

def case_run(a):
 pre=load_freeze(a.freeze);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P13_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P13_BINARY")
 q=case["qualification"]
 if not q["qualified"]:
  out={"schema":"c3x-g95-p13-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
       "position_id":case["position_id"],"source_id":case["source_id"],"qualified":False,
       "qualification_reason":q["qualification_reason"],"selected_targets":0,"eligible_targets":0,"fired_targets":0,
       "address_misses":[],"records":[],"raw_tt_key_emitted":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P13_WORLD_SKIP",case["case_id"]);return
 fen=case["cell"]["fen"];pair=q["pair"];winner=pair["winner"]["uci"];rival=pair["rival"]["uci"]
 root=Path(a.out).parent/".p13-world-private";root.mkdir(parents=True,exist_ok=True)
 base=run_context(a.binary,v["protocol"],case["cell"],"CATALOG",None,root/"base")
 if base["semantic"].get("bestmove")!=winner or base["semantic"].get("score")!=q["baseline"].get("score"):raise SystemExit("P13_BASELINE_DRIFT")
 shortlist=[z["move"]["uci"] for z in q["shortlist"]]
 fp,key_to_move,collisions=fingerprint(a.binary,v["protocol"],fen,shortlist,int(pre["execution"]["root_child_fingerprint_nodes"]),root/"fingerprint")
 base_exp=exposure_summary(base["trace"]["events"],key_to_move,shortlist,base["incumbent_timeline"],winner)
 selected,eligible=select_targets(base["trace"]["events"],key_to_move,{winner,rival},int(pre["execution"]["max_targets_per_world"]))
 records=[];miss=[]
 for j,(eid,bi,e,target_move) in enumerate(selected):
  t=run_context(a.binary,v["protocol"],case["cell"],"REMOVE_SET",[address(e)],root/f"t-{j:02d}")
  matches=[z for z in t["trace"]["events"] if z["address_id"]==eid]
  fired=bool(t["trace"]["targets"] and t["trace"]["targets"][0]["fired"])
  if not fired or len(matches)!=1:
   miss.append({"target_event_id_prefix":eid[:16],"fired":fired,"trace_matches":len(matches)});continue
  tm=t["semantic"].get("bestmove")
  if tm==rival:effect="DIRECT_PAIR_FLIP"
  elif tm==winner:effect="ROOT_UNCHANGED"
  else:effect="THIRD_MOVE_REDIRECT"
  t_exp=exposure_summary(t["trace"]["events"],key_to_move,shortlist,t["incumbent_timeline"],tm)
  rec={"record_id":f'{case["case_id"]}:{eid[:16]}',"engine":case["engine"],"position_id":case["position_id"],
   "source_id":case["source_id"],"source_ply":case["source_ply"],"candidate_sha256":case["candidate_sha256"],
   "target_event_id":eid,"target_event_id_prefix":eid[:16],"target_side":"WINNER" if target_move==winner else "RIVAL",
   "target_candidate":move_doc(fen,target_move),"target_bound":BOUND_NAME[int(e["bound"])],
   "isolated_pair":pair,"effect_category":effect,"preference_boundary_crossed":effect=="DIRECT_PAIR_FLIP",
   "baseline":sem(base["semantic"]),"t_only":sem(t["semantic"]),"baseline_root":move_doc(fen,winner),"t_only_root":move_doc(fen,tm),
   "baseline_pv_san":pv_san(fen,base["semantic"].get("pv")),"t_only_pv_san":pv_san(fen,t["semantic"].get("pv")),
   "first_pv_divergence_ply":pv_div(base["semantic"].get("pv"),t["semantic"].get("pv")),
   "baseline_incumbent_timeline":base["incumbent_timeline"],"t_only_incumbent_timeline":t["incumbent_timeline"],
   "baseline_pair_exposure":{m:base_exp[m] for m in (winner,rival)},"t_only_pair_exposure":{m:t_exp[m] for m in (winner,rival)},
   "pair_exposure_delta":exposure_delta({m:base_exp[m] for m in (winner,rival)},{m:t_exp[m] for m in (winner,rival)}),
   "raw_tt_key_emitted":False}
  bs=rec["baseline_root"].get("san",winner);ts=rec["t_only_root"].get("san",tm)
  rec["candidate_branch_replacement"]=f"{bs} -> {ts}; target={rec['target_side']} {rec['target_bound']}; effect={effect}"
  records.append(rec)
 out={"schema":"c3x-g95-p13-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"source_id":case["source_id"],"qualified":True,"pair":pair,
  "fingerprint_public_summary":fp,"fingerprint_collision_count":len(collisions),"selected_targets":len(selected),
  "eligible_targets":eligible,"fired_targets":len(records),"address_misses":miss,"records":records,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P13_WORLD",case["case_id"],"eligible",eligible,"selected",len(selected),"fired",len(records),
       "flips",sum(r["effect_category"]=="DIRECT_PAIR_FLIP" for r in records))

def sig(r):
 return "|".join([r["target_side"],r["target_bound"],r["isolated_pair"]["gap_band"],r["effect_category"]])

def adjudicate(a):
 pre=load_freeze(a.freeze);worlds=[]
 for p in Path(a.worlds).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p13-world-v1":worlds.append(x)
 if len(worlds)!=48:raise SystemExit(f"P13_WORLD_N {len(worlds)}")
 rows=sorted([r for w in worlds for r in w["records"]],key=lambda z:z["record_id"])
 qcases=[c for c in pre["cases"] if c["qualification"]["qualified"]]
 worlds_with_targets=sum(1 for w in worlds if w.get("qualified") and int(w.get("selected_targets",0))>0)
 misses=sum(len(w.get("address_misses",[])) for w in worlds)
 gate=pre["support_gate"]
 support=(len(qcases)>=gate["min_qualified_worlds"] and len({c["engine"] for c in qcases})>=gate["min_qualified_engines"]
  and len({c["source_id"] for c in qcases})>=gate["min_qualified_sources"]
  and len({c["position_id"] for c in qcases})>=gate["min_qualified_positions"]
  and worlds_with_targets>=gate["min_worlds_with_selected_target"] and len(rows)>=gate["min_fired_target_records"]
  and misses<=gate["max_address_misses"])
 effects=Counter(r["effect_category"] for r in rows)
 flips=[r for r in rows if r["effect_category"]=="DIRECT_PAIR_FLIP"]
 groups=defaultdict(list)
 for r in flips:groups[sig(r)].append(r)
 req=pre["replication_rule"]["replicated_direct_pair_flip_requires"];rep=[]
 for k,v in groups.items():
  if len(v)>=req["witnesses"] and len({x["engine"] for x in v})>=req["engines"] and len({x["position_id"] for x in v})>=req["positions"] and len({x["source_id"] for x in v})>=req["sources"]:
   rep.append({"signature":k,"witnesses":len(v),"engines":sorted({x["engine"] for x in v}),
    "positions":len({x["position_id"] for x in v}),"sources":sorted({x["source_id"] for x in v})})
 if not support:verdict="P13_FRESH_SUPPORT_HOLD"
 elif rep:verdict="P13_REPLICATED_PAIRWISE_PREFERENCE_BOUNDARY_CAUSALITY"
 elif flips:verdict="P13_PAIRWISE_PREFERENCE_BOUNDARY_CAUSALITY_LOCAL_ONLY"
 elif effects.get("THIRD_MOVE_REDIRECT",0)>0:verdict="P13_ROOT_CANDIDATE_COMPETITION_REDIRECTION_WITHOUT_PAIRWISE_BOUNDARY_REPLICATION"
 else:verdict="P13_NO_ROOT_PREFERENCE_BOUNDARY_EFFECT_UNDER_FROZEN_EXACT_EVENT_INTERVENTION"
 out={"schema":"c3x-g95-p13-adjudication-v1","scientific_stage":STAGE,"status":"CLOSED_PASS" if support else "HOLD",
  "verdict":verdict,"world_count":len(worlds),"support":{"pass":support,"qualified_worlds":len(qcases),
   "qualified_engines":sorted({c["engine"] for c in qcases}),"qualified_sources":sorted({c["source_id"] for c in qcases}),
   "qualified_positions":len({c["position_id"] for c in qcases}),"worlds_with_selected_target":worlds_with_targets,
   "fired_target_records":len(rows),"address_misses":misses},
  "effect_counts":dict(sorted(effects.items())),"direct_pair_flip_per_engine":dict(sorted(Counter(r["engine"] for r in flips).items())),
  "direct_pair_flip_per_source":dict(sorted(Counter(r["source_id"] for r in flips).items())),
  "replicated_direct_pair_flip_signatures":rep,"records":rows,"claim_ceiling":pre["claim_ceiling"],"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 lines=["# C3X G9.5-P13 — Root-Candidate Competition Diagnostic","",f"Status: **{out['status']} / {verdict}**",
  f"Qualified worlds: **{len(qcases)} / 48**; fired exact targets: **{len(rows)}**; direct W→R flips: **{len(flips)}**; third-move redirects: **{effects.get('THIRD_MOVE_REDIRECT',0)}**","",
  "## Preference-boundary witnesses"]
 if flips:
  for r in flips:
   w=r["baseline_root"];t=r["t_only_root"];p=r["isolated_pair"]
   lines.append(f"- {r['engine']} / {r['position_id']} @ source ply {r['source_ply']}: {w.get('san',w['uci'])} → {t.get('san',t['uci'])}; isolated gap={p['gap_cp_signed']} cp ({p['gap_band']}); target={r['target_side']}/{r['target_bound']}.")
 else:lines.append("- None.")
 lines+=["","## Replicated direct-pair signatures"]
 if rep:
  for z in rep:lines.append(f"- {z['signature']}: witnesses={z['witnesses']}; engines={','.join(z['engines'])}; positions={z['positions']}; sources={','.join(z['sources'])}")
 else:lines.append("- None under the frozen rule.")
 lines+=["","Root-child exposure is semantic-event exposure, not candidate-specific node allocation. Raw TT keys are not emitted."]
 Path(a.markdown).write_text("\n".join(lines)+"\n")
 print("P13_ADJUDICATE",verdict,out["support"])

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("design");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p12-closure",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=design)
 q=sp.add_parser("qualify");q.add_argument("--design",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=qualify)
 q=sp.add_parser("freeze");q.add_argument("--design",required=True);q.add_argument("--qualifications",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=freeze)
 q=sp.add_parser("case");q.add_argument("--freeze",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("adjudicate");q.add_argument("--freeze",required=True);q.add_argument("--worlds",required=True);q.add_argument("--out",required=True);q.add_argument("--markdown",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
