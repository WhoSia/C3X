#!/usr/bin/env python3
import argparse,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
import chess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P12"
ENGINES=("stockfish_19","berserk","ethereal")
BOUND_NAME={1:"UPPER",2:"LOWER"}

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

def depth_band(d):
 d=int(d)
 return "LE4" if d<=4 else "D5_8" if d<=8 else "D9_12" if d<=12 else "D13_PLUS"

def win_width(e):return int(e["beta"])-int(e["alpha"])
def win_class(e):
 w=win_width(e)
 return "NULL" if w<=1 else "NARROW" if w<=32 else "WIDE"
def fail_dir(e):
 v,a,b=int(e["tt_value"]),int(e["alpha"]),int(e["beta"])
 return "FAIL_HIGH" if v>=b else "FAIL_LOW" if v<=a else "INSIDE"

def prior_same_key(events,i):
 e=events[i];same=[z for z in events[:i] if z.get("key")==e.get("key")]
 return same

def cutoff_doc(events,i,target_i):
 e=events[i];same=prior_same_key(events,i);prev=same[-1] if same else None
 if prev is None:kind="FIRST_KEY"
 else:
  pc,pw=win_class(prev),win_width(prev);cc,cw=win_class(e),win_width(e)
  if int(prev.get("ply",-99))==int(e["ply"]) and pc in ("NULL","NARROW") and cw>pw:kind="WIDENING_RESEARCH_PROXY"
  elif int(prev.get("ply",-99))==int(e["ply"]) and (pc!=cc or fail_dir(prev)!=fail_dir(e)):kind="WINDOW_RELATION_CHANGE"
  elif int(prev.get("alpha",0))==int(e["alpha"]) and int(prev.get("beta",0))==int(e["beta"]):kind="SAME_WINDOW_REVISIT"
  else:kind="OTHER_REVISIT"
 return {
  "event_id":e["address_id"],"event_id_prefix":e["address_id"][:16],"scope":e["scope"],"ply":int(e["ply"]),"depth":int(e["depth"]),
  "alpha":int(e["alpha"]),"beta":int(e["beta"]),"window_width":win_width(e),"window_class":win_class(e),
  "tt_value":int(e["tt_value"]),"bound":BOUND_NAME.get(int(e.get("bound",0)),str(e.get("bound"))),
  "tt_move_present":bool(int(e.get("tt_move",0))),"payload":int(e.get("payload",0)),"fail_direction":fail_dir(e),
  "same_key_prior_count":len(same),"same_key_prior_window_class":None if prev is None else win_class(prev),
  "same_key_prior_depth":None if prev is None else int(prev["depth"]),"same_key_revisit_kind":kind,
  "trace_ordinal":i,"distance_from_target":i-target_i
 }

def select_targets(events,maxn):
 rows=[]
 for i,e in enumerate(events):
  if e.get("class")!="MOVE_ORDER_SEED" or e.get("scope")!="MAIN" or int(e.get("ply",-1))!=1:continue
  d=int(e.get("depth",0));b=int(e.get("bound",0))
  if not (5<=d<=8) or b not in (1,2) or int(e.get("tt_move",0))==0:continue
  same=[z for z in events[:i] if z.get("key")==e.get("key")]
  if not same or int(same[-1].get("tt_move",0))!=int(e.get("tt_move",0)):continue
  rows.append((e["address_id"],i,e))
 rows.sort(key=lambda z:z[0])
 return rows[:maxn],len(rows)

def cutoff_pair(base_events,t_events,base_target_i,t_target_i):
 a=[(i,e) for i,e in enumerate(base_events) if i>base_target_i and e.get("class")=="CUTOFF"]
 b=[(i,e) for i,e in enumerate(t_events) if i>t_target_i and e.get("class")=="CUTOFF"]
 j=0
 while j<min(len(a),len(b)) and a[j][1]["address_id"]==b[j][1]["address_id"]:j+=1
 if j==len(a)==len(b):return None,None
 return (a[j] if j<len(a) else None),(b[j] if j<len(b) else None)

def address(e):
 z=dict(e["address"]);z["address_id"]=e["address_id"];return z

def move_doc(fen,uci):
 if not uci:return None
 b=chess.Board(fen)
 try:m=chess.Move.from_uci(uci)
 except:return {"uci":uci,"legal":False}
 if m not in b.legal_moves:return {"uci":uci,"legal":False}
 return {"uci":uci,"san":b.san(m),"legal":True,"capture":b.is_capture(m),"check":b.gives_check(m),
         "castling":b.is_castling(m),"promotion":bool(m.promotion)}

