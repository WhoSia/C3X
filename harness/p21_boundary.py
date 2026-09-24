#!/usr/bin/env python3
import argparse,hashlib,json,math,os,re,statistics,subprocess
from collections import defaultdict
from pathlib import Path
import p20_transport as p20

P20_TARGETS=("stockfish_19","berserk","ethereal")
CORE_FAMILIES=("KQQvKQ","KQRvKQ","KQQvKR","KQRvKR","KRBvKB","KRNvKB","KRBvKN","KRNvKN")
CARRIER_FAMILIES=("KQQPvKQP","KQRPvKQP","KQQPvKRP","KQRPvKRP","KRBPvKBP","KRNPvKBP","KRBPvKNP","KRNPvKNP")
CORE_SQUARES={
 "HEAVY_HEAVY":{"00":"KQQvKQ","10":"KQRvKQ","01":"KQQvKR","11":"KQRvKR"},
 "MINOR_MINOR":{"00":"KRBvKB","10":"KRNvKB","01":"KRBvKN","11":"KRNvKN"}
}
CARRIER_SQUARES={
 "HEAVY_HEAVY":{"00":"KQQPvKQP","10":"KQRPvKQP","01":"KQQPvKRP","11":"KQRPvKRP"},
 "MINOR_MINOR":{"00":"KRBPvKBP","10":"KRNPvKBP","01":"KRBPvKNP","11":"KRNPvKNP"}
}
CENSUS_NODES=80000
INTERVENTION_NODES=300000
CORE_INANIS={"SHAM":"SHAM","TT_MAIN":"MASK_TT_MAIN","PAWN_Q":"MASK_PAWN_Q"}
CARRIER_INANIS={
 "SHAM":"SHAM","TT_MAIN":"MASK_TT_MAIN","PAWN_MAIN":"MASK_PAWN_MAIN",
 "PAWN_Q":"MASK_PAWN_Q","PAWN_ALL":"MASK_PAWN_ALL",
 "TT_MAIN_PAWN_Q":"MASK_TT_AND_PAWN_Q","ALL":"MASK_ALL"
}
FEATURES=tuple(
 f"{t}:{kind}" for t in P20_TARGETS for kind in ("LOG_MAIN","LOG_Q","Q_SHARE")
)

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha_obj(o):return hashlib.sha256(canon(o)).hexdigest()
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def read_until(p,pred,limit=100000):
 out=[]
 while len(out)<limit:
  x=p.stdout.readline()
  if x=="":break
  x=x.rstrip("\n");out.append(x)
  if pred(x):break
 return out

def has_option(text,name):return re.search(r"^option name "+re.escape(name)+r"(?: |$)",text,re.M) is not None

