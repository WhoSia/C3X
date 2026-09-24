#!/usr/bin/env python3
import argparse,hashlib,json,os,re,subprocess
from collections import defaultdict
from pathlib import Path
TARGETS=("frozen_20260810","stockfish_19")
REGIMES={"R125K":{"nodes":125000,"H_min":32,"U_min":8},"R200K":{"nodes":200000,"H_min":48,"U_min":12},"R300K":{"nodes":300000,"H_min":64,"U_min":16},"R450K":{"nodes":450000,"H_min":80,"U_min":20},"R700K":{"nodes":700000,"H_min":112,"U_min":28}}
ARMS={"00":"SHAM","10":"MASK_MAIN","01":"MASK_QSEARCH","11":"MASK_MAIN_QSEARCH","ALL":"MASK_ALL"}
SITES=("MAIN","SUCCESSOR","QSEARCH")
SEM_FIELDS=("bestmove","score","wdl","pv")
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha_obj(o):return hashlib.sha256(canon(o)).hexdigest()
def bins(items):
 o={}
 for x in items:
  k,p=x.split("=",1);o[k]=p
 if set(o)!=set(TARGETS):raise SystemExit("need both engine targets")
 return o
def run_search(binary,fen,mode,nodes):
 p=subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
 for c in ["uci",f"setoption name C3X_TTReadMode value {mode}","setoption name C3X_Telemetry value true","setoption name Threads value 1","setoption name Hash value 64","setoption name SyzygyProbeLimit value 0","setoption name UCI_ShowWDL value true","setoption name Clear Hash","isready",f"position fen {fen}",f"go nodes {nodes}"]:p.stdin.write(c+"\n")
 p.stdin.flush();lines=[]
 for line in p.stdout:
  line=line.rstrip("\n");lines.append(line)
  if line.startswith("bestmove "):break
 p.terminate()
 try:rest,_=p.communicate(timeout=5)
 except subprocess.TimeoutExpired:p.kill();rest,_=p.communicate(timeout=5)
 if rest:lines.extend(rest.splitlines())
 best=next((x for x in reversed(lines) if x.startswith("bestmove ")),None);infos=[x for x in lines if x.startswith("info depth ") and " score " in x and " pv " in x];tel=next((x for x in lines if x.startswith("info string c3x_ttread_v1 ")),None)
 if not best or not infos or not tel:raise RuntimeError("incomplete UCI receipt\n"+"\n".join(lines[-80:]))
 final=infos[-1];bt=best.split()
 def grab(pat):
  m=re.search(pat,final);return m.group(1) if m else None
 t={}
 for tok in tel.split()[3:]:
  if "=" in tok:
   k,v=tok.split("=",1)
   try:t[k]=int(v)
   except:t[k]=v
 return {"semantic":{"bestmove":bt[1],"depth":int(grab(r"\bdepth (\d+)") or 0),"seldepth":int(grab(r"\bseldepth (\d+)") or 0),"score":grab(r"\bscore ((?:cp|mate) -?\d+)"),"wdl":grab(r"\bwdl (\d+ \d+ \d+)"),"nodes":int(grab(r"\bnodes (\d+)") or 0),"pv":grab(r"\bpv (.+)$")},"telemetry":t,"telemetry_line":tel}
def site_uses(t):
 return {"MAIN":int(t.get("use_main_eval",0))+int(t.get("use_main_value",0))+int(t.get("use_main_cutoff_gate",0)),"SUCCESSOR":int(t.get("use_successor_value",0)),"QSEARCH":int(t.get("use_qsearch_eval",0))+int(t.get("use_qsearch_value",0))+int(t.get("use_qsearch_cutoff",0))}
def engagement(r,regime):
 t=r["telemetry"];hits={"MAIN":int(t.get("raw_hits_main",0)),"SUCCESSOR":int(t.get("raw_hits_successor",0)),"QSEARCH":int(t.get("raw_hits_qsearch",0))};uses=site_uses(t);H=sum(hits.values());U=sum(uses.values());g=REGIMES[regime]
 passed=H>=g["H_min"] and U>=g["U_min"] and all(hits[s]>0 for s in SITES) and all(uses[s]>0 for s in SITES)
 return {"H":H,"U":U,"B":sum(uses[s]>0 for s in SITES),"raw_hits_by_site":hits,"semantic_uses_by_site":uses,"site_use_floor":min(uses.values()),"passed":passed}
