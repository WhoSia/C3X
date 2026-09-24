#!/usr/bin/env python3
import argparse,hashlib,json,os,re,subprocess
from collections import defaultdict,Counter
from pathlib import Path

TARGETS=("stockfish_18","frozen_20260810","stockfish_19")
CHRONOLOGY=TARGETS
NODES=300000
ARMS={"00":"SHAM","10":"MASK_MAIN","01":"MASK_QSEARCH","11":"MASK_MAIN_QSEARCH","ALL":"MASK_ALL"}
SEM_FIELDS=("bestmove","score","wdl","pv")
SITES=("MAIN","SUCCESSOR","QSEARCH")
SQUARES={
 "HEAVY_HEAVY":{"00":"KQQvKQ","10":"KQRvKQ","01":"KQQvKR","11":"KQRvKR"},
 "MINOR_MINOR":{"00":"KRBvKB","10":"KRNvKB","01":"KRBvKN","11":"KRNvKN"}
}
FAMILIES=tuple(f for sq in SQUARES.values() for f in sq.values())

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha_obj(o):return hashlib.sha256(canon(o)).hexdigest()
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def bins(items):
 out={}
 for x in items:
  k,p=x.split("=",1);out[k]=p
 if set(out)!=set(TARGETS):raise SystemExit("P19 requires stockfish_18,frozen_20260810,stockfish_19 binaries")
 return out

def run_search(binary,fen,mode,nodes=NODES):
 p=subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
 cmds=["uci",f"setoption name C3X_TTReadMode value {mode}","setoption name C3X_Telemetry value true",
       "setoption name Threads value 1","setoption name Hash value 64","setoption name SyzygyProbeLimit value 0",
       "setoption name UCI_ShowWDL value true","setoption name Clear Hash","isready",
       f"position fen {fen}",f"go nodes {nodes}"]
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
   except:t[k]=v
 return {"semantic":{"bestmove":bt[1],"depth":int(grab(r"\bdepth (\d+)") or 0),
                     "seldepth":int(grab(r"\bseldepth (\d+)") or 0),
                     "score":grab(r"\bscore ((?:cp|mate) -?\d+)"),
                     "wdl":grab(r"\bwdl (\d+ \d+ \d+)"),
                     "nodes":int(grab(r"\bnodes (\d+)") or 0),
                     "pv":grab(r"\bpv (.+)$")},
         "telemetry":t,"telemetry_line":tel}

def site_uses(t):
 return {"MAIN":int(t.get("use_main_eval",0))+int(t.get("use_main_value",0))+int(t.get("use_main_cutoff_gate",0)),
         "SUCCESSOR":int(t.get("use_successor_value",0)),
         "QSEARCH":int(t.get("use_qsearch_eval",0))+int(t.get("use_qsearch_value",0))+int(t.get("use_qsearch_cutoff",0))}
def engagement(r):
 t=r["telemetry"];hits={"MAIN":int(t.get("raw_hits_main",0)),"SUCCESSOR":int(t.get("raw_hits_successor",0)),"QSEARCH":int(t.get("raw_hits_qsearch",0))}
 uses=site_uses(t);H=sum(hits.values());U=sum(uses.values());B=sum(uses[s]>0 for s in SITES)
 passed=H>=64 and U>=16 and B==3 and all(hits[s]>0 for s in SITES) and all(uses[s]>0 for s in SITES)
 return {"H":H,"U":U,"B":B,"raw_hits_by_site":hits,"semantic_uses_by_site":uses,
         "site_use_floor":min(uses.values()),"passed":passed}

def world_value(c,move):
 m=next((x for x in c["world"]["moves"] if x["uci"]==move),None)
 return None if m is None else {"wdl":int(m["mover_wdl"]),"precise_dtz":int(m["mover_precise_dtz"])}

def select_vertex(rows):
 byside=defaultdict(list)
 for r in rows:byside[r["candidate"]["side_to_move"]].append(r)
 for s in byside:
  byside[s].sort(key=lambda r:(-r["selection_floor"],-int(r["candidate"]["tau4"]["tau4"]),r["candidate"]["candidate_sha256"]))
 if len(byside["WHITE"])<6 or len(byside["BLACK"])<6:return []
 return sorted(byside["WHITE"][:6]+byside["BLACK"][:6],key=lambda r:r["candidate"]["candidate_sha256"])

