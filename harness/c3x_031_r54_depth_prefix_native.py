#!/usr/bin/env python3
"""R54 preregistered exposed six-case fixed-pair depth-prefix diagnostic."""
import argparse, hashlib, json, queue, re, subprocess, threading, time
from pathlib import Path

COHORT='7cbc31ed52b755cdffd479f87c6bfedf563d492b25eb6ebde8179b72e494026c'
ENGINE='78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb'
NET='5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b'
IDS=('T04-TAC-1','T04-QUI-1','T04-QUI-2','T04-PRO-1','T04-PRO-4','T04-END-1')
DEPTHS=(8,10,14,18,22)
POLICIES={'shallow':(8,10),'all_prefix':(8,10,14,18),'deep_tail':(14,18)}
TIMEOUT=120

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(x,msg):
    if not x:raise ValueError(msg)
def sign(x):return 1 if x>0 else -1

def run_arm(engine,net,fen,move,log):
    q=queue.Queue(); lines=[]; errs=[]; start=time.monotonic(); end=None; status='incomplete'
    p=subprocess.Popen([str(engine.resolve())],cwd=net.parent,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    def read():
        for line in p.stdout:q.put(line.rstrip('\n'))
        q.put(None)
    def readerr():
        for line in p.stderr:errs.append(line.rstrip('\n'))
    threading.Thread(target=read,daemon=True).start(); threading.Thread(target=readerr,daemon=True).start()
    def send(s):p.stdin.write(s+'\n');p.stdin.flush()
    def until(terminal,deadline):
        while True:
            line=q.get(timeout=max(.001,deadline-time.monotonic()))
            if line is None:raise RuntimeError('unexpected EOF')
            lines.append(line)
            if terminal(line):return line
    try:
        send('uci'); until(lambda x:x=='uciok',start+10)
        for opt,val in [('Threads','1'),('Hash','16'),('Use NNUE','false'),('EvalFile',str(net.resolve()))]:send(f'setoption name {opt} value {val}')
        send('isready');until(lambda x:x=='readyok',time.monotonic()+10)
        send('position fen '+fen);send('go depth 22 searchmoves '+move)
        end=until(lambda x:x.startswith('bestmove '),time.monotonic()+TIMEOUT)
        status='ok' if end.split()[1]==move else 'bestmove_mismatch'
    except (queue.Empty,TimeoutError):status='timeout'
    except (RuntimeError,BrokenPipeError,OSError) as e:status='engine_error:'+str(e)
    finally:
        try:send('quit');p.wait(timeout=3)
        except (BrokenPipeError,subprocess.TimeoutExpired):p.kill();p.wait()
    depth={str(d):{'status':'missing'} for d in DEPTHS}; observed={str(d):[] for d in DEPTHS}
    for line in lines:
        if not line.startswith('info depth '):continue
        m=re.search(r'\bdepth (\d+)\b.*?\bscore (cp|mate) (-?\d+)\b',line)
        if not m or int(m[1]) not in DEPTHS:continue
        d,kind,value=m.groups();pv=re.search(r'\bpv (\S+)',line);nodes=re.search(r'\bnodes (\d+)',line)
        bound='lowerbound' if ' lowerbound' in line else 'upperbound' if ' upperbound' in line else None
        obs={'status':'root_mismatch' if not pv or pv[1]!=move else 'bound' if bound else 'mate' if kind=='mate' else 'exact_cp','value':int(value),'kind':kind,'bound':bound,'pv_root':pv[1] if pv else None,'nodes':int(nodes[1]) if nodes else None}
        observed[d].append(obs)
        if obs['status']=='exact_cp' or depth[d]['status']!='exact_cp':depth[d]=obs
    if status!='ok':depth={str(d):{'status':status} for d in DEPTHS}
    log.write_text('\n'.join(lines)+'\n--- stderr ---\n'+'\n'.join(errs)+'\n')
    return {'status':status,'bestmove':end,'depths':depth,'observations':observed,'seconds':round(time.monotonic()-start,3),'log_sha256':sha(log)}

def decision(gaps,depths):
    g=[gaps[str(d)] for d in depths]
    return sign(g[0]) if all(x is not None and abs(x)>20 for x in g) and len({sign(x) for x in g})==1 else None

def main():
    p=argparse.ArgumentParser()
    for k in ('cohort','engine','net','out'):p.add_argument(k,type=Path)
    p.add_argument('--case',choices=IDS)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    for path,h in ((a.cohort,COHORT),(a.engine,ENGINE),(a.net,NET)):require(sha(path)==h,'identity drift: '+str(path))
    byid={x['id']:x for x in json.loads(a.cohort.read_text())['cohort']};rows=[]
    for ident in ((a.case,) if a.case else IDS):
        c=byid[ident];arms={}
        for side in ('A','B'):
            log=a.out/(ident+'_'+side+'.txt');require(not log.exists(),'repeat prohibited: '+str(log))
            print('START',ident,side,flush=True);arms[side]=run_arm(a.engine,a.net,c['fen'],c[side],log);print('DONE',ident,side,arms[side]['status'],arms[side]['seconds'],flush=True)
        gaps={};cost={}
        for d in map(str,DEPTHS):
            x,y=(arms[k]['depths'][d] for k in ('A','B'));gaps[d]=x['value']-y['value'] if x['status']==y['status']=='exact_cp' else None
            cost[d]=x['nodes']+y['nodes'] if x.get('nodes') is not None and y.get('nodes') is not None else None
        row={'id':ident,'arms':arms,'gaps':gaps,'prefix_nodes':cost,'reference':decision(gaps,(22,)),'policies':{k:decision(gaps,v) for k,v in POLICIES.items()}}
        (a.out/(ident+'.json')).write_text(json.dumps(row,indent=2,sort_keys=True)+'\n');print('CASE',ident,gaps,row['policies'],flush=True)
if __name__=='__main__':main()
