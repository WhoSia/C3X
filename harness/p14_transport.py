#!/usr/bin/env python3
import argparse, hashlib, json, math, os, random, re, subprocess
from collections import defaultdict
from pathlib import Path

C2_KEYS=["use_main_eval","use_main_value","use_main_cutoff_gate","use_successor_value","use_qsearch_eval","use_qsearch_value","use_qsearch_cutoff"]

def sha256_file(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def canon(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha256_obj(obj):return hashlib.sha256(canon(obj)).hexdigest()

def parse_binaries(items):
 out={}
 for x in items:
  k,p=x.split("=",1);out[k]=p
 if set(out)!={"frozen_20260810","stockfish_19"}:raise SystemExit("need exactly frozen_20260810 and stockfish_19 binaries")
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
 final=infos[-1]; bt=best.split()
 def grab(pat):
  m=re.search(pat,final);return m.group(1) if m else None
 t={}
 for tok in tel.split()[3:]:
  if "=" in tok:
   k,v=tok.split("=",1)
   try:t[k]=int(v)
   except ValueError:t[k]=v
 return {"semantic":{"bestmove":bt[1],"ponder":bt[3] if len(bt)>=4 and bt[2]=="ponder" else None,"depth":int(grab(r"\bdepth (\d+)") or 0),"seldepth":int(grab(r"\bseldepth (\d+)") or 0),"score":grab(r"\bscore ((?:cp|mate) -?\d+)"),"wdl":grab(r"\bwdl (\d+ \d+ \d+)"),"nodes":int(grab(r"\bnodes (\d+)") or 0),"pv":grab(r"\bpv (.+)$")},"telemetry":t,"telemetry_line":tel}

def engagement(r):
 t=r["telemetry"];H=sum(int(t.get(k,0)) for k in ("raw_hits_main","raw_hits_successor","raw_hits_qsearch"));U=int(t.get("semantic_uses",0));B=int(t.get("breadth",0))
 c2={k:int(t.get(k,0)) for k in C2_KEYS}; non=any(v>0 for v in c2.values())
 return {"H":H,"U":U,"B":B,"semantic_use_density":U/max(H,1),"qsearch_raw_hit_share":int(t.get("raw_hits_qsearch",0))/max(H,1),"c2":c2,"non_move_order":non,"passed":H>=64 and U>=16 and B>=2 and non}

def pct_ranks(vals):
 order=sorted(range(len(vals)),key=lambda i:(vals[i],i));out=[0.0]*len(vals);n=len(vals)
 i=0
 while i<n:
  j=i
  while j+1<n and vals[order[j+1]]==vals[order[i]]:j+=1
  rank=((i+j)/2)/(n-1) if n>1 else .5
  for k in range(i,j+1):out[order[k]]=rank
  i=j+1
 return out

def add_predictor(rows):
 tau=[math.log1p(r["candidate"]["tau4"]["tau4"]) for r in rows]
 dens=[sum(r["engagement"][t]["semantic_use_density"] for t in ("frozen_20260810","stockfish_19"))/2 for r in rows]
 qsh=[sum(r["engagement"][t]["qsearch_raw_hit_share"] for t in ("frozen_20260810","stockfish_19"))/2 for r in rows]
 a,b,c=pct_ranks(tau),pct_ranks(dens),pct_ranks(qsh)
 for i,r in enumerate(rows):
  r["predictor"]={"tau_rank":a[i],"semantic_density_rank":b[i],"qsearch_share_rank":c[i],"score":a[i]+b[i]+c[i]}

def assign_quintiles(rows):
 s=sorted(rows,key=lambda r:(r["predictor"]["score"],r["candidate"]["candidate_sha256"]))
 n=len(s)
 for i,r in enumerate(s):r["predictor"]["quintile"]=min(4,(5*i)//max(n,1))
 return s

def select_tranche(rows,target=30):
 s=assign_quintiles(rows);byq=defaultdict(list)
 for r in s:byq[r["predictor"]["quintile"]].append(r)
 chosen=[]
 for q in range(5):
  group=byq[q];strata=defaultdict(list)
  for r in group:strata[(r["candidate"]["material_signature"],r["candidate"]["side_to_move"])].append(r)
  for k in strata:strata[k].sort(key=lambda x:x["candidate"]["candidate_sha256"])
  keys=sorted(strata);i=0;qchosen=[]
  while len(qchosen)<6 and keys:
   progressed=False
   for k in keys:
    if i<len(strata[k]) and len(qchosen)<6:qchosen.append(strata[k][i]);progressed=True
   if not progressed:break
   i+=1
  chosen.extend(qchosen)
 if len(chosen)>target:chosen=chosen[:target]
 return chosen

def world_value(candidate,move):
 m=next((x for x in candidate["world"]["moves"] if x["uci"]==move),None)
 if m is None:return None
 return {"wdl":int(m["mover_wdl"]),"precise_dtz":int(m["mover_precise_dtz"]),"dtm":m.get("mover_dtm"),"zeroing":bool(m.get("zeroing",False))}

def auc(scores,labels):
 pos=[s for s,y in zip(scores,labels) if y];neg=[s for s,y in zip(scores,labels) if not y]
 if not pos or not neg:return None
 wins=0.0
 for p in pos:
  for n in neg:wins+=1 if p>n else .5 if p==n else 0
 return wins/(len(pos)*len(neg))

def permutation_p(scores,labels,seed,nperm=10000):
 obs=auc(scores,labels)
 if obs is None:return 1.0
 rng=random.Random(seed);base=list(labels);ge=0
 for _ in range(nperm):
  y=base[:];rng.shuffle(y);a=auc(scores,y)
  if a is not None and a>=obs-1e-15:ge+=1
 return (ge+1)/(nperm+1)

def predict_stats(rows,target,seed):
 scores=[r["predictor"]["score"] for r in rows];labels=[r["targets"][target]["action_changed"] for r in rows]
 A=auc(scores,labels);p=permutation_p(scores,labels,seed)
 top=[y for r,y in zip(rows,labels) if r["predictor"]["quintile"]==4];bottom=[y for r,y in zip(rows,labels) if r["predictor"]["quintile"]==0]
 rt=sum(top)/len(top) if top else 0;rb=sum(bottom)/len(bottom) if bottom else 0
 gate=A is not None and A>=.70 and p<=.05 and rt-rb>=.20
 return {"auc":A,"permutation_p_one_sided":p,"top_quintile_rate":rt,"bottom_quintile_rate":rb,"top_minus_bottom":rt-rb,"gate_pass":gate,"action_changes":sum(labels),"cells":len(labels)}

def sham_commit(args):
 stage=json.loads(Path(args.stage_a).read_text());bins=parse_binaries(args.binary);rows=[]
 for i,c in enumerate(stage["candidates"],1):
  sr={};eg={}
  for t,b in bins.items():
   sr[t]=run_search(b,c["fen"],"SHAM",args.nodes);eg[t]=engagement(sr[t])
  both=all(eg[t]["passed"] for t in bins)
  rows.append({"candidate":c,"sham":sr,"engagement":eg,"both_targets_engaged":both})
  print(f"SHAM {i:02d}/{len(stage['candidates'])} id={c['candidate_sha256'][:12]} both={both} frozen_U={eg['frozen_20260810']['U']} sf19_U={eg['stockfish_19']['U']}",flush=True)
 eligible=[r for r in rows if r["both_targets_engaged"]];add_predictor(eligible);chosen=select_tranche(eligible,30)
 mats=sorted({r["candidate"]["material_signature"] for r in chosen});turns=sorted({r["candidate"]["side_to_move"] for r in chosen})
 ready=len(chosen)>=25 and len(mats)>=5 and set(turns)=={"BLACK","WHITE"} and len({r["predictor"]["quintile"] for r in chosen})==5
 payload={"schema":"c3x-p14-sham-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P14","stage_a_pool_sha256":stage["pool_sha256"],"masked_outcomes_consulted":False,
 "binaries":{t:{"sha256":sha256_file(p),"path_basename":os.path.basename(p)} for t,p in bins.items()},
 "runtime":{"threads":1,"hash_mib":64,"nodes":args.nodes,"clear_hash_each_arm":True,"syzygy_probe_limit":0},
 "predictor":{"name":"P13-DERIVED-STRUCTURED-MEDIATION-SCORE-v1","formula":"pct_rank(log1p(tau4))+pct_rank(mean(U/H))+pct_rank(mean(qsearch_raw_hits/H))","fit_to_p14_masked":False},
 "counts":{"stage_a":len(rows),"dual_engaged":len(eligible),"committed":len(chosen),"material_signatures":len(mats),"sides_to_move":turns,"quintiles":{str(q):sum(r["predictor"]["quintile"]==q for r in chosen) for q in range(5)}},
 "authorization":"TARGET-INTERVENTION-READY" if ready else "P14-PRECOMMIT-HOLD","committed_cells":chosen}
 payload["precommit_sha256"]=sha256_obj(payload)
 Path(args.out).parent.mkdir(parents=True,exist_ok=True);Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
 print("P14_PRECOMMIT",payload["authorization"],payload["precommit_sha256"],payload["counts"])
 if not ready:raise SystemExit(2)

def masked_run(args):
 pre=json.loads(Path(args.precommit).read_text());bins=parse_binaries(args.binary)
 if pre.get("authorization")!="TARGET-INTERVENTION-READY":raise SystemExit("MASKED-HOLD")
 for t,p in bins.items():
  a=sha256_file(p);e=pre["binaries"][t]["sha256"]
  if a!=e:raise SystemExit(f"BINARY-IDENTITY-FAIL {t} {a} != {e}")
 rows=[]
 for i,row in enumerate(pre["committed_cells"],1):
  c=row["candidate"];out={"candidate_sha256":c["candidate_sha256"],"material_signature":c["material_signature"],"side_to_move":c["side_to_move"],"fen":c["fen"],"tau4":c["tau4"]["tau4"],"predictor":row["predictor"],"targets":{}}
  for t,b in bins.items():
   sham=run_search(b,c["fen"],"SHAM",args.nodes);masked=run_search(b,c["fen"],"MASKED",args.nodes)
   sv=world_value(c,sham["semantic"]["bestmove"]);mv=world_value(c,masked["semantic"]["bestmove"])
   if sv is None or mv is None:raise SystemExit(f"WORLD-MOVE-JOIN-FAIL {t} {c['candidate_sha256']}")
   out["targets"][t]={"sham":sham,"masked":masked,"sham_world":sv,"masked_world":mv,
    "action_changed":sham["semantic"]["bestmove"]!=masked["semantic"]["bestmove"],
    "coarse_quotient_changed":sv["wdl"]!=mv["wdl"],
    "fine_quotient_changed":(sv["wdl"],sv["precise_dtz"])!=(mv["wdl"],mv["precise_dtz"]),
    "fine_delta_precise_dtz":mv["precise_dtz"]-sv["precise_dtz"],
    "score_changed":sham["semantic"]["score"]!=masked["semantic"]["score"]}
  rows.append(out)
  print(f"PAIR {i:02d}/{len(pre['committed_cells'])} id={c['candidate_sha256'][:12]} score={row['predictor']['score']:.4f} frozen_change={out['targets']['frozen_20260810']['action_changed']} sf19_change={out['targets']['stockfish_19']['action_changed']}",flush=True)
 seed=int(pre["precommit_sha256"][:16],16)
 stats={t:predict_stats(rows,t,seed^(0 if t=="frozen_20260810" else 0x5F19)) for t in bins}
 counts={}
 for t in bins:
  counts[t]={"action_changed":sum(r["targets"][t]["action_changed"] for r in rows),"score_changed":sum(r["targets"][t]["score_changed"] for r in rows),"coarse_quotient_changed":sum(r["targets"][t]["coarse_quotient_changed"] for r in rows),"fine_quotient_changed":sum(r["targets"][t]["fine_quotient_changed"] for r in rows)}
 any_coarse=any(counts[t]["coarse_quotient_changed"] for t in bins);any_fine=any(counts[t]["fine_quotient_changed"] for t in bins)
 primary=stats["frozen_20260810"]["gate_pass"];cross=stats["stockfish_19"]["gate_pass"]
 if any_coarse:verdict="TT-READ-PATH-DEPENDENT-ROBUST-WDL-QUOTIENT"
 elif any_fine:verdict="TT-READ-PATH-DEPENDENT-FINE-EXACT-VALUE"
 elif primary and cross:verdict="PREDICTIVE-TT-MEDIATION-TRANSPORT / CROSS-VERSION"
 elif primary:verdict="PREDICTIVE-TT-MEDIATION-TRANSPORT / FROZEN-TARGET-ONLY"
 elif counts["frozen_20260810"]["action_changed"]>0:verdict="FRESH-CAUSAL-EFFECT / PREDICTIVE-LAW-NOT-ESTABLISHED / PATH-MULTIPLICITY-RIVAL-SURVIVES"
 else:verdict="NO-DETECTED-FRESH-MASKED-EFFECT"
 payload={"schema":"c3x-p14-masked-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P14","precommit_sha256":pre["precommit_sha256"],"masked_opened_only_after_precommit":True,
 "binary_sha256":{t:sha256_file(p) for t,p in bins.items()},"runtime":pre["runtime"],"counts":counts,"predictive_adjudication":stats,
 "cross_version":{"same_committed_cells":True,"same_predictor_without_refit":True,"action_change_concordance":sum(r["targets"]["frozen_20260810"]["action_changed"]==r["targets"]["stockfish_19"]["action_changed"] for r in rows)/len(rows)},
 "verdict":verdict,"authority_ceiling":"fresh P14-only exact micro-world families under frozen fixed-node dual-engine regime; no representation, cognition, or general-chess prevalence inference","pairs":rows}
 payload["result_sha256"]=sha256_obj(payload)
 Path(args.out).parent.mkdir(parents=True,exist_ok=True);Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
 print("P14_RESULT",verdict,counts,stats,payload["result_sha256"])

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="cmd",required=True)
 s=sub.add_parser("sham-commit");s.add_argument("--stage-a",required=True);s.add_argument("--binary",action="append",required=True);s.add_argument("--nodes",type=int,default=300000);s.add_argument("--out",required=True)
 m=sub.add_parser("masked-run");m.add_argument("--precommit",required=True);m.add_argument("--binary",action="append",required=True);m.add_argument("--nodes",type=int,default=300000);m.add_argument("--out",required=True)
 a=ap.parse_args()
 if a.cmd=="sham-commit":sham_commit(a)
 else:masked_run(a)
if __name__=="__main__":main()