def sham_commit(a):
 stage=json.loads(Path(a.stage_a).read_text());b=bins(a.binary);rows=[]
 for i,c in enumerate(stage["candidates"],1):
  sham={};eg={};allpass=True
  for t,p in b.items():
   r=run_search(p,c["fen"],"SHAM");sham[t]=r;eg[t]=engagement(r);allpass=allpass and eg[t]["passed"]
  floor=min(eg[t]["site_use_floor"] for t in TARGETS)
  rows.append({"candidate":c,"sham":sham,"engagement":eg,"all_targets_engaged":allpass,"selection_floor":floor})
  print(f"P19_SHAM {i:03d}/{len(stage['candidates'])} {c['material_seed_name']} pass={allpass} floor={floor}",flush=True)
 selected=[];counts={}
 for fam in FAMILIES:
  elig=[r for r in rows if r["candidate"]["material_seed_name"]==fam and r["all_targets_engaged"]]
  chosen=select_vertex(elig);counts[fam]={"eligible":len(elig),"committed":len(chosen)}
  if len(chosen)!=12:raise SystemExit(f"P19-ENGAGEMENT-HOLD {fam} eligible={len(elig)} committed={len(chosen)}")
  selected.extend(chosen)
 payload={"schema":"c3x-p19-sham-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P19",
          "stage_a_pool_sha256":stage["pool_sha256"],"intervention_outcomes_consulted":False,
          "engine_targets":list(TARGETS),"chronology":list(CHRONOLOGY),
          "binaries":{t:{"sha256":sha_file(p),"path_basename":os.path.basename(p)} for t,p in b.items()},
          "runtime":{"threads":1,"hash_mib":64,"nodes":NODES,"clear_hash_each_arm":True,"syzygy_probe_limit":0},
          "counts":{"stage_a":len(rows),"committed":len(selected),"by_vertex":counts},
          "authorization":"P19-MORPHISM-READY","committed_cells":selected}
 payload["precommit_sha256"]=sha_obj(payload)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
 print("P19_PRECOMMIT",payload["precommit_sha256"],payload["counts"])

def vertex_rows(pre,fam):
 return [r for r in pre["committed_cells"] if r["candidate"]["material_seed_name"]==fam]

def vertex_run(a):
 pre=json.loads(Path(a.precommit).read_text());b=bins(a.binary);fam=a.family
 if pre.get("authorization")!="P19-MORPHISM-READY":raise SystemExit("P19-HOLD")
 for t,p in b.items():
  if sha_file(p)!=pre["binaries"][t]["sha256"]:raise SystemExit("BINARY-IDENTITY-FAIL "+t)
 src=vertex_rows(pre,fam)
 if len(src)!=12:raise SystemExit(f"VERTEX-COMMIT-COUNT {fam} {len(src)}")
 out=[]
 for i,row in enumerate(src,1):
  c=row["candidate"];rec={"candidate_sha256":c["candidate_sha256"],"square":c["square"],"vertex":c["vertex"],
                          "material_family":fam,"side_to_move":c["side_to_move"],"fen":c["fen"],"targets":{}}
  for t,p in b.items():
   baseline=run_search(p,c["fen"],"SHAM");sealed=row["sham"][t]
   if any(baseline["semantic"][f]!=sealed["semantic"][f] for f in SEM_FIELDS):
    raise SystemExit(f"SEALED-SHAM-REPLAY-FAIL {fam} {t} {c['candidate_sha256']}")
   sv=world_value(c,baseline["semantic"]["bestmove"])
   if sv is None:raise SystemExit("WORLD-JOIN-FAIL SHAM")
   arms={"00":{"mode":"SHAM","receipt":baseline,"world":sv,"action_changed":False,"fine_changed":False,"coarse_changed":False}}
   for bits in ("10","01","11","ALL"):
    rr=run_search(p,c["fen"],ARMS[bits]);wv=world_value(c,rr["semantic"]["bestmove"])
    if wv is None:raise SystemExit("WORLD-JOIN-FAIL "+bits)
    arms[bits]={"mode":ARMS[bits],"receipt":rr,"world":wv,
                "action_changed":rr["semantic"]["bestmove"]!=baseline["semantic"]["bestmove"],
                "fine_changed":(wv["wdl"],wv["precise_dtz"])!=(sv["wdl"],sv["precise_dtz"]),
                "coarse_changed":wv["wdl"]!=sv["wdl"]}
   rec["targets"][t]={"arms":arms}
  out.append(rec);print(f"P19_VERTEX {fam} {i}/12",flush=True)
 payload={"schema":"c3x-p19-vertex-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P19","family":fam,
          "precommit_sha256":pre["precommit_sha256"],"binary_sha256":{t:sha_file(p) for t,p in b.items()},
          "sealed_sham_replay":"PASS","rows":out}
 payload["result_sha256"]=sha_obj(payload)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
 print("P19_VERTEX_PASS",fam,payload["result_sha256"])