def run_inanis(path,fen,mode,nodes):
 env=os.environ.copy();env["C3X_P21_MODE"]=mode
 p=subprocess.Popen([path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush();pre=read_until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):p.kill();raise RuntimeError("INANIS_UCIOK_MISSING")
 opts="\n".join(pre);cmd=[]
 if has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
 if has_option(opts,"Hash"):cmd.append("setoption name Hash value 64")
 if has_option(opts,"Search Noise"):cmd.append("setoption name Search Noise value false")
 if has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
 cmd+=["isready",f"position fen {fen}",f"go nodes {nodes}"]
 for c in cmd:p.stdin.write(c+"\n")
 p.stdin.flush();lines=pre+read_until(p,lambda x:x.startswith("bestmove "))
 p.terminate()
 try:rest,_=p.communicate(timeout=4)
 except subprocess.TimeoutExpired:p.kill();rest,_=p.communicate(timeout=4)
 if rest:lines+=rest.splitlines()
 if not any(x.strip()=="readyok" for x in lines):raise RuntimeError("INANIS_READYOK_MISSING")
 best=next((x for x in reversed(lines) if x.startswith("bestmove ")),None)
 infos=[x for x in lines if x.startswith("info ") and " score " in x and " pv " in x]
 tel=next((x for x in reversed(lines) if x.startswith("info string c3x_p21_inanis_v1 ")),None)
 if not best or not infos or not tel:raise RuntimeError("INANIS_RECEIPT_MISSING\n"+"\n".join(lines[-100:]))
 final=infos[-1]
 def grab(pat):
  m=re.search(pat,final);return m.group(1) if m else None
 t={}
 for z in tel.split()[3:]:
  if "=" in z:
   k,v=z.split("=",1)
   try:t[k]=int(v)
   except:t[k]=v
 return {
  "semantic":{"bestmove":best.split()[1],"score":grab(r"\bscore ((?:cp|mate) -?\d+)"),"nodes":int(grab(r"\bnodes (\d+)") or 0),"depth":int(grab(r"\bdepth (\d+)") or 0),"pv":grab(r"\bpv (.+)$")},
  "telemetry":t,
  "engagement":{
   "TT_MAIN":int(t.get("tt_main_hits",0)),
   "PAWN_MAIN":int(t.get("pawn_main_hits",0)),
   "PAWN_Q":int(t.get("pawn_q_hits",0))
  }
 }

def feature_map(sham):
 out={}
 for t in P20_TARGETS:
  m=int(sham[t]["engagement"]["MAIN"]);q=int(sham[t]["engagement"]["QSEARCH"])
  out[f"{t}:LOG_MAIN"]=math.log1p(m);out[f"{t}:LOG_Q"]=math.log1p(q);out[f"{t}:Q_SHARE"]=q/max(1,m+q)
 return out

def arm(c,base,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("WORLD_JOIN_FAIL "+str(c["candidate_sha256"]))
 return {
  "receipt":run,"world":w,
  "action_changed":run["semantic"]["bestmove"]!=base["semantic"]["bestmove"],
  "fine_changed":(w["wdl"],w["precise_dtz"])!=(base["world"]["wdl"],base["world"]["precise_dtz"]),
  "coarse_changed":w["wdl"]!=base["world"]["wdl"]
 }

def baseline_arm(c,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("WORLD_JOIN_FAIL_SHAM "+str(c["candidate_sha256"]))
 return {"receipt":run,"world":w,"action_changed":False,"fine_changed":False,"coarse_changed":False}

def core_census(a):
 stage=json.loads(Path(a.stage_a).read_text());eng=p20.parse_engines(a.engine)
 src=[c for c in stage["candidates"] if c["material_seed_name"]==a.family]
 if len(src)!=48:raise SystemExit(f"P21_CORE_CENSUS_COUNT {a.family} {len(src)}/48")
 rows=[]
 for i,c in enumerate(src,1):
  sham={};ok=True
  for t in P20_TARGETS:
   r=p20.run_search(eng[t],c["fen"],"SHAM",CENSUS_NODES);sham[t]=r;ok=ok and r["engagement"]["passed"]
  ir=run_inanis(a.inanis,c["fen"],"SHAM",CENSUS_NODES)
  rows.append({"candidate":c,"sham":sham,"inanis_sham":ir,"all_p20_targets_engaged":ok,"features":feature_map(sham)})
  print("P21_CORE_CENSUS",a.family,i,ok,flush=True)
 out={
  "schema":"c3x-p21-core-census-v1","scientific_stage":"C3X 0.7.0-G9.4-P21","family":a.family,
  "pool_sha256":stage["pool_sha256"],"selective_outcomes_consulted":False,"census_nodes":CENSUS_NODES,
  "p20_binaries":{t:{"protocol":eng[t]["protocol"],"sha256":sha_file(eng[t]["path"])} for t in P20_TARGETS},
  "inanis_binary_sha256":sha_file(a.inanis),"rows":rows
 }
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def carrier_census(a):
 stage=json.loads(Path(a.stage_a).read_text());eng=p20.parse_engines(a.engine)
 src=[c for c in stage["candidates"] if c["material_seed_name"]==a.family]
 if len(src)!=48:raise SystemExit(f"P21_CARRIER_CENSUS_COUNT {a.family} {len(src)}/48")
 rows=[]
 for i,c in enumerate(src,1):
  sham={};ok=True
  for t in P20_TARGETS:
   r=p20.run_search(eng[t],c["fen"],"SHAM",CENSUS_NODES);sham[t]=r;ok=ok and int(r["engagement"]["QSEARCH"])>0
  ir=run_inanis(a.inanis,c["fen"],"SHAM",CENSUS_NODES)
  ok=ok and int(ir["engagement"]["PAWN_Q"])>0
  rows.append({"candidate":c,"sham":sham,"inanis_sham":ir,"qmemory_engaged_all_targets":ok})
  print("P21_CARRIER_CENSUS",a.family,i,ok,flush=True)
 out={
  "schema":"c3x-p21-carrier-census-v1","scientific_stage":"C3X 0.7.0-G9.4-P21","family":a.family,
  "pool_sha256":stage["pool_sha256"],"selective_outcomes_consulted":False,"census_nodes":CENSUS_NODES,
  "p20_binaries":{t:{"protocol":eng[t]["protocol"],"sha256":sha_file(eng[t]["path"])} for t in P20_TARGETS},
  "inanis_binary_sha256":sha_file(a.inanis),"rows":rows
 }
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect_census(root,pattern,expected,schema,pool_sha):
 files=sorted(Path(root).rglob(pattern))
 if len(files)!=8:raise SystemExit(f"P21_CENSUS_FILE_COUNT {len(files)}/8")
 by={};pb=None;ib=None
 for p in files:
  x=json.loads(p.read_text())
  if x.get("schema")!=schema or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P21_CENSUS_SCHEMA_LEAK")
  if x["pool_sha256"]!=pool_sha:raise SystemExit("P21_CENSUS_POOL_MISMATCH")
  fam=x["family"]
  if fam in by:raise SystemExit("P21_CENSUS_DUP "+fam)
  if pb is None:pb=x["p20_binaries"];ib=x["inanis_binary_sha256"]
  elif pb!=x["p20_binaries"] or ib!=x["inanis_binary_sha256"]:raise SystemExit("P21_CENSUS_BINARY_MISMATCH")
  by[fam]=x
 if set(by)!=set(expected):raise SystemExit("P21_CENSUS_FAMILY_SET")
 return by,pb,ib

def smd(a,b):
 if not a or not b:return float("inf")
 ma=statistics.fmean(a);mb=statistics.fmean(b)
 va=statistics.variance(a) if len(a)>1 else 0.0;vb=statistics.variance(b) if len(b)>1 else 0.0
 den=math.sqrt((va+vb)/2)
 if den==0:return 0.0 if abs(ma-mb)<1e-12 else float("inf")
 return abs(ma-mb)/den

def core_seal(a):
 stage=json.loads(Path(a.stage_a).read_text())
 by,pb,ib=collect_census(a.census_dir,"p21-core-census-*.json",CORE_FAMILIES,"c3x-p21-core-census-v1",stage["pool_sha256"])
 eligible=[r for x in by.values() for r in x["rows"] if r["all_p20_targets_engaged"]]
 if len(eligible)<96:raise SystemExit("P21_CORE_ELIGIBLE_SHORTFALL")
 mu={k:statistics.fmean(r["features"][k] for r in eligible) for k in FEATURES}
 sd={}
 for k in FEATURES:
  vals=[r["features"][k] for r in eligible]
  z=statistics.pstdev(vals);sd[k]=z if z>1e-12 else 1.0
 selected=[]
 counts={}
 for fam in CORE_FAMILIES:
  rows=[r for r in by[fam]["rows"] if r["all_p20_targets_engaged"]]
  for r in rows:r["_distance"]=sum(((r["features"][k]-mu[k])/sd[k])**2 for k in FEATURES)
  chosen=[]
  sidecounts={}
  for side in ("WHITE","BLACK"):
   q=sorted([r for r in rows if r["candidate"]["side_to_move"]==side],key=lambda r:(r["_distance"],r["candidate"]["candidate_sha256"]))
   if len(q)<6:raise SystemExit(f"P21_CORE_SIDE_SHORTFALL {fam} {side} {len(q)}")
   chosen+=q[:6];sidecounts[side]=len(q)
  for r in chosen:r.pop("_distance",None)
  selected+=chosen
  counts[fam]={"eligible":len(rows),"eligible_by_side":sidecounts,"committed":12}
 heavy=[r for r in selected if r["candidate"]["square"]=="HEAVY_HEAVY"];minor=[r for r in selected if r["candidate"]["square"]=="MINOR_MINOR"]
 balance={k:smd([r["features"][k] for r in heavy],[r["features"][k] for r in minor]) for k in FEATURES}
 balance_pass=all(v<=0.50+1e-12 for v in balance.values())
 inanis_gate=all(int(r["inanis_sham"]["engagement"]["TT_MAIN"])>0 and int(r["inanis_sham"]["engagement"]["PAWN_Q"])>0 for r in selected)
 auth="P21-CORE-INTERVENTION-AUTHORIZED" if balance_pass and inanis_gate else "P21-CORE-HOLD"
 out={
  "schema":"c3x-p21-core-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P21","pool_sha256":stage["pool_sha256"],
  "selective_outcomes_consulted":False,"selection":"global exposure-center matching; 6 per side per vertex; tie candidate_sha256",
  "feature_mean":mu,"feature_sd":sd,"heavy_vs_minor_smd":balance,"balance_threshold":0.50,"exposure_balance_pass":balance_pass,
  "inanis_postselection_engagement_gate":inanis_gate,"p20_binaries":pb,"inanis_binary_sha256":ib,
  "counts":{"pool":len(stage["candidates"]),"committed":len(selected),"by_vertex":counts},
  "authorization":auth,"squares":CORE_SQUARES,"committed_cells":selected
 }
 out["precommit_sha256"]=sha_obj(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P21_CORE_PRECOMMIT",auth,out["precommit_sha256"],balance,flush=True)
 if auth!="P21-CORE-INTERVENTION-AUTHORIZED":raise SystemExit(auth)

def carrier_seal(a):
 stage=json.loads(Path(a.stage_a).read_text())
 by,pb,ib=collect_census(a.census_dir,"p21-carrier-census-*.json",CARRIER_FAMILIES,"c3x-p21-carrier-census-v1",stage["pool_sha256"])
 selected=[];counts={}
 for fam in CARRIER_FAMILIES:
  rows=[r for r in by[fam]["rows"] if r["qmemory_engaged_all_targets"]]
  chosen=[];sidecounts={}
  for side in ("WHITE","BLACK"):
   q=sorted([r for r in rows if r["candidate"]["side_to_move"]==side],key=lambda r:r["candidate"]["candidate_sha256"])
   if len(q)<6:raise SystemExit(f"P21_CARRIER_SIDE_SHORTFALL {fam} {side} {len(q)}")
   chosen+=q[:6];sidecounts[side]=len(q)
  selected+=chosen;counts[fam]={"eligible":len(rows),"eligible_by_side":sidecounts,"committed":12}
 out={
  "schema":"c3x-p21-carrier-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P21","pool_sha256":stage["pool_sha256"],
  "selective_outcomes_consulted":False,"selection":"positive q-memory engagement on all four targets; candidate_sha256 only; 6 per side per vertex",
  "p20_binaries":pb,"inanis_binary_sha256":ib,"counts":{"pool":len(stage["candidates"]),"committed":len(selected),"by_vertex":counts},
  "authorization":"P21-CARRIER-INTERVENTION-AUTHORIZED","squares":CARRIER_SQUARES,"committed_cells":selected
 }
 out["precommit_sha256"]=sha_obj(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P21_CARRIER_PRECOMMIT",out["precommit_sha256"],flush=True)

def selected_for(pre,fam):return [r for r in pre["committed_cells"] if r["candidate"]["material_seed_name"]==fam]

def do_vertex(a,lane):
 pre=json.loads(Path(a.precommit).read_text());eng=p20.parse_engines(a.engine)
 auth="P21-CORE-INTERVENTION-AUTHORIZED" if lane=="core" else "P21-CARRIER-INTERVENTION-AUTHORIZED"
 if pre.get("authorization")!=auth:raise SystemExit("P21_AUTH_HOLD")
 for t in P20_TARGETS:
  if sha_file(eng[t]["path"])!=pre["p20_binaries"][t]["sha256"]:raise SystemExit("P21_BINARY_IDENTITY "+t)
 if sha_file(a.inanis)!=pre["inanis_binary_sha256"]:raise SystemExit("P21_INANIS_BINARY_IDENTITY")
 src=selected_for(pre,a.family)
 if len(src)!=12:raise SystemExit("P21_COMMIT_COUNT")
 rows=[]
 for i,row in enumerate(src,1):
  c=row["candidate"];rec={"candidate_sha256":c["candidate_sha256"],"family":a.family,"square":c["square"],"vertex":c["vertex"],"side_to_move":c["side_to_move"],"fen":c["fen"],"targets":{}}
  for t in P20_TARGETS:
   base_run=p20.run_search(eng[t],c["fen"],"SHAM",INTERVENTION_NODES);base=baseline_arm(c,base_run)
   arms={"00":base}
   for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
    arms[bits]=arm(c,base,p20.run_search(eng[t],c["fen"],mode,INTERVENTION_NODES))
   rec["targets"][t]={"arms":arms}
  modes=CORE_INANIS if lane=="core" else CARRIER_INANIS
  ibase_run=run_inanis(a.inanis,c["fen"],"SHAM",INTERVENTION_NODES);ibase=baseline_arm(c,ibase_run)
  ia={"SHAM":ibase}
  for name,mode in modes.items():
   if name=="SHAM":continue
   ia[name]=arm(c,ibase,run_inanis(a.inanis,c["fen"],mode,INTERVENTION_NODES))
  rec["inanis"]={"arms":ia}
  rows.append(rec);print("P21_VERTEX",lane,a.family,i,flush=True)
 out={"schema":f"c3x-p21-{lane}-vertex-v1","scientific_stage":"C3X 0.7.0-G9.4-P21","lane":lane,"family":a.family,"precommit_sha256":pre["precommit_sha256"],"rows":rows}
 out["result_sha256"]=sha_obj(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P21_VERTEX_PASS",lane,a.family,out["result_sha256"])

def scalar_class(h,n):
 r=1/n
 if h<=-2*r+1e-12:return "NEGATIVE"
 if h>=2*r-1e-12:return "POSITIVE"
 if abs(h)<=r+1e-12:return "FLAT"
 return "BORDERLINE"

def scalar_square(by,mp,extract):
 vals={}
 for bit,fam in mp.items():
  rows=by[fam]["rows"];vals[bit]=sum(1 for r in rows if extract(r))/len(rows)
 h=vals["11"]-vals["10"]-vals["01"]+vals["00"];n=len(by[mp["00"]]["rows"])
 return {"vertices":vals,"H":h,"class":scalar_class(h,n),"one_cell_resolution":1/n}

def load_vertices(root,pattern,expected,schema):
 fs=sorted(Path(root).rglob(pattern))
 if len(fs)!=8:raise SystemExit(f"P21_VERTEX_FILE_COUNT {len(fs)}/8")
 by={};pre=None
 for p in fs:
  x=json.loads(p.read_text())
  if x.get("schema")!=schema:raise SystemExit("P21_VERTEX_SCHEMA")
  fam=x["family"]
  if fam in by:raise SystemExit("P21_VERTEX_DUP")
  if pre is None:pre=x["precommit_sha256"]
  elif pre!=x["precommit_sha256"]:raise SystemExit("P21_PRECOMMIT_MISMATCH")
  by[fam]=x
 if set(by)!=set(expected):raise SystemExit("P21_VERTEX_SET")
 return by,pre

def core_adjudicate(a):
 pre=json.loads(Path(a.precommit).read_text())
 by,ph=load_vertices(a.result_dir,"p21-core-vertex-*.json",CORE_FAMILIES,"c3x-p21-core-vertex-v1")
 if ph!=pre["precommit_sha256"]:raise SystemExit("P21_CORE_PREHASH")
 targets={}
 for t in P20_TARGETS:
  targets[t]={sq:p20.square_analysis({bit:by[fam] for bit,fam in mp.items()},t) for sq,mp in CORE_SQUARES.items()}
 def fp(t,sq):
  c=targets[t][sq]["curvature"];return (c["class"],c["dominant_coordinate"],c["dominant_sign"])
 heavy={t:fp(t,"HEAVY_HEAVY") for t in P20_TARGETS};minor={t:fp(t,"MINOR_MINOR") for t in P20_TARGETS}
 heavy_rep=all(z==("CURVED","QSEARCH",-1) for z in heavy.values())
 minor_common=len(set(minor.values()))==1 and next(iter(minor.values()))[0]=="CURVED"
 boundary=pre["exposure_balance_pass"] and heavy_rep and not minor_common
 pawn_q_changes=sum(r["inanis"]["arms"]["PAWN_Q"]["fine_changed"] for x in by.values() for r in x["rows"])
 pawn_negative_control=(pawn_q_changes==0)
 inanis_tt={sq:scalar_square(by,mp,lambda r:r["inanis"]["arms"]["TT_MAIN"]["fine_changed"]) for sq,mp in CORE_SQUARES.items()}
 coarse=any(r["targets"][t]["arms"][b]["coarse_changed"] for x in by.values() for r in x["rows"] for t in P20_TARGETS for b in ("10","01","11","ALL"))
 out={
  "schema":"c3x-p21-core-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P21","precommit_sha256":ph,
  "exposure_balance_pass":pre["exposure_balance_pass"],"heavy_vs_minor_smd":pre["heavy_vs_minor_smd"],
  "p20_targets":targets,"heavy_fingerprints":heavy,"minor_fingerprints":minor,
  "core_relation_boundary_replicated":boundary,
  "exposure_only_rival":"DEFEATED_WITHIN_BALANCED_SCOPE" if boundary else "NOT_DEFEATED",
  "inanis_pawn_q_negative_control":{"fine_changes":pawn_q_changes,"pass":pawn_negative_control},
  "inanis_search_tt_projection":inanis_tt,
  "robust_wdl_changed_any_arm":coarse,
  "authority":"fresh exposure-balanced relation-boundary confirmation" if boundary else "no fresh relation-boundary promotion"
 }
 out["result_sha256"]=sha_obj(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P21_CORE_RESULT",boundary,out["result_sha256"],flush=True)

def carrier_adjudicate(a):
 pre=json.loads(Path(a.precommit).read_text())
 by,ph=load_vertices(a.result_dir,"p21-carrier-vertex-*.json",CARRIER_FAMILIES,"c3x-p21-carrier-vertex-v1")
 if ph!=pre["precommit_sha256"]:raise SystemExit("P21_CARRIER_PREHASH")
 full={}
 for t in P20_TARGETS:
  full[t]={sq:p20.square_analysis({bit:by[fam] for bit,fam in mp.items()},t) for sq,mp in CARRIER_SQUARES.items()}
 qscalar={t:{sq:scalar_square(by,mp,lambda r,t=t:r["targets"][t]["arms"]["01"]["fine_changed"]) for sq,mp in CARRIER_SQUARES.items()} for t in P20_TARGETS}
 ich={}
 for ch in ("TT_MAIN","PAWN_MAIN","PAWN_Q","PAWN_ALL","TT_MAIN_PAWN_Q","ALL"):
  ich[ch]={sq:scalar_square(by,mp,lambda r,ch=ch:r["inanis"]["arms"][ch]["fine_changed"]) for sq,mp in CARRIER_SQUARES.items()}
 tt_neg=sum(qscalar[t]["HEAVY_HEAVY"]["class"]=="NEGATIVE" for t in P20_TARGETS)
 broader=ich["PAWN_Q"]["HEAVY_HEAVY"]["class"]=="NEGATIVE" and tt_neg>=2
 coarse=any(
  r["targets"][t]["arms"][b]["coarse_changed"]
  for x in by.values() for r in x["rows"] for t in P20_TARGETS for b in ("10","01","11","ALL")
 ) or any(
  r["inanis"]["arms"][ch]["coarse_changed"]
  for x in by.values() for r in x["rows"] for ch in ("TT_MAIN","PAWN_MAIN","PAWN_Q","PAWN_ALL","TT_MAIN_PAWN_Q","ALL")
 )
 out={
  "schema":"c3x-p21-carrier-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P21","precommit_sha256":ph,
  "p20_full_geometry":full,"qsearch_tt_scalar_curvature":qscalar,"inanis_channel_scalar_curvature":ich,
  "tt_qsearch_negative_targets_on_heavy":tt_neg,
  "broader_qsearch_memory_carrier_support":broader,
  "robust_wdl_changed_any_arm":coarse,
  "channel_homology_claim":"NOT_GRANTED_BY_SIGN_AGREEMENT"
 }
 out["result_sha256"]=sha_obj(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P21_CARRIER_RESULT",broader,out["result_sha256"],flush=True)

def synthesize(a):
 c=json.loads(Path(a.core).read_text());p=json.loads(Path(a.carrier).read_text())
 if not c["exposure_balance_pass"]:v="EXPOSURE_BALANCE_HOLD_NO_P21_CAUSAL_VERDICT"
 elif not c["core_relation_boundary_replicated"]:v="P20_RELATION_BOUNDARY_NOT_FRESHLY_REPLICATED"
 elif c["inanis_pawn_q_negative_control"]["pass"] and p["broader_qsearch_memory_carrier_support"]:
  v="RELATION_BOUNDARY_REPLICATED_AND_BROADER_QSEARCH_MEMORY_TRANSPORT_SUPPORTED"
 elif p["tt_qsearch_negative_targets_on_heavy"]>=2 and p["inanis_channel_scalar_curvature"]["PAWN_Q"]["HEAVY_HEAVY"]["class"]!="NEGATIVE":
  v="RELATION_BOUNDARY_REPLICATED_TT_QSEARCH_SPECIFIC_WITHIN_TESTED_SCOPE"
 else:v="RELATION_BOUNDARY_REPLICATED_CROSS_ARCHITECTURE_CARRIER_CONTEXT_HOLD"
 out={
  "schema":"c3x-p21-final-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P21",
  "core_result_sha256":c["result_sha256"],"carrier_result_sha256":p["result_sha256"],
  "primary_verdict":v,
  "exposure_only_rival":c["exposure_only_rival"],
  "pawnless_inanis_pawn_q_negative_control":c["inanis_pawn_q_negative_control"],
  "broader_qsearch_memory_carrier_support":p["broader_qsearch_memory_carrier_support"],
  "tt_qsearch_negative_targets_on_carrier_heavy":p["tt_qsearch_negative_targets_on_heavy"],
  "inanis_carrier_heavy_pawn_q":p["inanis_channel_scalar_curvature"]["PAWN_Q"]["HEAVY_HEAVY"],
  "robust_wdl_changed_any_arm":bool(c["robust_wdl_changed_any_arm"] or p["robust_wdl_changed_any_arm"]),
  "language_policy":"IMPLEMENTATION_LANGUAGE_NONAUTHORITATIVE_NATIVE_FIRST",
  "literal_sequential_noncommutativity":"NOT_IDENTIFIED"
 }
 out["result_sha256"]=sha_obj(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P21_FINAL_RESULT",v,out["result_sha256"]);print(json.dumps(out,sort_keys=True))

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 for name,fn,fams in (("core-census",core_census,CORE_FAMILIES),("carrier-census",carrier_census,CARRIER_FAMILIES)):
  q=sp.add_parser(name);q.add_argument("--stage-a",required=True);q.add_argument("--engine",action="append",required=True);q.add_argument("--inanis",required=True);q.add_argument("--family",choices=fams,required=True);q.add_argument("--out",required=True)
 for name in ("core-seal","carrier-seal"):
  q=sp.add_parser(name);q.add_argument("--stage-a",required=True);q.add_argument("--census-dir",required=True);q.add_argument("--out",required=True)
 for name,fams in (("core-vertex",CORE_FAMILIES),("carrier-vertex",CARRIER_FAMILIES)):
  q=sp.add_parser(name);q.add_argument("--precommit",required=True);q.add_argument("--engine",action="append",required=True);q.add_argument("--inanis",required=True);q.add_argument("--family",choices=fams,required=True);q.add_argument("--out",required=True)
 for name in ("core-adjudicate","carrier-adjudicate"):
  q=sp.add_parser(name);q.add_argument("--precommit",required=True);q.add_argument("--result-dir",required=True);q.add_argument("--out",required=True)
 q=sp.add_parser("synthesize");q.add_argument("--core",required=True);q.add_argument("--carrier",required=True);q.add_argument("--out",required=True)
 a=ap.parse_args();{
  "core-census":core_census,"carrier-census":carrier_census,"core-seal":core_seal,"carrier-seal":carrier_seal,
  "core-vertex":lambda x:do_vertex(x,"core"),"carrier-vertex":lambda x:do_vertex(x,"carrier"),
  "core-adjudicate":core_adjudicate,"carrier-adjudicate":carrier_adjudicate,"synthesize":synthesize
 }[a.cmd](a)

if __name__=="__main__":main()
