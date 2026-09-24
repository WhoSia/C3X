#!/usr/bin/env python3
import argparse,json,os,re,subprocess
from pathlib import Path
FENS=[
"r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PPQN1PPP/R1B2RK1 w - - 4 9",
"2r2rk1/pp1b1ppp/2n1pn2/q2p4/3P4/2P1PN2/PPQN1PPP/2R2RK1 w - - 2 12",
"4rrk1/1pp2ppp/p1np1n2/4p3/2P1P3/1PN2P2/PB1N2PP/2RR2K1 w - - 1 18"]
CMP=("bestmove","score","pv","nodes")
def until(p,pred):
 out=[]
 for _ in range(30000):
  x=p.stdout.readline()
  if x=="":break
  x=x.rstrip("\n");out.append(x)
  if pred(x):break
 return out
def run(bin,fen,nodes,mode=None):
 env=os.environ.copy()
 if mode is None:env.pop("C3X_PSM_MODE",None)
 else:env["C3X_PSM_MODE"]=mode
 p=subprocess.Popen([bin],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush();pre=until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("uciok missing")
 opts="\n".join(pre)
 if re.search(r"^option name Threads\b",opts,re.M):p.stdin.write("setoption name Threads value 1\n")
 if re.search(r"^option name Hash\b",opts,re.M):p.stdin.write("setoption name Hash value 64\n")
 p.stdin.write("isready\n");p.stdin.flush();ready=until(p,lambda x:x.strip()=="readyok")
 if not any(x.strip()=="readyok" for x in ready):raise RuntimeError("readyok missing")
 p.stdin.write(f"position fen {fen}\ngo nodes {nodes}\n");p.stdin.flush();lines=pre+ready+until(p,lambda x:x.startswith("bestmove "))
 p.terminate()
 try:rest,_=p.communicate(timeout=3)
 except subprocess.TimeoutExpired:p.kill();rest,_=p.communicate(timeout=3)
 if rest:lines+=rest.splitlines()
 best=next((x for x in reversed(lines) if x.startswith("bestmove ")),None)
 infos=[x for x in lines if x.startswith("info ") and " score " in x and " pv " in x]
 if not best or not infos:raise RuntimeError("search receipt missing\n"+"\n".join(lines[-80:]))
 final=infos[-1]
 def g(pat):
  m=re.search(pat,final);return m.group(1) if m else None
 tel=next((x for x in reversed(lines) if x.startswith("info string c3x_psm_v1 ")),None);t={}
 if tel:
  for z in tel.split()[3:]:
   if "=" in z:
    k,v=z.split("=",1)
    try:t[k]=int(v)
    except:t[k]=v
 return {"semantic":{"bestmove":best.split()[1],"score":g(r"\bscore ((?:cp|mate) -?\d+)"),"wdl":g(r"\bwdl (\d+ \d+ \d+)"),"nodes":int(g(r"\bnodes (\d+)") or 0),"depth":int(g(r"\bdepth (\d+)") or 0),"pv":g(r"\bpv (.+)$")},"telemetry":t,"telemetry_line":tel}
def same(a,b):return all(a["semantic"].get(k)==b["semantic"].get(k) for k in CMP)
def main():
 ap=argparse.ArgumentParser()
 for x in ("engine","baseline","instrument","removal","instrument_manifest","removal_manifest","out"):ap.add_argument("--"+x.replace("_","-"),dest=x,required=True)
 ap.add_argument("--nodes",type=int,default=80000);a=ap.parse_args()
 im=json.loads(Path(a.instrument_manifest).read_text());rm=json.loads(Path(a.removal_manifest).read_text())
 if not im["complete_scoped_mediation"] or not rm["complete_scoped_mediation"]:raise SystemExit("STATIC_MEDIATION_FAIL")
 rows=[];agg={k:0 for k in ("probes_main","hits_main","probes_qsearch","hits_qsearch")}
 for i,fen in enumerate(FENS):
  b=run(a.baseline,fen,a.nodes);n=run(a.instrument,fen,a.nodes,"NATIVE");s=run(a.instrument,fen,a.nodes,"SHAM");m=run(a.instrument,fen,a.nodes,"MASK_ALL");r=run(a.removal,fen,a.nodes)
  ip=same(b,n) and same(n,s);rp=same(m,r)
  if not s["telemetry_line"]:raise SystemExit("TELEMETRY_MISSING")
  for k in agg:agg[k]+=int(s["telemetry"].get(k,0))
  rows.append({"fen_index":i,"fen":fen,"identity_pass":ip,"semantic_removal_equivalence_pass":rp,"baseline":b["semantic"],"native":n,"sham":s,"mask_all":m,"semantic_removal":r})
  print("P20_ADMISSION",a.engine,i,ip,rp,flush=True)
 engagement=all(v>0 for v in agg.values());verdict=all(x["identity_pass"] and x["semantic_removal_equivalence_pass"] for x in rows) and engagement
 out={"schema":"c3x-p20-engine-admission-v1","scientific_stage":"C3X 0.7.0-G9.4-P20","engine":a.engine,"nodes_per_fen":a.nodes,"static_complete_mediation":True,"native_sham_noninterference":all(x["identity_pass"] for x in rows),"semantic_removal_equivalence":all(x["semantic_removal_equivalence_pass"] for x in rows),"dynamic_engagement":agg,"dynamic_engagement_pass":engagement,"wdl_field_observed_any":any(x["sham"]["semantic"]["wdl"] is not None for x in rows),"rows":rows,"instrument_manifest":im,"removal_manifest":rm,"verdict":"PASS" if verdict else "HOLD"}
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"engine":a.engine,"verdict":out["verdict"],"engagement":agg},sort_keys=True))
 if not verdict:raise SystemExit("P20-HETEROGENEOUS-ADMISSION-HOLD "+a.engine)
if __name__=="__main__":main()