def pv_san(fen,pv,limit=8):
 if isinstance(pv,str):moves=[x for x in pv.split() if x]
 elif isinstance(pv,list):moves=[str(x) for x in pv]
 else:moves=[]
 b=chess.Board(fen);out=[]
 for u in moves[:limit]:
  try:m=chess.Move.from_uci(u)
  except:break
  if m not in b.legal_moves:break
  out.append(b.san(m));b.push(m)
 return out

def pv_div(a,b):
 def xs(v):
  if isinstance(v,str):return [x for x in v.split() if x]
  return list(v or [])
 a,b=xs(a),xs(b);i=0
 while i<min(len(a),len(b)) and a[i]==b[i]:i+=1
 return None if i==len(a)==len(b) else i

def precommit(a):
 c=load(a.constitution);corp=load(a.corpus);p11=load(a.p11_closure)
 if c.get("schema")!="c3x-g95-p12-constitution-v1" or p11.get("receipt_sha256")!=c["parent"]["closure_receipt_sha256"]:raise SystemExit("P12_PARENT")
 if corp.get("schema")!="c3x-g95-p12-corpus-v1" or corp["selection"]["engine_outcomes_consulted"] is not False:raise SystemExit("P12_CORPUS")
 builds=Path(a.build_dir);variants={}
 for e in ENGINES:
  fs=list(builds.rglob(f"c3x-p12-{e}"))
  if len(fs)!=1:raise SystemExit(f"P12_BUILD {e} {len(fs)}")
  variants[e]={"sha256":sha_file(fs[0]),"protocol":p32.protocol_for(e)}
 cases=[]
 for pos in corp["positions"]:
  for e in ENGINES:
   cases.append({"case_id":f'p12:{e}:{pos["position_id"]}',"engine":e,"position_id":pos["position_id"],
    "source_id":pos["source_id"],"source_ply":pos["source_ply"],"candidate_sha256":pos["candidate_sha256"],
    "cell":pos["cell"],"complexity":pos["complexity"]})
 if len(cases)!=36:raise SystemExit("P12_CASE_COUNT")
 out={"schema":"c3x-g95-p12-precommit-v1","scientific_stage":STAGE,"selective_p12_outcomes_consulted":False,
      "constitution_sha256":digest(c),"corpus_sha256":digest(corp),"parent_p11_receipt_sha256":p11["receipt_sha256"],
      "variants":variants,"execution":c["execution"],"support_gate":c["support_gate"],"replication_rule":c["replication_rule"],
      "claim_ceiling":c["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P12_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def load_pre(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p12-precommit-v1" or x.get("selective_p12_outcomes_consulted") is not False:raise SystemExit("P12_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P12_PRE_HASH")
 return x

def case_run(a):
 pre=load_pre(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P12_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P12_BINARY")
 root=Path(a.out).parent/".p12-private";root.mkdir(parents=True,exist_ok=True)
 base=p32.run_history(a.binary,v["protocol"],case["cell"],"CATALOG","ALL",8,None,root/"base")
 selected,eligible=select_targets(base["trace"]["events"],int(pre["execution"]["max_targets_per_world"]))
 records=[];miss=[]
 fen=case["cell"]["fen"]
 for j,(eid,bi,e) in enumerate(selected):
  t=p32.run_history(a.binary,v["protocol"],case["cell"],"REMOVE_SET","ALL",8,[address(e)],root/f"{j:02d}-t")
  tmatches=[(i,z) for i,z in enumerate(t["trace"]["events"]) if z["address_id"]==eid]
  fired=bool(t["trace"]["targets"] and t["trace"]["targets"][0]["fired"])
  if not fired or len(tmatches)!=1:
   miss.append({"event_id_prefix":eid[:16],"fired":fired,"trace_matches":len(tmatches)});continue
  ti=tmatches[0][0];bm=base["semantic"].get("bestmove");tm=t["semantic"].get("bestmove")
  rec={"record_id":f'{case["case_id"]}:{eid[:16]}',"engine":case["engine"],"position_id":case["position_id"],
       "source_id":case["source_id"],"source_ply":case["source_ply"],"candidate_sha256":case["candidate_sha256"],
       "target_event_id":eid,"target_event_id_prefix":eid[:16],"target_bound":BOUND_NAME[int(e["bound"])],
       "root_change":tm!=bm,"baseline":sem(base["semantic"]),"t_only":sem(t["semantic"]),
       "legal_root_move_count":chess.Board(fen).legal_moves.count(),"baseline_root":move_doc(fen,bm),"t_only_root":move_doc(fen,tm),
       "first_pv_divergence_ply":pv_div(base["semantic"].get("pv"),t["semantic"].get("pv")),
       "baseline_pv_san":pv_san(fen,base["semantic"].get("pv")),"t_only_pv_san":pv_san(fen,t["semantic"].get("pv")),
       "cutoff_B":None,"cutoff_C":None,"b_only":None,"t_plus_c":None,"mediation_verdict":None,
       "raw_tt_key_emitted":False}
  if not rec["root_change"]:
   rec["mediation_verdict"]="NO_ROOT_CHANGE";records.append(rec);continue
  bp,cp=cutoff_pair(base["trace"]["events"],t["trace"]["events"],bi,ti)
  if bp is None and cp is None:
   rec["mediation_verdict"]="NO_EXACT_CUTOFF_PAIR";records.append(rec);continue
  bmove=None;cmove=None;bfired=None;tfired=None;cfired=None
  if bp is not None:
   bidx,be=bp;rec["cutoff_B"]=cutoff_doc(base["trace"]["events"],bidx,bi)
   br=p32.run_history(a.binary,v["protocol"],case["cell"],"REMOVE_SET","ALL",8,[address(be)],root/f"{j:02d}-b")
   bfired=bool(br["trace"]["targets"] and br["trace"]["targets"][0]["fired"]);bmove=br["semantic"].get("bestmove")
   rec["b_only"]={"target_fired":bfired,"semantic":sem(br["semantic"]),"root":move_doc(fen,bmove),"pv_san":pv_san(fen,br["semantic"].get("pv"))}
  if cp is not None:
   cidx,ce=cp;rec["cutoff_C"]=cutoff_doc(t["trace"]["events"],cidx,ti)
   xr=p32.run_history(a.binary,v["protocol"],case["cell"],"REMOVE_SET","ALL",8,[address(e),address(ce)],root/f"{j:02d}-tc")
   fires=[bool(z["fired"]) for z in xr["trace"]["targets"]];tfired=fires[0] if fires else False;cfired=fires[1] if len(fires)>1 else False
   cmove=xr["semantic"].get("bestmove")
   rec["t_plus_c"]={"target_fired":tfired,"cutoff_fired":cfired,"semantic":sem(xr["semantic"]),"root":move_doc(fen,cmove),"pv_san":pv_san(fen,xr["semantic"].get("pv"))}
  if (bp is not None and not bfired) or (cp is not None and not (tfired and cfired)):
   verdict="ADDRESS_DRIFT"
  else:
   suff=bp is not None and bmove==tm
   nec=cp is not None and cmove==bm
   third=(bp is not None and bmove not in (bm,tm)) or (cp is not None and cmove not in (bm,tm))
   if third:verdict="EXACT_CUTOFF_INTERACTION_REDIRECT"
   elif suff and nec:verdict="EXACT_CUTOFF_BRIDGE"
   elif suff:verdict="BASELINE_CUTOFF_SUFFICIENCY_ONLY"
   elif nec:verdict="COUNTERFACTUAL_CUTOFF_NECESSITY_ONLY"
   else:verdict="CUTOFF_COLOCATION_ONLY"
  rec["mediation_verdict"]=verdict
  rec["candidate_branch_replacement"]=f'{rec["baseline_root"].get("san",bm)} -> {rec["t_only_root"].get("san",tm)}; exact cutoff verdict={verdict}'
  records.append(rec)
 out={"schema":"c3x-g95-p12-world-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
      "position_id":case["position_id"],"source_id":case["source_id"],"eligible_targets":eligible,"selected_targets":len(selected),
      "fired_targets":len(records),"root_change_targets":sum(r["root_change"] for r in records),"missed_targets":miss,
      "records":records,"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P12_WORLD",case["case_id"],"eligible",eligible,"selected",len(selected),"fired",len(records),"root",out["root_change_targets"])

def sig(r):
 def side(z):
  if not z:return "NONE"
  return ":".join(str(z.get(k)) for k in ("fail_direction","window_class","same_key_revisit_kind"))
 return "|".join([r["target_bound"],side(r.get("cutoff_B")),side(r.get("cutoff_C")),r["mediation_verdict"]])

def adjudicate(a):
 pre=load_pre(a.precommit);worlds=[]
 for p in Path(a.worlds).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p12-world-v1":worlds.append(x)
 if len(worlds)!=36:raise SystemExit(f"P12_WORLD_N {len(worlds)}")
 rows=sorted([r for w in worlds for r in w["records"]],key=lambda z:z["record_id"])
 fired=len(rows);pos=[r for r in rows if r["root_change"]]
 pairs=[r for r in pos if r.get("cutoff_B") is not None or r.get("cutoff_C") is not None]
 mednames={"EXACT_CUTOFF_BRIDGE","BASELINE_CUTOFF_SUFFICIENCY_ONLY","COUNTERFACTUAL_CUTOFF_NECESSITY_ONLY"}
 mediated=[r for r in pos if r["mediation_verdict"] in mednames]
 engines=sorted({r["engine"] for r in pos});sources=sorted({r["source_id"] for r in pos});positions=sorted({r["position_id"] for r in pos})
 gate=pre["support_gate"]
 support=(fired>=gate["min_fired_target_records"] and len(pos)>=gate["min_root_change_targets"] and
          len(engines)>=gate["min_positive_engines"] and len(sources)>=gate["min_positive_sources"] and
          len(positions)>=gate["min_sensitive_positions"] and len(pairs)>=gate["min_exact_cutoff_pairs"] and
          len(mediated)>=gate["min_exact_bridge_or_one_sided_mediation"])
 groups=defaultdict(list)
 for r in pos:groups[sig(r)].append(r)
 req=pre["replication_rule"]["replicated_signature_requires"];rep=[]
 for k,v in groups.items():
  if len(v)>=req["root_change_witnesses"] and len({x["engine"] for x in v})>=req["positive_engines"] and len({x["position_id"] for x in v})>=req["positions"] and len({x["source_id"] for x in v})>=req["sources"]:
   rep.append({"signature":k,"witnesses":len(v),"engines":sorted({x["engine"] for x in v}),"positions":len({x["position_id"] for x in v}),"sources":sorted({x["source_id"] for x in v})})
 if not support:verdict="P12_FRESH_SUPPORT_HOLD"
 elif rep:verdict="P12_REPLICATED_EXACT_CUTOFF_MEDIATION"
 elif mediated:verdict="P12_EXACT_CUTOFF_MEDIATION_IDENTIFIED_REPLICATION_HOLD"
 else:verdict="P12_CUTOFF_COLOCATION_ONLY"
 out={"schema":"c3x-g95-p12-adjudication-v1","scientific_stage":STAGE,"status":"CLOSED_PASS" if support else "HOLD","verdict":verdict,
  "support":{"pass":support,"fired_target_records":fired,"root_change_targets":len(pos),"positive_engines":engines,
             "positive_sources":sources,"sensitive_positions":len(positions),"exact_cutoff_pairs":len(pairs),"mediated_targets":len(mediated)},
  "mediation_status_counts":dict(sorted(Counter(r["mediation_verdict"] for r in pos).items())),
  "root_change_per_engine":dict(sorted(Counter(r["engine"] for r in pos).items())),
  "root_change_per_source":dict(sorted(Counter(r["source_id"] for r in pos).items())),
  "replicated_transition_signatures":rep,"world_count":len(worlds),"records":rows,
  "claim_ceiling":pre["claim_ceiling"],"raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 lines=["# C3X G9.5-P12 — Chess-Native Exact-Cutoff Diagnostic","",f"Status: **{out['status']} / {verdict}**",
        f"Fresh target records: **{fired}**; ROOT_CHANGE: **{len(pos)}**; exact cutoff pairs: **{len(pairs)}**; mediated: **{len(mediated)}**","",
        "## Root-choice witnesses"]
 for r in pos:
  b=r["baseline_root"] or {};t=r["t_only_root"] or {};B=r.get("cutoff_B") or {};C=r.get("cutoff_C") or {}
  lines.append(f"- {r['engine']} / {r['position_id']} @ source ply {r['source_ply']}: {b.get('san',b.get('uci'))} -> {t.get('san',t.get('uci'))}; B={B.get('fail_direction','none')}/{B.get('window_class','none')}; C={C.get('fail_direction','none')}/{C.get('window_class','none')}; {r['mediation_verdict']}")
 lines += ["","## Replicated transition signatures"]
 if rep:
  for z in rep:lines.append(f"- {z['signature']}: witnesses={z['witnesses']}; engines={','.join(z['engines'])}; positions={z['positions']}; sources={','.join(z['sources'])}")
 else:lines.append("- None under the frozen replication rule.")
 lines += ["","Raw TT keys are not emitted. Re-search/PVS status is an operational same-key/window-transition proxy only."]
 Path(a.markdown).write_text("\n".join(lines)+"\n")
 print("P12_ADJUDICATE",verdict,out["support"])

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p11-closure",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("adjudicate");q.add_argument("--precommit",required=True);q.add_argument("--worlds",required=True);q.add_argument("--out",required=True);q.add_argument("--markdown",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
