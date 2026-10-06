#!/usr/bin/env python3
from __future__ import annotations
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import p27_age_morphism as p27
import p32_event_court as p32
import g95_p13_court as p13

def setup(path,protocol,arm,work):
 env=os.environ.copy()
 env["C3X_TT_USE_MODE"]=arm if arm in ("NO_CUTOFF","NO_MOVE","NO_EVAL") else "BASE"
 env["C3X_P20_FORCE_SEMANTIC_MEASUREMENT"]="1"
 env["C3X_P20_REDUCTION_MODE"]="NO_REDUCTION" if arm=="NO_REDUCTION" else "BASE"
 env["C3X_TT_USE_TRACE"]=str(work/"sem.csv")
 env["C3X_P20_REDUCTION_TRACE"]=str(work/"red.csv")
 env["C3X_P32_MODE"]="CATALOG";env["C3X_P32_FAMILY"]="ALL";env["C3X_P32_FRONTIER"]="8"
 env["C3X_P32_TRACE"]=str(work/"p32.csv");env["C3X_TT_TRACE"]=str(work/"tt.csv");env["C3X_TT_GRAPH_SEQ"]="0"
 if protocol=="env":env["C3X_PSM_MODE"]="SHAM"
 else:env.pop("C3X_PSM_MODE",None)
 p=subprocess.Popen([str(path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush();pre=p27.read_until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("P20_UCI")
 opts="\n".join(pre);cmd=[]
 if protocol=="stockfish_uci":
  if not p27.has_option(opts,"C3X_TTReadMode") or not p27.has_option(opts,"C3X_Telemetry"):raise RuntimeError("P20_SF_SURFACE")
  cmd += ["setoption name C3X_TTReadMode value SHAM","setoption name C3X_Telemetry value true"]
 if p27.has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
 if p27.has_option(opts,"Hash"):cmd.append("setoption name Hash value 1")
 if p27.has_option(opts,"SyzygyProbeLimit"):cmd.append("setoption name SyzygyProbeLimit value 0")
 if p27.has_option(opts,"UCI_ShowWDL"):cmd.append("setoption name UCI_ShowWDL value true")
 if p27.has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
 cmd.append("isready")
 for c in cmd:p.stdin.write(c+"\n")
 p.stdin.flush();ready=p27.read_until(p,lambda x:x.strip()=="readyok")
 if not any(x.strip()=="readyok" for x in ready):raise RuntimeError("P20_READY")
 return p

def run(path,protocol,fen,move,nodes,work,arm):
 work=Path(work);work.mkdir(parents=True,exist_ok=True);p=setup(path,protocol,arm,work)
 try:
  p.stdin.write(f"position fen {fen}\ngo nodes {nodes} searchmoves {move}\n");p.stdin.flush()
  lines=p27.read_until(p,lambda x:x.startswith("bestmove "))
  sem=p27.parse_sem(lines)
  try:p.stdin.write("quit\n");p.stdin.flush()
  except:pass
  try:p.communicate(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.communicate()
 finally:
  if p.poll() is None:p.kill()
 return sem

def score_cp(x):return p13.score_cp(x)
