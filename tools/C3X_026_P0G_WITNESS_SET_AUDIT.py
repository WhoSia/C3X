#!/usr/bin/env python3
"""Read-only C3X 0.26 P0-G opponent legal response identity audit."""
import argparse,collections,hashlib,json
from pathlib import Path
import chess
EXPECTED='18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2'
def main(p):
 raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('P11 source hash mismatch')
 rows=[json.loads(l) for l in raw.splitlines() if l.strip()]
 if len(rows)!=144:raise ValueError('row count mismatch')
 g=collections.defaultdict(list)
 for r in rows:g[(r['index'],r['mode'],r['root_move'],r['reply_depth'])].append(r)
 if len(g)!=72 or any(len(v)!=2 or sorted(r['repeat'] for r in v)!=[1,2] or v[0]['replies']!=v[1]['replies'] for v in g.values()):raise ValueError('repeat mismatch')
 groups=collections.defaultdict(dict)
 for (idx,mode,root,depth),v in g.items():
  r=v[0];b=chess.Board(r['fen_before_root']);m=chess.Move.from_uci(root)
  if m not in b.legal_moves:raise ValueError(('illegal root',idx,root))
  b.push(m)
  if b.fen(en_passant='fen')!=r['fen_after_root']:raise ValueError(('after-root fen',idx,root))
  groups[(idx,mode,depth)][root]={
    'legal':{m.uci() for m in b.legal_moves},
    'checks':{m.uci() for m in b.legal_moves if b.gives_check(m)},
    'captures':{m.uci() for m in b.legal_moves if b.is_capture(m)}}
 out=[]
 for (idx,mode,depth),roots in sorted(groups.items()):
  if len(roots)!=2:raise ValueError(('root number',idx,mode,depth))
  a,b=sorted(roots);record={'index':idx,'mode':mode,'reply_depth':depth,'roots':[a,b]}
  for kind in ('legal','checks','captures'):
   x=roots[a][kind];y=roots[b][kind]
   record[kind]={'n_A':len(x),'n_B':len(y),'only_A':sorted(x-y),'only_B':sorted(y-x),'shared_count':len(x&y),'symmetric_difference':len(x^y)}
  out.append(record)
 for idx in {r['index'] for r in out}:
  sub=[r for r in out if r['index']==idx]
  if len({json.dumps({k:v for k,v in r.items() if k not in ('mode','reply_depth')},sort_keys=True) for r in sub})!=1:
   raise ValueError(('depth/mode invariance',idx))
 return {'status':'P0G_DESCRIPTIVE_NOT_CAUSAL','source_sha256':EXPECTED,'rows':144,'unique_arms':72,'comparisons':out,
 'limitations':['UCI move identities are not strategy-equivalent semantics','Selected P10 outcome cohort, no held-out generalization','No chess value or algorithm causal attribution']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 r=main(a.input);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print('P0G_PASS',r['rows'],r['unique_arms'],len(r['comparisons']))