def parse(items):
 out={}
 for x in items:
  fam,p=x.split("=",1);out[fam]=json.loads(Path(p).read_text())
 return out

def sign(x,eps=1e-12):return -1 if x < -eps else 1 if x > eps else 0

def phase(v,n):
 vals={"MAIN":abs(v[0]),"QSEARCH":abs(v[1]),"INTERACTION":abs(v[2])};o=sorted(vals.items(),key=lambda x:(-x[1],x[0]))
 floor=2/n;margin=1/n
 if o[0][1]<floor:return "NULL"
 if o[0][1]-o[1][1]<margin:return "MIXED"
 return o[0][0]+"-DOMINANT"

def summary(rows,t):
 n=len(rows)
 m=sum(r["targets"][t]["arms"]["10"]["fine_changed"] for r in rows)
 q=sum(r["targets"][t]["arms"]["01"]["fine_changed"] for r in rows)
 mq=sum(r["targets"][t]["arms"]["11"]["fine_changed"] for r in rows)
 coarse=sum(r["targets"][t]["arms"][b]["coarse_changed"] for r in rows for b in ("10","01","11","ALL"))
 action={b:sum(r["targets"][t]["arms"][b]["action_changed"] for r in rows) for b in ("10","01","11","ALL")}
 v=[m/n,q/n,mq/n-m/n-q/n]
 return {"n":n,"vector":{"MAIN":v[0],"QSEARCH":v[1],"INTERACTION":v[2]},
         "counts":{"MAIN":m,"QSEARCH":q,"MAIN_QSEARCH":mq,"coarse_total":coarse,"action":action},
         "phase":phase(v,n),"interaction_sign":sign(v[2])}

def vec(s):return [s["vector"][k] for k in ("MAIN","QSEARCH","INTERACTION")]
def vsub(a,b):return [a[i]-b[i] for i in range(3)]
def vadd(a,b):return [a[i]+b[i] for i in range(3)]

def square_analysis(vertex,t):
 s={bits:summary(vertex[bits]["rows"],t) for bits in ("00","10","01","11")}
 v={bits:vec(s[bits]) for bits in s}
 h=[v["11"][i]-v["10"][i]-v["01"][i]+v["00"][i] for i in range(3)]
 n=s["00"]["n"];res=1/n;mx=max(abs(x) for x in h)
 if mx<=res+1e-12:cls="FLAT"
 elif mx>=2*res-1e-12:cls="CURVED"
 else:cls="BORDERLINE"
 names=("MAIN","QSEARCH","INTERACTION");dom=max(range(3),key=lambda i:(abs(h[i]),-i))
 alpha_phase=[s["00"]["phase"],s["10"]["phase"]]==[s["01"]["phase"],s["11"]["phase"]]
 beta_phase=[s["00"]["phase"],s["01"]["phase"]]==[s["10"]["phase"],s["11"]["phase"]]
 alpha_sign=[s["00"]["interaction_sign"],s["10"]["interaction_sign"]]==[s["01"]["interaction_sign"],s["11"]["interaction_sign"]]
 beta_sign=[s["00"]["interaction_sign"],s["01"]["interaction_sign"]]==[s["10"]["interaction_sign"],s["11"]["interaction_sign"]]
 return {"vertices":s,"curvature":{"vector":{"MAIN":h[0],"QSEARCH":h[1],"INTERACTION":h[2]},
          "linf":mx,"one_cell_resolution":res,"class":cls,"dominant_coordinate":names[dom],"dominant_sign":sign(h[dom])},
          "parallel_edge_equivariance":{"alpha_phase":alpha_phase,"beta_phase":beta_phase,
          "alpha_interaction_sign":alpha_sign,"beta_interaction_sign":beta_sign,
          "pass":alpha_phase and beta_phase and alpha_sign and beta_sign}}

