#!/usr/bin/env python3
import argparse, hashlib, itertools, json, os, re, subprocess
from collections import defaultdict
from pathlib import Path

TARGETS=("frozen_20260810","stockfish_19")
ARMS={
 "000":"SHAM",
 "100":"MASK_MAIN",
 "010":"MASK_SUCCESSOR",
 "001":"MASK_QSEARCH",
 "110":"MASK_MAIN_SUCCESSOR",
 "101":"MASK_MAIN_QSEARCH",
 "011":"MASK_SUCCESSOR_QSEARCH",
 "111":"MASK_ALL"
}
SITES=("MAIN","SUCCESSOR","QSEARCH")
SITE_BIT={"MAIN":0,"SUCCESSOR":1,"QSEARCH":2}

def sha256_file(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha256_obj(o):return hashlib.sha256(canon(o)).hexdigest()

def parse_binaries(items):
 out={}
 for x in items:
  k,p=x.split("=",1);out[k]=p
 if set(out)!=set(TARGETS):raise SystemExit("need exactly frozen_20260810 and stockfish_19 binaries")
 return out

def run_search(binary,fen,mode,nodes):
 p=subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
 cmds=["uci",f"setoption name C3X_TTReadMode value {mode}","setoption name C3X_Telemetry value true","setoption name Threads value 1","setoption name Hash value 64","setoption name SyzygyProbeLimit value 0","setoption name UCI_ShowWDL value true","setoption name Clear Hash","isready",f"position fen {fen}",f"go nodes {nodes}"]
 for c in cmds:p.stdin.write(c+"\n")
 p.stdin.flush();lines=[]
 for line in p.stdout:
  line=line.rstrip("\n");lines.append(line)
  if line.startswith("bestmove "):break
 p.terminate()
 try:rest,_=p.communicate(timeout=5)
 except subprocess.TimeoutExpired:p.kill();rest,_=p.communicate(timeout=5)
 if rest:lines.extend(rest.splitlines())
 best=next((x for x in reversed(lines) if x.startswith("bestmove ")),None)
 infos=[x for x in lines if x.startswith("info depth ") and " score " in x and " pv " in x]
 tel=next((x for x in lines if x.startswith("info string c3x_ttread_v1 ")),None)
 if not best or not infos or not tel:raise RuntimeError("incomplete receipt\n"+"\n".join(lines[-80:]))
 final=infos[-1];bt=best.split()
 def grab(pat):
  m=re.search(pat,final);return m.group(1) if m else None
 t={}
 for tok in tel.split()[3:]:
  if "=" in tok:
   k,v=tok.split("=",1)
   try:t[k]=int(v)
   except ValueError:t[k]=v
 return {"semantic":{"bestmove":bt[1],"ponder":bt[3] if len(bt)>=4 and bt[2]=="ponder" else None,"depth":int(grab(r"\bdepth (\d+)") or 0),"seldepth":int(grab(r"\bseldepth (\d+)") or 0),"score":grab(r"\bscore ((?:cp|mate) -?\d+)"),"wdl":grab(r"\bwdl (\d+ \d+ \d+)"),"nodes":int(grab(r"\bnodes (\d+)") or 0),"pv":grab(r"\bpv (.+)$")},"telemetry":t,"telemetry_line":tel}

def site_uses(t):
 return {
  "MAIN":int(t.get("use_main_eval",0))+int(t.get("use_main_value",0))+int(t.get("use_main_cutoff_gate",0)),
  "SUCCESSOR":int(t.get("use_successor_value",0)),
  "QSEARCH":int(t.get("use_qsearch_eval",0))+int(t.get("use_qsearch_value",0))+int(t.get("use_qsearch_cutoff",0))
 }
def engagement(r):
 t=r["telemetry"];hits={"MAIN":int(t.get("raw_hits_main",0)),"SUCCESSOR":int(t.get("raw_hits_successor",0)),"QSEARCH":int(t.get("raw_hits_qsearch",0))}
 uses=site_uses(t);H=sum(hits.values());U=sum(uses.values());B=sum(uses[s]>0 for s in SITES)
 passed=H>=64 and U>=16 and B==3 and all(hits[s]>0 for s in SITES) and all(uses[s]>0 for s in SITES)
 return {"H":H,"U":U,"B":B,"raw_hits_by_site":hits,"semantic_uses_by_site":uses,"site_use_floor":min(uses.values()),"passed":passed}

def world_value(c,move):
 m=next((x for x in c["world"]["moves"] if x["uci"]==move),None)
 if m is None:return None
 return {"wdl":int(m["mover_wdl"]),"precise_dtz":int(m["mover_precise_dtz"])}

def select_tranche(rows,target=24):
 strata=defaultdict(list)
 for r in rows:
  floors=[r["engagement"][t]["site_use_floor"] for t in TARGETS]
  r["selection_floor"]=min(floors)
  strata[(r["candidate"]["material_signature"],r["candidate"]["side_to_move"])].append(r)
 for k in strata:
  strata[k].sort(key=lambda r:(-r["selection_floor"],-int(r["candidate"]["tau4"]["tau4"]),r["candidate"]["candidate_sha256"]))
 keys=sorted(strata);chosen=[];i=0
 while len(chosen)<target and keys:
  progressed=False
  for k in keys:
   if i<len(strata[k]) and len(chosen)<target:
    chosen.append(strata[k][i]);progressed=True
  if not progressed:break
  i+=1
 return chosen

def arm_subset(bits):
 return tuple(SITES[i] for i,b in enumerate(bits) if b=="1")

def subsets_of(bits):
 idx=[i for i,b in enumerate(bits) if b=="1"]
 for r in range(len(idx)+1):
  for comb in itertools.combinations(idx,r):
   s=["0","0","0"]
   for i in comb:s[i]="1"
   yield "".join(s)

def mobius(rates,bits):
 k=bits.count("1");v=0.0
 for sub in subsets_of(bits):
  sign=(-1)**(k-sub.count("1"))
  v+=sign*rates[sub]
 return v

def overlap_fraction(single,full):
 if not full:return 0.0
 return len(single & full)/len(full)

def preflight(args):
 bins=parse_binaries(args.binary)
 fen="8/8/3k4/8/3K4/8/4R3/8 w - - 0 1"
 out={}
 for t,b in bins.items():
  a=run_search(b,fen,"MASK_ALL",args.nodes);z=run_search(b,fen,"MASKED",args.nodes)
  fields=("bestmove","score","wdl","pv")
  same=all(a["semantic"][f]==z["semantic"][f] for f in fields)
  out[t]={"same":same,"mask_all":a["semantic"],"legacy_masked":z["semantic"]}
  if not same:raise SystemExit(f"FULL-MASK-EQUIVALENCE-FAIL {t}")
 print(json.dumps({"P15_FULL_MASK_EQUIVALENCE":"PASS","targets":out},sort_keys=True))

def sham_commit(args):
 stage=json.loads(Path(args.stage_a).read_text());bins=parse_binaries(args.binary);rows=[]
 for i,c in enumerate(stage["candidates"],1):
  sham={};eg={}
  for t,b in bins.items():
   sham[t]=run_search(b,c["fen"],"SHAM",args.nodes);eg[t]=engagement(sham[t])
  both=all(eg[t]["passed"] for t in TARGETS)
  rows.append({"candidate":c,"sham":sham,"engagement":eg,"both_targets_engaged":both})
  print(f"SHAM {i:02d}/{len(stage['candidates'])} id={c['candidate_sha256'][:12]} both={both} floors={[eg[t]['site_use_floor'] for t in TARGETS]}",flush=True)
 eligible=[r for r in rows if r["both_targets_engaged"]];chosen=select_tranche(eligible,24)
 mats=sorted({r["candidate"]["material_signature"] for r in chosen});turns=sorted({r["candidate"]["side_to_move"] for r in chosen})
 ready=len(chosen)>=20 and len(mats)>=6 and set(turns)=={"BLACK","WHITE"}
 payload={"schema":"c3x-p15-sham-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P15","stage_a_pool_sha256":stage["pool_sha256"],"selective_mask_outcomes_consulted":False,"binaries":{t:{"sha256":sha256_file(p),"path_basename":os.path.basename(p)} for t,p in bins.items()},"runtime":{"threads":1,"hash_mib":64,"nodes":args.nodes,"clear_hash_each_arm":True,"syzygy_probe_limit":0},"arms":ARMS,"counts":{"stage_a":len(rows),"dual_engaged":len(eligible),"committed":len(chosen),"material_signatures":len(mats),"sides_to_move":turns},"authorization":"P15-FACTORIAL-READY" if ready else "P15-ENGAGEMENT-HOLD","committed_cells":chosen}
 payload["precommit_sha256"]=sha256_obj(payload)
 Path(args.out).parent.mkdir(parents=True,exist_ok=True);Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
 print("P15_PRECOMMIT",payload["authorization"],payload["precommit_sha256"],payload["counts"])
 if not ready:raise SystemExit(2)

def factorial_run(args):
 pre=json.loads(Path(args.precommit).read_text());bins=parse_binaries(args.binary)
 if pre.get("authorization")!="P15-FACTORIAL-READY":raise SystemExit("P15-HOLD")
 for t,p in bins.items():
  if sha256_file(p)!=pre["binaries"][t]["sha256"]:raise SystemExit(f"BINARY-IDENTITY-FAIL {t}")
 rows=[]
 for i,row in enumerate(pre["committed_cells"],1):
  c=row["candidate"];record={"candidate_sha256":c["candidate_sha256"],"material_signature":c["material_signature"],"side_to_move":c["side_to_move"],"fen":c["fen"],"tau4":c["tau4"]["tau4"],"targets":{}}
  for t,b in bins.items():
   arms={}
   sham=run_search(b,c["fen"],"SHAM",args.nodes);sv=world_value(c,sham["semantic"]["bestmove"])
   if sv is None:raise SystemExit(f"WORLD-MOVE-JOIN-FAIL {t} SHAM")
   arms["000"]={"mode":"SHAM","receipt":sham,"world":sv,"action_changed":False,"coarse_changed":False,"fine_changed":False}
   for bits,mode in ARMS.items():
    if bits=="000":continue
    rr=run_search(b,c["fen"],mode,args.nodes);wv=world_value(c,rr["semantic"]["bestmove"])
    if wv is None:raise SystemExit(f"WORLD-MOVE-JOIN-FAIL {t} {bits}")
    arms[bits]={"mode":mode,"receipt":rr,"world":wv,"action_changed":rr["semantic"]["bestmove"]!=sham["semantic"]["bestmove"],"coarse_changed":wv["wdl"]!=sv["wdl"],"fine_changed":(wv["wdl"],wv["precise_dtz"])!=(sv["wdl"],sv["precise_dtz"]),"precise_dtz_delta":wv["precise_dtz"]-sv["precise_dtz"]}
   record["targets"][t]={"arms":arms}
  rows.append(record)
  print(f"FACTORIAL {i:02d}/{len(pre['committed_cells'])} id={c['candidate_sha256'][:12]}",flush=True)

 rates={};contrasts={};changed_sets={}
 for t in TARGETS:
  rates[t]={};changed_sets[t]={}
  for outcome in ("action_changed","fine_changed","coarse_changed"):
   rates[t][outcome]={}
   changed_sets[t][outcome]={}
   for bits in ARMS:
    vals=[bool(r["targets"][t]["arms"][bits][outcome]) for r in rows]
    rates[t][outcome][bits]=sum(vals)/len(vals)
    changed_sets[t][outcome][bits]={r["candidate_sha256"] for r,v in zip(rows,vals) if v}
  contrasts[t]={o:{bits:mobius(rates[t][o],bits) for bits in ARMS if bits!="000"} for o in ("action_changed","fine_changed")}

 singleton=None
 for bits,name in (("100","MAIN"),("010","SUCCESSOR"),("001","QSEARCH")):
  ok=True
  detail={}
  for t in TARGETS:
   s=changed_sets[t]["fine_changed"][bits];full=changed_sets[t]["fine_changed"]["111"];ov=overlap_fraction(s,full)
   detail[t]={"count":len(s),"full_overlap_fraction":ov}
   ok=ok and len(s)>=2 and ov>=0.5
  if ok:
   singleton={"site":name,"bits":bits,"detail":detail};break

 interaction=None
 if singleton is None:
  for bits,name in (("110","MAINxSUCCESSOR"),("101","MAINxQSEARCH"),("011","SUCCESSORxQSEARCH"),("111","MAINxSUCCESSORxQSEARCH")):
   ok=all(rates[t]["fine_changed"][bits]>=0.10 and contrasts[t]["fine_changed"][bits]>=0.08 for t in TARGETS)
   if ok:
    cand={"interaction":name,"bits":bits,"min_contrast":min(contrasts[t]["fine_changed"][bits] for t in TARGETS),"detail":{t:{"rate":rates[t]["fine_changed"][bits],"mobius":contrasts[t]["fine_changed"][bits]} for t in TARGETS}}
    if interaction is None or cand["min_contrast"]>interaction["min_contrast"]:interaction=cand

 any_coarse=any(rates[t]["coarse_changed"][bits]>0 for t in TARGETS for bits in ARMS if bits!="000")
 any_effect=any(rates[t]["action_changed"][bits]>0 or rates[t]["fine_changed"][bits]>0 for t in TARGETS for bits in ARMS if bits!="000")
 if singleton:loc="SINGLE-SUBPATH-LOCALIZATION"
 elif interaction:loc="INTERACTION-SPECIFIC-LOCALIZATION"
 elif any_effect:loc="DISTRIBUTED-NONLOCAL-TT-MEDIATION"
 else:loc="NO-SELECTIVE-EFFECT"
 if any_coarse:primary="TT-READ-SUBPATH-DEPENDENT-ROBUST-WDL-QUOTIENT"
 elif any(rates[t]["fine_changed"][bits]>0 for t in TARGETS for bits in ARMS if bits!="000"):primary="TT-READ-SUBPATH-DEPENDENT-FINE-EXACT-VALUE"
 elif any_effect:primary="TT-READ-SUBPATH-DEPENDENT-ACTION"
 else:primary="NO-DETECTED-SELECTIVE-TT-EFFECT"
 payload={"schema":"c3x-p15-factorial-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P15","precommit_sha256":pre["precommit_sha256"],"selective_masks_opened_only_after_precommit":True,"binary_sha256":{t:sha256_file(p) for t,p in bins.items()},"runtime":pre["runtime"],"arms":ARMS,"rates":rates,"mobius_contrasts":contrasts,"localization":{"verdict":loc,"singleton":singleton,"interaction":interaction},"primary_verdict":primary,"authority_ceiling":"fresh P15-only exact micro-worlds under dual-target fixed-node selective TT-read interventions; no representation/cognition/general-chess inference","rows":rows}
 payload["result_sha256"]=sha256_obj(payload)
 Path(args.out).parent.mkdir(parents=True,exist_ok=True);Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
 print("P15_RESULT",primary,loc,payload["result_sha256"])

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="cmd",required=True)
 x=sub.add_parser("preflight");x.add_argument("--binary",action="append",required=True);x.add_argument("--nodes",type=int,default=30000)
 s=sub.add_parser("sham-commit");s.add_argument("--stage-a",required=True);s.add_argument("--binary",action="append",required=True);s.add_argument("--nodes",type=int,default=300000);s.add_argument("--out",required=True)
 f=sub.add_parser("factorial-run");f.add_argument("--precommit",required=True);f.add_argument("--binary",action="append",required=True);f.add_argument("--nodes",type=int,default=300000);f.add_argument("--out",required=True)
 a=ap.parse_args()
 if a.cmd=="preflight":preflight(a)
 elif a.cmd=="sham-commit":sham_commit(a)
 else:factorial_run(a)
if __name__=="__main__":main()