def world_value(c,move):
 m=next((x for x in c["world"]["moves"] if x["uci"]==move),None)
 return None if m is None else {"wdl":int(m["mover_wdl"]),"precise_dtz":int(m["mover_precise_dtz"])}
def select(rows,target=30):
 st=defaultdict(list)
 for r in rows:
  floors=[r["engagement"][g][t]["site_use_floor"] for g in REGIMES for t in TARGETS];r["selection_floor"]=min(floors);st[(r["candidate"]["material_signature"],r["candidate"]["side_to_move"])].append(r)
 for k in st:st[k].sort(key=lambda r:(-r["selection_floor"],-int(r["candidate"]["tau4"]["tau4"]),r["candidate"]["candidate_sha256"]))
 keys=sorted(st);out=[];i=0
 while len(out)<target:
  prog=False
  for k in keys:
   if i<len(st[k]) and len(out)<target:out.append(st[k][i]);prog=True
  if not prog:break
  i+=1
 return out
def sham_commit(a):
 stage=json.loads(Path(a.stage_a).read_text());b=bins(a.binary);rows=[]
 for i,c in enumerate(stage["candidates"],1):
  sham={};eg={};allpass=True
  for g,cfg in REGIMES.items():
   sham[g]={};eg[g]={}
   for t,p in b.items():
    r=run_search(p,c["fen"],"SHAM",cfg["nodes"]);sham[g][t]=r;eg[g][t]=engagement(r,g);allpass=allpass and eg[g][t]["passed"]
  rows.append({"candidate":c,"sham":sham,"engagement":eg,"all_regimes_both_targets_engaged":allpass})
  print(f"SHAM {i:02d}/{len(stage['candidates'])} id={c['candidate_sha256'][:12]} pass={allpass}",flush=True)
 eligible=[r for r in rows if r["all_regimes_both_targets_engaged"]];chosen=select(eligible);mats={r["candidate"]["material_signature"] for r in chosen};turns={r["candidate"]["side_to_move"] for r in chosen};ready=len(chosen)>=28 and len(mats)>=6 and turns=={"WHITE","BLACK"}
 payload={"schema":"c3x-p17-sham-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P17","stage_a_pool_sha256":stage["pool_sha256"],"intervention_outcomes_consulted":False,"regimes":REGIMES,"binaries":{t:{"sha256":sha_file(p),"path_basename":os.path.basename(p)} for t,p in b.items()},"runtime":{"threads":1,"hash_mib":64,"clear_hash_each_arm":True,"syzygy_probe_limit":0},"counts":{"stage_a":len(rows),"six_surface_engaged":len(eligible),"committed":len(chosen),"material_signatures":len(mats),"sides_to_move":sorted(turns)},"authorization":"P17-WINDOW-READY" if ready else "P17-ENGAGEMENT-HOLD","committed_cells":chosen};payload["precommit_sha256"]=sha_obj(payload)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print("P17_PRECOMMIT",payload["authorization"],payload["precommit_sha256"],payload["counts"])
 if not ready:raise SystemExit(2)
