#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys
from collections import defaultdict
from pathlib import Path
import chess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import p27_age_morphism as p27
import p32_event_court as p32
import g95_p13_court as p13

def load(p):return json.loads(Path(p).read_text())
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":")).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def chain_sig(ch):return "|".join([ch["target_edit"],ch["subset_edit"],ch["sham_edit"],",".join(ch.get("target_atoms",[])),",".join(ch.get("subset_atoms",[]))])
def world_rows(root):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g10-p19-engine-support-world-v1":out.append(x)
 return out
def find_binary(root,e):
 xs=list(Path(root).rglob(f"c3x-p20c-{e}"))
 if len(xs)!=1:raise SystemExit(f"P20C_BINARY_{e}_{len(xs)}")
 xs[0].chmod(0o755);return xs[0]
def resolve_cell(cell,tensor,worlddir):
 T=load(tensor);row=next((r for r in T["rows"] if r["row_id"]==cell["row_id"]),None)
 if not row:raise SystemExit("P20C_ROW")
 bypos=[w for w in world_rows(worlddir) if w["position_id"]==row["position_id"]]
 hit=None
 for w in bypos:
  for _,ch in w["chains"].items():
   if ch and chain_sig(ch)==row["chain_signature"]:hit=(w,ch);break
  if hit:break
 if not hit:raise SystemExit("P20C_WORLD")
 w,ch=hit
 return row,w,ch
def setup(binary,protocol,family,work):
 env=os.environ.copy()
 env["C3X_TT_USE_MODE"]="BASE"
 env["C3X_P20_FORCE_SEMANTIC_MEASUREMENT"]="1"
 env["C3X_P20_REDUCTION_MODE"]="BASE"
 env.pop("C3X_P20_REDUCTION_TARGET_FILE",None)
 env["C3X_TT_USE_TRACE"]=str(work/"sem.csv")
 env["C3X_P20_REDUCTION_TRACE"]=str(work/"red.csv")
 env["C3X_P32_MODE"]="CATALOG"
 env["C3X_P32_FAMILY"]=family if family!="REDUCTION" else "CUTOFF"
 env["C3X_P32_FRONTIER"]="8"
 env["C3X_P32_TRACE"]=str(work/"p32.csv")
 env["C3X_TT_TRACE"]=str(work/"tt.csv");env["C3X_TT_GRAPH_SEQ"]="0"
 env.pop("C3X_P32_TARGET_FILE",None)
 if protocol=="env":env["C3X_PSM_MODE"]="SHAM"
 else:env.pop("C3X_PSM_MODE",None)
 p=subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush();pre=p27.read_until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("P20C_UCI")
 opts="\n".join(pre);cmd=[]
 if protocol=="stockfish_uci":
  if not p27.has_option(opts,"C3X_TTReadMode") or not p27.has_option(opts,"C3X_Telemetry"):raise RuntimeError("P20C_SF_SURFACE")
  cmd += ["setoption name C3X_TTReadMode value SHAM","setoption name C3X_Telemetry value true"]
 if p27.has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
 if p27.has_option(opts,"Hash"):cmd.append("setoption name Hash value 1")
 if p27.has_option(opts,"SyzygyProbeLimit"):cmd.append("setoption name SyzygyProbeLimit value 0")
 if p27.has_option(opts,"UCI_ShowWDL"):cmd.append("setoption name UCI_ShowWDL value true")
 if p27.has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
 cmd.append("isready")
 for c in cmd:p.stdin.write(c+"\n")
 p.stdin.flush();ready=p27.read_until(p,lambda x:x.strip()=="readyok")
 if not any(x.strip()=="readyok" for x in ready):raise RuntimeError("P20C_READY")
 return p
def reduction_addresses(path):
 counts=defaultdict(int);out=[]
 p=Path(path)
 if not p.exists():return out
 for line in p.read_text().splitlines():
  z=line.split(",")
  if len(z)!=11 or z[0]!="D":continue
  _,scope,ply,depth,mi,r,nd,rd,a,b,q=z
  sig=(int(ply),int(depth),int(mi),int(r),int(nd),int(rd));counts[sig]+=1
  x={"scope":scope,"ply":sig[0],"depth":sig[1],"move_index":sig[2],"reduction":sig[3],"new_depth":sig[4],"reduced_depth":sig[5],"occ":counts[sig]}
  x["address_id"]=digest(x);out.append(x)
 return out
