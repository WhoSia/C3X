#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from collections import defaultdict
from pathlib import Path

def load(p):return json.loads(Path(p).read_text())
def pid(z):return f"p21:{z['source_id']}:{z['trajectory_hash'][:12]}"
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--corpus',required=True);ap.add_argument('--pair-freeze',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 corp=load(a.corpus);pf=load(a.pair_freeze);ctx={pid(z):z for z in corp['positions']};src_pairs=defaultdict(int);rows=[];pair_cells=0
 for p,z in sorted(pf['positions'].items()):
  if not z.get('admitted'):continue
  if p not in ctx:raise SystemExit('P21_PAIR_JOIN '+p)
  active=sorted(e for e,v in z.get('engine_views',{}).items() if v.get('active'));n=len(active);k=n*(n-1)//2;pair_cells+=k;src_pairs[z['source_id']]+=k
  rows.append({'position_id':p,'source_id':z['source_id'],'active_engines':active,'engine_pair_cells':k,'pair':z['pair'],'context':ctx[p]['context']})
 sources=sorted({z['source_id'] for z in corp['positions']});passed=len(sources)>=2 and pair_cells>=12 and all(src_pairs[s]>0 for s in sources)
 out={'schema':'c3x-g10-p21-phase-e-pair-gate-v1','stage':'C3X 0.10.0-G10-P21','verdict':'PASS_PHASE_E_PAIR_POSITIVITY' if passed else 'HOLD_PHASE_E_PAIR_SUPPORT','selected_worlds_pre_router':32,'router_assigned_worlds':len(corp['positions']),'admitted_positions':len(rows),'engine_pair_cells':pair_cells,'engine_pair_cells_by_source':dict(src_pairs),'sources':sources,'frozen_minimums':{'sources':2,'selected_positions':24,'engine_pair_cells':12},'p21_intervention_outcomes_consulted':False,'positions':rows}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('P21_PAIR_GATE',out['verdict'],'ADMITTED',len(rows),'PAIR_CELLS',pair_cells,'BY_SOURCE',dict(src_pairs))
if __name__=='__main__':main()
