#!/usr/bin/env python3
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'harness'))
import p27_age_morphism as p27
import p32_event_court as p32
import g95_p13_court as p13

def write_red(path,addrs):
 with open(path,'w') as f:
  for a in addrs:f.write(f"{a['ply']}\t{a['depth']}\t{a['move_index']}\t{a['reduction']}\t{a['new_depth']}\t{a['reduced_depth']}\t{a['occ']}\n")

def setup(binary,protocol,family,target,work):
 env=os.environ.copy();work=Path(work);work.mkdir(parents=True,exist_ok=True)
 env['C3X_TT_USE_MODE']='BASE';env['C3X_P20_FORCE_SEMANTIC_MEASUREMENT']='1';env['C3X_TT_GRAPH_SEQ']='0'
 env['C3X_TT_USE_TRACE']=str(work/'sem.csv');env['C3X_TT_TRACE']=str(work/'tt.csv');env['C3X_P32_TRACE']=str(work/'p32.csv');env['C3X_P20_REDUCTION_TRACE']=str(work/'red.csv')
 if family=='REDUCTION':
  rf=work/'targets-red.tsv';write_red(rf,target);env['C3X_P20_REDUCTION_MODE']='TARGET_REMOVE';env['C3X_P20_REDUCTION_TARGET_FILE']=str(rf);env['C3X_P32_MODE']='CATALOG';env['C3X_P32_FAMILY']='CUTOFF';env['C3X_P32_FRONTIER']='8'
 else:
  tf=work/'targets.tsv';p32.write_targets(tf,target);env['C3X_P20_REDUCTION_MODE']='BASE';env['C3X_P32_MODE']='REMOVE_SET';env['C3X_P32_FAMILY']=family;env['C3X_P32_FRONTIER']='8';env['C3X_P32_TARGET_FILE']=str(tf)
 if protocol=='env':env['C3X_PSM_MODE']='SHAM'
 else:env.pop('C3X_PSM_MODE',None)
 p=subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write('uci\n');p.stdin.flush();pre=p27.read_until(p,lambda x:x.strip()=='uciok');opts='\n'.join(pre)
 cmd=[]
 if protocol=='stockfish_uci':cmd+=['setoption name C3X_TTReadMode value SHAM','setoption name C3X_Telemetry value true']
 if p27.has_option(opts,'Threads'):cmd.append('setoption name Threads value 1')
 if p27.has_option(opts,'Hash'):cmd.append('setoption name Hash value 1')
 if p27.has_option(opts,'SyzygyProbeLimit'):cmd.append('setoption name SyzygyProbeLimit value 0')
 if p27.has_option(opts,'UCI_ShowWDL'):cmd.append('setoption name UCI_ShowWDL value true')
 if p27.has_option(opts,'Clear Hash'):cmd.append('setoption name Clear Hash')
 cmd.append('isready')
 for c in cmd:p.stdin.write(c+'\n')
 p.stdin.flush();ready=p27.read_until(p,lambda x:x.strip()=='readyok')
 if not any(x.strip()=='readyok' for x in ready):raise RuntimeError('P21_READY')
 return p

def run(binary,protocol,fen,move,family,target,work):
 p=setup(binary,protocol,family,target,work)
 try:
  p.stdin.write(f'position fen {fen}\ngo nodes 20000 searchmoves {move}\n');p.stdin.flush();lines=p27.read_until(p,lambda x:x.startswith('bestmove '));sem=p27.parse_sem(lines)
  try:p.stdin.write('quit\n');p.stdin.flush()
  except:pass
  try:p.communicate(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.communicate()
 finally:
  if p.poll() is None:p.kill()
 return p13.score_cp(sem.get('score'))