def run_once(binary,protocol,fen,move,family,work):
 work=Path(work);work.mkdir(parents=True,exist_ok=True);p=setup(binary,protocol,family,work)
 try:
  p.stdin.write(f"position fen {fen}\ngo nodes 20000 searchmoves {move}\n");p.stdin.flush()
  lines=p27.read_until(p,lambda x:x.startswith("bestmove "));sem=p27.parse_sem(lines)
  try:p.stdin.write("quit\n");p.stdin.flush()
  except:pass
  try:p.communicate(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.communicate()
 finally:
  if p.poll() is None:p.kill()
 cp=p13.score_cp(sem.get("score"))
 if family=="REDUCTION":addrs=reduction_addresses(work/"red.csv")
 else:
  tr=p32.parse_trace(work/"p32.csv")
  addrs=[dict(e["address"],address_id=e["address_id"]) for e in tr["events"]]
 return {"cp":cp,"addresses":addrs}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--support",required=True);ap.add_argument("--cell-id",required=True);ap.add_argument("--tensor",required=True);ap.add_argument("--worlds",required=True);ap.add_argument("--build-dir",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args();S=load(a.support);cell=next((x for x in S["cells"] if x["id"]==a.cell_id),None)
 if not cell:raise SystemExit("P20C_CELL")
 row,w,ch=resolve_cell(cell,a.tensor,a.worlds);e=cell["engine"];binary=find_binary(a.build_dir,e);protocol=p32.protocol_for(e)
 A=w["pair"]["A"]["uci"];B=w["pair"]["B"]["uci"];contexts=[];base_boards={};all_ids=[]
 for bn,key in (("TARGET","target_fen"),("SUBSET","subset_fen"),("SHAM","sham_fen")):
  fen=ch[key];legal={m.uci() for m in chess.Board(fen).legal_moves};vals={}
  for move in (A,B):
   reps=[run_once(binary,protocol,fen,move,cell["family"],Path(a.out).parent/f".private-{bn}-{move}-{r}") for r in range(2)]
   stable=reps[0]["cp"] is not None and reps[0]["cp"]==reps[1]["cp"]
   ids0=[x["address_id"] for x in reps[0]["addresses"] if int(x.get("ply",0))<=8]
   ids1=[x["address_id"] for x in reps[1]["addresses"] if int(x.get("ply",0))<=8]
   repeatable=ids0==ids1
   tagged=[]
   for z in reps[0]["addresses"]:
    if int(z.get("ply",0))>8:continue
    q=dict(z);q["context"]=f"{bn}:{move}";q["context_address_id"]=digest({"context":q["context"],"address_id":q["address_id"]});tagged.append(q);all_ids.append(q)
   vals[move]={"cp":reps[0]["cp"],"stable":stable,"address_repeatable":repeatable,"address_count":len(tagged)}
   contexts.append({"context":f"{bn}:{move}","cp":reps[0]["cp"],"stable":stable,"address_repeatable":repeatable,"addresses":tagged})
  gap=None if not all(vals[m]["stable"] for m in (A,B)) else abs(vals[A]["cp"]-vals[B]["cp"])
  base_boards[bn]={"gap_cp_abs":gap,"supported":bool(A in legal and B in legal and gap is not None and gap<=50),"pair":vals}
 base_support=all(z["supported"] for z in base_boards.values())
 frontiers={str(f):sum(int(z.get("ply",0))<=f for z in all_ids) for f in S["address_frontiers"]}
 repeatable=all(x["stable"] and x["address_repeatable"] for x in contexts)
 verdict="PASS_ADDRESSABILITY" if base_support==cell["base_support"] and repeatable and 0<len(all_ids)<=S["max_addresses_per_cell"] else "HOLD_ADDRESSABILITY"
 out={"schema":"c3x-g10-p20-phase-c-census-v1","stage":"C3X 0.10.0-G10-P20","cell":cell,"base_support":base_support,"base_boards":base_boards,
      "context_count":len(contexts),"contexts":contexts,"address_count":len(all_ids),"address_count_by_frontier":frontiers,
      "base_identity":base_support==cell["base_support"],"repeatable":repeatable,"verdict":verdict,"event_outcomes_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P20C_CENSUS",cell["id"],cell["engine"],cell["family"],verdict,"BASE",base_support,"ADDR",len(all_ids),"FRONTIERS",frontiers)
if __name__=="__main__":main()