def regime_run(a):
 pre=json.loads(Path(a.precommit).read_text());b=bins(a.binary);g=a.regime;cfg=REGIMES[g]
 if pre["authorization"]!="P17-WINDOW-READY":raise SystemExit("P17-HOLD")
 for t,p in b.items():
  if sha_file(p)!=pre["binaries"][t]["sha256"]:raise SystemExit("BINARY-IDENTITY-FAIL "+t)
 rows=[]
 for i,row in enumerate(pre["committed_cells"],1):
  c=row["candidate"];o={"candidate_sha256":c["candidate_sha256"],"material_signature":c["material_signature"],"side_to_move":c["side_to_move"],"fen":c["fen"],"targets":{}}
  for t,p in b.items():
   baseline=run_search(p,c["fen"],"SHAM",cfg["nodes"]);sealed=row["sham"][g][t]
   if any(baseline["semantic"][f]!=sealed["semantic"][f] for f in SEM_FIELDS):raise SystemExit(f"SEALED-SHAM-REPLAY-FAIL {g} {t} {c['candidate_sha256']}")
   sv=world_value(c,baseline["semantic"]["bestmove"])
   if sv is None:raise SystemExit("WORLD-JOIN-FAIL SHAM")
   arms={"00":{"mode":"SHAM","receipt":baseline,"world":sv,"action_changed":False,"fine_changed":False,"coarse_changed":False}}
   for bits in ("10","01","11","ALL"):
    rr=run_search(p,c["fen"],ARMS[bits],cfg["nodes"]);wv=world_value(c,rr["semantic"]["bestmove"])
    if wv is None:raise SystemExit("WORLD-JOIN-FAIL "+bits)
    arms[bits]={"mode":ARMS[bits],"receipt":rr,"world":wv,"action_changed":rr["semantic"]["bestmove"]!=baseline["semantic"]["bestmove"],"fine_changed":(wv["wdl"],wv["precise_dtz"])!=(sv["wdl"],sv["precise_dtz"]),"coarse_changed":wv["wdl"]!=sv["wdl"],"precise_dtz_delta":wv["precise_dtz"]-sv["precise_dtz"]}
   o["targets"][t]={"arms":arms}
  rows.append(o);print(f"REGIME {g} {i:02d}/{len(pre['committed_cells'])} {c['candidate_sha256'][:12]}",flush=True)
 payload={"schema":"c3x-p17-regime-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P17","regime":g,"nodes":cfg["nodes"],"precommit_sha256":pre["precommit_sha256"],"binary_sha256":{t:sha_file(p) for t,p in b.items()},"sealed_sham_replay":"PASS","rows":rows};payload["result_sha256"]=sha_obj(payload)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print("P17_REGIME_PASS",g,payload["result_sha256"])
def phase_label(m,q,mq,n):
 inter=mq-m-q;floor=2/n;margin=1/n;vals={"MAIN":abs(m),"QSEARCH":abs(q),"INTERACTION":abs(inter)}
 ordered=sorted(vals.items(),key=lambda x:(-x[1],x[0]))
 if ordered[0][1]<floor:return "NULL",inter,vals
 if ordered[0][1]-ordered[1][1]<margin:return "MIXED",inter,vals
 return ordered[0][0]+"-DOMINANT",inter,vals
def jacc(a,b):
 return 1.0 if not a and not b else len(a&b)/len(a|b) if a|b else 1.0