def adjudicate(a):
 res=parse(a.result)
 if set(res)!=set(FAMILIES):raise SystemExit("need all P19 vertices")
 vertex={sq:{bits:res[fam] for bits,fam in mapping.items()} for sq,mapping in SQUARES.items()}
 targets={};any_coarse=False
 for t in TARGETS:
  targets[t]={}
  for sq in SQUARES:
   targets[t][sq]=square_analysis(vertex[sq],t)
   any_coarse=any_coarse or any(targets[t][sq]["vertices"][b]["counts"]["coarse_total"] for b in ("00","10","01","11"))
 replicated={}
 engine_conditioned=False
 for sq in SQUARES:
  cur=[(t,targets[t][sq]["curvature"]) for t in TARGETS if targets[t][sq]["curvature"]["class"]=="CURVED"]
  groups=Counter((x["dominant_coordinate"],x["dominant_sign"]) for _,x in cur)
  best=max(groups.values()) if groups else 0
  replicated[sq]={"replicated":best>=2,"curved_targets":[t for t,_ in cur],
                  "fingerprints":{t:[targets[t][sq]["curvature"]["class"],
                                     targets[t][sq]["curvature"]["dominant_coordinate"],
                                     targets[t][sq]["curvature"]["dominant_sign"]] for t in TARGETS}}
  fps=list(replicated[sq]["fingerprints"].values())
  if len({tuple(x) for x in fps})>1:engine_conditioned=True
 any_rep=any(x["replicated"] for x in replicated.values())
 all_flat=all(targets[t][sq]["curvature"]["class"]=="FLAT" for t in TARGETS for sq in SQUARES)
 all_eq=all(targets[t][sq]["parallel_edge_equivariance"]["pass"] for t in TARGETS for sq in SQUARES)
 if any_rep:verdict="REPLICATED-MATERIAL-RELATION-CURVATURE"
 elif engine_conditioned:verdict="ENGINE-CONDITIONED-RELATION-GEOMETRY"
 elif all_flat and all_eq:verdict="CAUSAL-FUNCTORIALITY-SUPPORTED"
 else:verdict="RELATION-LAW-INDETERMINATE"
 engine_transport={}
 for a0,b0 in zip(CHRONOLOGY,CHRONOLOGY[1:]):
  engine_transport[a0+"_TO_"+b0]={}
  for sq in SQUARES:
   ha=targets[a0][sq]["curvature"]["vector"];hb=targets[b0][sq]["curvature"]["vector"]
   engine_transport[a0+"_TO_"+b0][sq]={"curvature_delta":{k:hb[k]-ha[k] for k in ha},
      "class_change":[targets[a0][sq]["curvature"]["class"],targets[b0][sq]["curvature"]["class"]]}
 payload={"schema":"c3x-p19-morphism-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P19",
          "engine_chronology":list(CHRONOLOGY),"targets":targets,"replicated_curvature":replicated,
          "engine_material_naturality":engine_transport,"engine_conditioned_relation_geometry":engine_conditioned,
          "robust_wdl_changed_any_arm":any_coarse,"literal_sequential_noncommutativity":"NOT_IDENTIFIED_BY_ENDPOINT_SQUARES",
          "primary_verdict":verdict,
          "authority_ceiling":"fresh matched exact-world squares; admitted Stockfish lineage targets; fixed 300k selective TT-read causal vectors; endpoint curvature identifies functoriality failure, not literal sequential order noncommutativity"}
 payload["result_sha256"]=sha_obj(payload)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
 print("P19_RESULT",verdict,payload["result_sha256"])

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 s=sp.add_parser("sham-commit");s.add_argument("--stage-a",required=True);s.add_argument("--binary",action="append",required=True);s.add_argument("--out",required=True)
 v=sp.add_parser("vertex-run");v.add_argument("--precommit",required=True);v.add_argument("--binary",action="append",required=True);v.add_argument("--family",choices=FAMILIES,required=True);v.add_argument("--out",required=True)
 d=sp.add_parser("adjudicate");d.add_argument("--result",action="append",required=True);d.add_argument("--out",required=True)
 a=ap.parse_args();{"sham-commit":sham_commit,"vertex-run":vertex_run,"adjudicate":adjudicate}[a.cmd](a)
if __name__=="__main__":main()
