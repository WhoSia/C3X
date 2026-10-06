#!/usr/bin/env python3
import argparse,copy,json,statistics,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'harness'))
import p32_event_court as p32
import g10_p20_phase_c_census as p20c
import g10_p21_target_runner as tr

def load(p):return json.loads(Path(p).read_text())
def pb(x):
 x=int(x);return '0' if x==0 else '1' if x==1 else '2' if x==2 else '3-4' if x<=4 else '5-8'
def db(x):
 x=int(x);return '<=0' if x<=0 else '1-4' if x<=4 else '5-8' if x<=8 else '9-12' if x<=12 else '13+'
def q0(family,a,arm,slot):return (family,a['scope'],arm,slot,pb(a['ply']),db(a['depth']))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--support',required=True);ap.add_argument('--cell-id',required=True);ap.add_argument('--census',required=True);ap.add_argument('--tensor',required=True);ap.add_argument('--worlds',required=True);ap.add_argument('--build-dir',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 S=load(a.support);cell=next(x for x in S['cells'] if x['id']==a.cell_id);C=load(a.census);row,w,ch=p20c.resolve_cell(cell,a.tensor,a.worlds)
 A=w['pair']['A']['uci'];B=w['pair']['B']['uci'];slot={A:'A',B:'B'};fib=defaultdict(list)
 for ctx in C['contexts']:
  arm,move=ctx['context'].split(':',1)
  for z in ctx['addresses']:fib[q0(cell['family'],z,arm,slot[move])].append(z)
 ranked=sorted(fib.items(),key=lambda kv:(-len(kv[1]),statistics.median(int(z['ply']) for z in kv[1]),str(kv[0])))[:32]
 binary=p20c.find_binary(a.build_dir,cell['engine']);protocol=p32.protocol_for(cell['engine']);base=C['base_boards'];probes=[]
 for i,(key,members) in enumerate(ranked):
  _,_,arm,sl,_,_=key;move=A if sl=='A' else B;fen=ch[{'TARGET':'target_fen','SUBSET':'subset_fen','SHAM':'sham_fen'}[arm]];scores=[]
  for rep in range(2):scores.append(tr.run(binary,protocol,fen,move,cell['family'],members,Path(a.out).parent/f'.private-{i}-{rep}'))
  stable=None not in scores and scores[0]==scores[1];bb=copy.deepcopy(base);support=None
  if stable:
   bb[arm]['pair'][move]['cp']=scores[0]
   for bn in ('TARGET','SUBSET','SHAM'):
    vals=list(bb[bn]['pair'].values());gap=abs(vals[0]['cp']-vals[1]['cp']);bb[bn]['gap_cp_abs']=gap;bb[bn]['supported']=gap<=50
   support=all(bb[bn]['supported'] for bn in ('TARGET','SUBSET','SHAM'))
  probes.append({'rank':i+1,'q0_key':list(key),'members':len(members),'median_ply':statistics.median(int(z['ply']) for z in members),'stable':stable,'score':scores[0] if stable else None,'support':support,'positive':stable and support==cell['class_support'] and support!=cell['base_support']})
 out={'schema':'c3x-g10-p21-fiber-probe-v1','stage':'C3X 0.10.0-G10-P21','cell':cell,'q_level':'Q0','probe_count':len(probes),'positive_count':sum(x['positive'] for x in probes),'first_positive_rank':next((x['rank'] for x in probes if x['positive']),None),'probes':probes,'verdict':'POSITIVE_FIBER_FOUND' if any(x['positive'] for x in probes) else 'NO_POSITIVE_FIBER_WITHIN_BUDGET'}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('P21_FIBER',cell['id'],out['verdict'],'POS',out['positive_count'],'FIRST',out['first_positive_rank'])
if __name__=='__main__':main()