def aggregate(a):
 pre=json.loads(Path(a.precommit).read_text());res={}
 for x in a.result:
  g,p=x.split("=",1);res[g]=json.loads(Path(p).read_text())
 if set(res)!=set(REGIMES):raise SystemExit("need all regimes")
 n=pre["counts"]["committed"];summary={};sets={}
 for t in TARGETS:
  summary[t]={};sets[t]={}
  for g in REGIMES:
   rows=res[g]["rows"];rates={};sets[t][g]={}
   for bits in ("10","01","11","ALL"):
    fine={r["candidate_sha256"] for r in rows if r["targets"][t]["arms"][bits]["fine_changed"]};action={r["candidate_sha256"] for r in rows if r["targets"][t]["arms"][bits]["action_changed"]};coarse={r["candidate_sha256"] for r in rows if r["targets"][t]["arms"][bits]["coarse_changed"]}
    rates[bits]={"fine":len(fine)/n,"action":len(action)/n,"coarse":len(coarse)/n,"fine_count":len(fine),"action_count":len(action),"coarse_count":len(coarse)};sets[t][g][bits]=fine
   label,inter,components=phase_label(rates["10"]["fine"],rates["01"]["fine"],rates["11"]["fine"],n)
   summary[t][g]={"phase":label,"rates":rates,"fine_mobius_main_x_qsearch":inter,"phase_component_abs":components}
 order=list(REGIMES)
 def window_for(t):
  phases=[summary[t][g]["phase"] for g in order]
  inter=[summary[t][g]["fine_mobius_main_x_qsearch"] for g in order]
  interior=[1,2,3];adjacent_pairs=[(1,2),(2,3)]
  qualifying=[i for i in interior if phases[i]=="INTERACTION-DOMINANT" and inter[i]<0]
  pair=next(((i,j) for i,j in adjacent_pairs if i in qualifying and j in qualifying),None)
  flanks_non_inter=(phases[0]!="INTERACTION-DOMINANT" and phases[4]!="INTERACTION-DOMINANT")
  at_least_one_null=(phases[0]=="NULL" or phases[4]=="NULL")
  most_negative=min(range(len(inter)),key=lambda i:inter[i])
  interior_peak=most_negative in interior
  replicate=bool(pair and at_least_one_null and flanks_non_inter and interior_peak)
  strict=bool(pair and flanks_non_inter and interior_peak)
  onset=None;exitb=None
  if qualifying:
   first=min(qualifying);last=max(qualifying)
   onset=[order[first-1],order[first]] if first>0 else None
   exitb=[order[last],order[last+1]] if last<len(order)-1 else None
  return {"phase_sequence":phases,"interaction_sequence":inter,"qualifying_negative_interaction_regimes":[order[i] for i in qualifying],"adjacent_interior_pair":[order[pair[0]],order[pair[1]]] if pair else None,"at_least_one_flank_null":at_least_one_null,"both_flanks_non_interaction":flanks_non_inter,"most_negative_regime":order[most_negative],"interior_peak":interior_peak,"replication_gate":replicate,"strict_bounded_window":strict,"onset_bracket":onset,"extinction_bracket":exitb}
 windows={t:window_for(t) for t in TARGETS}
 def idx_bracket(b):
  if not b:return None
  return (order.index(b[0]),order.index(b[1]))
 cross=False
 if all(windows[t]["strict_bounded_window"] for t in TARGETS):
  a0=idx_bracket(windows[TARGETS[0]]["onset_bracket"]);a1=idx_bracket(windows[TARGETS[1]]["onset_bracket"]);e0=idx_bracket(windows[TARGETS[0]]["extinction_bracket"]);e1=idx_bracket(windows[TARGETS[1]]["extinction_bracket"])
  cross=bool(a0 and a1 and e0 and e1 and abs(a0[0]-a1[0])<=1 and abs(e0[0]-e1[0])<=1)
 diagnostics={}
 for t in TARGETS:
  diagnostics[t]={}
  for bits in ("10","01","11","ALL"):
   diagnostics[t][bits]={}
   for a0,b0 in zip(order,order[1:]):
    diagnostics[t][bits][a0+"_"+b0]=jacc(sets[t][a0][bits],sets[t][b0][bits])
 any_coarse=any(summary[t][g]["rates"][bits]["coarse_count"] for t in TARGETS for g in REGIMES for bits in ("10","01","11","ALL"))
 sf=windows["stockfish_19"]
 if sf["replication_gate"] and cross:verdict="CROSS-VERSION-BOUNDED-INTERACTION-WINDOW"
 elif sf["replication_gate"]:verdict="SF19-BOUNDED-INTERACTION-WINDOW-REPLICATED"
 elif sf["strict_bounded_window"]:verdict="SF19-STRICT-WINDOW-WITHOUT-PRIMARY-REPLICATION-GATE"
 else:verdict="BOUNDED-INTERACTION-WINDOW-NOT-REPLICATED"
 payload={"schema":"c3x-p17-window-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P17","precommit_sha256":pre["precommit_sha256"],"causal_field":summary,"bounded_window":windows,"cross_version_boundary_transport":cross,"cell_surface_jaccard":diagnostics,"robust_wdl_changed_any_arm":any_coarse,"primary_verdict":verdict,"authority_ceiling":"fresh P17-only exact worlds under prospectively frozen dense fixed-node ladder and dual-engine selective TT-read interventions; no representation/cognition/general-chess inference"};payload["result_sha256"]=sha_obj(payload)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print("P17_RESULT",verdict,windows,payload["result_sha256"])

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 s=sp.add_parser("sham-commit");s.add_argument("--stage-a",required=True);s.add_argument("--binary",action="append",required=True);s.add_argument("--out",required=True)
 r=sp.add_parser("regime-run");r.add_argument("--precommit",required=True);r.add_argument("--binary",action="append",required=True);r.add_argument("--regime",choices=list(REGIMES),required=True);r.add_argument("--out",required=True)
 g=sp.add_parser("aggregate");g.add_argument("--precommit",required=True);g.add_argument("--result",action="append",required=True);g.add_argument("--out",required=True)
 a=ap.parse_args();{"sham-commit":sham_commit,"regime-run":regime_run,"aggregate":aggregate}[a.cmd](a)
if __name__=="__main__":main()
