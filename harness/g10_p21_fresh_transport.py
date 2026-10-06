#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,json,sys
from pathlib import Path
import chess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'harness'))
import g10_p19_engine_support as p19
import g10_p20_forced as full
import g10_p21_target_runner as targeted
import p32_event_court as p32

KEYS=[('MOVE_ORDER','MAIN','SHAM','A','2','5-8'),('MOVE_ORDER','MAIN','SUBSET','A','2','5-8'),('CUTOFF','MAIN','SHAM','B','3-4','1-4'),('CUTOFF','MAIN','TARGET','B','5-8','1-4'),('MOVE_ORDER','MAIN','SHAM','A','3-4','5-8'),('MOVE_ORDER','MAIN','SUBSET','A','3-4','5-8'),('CUTOFF','MAIN','TARGET','A','5-8','1-4')]
def load(p):return json.loads(Path(p).read_text())
def pb(x):
 x=int(x);return '0' if x==0 else '1' if x==1 else '2' if x==2 else '3-4' if x<=4 else '5-8'
def db(x):
 x=int(x);return '<=0' if x<=0 else '1-4' if x<=4 else '5-8' if x<=8 else '9-12' if x<=12 else '13+'
def cls(f,e):return (f=='MOVE_ORDER' and e['class']=='MOVE_ORDER_SEED') or (f=='CUTOFF' and e['class']=='CUTOFF')
def binary(root,e):
 xs=list(Path(root).rglob(f'c3x-p20c-{e}'))
 if len(xs)!=1:raise SystemExit(f'P21_FRESH_BINARY_{e}_{len(xs)}')
 xs[0].chmod(0o755);return xs[0]
def measure_arm(b,protocol,fen,A,B,arm,root):
 vals={}
 for move in (A,B):
  cps=[]
  for rep in range(2):cps.append(full.score_cp(full.run(b,protocol,fen,move,20000,Path(root)/f'{move}-{rep}',arm).get('score')))
  vals[move]={'stable':None not in cps and cps[0]==cps[1],'cp':cps[0] if None not in cps and cps[0]==cps[1] else None}
 gap=None if not all(vals[m]['stable'] for m in (A,B)) else abs(vals[A]['cp']-vals[B]['cp'])
 return vals,gap is not None and gap<=50
def catalog(b,protocol,fen,move,family,root):
 sem=full.run(b,protocol,fen,move,20000,root,'BASE');tr=p32.parse_trace(Path(root)/'p32.csv')
 return [e for e in tr['events'] if cls(family,e)]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--corpus',required=True);ap.add_argument('--pair-freeze',required=True);ap.add_argument('--build-dir',required=True);ap.add_argument('--shard',type=int,required=True);ap.add_argument('--shards',type=int,required=True);ap.add_argument('--out-dir',required=True);a=ap.parse_args()
 corp=load(a.corpus);pf=load(a.pair_freeze);by={f"p21:{z['source_id']}:{z['trajectory_hash'][:12]}":z for z in corp['positions']};rows=[]
 admitted=[(pid,z) for pid,z in sorted(pf['positions'].items()) if z.get('admitted')]
 for ix,(pid,z) in enumerate(admitted):
  meta=by[pid];ch=p19.choose_chain(meta['fen'],z['pair'],meta['router_grammar'])
  if not ch:continue
  for e,v in sorted(z['engine_views'].items()):
   if not v.get('active'):continue
   if len(rows)%a.shards!=a.shard:rows.append(None);continue
   b=binary(a.build_dir,e);protocol=pf['variants'][e]['protocol'];A=z['pair']['A']['uci'];B=z['pair']['B']['uci'];boards={'TARGET':ch['target_fen'],'SUBSET':ch['subset_fen'],'SHAM':ch['sham_fen']}
   for family,arm in (('MOVE_ORDER','NO_MOVE'),('CUTOFF','NO_CUTOFF')):
    base={};klass={};base_ok=True;class_ok=True
    for bn,fen in boards.items():
     vals,sup=measure_arm(b,protocol,fen,A,B,'BASE',Path(a.out_dir)/f'.b-{ix}-{e}-{family}-{bn}');base[bn]={'pair':vals,'supported':sup};base_ok &= sup
     vals2,sup2=measure_arm(b,protocol,fen,A,B,arm,Path(a.out_dir)/f'.c-{ix}-{e}-{family}-{bn}');klass[bn]={'pair':vals2,'supported':sup2};class_ok &= sup2
    matched={};fiber=copy.deepcopy(base);matched_n=0;stable=True
    for key in [k for k in KEYS if k[0]==family]:
     _,scope,bn,slot,pb0,db0=key;move=A if slot=='A' else B;ev=catalog(b,protocol,boards[bn],move,family,Path(a.out_dir)/f'.cat-{ix}-{e}-{family}-{bn}-{slot}')
     addrs=[dict(x['address']) for x in ev if x['scope']==scope and pb(x['ply'])==pb0 and db(x['depth'])==db0]
     if not addrs:continue
     matched_n+=len(addrs);scores=[targeted.run(b,protocol,boards[bn],move,family,addrs,Path(a.out_dir)/f'.f-{ix}-{e}-{family}-{bn}-{slot}-{r}') for r in range(2)]
     ok=None not in scores and scores[0]==scores[1];stable &= ok;matched['|'.join(key)]={'addresses':len(addrs),'stable':ok,'score':scores[0] if ok else None}
     if ok:fiber[bn]['pair'][move]['cp']=scores[0]
    fiber_ok=None
    if matched_n and stable:
     for bn in boards:
      vals=fiber[bn]['pair'];gap=abs(vals[A]['cp']-vals[B]['cp']);fiber[bn]['supported']=gap<=50
     fiber_ok=all(fiber[bn]['supported'] for bn in boards)
    status='NO_MATCHING_FIBER' if matched_n==0 else 'CLASS_NO_EFFECT' if class_ok==base_ok else 'UNSTABLE_FIBER' if not stable else 'FRESH_CONFIRMED' if fiber_ok==class_ok else 'FRESH_FALSIFIED'
    rows[-1 if rows and rows[-1] is None else len(rows):]=[]
    rows.append({'schema':'c3x-g10-p21-fresh-transport-cell-v1','position_id':pid,'source_id':z['source_id'],'engine':e,'family':family,'base_support':base_ok,'class_support':class_ok,'fiber_support':fiber_ok,'matching_addresses':matched_n,'matched_keys':matched,'status':status})
 out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
 for i,r in enumerate(x for x in rows if x is not None):(out/f'{a.shard}-{i:03d}.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
 print('P21_FRESH_SHARD',a.shard,'ROWS',sum(x is not None for x in rows))
if __name__=='__main__':main()
